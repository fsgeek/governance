"""End-to-end dual-set orchestration on V_2 (Target C per spec §7.2).

The orchestration ties together the V1 mechanism: train a surprise model on
a lifecycle-completed cohort, build the original dual-set R_T(ε_T) /
R_F(ε_F) and the surprise-revised dual-set R_T'(ε_T) / R_F'(ε_F) on V_2,
classify each V_2 failure via the Cat 1 / Cat 2 / ambiguous criterion, and
emit the construction manifest plus a per-case jsonl.

Exposed as a pure Python function so callers can run it on either a real
data vintage or on a synthetic fixture (via tests). A thin `main()` CLI
at the bottom of this module is invokable as `python -m wedge.orchestration`.

The orchestration is deliberately conservative about claims: Cat 2 yield
is empirically uncertain (the 2026-05-11 smoke on LC 2015Q4 showed weak
signal, AUC≈0.63). The function records the classification distribution
faithfully; consumers (Task 11 writeup) read it as it is.
"""
from __future__ import annotations

import datetime as dt
import json
import uuid
from dataclasses import asdict
from pathlib import Path
from typing import Any, Optional

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from policy.encoder import PolicyConstraints
from wedge.categories import CaseClassification, RefitSet, classify_case
from wedge.i_pred import compute_i_pred
from wedge.manifest import emit_manifest, write_manifest
from wedge.models import CartModel
from wedge.rashomon import (
    EpsilonAdmissibleSet,
    SweepConfig,
    SweepResult,
    build_dual_set,
    evaluate_policy,
    hyperparameter_sweep,
    inner_split,
    refit_members,
    select_diverse_members,
)
from wedge.surprise import (
    compute_outcome_surprise,
    predict_p_grant,
    train_surprise_model,
)


