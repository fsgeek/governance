"""Per-admissible-model accuracy on the Cat 1 subset from the 2026-05-11 run.

Falsification target named in the 2026-05-11 null-Cat-2 findings note: if any
single admissible model gets a meaningful fraction of the 3,941 Cat 1 cases
right, that points at "set-revision mechanism too coarse to surface it"
rather than "policy genuinely binding." If no admissible model does, the
binding-policy diagnosis stands.

Cat 1 on this run is structurally narrow: every case has realized=0 (charged
off) AND original ensemble verdict = 1 (predicted grant). So the test
reduces to: "for each admissible model, on what fraction of the 3,941
predicted-grant / actually-defaulted cases does the model predict deny?"

Output: a sorted table of (max_depth, min_samples_leaf, feature_subset,
holdout_auc, cat1_deny_fraction, n_cat1_correct) plus aggregate maxima.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from policy.encoder import load_policy
from wedge.collectors.lendingclub import (
    ORIGINATION_FEATURE_COLS,
    derive_label,
    filter_to_vintage,
    normalize_emp_length,
)
from wedge.models import fit_model
from wedge.rashomon import SweepConfig, evaluate_policy, hyperparameter_sweep


CSV_PATH = Path("data/accepted_2007_to_2018Q4.csv")
JSONL_PATH = Path("runs/2026-05-11T20-25-56Z-target-c.jsonl")
POLICY_PATH = Path("policy/thin_demo_hmda.yaml")
TARGET_VINTAGE = "2015Q4"
TERM = "36 months"
SEED = 0


def _load_target() -> tuple[pd.DataFrame, list[str]]:
    """Reproduce the orchestration's V_2 load identically."""
    raw = pd.read_csv(CSV_PATH, low_memory=False)
    df = filter_to_vintage(raw, vintage=TARGET_VINTAGE, term=TERM)
    df = df.copy()  # de-fragment to avoid PerformanceWarning churn
    df["label"] = derive_label(df["loan_status"])
    if "emp_length" in df.columns:
        df["emp_length"] = normalize_emp_length(df["emp_length"])
    feature_cols = [c for c in ORIGINATION_FEATURE_COLS if c in df.columns]
    df = df[feature_cols + ["label"]].dropna(subset=["label"]).reset_index(drop=True)
    return df, feature_cols


def _load_cat1(feature_cols: list[str]) -> tuple[pd.DataFrame, pd.Series]:
    """Read Cat 1 records from the run's jsonl."""
    feats = []
    labels = []
    with JSONL_PATH.open() as fh:
        for line in fh:
            r = json.loads(line)
            if r["classification"]["category"] == "Cat 1":
                feats.append(r["features"])
                labels.append(r["realized_outcome"])
    df = pd.DataFrame(feats)
    for c in feature_cols:
        if c not in df.columns:
            df[c] = float("nan")
    return df[feature_cols], pd.Series(labels)


def main() -> None:
    target_df, feature_cols = _load_target()
    print(f"V_2 rows: {len(target_df)}; features: {feature_cols}")

    # Same outer split (seed=0, test_size=0.30, stratify=label).
    train_df, _ = train_test_split(
        target_df, test_size=0.30, random_state=SEED, stratify=target_df["label"]
    )
    X_train = train_df[feature_cols]
    y_train = train_df["label"]
    print(f"outer-train: {len(X_train)} rows ({y_train.sum()} grants, {(1-y_train).sum()} denies)")

    # Same sweep config as orchestration.
    must_include = [c for c in ("fico_range_low", "dti") if c in feature_cols]
    optional = [c for c in feature_cols if c not in must_include]
    subsets = [tuple(feature_cols)]
    for drop in optional:
        subsets.append(tuple(c for c in feature_cols if c != drop))
    cfg = SweepConfig(
        max_depths=(4, 6, 8, 10, 12),
        min_samples_leafs=(25, 50, 100, 200, 400),
        feature_subsets=tuple(subsets),
        random_state=SEED,
        holdout_fraction=0.30,
    )
    policy = load_policy(POLICY_PATH)

    sweep = hyperparameter_sweep(X_train, y_train, config=cfg)
    admissible = evaluate_policy(sweep, policy_constraints=policy)
    print(
        f"swept {len(sweep)} combos; "
        f"admissible {len(admissible.admissible)}; "
        f"excluded {len(admissible.excluded)}"
    )

    # Refit every admissible model on the full outer-train.
    refits = []
    for i, sr in enumerate(admissible.admissible):
        m = fit_model(
            X_train,
            y_train,
            model_id=f"adm_{i:03d}",
            max_depth=sr.spec.max_depth,
            min_samples_leaf=sr.spec.min_samples_leaf,
            feature_subset=sr.spec.feature_subset,
            random_state=SEED,
        )
        refits.append((sr, m))

    cat1_X, cat1_y = _load_cat1(feature_cols)
    n_cat1 = len(cat1_y)
    print(f"Cat 1 cases loaded: {n_cat1}")
    print(f"Cat 1 realized label distribution: {Counter(cat1_y.tolist())}")

    # For each admissible model: fraction of Cat 1 cases predicted deny (0).
    # (Cat 1 ground truth is uniformly 0 on this run, so deny-fraction == accuracy.)
    rows = []
    for sr, m in refits:
        yhat = m.predict(cat1_X)
        n_deny = int((yhat == 0).sum())
        n_correct = int((yhat == cat1_y.values).sum())
        rows.append(
            dict(
                max_depth=sr.spec.max_depth,
                min_samples_leaf=sr.spec.min_samples_leaf,
                subset_size=len(sr.spec.feature_subset),
                subset=",".join(sr.spec.feature_subset),
                holdout_auc=round(sr.holdout_auc, 4),
                cat1_deny_fraction=round(n_deny / n_cat1, 4),
                n_cat1_deny=n_deny,
                n_cat1_correct=n_correct,
            )
        )

    rows.sort(key=lambda r: r["cat1_deny_fraction"], reverse=True)

    print("\nTop 10 admissible by Cat 1 deny-fraction (== accuracy here):")
    for r in rows[:10]:
        print(
            f"  d={r['max_depth']:2d} leaf={r['min_samples_leaf']:4d} "
            f"subset_size={r['subset_size']} auc={r['holdout_auc']:.4f} "
            f"cat1_deny={r['cat1_deny_fraction']:.4f} "
            f"({r['n_cat1_correct']}/{n_cat1}) subset={r['subset']}"
        )

    print("\nBottom 5 admissible by Cat 1 deny-fraction:")
    for r in rows[-5:]:
        print(
            f"  d={r['max_depth']:2d} leaf={r['min_samples_leaf']:4d} "
            f"subset_size={r['subset_size']} auc={r['holdout_auc']:.4f} "
            f"cat1_deny={r['cat1_deny_fraction']:.4f} "
            f"({r['n_cat1_correct']}/{n_cat1})"
        )

    max_acc = rows[0]["cat1_deny_fraction"]
    mean_acc = sum(r["cat1_deny_fraction"] for r in rows) / len(rows)
    print(f"\nmax admissible Cat 1 accuracy: {max_acc:.4f}")
    print(f"mean admissible Cat 1 accuracy: {mean_acc:.4f}")
    print(
        f"models with any deny prediction on Cat 1: "
        f"{sum(1 for r in rows if r['n_cat1_deny'] > 0)} / {len(rows)}"
    )


if __name__ == "__main__":
    main()
