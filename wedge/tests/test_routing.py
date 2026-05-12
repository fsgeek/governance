"""Tests for wedge/routing.py — the pure metrics behind the within-tier
disagreement-as-routing test (pre-reg:
docs/superpowers/specs/2026-05-12-disagreement-routing-preregistration-note.md).

The orchestration (`scripts/disagreement_routing_test.py`) does the slow data
load and the per-grade band rebuilds; these helpers compute per-borrower
disagreement, the consensus prediction, the four routing metrics, and the
feature-space-outlier diagnostic — unit-tested against planted fixtures with
known answers.
"""
from __future__ import annotations

import numpy as np
import pytest

from wedge.routing import (
    brier_by_tercile,
    calibration_gap_vs_disagreement,
    consensus_scores,
    cross_tier_consistency,
    disagreement_explainer,
    ece,
    feature_space_outlierness,
    grade_routing_verdict,
    member_score_matrix,
    operational_lift,
    partial_dependence_profile,
    per_borrower_disagreement,
    quantile_bin_labels,
    tercile_labels,
    threshold_proximity_correlation,
    univariate_disagreement_correlations,
    within_tercile_member_auc,
)


# ---------------------------------------------------------------------------
# member_score_matrix / per_borrower_disagreement / consensus_scores
# ---------------------------------------------------------------------------
def test_member_score_matrix_stacks_closures():
    X = np.arange(12, dtype=float).reshape(6, 2)
    fns = [lambda Z: Z[:, 0] / 100.0, lambda Z: Z[:, 1] / 100.0]
    M = member_score_matrix(fns, X)
    assert M.shape == (2, 6)
    np.testing.assert_allclose(M[0], X[:, 0] / 100.0)
    np.testing.assert_allclose(M[1], X[:, 1] / 100.0)


def test_member_score_matrix_rejects_wrong_length():
    X = np.zeros((5, 2))
    with pytest.raises(ValueError):
        member_score_matrix([lambda Z: np.zeros(4)], X)


def test_disagreement_and_consensus_known_values():
    # 3 members, 2 borrowers. Borrower 0: scores .1/.2/.3 -> mean .2, std sqrt(2/3)/10.
    # Borrower 1: all .5 -> mean .5, std 0.
    M = np.array([[0.1, 0.5], [0.2, 0.5], [0.3, 0.5]])
    d = per_borrower_disagreement(M)
    p = consensus_scores(M)
    np.testing.assert_allclose(p, [0.2, 0.5])
    np.testing.assert_allclose(d, [np.std([0.1, 0.2, 0.3]), 0.0])
    assert d[1] == 0.0


def test_disagreement_single_member_is_zero():
    M = np.array([[0.1, 0.4, 0.9]])
    np.testing.assert_array_equal(per_borrower_disagreement(M), np.zeros(3))


def test_disagreement_rejects_empty():
    with pytest.raises(ValueError):
        per_borrower_disagreement(np.empty((0, 5)))


# ---------------------------------------------------------------------------
# tercile_labels / quantile_bin_labels
# ---------------------------------------------------------------------------
def test_tercile_labels_equal_sized_on_distinct_values():
    vals = np.array([5, 1, 9, 3, 7, 2, 8, 4, 6], dtype=float)  # n=9 -> 3/3/3
    lab = tercile_labels(vals)
    # The 3 smallest -> 0, next 3 -> 1, largest 3 -> 2.
    assert sorted(vals[lab == 0]) == [1, 2, 3]
    assert sorted(vals[lab == 1]) == [4, 5, 6]
    assert sorted(vals[lab == 2]) == [7, 8, 9]


def test_tercile_labels_handles_ties_and_uneven_n():
    vals = np.array([0, 0, 0, 0, 0, 0, 0], dtype=float)  # all tied, n=7
    lab = tercile_labels(vals)
    counts = np.bincount(lab, minlength=3)
    # n=7 -> low gets the extra: 3,2,2 (rank-based, stable).
    assert counts.tolist() == [3, 2, 2]
    assert set(lab.tolist()) == {0, 1, 2}


def test_tercile_labels_degenerate_small_n():
    np.testing.assert_array_equal(tercile_labels(np.array([4.0, 9.0])), np.array([0, 0]))
    assert tercile_labels(np.array([])).size == 0


def test_quantile_bin_labels_ten_bins():
    vals = np.arange(100, dtype=float)
    bins = quantile_bin_labels(vals, 10)
    assert set(bins.tolist()) == set(range(10))
    assert np.bincount(bins).tolist() == [10] * 10
    # First 10 values in bin 0, last 10 in bin 9.
    assert set(vals[bins == 0]) == set(range(10))
    assert set(vals[bins == 9]) == set(range(90, 100))


