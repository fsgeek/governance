"""Unit-test contract for the fairwash-reorganization frontier harness (§6).

Pre-reg: docs/superpowers/specs/2026-05-23-fairwash-reorganization-frontier-preregistration-note.md

Covers the five §6 unit tests:
  1. T_naive / T_adv preserve retained effect r AND AUC on a toy.
  2. T_adv respects its convergence/ceiling budget.
  3. classify_reorganized separates hand-built reorganized vs honest uf-sets.
  4. each remediated control yields Delta ~ 0.
  5. weight-shift-within-stable-set is invisible to rung 3a (the §5 known limit).
"""
import importlib.util
import sys
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "fairwash_frontier_test",
    Path(__file__).resolve().parents[2] / "scripts" / "fairwash_frontier_test.py",
)
ff = importlib.util.module_from_spec(_spec)
sys.modules["fairwash_frontier_test"] = ff  # register before exec so @dataclass resolves __module__
_spec.loader.exec_module(ff)

N_TOY = 1500


def _sub(channel="D1", seed=0):
    return ff.make_substrate(channel, seed, n_total=N_TOY)


def test_substrate_is_valid_disparity():
    sub = _sub("D1")
    M = ff.fit_discriminatory_M(sub)
    d = ff.dp_gap(ff.decisions(M, sub.test), sub.test["G"].values)
    assert abs(d) >= ff.DELTA_MIN, f"toy D1 disparity {d} below floor"


def test_t_naive_preserves_retention_and_auc():
    # D2 (single-proxy) is the channel where naive rerouting onto an admissible
    # carrier is *designed* to launder: the disparity flows through a legit feature
    # the carrier can proxy. (D1's direct-G effect has no strong single carrier, so
    # naive laundering there debiases instead -- a separate, real phenomenon.)
    sub = _sub("D2")
    M = ff.fit_discriminatory_M(sub)
    auc_M = ff.auc_of(M, sub.test)
    T = ff.transform_naive(M, sub)
    # laundering, not debiasing: retained effect clears the floor ...
    assert T.r_retained >= ff.RETENTION_FLOOR, f"r={T.r_retained} below floor (debiasing, not laundering)"
    # ... while performance is preserved within tolerance.
    assert T.auc >= auc_M - 0.07, f"T_naive AUC {T.auc} collapsed vs M {auc_M}"


def test_t_adv_preserves_and_respects_budget():
    sub = _sub("D1")
    M = ff.fit_discriminatory_M(sub)
    auc_M = ff.auc_of(M, sub.test)
    T = ff.transform_adv(M, sub, patience_W=2, ceiling=10, auc_M=auc_M)
    # budget respected: reported step count cannot exceed the ceiling.
    import re
    steps = int(re.search(r"steps=(\d+)", T.note).group(1))
    assert steps <= 10, f"T_adv ran {steps} steps past ceiling 10"
    assert T.auc >= auc_M - 0.10, f"T_adv AUC {T.auc} collapsed vs M {auc_M}"


def test_classify_reorganized_separates_honest_from_reorganized():
    # honest: identical used-feature-sets after restriction -> not reorganized.
    A_honest = ff.restrict([["x0", "x1"], ["x2"]], prohibited=set())
    B_honest = {frozenset(["x0", "x1"]), frozenset(["x2"])}
    is_reorg, _, j = ff.classify_reorganized(A_honest, B_honest, ff.RUNG3A_JTHRESH)
    assert not is_reorg and j == 1.0
    # reorganized: B uses entirely different features.
    A_r = ff.restrict([["x0", "x1"], ["x2"]], prohibited=set())
    B_r = {frozenset(["cfresh_cont"]), frozenset(["cfresh_count"])}
    is_reorg2, _, j2 = ff.classify_reorganized(A_r, B_r, ff.RUNG3A_JTHRESH)
    assert is_reorg2 and j2 == 0.0


def test_controls_remediate_and_do_not_launder():
    # CORRECTED criterion (verification finding 2026-05-24): a genuinely-fair
    # control is NOT "Delta ~ 0" -- legitimate risk (x0) is entangled with G by
    # construction, so even the oracle shows a legitimate nonzero parity gap. The
    # right qualification is (a) the control remediates the EXCESS disparity (Delta
    # well below M, near the oracle's legitimate baseline) and (b) it does not
    # launder -- its c_fresh importance is ~ 0. (b) is what rung-3b's P5 calibration
    # actually rests on; demographic parity is the wrong axis.
    sub = _sub("D1")
    M = ff.fit_discriminatory_M(sub)
    d_M = ff.dp_gap(ff.decisions(M, sub.test), sub.test["G"].values)
    controls = ff.build_controls(sub)
    G = sub.test["G"].values
    d_oracle = ff.dp_gap(ff.decisions(controls["C_oracle"], sub.test), G)
    for name in ("C_drop", "C_oracle"):
        d_c = ff.dp_gap(ff.decisions(controls[name], sub.test), G)
        assert abs(d_c) < abs(d_M), f"{name} did not remediate excess disparity ({d_c} vs M {d_M})"
        # does not launder: negligible reliance on the admissible carriers
        cf = max(ff._cfresh_importance(controls[name], sub, estimator="split_gain").values())
        assert cf < 0.10, f"{name} routes through c_fresh (imp={cf}) -- not a clean control"
    # the oracle's legitimate baseline is itself nonzero (the entanglement point)
    assert abs(d_oracle) > 0.0


def test_weight_shift_within_stable_set_invisible_to_rung3a():
    # The §5 known limit: if the used-feature-set is held fixed (only weight moves),
    # the set-based rung 3a must score not-reorganized -- it cannot see weight.
    stable = [["x0", "cfresh_cont"], ["x1", "cfresh_cont"]]
    A = ff.restrict(stable, prohibited=set())
    B = {frozenset(u) for u in stable}  # identical sets, "weight" is invisible here
    is_reorg, reason, j = ff.classify_reorganized(A, B, ff.RUNG3A_JTHRESH)
    assert not is_reorg and j == 1.0, "rung 3a must be blind to weight-only shifts"
