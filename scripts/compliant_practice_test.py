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


# ---------------------------------------------------------------------------
# C1 -- the headline dose-response: does compliant practice RETAIN excess
# disparate impact, rising with proxy_strength? (World A, the contaminated world)
# ---------------------------------------------------------------------------
EPSILON_EXCESS = 0.05            # §2h denominator validity floor on adverse_excess(M_full)

# (feature set, training target). M_oracle trains on Y_clean over V_named -- per the
# anchor's OPEN subtlety, V_named excludes x6,x7 whose legit beta (0.60/0.35) the oracle
# is blind to; implemented AS WRITTEN, flagged in the JSON for the result note.
FAMILY = {
    "M_full":      (OBS + ["G"], "Y"),          # experimenter-side discriminatory upper baseline
    "M_compliant": (V_NAMED + CFRESH, "Y"),     # headline test article (no G, no declared proxies)
    "M_strict":    (V_NAMED, "Y"),              # strictest reading (differs from compliant by c_fresh)
    "M_oracle":    (V_NAMED, "Y_clean"),        # legitimate baseline (disparate term zeroed)
}


def _dp_gap(decision, G):
    g0 = decision[G == 0].mean() if (G == 0).any() else 0.0
    g1 = decision[G == 1].mean() if (G == 1).any() else 0.0
    return float(g0 - g1)


def fit_predict_family(fr, seed):
    """Fit the four models on a train half, score Δ and AUC on the held-out half."""
    n = len(fr)
    perm = np.random.default_rng(seed).permutation(n)
    te, tr = perm[:n // 2], perm[n // 2:]
    G_te, Y_te = fr["G"].values[te], fr["Y"].values[te].astype(int)
    out = {}
    for name, (feats, tgt) in FAMILY.items():
        m = GradientBoostingClassifier(random_state=seed, **GBT_KW)
        m.fit(fr[feats].values[tr], fr[tgt].values[tr].astype(int))
        p = m.predict_proba(fr[feats].values[te])[:, 1]
        out[name] = {"delta": _dp_gap((p >= 0.5).astype(int), G_te),
                     "auc": float(roc_auc_score(Y_te, p))}
    return out


def c1_grid_point(ps, seeds, n):
    rows = []
    for s in seeds:
        fr = dgp.generate_twin_world(ps, "A", n, s).frame
        r = fit_predict_family(fr, s)
        d_or = r["M_oracle"]["delta"]
        sign = np.sign(r["M_full"]["delta"] - d_or) or 1.0
        ae = {k: float(sign * (v["delta"] - d_or)) for k, v in r.items()}
        rows.append({"ae": ae, "auc": {k: v["auc"] for k, v in r.items()},
                     "delta": {k: v["delta"] for k, v in r.items()}})

    ae_full = np.array([x["ae"]["M_full"] for x in rows])
    ae_comp = np.array([x["ae"]["M_compliant"] for x in rows])
    ae_strict = np.array([x["ae"]["M_strict"] for x in rows])
    valid = ae_full >= EPSILON_EXCESS
    retained = (ae_comp[valid] / ae_full[valid]) if valid.any() else np.array([])
    ext_lift = ae_comp - ae_strict
    auc = {k: float(np.mean([x["auc"][k] for x in rows])) for k in FAMILY}

    def mci(a):
        if len(a) == 0:
            return None, [None, None]
        return float(np.mean(a)), list(_paired_ci(a))

    ret_m, ret_ci = mci(retained)
    ext_m, ext_ci = mci(ext_lift)
    return {
        "proxy_strength": ps, "n_seeds": len(seeds), "n_valid_seeds": int(valid.sum()),
        "retained_excess": ret_m, "retained_excess_ci": ret_ci,
        "external_carrier_lift": ext_m, "external_carrier_lift_ci": ext_ci,
        "adverse_excess_full_mean": float(ae_full.mean()),
        "adverse_excess_compliant_mean": float(ae_comp.mean()),
        "auc_mean": auc,
        "auc_decomp_legit_lost_to_prohibition": auc["M_full"] - auc["M_strict"],
        "auc_decomp_additional_under_compliant": auc["M_full"] - auc["M_compliant"],
    }


def run_c1(proxy_grid, seeds, n, out_path, smoke):
    t0 = time.time()
    points = []
    for ps in proxy_grid:
        pt = c1_grid_point(ps, list(seeds), n)
        points.append(pt)
        re = pt["retained_excess"]
        print(f"[{time.time()-t0:6.1f}s] ps={ps:.2f} | "
              f"retained_excess={re if re is None else f'{re:+.3f}'} "
              f"(valid {pt['n_valid_seeds']}/{pt['n_seeds']}) | "
              f"ext_carrier_lift={pt['external_carrier_lift']:+.4f} | "
              f"ae_full={pt['adverse_excess_full_mean']:+.3f} | "
              f"AUCdecomp legit_lost={pt['auc_decomp_legit_lost_to_prohibition']:+.3f} "
              f"compliant_extra={pt['auc_decomp_additional_under_compliant']:+.3f}", flush=True)
    out_path.write_text(json.dumps({
        "experiment": "compliant-practice disparate impact (V2) -- C1 dose-response",
        "pre_reg_commit": "8fa7992", "smoke": smoke,
        "note_oracle_blind_x6x7": "M_oracle trains on V_named (x0..x5), blind to x6,x7 legit beta "
                                  "(0.60/0.35) per anchor OPEN subtlety -- implemented as written, "
                                  "may inflate measured excess; flag in result note.",
        "points": points}, indent=2))
    print(f"\nWrote {out_path.relative_to(REPO)} ({len(points)} grid points)")


def run_c3(proxy_grid, bisg_grid, seeds, n, out_path, smoke):
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
    out_path.write_text(json.dumps({
        "experiment": "compliant-practice disparate impact (V2) -- C3 path",
        "pre_reg_commit": "8fa7992", "smoke": smoke,
        "estimator": "cross-fitted GBT AUC-lift (KSG/causal-forest backends pending deps)",
        "points": points}, indent=2))
    print(f"\nWrote {out_path.relative_to(REPO)} ({len(points)} grid points)")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mode", choices=["c3", "c1"], default="c3")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--seeds", type=int, default=N_SEEDS_DEFAULT)
    ap.add_argument("--n", type=int, default=N_DEFAULT)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    if args.smoke:
        proxy_grid, bisg_grid, seeds, n = (0.55, 0.70, 0.85), (0.85,), range(6), 3000
    else:
        proxy_grid, bisg_grid, seeds, n = PROXY_GRID, BISG_GRID, range(args.seeds), args.n

    REPO_runs = REPO / "runs"
    REPO_runs.mkdir(exist_ok=True)
    if args.mode == "c1":
        out_path = (Path(args.out).resolve() if args.out else
                    REPO_runs / ("compliant_practice_c1_smoke.json" if args.smoke
                                 else "compliant_practice_c1_2026-05-24.json"))
        run_c1(proxy_grid, seeds, n, out_path, args.smoke)
    else:
        out_path = (Path(args.out).resolve() if args.out else
                    REPO_runs / ("compliant_practice_smoke.json" if args.smoke
                                 else "compliant_practice_c3_2026-05-24.json"))
        run_c3(proxy_grid, bisg_grid, seeds, n, out_path, args.smoke)


if __name__ == "__main__":
    main()