def test_quantile_bin_labels_fewer_rows_than_bins():
    bins = quantile_bin_labels(np.array([3.0, 1.0, 2.0]), 10)
    assert sorted(bins.tolist()) == [0, 1, 2]


# ---------------------------------------------------------------------------
# within_tercile_member_auc
# ---------------------------------------------------------------------------
def test_within_tercile_member_auc_orders_predictability():
    rng = np.random.default_rng(0)
    n_per = 1500
    # Low-disagreement tercile: scores strongly track default. High-disagreement:
    # scores are noise. Middle: in between.
    def block(signal):
        y = (rng.random(n_per) < 0.2).astype(int)
        base = rng.random(n_per)
        s = signal * (y + rng.normal(0, 0.3, n_per)) + (1 - signal) * base
        return y, s
    y0, s0 = block(0.9)   # low-d tercile, very predictable
    y1, s1 = block(0.5)
    y2, s2 = block(0.0)   # high-d tercile, pure noise
    y = np.concatenate([y0, y1, y2])
    s = np.concatenate([s0, s1, s2])
    terc = np.concatenate([np.zeros(n_per), np.ones(n_per), np.full(n_per, 2)]).astype(int)
    M = np.vstack([s, s + rng.normal(0, 1e-6, s.size)])  # two near-identical members
    out = within_tercile_member_auc(M, y, terc, n_perm=200, percentile=95, rng_seed=1)
    assert out[0]["mean_member_auc"] > out[1]["mean_member_auc"] > out[2]["mean_member_auc"]
    assert out[0]["mean_member_auc"] > out[0]["null_p95"]            # low above its null
    assert out[2]["mean_member_auc"] <= out[2]["null_p95"] + 0.02    # high ~ at chance
    assert out[0]["n"] == out[1]["n"] == out[2]["n"] == n_per


def test_within_tercile_member_auc_degenerate_tercile():
    M = np.array([[0.1, 0.2, 0.3, 0.4]])
    y = np.array([1, 1, 1, 1])              # all-default everywhere
    terc = np.array([0, 0, 2, 2])
    out = within_tercile_member_auc(M, y, terc, n_perm=20, percentile=95, rng_seed=0)
    assert out[0]["mean_member_auc"] is None and out[0]["null_p95"] is None
    assert out[1]["n"] == 0


# ---------------------------------------------------------------------------
# calibration_gap_vs_disagreement (metric 2)
# ---------------------------------------------------------------------------
def test_calibration_gap_increases_with_disagreement():
    # 10 disagreement bins of 200 rows; consensus pinned at 0.2; the realized
    # default rate climbs with the bin index, so |gap| climbs too -> rho ~ +1.
    n_bin = 200
    d, cons, y = [], [], []
    rng = np.random.default_rng(0)
    for b in range(10):
        d.extend(np.full(n_bin, float(b)) + rng.normal(0, 0.01, n_bin))
        cons.extend(np.full(n_bin, 0.20))
        y.extend((rng.random(n_bin) < (0.20 + 0.03 * b)).astype(int))
    res = calibration_gap_vs_disagreement(np.array(d), np.array(cons), np.array(y), n_bins=10)
    assert res["n_bins_used"] == 10
    assert res["spearman_rho"] > 0.8


def test_calibration_gap_flat_when_no_relationship():
    rng = np.random.default_rng(1)
    n = 4000
    d = rng.random(n)
    cons = np.full(n, 0.15)
    y = (rng.random(n) < 0.15).astype(int)   # default rate independent of d
    res = calibration_gap_vs_disagreement(d, cons, y, n_bins=10)
    assert abs(res["spearman_rho"]) < 0.7    # no strong monotone trend


# ---------------------------------------------------------------------------
# brier_by_tercile (metric 3)
# ---------------------------------------------------------------------------
def test_brier_worse_on_high_disagreement_tercile():
    # Low tercile: consensus = truth -> tiny Brier. High tercile: consensus = 0.5
    # but truth is mostly 0 -> larger Brier. -> high_minus_low > 0.
    y = np.array([0, 0, 0, 1] * 3 + [0, 0, 0, 0] * 3, dtype=int)
    cons = np.array([0.0, 0.0, 0.0, 1.0] * 3 + [0.5, 0.5, 0.5, 0.5] * 3, dtype=float)
    terc = np.array([0] * 12 + [2] * 12, dtype=int)
    res = brier_by_tercile(cons, y, terc)
    assert res["brier_by_tercile"][0] == pytest.approx(0.0)
    assert res["brier_by_tercile"][2] == pytest.approx(0.25)
    assert res["high_minus_low"] == pytest.approx(0.25)


