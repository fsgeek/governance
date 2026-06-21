"""Age-residual pricing analysis: does the young-end overcharge survive lawful-risk controls?

Pure statistics, no file I/O. The runner (scripts/age_pricing_residual.py) handles loading.
See docs/superpowers/specs/2026-06-20-age-pricing-residual-design.md for the design and the
frozen prediction ledger.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import statsmodels.formula.api as smf

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


def _band_formula(outcome: str, controls: list[str], extra: str = "") -> str:
    ref = REFERENCE_BAND_INDEX
    numeric = " + ".join(controls)
    f = f"{outcome} ~ C(_band, Treatment(reference={ref})) + {numeric} + C(purpose)"
    if extra:
        f += " + " + extra
    return f


def fit_band_residuals(df: pd.DataFrame, outcome: str = "int_rate",
                       controls: list[str] | None = None,
                       age_band_col: str = "age_band",
                       extra_terms: str = "") -> BandResult:
    """OLS of `outcome` on age-band dummies + lawful controls; recover per-band bps residual.

    The outcome (int_rate) is in percentage points; coefficients are multiplied by 100 to
    report basis points. The reference band coefficient is identically 0. `extra_terms` allows
    the runner to add e.g. "C(grade)" for the net-of-grade decomposition without a new function.
    """
    controls = list(DEFAULT_CONTROLS if controls is None else controls)
    d = df.copy()
    d["_band"] = pd.Categorical(d[age_band_col])
    model = smf.ols(_band_formula(outcome, controls, extra_terms), data=d).fit()
    ref = REFERENCE_BAND_INDEX
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
    )
