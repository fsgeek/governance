#!/usr/bin/env python3
"""Fairwash-detection calibration floor — does a lawful-axis footprint detector resolve laundering?

THE DEVICE (assembled with Tony 2026-06-30): lawful disparity is the un-concealed CALIBRATION
source; fairwashing of an UNLAWFUL (protected) signal into a coarse lawful instrument leaves a
SPILLOVER FOOTPRINT on the lawful axis, landing on the UNPROTECTED co-riders who share the coarse
instrument; therefore a calibrated wedge detector run on the LAWFUL axis, UNPROTECTED-only, can
detect concealed laundering WITHOUT EVER TOUCHING THE PROTECTED ATTRIBUTE. This script tests the
load-bearing empirical question the prior-art scout cannot answer: novelty-open != detectable.
Does the footprint resolve above noise, and at what laundering magnitude does the detector floor out?

This is a CONTROLLED synthetic calibration (hypothetical-scenario grade, NOT a back-test). The whole
point is ground truth I set, so the detector can be measured against a known answer.

THE DGP (I control it; the spillover must EMERGE, never be hand-planted — see GUARD 1):
  R   ~ U(0,1)              true latent risk (continuous)
  P   ~ Bernoulli(0.3)      protected attribute (the thing we may NOT observe at detect time)
  default ~ Bernoulli(R)    realized outcome depends ONLY on true risk R (P is NOT a real risk factor)
  G (lawful grade) = coarse bin of a LAUNDERED risk score:
        score = R + lambda * P            <- lambda is the FAIRWASH knob: protected pushed to worse
        G = digitize(score, n_bins)          score independent of realized risk. lambda=0 => clean.
  price = base + grade_loading * G          price is set off the (contaminated) grade, NOT off R.
The SPILLOVER is emergent: because G is COARSE, laundering protected applicants into worse bins drags
the UNPROTECTED applicants sharing those bins to a higher grade-average => unprotected get over-priced
relative to their OWN realized default. Nothing adds a spillover term by hand.

THE DETECTOR (the lawful-axis footprint reader; uses ONLY G, price, default — never P):
  on the UNPROTECTED subpopulation, regress price on grade dummies, then compare each grade's price
  to the realized-default-justified price for that grade. footprint = mean over-pricing of unprotected
  applicants NOT explained by their realized default. (Same realized-risk-decoupling wedge as the SBA
  decoupling test, run attribute-free.)

FROZEN SUCCESS CRITERION (before any run):
  WORKS  <=> footprint(unprotected) is monotone-increasing in lambda AND its CI excludes 0 at some
             lambda* ; sensitivity floor = smallest lambda where the unprotected footprint CI clears 0.
  USELESS <=> footprint stays within noise across the lambda range even as the DIRECT protected
             disparity grows large (real-in-principle, sub-threshold-in-practice).

RESULT (2026-06-30): DETECTOR KILLED BY ITS OWN FROZEN GUARDS — do not trust this estimator.
  All three guards tripped: GUARD 2 FAILED (lambda=0 reports +50bps [49,51], confident footprint in a
  CLEAN world); footprint ANTI-monotone (50->100->...->87, falls as laundering rises); GUARD 1 FAILED
  (fine-grade footprint +386..+971bps, an order of magnitude LARGER, opposite of the coarseness-kills
  prediction). ROOT CAUSE (the exact failure pre-registered before the run): the "justified" baseline
  subtracts default_gap * (cohort price~default slope), but in a DGP where price is set OFF GRADE, that
  slope is induced by grade<->default correlation, not real risk-pricing — same circularity as the SBA
  binary-flag yardstick caught earlier the same day. The +50bps at lambda=0 IS the grade-price gradient
  mis-credited as a fairwash footprint. CONSEQUENCE: this run says NOTHING about whether a real footprint
  resolves; the hypothesis is NOT refuted, the MEASURING INSTRUMENT is. UNSOLVED DESIGN PROBLEM exposed:
  a field detector has ONE loan tape — no clean lambda=0 world to subtract — so the signal must be
  INTRINSIC to one surface. Candidate (UNVALIDATED, do not build on momentum): test whether the
  unprotected price-gradient across grades is PROPORTIONAL to the default-gradient (honest) or has a
  component ORTHOGONAL to it (laundered) — a shape test needing no baseline world. Left for a fresh run
  with the adversary hired BEFORE the next satisfying sentence.

THREE FROZEN GUARDS (each could fool me; named before running):
  GUARD 1 (no hand-planted spillover): spillover emerges from coarseness x lambda. FALSIFIER: at FINE
    grade granularity (n_bins large) the footprint must VANISH even at high lambda. If refining the
    instrument kills the footprint, coarseness was genuinely the mechanism. Run both coarse & fine.
  GUARD 2 (lambda=0 null): no laundering => no footprint. A footprint at lambda=0 = broken estimator,
    not a discovery. lambda=0 row must have CI spanning 0.
  GUARD 3 (footprint is not protected-disparity leaking through): measured on STRICTLY unprotected
    (P==0) rows only; P never enters the detector. Unprotected have zero P-signal by construction.

Artifacts -> runs/fairwash_calibration_floor_2026-06-30.{json,txt}. Seeded; no Math.random.
"""
import json

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

