#!/usr/bin/env python3
"""PROBE (not the deliverable) — is the twin-world leak a finite-p_obs artifact?

Follows c3_separation_probe.py, which found the G-free reference R_free shows
separation_auc 0.61-0.69 driven by a TINY but sign-consistent effect (World A
keeps ~0.006 more c_fresh->Y lift than World B). Hypothesis: that leak is the gap
between the FROZEN World-B label model (GradientBoostingRegressor depth=3,
n_estimators=200 -- scripts/fairwash_frontier_dgp.py:309) and the true
E[Y_A | observables]. If so, the twin-world is non-identifiable only UP TO the
capacity of the matching model: a reference more powerful than p_obs detects the
residual.

This does NOT touch the frozen DGP. It replicates the World-B construction in-probe
with p_obs of increasing capacity, holding World A and the observables fixed, and
measures whether the leak (R_free's A-B effect) shrinks toward 0.

    R_free(world) = lift_c_fresh(Y | V_named)
                  = AUC(GBT: Y ~ V_named + c_fresh) - AUC(GBT: Y ~ V_named), held-out.

PREDICTION (mine): the A-B effect shrinks monotonically as p_obs capacity rises;
the frozen depth-3/200 point sits at ~0.006 (matching the first probe). A plateau
well above 0 would mean structural (not capacity) mismatch -- the audit could
exploit it, and the substrate's non-identifiability would be weaker than claimed.

Run:  PYTHONPATH=. python3 scripts/c3_leak_capacity_probe.py
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

REPO = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "fairwash_frontier_dgp", REPO / "scripts" / "fairwash_frontier_dgp.py")
dgp = importlib.util.module_from_spec(_spec)
sys.modules["fairwash_frontier_dgp"] = dgp
_spec.loader.exec_module(dgp)

V_NAMED = [f"x{j}" for j in range(6)]
OBS = [f"x{j}" for j in range(8)]            # x0..x7 (the DGP's p_obs input)
CFRESH = ["cfresh_cont", "cfresh_cat", "cfresh_count"]
P_OBS_INPUT = OBS + CFRESH                     # matches dgp World-B construction

PS = 0.85
SEEDS = range(12)
N = 4000
# (depth, n_estimators); the frozen DGP point is (3, 200).
CAPACITIES = [(2, 100), (3, 200), (4, 400), (5, 800), (6, 1500)]


def _gbt(seed):
    return GradientBoostingClassifier(max_depth=3, n_estimators=80,
                                      subsample=0.8, random_state=seed)


def _auc(frame, feats, y, tr, te, seed):
    m = _gbt(seed).fit(frame[feats].values[tr], y[tr])
    return roc_auc_score(y[te], m.predict_proba(frame[feats].values[te])[:, 1])


def r_free(frame, y, seed):
    tr, te = train_test_split(np.arange(len(y)), test_size=0.4, random_state=0)
    return (_auc(frame, V_NAMED + CFRESH, y, tr, te, seed)
            - _auc(frame, V_NAMED, y, tr, te, seed))


def world_b_labels(frame, y_a, depth, n_est, seed):
    """Replicate the World-B draw with a p_obs of the given capacity."""
    obs = frame[P_OBS_INPUT].values
    reg = GradientBoostingRegressor(max_depth=depth, n_estimators=n_est,
                                    learning_rate=0.05, subsample=0.8,
                                    random_state=seed)
    p = np.clip(reg.fit(obs, y_a).predict(obs), 1e-4, 1 - 1e-4)
    return np.random.default_rng(seed + 777).binomial(1, p)


def paired_ci(diffs, reps=2000, seed=0):
    rng = np.random.default_rng(seed)
    d = np.asarray(diffs)
    boot = [rng.choice(d, len(d), replace=True).mean() for _ in range(reps)]
    return float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))


def main():
    print(f"ps={PS} n={N} seeds={list(SEEDS)} | R_free leak vs p_obs capacity\n")
    # World A is fixed; cache its R_free and Y_A per seed.
    A_vals, frames, y_as = {}, {}, {}
    for s in SEEDS:
        fa = dgp.generate_twin_world(PS, "A", N, s).frame
        frames[s], y_as[s] = fa, fa["Y"].values.astype(int)
        A_vals[s] = r_free(fa, y_as[s], s)

    # Anchor: the actual frozen DGP World B (its own independent generate call).
    fb_anchor = {s: dgp.generate_twin_world(PS, "B", N, s).frame for s in SEEDS}
    anchor_diffs = [A_vals[s] - r_free(fb_anchor[s], fb_anchor[s]["Y"].values.astype(int), s)
                    for s in SEEDS]
    sa = roc_auc_score(np.r_[np.ones(len(SEEDS)), np.zeros(len(SEEDS))],
                       np.r_[[A_vals[s] for s in SEEDS],
                             [r_free(fb_anchor[s], fb_anchor[s]["Y"].values.astype(int), s)
                              for s in SEEDS]])
    lo, hi = paired_ci(anchor_diffs)
    print(f"  frozen DGP World-B (depth3/200): effect(A-B)={np.mean(anchor_diffs):+.4f} "
          f"CI[{lo:+.4f},{hi:+.4f}]  sep_auc={sa:.3f}")
    print()

    for depth, n_est in CAPACITIES:
        diffs, B_vals = [], []
        for s in SEEDS:
            yb = world_b_labels(frames[s], y_as[s], depth, n_est, s)
            bval = r_free(frames[s], yb, s)
            B_vals.append(bval)
            diffs.append(A_vals[s] - bval)
        lo, hi = paired_ci(diffs)
        sep = roc_auc_score(np.r_[np.ones(len(SEEDS)), np.zeros(len(SEEDS))],
                            np.r_[[A_vals[s] for s in SEEDS], B_vals])
        tag = " <- frozen" if (depth, n_est) == (3, 200) else ""
        print(f"  p_obs depth={depth} n={n_est:4d}: effect(A-B)={np.mean(diffs):+.4f} "
              f"CI[{lo:+.4f},{hi:+.4f}]  sep_auc={sep:.3f}{tag}")


if __name__ == "__main__":
    main()
