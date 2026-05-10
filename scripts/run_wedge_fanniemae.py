"""Run the wedge pipeline on Fannie Mae data.

Mirrors wedge/run.py but swaps the LendingClub loader for the Fannie Mae
collector. Different feature space (FICO + DTI + LTV + loan_term, no
annual_inc/emp_length) and different label (ever-90+DPD-in-24mo, not
charge-off) — but the middle of the pipeline (Rashomon construction,
attribution, factor support) is feature-list-agnostic.

Synthetic boundary cases are skipped for this first run; the silence
analysis only needs real cases.

Usage:
    python scripts/run_wedge_fanniemae.py \\
        --path data/fanniemae/2018Q1.csv \\
        --vintage FM-2018Q1 \\
        --nrows 1000000 \\
        --epsilon 0.02 \\
        --n-members 5
"""
from __future__ import annotations

import argparse
import datetime as dt
import math
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from wedge.attribution import extract_factor_support
from wedge.collectors.fanniemae import load_fanniemae
from wedge.indeterminacy import (
    LeafStatistics,
    compute_ioannidis_battery,
    compute_local_density,
)
from wedge.output import RunMetadata, write_run
from wedge.rashomon import SweepConfig, build_rashomon_set, refit_members
from wedge.types import Case, PerModelOutput

NUMERIC_FEATURES = ("fico_range_low", "dti", "ltv", "loan_term_months")


def _now_iso() -> str:
    return dt.datetime.now(tz=dt.timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")


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
        path=[],
        leaf=e["leaf"],
        indeterminacy=indeterminacy,
    )


def _cases_to_train_frame(cases: list[Case]) -> pd.DataFrame:
    """Project Case.features to a DataFrame with NUMERIC_FEATURES + label.

    Drops rows missing any required numeric feature or label.
    """
    rows = []
    for c in cases:
        f = c.features
        row = {k: f.get(k) for k in NUMERIC_FEATURES}
        row["label"] = c.label
        rows.append(row)
    df = pd.DataFrame(rows)
    df = df.dropna(subset=list(NUMERIC_FEATURES) + ["label"])
    df["label"] = df["label"].astype(int)
    return df


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--path", type=Path, default=Path("data/fanniemae/2018Q1.csv"))
    p.add_argument("--vintage", default="FM-2018Q1")
    p.add_argument("--nrows", type=int, default=1_000_000,
                   help="cap raw performance rows read (one loan has many rows)")
    p.add_argument("--horizon-months", type=int, default=24)
    p.add_argument("--epsilon", type=float, default=0.02)
    p.add_argument("--n-members", type=int, default=5)
    p.add_argument("--top-k", type=int, default=5)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--output-dir", type=Path, default=Path("runs"))
    p.add_argument("--max-eval", type=int, default=30_000,
                   help="cap eval cases to keep per-model attribution tractable")
    args = p.parse_args()

    print(f"loading fanniemae {args.path} (nrows={args.nrows})...", flush=True)
    cases = load_fanniemae(
        args.path,
        horizon_months=args.horizon_months,
        nrows=args.nrows,
        vintage=args.vintage,
    )
    print(f"  {len(cases)} cases after collapse + eligibility filter", flush=True)
    if not cases:
        print("ERROR: no cases survived eligibility filter")
        return 1

    train_frame = _cases_to_train_frame(cases)
    print(f"  {len(train_frame)} cases with complete numeric features",
          flush=True)
    print(f"  charge-off / 90+DPD label rate: {train_frame['label'].mean():.4f}",
          flush=True)

    feature_cols = list(NUMERIC_FEATURES)
    train_df, eval_df = train_test_split(
        train_frame, test_size=0.30, random_state=args.seed,
        stratify=train_frame["label"],
    )
    X_train, y_train = train_df[feature_cols], train_df["label"]

    must_include = ["fico_range_low", "dti"]
    optional = [c for c in feature_cols if c not in must_include]
    subsets: list[tuple[str, ...]] = [tuple(feature_cols)]
    for drop in optional:
        subsets.append(tuple(c for c in feature_cols if c != drop))
    feature_subsets = tuple(subsets)

    print("building Rashomon set...", flush=True)
    cfg = SweepConfig(
        max_depths=(4, 6, 8, 10, 12),
        min_samples_leafs=(25, 50, 100, 200, 400),
        feature_subsets=feature_subsets,
        random_state=args.seed,
        holdout_fraction=0.30,
    )
    members = build_rashomon_set(
        X_train, y_train, config=cfg, epsilon=args.epsilon,
        n_members=args.n_members,
    )
    fitted = refit_members(X_train, y_train, members=members, random_state=args.seed)
    print(f"  fitted {len(fitted)} members "
          f"(holdout AUC {[round(m.holdout_auc, 4) for m in members]})", flush=True)

    leaf_stats_by_model = {
        m.model_id: LeafStatistics.fit(m, X_train) for m in fitted
    }

    eval_subset = eval_df.head(args.max_eval) if len(eval_df) > args.max_eval else eval_df
    print(f"emitting per-model output on {len(eval_subset)} eval cases...", flush=True)

    real_cases: list[Case] = []
    import uuid
    for _, row in eval_subset.iterrows():
        features = {c: (None if pd.isna(row[c]) else float(row[c])) for c in feature_cols}
        real_cases.append(Case(
            case_id=str(uuid.uuid4()),
            origin="real",
            synthetic_role=None,
            vintage=args.vintage,
            features=features,
            label=int(row["label"]),
            per_model=[],
        ))

    for case in real_cases:
        case.case_indeterminacy.extend(compute_ioannidis_battery(case.features))

    for case in real_cases:
        for model in fitted:
            case.per_model.append(_emit_per_model(
                model, case.features, args.top_k,
                leaf_stats=leaf_stats_by_model[model.model_id],
            ))

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
        notes=f"fanniemae path={args.path} nrows={args.nrows} "
              f"horizon={args.horizon_months} epsilon={args.epsilon}",
    )
    jsonl_path, meta_path = write_run(real_cases, meta, output_dir=args.output_dir)
    print(f"wrote {jsonl_path}")
    print(f"wrote {meta_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