OUT_TXT = "runs/fairwash_calibration_floor_2026-06-30.txt"
OUT_JSON = "runs/fairwash_calibration_floor_2026-06-30.json"

N = 60_000
P_RATE = 0.30
BASE_PRICE = 500.0       # bps
GRADE_LOADING = 60.0     # bps of price per grade-bin step (the lawful pricing gradient)
SEED = 20260630
LAMBDAS = [0.0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40]
COARSE_BINS = 5          # the coarse lawful instrument (grade A-E analog)
FINE_BINS = 50           # GUARD 1 falsifier: refine the instrument, footprint should die


def make_world(lam, n_bins, seed):
    """Generate the synthetic world for a given laundering lambda and grade granularity."""
    rng = np.random.default_rng(seed)
    R = rng.uniform(0, 1, N)
    P = (rng.uniform(0, 1, N) < P_RATE).astype(int)
    default = (rng.uniform(0, 1, N) < R).astype(int)   # realized outcome depends ONLY on R
    score = R + lam * P                                 # laundering: P pushed into the score
    # grade = coarse bin of the (contaminated) score; bin edges over the score's realized range
    edges = np.quantile(score, np.linspace(0, 1, n_bins + 1))
    edges[0] -= 1e-9; edges[-1] += 1e-9
    G = np.clip(np.digitize(score, edges[1:-1]), 0, n_bins - 1)
    price = BASE_PRICE + GRADE_LOADING * G             # price set off contaminated grade, NOT off R
    return pd.DataFrame({"R": R, "P": P, "default": default, "G": G, "price": price})


