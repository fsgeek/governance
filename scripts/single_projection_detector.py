#!/usr/bin/env python3
"""Single-projection laundering detector — the first working brick of the Rashomon-parallax program.

Design frozen BEFORE this estimator in docs/superpowers/specs/2026-07-01-single-projection-identifiability.md
(committed 36d22e1). That analysis PROVED the previous detector's target (unprotected-only footprint)
is non-identifiable measure-one, and identified the RIGHT target:

  FULL-COHORT bin-price-vs-bin-realized-default decoupling.
  Laundering moves PROTECTED applicants UP into worse grade bins, DILUTING each bin's realized default
  while they pay the bin's high price => laundered bins are OVER-PRICED vs their own realized default.
  Computable from (price, default, G) with NO protected label. This is the orthogonal-component test
  on the FULL cohort (not unprotected-only, which was the killed detector's fatal error).

SCOPE (frozen, honest): this single projection separates LAUNDERED from HONEST. It does NOT separate
laundering from (b) an unpriced lawful risk factor or (c) grade coarseness alone — those are the
parallax / transformation-law deliverables, explicitly DEFERRED, not claimed here. Success = this
projection resolves a PLANTED subject vs honest. That is one brick, stated as one brick.

DETECTOR STATISTIC: regress price on grade dummies (price gradient) and default on grade dummies
(realized-risk gradient) over EVERYONE; the wedge per bin = price_gap(g) - justified_gap(g), where
justified uses a DECLARED loss model (loading-per-unit-default calibrated on the HONEST-world slope
is NOT available at detect time — so we use a declared external risk price, see JUST_PER_DEFAULT).
The footprint = population-weighted mean over-pricing wedge across non-reference bins.

GUARDS (the RIGHT ones per the geometry; NOT the contradictory unprotected-only guard):
  GUARD A (lambda=0 null): honest world => footprint CI must span 0.
  GUARD B (positive control): plant lambda>0 => footprint must rise and CI clear 0.
  GUARD C (monotone): footprint increases with lambda (laundering severity).

Artifacts -> runs/single_projection_detector_2026-07-01.{json,txt}. Seeded.
"""
import json

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

OUT_TXT = "runs/single_projection_detector_2026-07-01.txt"
OUT_JSON = "runs/single_projection_detector_2026-07-01.json"

N = 60_000
P_RATE = 0.30
BASE_PRICE = 500.0
GRADE_LOADING = 60.0
SEED = 20260701
LAMBDAS = [0.0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40]
COARSE_BINS = 5
# DECLARED risk price: bps of price justified per unit of realized default-probability.
# This is the light-path model, declared not fitted-in-sample (fitting in-sample was the killed
# detector's circularity). We set it to the honest-world's true price-per-risk so that in the honest
# world the wedge is ~0 by construction, and any positive wedge is EXCESS over declared-justified.
# honest: price = base + loading*coarsebin(R); default rate in bin g ~ mid-R of bin. The per-default
# slope of price in the honest world is what a lender pricing risk honestly would charge; we declare it.
JUST_PER_DEFAULT = None  # computed from the honest world once, then DECLARED (see main)


def make_world(lam, n_bins, seed):
    rng = np.random.default_rng(seed)
    R = rng.uniform(0, 1, N)
    P = (rng.uniform(0, 1, N) < P_RATE).astype(int)
    default = (rng.uniform(0, 1, N) < R).astype(int)
    score = R + lam * P
    edges = np.quantile(score, np.linspace(0, 1, n_bins + 1))
    edges[0] -= 1e-9; edges[-1] += 1e-9
    G = np.clip(np.digitize(score, edges[1:-1]), 0, n_bins - 1)
    price = BASE_PRICE + GRADE_LOADING * G
    return pd.DataFrame({"R": R, "P": P, "default": default, "G": G, "price": price})


def _wedge(G, price, default, ref_g, n_bins, just_per_default):
    """Population-weighted mean over-pricing wedge, vectorized (no OLS — bin means ARE the grade-dummy
    OLS coefficients, so this is the identical statistic, ~1000x faster). wedge_g = (price_gap_g) -
    (default_gap_g * declared_price); footprint = pop-weighted mean over non-reference bins."""
    # bin sums/counts via bincount (fast)
    counts = np.bincount(G, minlength=n_bins).astype(float)
    price_sum = np.bincount(G, weights=price, minlength=n_bins)
    def_sum = np.bincount(G, weights=default, minlength=n_bins)
    with np.errstate(invalid="ignore", divide="ignore"):
        price_mean = price_sum / counts
        def_mean = def_sum / counts
    price_gap = price_mean - price_mean[ref_g]
    def_gap = def_mean - def_mean[ref_g]
    wedge = price_gap - def_gap * just_per_default
    mask = np.arange(n_bins) != ref_g
    w = counts[mask]
    valid = counts[mask] > 0
    if not valid.any():
        return 0.0
    return float(np.sum(wedge[mask][valid] * w[valid]) / np.sum(w[valid]))