def _now_iso() -> str:
    return dt.datetime.now(tz=dt.timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")


def _union_refit(
    set_a_members: list[SweepResult],
    set_a_models: list[CartModel],
    set_b_members: list[SweepResult],
    set_b_models: list[CartModel],
) -> RefitSet:
    """Union two (members, models) pairs by spec equality, preserving order.

    Order: every member of `set_a_*` first, then members of `set_b_*` whose
    spec is not already present. Alignment between results[i] and models[i]
    is preserved (RefitSet contract).
    """
    a_specs = {m.spec for m in set_a_members}
    results: list[SweepResult] = list(set_a_members)
    models: list[CartModel] = list(set_a_models)
    for sr, mdl in zip(set_b_members, set_b_models):
        if sr.spec in a_specs:
            continue
        results.append(sr)
        models.append(mdl)
    return RefitSet(results=results, models=models)


def _select_and_refit(
    epsilon_set: EpsilonAdmissibleSet,
    *,
    n: int,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    seed: int,
) -> tuple[list[SweepResult], list[CartModel]]:
    """Diversity-select n members from the ε-band and refit on (X_train, y_train).

    Returns aligned (members, refits). Empty ε-band yields ([], []).
    """
    members = select_diverse_members(epsilon_set.within_epsilon, n=n)
    if not members:
        return [], []
    refits = refit_members(X_train, y_train, members=members, random_state=seed)
    return members, refits


def _case_features(row: pd.Series, feature_cols: list[str]) -> dict[str, Any]:
    return {col: (None if pd.isna(row[col]) else row[col]) for col in feature_cols}


def _classification_to_json(c: CaseClassification) -> dict[str, Any]:
    """JSON-serializable form of a CaseClassification."""
    d = asdict(c)
    # Numpy int/float guards (asdict can carry numpy scalars through).
    for k, v in d.items():
        if isinstance(v, (np.integer,)):
            d[k] = int(v)
        elif isinstance(v, (np.floating,)):
            d[k] = float(v)
    return d


def run_dual_set_target_c(
    *,
    df_target: pd.DataFrame,
    df_surprise_train: pd.DataFrame,
    feature_cols: list[str],
    target_vintage_label: str,
    surprise_vintage_label: str,
    output_dir: Path,
    policy_constraints: Optional[PolicyConstraints] = None,
    epsilon_T: float = 0.05,
    epsilon_F: float = 0.05,
    w_T: float = 1.5,
    w_F: float = 1.5,
    n_members: int = 5,
    seed: int = 0,
    sweep_config: Optional[SweepConfig] = None,
    hypothesis_space: str = (
        "depth-bounded CART under cost-asymmetric loss; "
        "feature-subset diversification over optional features"
    ),
    run_id: Optional[str] = None,
) -> dict[str, Any]:
    """Run the V1 dual-set mechanism on `df_target`, write artifacts to `output_dir`.

    Returns a summary dict with paths and aggregate counts; the on-disk
    artifacts are the load-bearing deliverable (Target C).

    Both DataFrames must contain `feature_cols` plus a 'label' column
    (binary, grant-as-positive per spec §2.7 OD-9a/OD-13). The caller
    constructs both — typically via the LendingClub collector for one
    vintage block apiece.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    run_id = run_id or _now_iso()

    # Step 1: outer split on V₂ (train models on outer-train, classify cases
    # on outer-eval). Stratify on label to keep the eval set balanced enough
    # for AUC + classification.
    train_df, oos_df = train_test_split(
        df_target, test_size=0.30, random_state=seed, stratify=df_target["label"]
    )
    X_train = train_df[feature_cols]
    y_train = train_df["label"]

    # Step 2: train surprise model S on the lifecycle-completed cohort.
    X_surprise = df_surprise_train[feature_cols]
    y_surprise = df_surprise_train["label"]
    surprise_model = train_surprise_model(
        X_surprise, y_surprise, random_state=seed
    )
    surprise_meta = {
        "model_id": f"HistGBC_isotonic_cv5_seed{seed}",
        "training_sample_id": surprise_vintage_label,
        "n_training_rows": len(df_surprise_train),
    }

    # Step 3: build sweep config — same shape as wedge.run.main() for parity.
    if sweep_config is None:
        must_include = [c for c in ("fico_range_low", "dti") if c in feature_cols]
        optional = [c for c in feature_cols if c not in must_include]
        subsets: list[tuple[str, ...]] = [tuple(feature_cols)]
        for drop in optional:
            subsets.append(tuple(c for c in feature_cols if c != drop))
        cfg = SweepConfig(
            max_depths=(4, 6, 8, 10, 12),
            min_samples_leafs=(25, 50, 100, 200, 400),
            feature_subsets=tuple(subsets),
            random_state=seed,
            holdout_fraction=0.30,
        )
    else:
        cfg = sweep_config

    # Step 4: recover sweep's inner holdout features so surprise weights
    # align row-for-row with each SweepResult.holdout_y_true. Same call,
    # same args — `inner_split` is sweep's split factored out.
    _, X_holdout_inner, _, y_holdout_inner = inner_split(X_train, y_train, config=cfg)
    p_grant_holdout = predict_p_grant(surprise_model, X_holdout_inner)
    surprise = compute_outcome_surprise(
        p_grant=p_grant_holdout, realized_label=y_holdout_inner.to_numpy()
    )
    sample_weights = np.abs(surprise)

    # Step 5: sweep + policy filter.
    sweep_results = hyperparameter_sweep(X_train, y_train, config=cfg)
    admissible_set = evaluate_policy(sweep_results, policy_constraints=policy_constraints)

    # Step 6: build BOTH dual-sets on the same admissible pool.
    R_T, R_F = build_dual_set(
        admissible_set, epsilon_T=epsilon_T, epsilon_F=epsilon_F, w_T=w_T, w_F=w_F
    )
    R_T_prime, R_F_prime = build_dual_set(
        admissible_set,
        epsilon_T=epsilon_T,
        epsilon_F=epsilon_F,
        w_T=w_T,
        w_F=w_F,
        sample_weights=sample_weights,
    )

    # Step 7: diversity-select + refit each band on the full outer-train.
    rt_members, rt_refits = _select_and_refit(
        R_T, n=n_members, X_train=X_train, y_train=y_train, seed=seed
    )
    rf_members, rf_refits = _select_and_refit(
        R_F, n=n_members, X_train=X_train, y_train=y_train, seed=seed
    )
    rt_prime_members, rt_prime_refits = _select_and_refit(
        R_T_prime, n=n_members, X_train=X_train, y_train=y_train, seed=seed
    )
    rf_prime_members, rf_prime_refits = _select_and_refit(
        R_F_prime, n=n_members, X_train=X_train, y_train=y_train, seed=seed
    )

    original_set = _union_refit(rt_members, rt_refits, rf_members, rf_refits)
    revised_set = _union_refit(
        rt_prime_members, rt_prime_refits, rf_prime_members, rf_prime_refits
    )

    # Step 8: per-case I_pred under original (R_T, R_F) + classification.
    jsonl_path = output_dir / f"{run_id}-target-c.jsonl"
    category_counts: dict[str, int] = {
        "Cat 1": 0,
        "Cat 2": 0,
        "ambiguous": 0,
        "not_failure": 0,
    }
    i_pred_above_threshold = 0
    n_oos = 0
    I_PRED_FLAG_THRESHOLD = 0.2
    with jsonl_path.open("w") as fh:
        for _, row in oos_df.iterrows():
            feats = _case_features(row, feature_cols)
            realized = int(row["label"])
            i_pred = (
                compute_i_pred(rt_refits, rf_refits, feats)
                if rt_refits and rf_refits
                else float("nan")
            )
            classification = classify_case(
                feats,
                case_id=str(uuid.uuid4()),
                original_set=original_set,
                revised_set=revised_set,
                realized_outcome=realized,
            )
            category_counts[classification.category] += 1
            if not np.isnan(i_pred) and i_pred > I_PRED_FLAG_THRESHOLD:
                i_pred_above_threshold += 1
            n_oos += 1
            record = {
                "case_id": classification.case_id,
                "vintage": target_vintage_label,
                "in_regime": True,  # V1: regime gating is informational; OD-11 deferred
                "features": feats,
                "realized_outcome": realized,
                "i_pred": None if np.isnan(i_pred) else float(i_pred),
                "classification": _classification_to_json(classification),
            }
            fh.write(json.dumps(record, default=str) + "\n")

    # Step 9: manifest (original construction). Spec §3.6 records the
    # *first-pass* construction; the surprise-revised set is recorded as the
    # set-revision step inside the per-case classification records, not as a
    # second manifest. A separate revised manifest could be added in V1.1.
    manifest_path = output_dir / f"{run_id}-target-c-manifest.json"
    manifest = emit_manifest(
        R_T=R_T,
        R_F=R_F,
        policy_constraints=policy_constraints
        or PolicyConstraints(
            name="unconstrained",
            version="0",
            status="none",
            monotonicity_map={},
            mandatory_features=(),
            prohibited_features=(),
            applicable_regime={},
        ),
        w_T=w_T,
        w_F=w_F,
        surprise_model_metadata=surprise_meta,
        run_id=run_id,
        training_sample_id=target_vintage_label,
        hypothesis_space=hypothesis_space,
    )
    # Augment with revised-set summary so the manifest also names the
    # surprise-revised construction (audit-only, not a V1 required field).
    manifest["revised_set_summary"] = {
        "score_label_T_prime": R_T_prime.score_label,
        "score_label_F_prime": R_F_prime.score_label,
        "epsilon_T_prime": R_T_prime.epsilon,
        "epsilon_F_prime": R_F_prime.epsilon,
        "n_R_T_prime": len(R_T_prime.within_epsilon),
        "n_R_F_prime": len(R_F_prime.within_epsilon),
    }
    write_manifest(manifest, manifest_path)

    return {
        "run_id": run_id,
        "jsonl_path": str(jsonl_path),
        "manifest_path": str(manifest_path),
        "n_oos_cases": n_oos,
        "category_counts": category_counts,
        "i_pred_above_threshold": i_pred_above_threshold,
        "i_pred_threshold": I_PRED_FLAG_THRESHOLD,
        "admissible_count": len(admissible_set.admissible),
        "excluded_count": len(admissible_set.excluded),
        "n_R_T": len(R_T.within_epsilon),
        "n_R_F": len(R_F.within_epsilon),
        "n_R_T_prime": len(R_T_prime.within_epsilon),
        "n_R_F_prime": len(R_F_prime.within_epsilon),
        "surprise_weight_mean": float(sample_weights.mean()),
        "surprise_weight_max": float(sample_weights.max()),
    }


def _load_lc_block(csv_path: Path, *, vintages: list[str], term: str) -> pd.DataFrame:
    """Concatenate filtered LC origination data across multiple vintages."""
    from wedge.collectors.lendingclub import (
        ORIGINATION_FEATURE_COLS,
        derive_label,
        filter_to_vintage,
        normalize_emp_length,
    )

    raw = pd.read_csv(csv_path, low_memory=False)
    parts = [filter_to_vintage(raw, vintage=v, term=term) for v in vintages]
    df = pd.concat(parts, ignore_index=True) if parts else raw.iloc[0:0]
    # De-fragment before column assignment to silence pandas' high-fragmentation
    # warning on wide LC frames.
    df = df.copy()
    df["label"] = derive_label(df["loan_status"])
    if "emp_length" in df.columns:
        df["emp_length"] = normalize_emp_length(df["emp_length"])
    feature_cols = [c for c in ORIGINATION_FEATURE_COLS if c in df.columns]
    return df[feature_cols + ["label"]].dropna(subset=["label"]).reset_index(drop=True)


def main() -> int:
    """CLI for the Target C dual-set orchestration.

    Loads two LC vintage blocks (the target V_2 and the surprise training cohort),
    runs the orchestration, prints a summary, and writes jsonl + manifest into
    `--output-dir`.
    """
    import argparse

    from policy.encoder import load_policy

    p = argparse.ArgumentParser(
        description="Target C dual-set run on a target LC vintage."
    )
    p.add_argument("--csv", type=Path, required=True, help="LendingClub CSV path")
    p.add_argument("--target-vintage", default="2015Q4")
    p.add_argument(
        "--surprise-vintages",
        nargs="+",
        default=["2016Q1", "2016Q2", "2016Q3", "2016Q4"],
        help="Quarters used to train the surprise model S",
    )
    p.add_argument("--term", default="36 months")
    p.add_argument("--epsilon-T", type=float, default=0.05)
    p.add_argument("--epsilon-F", type=float, default=0.05)
    p.add_argument("--w-T", type=float, default=1.5)
    p.add_argument("--w-F", type=float, default=1.5)
    p.add_argument("--n-members", type=int, default=5)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--output-dir", type=Path, default=Path("runs"))
    p.add_argument(
        "--policy",
        type=Path,
        default=None,
        help="Policy-graph YAML; when omitted, the sweep is unconstrained",
    )
    args = p.parse_args()

    target_df = _load_lc_block(args.csv, vintages=[args.target_vintage], term=args.term)
    surprise_df = _load_lc_block(args.csv, vintages=args.surprise_vintages, term=args.term)

    from wedge.collectors.lendingclub import ORIGINATION_FEATURE_COLS

    feature_cols = [c for c in ORIGINATION_FEATURE_COLS if c in target_df.columns]
    policy = load_policy(args.policy) if args.policy else None

    surprise_label = ",".join(args.surprise_vintages)
    summary = run_dual_set_target_c(
        df_target=target_df,
        df_surprise_train=surprise_df,
        feature_cols=feature_cols,
        target_vintage_label=args.target_vintage,
        surprise_vintage_label=f"lc-{surprise_label}-{args.term.replace(' ', '_')}",
        output_dir=args.output_dir,
        policy_constraints=policy,
        epsilon_T=args.epsilon_T,
        epsilon_F=args.epsilon_F,
        w_T=args.w_T,
        w_F=args.w_F,
        n_members=args.n_members,
        seed=args.seed,
    )

    print(f"run_id: {summary['run_id']}")
    print(f"jsonl: {summary['jsonl_path']}")
    print(f"manifest: {summary['manifest_path']}")
    print(
        f"target rows={len(target_df)} surprise rows={len(surprise_df)} "
        f"oos cases={summary['n_oos_cases']}"
    )
    print(
        f"admissible={summary['admissible_count']} "
        f"excluded={summary['excluded_count']}"
    )
    print(
        f"|R_T|={summary['n_R_T']} |R_F|={summary['n_R_F']} "
        f"|R_T'|={summary['n_R_T_prime']} |R_F'|={summary['n_R_F_prime']}"
    )
    print(
        f"category_counts: {summary['category_counts']}  "
        f"I_pred>{summary['i_pred_threshold']}: {summary['i_pred_above_threshold']}"
    )
    print(
        f"surprise weight mean={summary['surprise_weight_mean']:.4f} "
        f"max={summary['surprise_weight_max']:.4f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
