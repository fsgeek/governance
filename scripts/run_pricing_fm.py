"""Pricing-space within-rate-band stratification on Fannie Mae (FM pilot).

The FM analog of the LC pricing run. LC publishes a discrete `sub_grade`;
FM hands you the continuous original interest rate. The "tier" here is the
rate-band: orig_interest_rate, deciled within the acquisition file. The
question is the same as the LC version:

    For each rate-band, is there a policy-expressible feature that partitions
    the band's loans into sub-populations with significantly different
    realized default rates?

Cat 2 / Cat 2-extension / Cat 1 (pricing) taxonomy carries over, with
`policy/thin_demo_fm.yaml`'s named features (fico_range_low, dti, ltv) as
the policy-expressible set.

Run across a regime-spanning set of FM acquisition quarters (extract each
from Performance_All.zip first) for the cross-regime arm of the pricing-
space result. The rate-bands are deciled *within each vintage*, so a band
index means "this position in this vintage's pricing distribution" — the
right comparison when the rate level shifts across regimes.

Usage:
    PYTHONPATH=. python scripts/run_pricing_fm.py --vintage 2018Q1 --n-bands 10 --output-dir runs

`--vintage YYYYQN` selects `data/fanniemae/{vintage}.csv` (extract it from
Performance_All.zip first) and tags the output filenames. Running the same
analysis across a regime-spanning set of vintages is the cross-regime arm
of the pricing-space result.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from collections import Counter
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd

from wedge.collectors.fanniemae import (
    derive_origination_and_label,
    filter_eligible,
    read_raw,
    to_feature_frame,
)
from wedge.pricing import GradeStratification, classify_grades


FM_DATA_DIR = Path("data/fanniemae")
# Features named by policy/thin_demo_fm.yaml (its threshold/mandatory nodes).
POLICY_FEATURES = {"fico_range_low", "dti", "ltv"}
# Other numeric origination features available in to_feature_frame's output
# that the thin demo FM policy does not name.
EXTENSION_FEATURES = ["loan_term_months"]
ALL_FEATURES = sorted(POLICY_FEATURES) + EXTENSION_FEATURES


def _now_iso() -> str:
    return dt.datetime.now(tz=dt.timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")


def _rate_band_labels(rate: pd.Series, n_bands: int) -> pd.Series:
    """Assign each loan a rate-band label ('rb00'..'rbNN') by quantile of the
    original interest rate. Ties are broken by `pd.qcut`'s default behavior;
    duplicate edges are dropped (fewer bands than requested if the rate is
    coarse)."""
    try:
        codes = pd.qcut(rate, q=n_bands, labels=False, duplicates="drop")
    except ValueError:
        # Degenerate (e.g. all-equal rates): single band.
        codes = pd.Series(np.zeros(len(rate), dtype=int), index=rate.index)
    return codes.map(lambda c: f"rb{int(c):02d}" if pd.notna(c) else None)


def main() -> int:
    ap = argparse.ArgumentParser(description="FM pricing-space within-rate-band stratification.")
    ap.add_argument("--vintage", default="2018Q1",
                    help="FM acquisition quarter; reads data/fanniemae/{vintage}.csv")
    ap.add_argument("--n-bands", type=int, default=10)
    ap.add_argument("--alpha", type=float, default=0.01)
    ap.add_argument("--min-loans-per-grade", type=int, default=2000)
    ap.add_argument("--min-loans-per-side", type=int, default=500)
    ap.add_argument("--output-dir", type=Path, default=Path("runs"))
    args = ap.parse_args()

    fm_csv = FM_DATA_DIR / f"{args.vintage}.csv"
    if not fm_csv.exists():
        raise FileNotFoundError(
            f"{fm_csv} not found — extract it first: "
            f"unzip data/fanniemae/Performance_All.zip {args.vintage}.csv -d data/fanniemae/"
        )
    print(f"loading FM {args.vintage} from {fm_csv} (a few minutes; large perf file)...")
    raw = read_raw(fm_csv)
    collapsed = derive_origination_and_label(raw)
    eligible = filter_eligible(collapsed)
    feats = to_feature_frame(eligible).copy()
    print(f"FM eligible rows: {len(feats)}")

    cols = ["fico_range_low", "dti", "ltv", "loan_term_months", "orig_interest_rate", "label"]
    feats = feats[[c for c in cols if c in feats.columns]]
    feats = feats.dropna(subset=["orig_interest_rate", "label"]).reset_index(drop=True)
    print(
        f"after dropna(rate, label): {len(feats)} loans; "
        f"default rate {float((feats['label'] == 0).mean()):.4f}; "
        f"rate range [{feats['orig_interest_rate'].min():.3f}, {feats['orig_interest_rate'].max():.3f}]"
    )

    feats["rate_band"] = _rate_band_labels(feats["orig_interest_rate"], args.n_bands)
    feats = feats.dropna(subset=["rate_band"]).reset_index(drop=True)
    band_counts = feats["rate_band"].value_counts().sort_index()
    print(f"rate bands ({feats['rate_band'].nunique()}): "
          + ", ".join(f"{b}:n={n}" for b, n in band_counts.items()))

    feature_cols = [c for c in ALL_FEATURES if c in feats.columns]
    strat = GradeStratification.compute(
        feats,
        grade_col="rate_band",
        label_col="label",
        feature_cols=feature_cols,
        policy_features=POLICY_FEATURES,
        alpha=args.alpha,
        min_loans_per_grade=args.min_loans_per_grade,
        min_loans_per_side=args.min_loans_per_side,
    )
    classes = classify_grades(strat)
    cat_counts = Counter(classes.values())
    print(f"\nrate-band classification: {dict(cat_counts)}")
    print(f"significant within-band splits: {len(strat.splits)}")

    if strat.splits:
        top = sorted(strat.splits, key=lambda s: s.gap, reverse=True)[:10]
        print("\nTop splits by default-rate gap:")
        for s in top:
            tag = "POLICY" if s.policy_expressible else "extension"
            print(
                f"  {s.grade}  {s.feature}@{s.threshold:.4g}  "
                f"lo={s.default_rate_lo:.4f}(n={s.n_lo})  "
                f"hi={s.default_rate_hi:.4f}(n={s.n_hi})  "
                f"gap={s.gap:.4f}  p={s.p_value:.2e}  [{tag}]"
            )
        print(f"\nsplit feature frequency: {dict(Counter(s.feature for s in strat.splits))}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    run_id = _now_iso()
    jsonl_path = args.output_dir / f"{run_id}-pricing-fm-{args.vintage}.jsonl"
    summary_path = args.output_dir / f"{run_id}-pricing-fm-{args.vintage}-summary.json"
    with jsonl_path.open("w") as fh:
        for s in strat.splits:
            fh.write(json.dumps(asdict(s)) + "\n")
    summary = {
        "run_id": run_id,
        "substrate": f"FM-{args.vintage}",
        "n_loans": len(feats),
        "n_rate_bands": int(feats["rate_band"].nunique()),
        "n_bands_requested": args.n_bands,
        "default_rate": float((feats["label"] == 0).mean()),
        "features": feature_cols,
        "policy_features": sorted(POLICY_FEATURES),
        "alpha": args.alpha,
        "min_loans_per_grade": args.min_loans_per_grade,
        "min_loans_per_side": args.min_loans_per_side,
        "band_loan_counts": strat.grade_loan_counts,
        "band_default_rate": strat.grade_default_rate,
        "band_classification": classes,
        "category_counts": dict(cat_counts),
        "n_significant_splits": len(strat.splits),
        "split_feature_frequency": dict(Counter(s.feature for s in strat.splits)),
    }
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True))
    print(f"\nwrote {jsonl_path}")
    print(f"wrote {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
