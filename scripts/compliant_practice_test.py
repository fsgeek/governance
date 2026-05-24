#!/usr/bin/env python3
"""Compliant-practice disparate impact (V2) — POST-FREEZE experiment.

Pre-registration (FROZEN, predictions immutable):
    docs/superpowers/specs/2026-05-24-compliant-practice-disparate-impact-V2-preregistration-note.md
    commit 8fa7992 / OTS cbd4298
Binding DGP spec (same freeze): scripts/fairwash_frontier_dgp.py::generate_twin_world

This first build covers the C3 path (the headline coin), built per the pre-harness
probe findings (working_notes/2026-05-24-c3-substrate-probe-findings.md):

  - C3-payload headline = R4-deconfounding's effect-size DOSE-RESPONSE in BISG quality
    (the live signal; the G-free family is blind in effect size by the matched joint).
  - Metric: EFFECT-SIZE (paired-bootstrap mean A-B + CI) and MARGIN-OVER-R1-NULL are
    co-primary. separation_auc is reported only as a CONTRAST (it manufactures signal
    from sign-consistent leak; the R1-null sanity check is reported and expected to fire).
  - R4 in BOTH forms: R4_marginal (the pinned 'I(c_fresh;Y|V_named) vs I(c_fresh;Ghat|
    V_named)' shape -- documented blind, both operands world-invariant) and R4_deconf
    (the operative deconfounding contrast, the result-note pre-reg correction).
  - The BRACKET (Tony's frame): C3-floor's omnibus row-level gate (LOWER-bound-denier)
    reported beside the targeted references (which reach the residual) -- the
    lower/upper bracket on achievable separation. Pair-INDEX splits throughout (a
    shuffled split inverts on the shared-X twins -- a probe-caught artifact).

ESTIMATOR NOTE: references use robust cross-fitted GBT AUC-lift estimators (validated
mechanism-faithful by the probes). The pre-reg pins KSG/npeet for R4 and EconML
causal-forest for R5's robustness arm; both libs are ABSENT and a swap is gated on a
deps decision (flagged, not silently substituted).

NOT YET BUILT (next): R6 reliance-shift, KSG R4 backend, C1 dose-retention + the model
family's M_full/M_oracle disparate-impact metrics, C2 rungs, C4 V2_adv. Structured for
those to slot in.

Run (smoke):  PYTHONPATH=. python3 scripts/compliant_practice_test.py --smoke
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from pathlib import Path

import numpy as np
from sklearn.ensemble import GradientBoostingClassifier, HistGradientBoostingClassifier
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold

REPO = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "fairwash_frontier_dgp", REPO / "scripts" / "fairwash_frontier_dgp.py")
dgp = importlib.util.module_from_spec(_spec)
sys.modules["fairwash_frontier_dgp"] = dgp
_spec.loader.exec_module(dgp)

# --- frozen scalars mirrored from pre-reg §2h --------------------------------
V_NAMED = [f"x{j}" for j in range(6)]            # x0..x5
DECLARED_PROXIES = ["x6", "x7"]
CFRESH = ["cfresh_cont", "cfresh_cat", "cfresh_count"]
OBS = [f"x{j}" for j in range(8)]                # x0..x7 audit-visible
OMNIBUS_FEATS = OBS + CFRESH + ["Y"]             # §2d audit-observable joint
PROXY_GRID = (0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85)
BISG_GRID = (0.75, 0.85, 0.95)
DELTA_SEP = 0.05                                  # margin-over-R1-null bet metric
R1_NULL_SANITY = 0.55                             # if R1 sep_auc exceeds this -> reconsider
N_DEFAULT = 8000
N_SEEDS_DEFAULT = 20

GBT_KW = dict(max_depth=3, n_estimators=120, subsample=0.8, learning_rate=0.1)


# ---------------------------------------------------------------------------
# Cross-fitted AUC-lift primitive (pair-index safe: operates within one frame)
# ---------------------------------------------------------------------------
def _cf_auc(frame, feats, target, seed, folds=2):
    """Cross-fitted out-of-sample AUC of GBT(target ~ feats)."""
    X = frame[feats].values
    y = np.asarray(target)
    skf = StratifiedKFold(n_splits=folds, shuffle=True, random_state=seed)
    oof = np.zeros(len(y))
    for tr, te in skf.split(X, y):
        m = GradientBoostingClassifier(random_state=seed, **GBT_KW).fit(X[tr], y[tr])
        oof[te] = m.predict_proba(X[te])[:, 1]
    return float(roc_auc_score(y, oof))


def _cfresh_lift(frame, base_feats, target, seed):
    """OOS AUC gained by adding the c_fresh portfolio to base_feats for `target`."""
    return (_cf_auc(frame, base_feats + CFRESH, target, seed)
            - _cf_auc(frame, base_feats, target, seed))


# ---------------------------------------------------------------------------
# Reference battery (each returns one scalar per frame; audit-observable inputs)
# ---------------------------------------------------------------------------
def references(frame, seed):
    y = frame["Y"].values.astype(int)
    ghat = frame["Ghat_bisg"].values
    ghat_bin = (ghat > np.median(ghat)).astype(int)
    fr = frame.copy()
    fr["_ghat"] = ghat

    # R1 -- held-out same-pool importance: c_fresh lift for Y given V_named. NULL FLOOR.
    r1 = _cfresh_lift(fr, V_NAMED, y, seed)

    # R3 -- residualized-carrier importance: strip the V_named-linear part of each
    # c_fresh, then measure the residuals' lift for Y over V_named.
    fr3 = fr.copy()
    Xn = fr[V_NAMED].values
    Xn1 = np.column_stack([np.ones(len(Xn)), Xn])
    for c in CFRESH:
        beta, *_ = np.linalg.lstsq(Xn1, fr[c].values, rcond=None)
        fr3[c] = fr[c].values - Xn1 @ beta
    r3 = _cfresh_lift(fr3, V_NAMED, y, seed)

    # R5 -- double-ML style: residualize Y and c_fresh on V_named (OOF), lift of the
    # c_fresh residuals for the Y residual (here: AUC of Y vs c_fresh-residual model
    # added over a V_named model == the partialled c_fresh->Y signal). Approximated by
    # the residualized-carrier lift on a fresh fold seed (decorrelates from R3's split).
    r5 = _cfresh_lift(fr3, V_NAMED, y, seed + 101)

    # R4_marginal (PINNED shape, documented blind): c_fresh's Y-lift minus its Ghat-lift,
    # both given V_named. Both operands are world-invariant (Y matched; Ghat shared) -> ~0.
    r4_marg = (_cfresh_lift(fr, V_NAMED, y, seed)
               - _cfresh_lift(fr, V_NAMED, ghat_bin, seed))

    # R4_deconf (OPERATIVE): reduction in c_fresh's Y-lift when Ghat is added to the
    # conditioning set. Large in World A (c_fresh->Y via latent G, deconfounded by Ghat),
    # small in World B (c_fresh->Y direct). Uses Ghat -> outside the matched joint.
    r4_deconf = (_cfresh_lift(fr, V_NAMED, y, seed)
                 - _cfresh_lift(fr, V_NAMED + ["_ghat"], y, seed))

    return {"R1": r1, "R3": r3, "R5": r5, "R4_marginal": r4_marg, "R4_deconf": r4_deconf}


G_FREE_REFS = ["R1", "R3", "R5"]          # R4_marginal is G-free-but-pinned-blind
ALL_REFS = ["R1", "R3", "R5", "R4_marginal", "R4_deconf"]


# ---------------------------------------------------------------------------
# The bracket: §2d omnibus row-level gate (LOWER-bound-denier), pair-index split
# ---------------------------------------------------------------------------
def omnibus_acc(fa, fb, depth=3, seed=0):
    """World-A rows vs World-B rows held-out accuracy. Pair-INDEX split (A/B twins of a
    row stay on the same side -- a shuffled split memorizes X->class and inverts)."""
    n = len(fa)
    perm = np.random.default_rng(seed).permutation(n)
    te, tr = perm[:int(0.4 * n)], perm[int(0.4 * n):]
    Xa, Xb = fa[OMNIBUS_FEATS].values, fb[OMNIBUS_FEATS].values
    Xtr = np.vstack([Xa[tr], Xb[tr]]); ytr = np.r_[np.zeros(len(tr)), np.ones(len(tr))]
    Xte = np.vstack([Xa[te], Xb[te]]); yte = np.r_[np.zeros(len(te)), np.ones(len(te))]
    clf = HistGradientBoostingClassifier(max_depth=depth, max_iter=200, random_state=seed)
    clf.fit(Xtr, ytr)
    return float(accuracy_score(yte, clf.predict(Xte)))


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------
def _paired_ci(diffs, reps=2000, seed=0):
    rng = np.random.default_rng(seed)
    d = np.asarray(diffs)
    boot = [rng.choice(d, len(d), replace=True).mean() for _ in range(reps)]
    return float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))


def _sep_auc(a_vals, b_vals):
    return float(roc_auc_score(np.r_[np.ones(len(a_vals)), np.zeros(len(b_vals))],
                               np.r_[a_vals, b_vals]))


def score_grid_point(ps, bisg, seeds, n):
    """Run all references on World A vs World B across seeds; return the metric block."""
    A = {r: [] for r in ALL_REFS}
    B = {r: [] for r in ALL_REFS}
    omni = []
    for s in seeds:
        fa = dgp.generate_twin_world(ps, "A", n, s, bisg_auc=bisg).frame
        fb = dgp.generate_twin_world(ps, "B", n, s, bisg_auc=bisg).frame
        ra, rb = references(fa, s), references(fb, s)
        for r in ALL_REFS:
            A[r].append(ra[r]); B[r].append(rb[r])
        omni.append(omnibus_acc(fa, fb, depth=3, seed=s))

    out = {"proxy_strength": ps, "bisg_auc": bisg, "n_seeds": len(seeds), "refs": {}}
    eff = {}
    for r in ALL_REFS:
        a, b = np.array(A[r]), np.array(B[r])
        diffs = a - b
        lo, hi = _paired_ci(diffs)
        eff[r] = float(diffs.mean())
        out["refs"][r] = {
            "effect_A_minus_B": float(diffs.mean()), "effect_ci": [lo, hi],
            "sep_auc": _sep_auc(a, b), "mean_A": float(a.mean()), "mean_B": float(b.mean()),
        }
    # margin-over-R1-null (effect-size form, the honest payload metric)
    for r in ALL_REFS:
        out["refs"][r]["effect_margin_over_R1"] = eff[r] - eff["R1"]
    # the bracket
    omni_mean = float(np.mean(omni))
    best_gfree_margin = max(out["refs"][r]["effect_margin_over_R1"] for r in G_FREE_REFS)
    out["bracket"] = {
        "omnibus_lowerbound_acc": omni_mean,        # gate passes if <= 0.53
        "gate_passes": omni_mean <= 0.53,
        "best_Gfree_effect_margin_over_R1": best_gfree_margin,
        "R4_deconf_effect_margin_over_R1": out["refs"]["R4_deconf"]["effect_margin_over_R1"],
        "R1_null_sanity_sep_auc": out["refs"]["R1"]["sep_auc"],
        "R1_null_sanity_fires": out["refs"]["R1"]["sep_auc"] > R1_NULL_SANITY,
    }
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--seeds", type=int, default=N_SEEDS_DEFAULT)
    ap.add_argument("--n", type=int, default=N_DEFAULT)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    if args.smoke:
        proxy_grid, bisg_grid, seeds, n = (0.55, 0.85), (0.85,), range(6), 3000
    else:
        proxy_grid, bisg_grid, seeds, n = PROXY_GRID, BISG_GRID, range(args.seeds), args.n

    t0 = time.time()
    points = []
    for ps in proxy_grid:
        for b in bisg_grid:
            pt = score_grid_point(ps, b, list(seeds), n)
            points.append(pt)
            br = pt["bracket"]
            print(f"[{time.time()-t0:6.1f}s] ps={ps:.2f} bisg={b:.2f} | "
                  f"R4_deconf eff={pt['refs']['R4_deconf']['effect_A_minus_B']:+.4f} "
                  f"margin={br['R4_deconf_effect_margin_over_R1']:+.4f} | "
                  f"bestGfree margin={br['best_Gfree_effect_margin_over_R1']:+.4f} | "
                  f"omnibus={br['omnibus_lowerbound_acc']:.3f} pass={br['gate_passes']} | "
                  f"R1sanity_fires={br['R1_null_sanity_fires']}", flush=True)

    out_path = (Path(args.out).resolve() if args.out else
                REPO / "runs" / ("compliant_practice_smoke.json" if args.smoke
                                 else "compliant_practice_c3_2026-05-24.json"))
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(json.dumps({
        "experiment": "compliant-practice disparate impact (V2) -- C3 path",
        "pre_reg_commit": "8fa7992", "smoke": args.smoke,
        "estimator": "cross-fitted GBT AUC-lift (KSG/causal-forest backends pending deps)",
        "points": points}, indent=2))
    print(f"\nWrote {out_path.relative_to(REPO)} ({len(points)} grid points)")


if __name__ == "__main__":
    main()
