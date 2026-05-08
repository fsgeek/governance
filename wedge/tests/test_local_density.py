"""Unit tests for the local_density indeterminacy species."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from wedge.indeterminacy.local_density import (
    LeafStatistics,
    Z_ATYPICAL,
    Z_CAP,
    compute_local_density,
)
from wedge.models import fit_model
from wedge.tests.fixtures import tiny_separable_dataset


def _fit_simple_model():
    df = tiny_separable_dataset(seed=0)
    X = df[["fico_proxy", "dti_proxy", "income_proxy", "history_depth"]]
    y = df["label"]
    model = fit_model(
        X,
        y,
        model_id="test",
        max_depth=3,
        min_samples_leaf=5,
        feature_subset=("fico_proxy", "dti_proxy", "income_proxy", "history_depth"),
        random_state=0,
    )
    return model, X


def test_leaf_statistics_fit_covers_all_leaves():
    model, X = _fit_simple_model()
    stats = LeafStatistics.fit(model, X)
    leaf_ids_observed = np.unique(model.tree.apply(X.to_numpy()))
    assert set(stats.stats.keys()) == set(int(lid) for lid in leaf_ids_observed)
    for lid in stats.stats:
        assert stats.leaf_n[lid] > 0


def test_centroid_case_scores_ordinary():
    model, X = _fit_simple_model()
    stats = LeafStatistics.fit(model, X)
    # Pick a leaf with at least 2 training samples
    leaf_id = next(lid for lid, n in stats.leaf_n.items() if n >= 2)
    centroid = {f: stats.stats[leaf_id][f][0] for f in stats.feature_names}
    comp = compute_local_density(centroid, leaf_id, stats)
    assert comp.species == "local_density"
    assert comp.score < Z_ATYPICAL
    assert comp.direction == "ordinary"


def test_far_case_scores_atypical():
    model, X = _fit_simple_model()
    stats = LeafStatistics.fit(model, X)
    leaf_id = next(lid for lid, n in stats.leaf_n.items() if n >= 5)
    # Build a case far from this leaf's centroid in fico_proxy
    case = {f: stats.stats[leaf_id][f][0] for f in stats.feature_names}
    mu, sigma = stats.stats[leaf_id]["fico_proxy"]
    case["fico_proxy"] = mu + 5 * max(sigma, 1.0)  # 5 sigma away (or 5 if sigma=0)
    comp = compute_local_density(case, leaf_id, stats)
    assert comp.score > Z_ATYPICAL
    assert comp.direction == "atypical"
    # The far feature should dominate factor_support
    assert comp.factor_support[0].feature == "fico_proxy"


def test_factor_support_sorted_descending():
    model, X = _fit_simple_model()
    stats = LeafStatistics.fit(model, X)
    leaf_id = next(iter(stats.stats))
    centroid = {f: stats.stats[leaf_id][f][0] for f in stats.feature_names}
    # Push two features off-centroid by different amounts
    for f, multiplier in zip(stats.feature_names[:2], (3.0, 1.0)):
        mu, sigma = stats.stats[leaf_id][f]
        centroid[f] = mu + multiplier * max(sigma, 1.0)
    comp = compute_local_density(centroid, leaf_id, stats)
    weights = [e.weight for e in comp.factor_support]
    assert weights == sorted(weights, reverse=True)


def test_nan_features_skipped():
    model, X = _fit_simple_model()
    stats = LeafStatistics.fit(model, X)
    leaf_id = next(iter(stats.stats))
    case = {f: stats.stats[leaf_id][f][0] for f in stats.feature_names}
    # Replace one feature with NaN
    case[stats.feature_names[0]] = float("nan")
    comp = compute_local_density(case, leaf_id, stats)
    # NaN feature should not appear in factor support
    feature_set = {e.feature for e in comp.factor_support}
    assert stats.feature_names[0] not in feature_set


def test_all_nan_returns_unknown():
    model, X = _fit_simple_model()
    stats = LeafStatistics.fit(model, X)
    leaf_id = next(iter(stats.stats))
    case = {f: float("nan") for f in stats.feature_names}
    comp = compute_local_density(case, leaf_id, stats)
    assert comp.score == 0.0
    assert comp.direction == "unknown"
    assert comp.factor_support == []


def test_unknown_leaf_returns_unknown():
    model, X = _fit_simple_model()
    stats = LeafStatistics.fit(model, X)
    case = {f: 0.0 for f in stats.feature_names}
    bogus_leaf_id = max(stats.stats) + 999
    comp = compute_local_density(case, bogus_leaf_id, stats)
    assert comp.score == 0.0
    assert comp.direction == "unknown"


def test_zero_variance_leaf_caps_at_z_cap():
    """When a leaf has zero variance on a feature and the case differs, z is capped."""
    feature_names = ("x", "y")
    # Hand-construct a LeafStatistics with zero variance on x
    stats = LeafStatistics(
        feature_names=feature_names,
        stats={1: {"x": (5.0, 0.0), "y": (10.0, 1.0)}},
        leaf_n={1: 3},
    )
    case_at_value = {"x": 5.0, "y": 10.0}
    comp = compute_local_density(case_at_value, 1, stats)
    # x contributes 0, y contributes 0 => score 0
    assert comp.score == 0.0

    case_far_off = {"x": 99.0, "y": 10.0}
    comp = compute_local_density(case_far_off, 1, stats)
    # x's z is capped at Z_CAP
    assert comp.score == pytest.approx(Z_CAP)
    assert comp.direction == "atypical"
