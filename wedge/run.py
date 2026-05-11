"""CLI orchestration for the Rashomon wedge.

Pipeline:
  1. Load real data via the LendingClub collector for the given vintage.
  2. Optionally generate synthetic boundary cases via the synthetic collector.
  3. Build R(ε): hyperparameter sweep on the train hold-out, ε filter,
     diversity-weighted selection of n members.
  4. Re-fit the selected members on the full training set.
  5. For each eval case (real + synthetic), emit per-model (T, F, leaf)
     and extract per-component factor support (top-k features).
  6. Write the resulting Case records to a jsonl + metadata sidecar.

Usage:
  python -m wedge.run \\
      --csv path/to/lendingclub.csv \\
      --vintage 2015Q3 \\
      --term '36 months' \\
      --epsilon 0.02 \\
      --n-members 5 \\
      --top-k 5 \\
      --synthetic-n 200 \\
      --output-dir runs/
"""

from __future__ import annotations

import argparse
import datetime as dt
import uuid
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from policy.encoder import load_policy
from wedge.attribution import extract_factor_support
from wedge.collectors.lendingclub import (
    ORIGINATION_FEATURE_COLS,
    derive_label,
    filter_to_vintage,
    normalize_emp_length,
)
from wedge.collectors.synthetic import generate_boundary_cases
from wedge.indeterminacy import (
    LeafStatistics,
    compute_ioannidis_battery,
    compute_local_density,
)
from wedge.output import RunMetadata, write_run
from wedge.rashomon import (
    SweepConfig,
    evaluate_policy,
    filter_to_epsilon,
    hyperparameter_sweep,
    refit_members,
    select_diverse_members,
)
from wedge.types import Case, PerModelOutput


