"""Tests for wedge.surprise — outcome surprise model S (spec §5.2).

Under the grant-as-positive convention (spec §2.7 OD-9a / OD-13), the surprise
model predicts P(grant | origination_features). Realized outcome surprise is
the signed difference (realized_label - predicted_p_grant); positive surprise
means the case got a *better* outcome than predicted, negative surprise means
*worse*.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from wedge.surprise import (
    compute_outcome_surprise,
    predict_p_grant,
    train_surprise_model,
)


# ---------------------------------------------------------------------------
# compute_outcome_surprise — pure function on scalars / arrays
# ---------------------------------------------------------------------------


def test_outcome_surprise_zero_when_prediction_matches_realized():
    """Case predicted P(grant)=1.0 and realized grant (label=1) -> surprise=0."""
    assert compute_outcome_surprise(p_grant=1.0, realized_label=1) == pytest.approx(0.0)
    assert compute_outcome_surprise(p_grant=0.0, realized_label=0) == pytest.approx(0.0)


def test_outcome_surprise_positive_when_better_than_predicted():
    """Low predicted P(grant), actually granted -> large positive surprise."""
    s = compute_outcome_surprise(p_grant=0.1, realized_label=1)
    assert s == pytest.approx(0.9)


def test_outcome_surprise_negative_when_worse_than_predicted():
    """High predicted P(grant), actually denied -> large negative surprise."""
    s = compute_outcome_surprise(p_grant=0.95, realized_label=0)
    assert s == pytest.approx(-0.95)


def test_outcome_surprise_vectorized():
    """Accepts numpy / pandas arrays element-wise."""
    p = np.array([0.1, 0.5, 0.9])
    y = np.array([1, 0, 0])
    s = compute_outcome_surprise(p_grant=p, realized_label=y)
    assert s.shape == p.shape
    np.testing.assert_allclose(s, [0.9, -0.5, -0.9])


def test_outcome_surprise_rejects_p_out_of_range():
    with pytest.raises(ValueError, match="probabil"):
        compute_outcome_surprise(p_grant=1.5, realized_label=1)
    with pytest.raises(ValueError, match="probabil"):
        compute_outcome_surprise(p_grant=-0.1, realized_label=1)


# ---------------------------------------------------------------------------
# train_surprise_model + predict_p_grant — end-to-end on a synthetic cohort
# ---------------------------------------------------------------------------


def _synthetic_cohort(n: int = 200, seed: int = 0) -> tuple[pd.DataFrame, pd.Series]:
    """Generate a small lifecycle-completed cohort: features + realized grant label.

    Rule mirrors fixtures.tiny_separable_dataset under the grant-as-positive
    convention: label=1 (grant) iff fico_proxy >= 650 AND dti_proxy <= 30,
    with 10% label noise.
    """
    rng = np.random.default_rng(seed)
    df = pd.DataFrame({
        "fico_proxy": rng.integers(580, 800, size=n),
        "dti_proxy": rng.integers(5, 50, size=n),
        "annual_inc": rng.integers(20000, 200000, size=n),
    })
    base = ((df["fico_proxy"] >= 650) & (df["dti_proxy"] <= 30)).astype(int)
    flip = rng.random(n) < 0.10
    df["label"] = (base.values ^ flip.astype(int)).astype(int)
    return df[["fico_proxy", "dti_proxy", "annual_inc"]], df["label"]


def test_train_surprise_model_returns_calibrated_classifier_with_predict_proba():
    X, y = _synthetic_cohort(n=200, seed=0)
    model = train_surprise_model(X, y, random_state=0)
    # Should expose predict_proba and produce a (n, 2) array on a small batch.
    probs = model.predict_proba(X.iloc[:5])
    assert probs.shape == (5, 2)
    # Row sums ~ 1 (calibrated probability).
    np.testing.assert_allclose(probs.sum(axis=1), 1.0, atol=1e-6)


def test_predict_p_grant_returns_p_label_one():
    """predict_p_grant returns P(label=1) under the grant-as-positive convention."""
    X, y = _synthetic_cohort(n=200, seed=0)
    model = train_surprise_model(X, y, random_state=0)
    p_grant = predict_p_grant(model, X)
    assert p_grant.shape == (len(X),)
    assert (p_grant >= 0).all() and (p_grant <= 1).all()
    # A clearly low-risk case should have higher P(grant) than a clearly high-risk one.
    low_risk = pd.DataFrame([{"fico_proxy": 780, "dti_proxy": 8, "annual_inc": 120000}])
    high_risk = pd.DataFrame([{"fico_proxy": 600, "dti_proxy": 45, "annual_inc": 25000}])
    assert predict_p_grant(model, low_risk)[0] > predict_p_grant(model, high_risk)[0]


def test_surprise_pipeline_end_to_end():
    """Train surprise model on one cohort, score surprise on a different cohort."""
    X_train, y_train = _synthetic_cohort(n=300, seed=0)
    X_eval, y_eval = _synthetic_cohort(n=100, seed=42)
    model = train_surprise_model(X_train, y_train, random_state=0)
    p_grant = predict_p_grant(model, X_eval)
    surprise = compute_outcome_surprise(p_grant=p_grant, realized_label=y_eval.values)
    assert surprise.shape == (100,)
    # Surprises must be in [-1, 1].
    assert (surprise >= -1.0 - 1e-9).all() and (surprise <= 1.0 + 1e-9).all()
