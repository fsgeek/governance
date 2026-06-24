"""Do the young default ABOVE their assigned grade, or AT it? The L2(launder)-vs-L3(honest) discriminant.

Pure statistics, no file I/O. The runner handles loading. The steering-detectability result
(wedge/steering_detectability.py) showed the price-gradient and realized-return sign CANNOT separate
grade-laundering (young over-priced past risk) from honest pricing of latently-riskier young. This does:
within-grade realized default rate. If the young default ABOVE their grade's base rate, grade under-
states their risk (L2-ish); if AT it, grade is honest (L3).

See docs/superpowers/specs/2026-06-23-steering-detectability-design.md (L3 addendum) for lineage.
"""
from __future__ import annotations

import pandas as pd
import statsmodels.formula.api as smf

PRIME_GRADES = ["A", "B", "C"]
SUBPRIME_GRADES = ["D", "E", "F", "G"]


def default_proxy(df: pd.DataFrame, loss_col: str = "loss", thresh: float = 0.01) -> pd.Series:
    """Binary default = realized principal loss above `thresh` (charge-off mass). 1=default."""
    return (df[loss_col] > thresh).astype(int)


def within_grade_default_gap(df: pd.DataFrame, young_band: int = 0,
                             old_band_min: int = 5, grade_col: str = "grade") -> dict:
    """Per-grade realized default rate, young [band==young_band] vs older [band>=old_band_min].
    Returns {grade: {young_rate, old_rate, gap_pp, n_young, n_old}} for grades with both n>30."""
    d = df.copy()
    d["_defaulted"] = default_proxy(d)
    d["_young"] = (d["age_band"] == young_band).astype(int)
    d["_old"] = (d["age_band"] >= old_band_min).astype(int)
    out = {}
    for g in sorted(d[grade_col].dropna().unique()):
        sub = d[d[grade_col] == g]
        y = sub[sub["_young"] == 1]["_defaulted"]
        o = sub[sub["_old"] == 1]["_defaulted"]
        if len(y) > 30 and len(o) > 30:
            out[str(g)] = {
                "young_rate": float(y.mean()), "old_rate": float(o.mean()),
                "gap_pp": float((y.mean() - o.mean()) * 100.0),
                "n_young": int(len(y)), "n_old": int(len(o)),
            }
    return out


def net_of_grade_young_default(df: pd.DataFrame, grades: list[str] | None = None,
                               young_band: int = 0, grade_col: str = "grade") -> dict:
    """OLS of realized default on C(grade) + young indicator, over `grades` (all if None). The `young`
    coefficient = how much the young default ABOVE their grade's base rate, in pp. >0 => grade under-
    grades the young (L2-ish: under-priced risk); ~0 => grade prices young risk honestly (L3)."""
    d = df.copy()
    if grades is not None:
        d = d[d[grade_col].isin(grades)]
    d["_defaulted"] = default_proxy(d)
    d["_young"] = (d["age_band"] == young_band).astype(int)
    m = smf.ols(f"_defaulted ~ C({grade_col}) + _young", data=d).fit()
    coef = float(m.params["_young"]) * 100.0
    lo, hi = m.conf_int().loc["_young"]
    return {"young_above_grade_pp": coef, "ci": (float(lo) * 100.0, float(hi) * 100.0),
            "n": int(len(d)), "excludes_zero": bool(lo * hi > 0)}
