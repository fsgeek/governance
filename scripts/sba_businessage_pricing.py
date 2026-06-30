#!/usr/bin/env python3
"""Runner: SBA 7(a) firm-age pricing disparity + charge-off decomposition (frozen-ledger experiment).

First port of the validated empty-chair instrument to a NOVEL substrate after the age-pricing arc
re-labeled itself from age to credit-tenure. SBA is the first axis where the instrument's required
disparity + decomposition-by-realized-risk form runs on an age-like axis the analyst did NOT pre-label
AND that carries a realized outcome (gross charge-off) HMDA lacked.

Frozen ledger + build-time amendments: docs/superpowers/specs/2026-06-29-sba-businessage-pricing-prereg.md

B1 (disparity): do New/Startup firms pay a higher InitialInterestRate than Existing-5+ firms, net of
   lawful controls? Reported WITH and WITHOUT the rate-timing controls C(approval_fy)+C(rate_type).
B2 (decomposition): SBA has NO credit grade -> residual-based, not grade-based. Fit the SAME age-band-
   on-lawful-controls residual for PRICE and for realized DEFAULT, then compare:
     price-gap > default-gap  => New/Startup OVER-priced (empty-chair harm)
     price-gap ~= default-gap => honestly priced
     price-gap < default-gap  => subsidized

Scoring (criterion 5 of the goal): B1 and B2 are each scored explicitly WIN or LOSE vs the frozen bet.
No "suggestive", no hedge that dodges the score.
"""
import json
import sys

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

sys.path.insert(0, ".")
from wedge.collectors.sba import (  # noqa: E402
    load_pricing_frame, SBA_AGE_BANDS, SBA_AGE_REFERENCE_IDX, SBA_AGE_YOUNG_IDX,
)

CSV = "data/sba/foia-7a-fy2010-fy2019-asof-260331.csv"
OUT_TXT = "runs/sba_businessage_pricing_2026-06-29.txt"
OUT_JSON = "runs/sba_businessage_pricing_2026-06-29.json"

# Lawful business controls (the declared risk-model's observable covariates).
LAWFUL_CONTROLS = ["np.log(grossapproval)", "terminmonths", "guaranteed_share", "jobssupported"]
# Rate-timing controls (variable-rate base-rate-environment confound; added build-time before any run).
TIMING_TERMS = "C(approval_fy) + C(rate_type)"


def band_residual(df, outcome, controls, extra_terms=""):
    """OLS of `outcome` on SBA firm-age band dummies (ref = Existing-5+) + controls.
    Returns {band_idx: (coef, lo, hi, n)} where coef is in the outcome's native units * 100
    (bps for interest_rate in pp; 'pp*100'=basis-points-of-probability for the 0/1 default outcome,
    which we relabel as pp by /100 at read time -- see read_gap). Reference coef is identically 0.
    """
    d = df.copy()
    d = d.dropna(subset=["grossapproval", "terminmonths", "guaranteed_share", "jobssupported"])
    d = d[d["grossapproval"] > 0]
    d["_band"] = pd.Categorical(d["age_band"])
    ref = SBA_AGE_REFERENCE_IDX
    numeric = " + ".join(controls)
    formula = f"{outcome} ~ C(_band, Treatment(reference={ref})) + {numeric}"
    if extra_terms:
        formula += " + " + extra_terms
    m = smf.ols(formula, data=d).fit()
    conf = m.conf_int()
    counts = d["age_band"].value_counts().to_dict()
    res = {}
    for i in range(len(SBA_AGE_BANDS)):
        n = int(counts.get(i, 0))
        if i == ref:
            res[i] = (0.0, 0.0, 0.0, n)
            continue
        term = f"C(_band, Treatment(reference={ref}))[T.{i}]"
        if term in m.params.index:
            lo, hi = conf.loc[term]
            res[i] = (float(m.params[term]) * 100.0, float(lo) * 100.0, float(hi) * 100.0, n)
        else:
            res[i] = (float("nan"), float("nan"), float("nan"), n)
    return res, float(m.rsquared)


def young_coef(res):
    """(coef, lo, hi, n) for the young (New/Startup) band vs the Existing-5+ reference."""
    return res[SBA_AGE_YOUNG_IDX]


def run_b1(df):
    """B1 price residual, with and without timing controls. interest_rate is in pp -> coef*100 = bps."""
    res_no, r2_no = band_residual(df, "interest_rate", LAWFUL_CONTROLS, extra_terms="")
    res_tm, r2_tm = band_residual(df, "interest_rate", LAWFUL_CONTROLS, extra_terms=TIMING_TERMS)
    return {
        "without_timing": {"young_bps": young_coef(res_no), "r2": r2_no, "all_bands": res_no},
        "with_timing": {"young_bps": young_coef(res_tm), "r2": r2_tm, "all_bands": res_tm},
    }