def _now_iso() -> str:
    return dt.datetime.now(tz=dt.timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")


def _to_case_real(row, vintage, feature_cols) -> Case:
    features = {col: (None if pd.isna(row[col]) else row[col]) for col in feature_cols}
    return Case(
        case_id=str(uuid.uuid4()),
        origin="real",
        synthetic_role=None,
        vintage=vintage,
        features=features,
        label=int(row["label"]),
        per_model=[],
    )


def _emit_per_model(model, case_features, top_k, leaf_stats=None):
    e = model.emit_for_case(case_features)
    fst, fsf = extract_factor_support(model, case_features, top_k=top_k)
    indeterminacy = []
    if leaf_stats is not None:
        indeterminacy.append(
            compute_local_density(case_features, e["leaf_id"], leaf_stats)
        )
    return PerModelOutput(
        model_id=model.model_id,
        T=e["T"],
        F=e["F"],
        factor_support_T=fst,
        factor_support_F=fsf,
        path=[],  # spec §11 keeps path optional in jsonl; populating it is iteration 2
        leaf=e["leaf"],
        indeterminacy=indeterminacy,
    )


def main() -> int:
    p = argparse.ArgumentParser(description="Run the Rashomon wedge.")
    p.add_argument("--csv", type=Path, required=True, help="LendingClub CSV path")
    p.add_argument("--vintage", default="2015Q3")
    p.add_argument("--term", default="36 months")
    p.add_argument("--epsilon", type=float, default=0.02)
    p.add_argument("--n-members", type=int, default=5)
    p.add_argument("--top-k", type=int, default=5)
    p.add_argument("--synthetic-n", type=int, default=200)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--output-dir", type=Path, default=Path("runs"))
    p.add_argument(
        "--policy",
        type=Path,
        default=None,
        help="Path to a policy-graph YAML (e.g. policy/thin_demo_hmda.yaml). "
        "When provided, evaluate_policy gates the sweep against mandatory/prohibited "
        "features and a post-fit split-use check (spec §2.7 OD-9b / OD-12). "
        "When omitted, the sweep runs unconstrained.",
    )
    args = p.parse_args()

    # 1. Load real data.
    df = pd.read_csv(args.csv)
    df = filter_to_vintage(df, vintage=args.vintage, term=args.term)
    df["label"] = derive_label(df["loan_status"])
    if "emp_length" in df.columns:
        df["emp_length"] = normalize_emp_length(df["emp_length"])
    feature_cols = [c for c in ORIGINATION_FEATURE_COLS if c in df.columns]

    # 2. Train/eval split.
    train_df, eval_df = train_test_split(
        df, test_size=0.30, random_state=args.seed, stratify=df["label"]
    )
    X_train, y_train = train_df[feature_cols], train_df["label"]

    # Build feature subsets that always retain the must-include features
    # (FICO and DTI per spec §5: "operationally non-optional in any
    # realistic underwriting model") and vary the optional ones to give the
    # diversity-selection algorithm a third axis with non-zero range.
    must_include = [c for c in ("fico_range_low", "dti") if c in feature_cols]
    optional = [c for c in feature_cols if c not in must_include]

    # Subsets: full, drop-each-optional-one-at-a-time. If there are no
    # optional features, fall back to (full,).
    subsets: list[tuple[str, ...]] = [tuple(feature_cols)]
    for drop in optional:
        subsets.append(tuple(c for c in feature_cols if c != drop))
    feature_subsets = tuple(subsets)

    # 3. Build R(ε) via the three-phase pipeline (spec §2.7 OD-9b / OD-12):
    #    sweep -> evaluate_policy -> filter_to_epsilon -> select_diverse_members.
    cfg = SweepConfig(
        max_depths=(4, 6, 8, 10, 12),
        min_samples_leafs=(25, 50, 100, 200, 400),
        feature_subsets=feature_subsets,
        random_state=args.seed,
        holdout_fraction=0.30,
    )
    policy_constraints = load_policy(args.policy) if args.policy else None
    sweep = hyperparameter_sweep(X_train, y_train, config=cfg)
    admissible_set = evaluate_policy(sweep, policy_constraints=policy_constraints)
    epsilon_set = filter_to_epsilon(admissible_set, epsilon=args.epsilon)
    members = select_diverse_members(epsilon_set.within_epsilon, n=args.n_members)
    fitted = refit_members(X_train, y_train, members=members, random_state=args.seed)

    # Audit trail: print the three-phase summary so a human running the wedge
    # sees policy exclusions and ε-band attrition immediately.
    print(
        f"sweep: {admissible_set.total_swept} combos | "
        f"policy-admissible: {len(admissible_set.admissible)} | "
        f"policy-excluded: {len(admissible_set.excluded)}"
    )
    if admissible_set.excluded:
        from collections import Counter
        reason_labels = Counter(
            er.reason.split(":")[0] for er in admissible_set.excluded
        )
        for label, count in sorted(reason_labels.items()):
            print(f"  excluded ({label}): {count}")
    print(
        f"ε-band ε={args.epsilon} vs admissible_best={epsilon_set.global_best_auc:.4f}: "
        f"within={len(epsilon_set.within_epsilon)} | out={len(epsilon_set.out_of_epsilon)} | "
        f"selected={len(members)}"
    )

    # Per-model leaf statistics for the local_density I species (computed once
    # on the full training set, queried per case).
    leaf_stats_by_model = {
        m.model_id: LeafStatistics.fit(m, X_train) for m in fitted
    }

    # 4. Build eval cases (real + synthetic).
    real_cases: list[Case] = []
    for _, row in eval_df.iterrows():
        real_cases.append(_to_case_real(row, args.vintage, feature_cols))
    synthetic_cases = generate_boundary_cases(
        train_df[feature_cols + ["label"]],
        n=args.synthetic_n,
        vintage=args.vintage,
        seed=args.seed + 7,
    )

    # 5a. Compute case-level (model-independent) I species for every eval case.
    #     Ioannidis battery only at this iteration; multivariate_coherence
    #     and retrospective species deferred per the 2026-05-08 memo.
    for case in [*real_cases, *synthetic_cases]:
        case.case_indeterminacy.extend(compute_ioannidis_battery(case.features))

    # 5b. Emit per-model outputs (T, F, factor support, model-dependent I).
    for case in [*real_cases, *synthetic_cases]:
        for model in fitted:
            case.per_model.append(
                _emit_per_model(
                    model,
                    case.features,
                    args.top_k,
                    leaf_stats=leaf_stats_by_model[model.model_id],
                )
            )

    # 6. Write run.
    meta = RunMetadata(
        run_id=_now_iso(),
        vintage=args.vintage,
        epsilon=args.epsilon,
        random_seed=args.seed,
        members=[
            {
                "model_id": f.model_id,
                "max_depth": f.tree.max_depth,
                "min_samples_leaf": f.tree.min_samples_leaf,
                "feature_subset": list(f.feature_subset),
                "holdout_auc": m.holdout_auc,
            }
            for f, m in zip(fitted, members)
        ],
        notes=f"vintage={args.vintage} term={args.term} epsilon={args.epsilon}",
    )
    jsonl_path, meta_path = write_run(
        real_cases + synthetic_cases, meta, output_dir=args.output_dir
    )
    print(f"wrote {jsonl_path}")
    print(f"wrote {meta_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