def test_brier_by_tercile_missing_tercile_is_none():
    res = brier_by_tercile(np.array([0.1, 0.2]), np.array([0, 1]), np.array([0, 0]))
    assert res["brier_by_tercile"][1] is None and res["brier_by_tercile"][2] is None
    assert res["high_minus_low"] is None


# ---------------------------------------------------------------------------
# ece / operational_lift (metric 4)
# ---------------------------------------------------------------------------
def test_ece_zero_for_perfectly_calibrated_bins():
    # 10 deciles of consensus 0.05,0.15,...,0.95; realized default == bin mean.
    cons, y = [], []
    rng = np.random.default_rng(0)
    for k in range(10):
        m = 0.05 + 0.1 * k
        cons.extend(np.full(500, m))
        y.extend((rng.random(500) < m).astype(int))
    val = ece(np.array(cons), np.array(y), n_bins=10)
    assert val < 0.02


def test_operational_lift_positive_when_high_tercile_is_miscalibrated():
    rng = np.random.default_rng(0)
    n_per = 2000
    # Low + middle terciles: well calibrated at ~0.15. High tercile: consensus
    # says 0.15 but realized default is 0.45 -> dropping it tightens ECE.
    def block(cons_val, true_rate):
        cons = np.full(n_per, cons_val) + rng.normal(0, 0.02, n_per)
        y = (rng.random(n_per) < true_rate).astype(int)
        return cons, y
    c0, y0 = block(0.15, 0.15)
    c1, y1 = block(0.15, 0.15)
    c2, y2 = block(0.15, 0.45)
    cons = np.concatenate([c0, c1, c2])
    y = np.concatenate([y0, y1, y2])
    terc = np.concatenate([np.zeros(n_per), np.ones(n_per), np.full(n_per, 2)]).astype(int)
    res = operational_lift(cons, y, terc, n_bins=10)
    assert res["n_routed_out"] == n_per
    assert res["ece_all"] > res["ece_auto_kept"]
    assert res["lift"] > 0.0


def test_operational_lift_nonpositive_when_routing_removes_good_cases():
    rng = np.random.default_rng(2)
    n_per = 2000
    # Everyone equally well calibrated; routing out the high-d tercile can't help.
    cons = np.full(3 * n_per, 0.2) + rng.normal(0, 0.02, 3 * n_per)
    y = (rng.random(3 * n_per) < 0.2).astype(int)
    terc = np.concatenate([np.zeros(n_per), np.ones(n_per), np.full(n_per, 2)]).astype(int)
    res = operational_lift(cons, y, terc, n_bins=10)
    assert res["lift"] is not None and res["lift"] < 0.02   # ~0, not a meaningful gain


# ---------------------------------------------------------------------------
# feature_space_outlierness
# ---------------------------------------------------------------------------
def test_outlierness_flags_far_high_tercile():
    rng = np.random.default_rng(0)
    ref = rng.normal(0, 1, size=(2000, 3))
    # eval: low tercile near the reference centroid, high tercile pushed out.
    low = rng.normal(0, 1, size=(300, 3))
    mid = rng.normal(0, 1, size=(300, 3)) + 1.0
    high = rng.normal(0, 1, size=(300, 3)) + 5.0
    Xe = np.vstack([low, mid, high])
    terc = np.array([0] * 300 + [1] * 300 + [2] * 300)
    res = feature_space_outlierness(Xe, ref, terc)
    by = res["mean_mahalanobis_by_tercile"]
    assert by[2] > by[1] > by[0]
    assert res["high_over_low"] > 2.0


def test_outlierness_ratio_near_one_when_all_interior():
    rng = np.random.default_rng(1)
    ref = rng.normal(0, 1, size=(2000, 3))
    Xe = rng.normal(0, 1, size=(900, 3))
    terc = np.array([0] * 300 + [1] * 300 + [2] * 300)
    res = feature_space_outlierness(Xe, ref, terc)
    assert 0.7 < res["high_over_low"] < 1.4


