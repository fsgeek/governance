"""Pricing-space dual-set analog on a LendingClub vintage (option 4).

Runs the within-grade stratification (`wedge/pricing.py`) on LC accepted-loan
data: for each `sub_grade`, is there a feature that partitions the tier's
loans into sub-populations with significantly different realized default
rates? Splits on features named by the thin demo HMDA policy are
"Cat 2 (pricing)" (the policy should have used the factor better); splits on
features the policy does not name are "Cat 2-extension (pricing)" (the policy
should name the factor); grades with no significant split (and adequate
power) are "Cat 1 (pricing)" (the grading is as fine as the governed
vocabulary allows).

Usage:
    PYTHONPATH=. python scripts/run_pricing_lc.py --vintage 2015Q3 \\
        --term '36 months' --output-dir runs
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from dataclasses import asdict
from pathlib import Path

import pandas as pd

from wedge.collectors.lendingclub import (
    derive_label,
    filter_to_vintage,
    normalize_emp_length,
)
from wedge.pricing import GradeStratification, classify_grades


CSV_PATH = Path("data/accepted_2007_to_2018Q4.csv")

# Features named by the thin demo HMDA policy (policy/thin_demo_hmda.yaml):
# the decision graph's threshold/mandatory features. A within-grade split on
# one of these is a "the grade should have used this factor better" finding.
POLICY_FEATURES = {"fico_range_low", "dti", "annual_inc", "emp_length"}

# Standard LC underwriting fields NOT in the thin demo policy. A within-grade
# split on one of these is a "the policy should name this factor" finding.
EXTENSION_FEATURES = [
    "revol_util",
    "open_acc",
    "inq_last_6mths",
    "delinq_2yrs",
    "total_acc",
    "mort_acc",
    "loan_amnt",
    "revol_bal",
    "pub_rec",
]

ALL_FEATURES = sorted(POLICY_FEATURES) + EXTENSION_FEATURES


def _now_iso() -> str:
    return dt.datetime.now(tz=dt.timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")


def _coerce_numeric(s: pd.Series) -> pd.Series:
    """Robust numeric coercion: strips a trailing '%' if present."""
    return pd.to_numeric(
        s.astype(str).str.strip().str.rstrip("%"), errors="coerce"
    )


def _load_lc_priced(vintage: str, term: str) -> pd.DataFrame:
    needed = [
        "issue_d", "term", "loan_status", "sub_grade", "grade", "int_rate",
        *POLICY_FEATURES, *EXTENSION_FEATURES,
    ]
    raw = pd.read_csv(CSV_PATH, low_memory=False)
    cols = [c for c in needed if c in raw.columns]
    df = raw[cols].copy()
    df = filter_to_vintage(df, vintage=vintage, term=term)
    df["label"] = derive_label(df["loan_status"])
    if "emp_length" in df.columns:
        df["emp_length"] = normalize_emp_length(df["emp_length"])
    for c in EXTENSION_FEATURES + ["int_rate", "fico_range_low", "dti", "annual_inc"]:
        if c in df.columns:
            df[c] = _coerce_numeric(df[c])
    return df.dropna(subset=["label", "sub_grade"]).reset_index(drop=True)


def main() -> int:
    ap = argparse.ArgumentParser(description="Pricing-space stratification on LC.")
    ap.add_argument("--vintage", default="2015Q3")
    ap.add_argument("--term", default="36 months")
    ap.add_argument("--alpha", type=float, default=0.01)
    ap.add_argument("--min-loans-per-grade", type=int, default=300)
    ap.add_argument("--min-loans-per-side", type=int, default=100)
    ap.add_argument("--output-dir", type=Path, default=Path("runs"))
    args = ap.parse_args()

    df = _load_lc_priced(args.vintage, args.term)
    feature_cols = [c for c in ALL_FEATURES if c in df.columns]
    print(f"LC {args.vintage} {args.term}: {len(df)} terminal loans; "
          f"{df['sub_grade'].nunique()} sub-grades; features: {feature_cols}")

    strat = GradeStratification.compute(
        df,
        grade_col="sub_grade",
        label_col="label",
        feature_cols=feature_cols,
        policy_features=POLICY_FEATURES,
        alpha=args.alpha,
        min_loans_per_grade=args.min_loans_per_grade,
        min_loans_per_side=args.min_loans_per_side,
    )
    classes = classify_grades(strat)

    from collections import Counter
    cat_counts = Counter(classes.values())
    print(f"grade classification: {dict(cat_counts)}")
    print(f"significant within-grade splits: {len(strat.splits)}")

    if strat.splits:
        top = sorted(strat.splits, key=lambda s: s.gap, reverse=True)[:10]
        print("\nTop 10 splits by default-rate gap:")
        for s in top:
            tag = "POLICY" if s.policy_expressible else "extension"
            print(
                f"  {s.grade}  {s.feature}@{s.threshold:.3g}  "
                f"lo={s.default_rate_lo:.3f}(n={s.n_lo})  "
                f"hi={s.default_rate_hi:.3f}(n={s.n_hi})  "
                f"gap={s.gap:.3f}  p={s.p_value:.2e}  [{tag}]"
            )
        feat_counts = Counter(s.feature for s in strat.splits)
        print(f"\nsplit feature frequency: {dict(feat_counts.most_common())}")

    # Artifacts.
    args.output_dir.mkdir(parents=True, exist_ok=True)
    run_id = _now_iso()
    jsonl_path = args.output_dir / f"{run_id}-pricing-lc-{args.vintage}.jsonl"
    summary_path = args.output_dir / f"{run_id}-pricing-lc-{args.vintage}-summary.json"
    with jsonl_path.open("w") as fh:
        for s in strat.splits:
            fh.write(json.dumps(asdict(s)) + "\n")
    summary = {
        "run_id": run_id,
        "vintage": args.vintage,
        "term": args.term,
        "n_loans": len(df),
        "n_sub_grades": int(df["sub_grade"].nunique()),
        "features": feature_cols,
        "policy_features": sorted(POLICY_FEATURES),
        "alpha": args.alpha,
        "min_loans_per_grade": args.min_loans_per_grade,
        "min_loans_per_side": args.min_loans_per_side,
        "grade_classification": classes,
        "category_counts": dict(cat_counts),
        "n_significant_splits": len(strat.splits),
        "grade_loan_counts": strat.grade_loan_counts,
        "grade_default_rate": strat.grade_default_rate,
        "split_feature_frequency": dict(Counter(s.feature for s in strat.splits)),
    }
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True))
    print(f"\nwrote {jsonl_path}")
    print(f"wrote {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