def footprint_unprotected(df):
    """Detector: on UNPROTECTED rows only, the mean over-pricing not justified by realized default.
    Uses ONLY G, price, default. Never reads P (P used here solely to SELECT the unprotected cohort,
    which is GUARD 3's by-construction control, not a detector input).
    Returns (footprint_bps, ci_lo, ci_hi) via grade-level over-pricing vs realized-default-justified.
    """
    d = df[df["P"] == 0].copy()
    # realized-risk-justified price per grade: regress price on realized default within the cohort,
    # then the grade over-pricing is the part of the grade price gradient NOT tracked by default.
    # footprint = mean_g [ price_gap(g) - default_justified_gap(g) ], weighted by grade population.
    ref_g = int(d["G"].mode().iloc[0])  # most-populated grade as reference
    d["_g"] = pd.Categorical(d["G"])
    m_price = smf.ols(f"price ~ C(_g, Treatment(reference={ref_g}))", data=d).fit()
    m_def = smf.ols(f"default ~ C(_g, Treatment(reference={ref_g}))", data=d).fit()
    # justified bps per unit default-prob: the cohort's own price-on-default slope (its risk pricing).
    slope = smf.ols("price ~ default", data=d).fit().params["default"]
    grades = sorted(d["G"].unique())
    pops = d["G"].value_counts(normalize=True).to_dict()
    wedges, weights = [], []
    for g in grades:
        if g == ref_g:
            continue
        t = f"C(_g, Treatment(reference={ref_g}))[T.{g}]"
        if t not in m_price.params.index:
            continue
        price_gap = m_price.params[t]
        def_gap = m_def.params.get(t, 0.0)
        justified = def_gap * slope
        wedges.append(price_gap - justified)
        weights.append(pops.get(g, 0.0))
    if not wedges:
        return 0.0, 0.0, 0.0
    wedges = np.array(wedges); weights = np.array(weights); weights = weights / weights.sum()
    point = float(np.sum(wedges * weights))
    # bootstrap CI over unprotected rows
    rng = np.random.default_rng(SEED + 7)
    boots = []
    idx = d.index.to_numpy()
    for _ in range(300):
        s = d.loc[rng.choice(idx, len(idx), replace=True)]
        try:
            mp = smf.ols(f"price ~ C(G, Treatment(reference={ref_g}))", data=s).fit()
            md = smf.ols(f"default ~ C(G, Treatment(reference={ref_g}))", data=s).fit()
            sl = smf.ols("price ~ default", data=s).fit().params["default"]
            w, ww = [], []
            for g in grades:
                if g == ref_g:
                    continue
                tt = f"C(G, Treatment(reference={ref_g}))[T.{g}]"
                if tt not in mp.params.index:
                    continue
                w.append(mp.params[tt] - md.params.get(tt, 0.0) * sl)
                ww.append((s["G"] == g).mean())
            ww = np.array(ww); ww = ww / ww.sum() if ww.sum() else ww
            boots.append(float(np.sum(np.array(w) * ww)))
        except Exception:
            continue
    lo, hi = np.percentile(boots, [2.5, 97.5]) if boots else (point, point)
    return point, float(lo), float(hi)


def direct_protected_disparity(df):
    """The DIRECT disparity (what you'd measure WITH the protected attribute) — for the USELESS check:
    if footprint stays in noise while THIS grows large, the device is real-but-sub-threshold."""
    m = smf.ols("price ~ P + default", data=df).fit()
    return float(m.params["P"])


