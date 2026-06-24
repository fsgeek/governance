"""Age × realized lender return: did the young-end overcharge actually PAY OFF for the lender?

Pure statistics, no file I/O. The runner (scripts/age_realized_return.py) handles loading.
See docs/superpowers/specs/2026-06-23-age-realized-return-design.md for the frozen ledger.

Lineage: the RAIL block of runs/lc_age_grade_default_2026-06-22.txt proved grade prices the young
2.9x harder than realized DEFAULT justifies. Default incidence != lender return, so this module asks
whether the over-pricing converted to realized margin (Claude: no, bias-against-lender-interest) or
profit (Tony: yes, and the gradient indexes deliberateness).

Reuses the band machinery from wedge.age_residual so the age-band definitions stay identical across
the whole age program.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from wedge.age_residual import AGE_BANDS, REFERENCE_BAND_INDEX

# Lawful risk controls, identical set to the residual analysis (purpose added as a factor in the
# formula, not here). term_months kept: duration is a lawful price input.
RETURN_CONTROLS = ["fico_mid", "dti", "annual_inc", "loan_amnt", "term_months"]


@dataclass
class BandReturn:
    band_val: dict           # band index -> coefficient vs reference, in RETURN POINTS (pp of funded principal)
    band_ci: dict            # band index -> (lo, hi) 95% CI, same units
    n_per_band: dict
    r2: float
    reference_band: int


def _band_formula(outcome: str, controls: list[str], ref: int, extra: str = "") -> str:
    numeric = " + ".join(controls)
    f = f"{outcome} ~ C(_band, Treatment(reference={ref})) + {numeric} + C(purpose)"
    if extra:
        f += " + " + extra
    return f


def _choose_reference(present_bands) -> int:
    counts = present_bands.value_counts()
    if REFERENCE_BAND_INDEX in counts.index:
        return REFERENCE_BAND_INDEX
    return int(counts.idxmax())


def fit_band_return(df: pd.DataFrame, outcome: str,
                    controls: list[str] | None = None,
                    age_band_col: str = "age_band",
                    extra_terms: str = "") -> BandReturn:
    """OLS of a realized-return outcome on age-band dummies + lawful controls.

    `outcome` is a *rate of return on funded principal* (a fraction, e.g. 0.12 = 12%); coefficients
    are multiplied by 100 to report return points (pp). The reference band coefficient is identically 0.
    `extra_terms` lets the runner add "C(grade)" for the net-of-grade cell without a new function —
    same pattern as wedge.age_residual.fit_band_residuals.
    """
    controls = list(RETURN_CONTROLS if controls is None else controls)
    d = df.copy()
    d["_band"] = pd.Categorical(d[age_band_col])
    ref = _choose_reference(d[age_band_col])
    model = smf.ols(_band_formula(outcome, controls, ref, extra_terms), data=d).fit()
    conf = model.conf_int()
    band_val, band_ci = {}, {}
    for i in range(len(AGE_BANDS)):
        if i == ref:
            band_val[i] = 0.0
            band_ci[i] = (0.0, 0.0)
            continue
        term = f"C(_band, Treatment(reference={ref}))[T.{i}]"
        if term in model.params.index:
            band_val[i] = float(model.params[term]) * 100.0
            lo, hi = conf.loc[term]
            band_ci[i] = (float(lo) * 100.0, float(hi) * 100.0)
        else:
            band_val[i] = float("nan")
            band_ci[i] = (float("nan"), float("nan"))
    n_per_band = d[age_band_col].value_counts().to_dict()
    return BandReturn(
        band_val=band_val,
        band_ci=band_ci,
        n_per_band={int(k): int(v) for k, v in n_per_band.items()},
        r2=float(model.rsquared),
        reference_band=ref,
    )


def realized_return(df: pd.DataFrame) -> pd.Series:
    """(total_pymnt + recoveries - funded_amnt) / funded_amnt. Resolved loans only (out_prncp~0)."""
    return (df["total_pymnt"] + df["recoveries"] - df["funded_amnt"]) / df["funded_amnt"]


def interest_collected_rate(df: pd.DataFrame) -> pd.Series:
    """total_rec_int / funded_amnt — interest the lender actually collected, as a rate."""
    return df["total_rec_int"] / df["funded_amnt"]


def loss_rate(df: pd.DataFrame) -> pd.Series:
    """(funded_amnt - total_rec_prncp - recoveries) / funded_amnt — principal not recovered, as a rate.
    Positive = principal lost; near 0 = fully repaid; can be slightly negative if recoveries+principal
    overshoot funded (rare rounding)."""
    return (df["funded_amnt"] - df["total_rec_prncp"] - df["recoveries"]) / df["funded_amnt"]


def gradient_characterization(band_return: BandReturn) -> dict:
    """Tony's deliberateness instrument: characterize the band-return-vs-age GRADIENT, not just the
    young point. A clean monotone profit-by-youth slope is the fingerprint of a steering process;
    a noisy point estimate with no slope is 'they're not looking'.

    Returns:
      slope_pp_per_band: OLS slope of band coefficient on band index (signed; negative = profit rises
                         toward the young end, since lower index = younger).
      slope_r2:          R^2 of that fit — how cleanly monotone (the deliberateness signal strength).
      monotone_young_to_old: True iff the coefficients are non-increasing from young band to old band
                         (profit highest at the young end and falling) OR non-decreasing (the opposite),
                         reported with direction. Strict monotonicity across all populated bands.
      spearman:          rank correlation of band coefficient with band index (robust monotonicity).
    Uses only populated bands (n>0) and excludes the reference (coef==0 by construction is informative
    only relative to neighbors, so we KEEP it — it is a real data point at value 0).
    """
    idx = sorted(i for i in band_return.band_val
                 if not np.isnan(band_return.band_val[i]) and band_return.n_per_band.get(i, 0) > 0)
    if len(idx) < 3:
        return {"slope_pp_per_band": float("nan"), "slope_r2": float("nan"),
                "monotone": "insufficient_bands", "spearman": float("nan")}
    x = np.array(idx, dtype=float)
    y = np.array([band_return.band_val[i] for i in idx], dtype=float)
    # OLS slope of coefficient on band index
    A = np.vstack([x, np.ones_like(x)]).T
    slope, _intercept = np.linalg.lstsq(A, y, rcond=None)[0]
    yhat = A @ np.array([slope, _intercept])
    ss_res = float(np.sum((y - yhat) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    slope_r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    # strict monotonicity, young (low idx) to old (high idx)
    diffs = np.diff(y)
    if np.all(diffs <= 0):
        mono = "monotone_decreasing_young_to_old"   # profit highest at young end
    elif np.all(diffs >= 0):
        mono = "monotone_increasing_young_to_old"
    else:
        mono = "non_monotone"
    # Spearman rank corr (robust to nonlinearity)
    rx = np.asarray(pd.Series(x).rank())
    ry = np.asarray(pd.Series(y).rank())
    spear = float(np.corrcoef(rx, ry)[0, 1]) if len(idx) > 1 else float("nan")
    return {"slope_pp_per_band": float(slope), "slope_r2": float(slope_r2),
            "monotone": mono, "spearman": spear}


def inject_return_premium(df: pd.DataFrame, outcome_col: str, band_col: str, young_band: int,
                          premium_pp: float, frac: float, seed: int) -> pd.DataFrame:
    """Positive control (anti-confabulation): add `premium_pp`/100 to the outcome on a random `frac`
    of rows in `young_band`. Cell A must recover ~premium_pp at that band within CI, else the
    estimator is not measuring what we think. Mirrors the planted-premium guard in wedge.age_residual.
    """
    d = df.copy()
    mask = d[band_col] == young_band
    young_idx = d.index[mask]
    rng = np.random.default_rng(seed)
    k = int(len(young_idx) * frac)
    if k == 0:
        return d
    chosen = rng.choice(np.asarray(young_idx), size=k, replace=False)
    d.loc[chosen, outcome_col] = d.loc[chosen, outcome_col] + premium_pp / 100.0
    return d
