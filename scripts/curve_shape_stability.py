#!/usr/bin/env python3
"""Runner: is the SHAPE (curvature) of the honest price-risk curve vintage-stable on SBA 7(a)?

Follow-on to scripts/cross_vintage_stability.py (slope L drifts). Frozen pre-reg:
docs/superpowers/specs/2026-07-03-curve-shape-stability-prereg.md.

QUESTION: even though the SLOPE of price-on-realized-risk drifts across vintages, is the CURVATURE
(the second-order shape) vintage-invariant? A stable shape coordinate under a drifting slope would be
the anchor Tony's backtesting/drift-manifold idea needs.

METHOD (per pre-reg — high-power interacted individual-level OLS, NOT per-vintage bin regression,
because per-vintage curvature off 10 bins is hopelessly under-powered):
  1. First-stage logit: defaulted ~ lawful_controls => per-loan continuous risk score = predicted
     default prob (a bounded [0,1] risk quantity; DECLARED construction, in the light path).
  2. Main OLS: interest_rate ~ lawful_controls + score + score^2 + C(fy) + C(fy):score + C(fy):score^2
     - coefficient path on C(fy):score      = slope drift    (already established)
     - coefficient path on C(fy):score^2    = CURVATURE drift (the object under test)
  3. Wald test: joint equality of the C(fy):score^2 interaction terms across vintages.
     REJECT (p<0.01) => shape drifts (P1 WIN, betting instability). FAIL-to-reject => stable shape.
  4. Placebo: shuffle vintage labels; the curvature-interaction Wald should collapse to non-sig.
"""
import json
import sys

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

sys.path.insert(0, ".")
from wedge.collectors.sba import load_pricing_frame  # noqa: E402

CSV = "data/sba/foia-7a-fy2010-fy2019-asof-260331.csv"
OUT_TXT = "runs/curve_shape_stability_2026-07-03.txt"
OUT_JSON = "runs/curve_shape_stability_2026-07-03.json"

LAWFUL_CONTROLS = ["np.log(grossapproval)", "terminmonths", "guaranteed_share", "jobssupported"]
SEED = 20260703
RNG = np.random.default_rng(SEED)


def _prep(df):
    d = df.dropna(subset=["grossapproval", "terminmonths", "guaranteed_share", "jobssupported",
                          "interest_rate", "defaulted"]).copy()
    d = d[d["grossapproval"] > 0].copy()
    d["jobssupported"] = pd.to_numeric(d["jobssupported"], errors="coerce")
    d = d.dropna(subset=["jobssupported"]).copy()
    d["fy"] = pd.to_numeric(d["approval_fy"], errors="coerce").fillna(0).astype("int64")
    d = d[d["fy"] > 0].copy()
    return d


def _risk_score(d):
    """First-stage logit: predicted default prob per loan (bounded [0,1], DECLARED risk score)."""
    formula = "defaulted ~ " + " + ".join(LAWFUL_CONTROLS)
    m = smf.logit(formula, data=d).fit(disp=0)
    return m.predict(d).to_numpy()


def _fit_and_test(d, label):
    """Interacted OLS with score + score^2 x C(fy); Wald test on the curvature-interaction block."""
    d = d.copy()
    d["score"] = _risk_score(d)
    # Center score so score^2 is less collinear with score; store mean for reporting.
    d["score_c"] = d["score"] - d["score"].mean()
    d["score2"] = d["score_c"] ** 2
    d["fy_s"] = pd.Categorical(d["fy"].astype(str))
    ref = str(int(d["fy"].min()))
    ctrl = " + ".join(LAWFUL_CONTROLS)
    formula = (f"interest_rate ~ {ctrl} + score_c + score2 "
               f"+ C(fy_s, Treatment(reference='{ref}')) "
               f"+ C(fy_s, Treatment(reference='{ref}')):score_c "
               f"+ C(fy_s, Treatment(reference='{ref}')):score2")
    m = smf.ols(formula, data=d).fit()
    # Curvature-interaction terms = params whose name contains both the fy interaction and score2.
    curv_terms = [p for p in m.params.index if ":score2" in p]
    slope_terms = [p for p in m.params.index if ":score_c" in p]
    # Wald: all curvature-interaction coefs jointly zero (= curvature is vintage-invariant).
    wald_curv = m.f_test(" , ".join(f"{t} = 0" for t in curv_terms)) if curv_terms else None
    wald_slope = m.f_test(" , ".join(f"{t} = 0" for t in slope_terms)) if slope_terms else None
    # Per-vintage curvature = base score2 coef + that vintage's interaction (0 for ref vintage).
    base_curv = float(m.params["score2"])
    curv_by_fy = {}
    for t in curv_terms:
        # term looks like C(fy_s,...)[T.2014]:score2
        fy = t.split("[T.")[1].split("]")[0]
        curv_by_fy[fy] = round(base_curv + float(m.params[t]), 4)
    curv_by_fy[ref] = round(base_curv, 4)
    return {
        "label": label,
        "n": int(len(d)),
        "score_mean": round(float(d["score"].mean()), 4),
        "base_curvature_score2": round(base_curv, 4),
        "curvature_by_fy": dict(sorted(curv_by_fy.items())),
        "wald_curvature_equal_across_fy": {
            "fvalue": round(float(np.ravel(wald_curv.fvalue)[0]), 3) if wald_curv else None,
            "pvalue": float(np.ravel(wald_curv.pvalue)[0]) if wald_curv else None,
        },
        "wald_slope_equal_across_fy": {
            "fvalue": round(float(np.ravel(wald_slope.fvalue)[0]), 3) if wald_slope else None,
            "pvalue": float(np.ravel(wald_slope.pvalue)[0]) if wald_slope else None,
        },
    }