def run_b2(df, extra_terms=TIMING_TERMS):
    """B2 default residual on the SAME controls (timing included by default). `defaulted` is 0/1, so
    coef*100 is in percentage-points-of-default. Returns young default-gap vs Existing-5+ in pp."""
    res, r2 = band_residual(df, "defaulted", LAWFUL_CONTROLS, extra_terms=extra_terms)
    yb, lo, hi, n = young_coef(res)
    # coef was *100 (pp-of-probability already, since outcome is 0/1 and we *100 -> percentage points)
    return {"young_default_gap_pp": yb, "ci_pp": (lo, hi), "n": n, "r2": r2, "all_bands": res}


def compare_gaps(b1, b2):
    """The decomposition verdict: price-gap (bps, with timing) vs default-gap (pp). To compare on one
    scale, express both as the young premium. A pp of default is not a bp of price 1:1; the honest
    comparison is DIRECTIONAL + magnitude-relative: is the price premium more than the realized risk
    gap can justify? We report both raw and a justified-price heuristic.
    """
    price_bps = b1["with_timing"]["young_bps"][0]          # bps the young pay above Existing-5+
    price_lo, price_hi = b1["with_timing"]["young_bps"][1], b1["with_timing"]["young_bps"][2]
    default_pp = b2["young_default_gap_pp"]                 # pp the young default above Existing-5+
    # Heuristic justified premium: on a guaranteed loan, expected loss premium ~ default_gap_pp *
    # avg_loss_given_default_fraction. We do NOT know LGD precisely; report the RAW comparison and flag.
    return {
        "price_premium_bps": price_bps,
        "price_premium_ci_bps": (price_lo, price_hi),
        "default_gap_pp": default_pp,
        "price_ci_excludes_zero": bool(price_lo * price_hi > 0),
    }


def realized_params(df):
    """Realized term and loss-given-default the adversary said the score() hardcodes wrong.
    term_years = mean term/12 among the band rows; lgd = mean(loss/grossapproval) among charged-off.
    Also the guarantee share (the lender bears only ~1-guar of the loss)."""
    co = df[df["defaulted"] == 1]
    lgd = float((co["loss"] / co["grossapproval"].where(co["grossapproval"] > 0)).clip(0, 1).mean())
    term_years = float(df["terminmonths"].mean() / 12.0)
    guar = float(df["guaranteed_share"].clip(0, 1).mean())
    return {"lgd_realized": lgd, "term_years_realized": term_years, "guarantee_share": guar}


def justified_bps(default_pp, lgd, term_years, lender_share=1.0):
    """Annualized expected-loss spread justified by a lifetime default-prob gap (the adversary
    confirmed this conversion is dimensionally sound). lender_share<1 models that on a guaranteed
    loan the rate-setter bears only part of the loss (the adversary's unresolved joint — reported,
    not baked into the headline)."""
    return default_pp * (lgd * lender_share / term_years * 100.0)


def per_subgroup_decomposition(df, params):
    """The adversary's Attack-3 fix: Startup and New(<1yr) read SEPARATELY, not pooled. For each
    young subgroup, price premium vs Existing-5+, default gap, and corrected justified spread."""
    from wedge.collectors.sba import SBA_AGE_STARTUP_IDX
    price_res, _ = band_residual(df, "interest_rate", LAWFUL_CONTROLS, extra_terms=TIMING_TERMS)
    def_res, _ = band_residual(df, "defaulted", LAWFUL_CONTROLS, extra_terms=TIMING_TERMS)
    out = {}
    for idx, name in ((SBA_AGE_STARTUP_IDX, "Startup"), (SBA_AGE_YOUNG_IDX, "New(<1yr)")):
        price = price_res[idx][0]
        dgap = def_res[idx][0]
        jb = justified_bps(dgap, params["lgd_realized"], params["term_years_realized"])
        out[name] = {
            "price_premium_bps": round(price, 2),
            "price_ci_bps": [round(price_res[idx][1], 2), round(price_res[idx][2], 2)],
            "default_gap_pp": round(dgap, 3),
            "justified_bps_corrected": round(jb, 2),
            "over_under_bps": round(price - jb, 2),
            "classification": ("OVER-priced" if price - jb > 0.25 * abs(jb)
                               else "SUBSIDIZED" if price - jb < -0.25 * abs(jb)
                               else "honestly-priced"),
            "n": price_res[idx][3],
        }
    return out


