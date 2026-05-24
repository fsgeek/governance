#!/usr/bin/env python3
"""PROBE (not the deliverable) — does the §2d omnibus gate miss what a targeted
reference sees on the SAME frozen twin-world?

Findings so far (c3_separation_probe.py, c3_leak_capacity_probe.py):
  - the frozen twin-world (depth-3 p_obs) leaves a tiny (~0.005) but sign-consistent
    leak: World A keeps marginally more c_fresh->Y signal than World B.
  - a targeted aggregate reference (R_free, paired over seeds) reports sep_auc ~0.65.

The pre-reg's substrate-validity gate (§2d) is a ROW-LEVEL OMNIBUS discriminator:
stack World-A rows vs World-B rows, classify, require CV accuracy <= 0.53 (soft
0.56). The smoke passes that 8/8. HYPOTHESIS: that gate is at chance on the SAME
data where the targeted reference separates -- the gate tests row-level
distinguishability, the references test a targeted distributional functional.
A pass on the omnibus gate does NOT certify the references can't separate.

This probe runs the §2d omnibus discriminator at depth {3,6} on the frozen
substrate and prints it beside the targeted R_free sep_auc, per proxy_strength.

PREDICTION (mine): omnibus accuracy ~0.50 at BOTH depths (row-level match holds),
while targeted R_free sep_auc ~0.6-0.7. Same data, opposite verdicts => the
calibration gate and the reference threat model are mismatched.

Run:  PYTHONPATH=. python3 scripts/c3_detector_mismatch_probe.py
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
from sklearn.ensemble import GradientBoostingClassifier, HistGradientBoostingClassifier
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import train_test_split

REPO = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "fairwash_frontier_dgp", REPO / "scripts" / "fairwash_frontier_dgp.py")
dgp = importlib.util.module_from_spec(_spec)
sys.modules["fairwash_frontier_dgp"] = dgp
_spec.loader.exec_module(dgp)

V_NAMED = [f"x{j}" for j in range(6)]
OBS = [f"x{j}" for j in range(8)]
CFRESH = ["cfresh_cont", "cfresh_cat", "cfresh_count"]
OMNIBUS_FEATS = OBS + CFRESH + ["Y"]          # §2d's audit-observable joint

PS_GRID = (0.70, 0.85)
SEEDS = range(8)
N = 3000


def _ref_gbt(seed):
    return GradientBoostingClassifier(max_depth=3, n_estimators=80,
                                      subsample=0.8, random_state=seed)


def r_free(frame, seed):
    y = frame["Y"].values.astype(int)
    tr, te = train_test_split(np.arange(len(y)), test_size=0.4, random_state=0)
    def auc(feats):
        m = _ref_gbt(seed).fit(frame[feats].values[tr], y[tr])
        return roc_auc_score(y[te], m.predict_proba(frame[feats].values[te])[:, 1])
    return auc(V_NAMED + CFRESH) - auc(V_NAMED)


def omnibus_acc(fa, fb, depth):
    """§2d row-level discriminator: World-A rows vs World-B rows, held-out acc.

    A and B share identical X/c_fresh at the same seed (only Y differs), so the
    split MUST keep each row's A/B twins on the same side -- a shuffled split lets
    the classifier memorize X->class from one twin and invert the other (accuracy
    below chance). Split by PAIR INDEX.
    """
    n = len(fa)
    rng = np.random.default_rng(0)
    perm = rng.permutation(n)
    te_i, tr_i = perm[:int(0.4 * n)], perm[int(0.4 * n):]
    Xa, Xb = fa[OMNIBUS_FEATS].values, fb[OMNIBUS_FEATS].values
    Xtr = np.vstack([Xa[tr_i], Xb[tr_i]]); ytr = np.r_[np.zeros(len(tr_i)), np.ones(len(tr_i))]
    Xte = np.vstack([Xa[te_i], Xb[te_i]]); yte = np.r_[np.zeros(len(te_i)), np.ones(len(te_i))]
    clf = HistGradientBoostingClassifier(max_depth=depth,
                                         max_iter=150 if depth == 3 else 350,
                                         random_state=0)
    clf.fit(Xtr, ytr)
    return float(accuracy_score(yte, clf.predict(Xte)))


def main():
    print(f"n={N} seeds={list(SEEDS)} | omnibus row-level gate vs targeted reference\n")
    for ps in PS_GRID:
        A, B, omni3, omni6 = [], [], [], []
        for s in SEEDS:
            fa = dgp.generate_twin_world(ps, "A", N, s).frame
            fb = dgp.generate_twin_world(ps, "B", N, s).frame
            A.append(r_free(fa, s)); B.append(r_free(fb, s))
            omni3.append(omnibus_acc(fa, fb, 3))
            omni6.append(omnibus_acc(fa, fb, 6))
        sep = roc_auc_score(np.r_[np.ones(len(SEEDS)), np.zeros(len(SEEDS))], np.r_[A, B])
        print(f"ps={ps:.2f}")
        print(f"   §2d omnibus row-level acc  depth3={np.mean(omni3):.4f}  "
              f"depth6={np.mean(omni6):.4f}   (gate passes if <= 0.53)")
        print(f"   targeted R_free  sep_auc={sep:.3f}  effect(A-B)={np.mean(A)-np.mean(B):+.4f}")
        print()


if __name__ == "__main__":
    main()
