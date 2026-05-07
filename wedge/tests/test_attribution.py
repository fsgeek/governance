"""Tests for wedge.attribution — path walk + per-component split attribution."""

from __future__ import annotations

from wedge.attribution import (
    extract_factor_support,
    walk_path,
)
from wedge.models import fit_model
from wedge.tests.fixtures import FEATURE_COLS, tiny_separable_dataset


def _trained_model():
    df = tiny_separable_dataset(seed=0)
    return fit_model(
        df[FEATURE_COLS],
        df["label"],
        model_id="m_attr",
        max_depth=4,
        min_samples_leaf=5,
        feature_subset=tuple(FEATURE_COLS),
        random_state=0,
    )


def test_walk_path_returns_decisions_root_to_leaf():
    model = _trained_model()
    case = {"fico_proxy": 750, "dti_proxy": 10, "income_proxy": 100000, "history_depth": 20}
    path = walk_path(model, case)
    # At minimum, the path describes the splits the case took.
    assert len(path) >= 1
    for entry in path:
        assert "feature" in entry
        assert "threshold" in entry
        assert "direction" in entry  # 'left' or 'right'
        assert "info_gain" in entry
        assert "chosen_grant_purity" in entry
        assert "chosen_deny_purity" in entry
        assert "unchosen_grant_purity" in entry
        assert "unchosen_deny_purity" in entry


def test_factor_support_T_includes_features_routing_toward_grant():
    """For a strongly low-risk case the per-component split should attribute
    feature gain to T (factor_support_T should be non-empty)."""
    model = _trained_model()
    low_risk = {"fico_proxy": 780, "dti_proxy": 8, "income_proxy": 100000, "history_depth": 20}
    fst, fsf = extract_factor_support(model, low_risk, top_k=5)
    # We expect at least one feature to attribute to T because the case is routed
    # to a high-grant-purity leaf along splits that increased grant purity.
    assert len(fst) >= 1
    assert all(0.0 <= e.weight <= 1.0 + 1e-9 for e in fst)


def test_factor_support_F_includes_features_routing_toward_deny():
    model = _trained_model()
    high_risk = {"fico_proxy": 590, "dti_proxy": 45, "income_proxy": 25000, "history_depth": 1}
    fst, fsf = extract_factor_support(model, high_risk, top_k=5)
    assert len(fsf) >= 1
    assert all(0.0 <= e.weight <= 1.0 + 1e-9 for e in fsf)


def test_factor_support_top_k_truncates():
    model = _trained_model()
    case = {"fico_proxy": 720, "dti_proxy": 25, "income_proxy": 60000, "history_depth": 5}
    fst, fsf = extract_factor_support(model, case, top_k=1)
    assert len(fst) <= 1
    assert len(fsf) <= 1


def test_factor_support_weights_sorted_descending():
    model = _trained_model()
    case = {"fico_proxy": 600, "dti_proxy": 40, "income_proxy": 30000, "history_depth": 3}
    fst, fsf = extract_factor_support(model, case, top_k=10)
    for entries in (fst, fsf):
        weights = [e.weight for e in entries]
        assert weights == sorted(weights, reverse=True)