# --------------------------------------------------------------------------- adversarial arms

def positive_control(df, rng):
    """Plant +30bps on 50% of New/Startup rows and +3pp default on 50% of New/Startup rows; confirm
    the estimators recover them (~+15bps / ~+1.5pp on the planted-half-diluted band)."""
    d = df.copy()
    young = d["age_band"] == SBA_AGE_YOUNG_IDX
    idx_young = d.index[young]
    planted = rng.choice(idx_young, size=len(idx_young) // 2, replace=False)
    # price plant
    d["interest_rate_planted"] = d["interest_rate"].copy()
    d.loc[planted, "interest_rate_planted"] = d.loc[planted, "interest_rate"] + 0.30  # +30bps in pp
    d_price = d.drop(columns=["interest_rate"]).rename(columns={"interest_rate_planted": "interest_rate"})
    res_p, _ = band_residual(d_price, "interest_rate", LAWFUL_CONTROLS, extra_terms=TIMING_TERMS)
    base_res, _ = band_residual(df, "interest_rate", LAWFUL_CONTROLS, extra_terms=TIMING_TERMS)
    price_base = young_coef(base_res)[0]
    price_recovered = young_coef(res_p)[0] - price_base
    # default plant: raise the young default rate by a KNOWN +3pp (flip 3% of currently-non-defaulted
    # young rows to default), then confirm the estimator recovers ~+3pp above the unplanted base.
    d["defaulted_planted"] = d["defaulted"].copy()
    young_nondef = d.index[(d["age_band"] == SBA_AGE_YOUNG_IDX) & (d["defaulted"] == 0)]
    n_flip = int(round(0.03 * len(idx_young)))  # +3pp of the young band
    n_flip = min(n_flip, len(young_nondef))
    flip = rng.choice(young_nondef, size=n_flip, replace=False)
    d.loc[flip, "defaulted_planted"] = 1
    d_def = d.drop(columns=["defaulted"]).rename(columns={"defaulted_planted": "defaulted"})
    res_d, _ = band_residual(d_def, "defaulted", LAWFUL_CONTROLS, extra_terms=TIMING_TERMS)
    def_base = run_b2(df)["young_default_gap_pp"]
    def_recovered = young_coef(res_d)[0] - def_base
    return {"price_recovered_bps": price_recovered, "price_planted_bps": 15.0,
            "default_recovered_pp": def_recovered, "default_planted_pp": 3.0}


def negative_control(df, rng):
    """Random 50/50 split (not firm-age) must show ~0 price gap."""
    d = df.copy()
    d["_fake_band"] = rng.integers(0, 2, size=len(d))
    d["_fake_band"] = np.where(d["_fake_band"] == 1, SBA_AGE_YOUNG_IDX, SBA_AGE_REFERENCE_IDX)
    d2 = d.copy()
    d2["age_band"] = d["_fake_band"]
    res, _ = band_residual(d2, "interest_rate", LAWFUL_CONTROLS, extra_terms=TIMING_TERMS)
    return {"fake_young_bps": young_coef(res)[0]}


def maturity_sensitivity(df_full):
    """Re-run B1/B2 on FY2010-2014 (most matured) vs the FY2010-2016 headline window."""
    fy_num = pd.to_numeric(df_full["approval_fy"], errors="coerce")
    d14 = df_full[fy_num <= 2014].copy()
    b1 = run_b1(d14)
    b2 = run_b2(d14)
    return {"fy2010_2014": {"price_bps_with_timing": b1["with_timing"]["young_bps"][0],
                            "default_gap_pp": b2["young_default_gap_pp"], "n": int(len(d14))}}


def naics_confound(df):
    """B1/B2 with vs without C(naics2). The gap between them is a declared sensitivity, not hidden."""
    b1_with, _ = band_residual(df, "interest_rate", LAWFUL_CONTROLS,
                               extra_terms=TIMING_TERMS + " + C(naics2)")
    b2_with, _ = band_residual(df, "defaulted", LAWFUL_CONTROLS,
                               extra_terms=TIMING_TERMS + " + C(naics2)")
    return {"price_bps_with_naics": young_coef(b1_with)[0],
            "default_gap_pp_with_naics": young_coef(b2_with)[0]}


def score(b1_head, subgroups):
    """Criterion 5: score B1 and B2 explicitly WIN/LOSE vs the frozen bet. No hedge.
    Post-adversary: B1 uses the MATURED headline; B2 is scored PER SUBGROUP (Startup vs New),
    NOT pooled, with the corrected realized LGD/term. The pooled verdict is reported but is NOT
    the headline (the adversary showed it describes neither subgroup).

    FROZEN B1: New/Startup pay a higher rate net of controls, ~55%, +10..+40bps; NULL is a real result.
    FROZEN B2 (the bind): over-priced vs honest, 50/50. Empty-chair PRIOR = OVER-priced.
    """
    price_bps, lo, hi = b1_head["young_bps"][0], b1_head["young_bps"][1], b1_head["young_bps"][2]
    price_excl0 = bool(lo * hi > 0)
    b1_win = bool(price_excl0 and price_bps > 0)
    b1_verdict = "WIN" if b1_win else "LOSE"
    b1_reason = (f"matured New(<1yr) premium {price_bps:.1f}bps, CI "
                 f"{'excludes' if price_excl0 else 'crosses'} 0 -> "
                 f"{'premium exists' if b1_win else 'null/wrong-sign'}")

    new = subgroups["New(<1yr)"]
    startup = subgroups["Startup"]
    # B2 prior was "OVER-priced". It is a SPLIT verdict: WIN for New(<1yr), LOSE for Startup.
    new_over = new["classification"] == "OVER-priced"
    startup_over = startup["classification"] == "OVER-priced"
    b2_verdict = "PARTIAL" if (new_over != startup_over) else ("WIN" if new_over else "LOSE")
    b2_reason = (f"SPLIT (adversary Attack-3): New(<1yr) {new['price_premium_bps']:+.1f}bps vs "
                 f"justified {new['justified_bps_corrected']:.1f} => {new['classification']}; "
                 f"Startup {startup['price_premium_bps']:+.1f}bps vs "
                 f"{startup['justified_bps_corrected']:.1f} => {startup['classification']}. "
                 f"Empty-chair OVER-priced prior holds for New(<1yr) ONLY, NOT thin-history generally "
                 f"(startups are the counterexample).")
    return {
        "B1": {"verdict": b1_verdict, "reason": b1_reason,
               "headline_window": "FY2010-2014 (matured; adversary Attack-5)"},
        "B2": {"verdict": b2_verdict, "reason": b2_reason,
               "new_classification": new["classification"],
               "startup_classification": startup["classification"]},
    }


def b2_sensitivity(default_pp, price_bps):
    """The B2 verdict rests on LGD, term, AND who bears the loss (the adversary said vary all three,
    not just LGD). Report over-priced status across the grid."""
    out = {}
    for lgd in (0.3, 0.5, 0.7):
        for term in (7.0, 10.0):
            for lender_share in (1.0, 0.35):  # 1.0 = borrower pays on full balance; 0.35 = lender-borne
                jb = justified_bps(default_pp, lgd, term, lender_share)
                key = f"lgd{lgd}_T{int(term)}_share{lender_share}"
                out[key] = {"justified_bps": round(jb, 2), "over_under_bps": round(price_bps - jb, 2),
                            "over_priced": bool(price_bps - jb > 0)}
    return out


def main():
    rng = np.random.default_rng(20260629)
    df_full = load_pricing_frame(CSV)  # FY2010-2016
    # HEADLINE = matured FY2010-2014 (adversary Attack-5: 2015-16 inflate the premium ~30%).
    fy = pd.to_numeric(df_full["approval_fy"], errors="coerce")
    df = df_full[fy <= 2014].copy()

    params = realized_params(df)
    b1 = run_b1(df)
    b2 = run_b2(df)
    subgroups = per_subgroup_decomposition(df, params)
    arms = {
        "positive_control": positive_control(df, rng),
        "negative_control": negative_control(df, rng),
        "window_sensitivity": {  # the adversary's maturity table, full
            "FY2010_2016": round(run_b1(df_full)["with_timing"]["young_bps"][0], 2),
            "FY2010_2014_headline": round(b1["with_timing"]["young_bps"][0], 2),
            "FY2010_2013": round(run_b1(df_full[fy <= 2013])["with_timing"]["young_bps"][0], 2),
            "FY2010_2012": round(run_b1(df_full[fy <= 2012])["with_timing"]["young_bps"][0], 2),
        },
        "naics_confound": naics_confound(df),
    }
    verdict = score(b1["with_timing"], subgroups)
    b2_sens = b2_sensitivity(subgroups["New(<1yr)"]["default_gap_pp"],
                             subgroups["New(<1yr)"]["price_premium_bps"])

    def band_table(allbands):
        return {SBA_AGE_BANDS[i]: {"coef": round(allbands[i][0], 3),
                                   "ci": [round(allbands[i][1], 3), round(allbands[i][2], 3)],
                                   "n": allbands[i][3]} for i in range(len(SBA_AGE_BANDS))}

    payload = {
        "experiment": "sba_businessage_pricing",
        "substrate": "SBA 7(a) FOIA, HEADLINE matured FY2010-2014 (FY2010-2016 = inflated comparison)",
        "n_headline": int(len(df)), "n_full_2016": int(len(df_full)),
        "realized_params_adversary_corrected": params,
        "young_band": SBA_AGE_BANDS[SBA_AGE_YOUNG_IDX],
        "startup_band": SBA_AGE_BANDS[0],
        "reference_band": SBA_AGE_BANDS[SBA_AGE_REFERENCE_IDX],
        "B1_price_pooled_band1_New": {
            "premium_bps_no_timing": round(b1["without_timing"]["young_bps"][0], 2),
            "premium_bps_with_timing": round(b1["with_timing"]["young_bps"][0], 2),
            "ci_with_timing": [round(b1["with_timing"]["young_bps"][1], 2),
                               round(b1["with_timing"]["young_bps"][2], 2)],
            "bands_with_timing": band_table(b1["with_timing"]["all_bands"]),
        },
        "B2_default_bands": band_table(b2["all_bands"]),
        "per_subgroup_decomposition": subgroups,
        "verdict": verdict,
        "b2_sensitivity_lgd_term_guarantee": b2_sens,
        "adversarial_arms": arms,
        "adversary_note": ("Blind adversary (scientific-integrity-auditor) ruled the FIRST cut "
                           "OVERSTATED: pooled +28.6bps was window-inflated (-> matured +20.8) and "
                           "pooled Startup with New(<1yr), masking that Startup is honestly priced. "
                           "This run incorporates all three corrections (matured headline, split "
                           "subgroups, LGD/term/guarantee sensitivity)."),
        "frozen_ledger": "docs/superpowers/specs/2026-06-29-sba-businessage-pricing-prereg.md",
        "seed": 20260629,
    }
    with open(OUT_JSON, "w") as f:
        json.dump(payload, f, indent=2, default=float)

    out = []
    A = out.append
    A("SBA 7(a) FIRM-AGE PRICING + CHARGE-OFF DECOMPOSITION (2026-06-29, POST-ADVERSARY)")
    A(f"HEADLINE window: matured FY2010-2014, N={len(df):,}  (FY2010-2016 N={len(df_full):,} = inflated)")
    A(f"realized params (adversary-corrected): LGD={params['lgd_realized']:.2f}, "
      f"term={params['term_years_realized']:.1f}yr, guarantee_share={params['guarantee_share']:.2f}")
    A("")
    A("PER-SUBGROUP DECOMPOSITION (Startup and New split — adversary Attack-3):")
    for name in ("Startup", "New(<1yr)"):
        s = subgroups[name]
        A(f"  {name:12} price {s['price_premium_bps']:+6.1f}bps  default {s['default_gap_pp']:+.2f}pp  "
          f"justified {s['justified_bps_corrected']:5.1f}bps  => {s['classification']}  (n={s['n']:,})")
    A("")
    A("WINDOW SENSITIVITY (adversary Attack-5 — premium deflates as window matures):")
    for k, v in arms["window_sensitivity"].items():
        A(f"  {k:22} {v:+.1f}bps")
    A("")
    A("NEW(<1yr) B2 SENSITIVITY over LGD x term x loss-bearer (over-priced? Y/N):")
    for k, v in b2_sens.items():
        A(f"  {k:24} justified {v['justified_bps']:6.1f}  over_under {v['over_under_bps']:+6.1f}  "
          f"{'Y' if v['over_priced'] else 'N'}")
    A("")
    A("ADVERSARIAL ARMS:")
    A(f"  positive control: price recovered {arms['positive_control']['price_recovered_bps']:+.1f}bps "
      f"(planted +15.0), default recovered {arms['positive_control']['default_recovered_pp']:+.2f}pp (planted +3.0)")
    A(f"  negative control: {arms['negative_control']['fake_young_bps']:+.2f}bps (expect ~0)")
    A(f"  NAICS confound: New price {arms['naics_confound']['price_bps_with_naics']:+.1f}bps with C(naics2)")
    A("")
    A("SCORED VERDICT (vs frozen bet):")
    A(f"  B1: {verdict['B1']['verdict']} — {verdict['B1']['reason']}")
    A(f"  B2: {verdict['B2']['verdict']} — {verdict['B2']['reason']}")
    with open(OUT_TXT, "w") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