def main():
    rows = []
    for lam in LAMBDAS:
        df = make_world(lam, COARSE_BINS, SEED)
        fp, lo, hi = footprint_unprotected(df)
        direct = direct_protected_disparity(df)
        # GUARD 1 falsifier: same lambda at FINE granularity — footprint should die.
        df_fine = make_world(lam, FINE_BINS, SEED)
        fp_fine, lo_fine, hi_fine = footprint_unprotected(df_fine)
        rows.append({
            "lambda": lam,
            "footprint_unprotected_bps": round(fp, 2),
            "footprint_ci": [round(lo, 2), round(hi, 2)],
            "ci_excludes_zero": bool(lo > 0 or hi < 0),
            "direct_protected_disparity_bps": round(direct, 2),
            "footprint_FINE_grade_bps": round(fp_fine, 2),
            "footprint_FINE_ci": [round(lo_fine, 2), round(hi_fine, 2)],
            "fine_ci_excludes_zero": bool(lo_fine > 0 or hi_fine < 0),
        })

    # sensitivity floor = smallest lambda>0 where the COARSE footprint CI clears 0
    detected = [r for r in rows if r["lambda"] > 0 and r["ci_excludes_zero"]]
    floor = min((r["lambda"] for r in detected), default=None)
    # monotonicity of footprint in lambda (coarse)
    fps = [r["footprint_unprotected_bps"] for r in rows]
    monotone = all(b >= a - 1e-6 for a, b in zip(fps, fps[1:]))
    # GUARD 2: lambda=0 must be null
    null_row = next(r for r in rows if r["lambda"] == 0.0)
    guard2_ok = not null_row["ci_excludes_zero"]
    # GUARD 1: at high lambda, fine-grade footprint should be much smaller than coarse
    hi_lam = rows[-1]
    guard1_ok = (abs(hi_lam["footprint_FINE_grade_bps"]) < 0.5 * abs(hi_lam["footprint_unprotected_bps"])
                 + 1e-9) if hi_lam["footprint_unprotected_bps"] != 0 else None

    if floor is not None and monotone and guard2_ok:
        verdict = (f"DEVICE WORKS — attribute-free footprint is monotone in lambda and resolves above "
                   f"noise; sensitivity floor lambda*={floor}. lambda=0 null held (GUARD 2). "
                   f"GUARD 1 (fine-grade kills footprint)={'PASS' if guard1_ok else 'CHECK'}.")
    elif floor is None:
        verdict = ("DEVICE USELESS HERE — footprint never clears noise across the lambda range; "
                   "real-in-principle, sub-threshold-in-practice (the named failure). Check direct "
                   "disparity column: if it grew large while footprint stayed flat, the floor is above "
                   "the tested range.")
    else:
        verdict = "PARTIAL — footprint resolves but not cleanly monotone or a guard tripped; report partial."

    out = {
        "experiment": "fairwash_calibration_floor",
        "grade": "CONTROLLED synthetic, hypothetical-scenario validity — NOT a back-test",
        "dgp": "default~Bernoulli(R); G=coarse_bin(R+lambda*P); price=base+loading*G; spillover EMERGENT not planted",
        "n": N, "coarse_bins": COARSE_BINS, "fine_bins": FINE_BINS,
        "per_lambda": rows,
        "sensitivity_floor_lambda": floor,
        "footprint_monotone_in_lambda": monotone,
        "guard1_fine_grade_kills_footprint_at_max_lambda": guard1_ok,
        "guard2_lambda0_null_held": guard2_ok,
        "verdict": verdict,
    }
    with open(OUT_JSON, "w") as f:
        json.dump(out, f, indent=2)

    lines = []
    lines.append("FAIRWASH-DETECTION CALIBRATION FLOOR (2026-06-30, CONTROLLED SYNTHETIC)")
    lines.append("Q: does an attribute-free lawful-axis footprint detector resolve laundering, and at what floor?")
    lines.append(f"DGP: default~R; grade=coarse_bin(R+lambda*P); price off grade. spillover EMERGENT. N={N}, coarse_bins={COARSE_BINS}")
    lines.append("")
    lines.append(f"{'lambda':>7} {'footprint(unprot)':>17} {'CI':>16} {'CI≠0':>5} {'direct(P)':>10} {'fine-grade fp':>13} {'fine≠0':>6}")
    for r in rows:
        ci = f"[{r['footprint_ci'][0]:+.1f},{r['footprint_ci'][1]:+.1f}]"
        fci = "yes" if r["fine_ci_excludes_zero"] else "no"
        lines.append(f"{r['lambda']:7.2f} {r['footprint_unprotected_bps']:+17.1f} {ci:>16} "
                     f"{('yes' if r['ci_excludes_zero'] else 'no'):>5} {r['direct_protected_disparity_bps']:+10.1f} "
                     f"{r['footprint_FINE_grade_bps']:+13.1f} {fci:>6}")
    lines.append("")
    lines.append(f"sensitivity floor lambda* = {floor}    footprint monotone in lambda: {monotone}")
    lines.append(f"GUARD 1 (fine-grade kills footprint @ max lambda): {guard1_ok}    GUARD 2 (lambda=0 null held): {guard2_ok}")
    lines.append("")
    lines.append(f"VERDICT: {verdict}")
    txt = "\n".join(lines)
    with open(OUT_TXT, "w") as f:
        f.write(txt + "\n")
    print(txt)


if __name__ == "__main__":
    main()
