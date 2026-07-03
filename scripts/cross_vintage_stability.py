#!/usr/bin/env python3
"""Runner: cross-vintage stability of the honest lawful risk-loading L on SBA 7(a).

Feasibility test for the cross-vintage identifying restriction (bucket iv) named in
docs/superpowers/specs/2026-07-03-calibration-floor-resolution.md. Frozen pre-reg:
docs/superpowers/specs/2026-07-03-cross-vintage-stability-prereg.md.

QUESTION: is L_v (bps of price per unit realized default RATE, net of lawful controls) stable
across matured origination vintages FY2010-2016? Stable => the honest surface can serve as a
non-circular calibration anchor for detector #4.

METHOD (per the frozen pre-reg, Fact-B discipline):
  - Per vintage v, stratify loans into fixed quantile bins of a bounded realized-risk score.
  - Regress BIN-MEAN price on BIN-MEAN realized default rate (a [0,1] rate, NOT a bin index;
    bin-mean regression, NOT individual-row OLS which is attenuated by the binary default).
  - L_v = that slope, net of lawful controls (residualize price and default on controls first).
    UNIT: percentage POINTS of price per unit of realized default rate (interest_rate is in pct,
    defaulted is 0/1), NOT basis points. L~0.4 => a cohort defaulting 1.0 above prediction pays
    ~0.4pp (40bps) more. (Corrected 2026-07-03 after blind-adversary flagged the label.)
  - Test: CoV of L_v across vintages < 0.25 (P1); per-vintage CI vs pooled L; fixed vs variable
    (P2); shuffled-vintage placebo (P3).

No hedge: P1/P2/P3 scored WIN/LOSE/PASS-FAIL against the frozen bet.
"""
import json
import sys

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

sys.path.insert(0, ".")
from wedge.collectors.sba import load_pricing_frame  # noqa: E402

CSV = "data/sba/foia-7a-fy2010-fy2019-asof-260331.csv"
OUT_TXT = "runs/cross_vintage_stability_2026-07-03.txt"
OUT_JSON = "runs/cross_vintage_stability_2026-07-03.json"

LAWFUL_CONTROLS = ["np.log(grossapproval)", "terminmonths", "guaranteed_share", "jobssupported"]
N_BINS = 10          # quantile bins of the risk score, per vintage
SEED = 20260703
RNG = np.random.default_rng(SEED)


def _prep(df):
    """Restrict to rows with all lawful controls present and positive loan size."""
    d = df.dropna(subset=["grossapproval", "terminmonths", "guaranteed_share", "jobssupported",
                          "interest_rate", "defaulted"]).copy()
    d = d[d["grossapproval"] > 0].copy()
    d["jobssupported"] = pd.to_numeric(d["jobssupported"], errors="coerce")
    d = d.dropna(subset=["jobssupported"]).copy()
    return d


def _residualize(d, col):
    """Return residuals of `col` on the lawful controls (net-of-controls quantity)."""
    formula = f"{col} ~ " + " + ".join(LAWFUL_CONTROLS)
    m = smf.ols(formula, data=d).fit()
    return m.resid


def _loading_for_frame(d):
    """Estimate L (price-per-realized-default-rate slope) via bin-mean regression on residualized
    price and default. Returns (L, se_L, n_bins_used, n_rows). Risk score for binning = the
    net-of-controls realized-default residual itself (higher => riskier than controls predict)."""
    if len(d) < 5 * N_BINS:
        return None
    d = d.copy()
    d["_price_r"] = _residualize(d, "interest_rate").to_numpy()
    d["_def_r"] = _residualize(d, "defaulted").to_numpy()
    # Bin by the default residual (bounded proxy for latent risk not captured by controls).
    try:
        d["_bin"] = pd.qcut(d["_def_r"].rank(method="first"), N_BINS, labels=False)
    except ValueError:
        return None
    g = d.groupby("_bin").agg(price_r=("_price_r", "mean"),
                              def_r=("_def_r", "mean"),
                              n=("_price_r", "size")).reset_index()
    if len(g) < 3:
        return None
    # Bin-mean regression: price residual ~ default residual. Slope = L (bps per unit default rate).
    m = smf.wls("price_r ~ def_r", data=g, weights=g["n"]).fit()
    return (float(m.params["def_r"]), float(m.bse["def_r"]), len(g), len(d))


def _cov(vals):
    """Coefficient of variation (|std/mean|). Guards mean~0."""
    a = np.asarray(vals, float)
    mean = a.mean()
    if abs(mean) < 1e-9:
        return float("inf")
    return float(a.std(ddof=1) / abs(mean))


