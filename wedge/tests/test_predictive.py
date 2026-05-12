"""Tests for wedge/predictive.py — the pure metrics behind the within-tier
forward-predictive test (pre-reg: docs/superpowers/specs/2026-05-12-within-tier-predictive-test-preregistration-note.md).

The orchestration (`scripts/within_tier_predictive_test.py`) does the slow data
load, the per-grade logistic fits, and the freeze-and-evaluate; these helpers do
the shuffle-null AUC and the hit/miss classification, unit-tested against
fixtures.
"""
from __future__ import annotations

import numpy as np
import pytest

from wedge.predictive import classify_hit, shuffle_null_auc


# ---------------------------------------------------------------------------
# shuffle_null_auc
# ---------------------------------------------------------------------------
def test_shuffle_null_auc_centers_near_half():
    rng = np.random.default_rng(0)
    n = 4000
    y = (rng.random(n) < 0.15).astype(int)
    scores = rng.random(n)  # scores unrelated to y
    # The null distribution of AUC under label permutation is centered at 0.5;
    # its 50th percentile should be ~0.5 and its 95th a bit above.
    p50 = shuffle_null_auc(y, scores, n_perm=400, percentile=50, rng_seed=1)
    p95 = shuffle_null_auc(y, scores, n_perm=400, percentile=95, rng_seed=1)
    assert abs(p50 - 0.5) < 0.02
    assert 0.5 < p95 < 0.6  # one-sided tail, modest for n=4000


def test_shuffle_null_auc_wider_band_for_small_grade():
    rng = np.random.default_rng(0)
    big_y = (rng.random(8000) < 0.15).astype(int)
    big_s = rng.random(8000)
    small_y = (rng.random(300) < 0.15).astype(int)
    small_s = rng.random(300)
    p95_big = shuffle_null_auc(big_y, big_s, n_perm=400, percentile=95, rng_seed=2)
    p95_small = shuffle_null_auc(small_y, small_s, n_perm=400, percentile=95, rng_seed=2)
    # Smaller grade -> wider null band -> higher 95th percentile.
    assert p95_small > p95_big


def test_shuffle_null_auc_deterministic_with_seed():
    rng = np.random.default_rng(3)
    y = (rng.random(1000) < 0.2).astype(int)
    s = rng.random(1000)
    a = shuffle_null_auc(y, s, n_perm=200, percentile=95, rng_seed=42)
    b = shuffle_null_auc(y, s, n_perm=200, percentile=95, rng_seed=42)
    assert a == b


def test_shuffle_null_auc_degenerate_labels_returns_half():
    # All-one or all-zero labels: AUC undefined; helper should return 0.5.
    y = np.ones(100, dtype=int)
    s = np.random.default_rng(0).random(100)
    assert shuffle_null_auc(y, s, n_perm=50, percentile=95, rng_seed=0) == 0.5


# ---------------------------------------------------------------------------
# classify_hit
# ---------------------------------------------------------------------------
def test_classify_hit_above_null_and_floor():
    assert classify_hit(oos_auc=0.60, null_p95=0.54, floor=0.52) == "HIT"


def test_classify_hit_below_null_is_miss():
    assert classify_hit(oos_auc=0.53, null_p95=0.55, floor=0.52) == "MISS"


def test_classify_hit_above_null_below_floor_is_near_hit():
    # Clears the percentile bar (a tiny grade with a tight... no, a huge grade
    # with a tiny effect) but below the practical floor.
    assert classify_hit(oos_auc=0.514, null_p95=0.510, floor=0.52) == "NEAR-HIT"


def test_classify_hit_below_chance_is_miss():
    assert classify_hit(oos_auc=0.47, null_p95=0.55, floor=0.52) == "MISS"


def test_classify_hit_exactly_at_floor_is_hit():
    assert classify_hit(oos_auc=0.52, null_p95=0.515, floor=0.52) == "HIT"