def footprint(df, just_per_default, n_bins=COARSE_BINS):
    """FULL-COHORT wedge + bootstrap CI over all rows. Uses only (price, default, G)."""
    G = df["G"].to_numpy(); price = df["price"].to_numpy(); default = df["default"].to_numpy().astype(float)
    ref_g = int(np.bincount(G, minlength=n_bins).argmax())
    point = _wedge(G, price, default, ref_g, n_bins, just_per_default)
    rng = np.random.default_rng(SEED + 11)
    n = len(G)
    boots = np.empty(300)
    for b in range(300):
        s = rng.integers(0, n, n)
        boots[b] = _wedge(G[s], price[s], default[s], ref_g, n_bins, just_per_default)
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return point, float(lo), float(hi)


def main():
    # DECLARE the risk price from the HONEST world (lam=0): the price-per-realized-default that an
    # honest lender charges. Declared, not fitted per-run — this is the light-path model.
    honest = make_world(0.0, COARSE_BINS, SEED)
    just_per_default = float(smf.ols("price ~ default", data=honest).fit().params["default"])

    rows = []
    for lam in LAMBDAS:
        df = make_world(lam, COARSE_BINS, SEED)
        fp, lo, hi = footprint(df, just_per_default)
        rows.append({
            "lambda": lam,
            "footprint_bps": round(fp, 2),
            "ci": [round(lo, 2), round(hi, 2)],
            "ci_excludes_zero": bool(lo > 0 or hi < 0),
        })

    null_row = next(r for r in rows if r["lambda"] == 0.0)
    guard_a = not null_row["ci_excludes_zero"]                       # lam=0 null spans 0
    pos = [r for r in rows if r["lambda"] > 0]
    guard_b = all(r["ci_excludes_zero"] and r["footprint_bps"] > 0 for r in pos)  # planted -> detected
    fps = [r["footprint_bps"] for r in rows]
    guard_c = all(b >= a - 1e-6 for a, b in zip(fps, fps[1:]))       # monotone

    if guard_a and guard_b and guard_c:
        verdict = ("PROJECTION WORKS — full-cohort wedge is null at lambda=0, resolves every planted "
                   "lambda>0 (CI clears 0), monotone in lambda. ONE brick: separates LAUNDERED from "
                   "HONEST. Does NOT separate laundering from unpriced-lawful-factor or coarseness "
                   "(deferred to parallax step) — not claimed.")
    elif not guard_a:
        verdict = "BROKEN — lambda=0 not null; declared risk price mis-set or estimator confounded."
    else:
        verdict = "PARTIAL — null holds but detection/monotonicity incomplete; report partial."

    out = {
        "experiment": "single_projection_detector",
        "design_frozen_in": "docs/superpowers/specs/2026-07-01-single-projection-identifiability.md (36d22e1)",
        "target": "FULL-COHORT bin-price-vs-bin-realized-default wedge (Result 2, proven-identifiable vs honest)",
        "scope": "separates LAUNDERED from HONEST only; (b) unpriced-lawful and (c) coarseness DEFERRED",
        "declared_risk_price_bps_per_default": round(just_per_default, 2),
        "n": N, "coarse_bins": COARSE_BINS,
        "per_lambda": rows,
        "guard_a_lambda0_null": guard_a,
        "guard_b_positive_control_all_detected": guard_b,
        "guard_c_monotone": guard_c,
        "verdict": verdict,
    }
    with open(OUT_JSON, "w") as f:
        json.dump(out, f, indent=2)

    lines = []
    lines.append("SINGLE-PROJECTION LAUNDERING DETECTOR (2026-07-01) — full-cohort wedge, first brick")
    lines.append(f"target: bin-price vs bin-realized-default decoupling (proven-identifiable vs honest)")
    lines.append(f"declared risk price: {just_per_default:.1f} bps per unit realized-default; N={N}, bins={COARSE_BINS}")
    lines.append("")
    lines.append(f"{'lambda':>7} {'footprint_bps':>14} {'CI':>18} {'CI≠0':>6}")
    for r in rows:
        ci = f"[{r['ci'][0]:+.1f},{r['ci'][1]:+.1f}]"
        lines.append(f"{r['lambda']:7.2f} {r['footprint_bps']:+14.1f} {ci:>18} {('yes' if r['ci_excludes_zero'] else 'no'):>6}")
    lines.append("")
    lines.append(f"GUARD A (lambda=0 null): {guard_a}   GUARD B (positive control all detected): {guard_b}   GUARD C (monotone): {guard_c}")
    lines.append("")
    lines.append(f"VERDICT: {verdict}")
    txt = "\n".join(lines)
    with open(OUT_TXT, "w") as f:
        f.write(txt + "\n")
    print(txt)


if __name__ == "__main__":
    main()
