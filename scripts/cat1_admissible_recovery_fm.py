"""Per-admissible-model Cat 1 recovery on the FM 2018Q1 dual-set run.

Mirror of `cat1_admissible_recovery.py` for the Fannie Mae substrate. The
LC script's data loader uses LendingClub conventions (issue_d/term filters,
charge-off label); this one uses the FM acquisition-and-performance loader
and the FM-specific thin demo policy.

Cat 1 on FM is small (479 cases vs ~3k on LC vintages) — class imbalance
is much sharper (0.80% deny vs ~14%). The falsification reads the same:
if no admissible model recovers a meaningful fraction of these cases,
"policy genuinely binding on this substrate × hypothesis space" holds.

Usage:
    PYTHONPATH=. python scripts/cat1_admissible_recovery_fm.py \\
        --jsonl runs/2026-05-11T22-12-32Z-target-c.jsonl
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from policy.encoder import load_policy
from wedge.collectors.fanniemae import (
    derive_origination_and_label,
    filter_eligible,
    read_raw,
    to_feature_frame,
)
from wedge.models import fit_model
from wedge.rashomon import SweepConfig, evaluate_policy, hyperparameter_sweep


FM_CSV = Path("data/fanniemae/2018Q1.csv")
POLICY_PATH = Path("policy/thin_demo_fm.yaml")
FEATURE_COLS = ["fico_range_low", "dti", "ltv", "loan_term_months"]
SEED = 0


def _load_fm() -> pd.DataFrame:
    raw = read_raw(FM_CSV)
    collapsed = derive_origination_and_label(raw)
    eligible = filter_eligible(collapsed)
    feats = to_feature_frame(eligible)
    return feats[FEATURE_COLS + ["label"]].dropna(
        subset=FEATURE_COLS + ["label"]
    ).reset_index(drop=True)


def _load_cat1(jsonl_path: Path) -> tuple[pd.DataFrame, pd.Series]:
    feats = []
    labels = []
    with jsonl_path.open() as fh:
        for line in fh:
            r = json.loads(line)
            if r["classification"]["category"] == "Cat 1":
                feats.append(r["features"])
                labels.append(r["realized_outcome"])
    df = pd.DataFrame(feats)
    for c in FEATURE_COLS:
        if c not in df.columns:
            df[c] = float("nan")
    return df[FEATURE_COLS], pd.Series(labels)


def main() -> None:
    import argparse

    ap = argparse.ArgumentParser(
        description="FM Cat 1 admissible-recovery test."
    )
    ap.add_argument(
        "--jsonl",
        type=Path,
        default=Path("runs/2026-05-11T22-12-32Z-target-c.jsonl"),
        help="Path to the FM run's per-case jsonl",
    )
    args = ap.parse_args()

    frame = _load_fm()
    print(f"FM eligible rows: {len(frame)}")

    # Same 50/50 stratified split as the FM orchestration script.
    target_df, _surprise_df = train_test_split(
        frame, test_size=0.50, random_state=SEED, stratify=frame["label"]
    )
    target_df = target_df.reset_index(drop=True)

    # Same outer split (orchestration uses 0.30 test).
    train_df, _ = train_test_split(
        target_df, test_size=0.30, random_state=SEED, stratify=target_df["label"]
    )
    X_train = train_df[FEATURE_COLS]
    y_train = train_df["label"]
    print(
        f"outer-train: {len(X_train)} rows "
        f"(grants={int(y_train.sum())}, denies={int((1-y_train).sum())})"
    )

    must_include = [c for c in ("fico_range_low", "dti") if c in FEATURE_COLS]
    optional = [c for c in FEATURE_COLS if c not in must_include]
    subsets = [tuple(FEATURE_COLS)]
    for drop in optional:
        subsets.append(tuple(c for c in FEATURE_COLS if c != drop))
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
        f"swept {len(sweep)}; admissible {len(admissible.admissible)}; "
        f"excluded {len(admissible.excluded)}"
    )

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

    cat1_X, cat1_y = _load_cat1(args.jsonl)
    n_cat1 = len(cat1_y)
    print(f"Cat 1 cases loaded: {n_cat1}")
    print(f"Cat 1 realized label distribution: {Counter(cat1_y.tolist())}")

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

    print("\nTop 10 admissible by Cat 1 deny-fraction:")
    for r in rows[:10]:
        print(
            f"  d={r['max_depth']:2d} leaf={r['min_samples_leaf']:4d} "
            f"subset_size={r['subset_size']} auc={r['holdout_auc']:.4f} "
            f"cat1_deny={r['cat1_deny_fraction']:.4f} "
            f"({r['n_cat1_correct']}/{n_cat1})"
        )

    print("\nBottom 5 admissible:")
    for r in rows[-5:]:
        print(
            f"  d={r['max_depth']:2d} leaf={r['min_samples_leaf']:4d} "
            f"subset_size={r['subset_size']} auc={r['holdout_auc']:.4f} "
            f"cat1_deny={r['cat1_deny_fraction']:.4f}"
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
