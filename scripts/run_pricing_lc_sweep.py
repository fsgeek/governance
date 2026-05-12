"""LC pricing-space stratification — temporal sweep across vintages.

Runs the within-grade stratification (`wedge/pricing.py`) on every LendingClub
36-month vintage from 2008Q1 to 2015Q4 (later vintages' terminal-loan subset
over-represents early defaults — the cohort hasn't matured by the 2018Q4 data
cut — so they are excluded from the clean sweep). For each vintage, reports the
per-vintage Cat 1 / Cat 2 / Cat 2-extension / underpowered breakdown and the
dominant recovered feature.

Question this answers: is the within-tier structure (Cat 2 (pricing)) a stable
property across 2008–2015, or does it spike around 2014–2015 — which would
suggest the load-bearing LC-DTI positive is a lender-specific underwriting-
loosening episode (LC's 2016 scandal-era cohorts), not a persistent
miscalibration? It is the temporal version of the per-vintage "N tiers conflate
named-factor strata, M are defensible" breakdown.

Usage:
    PYTHONPATH=. python scripts/run_pricing_lc_sweep.py
    PYTHONPATH=. python scripts/run_pricing_lc_sweep.py --term '60 months' \
        --first 2010Q1 --last 2013Q4
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import pandas as pd

from wedge.collectors.lendingclub import (
    derive_label,
    filter_to_vintage,
    normalize_emp_length,
)
from wedge.pricing import GradeStratification, classify_grades

CSV_PATH = Path("data/accepted_2007_to_2018Q4.csv")

# Same partition as scripts/run_pricing_lc.py.
POLICY_FEATURES = {"fico_range_low", "dti", "annual_inc", "emp_length"}
EXTENSION_FEATURES = [
    "revol_util", "open_acc", "inq_last_6mths", "delinq_2yrs",
    "total_acc", "mort_acc", "loan_amnt", "revol_bal", "pub_rec",
]
ALL_FEATURES = sorted(POLICY_FEATURES) + EXTENSION_FEATURES


def _coerce_numeric(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s.astype(str).str.strip().str.rstrip("%"), errors="coerce")


def _quarters(first: str, last: str) -> list[str]:
    fy, fq = int(first[:4]), int(first[5])
    ly, lq = int(last[:4]), int(last[5])
    out = []
    y, q = fy, fq
    while (y, q) <= (ly, lq):
        out.append(f"{y}Q{q}")
        q += 1
        if q > 4:
            q, y = 1, y + 1
    return out


def _prep(raw: pd.DataFrame, vintage: str, term: str) -> pd.DataFrame:
    df = raw.copy()
    df = filter_to_vintage(df, vintage=vintage, term=term)
    if df.empty:
        return df
    df["label"] = derive_label(df["loan_status"])
    if "emp_length" in df.columns:
        df["emp_length"] = normalize_emp_length(df["emp_length"])
    for c in EXTENSION_FEATURES + ["fico_range_low", "dti", "annual_inc"]:
        if c in df.columns:
            df[c] = _coerce_numeric(df[c])
    df = df.dropna(subset=["label", "sub_grade"]).reset_index(drop=True)
    keep = df["sub_grade"].apply(
        lambda s: isinstance(s, str) and len(s) == 2 and s[0] in "ABCDEFG" and s[1] in "12345"
    )
    return df[keep].reset_index(drop=True)


def main() -> int:
    ap = argparse.ArgumentParser(description="LC pricing-space stratification temporal sweep.")
    ap.add_argument("--term", default="36 months")
    ap.add_argument("--first", default="2008Q1")
    ap.add_argument("--last", default="2015Q4")
    ap.add_argument("--alpha", type=float, default=0.01)
    ap.add_argument("--min-loans-per-grade", type=int, default=300)
    ap.add_argument("--min-loans-per-side", type=int, default=100)
    ap.add_argument("--output-dir", type=Path, default=Path("runs"))
    args = ap.parse_args()

    needed = ["issue_d", "term", "loan_status", "sub_grade", *POLICY_FEATURES, *EXTENSION_FEATURES]
    print(f"Reading {CSV_PATH} (columns only)...", flush=True)
    raw = pd.read_csv(CSV_PATH, usecols=lambda c: c in needed, low_memory=False)
    print(f"  raw rows: {len(raw)}", flush=True)

    vintages = _quarters(args.first, args.last)
    print(f"\n{'vintage':>8}  {'n_loans':>8}  {'def_rate':>8}  {'tested':>4}  "
          f"{'Cat2':>4}  {'Cat2x':>5}  {'Cat1':>4}  {'underpwr':>8}  dominant_feature  split_feat_freq", flush=True)
    rows = []
    for vintage in vintages:
        df = _prep(raw, vintage, args.term)
        if df.empty or len(df) < args.min_loans_per_grade:
            print(f"{vintage:>8}  {'(skip: too few loans)':>40}", flush=True)
            continue
        feature_cols = [c for c in ALL_FEATURES if c in df.columns]
        strat = GradeStratification.compute(
            df, grade_col="sub_grade", label_col="label", feature_cols=feature_cols,
            policy_features=POLICY_FEATURES, alpha=args.alpha,
            min_loans_per_grade=args.min_loans_per_grade,
            min_loans_per_side=args.min_loans_per_side,
        )
        classes = classify_grades(strat)
        cat = Counter(classes.values())
        n_testable = sum(1 for v in classes.values() if v != "underpowered")
        feat_freq = Counter(s.feature for s in strat.splits)
        dom = feat_freq.most_common(1)[0][0] if feat_freq else "-"
        def_rate = float((df["label"] == 0).mean())
        c2 = cat.get("Cat 2 (pricing)", 0)
        c2x = cat.get("Cat 2-extension (pricing)", 0)
        c1 = cat.get("Cat 1 (pricing)", 0)
        up = cat.get("underpowered", 0)
        print(f"{vintage:>8}  {len(df):>8}  {def_rate:>8.4f}  {n_testable:>4}  "
              f"{c2:>4}  {c2x:>5}  {c1:>4}  {up:>8}  {dom:>16}  {dict(feat_freq.most_common())}",
              flush=True)
        rows.append({
            "vintage": vintage, "n_loans": len(df), "default_rate": round(def_rate, 5),
            "n_sub_grades": int(df["sub_grade"].nunique()), "n_testable_grades": n_testable,
            "cat2_pricing": c2, "cat2_extension": c2x, "cat1_pricing": c1, "underpowered": up,
            "cat2_share_of_testable": round(c2 / n_testable, 4) if n_testable else None,
            "n_significant_splits": len(strat.splits),
            "dominant_recovered_feature": dom,
            "split_feature_frequency": dict(feat_freq.most_common()),
            "grade_classification": classes,
        })

    # Summary line.
    if rows:
        shares = [r["cat2_share_of_testable"] for r in rows if r["cat2_share_of_testable"] is not None]
        doms = Counter(r["dominant_recovered_feature"] for r in rows)
        print(f"\nCat-2-(pricing) share of testable grades across {len(rows)} vintages: "
              f"min={min(shares):.3f} max={max(shares):.3f} "
              f"mean={sum(shares)/len(shares):.3f}", flush=True)
        print(f"dominant recovered feature, by vintage count: {dict(doms.most_common())}", flush=True)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    term_tag = args.term.split()[0]
    out = args.output_dir / f"pricing-lc-sweep-{term_tag}mo-summary.json"
    out.write_text(json.dumps({
        "term": args.term, "first": args.first, "last": args.last,
        "alpha": args.alpha, "min_loans_per_grade": args.min_loans_per_grade,
        "min_loans_per_side": args.min_loans_per_side,
        "policy_features": sorted(POLICY_FEATURES),
        "note": ("Late vintages excluded: the Fully-Paid/Charged-Off subset over-represents "
                 "early-terminating loans for cohorts that have not matured by the 2018Q4 data cut."),
        "vintages": rows,
    }, indent=2))
    print(f"\nwrote {out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
