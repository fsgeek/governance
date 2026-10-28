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


def fit(X, y, cols=(0, 1), depth=4, leaf=200, mono_cst=False):
    cols = list(cols)
    t = DecisionTreeClassifier(max_depth=depth, min_samples_leaf=leaf, random_state=0,
                               monotonic_cst=[V.MONO[c] for c in cols] if mono_cst else None).fit(X[:, cols], y)
    return V.Member(t, cols, depth, leaf)


def test_sklearn_monotonic_cst_cannot_represent_the_rule_but_the_filter_admits_it():
    """The r3 trap: sklearn's monotonic_cst midpoint bounds forbid the 720 interaction leaf. Built on it, G could
    never embody the written rule and the verdict would be POLICY_MATTERS for any lender."""
    X, y = realistic(150000, V.written_rule_declines, seed=1, p_other=0.9, sparse_cell=False)
    ref = (X[:50000], y[:50000])
    cst, free = fit(X, y, depth=4, leaf=300, mono_cst=True), fit(X, y, depth=4, leaf=300)
    for m in (cst, free):
        m.val_loss = V.logloss(ref[1], V.p_accept(m, ref[0]))
    assert V.gating_gain(cst, *ref) > 0.01             # constrained: can't find the staircase
    assert abs(V.gating_gain(free, *ref)) < 1e-3        # unconstrained: finds it exactly
    assert not V.monotone_violation(free, X[50000:100000], y[50000:100000])   # and the exact filter admits it


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


def test_gating_gain_zero_for_a_tree_that_found_the_rule_and_positive_for_one_that_pooled():
    Xf, yf = realistic(150000, V.written_rule_declines, seed=1, p_other=0.9, sparse_cell=False)
    sharp = fit(Xf, yf, depth=4, leaf=300)
    sharp.val_loss = V.logloss(yf[:50000], V.p_accept(sharp, Xf[:50000]))
    assert abs(V.gating_gain(sharp, Xf[:50000], yf[:50000])) < 1e-3
    coarse = fit(Xf, yf, depth=1, leaf=300)                    # one split can't hold the staircase
    coarse.val_loss = V.logloss(yf[:50000], V.p_accept(coarse, Xf[:50000]))
    assert V.gating_gain(coarse, Xf[:50000], yf[:50000]) > 0.005


def test_gating_hurts_when_the_lender_did_not_follow_the_rule():
    Xc, yc = realistic(150000, cap30, seed=1, p_other=0.9, sparse_cell=False)
    m = fit(Xc, yc, depth=4, leaf=300)
    m.val_loss = V.logloss(yc[:50000], V.p_accept(m, Xc[:50000]))
    assert V.gating_gain(m, Xc[:50000], yc[:50000]) < -0.005


def test_cap30_lender_violates_but_respects_floors():
    Xc, yc = realistic(120000, cap30, seed=1, p_other=0.9, sparse_cell=False)
    ignores = fit(Xc, yc, leaf=300)
    assert V.violates(ignores, Xc[:40000])
    assert not V.violates(ignores, Xc[:40000], V.floors_declines)


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


def test_monotone_filter_rejects_a_reversal_and_tolerates_small_noise():
    X, y = realistic(40000, V.written_rule_declines, seed=5)
    rev = fit(X[:30000], 1 - y[:30000])
    assert V.monotone_violation(rev, X[30000:], 1 - y[30000:])   # rewards low scores / high DTI
    rng = np.random.default_rng(9)
    n = 60000
    Xn = np.column_stack([V.bucket5(rng.uniform(640, 800, n)), rng.uniform(0, 20, n), np.zeros(n), np.zeros(n)])
    yn = (rng.random(n) < 0.3).astype(int)                  # flat rate: leaf noise only, well under DELTA
    noise = fit(Xn[:30000], yn[:30000], depth=3, leaf=3000)
    assert not V.monotone_violation(noise, Xn[30000:], yn[30000:])   # held-out estimates don't


def test_seed_metrics_uses_heldout_leaves_for_monotonicity():
    """The pipeline path, not just the helper: a noise tree whose TRAINING leaves show a selection-inflated gap must
    still count as monotone in seed_metrics, because seed_metrics estimates leaves on validation rows."""
    rng = np.random.default_rng(9)
    n = 60000
    Xn = np.column_stack([V.bucket5(rng.uniform(640, 800, n)), rng.uniform(0, 20, n), np.zeros(n), np.zeros(n)])
    yn = (rng.random(n) < 0.3).astype(int)
    noise = fit(Xn, yn, depth=3, leaf=3000)
    assert V.monotone_violation(noise)                      # training leaves: flagged (the trap)
    r2 = np.random.default_rng(10)                          # an independent held-out draw of the same noise
    Xh = np.column_stack([V.bucket5(r2.uniform(640, 800, n)), r2.uniform(0, 20, n), np.zeros(n), np.zeros(n)])
    yh = (r2.random(n) < 0.3).astype(int)
    noise.val_loss = V.logloss(yh, V.p_accept(noise, Xh))
    out = V.seed_metrics([noise], Xh, yh, Xh, [0.01])
    assert out["n_monotone"] == 1