# ---------------------------------------------------------------------------
# grade_routing_verdict
# ---------------------------------------------------------------------------
def test_grade_routing_verdict_all_routing_relevant():
    m1 = {0: {"mean_member_auc": 0.62, "null_p95": 0.55},
          2: {"mean_member_auc": 0.51, "null_p95": 0.55}}
    m2 = {"spearman_rho": 0.7}
    m3 = {"high_minus_low": 0.01}
    m4 = {"lift": 0.002}
    v = grade_routing_verdict(metric1=m1, metric2=m2, metric3=m3, metric4=m4)
    assert v == {"m1_tercile_predictability_routing": True,
                 "m2_calibration_gap_routing": True,
                 "m3_brier_routing": True,
                 "m4_operational_lift_nonneg": True}


def test_grade_routing_verdict_no_signal():
    m1 = {0: {"mean_member_auc": 0.54, "null_p95": 0.55},   # low not even above its null
          2: {"mean_member_auc": 0.555, "null_p95": 0.55}}  # high actually slightly better
    v = grade_routing_verdict(metric1=m1, metric2={"spearman_rho": -0.2},
                              metric3={"high_minus_low": -0.003}, metric4={"lift": -0.001})
    assert v["m1_tercile_predictability_routing"] is False
    assert v["m2_calibration_gap_routing"] is False
    assert v["m3_brier_routing"] is False
    assert v["m4_operational_lift_nonneg"] is False


def test_grade_routing_verdict_degenerate_inputs_are_none():
    m1 = {0: {"mean_member_auc": None, "null_p95": None}, 2: {"mean_member_auc": None, "null_p95": None}}
    v = grade_routing_verdict(metric1=m1, metric2={"spearman_rho": None},
                              metric3={"high_minus_low": None}, metric4={"lift": None})
    assert all(x is None for x in v.values())


# ---------------------------------------------------------------------------
# disagreement_explainer
# ---------------------------------------------------------------------------
def test_explainer_recovers_the_driving_feature():
    rng = np.random.default_rng(0)
    n = 2000
    f0 = rng.normal(0, 1, n)
    f1 = rng.uniform(0, 100, n)          # the driver
    f2 = rng.normal(50, 5, n)
    X = np.column_stack([f0, f1, f2])
    names = ["fico", "dti", "annual_inc"]
    d = 0.01 + 0.0008 * np.abs(f1 - 50) + rng.normal(0, 0.0005, n)   # U-shaped in dti
    res = disagreement_explainer(d, X, names, max_depth=3, min_samples_leaf=50, n_splits=5, seed=0)
    assert res["root_feature"] == "dti"
    assert res["top_importances"][0][0] == "dti"
    assert res["cv_r2"] > 0.3                                         # well-explained
    assert res["n"] == n and res["n_features"] == 3


def test_explainer_low_r2_when_d_is_noise():
    rng = np.random.default_rng(1)
    n = 1500
    X = rng.normal(0, 1, size=(n, 4))
    d = 0.02 + rng.normal(0, 0.003, n)   # d unrelated to X
    res = disagreement_explainer(d, X, ["a", "b", "c", "d"], n_splits=5, seed=0)
    assert res["cv_r2"] is not None and res["cv_r2"] < 0.1


def test_explainer_degenerate_small_n_or_constant_d():
    X = np.arange(20, dtype=float).reshape(10, 2)
    assert disagreement_explainer(np.linspace(0, 1, 10), X, ["a", "b"], n_splits=5)["cv_r2"] is None  # n too small
    Xb = np.random.default_rng(0).normal(0, 1, size=(200, 2))
    assert disagreement_explainer(np.full(200, 0.03), Xb, ["a", "b"])["cv_r2"] is None                # constant d


def test_explainer_shape_mismatch_raises():
    with pytest.raises(ValueError):
        disagreement_explainer(np.zeros(10), np.zeros((10, 3)), ["a", "b"])


# ---------------------------------------------------------------------------
# partial_dependence_profile
# ---------------------------------------------------------------------------
def test_pd_profile_detects_u_shape_tails():
    rng = np.random.default_rng(0)
    f = rng.uniform(0, 100, 5000)
    d = 0.01 + 0.0010 * np.abs(f - 50) + rng.normal(0, 0.0002, 5000)   # U in f
    prof = partial_dependence_profile(d, f, n_deciles=10)
    assert prof["shape"] == "tails"
    assert prof["tail_ratio"] is not None and prof["tail_ratio"] >= 1.5
    assert prof["argmax_bucket"] in (0, 9)


def test_pd_profile_detects_monotone():
    rng = np.random.default_rng(1)
    f = rng.uniform(0, 100, 5000)
    d = 0.01 + 0.0003 * f + rng.normal(0, 0.0002, 5000)               # increasing in f
    prof = partial_dependence_profile(d, f, n_deciles=10)
    assert prof["shape"] == "monotone"


