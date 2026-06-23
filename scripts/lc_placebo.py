#!/usr/bin/env python3
"""Arm C (placebo / artifact detector) — does the default-justified-excess benchmark INVENT a
young-end gradient on a band column with NO age content?

Frozen pre-reg: docs/superpowers/specs/2026-06-23-cross-substrate-falsification-prereg.md
If the placebo reproduces the real LC +134bps young-end excess on PERMUTED tenure or an age-neutral
field, the machinery is artifact-generating and BOTH the committed LC result and any Arm-A finding
are suspect -> HALT (kill-condition K-C1). If placebo ~0, the method is trustworthy.

Two placebos, both reuse the EXACT corpus benchmark (band_excess_corpus keys on `age_band`):
  P1 PERMUTED TENURE: shuffle est_age across rows, re-band. Destroys any est_age<->row alignment
     while preserving the marginal band-size distribution. The real +134 must NOT survive this.
  P2 AGE-NEUTRAL FIELD: band loan_amnt into 10 quantiles, treat as pseudo-age bands. A field with
     no inherent age ordering must show ~0 excess in its band-0.

Glue + I/O only; statistics live in the tested wedge/age_grade_default.py.
"""
import json
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, ".")
from scripts.age_pricing_residual import load  # noqa: E402
from wedge.age_grade_default import band_excess_corpus, predicted_default  # noqa: E402
from wedge.age_residual import AGE_BANDS  # noqa: E402

OUT_TXT = "runs/lc_placebo_2026-06-23.txt"
OUT_JSON = "runs/lc_placebo_2026-06-23.json"
SEED = 0
PLACEBO_TOL_BPS = 30.0  # frozen: |young-analog excess| must be < this for the placebo to PASS


def quantile_bands(series: pd.Series, n: int = 10) -> pd.Series:
    """Band a continuous field into n quantile bins labelled 0..n-1 (band 0 = lowest values),
    mirroring the 10 age bands so band_excess_corpus's age_band keying works unchanged."""
    bands = pd.qcut(series, q=n, labels=False, duplicates="drop")
    return pd.Series(bands, index=series.index).astype(int)


def fmt(res, label0="band 0"):
    lines = []
    for i in range(len(AGE_BANDS)):
        if i not in res.band_bps:
            continue
        bps = res.band_bps[i]
        lo, hi = res.band_ci.get(i, (float("nan"), float("nan")))
        n = res.n_per_band.get(i, 0)
        tag = f"  <- {label0}" if i == 0 else ""
        lines.append(f"  band {i:>2} n={n:>7}  excess={bps:+8.1f} bps  CI=[{lo:+8.1f},{hi:+8.1f}]{tag}")
    return "\n".join(lines)


def main():
    df = load()
    df["default"] = (df["loan_status"] == "Charged Off").astype(int)
    p_hat = predicted_default(df)  # computed once; placebos differ only in the BAND column
    out, payload = [], {"n_total": int(len(df)), "tol_bps": PLACEBO_TOL_BPS}

    out.append("LC PLACEBO (Arm C) — does the benchmark invent a young-end gradient on no-age-content "
               "bands? (2026-06-23)")
    out.append(f"Source: LC resolved loans, N={len(df)}. Real result to NOT reproduce: young +134 bps.")
    out.append(f"FROZEN: placebo PASSES if |band-0 excess| < {PLACEBO_TOL_BPS} bps (CI includes 0). "
               "K-C1: if a placebo shows ~+134, machinery is artifact-generating -> HALT.")
    out.append("")

    verdicts = {}

    # ---- P1: permuted tenure ----
    d1 = df.copy()
    rng = np.random.default_rng(SEED)
    d1["age_band"] = df["age_band"].to_numpy()[rng.permutation(len(df))]  # shuffle band labels
    r1 = band_excess_corpus(d1, map_kind="isotonic", p_hat=p_hat)
    b0_1 = r1.band_bps.get(0, float("nan"))
    lo1, hi1 = r1.band_ci.get(0, (float("nan"), float("nan")))
    pass1 = abs(b0_1) < PLACEBO_TOL_BPS and (lo1 <= 0 <= hi1)
    out.append("[P1] PERMUTED-TENURE bands (real age signal destroyed by shuffle):")
    out.append(fmt(r1, "shuffled band 0"))
    out.append(f"  -> band-0 excess = {b0_1:+.1f} bps, CI=[{lo1:+.1f},{hi1:+.1f}]  "
               f"PLACEBO {'PASS' if pass1 else 'FAIL (K-C1 HALT)'}")
    out.append("")
    verdicts["P1_permuted_tenure"] = {"band0_bps": b0_1, "ci": [lo1, hi1], "pass": bool(pass1)}

    # ---- P2: age-neutral field (loan_amnt deciles) ----
    d2 = df.copy()
    d2["age_band"] = quantile_bands(df["loan_amnt"], n=10)
    r2 = band_excess_corpus(d2, map_kind="isotonic", p_hat=p_hat)
    b0_2 = r2.band_bps.get(0, float("nan"))
    lo2, hi2 = r2.band_ci.get(0, (float("nan"), float("nan")))
    # loan_amnt may legitimately carry SOME pricing signal; the placebo claim is only that it must
    # NOT manufacture a +134-scale young-end overcharge. Report the value; flag only a +134-scale hit.
    big2 = abs(b0_2) > 100.0
    out.append("[P2] AGE-NEUTRAL FIELD bands (loan_amnt deciles as pseudo-age):")
    out.append(fmt(r2, "smallest-loan band 0"))
    out.append(f"  -> band-0 excess = {b0_2:+.1f} bps, CI=[{lo2:+.1f},{hi2:+.1f}]  "
               f"{'+134-SCALE HIT (K-C1 concern)' if big2 else 'no +134-scale artifact'}")
    out.append("  (note: loan_amnt may carry real pricing signal; the test is only that it does not "
               "MANUFACTURE a +134-scale young-end overcharge from nothing.)")
    out.append("")
    verdicts["P2_loan_amnt"] = {"band0_bps": b0_2, "ci": [lo2, hi2], "plus134_scale": bool(big2)}

    # ---- overall ----
    halt = (not pass1) or big2
    out.append("VERDICT (Arm C):")
    out.append(f"  P1 permuted-tenure: {'PASS' if pass1 else 'FAIL'} (band-0 {b0_1:+.0f} bps). "
               "The real +134 does NOT reproduce on shuffled age." if pass1 else
               f"  P1 permuted-tenure: FAIL — band-0 {b0_1:+.0f} bps on shuffled age. K-C1 HALT.")
    out.append(f"  P2 loan_amnt: band-0 {b0_2:+.0f} bps — "
               f"{'+134-scale artifact present (K-C1 concern)' if big2 else 'no +134-scale artifact'}.")
    out.append(f"  => Method is {'ARTIFACT-GENERATING — HALT before Arm A' if halt else 'TRUSTWORTHY — proceed to Arm A'}.")
    payload["verdicts"] = verdicts
    payload["halt"] = bool(halt)

    with open(OUT_TXT, "w") as fh:
        fh.write("\n".join(out) + "\n")
    with open(OUT_JSON, "w") as fh:
        json.dump(payload, fh, indent=2, default=float)
    print("\n".join(out))
    print(f"\nWrote {OUT_TXT}, {OUT_JSON}  (halt={halt})")


if __name__ == "__main__":
    main()
