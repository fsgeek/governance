"""Tests for the frozen record-sufficiency metrics.

These guard the pre-registered primary (top-k Jaccard k=5 >= 0.90, sufficiency
at 95%) against silent drift. If a test here needs changing, the pre-registration
is being edited -- which is only legitimate before data, with the OTS record
showing it.
"""

import numpy as np
import pytest

from metrics import (
    PRIMARY_K,
    PRIMARY_THRESHOLD,
    SUFFICIENCY_FRACTION,
    cosine,
    full_report,
    l2,
    rbo,
    reproduces,
    topk_jaccard,
)


def test_frozen_constants():
    """The pre-registered numbers. Changing these post-data is the failure mode."""
    assert PRIMARY_K == 5
    assert PRIMARY_THRESHOLD == 0.90
    assert SUFFICIENCY_FRACTION == 0.95


def test_identical_attributions_reproduce_perfectly():
    a = np.array([[3.0, -2.0, 1.0, 0.5, -0.1, 0.01, 0.0]])
    assert topk_jaccard(a, a.copy())[0] == 1.0
    assert reproduces(a, a.copy())["SUFFICIENT"] is True


def test_sign_ignored_magnitude_ranks():
    """Attribution rank is by |value| -- a sign flip must not change the top-k."""
    a = np.array([[3.0, -2.0, 1.0, 0.5, -0.1, 0.01, 0.0]])
    b = -a
    assert topk_jaccard(a, b)[0] == 1.0


def test_disjoint_topk_scores_zero():
    n = 10
    a = np.zeros((1, n))
    b = np.zeros((1, n))
    a[0, :5] = [5, 4, 3, 2, 1]
    b[0, 5:] = [5, 4, 3, 2, 1]
    assert topk_jaccard(a, b)[0] == 0.0


def test_reordering_within_topk_does_not_hurt_jaccard():
    """Jaccard is set-based: permuting inside the top-k is invisible to it.

    This is a known blind spot of the primary and is why RBO is reported.
    """
    a = np.array([[5.0, 4.0, 3.0, 2.0, 1.0, 0.0, 0.0]])
    b = np.array([[1.0, 2.0, 3.0, 4.0, 5.0, 0.0, 0.0]])
    assert topk_jaccard(a, b)[0] == 1.0
    assert rbo(a, b)[0] < 1.0  # RBO does see it


def test_one_swap_at_the_boundary():
    """Swapping the 5th and 6th features: 4 of 5 shared -> 4/6 Jaccard."""
    a = np.zeros((1, 8))
    b = np.zeros((1, 8))
    a[0, :6] = [9, 8, 7, 6, 5, 1]
    b[0, :6] = [9, 8, 7, 6, 1, 5]
    assert topk_jaccard(a, b)[0] == pytest.approx(4 / 6)


def test_deterministic_tie_breaking():
    """All-equal attributions must still give a stable, reproducible top-k."""
    a = np.ones((1, 10))
    b = np.ones((1, 10))
    assert topk_jaccard(a, b)[0] == 1.0


def test_sufficiency_fraction_gate():
    """94% reproducing fails the 95% gate; 96% passes. The gate is sharp."""
    n_feat = 10
    good = np.tile(np.arange(n_feat, 0, -1, dtype=float), (100, 1))

    bad_rows = 6
    recomputed = good.copy()
    recomputed[:bad_rows] = np.arange(1, n_feat + 1, dtype=float)  # reversed
    assert reproduces(good, recomputed)["SUFFICIENT"] is False

    recomputed = good.copy()
    recomputed[:4] = np.arange(1, n_feat + 1, dtype=float)
    assert reproduces(good, recomputed)["SUFFICIENT"] is True


def test_l2_can_disagree_with_rank_verdict():
    """The pre-reg's P4 in miniature.

    Two tiny magnitude nudges reorder the top-k while leaving L2 minuscule.
    An L2 criterion would call this reproduced; the frozen rank primary does not.
    """
    n = 100
    a = np.zeros((n, 8))
    b = np.zeros((n, 8))
    base = np.array([1.00, 0.99, 0.98, 0.97, 0.96, 0.95, 0.10, 0.05])
    a[:] = base
    swapped = base.copy()
    swapped[4], swapped[5] = base[5], base[4]
    b[:] = swapped

    assert l2(a, b).mean() < 0.02          # L2 says "identical"
    assert cosine(a, b).mean() > 0.999     # cosine agrees
    assert reproduces(a, b)["SUFFICIENT"] is False  # rank primary does not


def test_full_report_namespaces_secondaries():
    a = np.random.RandomState(0).randn(20, 12)
    b = a + np.random.RandomState(1).randn(20, 12) * 0.01
    rep = full_report(a, b)
    assert "primary" in rep
    assert "SUFFICIENT" in rep["primary"]
    for key in ("secondary_rbo", "secondary_l2", "secondary_cosine"):
        assert key in rep
        assert "SUFFICIENT" not in rep[key], "a secondary must never carry a verdict"
    assert "sensitivity_NON_GATING" in rep


def test_shape_mismatch_raises():
    with pytest.raises(ValueError):
        topk_jaccard(np.zeros((3, 5)), np.zeros((3, 6)))
    with pytest.raises(ValueError):
        topk_jaccard(np.zeros(5), np.zeros(5))


def test_rbo_bounds():
    rs = np.random.RandomState(7)
    a = rs.randn(15, 10)
    v_same = rbo(a, a.copy())
    assert np.all(v_same > 0.99)
    b = rs.randn(15, 10)
    v_diff = rbo(a, b)
    assert np.all((v_diff >= 0.0) & (v_diff <= 1.0))


def test_rbo_identical_is_one_at_every_feature_count():
    """Regression guard: RBO must not depend on how many features exist.

    The raw truncated RBO sum saturates at 1 - p**n, so identical rankings score
    0.651 at n=10 and 0.878 at n=20 -- a metric whose ceiling moves with feature
    count silently corrupts any cross-substrate comparison. The extrapolated
    form fixes this. Caught by a failing test before any data was touched.
    """
    rs = np.random.RandomState(11)
    for n_feat in (5, 10, 20, 40):
        a = rs.randn(6, n_feat)
        assert np.allclose(rbo(a, a.copy()), 1.0), f"n_feat={n_feat}"


def test_rbo_is_topweighted():
    """Disagreement at rank 1 must cost more than the same swap far down."""
    n = 20
    base = np.arange(n, 0, -1, dtype=float).reshape(1, n)

    top = base.copy()
    top[0, 0], top[0, 1] = base[0, 1], base[0, 0]

    deep = base.copy()
    deep[0, 15], deep[0, 16] = base[0, 16], base[0, 15]

    assert rbo(base, top)[0] < rbo(base, deep)[0]
