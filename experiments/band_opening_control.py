"""Stage-1 control runner. Run directly: python -m experiments.band_opening_control

Prints per-family C/A/B and asserts the gate. Stage 2 is forbidden until this passes.
"""
from __future__ import annotations

from functools import partial

from wedge.band_outcomes import band_outcomes
from wedge.losses import grant_emphasis_loss
from wedge.rashomon import evaluate_policy, filter_to_epsilon_under_loss
from wedge.sweep_families import sweep_family
from experiments.synthetic_planted import make_planted_dataset

EPS = 0.05  # control uses the loose end of the frozen sweep; full sweep in Stage 2


def run_control(random_state: int = 0) -> dict:
    X, y, protected, mono, policy = make_planted_dataset(random_state=random_state)
    feature_subsets = (("legit_a", "legit_b"),)  # the clean subset (proxy excluded)
    grids = {"cart": {"max_depths": (2, 3, 4), "min_samples_leafs": (20,)},
             "linear": {"Cs": (0.05, 0.2, 1.0)},
             "gbm": {"max_iters": (50,)}}
    out = {}
    for fam, grid in grids.items():
        results = sweep_family(X, y, family=fam, grid=grid,
                               feature_subsets=feature_subsets, monotonic_cst=mono)
        pa = evaluate_policy(results, policy_constraints=policy)
        band = filter_to_epsilon_under_loss(
            pa, loss_fn=partial(grant_emphasis_loss), loss_label="L_T", epsilon=EPS)
        members = [m.fitted_model for m in band.within_epsilon]
        out[fam] = band_outcomes(members, X, protected, tau=0.02)
    gate_passed = bool(out["cart"]["B_plain"] and out["linear"]["B_plain"])
    out["gate_passed"] = gate_passed
    return out


if __name__ == "__main__":
    res = run_control()
    for fam in ("cart", "linear", "gbm"):
        print(fam, res[fam])
    print("GATE PASSED:", res["gate_passed"])
    assert res["gate_passed"], (
        "CONTROL FAILED: harness did not recover a planted clean member. "
        "Fix the harness before Stage 2. Do NOT run real data.")
