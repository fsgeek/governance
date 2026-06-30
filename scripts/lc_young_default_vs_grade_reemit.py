#!/usr/bin/env python3
"""Re-emit the LC young-default-vs-grade result as JSON (clears the txt-only provenance debt).

The 2026-06-23 young-default-vs-grade result (commit 061301d) produced runs/lc_young_default_vs_grade_
2026-06-23.txt but NO machine-readable JSON — the only result in the age-pricing arc without one (see
the qhaway provenance-debt memo). This runner reproduces those numbers from the same matured-vintage LC
load path and emits runs/lc_young_default_vs_grade_2026-06-23.json so every headline number in the arc
is artifact-backed and machine-readable. Method byte-for-byte matches the txt: matured 2011-2014,
default=loss>0.01, young=[18,25) (age_band 0), net-of-grade OLS via wedge.young_default_vs_grade.

It also emits the 2012-13 replication CI [0.67,1.99] that lived only in the memo (un-artifacted).
"""
import json
import sys

sys.path.insert(0, ".")
from scripts.age_realized_return import load  # noqa: E402  (the shared matured-data loader)
from wedge.young_default_vs_grade import (  # noqa: E402
    within_grade_default_gap, net_of_grade_young_default,
)

OUT_JSON = "runs/lc_young_default_vs_grade_2026-06-23.json"
PRIME = ["A", "B", "C"]
SUBPRIME = ["D", "E", "F", "G"]


def matured(df):
    """Matured 2011-2014 (>=95% resolved; survivorship-robust per the realized-return correction)."""
    return df[df["issue_year"].isin([2011, 2012, 2013, 2014])].copy()


def fit_block(df):
    pooled = net_of_grade_young_default(df, grades=None)
    prime = net_of_grade_young_default(df, grades=PRIME)
    subprime = net_of_grade_young_default(df, grades=SUBPRIME)
    gaps = within_grade_default_gap(df)
    return pooled, prime, subprime, gaps


def main():
    df = matured(load())
    pooled, prime, subprime, gaps = fit_block(df)

    # 2012-13 replication (the CI that lived only in the memo).
    df_1213 = df[df["issue_year"].isin([2012, 2013])].copy()
    prime_1213 = net_of_grade_young_default(df_1213, grades=PRIME)

    payload = {
        "experiment": "lc_young_default_vs_grade",
        "reemit_note": "JSON re-emit of the 2026-06-23 txt-only result (provenance debt cleared "
                       "2026-06-29). Method matches runs/lc_young_default_vs_grade_2026-06-23.txt.",
        "source": "data/accepted_2007_to_2018Q4.csv, resolved, matured issue_year 2011-2014",
        "default_proxy": "loss > 0.01",
        "young_band": "[18,25) (age_band 0)",
        "n_matured": int(len(df)),
        "pooled_net_of_grade": pooled,
        "prime_ABC": prime,
        "subprime_DG": subprime,
        "prime_ABC_2012_13_replication": prime_1213,
        "within_grade_gap": gaps,
    }
    with open(OUT_JSON, "w") as f:
        json.dump(payload, f, indent=2, default=float)

    print(f"N matured = {len(df):,}")
    print(f"pooled net-of-grade young = {pooled['young_above_grade_pp']:+.2f}pp "
          f"CI[{pooled['ci'][0]:+.2f},{pooled['ci'][1]:+.2f}]")
    print(f"PRIME A/B/C   = {prime['young_above_grade_pp']:+.2f}pp "
          f"CI[{prime['ci'][0]:+.2f},{prime['ci'][1]:+.2f}]  n={prime['n']:,}")
    print(f"  2012-13 repl = {prime_1213['young_above_grade_pp']:+.2f}pp "
          f"CI[{prime_1213['ci'][0]:+.2f},{prime_1213['ci'][1]:+.2f}]  (was memo-only)")
    print(f"SUBPRIME D-G  = {subprime['young_above_grade_pp']:+.2f}pp "
          f"CI[{subprime['ci'][0]:+.2f},{subprime['ci'][1]:+.2f}]  n={subprime['n']:,}")
    print(f"JSON -> {OUT_JSON}")


if __name__ == "__main__":
    main()
