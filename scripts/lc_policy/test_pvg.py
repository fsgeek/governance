"""Constructed violators for step 2 (pre-reg §4). No real data is read."""
import math
import sys
from pathlib import Path

import numpy as np
import pytest
from sklearn.tree import DecisionTreeClassifier

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pvg as V


def test_written_rule():
    s = np.array([655, 660, 715, 715, 720, 720, 720])
    d = np.array([10, 10, 24.9, 25, 29.9, 30, 10])
    assert V.written_rule_declines(s, d).tolist() == [True, False, False, True, False, True, False]
    # tolerance moves the DTI boundary inward only
    assert V.written_rule_declines(np.array([700.0]), np.array([25.3]), 0.5).tolist() == [False]


def test_straddle32_brackets_unrepresentable_thresholds():
    for t in (25.000001, 0.1, 657.5, 1e-7, 24.995):
        lo, hi = V.straddle32(t)
        # compare in float64, as sklearn does (float32 X promoted to double against a double threshold)
        assert float(np.float32(lo)) <= t < float(np.float32(hi))
        assert float(np.float32(lo)) == lo and float(np.float32(hi)) == hi


def test_straddle32_lands_on_both_sides_of_a_real_sklearn_split():
    rng = np.random.default_rng(0)
    x = rng.uniform(0, 50, 5000)
    y = (x < 24.995).astype(int)
    t = DecisionTreeClassifier(max_depth=1).fit(x.reshape(-1, 1), y)
    thr = float(t.tree_.threshold[0])
    lo, hi = V.straddle32(thr)
    leaves = t.apply(np.array([[lo], [hi]], dtype=np.float32))
    assert leaves[0] != leaves[1]


def test_float64_nextafter_would_have_failed_somewhere():
    """Regression for the bug class: some float64 nextafter(t, inf) values round to float32 <= t."""
    bad = [t for t in np.linspace(24.9, 25.1, 2001) if float(np.float32(np.nextafter(t, np.inf))) <= t]
    assert bad, "if this ever passes vacuously, the straddle32 test above is the guard"


def fit_member(X, y, cols, depth=3, leaf=50):
    t = DecisionTreeClassifier(max_depth=depth, min_samples_leaf=leaf, random_state=0).fit(X[:, cols], y)
    m = V.Member(t, cols, 0.5, 0.0)
    return m


def synth(n, rule, seed=0):
    rng = np.random.default_rng(seed)
    X = np.column_stack([V.bucket5(rng.uniform(600, 800, n)), rng.uniform(0, 40, n),
                         rng.uniform(1000, 35000, n), rng.integers(-1, 11, n).astype(float)])
    y = (~rule(X[:, 0], X[:, 1])).astype(int)
    return X, y


def test_monotone_tree_passes_and_reversed_tree_fails():
    X, y = synth(20000, V.written_rule_declines)
    good = fit_member(X, y, [0, 1])
    assert not V.violates_monotone(good, X[:500])
    bad = fit_member(X, 1 - y, [0, 1])            # accepts the low scores and high DTIs: reversed
    assert V.violates_monotone(bad, X[:500])


def test_policy_respecting_tree_passes_and_interaction_ignoring_tree_fails():
    X, y = synth(40000, V.written_rule_declines)
    grid = np.vstack([X[:500], V.policy_grid(18000.0, 5.0)])
    follows = fit_member(X, y, [0, 1], depth=4, leaf=50)
    assert not V.violates_policy(follows, grid)
    cap30 = lambda s, d, tol=0.0: (s < 660) | (d >= 30 + tol)      # lender ignores the 720 conditional
    X2, y2 = synth(40000, cap30)
    ignores = fit_member(X2, y2, [0, 1], depth=4, leaf=50)
    assert V.violates_policy(ignores, grid)
    assert not V.violates_policy(ignores, grid, V.floors_declines)   # it does respect the floors alone


def test_tree_not_using_score_violates_floor():
    X, y = synth(20000, V.written_rule_declines)
    no_score = fit_member(X, y, [1, 2])
    assert V.violates_policy(no_score, np.vstack([X[:500], V.policy_grid(18000.0, 5.0)]))


def test_seed_verdict_branches():
    base = {"void": False, "n_P": 300, "retention": 0.95, "jaccard": 0.95, "dpflip": 0.001}
    assert V.seed_verdict(base) == "KILL"
    assert V.seed_verdict({**base, "retention": 0.4}) == "POLICY_MATTERS"
    assert V.seed_verdict({**base, "jaccard": 0.6}) == "POLICY_MATTERS"
    assert V.seed_verdict({**base, "n_P": 0, "jaccard": float("nan")}) == "POLICY_MATTERS"
    assert V.seed_verdict({**base, "retention": 0.8}) == "INCONCLUSIVE"
    assert V.seed_verdict({**base, "dpflip": 0.02}) == "INCONCLUSIVE"
    assert V.seed_verdict({**base, "void": True}) == "VOID"


def test_overall_verdict_needs_4_of_5_and_at_most_one_void():
    assert V.overall_verdict(["KILL"] * 4 + ["VOID"]) == "KILL"
    assert V.overall_verdict(["KILL"] * 3 + ["VOID"] * 2) == "INCONCLUSIVE"
    assert V.overall_verdict(["KILL"] * 3 + ["POLICY_MATTERS"] * 2) == "INCONCLUSIVE"
    assert V.overall_verdict(["POLICY_MATTERS"] * 5) == "POLICY_MATTERS"


def test_emp_and_bucket():
    assert [V.emp_code(x) for x in ["< 1 year", "1 year", "5 years", "10+ years", "n/a", None]] == [0, 1, 5, 10, -1, -1]
    assert V.bucket5(np.array([657, 660, 664.9])).tolist() == [655, 660, 660]


@pytest.mark.parametrize("rule,expect", [("follows", "KILL"), ("ignores_interaction", "POLICY_MATTERS")])
def test_end_to_end_constructed_lenders(rule, expect):
    """A lender that follows the written rule on a well-populated grid should give KILL (trees learn it);
    one that ignores the 720 conditional should give POLICY_MATTERS. Small sizes, so leaves are scaled down."""
    r = V.written_rule_declines if rule == "follows" else (lambda s, d, tol=0.0: (s < 660) | (d >= 30 + tol))
    X, y = synth(60000, r, seed=3)
    old = (V.LEAVES, V.MIN_G)
    V.LEAVES, V.MIN_G = (100, 300), 10
    try:
        res = V.run(X, y, seeds=V.SEEDS, n_trees=300, eps_list=[0.01])
    finally:
        V.LEAVES, V.MIN_G = old
    assert res["verdict"] == expect, res["per_seed_primary"]