def test_pd_profile_detects_interior_threshold_bump():
    rng = np.random.default_rng(2)
    f = rng.uniform(0, 100, 8000)
    # A bump centred at f=50 (deciles 4-5) and low elsewhere -> interior argmax.
    d = 0.01 + 0.02 * np.exp(-((f - 50) ** 2) / (2 * 6.0 ** 2)) + rng.normal(0, 0.0003, 8000)
    prof = partial_dependence_profile(d, f, n_deciles=10)
    assert prof["shape"] == "threshold"
    assert prof["argmax_bucket"] not in (0, 9)


def test_pd_profile_flat_when_d_constant_ish():
    rng = np.random.default_rng(3)
    f = rng.uniform(0, 100, 4000)
    d = 0.02 + rng.normal(0, 0.0002, 4000)   # essentially no dependence
    assert partial_dependence_profile(d, f, n_deciles=10)["shape"] == "flat"


# ---------------------------------------------------------------------------
# univariate_disagreement_correlations
# ---------------------------------------------------------------------------
def test_univariate_correlations_pick_up_the_monotone_driver():
    rng = np.random.default_rng(0)
    n = 3000
    f0 = rng.uniform(0, 100, n)
    f1 = rng.normal(0, 1, n)
    X = np.column_stack([f0, f1])
    d = 0.01 + 0.0004 * f0 + rng.normal(0, 0.0003, n)
    res = univariate_disagreement_correlations(d, X, ["dti", "noise"], n_deciles=10)
    assert res["dti"]["spearman_rho"] > 0.5
    assert abs(res["noise"]["spearman_rho"]) < 0.1
    assert res["dti"]["mean_d_top_decile"] > res["dti"]["mean_d_bottom_decile"]


def test_univariate_correlations_constant_feature_is_none():
    X = np.column_stack([np.full(100, 5.0), np.arange(100, dtype=float)])
    d = np.arange(100, dtype=float) / 100.0
    res = univariate_disagreement_correlations(d, X, ["const", "ramp"], n_deciles=5)
    assert res["const"]["spearman_rho"] is None
    assert res["ramp"]["spearman_rho"] is not None


# ---------------------------------------------------------------------------
# threshold_proximity_correlation
# ---------------------------------------------------------------------------
def test_threshold_proximity_picks_up_distance_to_ceiling():
    rng = np.random.default_rng(0)
    n = 4000
    dti = rng.uniform(10, 40, n)         # interior tier, below the 43 ceiling
    fico = rng.uniform(660, 720, n)
    # d grows as dti approaches 43 (proximity small -> d large): negative rho on |dti-43|.
    d = 0.01 + 0.0015 * (1.0 / (1.0 + np.abs(dti - 43.0))) + rng.normal(0, 0.00001, n)
    res = threshold_proximity_correlation(d, dti, fico, dti_ceiling=43.0, fico_floor=620.0)
    assert res["dti_proximity"]["spearman_rho"] < -0.3   # closer to 43 -> higher d
    assert res["max_abs_rho"] is not None and res["max_abs_rho"] > 0.3


def test_threshold_proximity_missing_feature_is_none():
    d = np.arange(50, dtype=float) / 50.0
    res = threshold_proximity_correlation(d, None, np.linspace(600, 700, 50))
    assert res["dti_proximity"]["spearman_rho"] is None
    assert res["fico_proximity"]["spearman_rho"] is not None


# ---------------------------------------------------------------------------
# cross_tier_consistency
# ---------------------------------------------------------------------------
def test_cross_tier_consistency_majority():
    tops = {"A5": "dti", "B1": "dti", "C1": "dti", "C5": "annual_inc", "D4": "dti"}
    shapes = {"A5": "tails", "B1": "tails", "C1": "monotone", "C5": "tails", "D4": "threshold"}
    res = cross_tier_consistency(tops, shapes)
    assert res["dominant_feature"]["modal"] == "dti" and res["dominant_feature"]["modal_count"] == 4
    assert res["dominant_feature"]["majority"] is True
    # tails 3 of 5 -> 3 > 2.5 -> majority True
    assert res["pd_shape"]["modal"] == "tails" and res["pd_shape"]["majority"] is True


def test_cross_tier_consistency_no_majority():
    tops = {"A": "dti", "B": "annual_inc", "C": "fico", "D": "emp_length", "E": "dti"}
    res = cross_tier_consistency(tops, {})
    assert res["dominant_feature"]["majority"] is False  # modal "dti" is only 2 of 5
    assert res["pd_shape"]["n"] == 0
