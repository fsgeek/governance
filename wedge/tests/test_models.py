"""Tests for wedge.models — CART wrapper with T/F emission."""

from __future__ import annotations

import numpy as np

from wedge.models import CartModel, fit_model
from wedge.tests.fixtures import FEATURE_COLS, tiny_separable_dataset


def test_fit_model_reaches_full_accuracy_on_separable():
    df = tiny_separable_dataset(seed=0)
    model = fit_model(
        df[FEATURE_COLS],
        df["label"],
        model_id="m1",
        max_depth=4,
        min_samples_leaf=5,
        feature_subset=tuple(FEATURE_COLS),
        random_state=0,
    )
    preds = model.predict(df[FEATURE_COLS])
    assert (preds == df["label"]).mean() > 0.95


def test_emit_returns_T_plus_F_equal_one():
    df = tiny_separable_dataset(seed=0)
    model = fit_model(
        df[FEATURE_COLS],
        df["label"],
        model_id="m1",
        max_depth=4,
        min_samples_leaf=5,
        feature_subset=tuple(FEATURE_COLS),
        random_state=0,
    )
    sample = df.iloc[0:5][FEATURE_COLS]
    emissions = [model.emit_for_case(sample.iloc[i].to_dict()) for i in range(5)]
    for e in emissions:
        assert abs(e["T"] + e["F"] - 1.0) < 1e-9
        assert 0.0 <= e["T"] <= 1.0
        assert 0.0 <= e["F"] <= 1.0


def test_emit_T_high_for_low_risk_case():
    df = tiny_separable_dataset(seed=0)
    model = fit_model(
        df[FEATURE_COLS],
        df["label"],
        model_id="m1",
        max_depth=4,
        min_samples_leaf=5,
        feature_subset=tuple(FEATURE_COLS),
        random_state=0,
    )
    # Low-risk case per the rule: high FICO, low DTI -> label=0 -> T should be high.
    low_risk = {"fico_proxy": 750, "dti_proxy": 10, "income_proxy": 100000, "history_depth": 20}
    e = model.emit_for_case(low_risk)
    assert e["T"] > 0.7


def test_emit_F_high_for_high_risk_case():
    df = tiny_separable_dataset(seed=0)
    model = fit_model(
        df[FEATURE_COLS],
        df["label"],
        model_id="m1",
        max_depth=4,
        min_samples_leaf=5,
        feature_subset=tuple(FEATURE_COLS),
        random_state=0,
    )
    high_risk = {"fico_proxy": 600, "dti_proxy": 45, "income_proxy": 30000, "history_depth": 2}
    e = model.emit_for_case(high_risk)
    assert e["F"] > 0.7


def test_feature_subset_restricts_features():
    df = tiny_separable_dataset(seed=0)
    model = fit_model(
        df[FEATURE_COLS],
        df["label"],
        model_id="m_restricted",
        max_depth=4,
        min_samples_leaf=5,
        feature_subset=("fico_proxy", "dti_proxy"),
        random_state=0,
    )
    assert tuple(model.feature_subset) == ("fico_proxy", "dti_proxy")
    # Predict using only the subset columns; ignored columns should not affect output.
    case_a = {"fico_proxy": 750, "dti_proxy": 10, "income_proxy": 100000, "history_depth": 20}
    case_b = {"fico_proxy": 750, "dti_proxy": 10, "income_proxy": 30000, "history_depth": 2}
    e_a = model.emit_for_case(case_a)
    e_b = model.emit_for_case(case_b)
    assert e_a["T"] == e_b["T"]
    assert e_a["F"] == e_b["F"]
