"""Tests for wedge/shap_pricing.py — the pure metrics behind the SHAP-vs-pricing
non-inferiority experiment (pre-reg: docs/superpowers/specs/2026-05-12-shap-vs-pricing-preregistration-note.md).

These functions take SHAP value matrices + feature names + a within-grade mask
and compute the pre-registered recovery criteria (C1 dispersion, C2 prominence,
C3 dependence-materiality, C5 attribution-gap). The script
`scripts/shap_vs_pricing.py` does the slow data load + model fit + TreeSHAP and
calls these; the metrics are unit-tested here against planted fixtures.
"""
from __future__ import annotations

import numpy as np
import pytest

from wedge.shap_pricing import (
    attribution_rank,
    dependence_materiality,
    subgrade_to_ordinal,
    within_grade_dispersion_ratio,
    within_grade_feature_rank,
    within_grade_mean_abs,
)


# ---------------------------------------------------------------------------
# subgrade_to_ordinal
# ---------------------------------------------------------------------------
def test_subgrade_to_ordinal_endpoints_and_order():
    assert subgrade_to_ordinal("A1") == 0
    assert subgrade_to_ordinal("A5") == 4
    assert subgrade_to_ordinal("B1") == 5
    assert subgrade_to_ordinal("C2") == 11
    assert subgrade_to_ordinal("G5") == 34
    # Monotone in the obvious order.
    grades = ["A1", "A3", "B1", "B5", "C2", "D4", "G5"]
    ords = [subgrade_to_ordinal(g) for g in grades]
    assert ords == sorted(ords)
    assert len(set(ords)) == len(ords)


def test_subgrade_to_ordinal_rejects_garbage():
    with pytest.raises(ValueError):
        subgrade_to_ordinal("H1")
    with pytest.raises(ValueError):
        subgrade_to_ordinal("A6")
    with pytest.raises(ValueError):
        subgrade_to_ordinal("A0")
    with pytest.raises(ValueError):
        subgrade_to_ordinal("AA")


# ---------------------------------------------------------------------------
# within_grade_dispersion_ratio (C1)
# ---------------------------------------------------------------------------
def test_dispersion_ratio_compressed_when_grade_is_homogeneous():
    # Population SHAP_DTI spans a wide range; the grade-G subset is a tight
    # cluster -> ratio small (the grade "used up" the cross-grade DTI spread).
    rng = np.random.default_rng(0)
    shap_dti = rng.normal(0, 1.0, size=5000)
    grade_mask = np.zeros(5000, dtype=bool)
    # Grade members all near +0.4 with tiny within-grade spread.
    grade_idx = rng.choice(5000, size=400, replace=False)
    shap_dti[grade_idx] = rng.normal(0.4, 0.05, size=400)
    grade_mask[grade_idx] = True
    ratio = within_grade_dispersion_ratio(shap_dti, grade_mask)
    assert ratio < 0.25  # pre-registered C1 threshold


def test_dispersion_ratio_high_when_grade_spans_population():
    rng = np.random.default_rng(1)
    shap_dti = rng.normal(0, 1.0, size=5000)
    grade_mask = rng.random(5000) < 0.1  # a random 10% — same spread as pop
    ratio = within_grade_dispersion_ratio(shap_dti, grade_mask)
    assert ratio > 0.8


def test_dispersion_ratio_zero_population_std_is_zero_not_nan():
    shap_dti = np.zeros(100)
    grade_mask = np.zeros(100, dtype=bool)
    grade_mask[:10] = True
    assert within_grade_dispersion_ratio(shap_dti, grade_mask) == 0.0


# ---------------------------------------------------------------------------
# within_grade_feature_rank (C2) and within_grade_mean_abs
# ---------------------------------------------------------------------------
def _toy_shap(n: int, seed: int = 0):
    """3 features: 'fico' large, 'dti' medium, 'inq' small."""
    rng = np.random.default_rng(seed)
    fico = rng.normal(0, 3.0, size=n)
    dti = rng.normal(0, 1.0, size=n)
    inq = rng.normal(0, 0.2, size=n)
    return np.column_stack([fico, dti, inq]), ["fico", "dti", "inq"]


def test_feature_rank_orders_by_within_grade_mean_abs():
    sv, names = _toy_shap(2000)
    mask = np.ones(2000, dtype=bool)
    assert within_grade_feature_rank(sv, names, mask, "fico") == 1
    assert within_grade_feature_rank(sv, names, mask, "dti") == 2
    assert within_grade_feature_rank(sv, names, mask, "inq") == 3


def test_feature_rank_respects_the_mask():
    # Build SHAP where, inside the grade subset, 'dti' is the biggest.
    rng = np.random.default_rng(2)
    n = 2000
    fico = rng.normal(0, 3.0, size=n)
    dti = rng.normal(0, 1.0, size=n)
    inq = rng.normal(0, 0.2, size=n)
    mask = np.zeros(n, dtype=bool)
    mask[:300] = True
    dti[:300] = rng.normal(0, 10.0, size=300)   # dti dominates inside the grade
    fico[:300] = rng.normal(0, 0.5, size=300)
    sv = np.column_stack([fico, dti, inq])
    names = ["fico", "dti", "inq"]
    assert within_grade_feature_rank(sv, names, mask, "dti") == 1


def test_within_grade_mean_abs_value():
    sv = np.array([[1.0, -2.0], [3.0, 4.0], [-5.0, 0.0]])
    names = ["a", "b"]
    mask = np.array([True, True, False])
    # mean(|a|) over first two rows = (1 + 3)/2 = 2.0
    assert within_grade_mean_abs(sv, names, mask, "a") == pytest.approx(2.0)
    assert within_grade_mean_abs(sv, names, mask, "b") == pytest.approx(3.0)


def test_feature_rank_unknown_feature_raises():
    sv, names = _toy_shap(10)
    with pytest.raises(ValueError):
        within_grade_feature_rank(sv, names, np.ones(10, dtype=bool), "nope")


# ---------------------------------------------------------------------------
# dependence_materiality (C3)
# ---------------------------------------------------------------------------
def test_dependence_materiality_linear_relationship():
    # SHAP_DTI = 0.5 * DTI + noise. Between DTI=10 and DTI=20 the dependence
    # plot rises by ~5.0 units.
    rng = np.random.default_rng(0)
    dti = rng.uniform(2, 40, size=20000)
    shap_dti = 0.5 * dti + rng.normal(0, 0.1, size=20000)
    delta = dependence_materiality(dti, shap_dti, lo=10.0, hi=20.0)
    assert delta == pytest.approx(5.0, abs=0.5)


def test_dependence_materiality_flat_relationship_is_immaterial():
    rng = np.random.default_rng(1)
    dti = rng.uniform(2, 40, size=20000)
    # DTI's SHAP effect is concentrated at the high tail only; flat in [10,20].
    shap_dti = np.where(dti > 32, 0.3 * (dti - 32), 0.0) + rng.normal(0, 0.02, size=20000)
    delta = dependence_materiality(dti, shap_dti, lo=10.0, hi=20.0)
    assert delta < 1.0  # pre-registered C3 threshold (sub-grade units)


# ---------------------------------------------------------------------------
# attribution_rank (C5 building block)
# ---------------------------------------------------------------------------
def test_attribution_rank_global():
    sv, names = _toy_shap(3000)
    assert attribution_rank(sv, names, "fico") == 1
    assert attribution_rank(sv, names, "dti") == 2
    assert attribution_rank(sv, names, "inq") == 3
