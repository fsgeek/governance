#!/usr/bin/env python3
"""PROBE (not the deliverable) — does the matched-joint argument hold empirically?

Pre-reg under test:
    docs/superpowers/specs/2026-05-24-compliant-practice-disparate-impact-V2-preregistration-note.md

Structural claim being risked:
    The twin-world is matched on the observable joint P(V_named, c_fresh, Y).
    => ANY reference that is a functional of that joint is world-invariant, so its
       separation_auc (ranking World-A=proxy above World-B=legit) is ~0.5 by
       construction, bounded only by calibration leak (eps_world).
    => The whole G-free reference family (R1/R2/R3/R5/R6) is BLIND.
    => R4 escapes ONLY by conditioning the Y-channel on Ghat_bisg (built from true
       G, outside the matched joint). The R4 *as pinned* (two marginal CMIs, both
       world-invariant) is ALSO blind; only the deconfounding contrast separates,
       scaling with bisg_auc.

This probe uses AUC-lift operationalizations (dependency-light) of three references
that cleanly discriminate the claim. If confirmed, the full harness implements the
pinned KSG/npeet estimators for R1-R6; if a G-free ref separates, the substrate
leaks and the argument is wrong (either way a finding).

    R_free   = lift_c_fresh(Y | V_named)
                 [represents the G-free family: c_fresh residual association w/ Y
                  given observables. PREDICTED ~0.5]
    R4_lit   = lift_c_fresh(Y | V_named) - lift_c_fresh(Ghat_bin | V_named)
                 [the pinned 'I(c_fresh;Y|V_named) vs I(c_fresh;Ghat|V_named)' shape;
                  both operands world-invariant. PREDICTED ~0.5]
    R4_deconf= lift_c_fresh(Y | V_named) - lift_c_fresh(Y | V_named, Ghat)
                 [deconfounding: how much of c_fresh's Y-association is explained by
                  estimated G. PREDICTED >0.5, rising with bisg_auc]

where lift_c_fresh(T | S) = AUC(GBT: T ~ S + c_fresh) - AUC(GBT: T ~ S), held-out.

Run:  PYTHONPATH=. python3 scripts/c3_separation_probe.py
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

REPO = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "fairwash_frontier_dgp", REPO / "scripts" / "fairwash_frontier_dgp.py")
dgp = importlib.util.module_from_spec(_spec)
sys.modules["fairwash_frontier_dgp"] = dgp
_spec.loader.exec_module(dgp)

V_NAMED = [f"x{j}" for j in range(6)]
CFRESH = ["cfresh_cont", "cfresh_cat", "cfresh_count"]

PROXY_GRID = (0.55, 0.70, 0.85)
BISG_GRID = (0.75, 0.85, 0.95)
SEEDS = range(6)
N = 4000


def _gbt(seed):
    return GradientBoostingClassifier(max_depth=3, n_estimators=80,
                                      subsample=0.8, random_state=seed)


def _auc(frame, feats, target, tr, te, seed):
    m = _gbt(seed).fit(frame[feats].values[tr], target[tr])
    return roc_auc_score(target[te], m.predict_proba(frame[feats].values[te])[:, 1])


def _lift(frame, base_feats, target, tr, te, seed):
    """AUC lift of adding c_fresh to base_feats for predicting `target`."""
    with_cf = base_feats + CFRESH
    return (_auc(frame, with_cf, target, tr, te, seed)
            - _auc(frame, base_feats, target, tr, te, seed))


def references(frame, seed):
    y = frame["Y"].values.astype(int)
    ghat = frame["Ghat_bisg"].values
    ghat_bin = (ghat > np.median(ghat)).astype(int)
    frame = frame.copy()
    frame["_ghat"] = ghat
    tr, te = train_test_split(np.arange(len(y)), test_size=0.4, random_state=0)

    r_free = _lift(frame, V_NAMED, y, tr, te, seed)
    lift_y_given_vn_ghat = _lift(frame, V_NAMED + ["_ghat"], y, tr, te, seed)
    lift_ghat_given_vn = _lift(frame, V_NAMED, ghat_bin, tr, te, seed)

    return {
        "R_free": r_free,
        "R4_lit": r_free - lift_ghat_given_vn,
        "R4_deconf": r_free - lift_y_given_vn_ghat,
    }


def sep_auc(vals_A, vals_B):
    """AUC ranking World-A (proxy, label 1) above World-B (legit, label 0)."""
    labels = np.r_[np.ones(len(vals_A)), np.zeros(len(vals_B))]
    scores = np.r_[vals_A, vals_B]
    return roc_auc_score(labels, scores)


def main():
    refs = ["R_free", "R4_lit", "R4_deconf"]
    print(f"n={N} seeds={list(SEEDS)} | sep_auc = rank(WorldA proxy > WorldB legit)\n")
    for ps in PROXY_GRID:
        for b in BISG_GRID:
            A = {r: [] for r in refs}
            B = {r: [] for r in refs}
            for s in SEEDS:
                fa = dgp.generate_twin_world(ps, "A", N, s, bisg_auc=b).frame
                fb = dgp.generate_twin_world(ps, "B", N, s, bisg_auc=b).frame
                ra, rb = references(fa, s), references(fb, s)
                for r in refs:
                    A[r].append(ra[r]); B[r].append(rb[r])
            cells = []
            for r in refs:
                sa = sep_auc(A[r], B[r])
                cells.append(f"{r}={sa:.3f} (A{np.mean(A[r]):+.3f}/B{np.mean(B[r]):+.3f})")
            print(f"ps={ps:.2f} bisg={b:.2f} | " + " | ".join(cells))
        print()


if __name__ == "__main__":
    main()
