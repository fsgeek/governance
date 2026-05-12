"""Tests for wedge/refinement_set.py — the within-grade policy-constrained
refinement epsilon-band (follow-on #6).

Pre-reg: docs/superpowers/specs/2026-05-12-policy-constrained-rashomon-refinement-preregistration-note.md.

The orchestration (`scripts/within_tier_rashomon_test.py`) does the slow data
load and the per-grade band builds across bursts; these tests cover the band
construction, the monotonicity wiring, the de-dup, and the plurality metrics
against planted fixtures.
"""
from __future__ import annotations

import numpy as np
import pytest

from wedge.refinement_set import (
    build_refinement_band,
    pairwise_ranking_spearman,
    refit_member,
    used_feature_set,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
def _within_tier_fixture(n=4000, seed=0):
    """A within-tier-like dataset: default depends mostly on `dti` (monotone up)
    and a little on `annual_inc` (down), nothing on `fico` (already absorbed by
    the tier) or `emp_length`."""
    rng = np.random.default_rng(seed)
    fico = rng.normal(680, 5, n)            # tiny residual variance (tier absorbed it)
    dti = rng.uniform(5, 40, n)
    annual_inc = rng.lognormal(11.0, 0.4, n)
    emp_length = rng.integers(0, 11, n).astype(float)
    logit = -2.0 + 0.06 * (dti - 20) - 0.0000015 * (annual_inc - 60000)
    p = 1 / (1 + np.exp(-logit))
    y = (rng.random(n) < p).astype(int)     # 1 = default
    X = np.column_stack([fico, dti, annual_inc, emp_length])
    names = ["fico_range_low", "dti", "annual_inc", "emp_length"]
    return X, y, names


# ---------------------------------------------------------------------------
# build_refinement_band
# ---------------------------------------------------------------------------
def test_band_is_nonempty_and_within_epsilon():
    X, y, names = _within_tier_fixture()
    band = build_refinement_band(
        X, y, feature_names=names, monotonic_cst_map={"dti": +1, "fico_range_low": -1},
        epsilon=0.02, depths=(1, 2, 3), leaf_mins=(25, 50, 100), holdout_frac=0.3, seed=0,
    )
    assert band.n_combos_tried > 0
    assert len(band.members) >= 1
    # Every member is within epsilon of the best holdout AUC.
    for m in band.members:
        assert m.holdout_auc >= band.best_holdout_auc - 0.02 - 1e-9
    # The best member should beat chance on this planted signal.
    assert band.best_holdout_auc > 0.55


def test_band_distinct_members_dedups_identical_trees():
    X, y, names = _within_tier_fixture()
    band = build_refinement_band(
        X, y, feature_names=names, monotonic_cst_map={"dti": +1, "fico_range_low": -1},
        epsilon=0.05, depths=(1, 2, 3), leaf_mins=(25, 50, 100), holdout_frac=0.3, seed=0,
    )
    sigs = [m.tree_signature for m in band.distinct_members]
    assert len(sigs) == len(set(sigs))  # distinct_members really are distinct
    assert len(band.distinct_members) <= len(band.members)


def test_monotonicity_constraint_is_enforced():
    # A dataset where, unconstrained, a tree would split dti the "wrong" way in
    # some leaf (noise); with monotonic_cst={dti:+1} the fitted tree's predicted
    # P(default) must be non-decreasing in dti.
    X, y, names = _within_tier_fixture(seed=3)
    band = build_refinement_band(
        X, y, feature_names=names, monotonic_cst_map={"dti": +1, "fico_range_low": -1},
        epsilon=0.10, depths=(2, 3), leaf_mins=(50,), holdout_frac=0.3, seed=0,
    )
    dti_only = [m for m in band.members if m.feature_subset == ("dti",)]
    assert dti_only, "expected a dti-only member in the band"
    m = dti_only[0]
    model = refit_member(m, X, y, feature_names=names)
    grid = np.linspace(5, 40, 50).reshape(-1, 1)
    preds = model.predict_proba(grid)[:, 1]
    assert np.all(np.diff(preds) >= -1e-9), "P(default) must be non-decreasing in dti"


def test_unconstrained_band_via_empty_map():
    X, y, names = _within_tier_fixture()
    band = build_refinement_band(
        X, y, feature_names=names, monotonic_cst_map={}, epsilon=0.02,
        depths=(1, 2, 3), leaf_mins=(25, 50, 100), holdout_frac=0.3, seed=0,
    )
    assert len(band.members) >= 1


def test_band_degenerate_labels_returns_empty():
    X = np.random.default_rng(0).normal(size=(200, 4))
    y = np.ones(200, dtype=int)
    band = build_refinement_band(
        X, y, feature_names=["a", "b", "c", "d"], monotonic_cst_map={},
        epsilon=0.02, depths=(2,), leaf_mins=(50,), holdout_frac=0.3, seed=0,
    )
    assert band.members == []
    assert band.best_holdout_auc is None


# ---------------------------------------------------------------------------
# used_feature_set
# ---------------------------------------------------------------------------
def test_used_feature_set_reads_split_features():
    X, y, names = _within_tier_fixture()
    band = build_refinement_band(
        X, y, feature_names=names, monotonic_cst_map={"dti": +1},
        epsilon=0.02, depths=(2,), leaf_mins=(50,), holdout_frac=0.3, seed=0,
    )
    # A dti-only member that actually splits must report {"dti"}.
    for m in band.members:
        if m.feature_subset == ("dti",):
            model = refit_member(m, X, y, feature_names=names)
            assert used_feature_set(model, m.feature_subset) <= {"dti"}
            # On this planted signal a depth-2 dti tree does split.
            if model.tree_.node_count > 1:
                assert used_feature_set(model, m.feature_subset) == {"dti"}
            break


# ---------------------------------------------------------------------------
# pairwise_ranking_spearman
# ---------------------------------------------------------------------------
def test_pairwise_spearman_identical_models_is_one():
    rng = np.random.default_rng(0)
    s = rng.random(500)
    med, mn = pairwise_ranking_spearman([s, s, s])
    assert med == pytest.approx(1.0)
    assert mn == pytest.approx(1.0)


def test_pairwise_spearman_disagreeing_models_below_one():
    rng = np.random.default_rng(0)
    a = rng.random(2000)
    b = rng.random(2000)  # independent
    c = a + rng.normal(0, 0.5, 2000)  # correlated with a
    med, mn = pairwise_ranking_spearman([a, b, c])
    assert mn < 0.5            # the a-vs-b pair is near zero
    assert 0.0 < med < 1.0


def test_pairwise_spearman_single_model_returns_one():
    med, mn = pairwise_ranking_spearman([np.array([1.0, 2.0, 3.0])])
    assert med == 1.0 and mn == 1.0
