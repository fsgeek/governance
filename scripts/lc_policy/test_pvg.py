"""Constructed violators for step 2 r2 (pre-reg §4). No real data is read."""
import math
import sys
from pathlib import Path

import numpy as np
import pytest
from sklearn.tree import DecisionTreeClassifier

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pvg as V


def realistic(n, rule, seed=0, p_other=0.35, sparse_cell=True):
    """About 16% accepts: eligible applicants are accepted with probability p_other (other-reason declines).
    Score ~ N(680, 45), so the FICO >= 720 x DTI 25-30 cell is sparse."""
    rng = np.random.default_rng(seed)
    score = V.bucket5(np.clip(rng.normal(680, 45, n), 560, 850))
    dti = np.clip(rng.gamma(4, 4.5, n), 0, 60) if sparse_cell else rng.uniform(0, 40, n)
    amount = rng.uniform(1000, 35000, n)
    emp = rng.integers(-1, 11, n).astype(float)
    X = np.column_stack([score, dti, amount, emp])
    eligible = ~rule(score, dti)
    y = (eligible & (rng.random(n) < p_other)).astype(int)
    return X, y


def cap30(s, d, tol_dti=0.0, tol_score=0.0):
    """A lender that ignores the 720 conditional: FICO >= 660 and DTI < 30 for everyone."""
    return (np.asarray(s) < 660) | (np.asarray(d) >= 30 + tol_dti)


def fit(X, y, cols=(0, 1), depth=4, leaf=200):
    cols = list(cols)
    t = DecisionTreeClassifier(max_depth=depth, min_samples_leaf=leaf,
                               monotonic_cst=[V.MONO[c] for c in cols], random_state=0).fit(X[:, cols], y)
    return V.Member(t, cols, depth, leaf)


def test_rule_and_tolerances():
    s = np.array([655, 660, 710, 710, 715, 715, 720, 720, 725])
    d = np.array([10, 10, 24.9, 25.0, 25.2, 30.0, 29.9, 30.0, 30.6])
    assert V.written_rule_declines(s, d).tolist() == [True, False, False, True, True, True, False, True, True]
    tol = V.written_rule_declines(s, d, 0.5, 5.0).tolist()
    # 710 @ 25.0 is inside the DTI tolerance; 715 @ 25.2 is inside the score tolerance; 715 @ 30.0 too (needs 30.5)
    assert tol == [True, False, False, False, False, False, False, False, True]


def test_true_reasons():
    assert V.true_reasons(650, 10) == {"score"}
    assert V.true_reasons(700, 27) == {"dti", "score"}
    assert V.true_reasons(750, 33) == {"dti"}
    assert V.true_reasons(700, 33) == {"dti"}


def test_leaf_boxes_match_sklearn_apply():
    X, y = realistic(30000, V.written_rule_declines)
    m = fit(X, y, cols=(0, 1, 2))
    boxes = V.leaf_boxes(m)
    Z = X[:3000]
    member = np.array([[V.in_box(Z, b)[i] for b, _ in boxes] for i in range(len(Z))])
    assert (member.sum(axis=1) == 1).all()                                  # each row in exactly one leaf
    leaf_p = np.array([p for _, p in boxes])[member.argmax(axis=1)]
    assert np.allclose(leaf_p, V.p_accept(m, Z))                            # and it's sklearn's leaf


def test_follower_respects_and_cap30_lender_violates():
    Xf, yf = realistic(120000, V.written_rule_declines, seed=1, sparse_cell=False)
    Xc, yc = realistic(120000, cap30, seed=1, sparse_cell=False)
    follows, ignores = fit(Xf, yf, leaf=300), fit(Xc, yc, leaf=300)
    assert not V.violates(follows, Xf[:40000])
    assert V.violates(ignores, Xc[:40000])
    assert not V.violates(ignores, Xc[:40000], V.floors_declines)       # it respects the floors alone


