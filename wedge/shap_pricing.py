"""Pure metrics for the SHAP-vs-pricing non-inferiority experiment.

Pre-registration: docs/superpowers/specs/2026-05-12-shap-vs-pricing-preregistration-note.md.

The experiment asks whether SHAP, applied the standard way to the deployed
grading model, recovers the within-grade DTI structure the policy-constrained
stratification test (`wedge/pricing.py`) found. These functions compute the
pre-registered recovery criteria over a SHAP value matrix; the slow data load,
model fit, and TreeSHAP call live in `scripts/shap_vs_pricing.py`.

Conventions:
- A "SHAP value matrix" is a dense (n_cases, n_features) float array of margin
  contributions (TreeExplainer's standard output for a single-output model).
- `feature_names` is the column order of that matrix.
- A "grade mask" is a boolean array of length n_cases selecting one sub-grade's
  borrowers.
- Sub-grade ordinal scale: A1=0, A2=1, ..., A5=4, B1=5, ..., G5=34 (the unit in
  which C3's dependence-materiality threshold of 1.0 is stated).
"""
from __future__ import annotations

import numpy as np

_GRADE_LETTERS = "ABCDEFG"


def subgrade_to_ordinal(sub_grade: str) -> int:
    """Map a LendingClub sub-grade string ("A1".."G5") to an ordinal 0..34.

    Raises ValueError on anything outside that grid.
    """
    s = str(sub_grade).strip().upper()
    if len(s) != 2 or s[0] not in _GRADE_LETTERS or not s[1].isdigit():
        raise ValueError(f"not a sub-grade: {sub_grade!r}")
    letter_idx = _GRADE_LETTERS.index(s[0])
    digit = int(s[1])
    if not 1 <= digit <= 5:
        raise ValueError(f"sub-grade digit out of range: {sub_grade!r}")
    return letter_idx * 5 + (digit - 1)


def _feature_col(feature_names, feature: str) -> int:
    try:
        return list(feature_names).index(feature)
    except ValueError:
        raise ValueError(f"feature {feature!r} not in {list(feature_names)!r}")


def within_grade_dispersion_ratio(
    shap_feature: np.ndarray, grade_mask: np.ndarray
) -> float:
    """C1: std of a feature's SHAP values inside one grade, divided by the
    population std of the same feature's SHAP values.

    Small (< 0.25, the pre-registered threshold) means the grade treats its
    members as near-equivalent on this feature — the cross-grade variation is
    what the model spent assigning the grade, and the within-grade residual
    gets little attribution. Returns 0.0 when the population std is 0.
    """
    shap_feature = np.asarray(shap_feature, dtype=float)
    grade_mask = np.asarray(grade_mask, dtype=bool)
    pop_std = float(np.std(shap_feature))
    if pop_std == 0.0:
        return 0.0
    if grade_mask.sum() < 2:
        return 0.0
    grade_std = float(np.std(shap_feature[grade_mask]))
    return grade_std / pop_std


def _mean_abs_by_feature(shap_matrix: np.ndarray, mask: np.ndarray) -> np.ndarray:
    shap_matrix = np.asarray(shap_matrix, dtype=float)
    mask = np.asarray(mask, dtype=bool)
    if mask.sum() == 0:
        return np.zeros(shap_matrix.shape[1])
    return np.abs(shap_matrix[mask]).mean(axis=0)


def within_grade_mean_abs(
    shap_matrix: np.ndarray, feature_names, grade_mask: np.ndarray, feature: str
) -> float:
    """Mean |SHAP| of one feature over the borrowers in one grade."""
    col = _feature_col(feature_names, feature)
    return float(_mean_abs_by_feature(shap_matrix, grade_mask)[col])


def within_grade_feature_rank(
    shap_matrix: np.ndarray, feature_names, grade_mask: np.ndarray, feature: str
) -> int:
    """C2: rank of one feature among all features by within-grade mean |SHAP|.

    1 = the most-attributed feature inside the grade. Pre-registered C2 fires
    when this is <= 3 for the recovered feature in a flagged grade.
    """
    col = _feature_col(feature_names, feature)
    mabs = _mean_abs_by_feature(shap_matrix, grade_mask)
    # Rank by descending mean|SHAP|; ties broken by column index (stable).
    order = np.argsort(-mabs, kind="stable")
    return int(np.where(order == col)[0][0]) + 1


def attribution_rank(shap_matrix: np.ndarray, feature_names, feature: str) -> int:
    """Global rank of one feature by population mean |SHAP| (1 = highest).

    The building block of C5: the pricing-recovered feature should rank
    materially higher on a realized-default model `f` than on the grading
    surrogate `g` for "the grade underuses this factor" to be SHAP-visible at
    all — and even then only via the `f`-vs-`g` diff, not SHAP on `g` alone.
    """
    full_mask = np.ones(np.asarray(shap_matrix).shape[0], dtype=bool)
    return within_grade_feature_rank(shap_matrix, feature_names, full_mask, feature)


def dependence_materiality(
    feature_values: np.ndarray,
    shap_feature: np.ndarray,
    *,
    lo: float,
    hi: float,
    n_bins: int = 20,
) -> float:
    """C3: how much the SHAP-dependence relationship for a feature changes
    between two feature values.

    Bins the population by `feature_values` quantiles, takes the mean SHAP
    value per bin, and returns |mean_SHAP(bin containing hi) - mean_SHAP(bin
    containing lo)|. This is the "read the dependence plot at two x-values"
    operation a validator does. Stated in the units of whatever the explained
    model outputs; for the grading surrogate `g` (target = sub-grade ordinal)
    the pre-registered C3 threshold is 1.0 (one sub-grade unit) across the
    [10, 20] DTI interval.
    """
    fv = np.asarray(feature_values, dtype=float)
    sv = np.asarray(shap_feature, dtype=float)
    finite = np.isfinite(fv) & np.isfinite(sv)
    fv, sv = fv[finite], sv[finite]
    if fv.size == 0:
        return 0.0
    # Quantile bin edges over the population; de-duplicated for lumpy features.
    edges = np.unique(np.quantile(fv, np.linspace(0.0, 1.0, n_bins + 1)))
    if edges.size < 2:
        return 0.0

    def _bin_mean_at(x: float) -> float:
        # Bin index for x (clamped into [0, n_edges-2]).
        idx = int(np.clip(np.searchsorted(edges, x, side="right") - 1, 0, edges.size - 2))
        in_bin = (fv >= edges[idx]) & (fv <= edges[idx + 1])
        if not in_bin.any():
            # Fall back to nearest observed point.
            return float(sv[np.argmin(np.abs(fv - x))])
        return float(sv[in_bin].mean())

    return abs(_bin_mean_at(hi) - _bin_mean_at(lo))