def main():
    df_all = _prep(load_pricing_frame(CSV))
    df_all["fy"] = pd.to_numeric(df_all["approval_fy"], errors="coerce").fillna(0).astype("int64")
    df_all = df_all[df_all["fy"] > 0].copy()
    vintages = sorted(df_all["fy"].unique())

    def loadings_by_vintage(d):
        out = {}
        for v in vintages:
            dv = d[d["fy"] == v]
            res = _loading_for_frame(dv)
            if res is not None:
                out[v] = res
        return out

    # ---- real vintages, all rate types ----
    L_all = loadings_by_vintage(df_all)
    # ---- fixed-rate cell (base-rate confound weakest) ----
    df_fixed = df_all[df_all["rate_type"] == "F"]
    L_fixed = loadings_by_vintage(df_fixed)
    # ---- variable-rate cell ----
    df_var = df_all[df_all["rate_type"] == "V"]
    L_var = loadings_by_vintage(df_var)

    # Pooled-across-vintage L (all rate types) for the CI-exclusion test.
    pooled = _loading_for_frame(df_all)
    pooled_L = pooled[0] if pooled else float("nan")

    def summarize(Ld, label):
        if len(Ld) < 3:
            return {"label": label, "n_vintages": len(Ld), "cov": None, "note": "too few vintages"}
        Ls = {int(v): Ld[v][0] for v in Ld}
        cov = _cov(list(Ls.values()))
        # per-vintage CI exclusion of pooled_L
        excl = {}
        for v, (L, se, _, _) in Ld.items():
            lo, hi = L - 1.96 * se, L + 1.96 * se
            excl[int(v)] = bool(pooled_L < lo or pooled_L > hi)
        return {"label": label, "n_vintages": len(Ld),
                "L_by_vintage": {int(v): round(Ld[v][0], 2) for v in Ld},
                "se_by_vintage": {int(v): round(Ld[v][1], 2) for v in Ld},
                "n_by_vintage": {int(v): Ld[v][3] for v in Ld},
                "cov": round(cov, 4),
                # CAVEAT (blind adversary, 2026-07-03): this clause compares each vintage's WIDE
                # bin-mean CI (10 points) against pooled L and is UNDER-POWERED — it reads False
                # (looks "stable") while a standard interacted OLS rejects slope-equality at
                # p~6e-62. Do NOT read False here as stability. The CoV is the load-bearing
                # evidence; this clause if anything UNDERSTATES the instability.
                "any_vintage_ci_excludes_pooled": any(excl.values()),
                "any_vintage_ci_excludes_pooled_CAVEAT": "under-powered; CoV is load-bearing, not this",
                "which_exclude": [v for v, e in excl.items() if e]}

    s_all = summarize(L_all, "all_rate_types")
    s_fixed = summarize(L_fixed, "fixed_rate")
    s_var = summarize(L_var, "variable_rate")

    # ---- P3 placebo: shuffle vintage labels, dispersion should collapse ----
    placebo_covs = []
    for _ in range(20):
        dperm = df_all.copy()
        dperm["fy"] = RNG.permutation(dperm["fy"].to_numpy())
        Lp = {}
        for v in vintages:
            res = _loading_for_frame(dperm[dperm["fy"] == v])
            if res is not None:
                Lp[v] = res[0]
        if len(Lp) >= 3:
            placebo_covs.append(_cov(list(Lp.values())))
    placebo_cov_mean = float(np.mean(placebo_covs)) if placebo_covs else None

    # ---- scoring ----
    cov_fixed = s_fixed.get("cov")
    p1_win = (cov_fixed is not None and cov_fixed < 0.25
              and not s_fixed.get("any_vintage_ci_excludes_pooled", True))
    p2_win = (s_var.get("cov") is not None and cov_fixed is not None
              and s_var["cov"] > cov_fixed)
    # P3 passes if real fixed-rate dispersion clearly exceeds placebo (structure > noise),
    # OR if P1 wins (stable is stable regardless of placebo).
    p3_pass = (placebo_cov_mean is not None and cov_fixed is not None
               and (p1_win or cov_fixed > 1.5 * placebo_cov_mean))

    result = {
        "prereg": "docs/superpowers/specs/2026-07-03-cross-vintage-stability-prereg.md",
        "vintages": [int(v) for v in vintages],
        "pooled_L_all": round(pooled_L, 2),
        "all_rate_types": s_all,
        "fixed_rate": s_fixed,
        "variable_rate": s_var,
        "placebo_cov_mean": round(placebo_cov_mean, 4) if placebo_cov_mean is not None else None,
        "scoring": {
            "P1_fixed_L_stable_cov_lt_0.25": bool(p1_win),
            "P2_drift_larger_on_variable": bool(p2_win),
            "P3_placebo_dispersion_collapses": bool(p3_pass),
        },
    }

    with open(OUT_JSON, "w") as f:
        json.dump(result, f, indent=2)

    lines = []
    lines.append("CROSS-VINTAGE STABILITY OF THE HONEST RISK-LOADING L — SBA 7(a) matured FY2010-2016")
    lines.append("=" * 78)
    lines.append(f"pre-reg: {result['prereg']}")
    lines.append(f"vintages: {result['vintages']}   pooled L (all): {result['pooled_L_all']} bps/unit-default")
    lines.append("")
    for s in (s_all, s_fixed, s_var):
        lines.append(f"[{s['label']}]  n_vintages={s.get('n_vintages')}")
        if s.get("cov") is not None:
            lines.append(f"    L_by_vintage: {s.get('L_by_vintage')}")
            lines.append(f"    n_by_vintage: {s.get('n_by_vintage')}")
            lines.append(f"    CoV = {s['cov']}   any CI excludes pooled: {s['any_vintage_ci_excludes_pooled']} {s.get('which_exclude')}")
        else:
            lines.append(f"    {s.get('note')}")
        lines.append("")
    lines.append(f"placebo (shuffled-vintage) mean CoV: {result['placebo_cov_mean']}")
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