def test_violation_only_at_a_non_median_amount_is_caught():
    """Adversary finding 6: a lender that ignores the 720 conditional only for large loans. A median-amount grid
    would miss it; the leaf-box check must not."""
    rng = np.random.default_rng(4)
    n = 150000
    X = np.column_stack([V.bucket5(rng.uniform(640, 800, n)), rng.uniform(0, 40, n), rng.uniform(1000, 35000, n),
                         np.zeros(n)])
    big = X[:, 2] > 30000
    declined = np.where(big, cap30(X[:, 0], X[:, 1]), V.written_rule_declines(X[:, 0], X[:, 1]))
    y = (~declined & (rng.random(n) < 0.5)).astype(int)
    m = fit(X, y, cols=(0, 1, 2), depth=4, leaf=300)
    assert V.violates(m, X[:50000])


def test_violation_needs_test_mass():
    X, y = realistic(60000, cap30, seed=2, sparse_cell=False)
    m = fit(X, y, leaf=300)
    mass = V.violation_mass(m, X[:20000])
    assert mass >= V.MIN_MASS
    assert V.violation_mass(m, X[:3][X[:3, 1] < 20]) < V.MIN_MASS          # no applicants in the region, no violation


def test_monotone_constraint_holds_on_constructed_reversal():
    """G is trained monotone: even on labels that reward low scores, P(accept) can't fall as score rises."""
    X, y = realistic(40000, V.written_rule_declines, seed=5)
    m = fit(X, 1 - y)
    grid = np.column_stack([np.arange(600, 820, 5.0), np.full(44, 15.0), np.full(44, 10000.0), np.zeros(44)])
    p = V.p_accept(m, grid)
    assert np.all(np.diff(p) >= -1e-12)


def test_first_reason_and_fidelity():
    X, y = realistic(120000, V.written_rule_declines, seed=6, sparse_cell=False)
    m = fit(X, y, leaf=300)
    assert V.first_reason(m, np.array([750.0, 35.0, 10000.0, 3.0])) == "dti"
    assert V.first_reason(m, np.array([640.0, 10.0, 10000.0, 3.0])) == "score"
    fid = V.reason_fidelity([m], X[:20000], n_app=100)
    assert fid["pairs"] > 0 and fid["outside_share"] < 0.2


def test_straddle32():
    for t in (25.000001, 0.1, 657.5, 24.995):
        lo, hi = V.straddle32(t)
        assert float(np.float32(lo)) <= t < float(np.float32(hi))


def test_verdicts():
    b = {"void": False, "retention": 0.95}
    assert V.seed_verdict(b) == "KILL"
    assert V.seed_verdict({**b, "retention": 0.4}) == "POLICY_MATTERS"
    assert V.seed_verdict({**b, "retention": 0.7}) == "INCONCLUSIVE"
    assert V.seed_verdict({**b, "void": True}) == "VOID"
    assert V.overall_verdict(["KILL"] * 4 + ["VOID"]) == "KILL"
    assert V.overall_verdict(["KILL"] * 3 + ["VOID"] * 2) == "INCONCLUSIVE"
    assert V.overall_verdict(["KILL"] * 3 + ["INCONCLUSIVE"] * 2) == "INCONCLUSIVE"


@pytest.mark.parametrize("rule,expect", [(V.written_rule_declines, "KILL"), (cap30, "POLICY_MATTERS")])
def test_end_to_end_realistic_lenders(rule, expect):
    """Realistic imbalance and a sparse 720 cell, leaves scaled to the sample: a follower gives KILL, a lender that
    ignores the conditional gives POLICY_MATTERS."""
    X, y = realistic(80000, rule, seed=7)
    old = (V.LEAVES, V.MIN_G, V.MIN_MASS)
    V.LEAVES, V.MIN_G, V.MIN_MASS = (150, 400), 10, 5
    try:
        res = V.run(X, y, seeds=V.SEEDS, n_trees=150, eps_list=[0.01], reasons=False)
    finally:
        V.LEAVES, V.MIN_G, V.MIN_MASS = old
    assert res["verdict"] == expect, res["per_seed_primary"]
