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
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from wedge.attribution import extract_factor_support
from wedge.collectors.lendingclub import (
    ORIGINATION_FEATURE_COLS,
    derive_label,
    filter_to_vintage,
)
from wedge.collectors.synthetic import generate_boundary_cases
from wedge.output import RunMetadata, write_run
from wedge.rashomon import SweepConfig, build_rashomon_set, refit_members
from wedge.types import Case, PerModelOutput


def _now_iso() -> str:
    return dt.datetime.now(tz=dt.timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")


def _to_case_real(row, vintage, feature_cols) -> Case:
    import uuid
    features = {col: row[col] for col in feature_cols}
    return Case(
        case_id=str(uuid.uuid4()),
        origin="real",
        synthetic_role=None,
        vintage=vintage,
        features=features,
        label=int(row["label"]),
        per_model=[],
    )


def _emit_per_model(model, case_features, top_k):
    e = model.emit_for_case(case_features)
    fst, fsf = extract_factor_support(model, case_features, top_k=top_k)
    return PerModelOutput(
        model_id=model.model_id,
        T=e["T"],
        F=e["F"],
        factor_support_T=fst,
        factor_support_F=fsf,
        path=[],  # spec §11 keeps path optional in jsonl; populating it is iteration 2
        leaf=e["leaf"],
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
    args = p.parse_args()

    # 1. Load real data.
    df = pd.read_csv(args.csv)
    df = filter_to_vintage(df, vintage=args.vintage, term=args.term)
    df["label"] = derive_label(df["loan_status"])
    feature_cols = [c for c in ORIGINATION_FEATURE_COLS if c in df.columns]

    # 2. Train/eval split.
    train_df, eval_df = train_test_split(
        df, test_size=0.30, random_state=args.seed, stratify=df["label"]
    )
    X_train, y_train = train_df[feature_cols], train_df["label"]
    X_eval, y_eval = eval_df[feature_cols], eval_df["label"]

    # 3. Build R(ε).
    cfg = SweepConfig(
        max_depths=(4, 6, 8, 10, 12),
        min_samples_leafs=(25, 50, 100, 200, 400),
        feature_subsets=(tuple(feature_cols),),
        random_state=args.seed,
        holdout_fraction=0.30,
    )
    members = build_rashomon_set(
        X_train, y_train, config=cfg, epsilon=args.epsilon, n_members=args.n_members
    )
    fitted = refit_members(X_train, y_train, members=members, random_state=args.seed)

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

    # 5. Emit per-model outputs for every eval case.
    for case in [*real_cases, *synthetic_cases]:
        for model in fitted:
            case.per_model.append(_emit_per_model(model, case.features, args.top_k))

    # 6. Write run.
    meta = RunMetadata(
        run_id=_now_iso(),
        vintage=args.vintage,
        epsilon=args.epsilon,
        random_seed=args.seed,
        members=[
            {
                "model_id": m.model_id,
                "max_depth": m.tree.max_depth,
                "min_samples_leaf": m.tree.min_samples_leaf,
                "feature_subset": list(m.feature_subset),
            }
            for m in fitted
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
