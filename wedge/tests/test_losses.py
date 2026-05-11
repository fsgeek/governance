"""Tests for wedge.losses — cost-asymmetric loss functions per spec §3.2 / §3.3.

L_T (grant_emphasis_loss): weights missed grants heavier than missed denies.
L_F (deny_emphasis_loss): weights missed denies heavier than missed grants.
L_T' / L_F': surprise-weighted variants for retrospective set revision (§5).

Convention: y=1 ⇔ grant (paid / originated), y=0 ⇔ deny (charged_off / denied),
per the grant-as-positive label-polarity (spec §2.7 OD-9a / OD-13).
"""

from __future__ import annotations

import numpy as np
import pytest

from wedge.losses import (
    deny_emphasis_loss,
    deny_emphasis_loss_weighted,
    grant_emphasis_loss,
    grant_emphasis_loss_weighted,
)


# ---------------------------------------------------------------------------
# Unweighted: L_T and L_F
# ---------------------------------------------------------------------------


def test_grant_emphasis_loss_weights_missed_grants_by_w_T():
    """L_T(y, ŷ) = w_T · |missed grants| + |missed denies|."""
    y = np.array([1, 0, 1, 0])
    y_hat = np.array([0, 1, 1, 0])  # 1 missed grant (idx 0), 1 missed deny (idx 1)
    loss = grant_emphasis_loss(y, y_hat, w_T=2.0)
    expected = 2.0 * 1 + 1.0 * 1
    assert loss == pytest.approx(expected)


def test_deny_emphasis_loss_weights_missed_denies_by_w_F():
    """L_F(y, ŷ) = |missed grants| + w_F · |missed denies|."""
    y = np.array([1, 0, 1, 0])
    y_hat = np.array([0, 1, 1, 0])
    loss = deny_emphasis_loss(y, y_hat, w_F=2.0)
    expected = 1.0 * 1 + 2.0 * 1
    assert loss == pytest.approx(expected)


def test_grant_and_deny_emphasis_equal_when_weight_is_one():
    """w_T = w_F = 1 reduces both losses to symmetric 0/1 loss."""
    y = np.array([1, 0, 1, 0, 1])
    y_hat = np.array([0, 1, 1, 0, 0])  # 2 missed grants, 1 missed deny -> total 3
    assert grant_emphasis_loss(y, y_hat, w_T=1.0) == pytest.approx(3.0)
    assert deny_emphasis_loss(y, y_hat, w_F=1.0) == pytest.approx(3.0)


def test_perfect_prediction_gives_zero_loss():
    y = np.array([1, 0, 1, 0])
    assert grant_emphasis_loss(y, y, w_T=2.0) == 0.0
    assert deny_emphasis_loss(y, y, w_F=2.0) == 0.0


def test_grant_emphasis_loss_rejects_mismatched_shapes():
    with pytest.raises(ValueError, match="shape"):
        grant_emphasis_loss(np.array([1, 0]), np.array([1, 0, 1]), w_T=1.5)


def test_grant_emphasis_loss_rejects_non_binary_input():
    with pytest.raises(ValueError, match="binary"):
        grant_emphasis_loss(np.array([1, 0, 2]), np.array([1, 0, 1]), w_T=1.5)


# ---------------------------------------------------------------------------
# Weighted: L_T' and L_F' for surprise-weighted set revision (spec §5)
# ---------------------------------------------------------------------------


def test_grant_emphasis_loss_weighted_applies_per_sample_weights():
    """L_T'(y, ŷ; w) = sum over i of w_i · (w_T · 1[miss grant] + 1[miss deny])."""
    y = np.array([1, 0, 1, 0])
    y_hat = np.array([0, 1, 1, 0])
    sample_weights = np.array([2.0, 0.5, 1.0, 1.0])
    # Sample-by-sample: idx 0 misses grant (w_T*w_i = 2.0*2.0 = 4.0);
    #                   idx 1 misses deny  (1.0*w_i = 0.5).
    loss = grant_emphasis_loss_weighted(y, y_hat, w_T=2.0, sample_weights=sample_weights)
    assert loss == pytest.approx(4.0 + 0.5)


def test_deny_emphasis_loss_weighted_applies_per_sample_weights():
    y = np.array([1, 0, 1, 0])
    y_hat = np.array([0, 1, 1, 0])
    sample_weights = np.array([2.0, 0.5, 1.0, 1.0])
    # idx 0 misses grant (1.0*w_i = 2.0); idx 1 misses deny (w_F*w_i = 2.0*0.5 = 1.0).
    loss = deny_emphasis_loss_weighted(y, y_hat, w_F=2.0, sample_weights=sample_weights)
    assert loss == pytest.approx(2.0 + 1.0)


def test_weighted_loss_reduces_to_unweighted_when_weights_are_one():
    y = np.array([1, 0, 1, 0])
    y_hat = np.array([0, 1, 1, 0])
    ones = np.ones_like(y, dtype=float)
    assert grant_emphasis_loss_weighted(
        y, y_hat, w_T=1.5, sample_weights=ones
    ) == pytest.approx(grant_emphasis_loss(y, y_hat, w_T=1.5))
    assert deny_emphasis_loss_weighted(
        y, y_hat, w_F=1.5, sample_weights=ones
    ) == pytest.approx(deny_emphasis_loss(y, y_hat, w_F=1.5))


def test_weighted_loss_rejects_mismatched_weight_shape():
    y = np.array([1, 0, 1, 0])
    y_hat = np.array([0, 1, 1, 0])
    with pytest.raises(ValueError, match="shape"):
        grant_emphasis_loss_weighted(y, y_hat, w_T=1.5, sample_weights=np.array([1.0, 1.0]))
