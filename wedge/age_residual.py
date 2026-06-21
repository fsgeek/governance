"""Age-residual pricing analysis: does the young-end overcharge survive lawful-risk controls?

Pure statistics, no file I/O. The runner (scripts/age_pricing_residual.py) handles loading.
See docs/superpowers/specs/2026-06-20-age-pricing-residual-design.md for the design and the
frozen prediction ledger.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.stats.outliers_influence import variance_inflation_factor

AGE_BANDS: list[tuple[float, float]] = [
    (18, 25), (25, 30), (30, 35), (35, 40), (40, 45),
    (45, 50), (50, 55), (55, 60), (60, 70), (70, 95),
]
# [45,50) is the reference band for residuals (0-indexed -> 5).
REFERENCE_BAND_INDEX = next(i for i, b in enumerate(AGE_BANDS) if b == (45, 50))


def band_label(i: int) -> str:
    lo, hi = AGE_BANDS[i]
    return f"[{int(lo)},{int(hi)})"


def assign_age_band(age: float) -> int:
    """Return band index 0..9, or -1 if age is outside [18, 95].

    Left-closed bands; the final band [70,95] is right-inclusive so age==95 lands in it.
    """
    if age < AGE_BANDS[0][0] or age > AGE_BANDS[-1][1]:
        return -1
    for i, (lo, hi) in enumerate(AGE_BANDS):
        if lo <= age < hi or (i == len(AGE_BANDS) - 1 and age == hi):
            return i
    return -1


DEFAULT_CONTROLS = ["fico_mid", "dti", "annual_inc", "loan_amnt", "term_months"]


@dataclass
class BandResult:
    band_bps: dict           # band index -> residual coef in bps vs reference (0 for reference)
    band_ci: dict            # band index -> (lo, hi) 95% CI in bps
    n_per_band: dict         # band index -> row count
    r2: float
    reference_band: int      # band index used as the OLS baseline (canonical 5 when present)


def _band_formula(outcome: str, controls: list[str], ref: int, extra: str = "") -> str:
    numeric = " + ".join(controls)
    f = f"{outcome} ~ C(_band, Treatment(reference={ref})) + {numeric} + C(purpose)"
    if extra:
        f += " + " + extra
    return f


def _choose_reference(present_bands) -> int:
    """Use the canonical reference band ([45,50), index 5) when it is present; otherwise fall
    back to the most-populated present band. Within a tenure stratum the canonical band may be
    absent, so the baseline must adapt or patsy raises 'level out of range'."""
    counts = present_bands.value_counts()
    if REFERENCE_BAND_INDEX in counts.index:
        return REFERENCE_BAND_INDEX
    return int(counts.idxmax())


def fit_band_residuals(df: pd.DataFrame, outcome: str = "int_rate",
                       controls: list[str] | None = None,
                       age_band_col: str = "age_band",
                       extra_terms: str = "") -> BandResult:
    """OLS of `outcome` on age-band dummies + lawful controls; recover per-band bps residual.

    The outcome (int_rate) is in percentage points; coefficients are multiplied by 100 to
    report basis points. The reference band coefficient is identically 0. `extra_terms` allows
    the runner to add e.g. "C(grade)" for the net-of-grade decomposition without a new function.
    The reference band adapts (see _choose_reference) so within-tenure strata that lack [45,50)
    still fit; `BandResult.reference_band` records which band served as the baseline.
    """
    controls = list(DEFAULT_CONTROLS if controls is None else controls)
    d = df.copy()
    d["_band"] = pd.Categorical(d[age_band_col])
    ref = _choose_reference(d[age_band_col])
    model = smf.ols(_band_formula(outcome, controls, ref, extra_terms), data=d).fit()
    conf = model.conf_int()
    band_bps, band_ci = {}, {}
    for i in range(len(AGE_BANDS)):
        if i == ref:
            band_bps[i] = 0.0
            band_ci[i] = (0.0, 0.0)
            continue
        term = f"C(_band, Treatment(reference={ref}))[T.{i}]"
        if term in model.params.index:
            band_bps[i] = float(model.params[term]) * 100.0  # pp -> bps
            lo, hi = conf.loc[term]
            band_ci[i] = (float(lo) * 100.0, float(hi) * 100.0)
        else:
            band_bps[i] = float("nan")
            band_ci[i] = (float("nan"), float("nan"))
    n_per_band = d[age_band_col].value_counts().to_dict()
    return BandResult(
        band_bps=band_bps,
        band_ci=band_ci,
        n_per_band={int(k): int(v) for k, v in n_per_band.items()},
        r2=float(model.rsquared),
        reference_band=ref,
    )


def fit_poly_age(df: pd.DataFrame, outcome: str = "int_rate",
                 controls: list[str] | None = None) -> dict:
    """Robustness: est_age + est_age^2 on outcome, net of controls. Confirms the U-curvature
    is not a band-binning artifact. Requires an `est_age` column. Coefs reported in bps."""
    controls = list(DEFAULT_CONTROLS if controls is None else controls)
    d = df.copy()
    d["est_age_sq"] = d["est_age"] ** 2
    numeric = " + ".join(controls)
    formula = f"{outcome} ~ est_age + est_age_sq + {numeric} + C(purpose)"
    m = smf.ols(formula, data=d).fit()
    return {
        "est_age_coef_bps": float(m.params["est_age"]) * 100.0,
        "est_age_sq_coef_bps": float(m.params["est_age_sq"]) * 100.0,
        "r2": float(m.rsquared),
    }


def within_tenure_residuals(df: pd.DataFrame, outcome: str = "int_rate",
                            controls: list[str] | None = None,
                            n_tenure_bins: int = 5) -> dict:
    """Co-primary cell D: stratify by credit-tenure quantile, run the band residual within each
    stratum. Compares young-vs-old AT EQUAL TENURE, sidestepping est_age/control collinearity
    by conditioning on it. Returns {tenure_bin_index: BandResult}."""
    d = df.copy()
    d["_tenure"] = d["est_age"] - 18.0
    d["_tbin"] = pd.qcut(d["_tenure"], q=n_tenure_bins, labels=False, duplicates="drop")
    out = {}
    for b in sorted(x for x in d["_tbin"].dropna().unique()):
        sub = d[d["_tbin"] == b]
        if sub["age_band"].nunique() < 2:
            continue
        out[int(b)] = fit_band_residuals(sub, outcome=outcome, controls=controls)
    return out


def collinearity_diagnostics(df: pd.DataFrame, controls: list[str] | None = None) -> dict:
    """Cell B: how much of any attenuation is mechanical est_age/control overlap vs real risk.
    Returns VIF per control and Pearson corr of est_age with each control."""
    controls = list(DEFAULT_CONTROLS if controls is None else controls)
    d = df[controls].dropna().astype(float).copy()
    d["_const"] = 1.0
    cols = controls + ["_const"]
    mat = d[cols].values
    vif = {c: float(variance_inflation_factor(mat, i))
           for i, c in enumerate(cols) if c != "_const"}
    corr = {c: float(np.corrcoef(df[c].astype(float), df["est_age"].astype(float))[0, 1])
            for c in controls}
    return {"vif": vif, "corr_with_est_age": corr}


def orthogonalized_age_residual(df: pd.DataFrame, outcome: str = "int_rate",
                                controls: list[str] | None = None,
                                age_band_col: str = "age_band") -> BandResult:
    """Cell C (literal orthogonalization): regress est_age on the lawful controls, take the
    residual (age-not-explained-by-risk), then run the band residual of price on bands defined
    over that orthogonalized age. Isolates the age signal beyond what risk predicts.

    The age bands are recomputed on the ORIGINAL est_age (so band membership is unchanged); the
    orthogonalization enters by adding the age-residual as a control, removing the part of price
    explained by the risk-predictable component of age. This keeps band labels interpretable
    while pricing only the age-beyond-risk component.
    """
    controls = list(DEFAULT_CONTROLS if controls is None else controls)
    d = df.copy()
    numeric = " + ".join(controls)
    age_model = smf.ols(f"est_age ~ {numeric} + C(purpose)", data=d).fit()
    d["_age_resid"] = d["est_age"] - age_model.fittedvalues
    # price on age-bands, controlling for the risk-predictable age component implicitly removed:
    # add _age_resid is NOT what we want (that re-adds age); instead we band on est_age but
    # control for the FITTED (risk-predictable) age so only age-beyond-risk drives band coefs.
    d["_age_riskpart"] = age_model.fittedvalues
    return fit_band_residuals(d, outcome=outcome, controls=controls,
                              age_band_col=age_band_col, extra_terms="_age_riskpart")