def test_leaf_box_order_matches_tree_node_order():
    X, y = realistic(30000, V.written_rule_declines)
    m = fit(X, y, cols=(0, 1, 2))
    tr = m.tree.tree_
    leaves = [j for j in range(tr.node_count) if tr.children_left[j] == -1]
    boxes = V.leaf_boxes(m, with_n=True)
    assert [j for *_, j in boxes] == leaves                     # node ids recorded, not inferred from order
    assert [n for _, _, n, _ in boxes] == [int(tr.n_node_samples[j]) for j in leaves]


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
    b = {"void": False, "best_tree": {"material": 0}, "eps_star": 0.03}
    assert V.seed_verdict(b) == "KILL"
    assert V.seed_verdict({**b, "eps_star": 0.002}) == "POLICY_MATTERS"
    assert V.seed_verdict({**b, "eps_star": 0.008}) == "DEPENDS_ON_EPSILON"
    assert V.seed_verdict({**b, "eps_star": float("inf")}) == "KILL"           # no band is ever dominated
    assert V.seed_verdict({**b, "void": True}) == "VOID"
    assert V.overall_verdict(["DEPENDS_ON_EPSILON"] * 4 + ["KILL"]) == "DEPENDS_ON_EPSILON"
    assert V.overall_verdict(["KILL"] * 3 + ["VOID"] * 2) == "INCONCLUSIVE"


def test_construct_share_and_tolerant_gate():
    X = np.array([[700, 24.9, 0, 0], [700, 25.0, 0, 0], [700, 25.6, 0, 0], [715, 27.0, 0, 0], [650, 10, 0, 0]], float)
    assert V.gate_mask(X).tolist() == [False, False, True, False, True]    # 25.0 and the 715 bucket are tolerated
    y = np.array([1, 1, 1, 1, 0])
    assert V.construct_share(X, y) == 0.25


def test_gated_accepts_are_excluded_from_the_materiality_test():
    """Adversary 3, finding 2: a handful of accepts inside the gate (13.8 nats each) mustn't swamp a real gain."""
    Xf, yf = realistic(150000, V.written_rule_declines, seed=1, p_other=0.9, sparse_cell=False)
    coarse = fit(Xf, yf, depth=1, leaf=300)
    Xv, yv = Xf[:50000].copy(), yf[:50000].copy()
    g0, z0 = V.gating_z(coarse, Xv, yv)
    Xv[:6] = [700.0, 27.0, 10000.0, 3.0]; yv[:6] = 1           # six accepted rows inside the gate
    g1, z1 = V.gating_z(coarse, Xv, yv)
    assert z0 > 3 and z1 > 3 and abs(g1 - g0) / g0 < 0.05


def test_one_accepted_row_in_the_gate_costs_13_8_nats():
    assert abs(V.row_losses(np.array([1]), np.array([0.0]))[0] - (-math.log(1e-6))) < 1e-9


def test_gating_z_is_zero_for_a_rule_embodying_tree_and_large_for_a_pooling_one():
    Xf, yf = realistic(150000, V.written_rule_declines, seed=1, p_other=0.9, sparse_cell=False)
    sharp, coarse = fit(Xf, yf, depth=4, leaf=300), fit(Xf, yf, depth=1, leaf=300)
    assert abs(V.gating_z(sharp, Xf[:50000], yf[:50000])[1]) < 3
    assert V.gating_z(coarse, Xf[:50000], yf[:50000])[1] > 3


@pytest.mark.parametrize("p_other,rule,depths,expect", [
    (0.9, V.written_rule_declines, (2, 3, 4), "KILL"),             # follower whose misstating trees cost a lot of fit
    (0.9, V.written_rule_declines, (1,), "POLICY_MATTERS"),        # even the best model can't hold the rule
    (0.9, cap30, (2, 3, 4), "CONSTRUCT_INVALID"),                  # accepts the rule declines: the gate would measure mismatch
])
def test_end_to_end_branches_reachable(p_other, rule, depths, expect):
    X, y = realistic(80000, rule, seed=7, p_other=p_other, sparse_cell=False)
    old = (V.LEAVES, V.MIN_G, V.MIN_MASS, V.DEPTHS)
    V.LEAVES, V.MIN_G, V.MIN_MASS, V.DEPTHS = (150, 400), 10, 5, depths
    try:
        res = V.run(X, y, seeds=V.SEEDS, n_trees=400, eps_list=[0.01], reasons=False, capacity=False)
    finally:
        V.LEAVES, V.MIN_G, V.MIN_MASS, V.DEPTHS = old
    assert res["verdict"] == expect, (res.get("per_seed"), res.get("eps_star_median"), res.get("construct_share"))


def test_capacity_check_downgrades_a_size_driven_verdict():
    """Adversary 3, finding 1: a follower fit with depth-1 trees reads POLICY_MATTERS; deeper trees learn the rule, so
    the frozen verdict must become CAPACITY_DEPENDENT rather than claim the record corrects models in general."""
    X, y = realistic(80000, V.written_rule_declines, seed=7, p_other=0.9, sparse_cell=False)
    old = (V.LEAVES, V.MIN_G, V.MIN_MASS, V.DEPTHS, V.CAPACITY_SEEDS)
    V.LEAVES, V.MIN_G, V.MIN_MASS, V.DEPTHS, V.CAPACITY_SEEDS = (150, 400), 10, 5, (1,), 2
    try:
        res = V.run(X, y, seeds=V.SEEDS, n_trees=300, eps_list=[0.01], reasons=False, capacity=True)
    finally:
        V.LEAVES, V.MIN_G, V.MIN_MASS, V.DEPTHS, V.CAPACITY_SEEDS = old
    assert res["primary_verdict"] == "POLICY_MATTERS" and res["verdict"] == "CAPACITY_DEPENDENT", res.get("capacity_regions")
    assert V.DEPTHS == old[3]                                   # the global depth list is restored