def main():
    d_all = _prep(load_pricing_frame(CSV))
    res_all = _fit_and_test(d_all, "all_rate_types")
    d_fixed = d_all[d_all["rate_type"] == "F"].copy()
    res_fixed = _fit_and_test(d_fixed, "fixed_rate") if len(d_fixed) > 5000 else {"label": "fixed_rate", "note": "n too small"}

    # ---- P3 placebo: shuffle vintage labels, curvature-interaction Wald should collapse ----
    placebo_p = []
    for _ in range(10):
        dp = d_all.copy()
        dp["fy"] = RNG.permutation(dp["fy"].to_numpy())
        try:
            rp = _fit_and_test(dp, "placebo")
            pv = rp["wald_curvature_equal_across_fy"]["pvalue"]
            if pv is not None:
                placebo_p.append(pv)
        except Exception:
            pass
    placebo_p_median = float(np.median(placebo_p)) if placebo_p else None

    real_p = res_all["wald_curvature_equal_across_fy"]["pvalue"]
    # Scoring
    p1_win = real_p is not None and real_p < 0.01              # shape DRIFTS (betting instability)
    p3_pass = (placebo_p_median is not None and
               (placebo_p_median > 0.05 or (real_p is not None and real_p < 0.01 and real_p < placebo_p_median / 10)))

    result = {
        "prereg": "docs/superpowers/specs/2026-07-03-curve-shape-stability-prereg.md",
        "all_rate_types": res_all,
        "fixed_rate": res_fixed,
        "placebo_curvature_wald_p_median": placebo_p_median,
        "placebo_p_values": [round(p, 4) for p in placebo_p],
        "scoring": {
            "P1_shape_DRIFTS_wald_p_lt_0.01": bool(p1_win),
            "P3_placebo_collapses": bool(p3_pass),
        },
    }
    with open(OUT_JSON, "w") as f:
        json.dump(result, f, indent=2, default=str)

    lines = []
    lines.append("CURVE-SHAPE (CURVATURE) STABILITY ACROSS VINTAGES — SBA 7(a) matured FY2010-2016")
    lines.append("=" * 78)
    lines.append(f"pre-reg: {result['prereg']}")
    for r in (res_all, res_fixed):
        lines.append("")
        lines.append(f"[{r['label']}]  n={r.get('n')}")
        if "curvature_by_fy" in r:
            lines.append(f"    curvature (score^2 coef) by vintage: {r['curvature_by_fy']}")
            wc = r["wald_curvature_equal_across_fy"]
            ws = r["wald_slope_equal_across_fy"]
            lines.append(f"    Wald curvature==across vintages: F={wc['fvalue']}  p={wc['pvalue']:.3e}")
            lines.append(f"    Wald slope==across vintages:     F={ws['fvalue']}  p={ws['pvalue']:.3e}")
        else:
            lines.append(f"    {r.get('note')}")
    lines.append("")
    lines.append(f"placebo curvature-Wald median p (shuffled vintage): {result['placebo_curvature_wald_p_median']}")
    lines.append("")
    lines.append("SCORING (vs frozen pre-reg):")
    for k, v in result["scoring"].items():
        lines.append(f"    {k}: {'WIN/PASS' if v else 'LOSE/FAIL'}")
    txt = "\n".join(lines)
    with open(OUT_TXT, "w") as f:
        f.write(txt + "\n")
    print(txt)


if __name__ == "__main__":
    main()
