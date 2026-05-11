"""Tests for wedge.i_pred — per-case predictive disagreement between R_T and R_F.

Per spec §4.2:
    I_pred(x) = |E[h_T(x) | h_T ∈ R_T(ε_T)] − E[h_F(x) | h_F ∈ R_F(ε_F)]|

V1 default emits on the predicted-probability surface (each model's T = P(grant)
at case x); the hard-label variant is named in the spec but not the V1 default.
"""

from __future__ import annotations

import pytest

from wedge.i_pred import compute_i_pred


class _StubModel:
    """Minimal stub mimicking CartModel.emit_for_case for I_pred tests.

    Real CartModel emits a dict including T (P(grant)); compute_i_pred only
    reads `T`, so the stub returns the configured value.
    """

    def __init__(self, t_value: float):
        self._t = t_value

    def emit_for_case(self, case_features):
        return {"T": self._t, "F": 1.0 - self._t, "leaf": "stub", "leaf_id": 0}


def test_i_pred_zero_when_sets_agree():
    """If every member of R_T and R_F predicts P(grant)=0.8 at case x, I_pred=0."""
    R_T_models = [_StubModel(0.8) for _ in range(3)]
    R_F_models = [_StubModel(0.8) for _ in range(3)]
    case = {"feature": 1.0}
    assert compute_i_pred(R_T_models, R_F_models, case) == pytest.approx(0.0)


def test_i_pred_maximum_when_sets_disagree_fully():
    """R_T predicts P(grant)=1.0, R_F predicts P(grant)=0.0 -> I_pred=1.0."""
    R_T_models = [_StubModel(1.0) for _ in range(2)]
    R_F_models = [_StubModel(0.0) for _ in range(2)]
    case = {"feature": 1.0}
    assert compute_i_pred(R_T_models, R_F_models, case) == pytest.approx(1.0)


def test_i_pred_is_absolute_value():
    """I_pred is symmetric: swap R_T and R_F, same value."""
    R_T_models = [_StubModel(0.3) for _ in range(2)]
    R_F_models = [_StubModel(0.7) for _ in range(2)]
    case = {"feature": 1.0}
    forward = compute_i_pred(R_T_models, R_F_models, case)
    reverse = compute_i_pred(R_F_models, R_T_models, case)
    assert forward == pytest.approx(reverse)
    assert forward == pytest.approx(0.4)


def test_i_pred_averages_within_each_set():
    """E[h_T(x)] is the *mean* of T across R_T members, not max/min."""
    R_T_models = [_StubModel(0.6), _StubModel(0.8), _StubModel(1.0)]  # mean 0.8
    R_F_models = [_StubModel(0.0), _StubModel(0.4)]  # mean 0.2
    case = {"feature": 1.0}
    assert compute_i_pred(R_T_models, R_F_models, case) == pytest.approx(0.6)


def test_i_pred_raises_on_empty_set():
    """Empty R_T or R_F has no defined mean prediction; surface explicitly
    rather than silently returning NaN."""
    case = {"feature": 1.0}
    with pytest.raises(ValueError, match="empty"):
        compute_i_pred([], [_StubModel(0.5)], case)
    with pytest.raises(ValueError, match="empty"):
        compute_i_pred([_StubModel(0.5)], [], case)


def test_i_pred_integrates_with_real_cart_models():
    """End-to-end: real fitted CART models from the wedge pipeline produce
    a finite I_pred value at an admissible case."""
    import pandas as pd

    from wedge.models import fit_model
    from wedge.tests.fixtures import FEATURE_COLS, tiny_separable_dataset

    df = tiny_separable_dataset(seed=0)
    # Two slightly different models; should give a small but well-defined I_pred.
    m1 = fit_model(
        df[FEATURE_COLS], df["label"], model_id="m1",
        max_depth=3, min_samples_leaf=5, feature_subset=tuple(FEATURE_COLS),
        random_state=0,
    )
    m2 = fit_model(
        df[FEATURE_COLS], df["label"], model_id="m2",
        max_depth=5, min_samples_leaf=10, feature_subset=tuple(FEATURE_COLS),
        random_state=1,
    )
    low_risk = {"fico_proxy": 750, "dti_proxy": 10, "income_proxy": 100000, "history_depth": 20}
    val = compute_i_pred([m1], [m2], low_risk)
    assert 0.0 <= val <= 1.0
