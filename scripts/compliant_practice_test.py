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

# V1 harness: reuse its Substrate + rung/band primitives verbatim (C2/C4). It
# self-bootstraps REPO onto sys.path and reuses the dgp already registered above.
_fspec = importlib.util.spec_from_file_location(
    "fairwash_frontier_test", REPO / "scripts" / "fairwash_frontier_test.py")
fft = importlib.util.module_from_spec(_fspec)
sys.modules["fairwash_frontier_test"] = fft
_fspec.loader.exec_module(fft)

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


# ---------------------------------------------------------------------------
# C2 -- does compliant practice PASS the behavioral + set-structural rungs?
# (P-C2 line 22/80: M_compliant passes rungs 1, 2, 3a; prior 0.85. rung 3b is a
# C3 instrument, NOT part of C2.) Reuses the V1 rung/band code verbatim via the
# twin-world -> Substrate adapter; the schemas align (x0..x7 + cfresh, declared
# proxies x6,x7), so no rung is reimplemented.
# ---------------------------------------------------------------------------
def twin_to_substrate(frame, seed):
    """Wrap one twin-world frame in the V1 Substrate shape (0.4/0.1/0.5 split).
    proxies = the DECLARED off-limits proxies (x6,x7) -- NOT c_fresh, which is the
    admissible carrier the audit treats as legitimate. all_protected = proxies + G.
    legit_coeffs from the DGP's frozen beta (used by rung-3b's control null, C3)."""
    n = len(frame)
    ntr, nva = int(0.4 * n), int(0.1 * n)
    train = frame.iloc[:ntr].reset_index(drop=True)
    val = frame.iloc[ntr:ntr + nva].reset_index(drop=True)
    test = frame.iloc[ntr + nva:].reset_index(drop=True)
    legit = {f"x{j}": float(dgp._LEGIT_BETA[j]) for j in range(dgp.N_LEGIT)}
    proxies = [p for p in fft.DECLARED_PROXIES if p in fft.BAND_POOL]   # x6, x7
    return fft.Substrate(train=train, val=val, test=test, legit_coeffs=legit,
                         channel="twinA", proxies=proxies,
                         all_protected=proxies + ["G"], seed=seed)


def fit_compliant(sub, seed):
    """M_compliant: standard GBT on admissible features only (no G, no declared
    proxies). Stash ._feats for the rung primitives' predict path."""
    feats = V_NAMED + CFRESH
    m = GradientBoostingClassifier(random_state=seed, **GBT_KW)
    m.fit(sub.train[feats].values, sub.train["Y"].values.astype(int))
    m._feats = feats
    return m


def c2_cell(ps, seed, n, smoke):
    frame = dgp.generate_twin_world(ps, "A", n, seed).frame
    sub = twin_to_substrate(frame, seed)
    M = fit_compliant(sub, seed)
    train_dec = fft.decisions(M, sub.train)

    band_full = fft.build_surrogate_band(sub.train, train_dec, fft.BAND_POOL, seed=seed)
    prohibited = set(fft.PROHIBITED_IN_POOL)                  # {x6, x7}; G never in pool
    restricted_pool = [f for f in fft.BAND_POOL if f not in prohibited]
    band_restr = fft.build_surrogate_band(sub.train, train_dec, restricted_pool, seed=seed)

    r1 = (fft.rung1_shap_lime(M, sub) if not smoke
          else {"P1_shap_lime_evade": None, "note": "SHAP/LIME skipped in smoke"})
    r2 = fft.rung2_disagreement(band_full, sub, train_dec, fft.BAND_POOL)
    r3a = fft.rung3a(band_full, band_restr, prohibited)

    evade1 = r1.get("P1_shap_lime_evade")
    catch3a = r3a["P3a_reorg_catch"]
    # Binary pass keys on the two rungs with frozen binary criteria (1 evade + 3a
    # no-catch). rung 2 has NO frozen threshold in the V1 instrument -> reported as a
    # continuous diagnostic (documented interpretation owed to the result note, NOT
    # a silent binarization). In smoke r1 is skipped (None) -> behavioral pass is null.
    passes = None if evade1 is None else bool(evade1 and not catch3a)

    G_te = sub.test["G"].values
    delta = fft.dp_gap(fft.decisions(M, sub.test), G_te)
    auc = float(roc_auc_score(sub.test["Y"].values.astype(int), fft.proba(M, sub.test)))
    return {
        "proxy_strength": ps, "seed": seed,
        "rung1_evade": evade1, "rung1_proxies_present": r1.get("proxies_present", []),
        "rung2_disagreement": r2["disagreement"], "rung2_n_members": r2["n_members"],
        "rung3a_catch": catch3a, "rung3a_jaccard_margin": r3a["jaccard"],
        "behavioral_pass": passes,
        "compliant_delta": delta, "compliant_auc": auc,
    }


def run_c2(proxy_grid, seeds, n, out_path, smoke):
    t0 = time.time()
    cells = []
    for ps in proxy_grid:
        for s in seeds:
            c = c2_cell(ps, s, n, smoke)
            cells.append(c)
            print(f"[{time.time()-t0:6.1f}s] ps={ps:.2f} seed={s} | "
                  f"r1_evade={c['rung1_evade']} r2_disag={c['rung2_disagreement']:.3f} "
                  f"r3a_catch={c['rung3a_catch']} j={c['rung3a_jaccard_margin']:.3f} | "
                  f"pass={c['behavioral_pass']} | Δ={c['compliant_delta']:+.3f} "
                  f"auc={c['compliant_auc']:.3f}", flush=True)
    # aggregate pass-rate per ps (P-C2: passes on >=90% of seeds at proxy_strength*)
    by_ps = {}
    for ps in proxy_grid:
        sub = [c for c in cells if c["proxy_strength"] == ps]
        passes = [c["behavioral_pass"] for c in sub if c["behavioral_pass"] is not None]
        js = [c["rung3a_jaccard_margin"] for c in sub]
        by_ps[f"{ps:.2f}"] = {
            "n": len(sub), "n_scored": len(passes),
            "pass_rate": (float(np.mean(passes)) if passes else None),
            "rung3a_jaccard_mean": float(np.mean(js)),
            "rung3a_jaccard_min": float(np.min(js)),
            "rung2_disagreement_mean": float(np.mean([c["rung2_disagreement"] for c in sub])),
        }
    out_path.write_text(json.dumps({
        "experiment": "compliant-practice disparate impact (V2) -- C2 behavioral rungs",
        "pre_reg_commit": "8fa7992", "smoke": smoke,
        "P_C2": "M_compliant passes rungs 1,2,3a on >=90% of seeds at proxy_strength* (prior 0.85)",
        "rung2_note": "rung 2 (disagreement) has no frozen binary threshold in the V1 "
                      "instrument; reported as a continuous diagnostic. behavioral_pass "
                      "keys on rung1 (evade) AND rung3a (no-catch). Documented choice owed "
                      "to the result note -- predictions NOT edited.",
        "by_proxy_strength": by_ps, "cells": cells}, indent=2))
    print(f"\nWrote {out_path.relative_to(REPO)} ({len(cells)} cells)")


# ---------------------------------------------------------------------------
# C4 -- the optimized adversarial upper bound (V2_adv). SECONDARY, intent-by-
# construction (P-C4 line 84, prior 0.60): CMA-ES over the admissible pool to
# MAXIMIZE adverse_excess s.t. rungs 1/2/3a pass AND a dual AUC gate.
#
# DESIGN CHOICE (load-bearing, documented -- the §2f "weighting/subset" lever).
# GBTs are invariant to per-feature monotone scaling, so "feature weighting" of a
# tree ensemble is a literal no-op. The non-vacuous CMA-ES lever over an admissible
# tree model is therefore SAMPLE-REWEIGHTING: sample_weight_i = exp(w . x_std_i)
# over the admissible features (x0..x5 + c_fresh), CMA-ES over w. This is a real,
# intentful analyst move using ONLY admissible inputs (no G, no declared proxies),
# so rungs 1 and 3a pass by the same structural argument as M_compliant (the model
# never touches a prohibited feature). The realized feature subset (what the
# reweighted model splits on) is reported. Feature-scaling excluded for the stated
# tree-invariance reason -- itself a small result-note finding.
# ---------------------------------------------------------------------------
ADMISSIBLE = V_NAMED + CFRESH
GAMMA_C4 = 0.02                     # dual AUC gate tolerance (pre-reg §2h)
C4_POP = 16                         # CMA-ES population (pre-reg §2h)
C4_MAXGEN = 200
C4_CEILING = 5000                   # hard evaluation ceiling
C4_CONV_TOL = 1e-3                  # converge if best-objective improves < tol ...
C4_CONV_PATIENCE = 20               # ... over this many generations
C4_SW_CLIP = 4.0                    # clip w.x_std into [-clip, clip] before exp


def _fit_model(sub, feats, target, seed, sample_weight=None):
    m = GradientBoostingClassifier(random_state=seed, **GBT_KW)
    m.fit(sub.train[feats].values, sub.train[target].values.astype(int),
          sample_weight=sample_weight)
    m._feats = feats
    return m


def _delta_auc(m, sub):
    dec = fft.decisions(m, sub.test)
    delta = fft.dp_gap(dec, sub.test["G"].values)
    auc = float(roc_auc_score(sub.test["Y"].values.astype(int), fft.proba(m, sub.test)))
    return delta, auc


def c4_cell(ps, seed, n, smoke, lever="reweight"):
    import cmaes
    fr = dgp.generate_twin_world(ps, "A", n, seed).frame
    sub = twin_to_substrate(fr, seed)

    # baselines on the shared split
    base = {
        "M_full": _fit_model(sub, OBS + ["G"], "Y", seed),
        "M_compliant": _fit_model(sub, ADMISSIBLE, "Y", seed),
        "M_strict": _fit_model(sub, V_NAMED, "Y", seed),
        "M_oracle": _fit_model(sub, V_NAMED, "Y_clean", seed),
    }
    da = {k: _delta_auc(m, sub) for k, m in base.items()}
    delta_full, auc_full = da["M_full"]
    delta_oracle, _ = da["M_oracle"]
    auc_comp, auc_strict = da["M_compliant"][1], da["M_strict"][1]
    s = float(np.sign(delta_full - delta_oracle)) or 1.0
    ae_full = s * (delta_full - delta_oracle)
    best_adm_auc = max(auc_comp, auc_strict)
    ae_comp = s * (da["M_compliant"][0] - delta_oracle)

    # standardized admissible train matrix (reweighting lever)
    Xtr = sub.train[ADMISSIBLE].values.astype(float)
    mu, sd = Xtr.mean(0), Xtr.std(0) + 1e-9
    Xstd = (Xtr - mu) / sd
    d = len(ADMISSIBLE)
    use_rw = lever in ("reweight", "both")     # sample-reweighting half
    use_sub = lever in ("subset", "both")      # feature-subset half
    dim = d * (int(use_rw) + int(use_sub))

    def _split(w):
        i = 0
        wr = w[i:i + d] if use_rw else None
        i += d if use_rw else 0
        ws = w[i:i + d] if use_sub else None
        return wr, ws

    def make_sw(wr):
        if wr is None:
            return None
        z = np.clip(Xstd @ wr, -C4_SW_CLIP, C4_SW_CLIP)
        sw = np.exp(z - z.max())
        return sw * (len(sw) / sw.sum())                 # mean-1 normalized

    def select_feats(ws):
        if ws is None:
            return list(ADMISSIBLE)
        keep = [ADMISSIBLE[i] for i in range(d) if ws[i] > 0.0]   # sigmoid>0.5 == logit>0
        return keep or [ADMISSIBLE[int(np.argmax(ws))]]           # never empty

    def evaluate(w):
        wr, ws = _split(w)
        feats = select_feats(ws)
        m = _fit_model(sub, feats, "Y", seed, sample_weight=make_sw(wr))
        dd, a = _delta_auc(m, sub)
        return m, s * (dd - delta_oracle), a, feats

    def objective(w):
        # ADMISSIBLE gate enforced as a HARD barrier (§2f's "s.t. dual AUC gate" is a
        # constraint, not a soft preference -- a probe showed a 5x penalty let CMA buy
        # gap by trading through the gate). Infeasible points dominated by any feasible
        # point; deficit term guides CMA back. w=0 == M_compliant is always feasible.
        # FULL gate is structurally infeasible for an admissible-only model -> reported,
        # not enforced (pre-reg-interpretation correction; predictions NOT edited).
        _, ae, a, _ = evaluate(w)
        deficit = (best_adm_auc - GAMMA_C4) - a
        if deficit > 0:
            return float(100.0 + 10.0 * deficit)         # infeasible barrier
        return float(-ae)                                # feasible: maximize gap

    pop = 6 if smoke else C4_POP
    ceiling = 60 if smoke else C4_CEILING
    maxgen = 5 if smoke else C4_MAXGEN
    # Start the subset logits positive (sigmoid(1.5)=0.82 -> all admissible features
    # included == ~M_compliant, a feasible point) so CMA optimizes DOWN from a valid
    # baseline rather than up from the degenerate empty-subset fallback.
    m0 = np.zeros(dim)
    if use_sub:
        m0[(d if use_rw else 0):] = 1.5
    opt = cmaes.CMA(mean=m0, sigma=1.0, seed=seed, population_size=pop)
    best_w, best_obj = m0.copy(), float("inf")
    evals, gen, conv_stall = 0, 0, 0
    while gen < maxgen and evals + opt.population_size <= ceiling:
        sols, improved = [], False
        for _ in range(opt.population_size):
            w = opt.ask()
            val = objective(w)
            sols.append((w, val))
            evals += 1
            if val < best_obj - C4_CONV_TOL:
                best_obj, best_w, improved = val, w, True
        opt.tell(sols)
        gen += 1
        conv_stall = 0 if improved else conv_stall + 1
        if conv_stall >= C4_CONV_PATIENCE or opt.should_stop():
            break

    V2_adv, ae_adv, auc_adv, realized_feats = evaluate(best_w)
    retained = (ae_adv / ae_full) if abs(ae_full) >= EPSILON_EXCESS else None

    # rung validation on the final model (expected structural pass: admissible-only)
    train_dec = fft.decisions(V2_adv, sub.train)
    band_full = fft.build_surrogate_band(sub.train, train_dec, fft.BAND_POOL, seed=seed)
    prohibited = set(fft.PROHIBITED_IN_POOL)
    restricted_pool = [f for f in fft.BAND_POOL if f not in prohibited]
    band_restr = fft.build_surrogate_band(sub.train, train_dec, restricted_pool, seed=seed)
    r1 = (fft.rung1_shap_lime(V2_adv, sub) if not smoke
          else {"P1_shap_lime_evade": None, "note": "SHAP/LIME skipped in smoke"})
    r2 = fft.rung2_disagreement(band_full, sub, train_dec, fft.BAND_POOL)
    r3a = fft.rung3a(band_full, band_restr, prohibited)
    evade1, catch3a = r1.get("P1_shap_lime_evade"), r3a["P3a_reorg_catch"]
    rungs_pass = None if evade1 is None else bool(evade1 and not catch3a)

    realized_subset = [f for f, imp in zip(realized_feats, V2_adv.feature_importances_)
                       if imp > 1e-4]
    gate_full = bool(auc_adv >= auc_full - GAMMA_C4)
    gate_adm = bool(auc_adv >= best_adm_auc - GAMMA_C4)
    # P-C4 success (literal pre-reg text): retained_excess >= 0.80 while passing rungs
    # 1/2/3a, under the feasible (admissible) gate. gate_full reported, NOT required.
    success = (retained is not None and retained >= 0.80
               and (rungs_pass in (True, None)) and gate_adm)
    return {
        "proxy_strength": ps, "seed": seed, "lever": lever,
        "retained_excess_adv": (None if retained is None else float(retained)),
        "ae_adv": float(ae_adv), "ae_full": float(ae_full), "ae_compliant": float(ae_comp),
        "auc_adv": auc_adv, "auc_full": auc_full,
        "auc_compliant": auc_comp, "auc_strict": auc_strict,
        "gate_full_pass": gate_full, "gate_admissible_pass": gate_adm,
        "rung1_evade": evade1, "rung3a_catch": catch3a,
        "rung2_disagreement": r2["disagreement"], "rungs_pass": rungs_pass,
        "realized_subset": realized_subset,
        "cmaes_evals": evals, "cmaes_gens": gen,
        "P_C4_success": bool(success),
    }


def run_c4(proxy_grid, seeds, n, out_path, smoke, lever="reweight"):
    t0 = time.time()
    cells = []
    for ps in proxy_grid:
        for sd in seeds:
            c = c4_cell(ps, sd, n, smoke, lever=lever)
            cells.append(c)
            re = c["retained_excess_adv"]
            print(f"[{time.time()-t0:6.1f}s] ps={ps:.2f} seed={sd} | "
                  f"retained_adv={'None' if re is None else f'{re:+.3f}'} "
                  f"(comp {c['ae_compliant']/c['ae_full']:+.3f}) | "
                  f"auc_adv={c['auc_adv']:.3f} (full {c['auc_full']:.3f}) "
                  f"gates F={c['gate_full_pass']} A={c['gate_admissible_pass']} | "
                  f"rungs={c['rungs_pass']} | success={c['P_C4_success']} | "
                  f"evals={c['cmaes_evals']}", flush=True)
    by_ps = {}
    for ps in proxy_grid:
        sub = [c for c in cells if c["proxy_strength"] == ps]
        ra = [c["retained_excess_adv"] for c in sub if c["retained_excess_adv"] is not None]
        by_ps[f"{ps:.2f}"] = {
            "n": len(sub),
            "retained_excess_adv_mean": (float(np.mean(ra)) if ra else None),
            "retained_excess_adv_ci": (list(_paired_ci(np.array(ra))) if len(ra) > 1 else None),
            "success_rate": float(np.mean([c["P_C4_success"] for c in sub])),
        }
    out_path.write_text(json.dumps({
        "experiment": "compliant-practice disparate impact (V2) -- C4 V2_adv upper bound",
        "pre_reg_commit": "8fa7992", "smoke": smoke, "lever": lever,
        "P_C4": "V2_adv reaches retained_excess >= 0.80 while passing rungs 1/2/3a (prior 0.60)",
        "design_note": "lever = admissible SAMPLE-REWEIGHTING via CMA-ES (feature-scaling "
                       "is vacuous for GBTs); dual AUC gate (full + admissible), gamma=0.02; "
                       "budget pop=16/<=200gen/<=5000eval. Documented choice, predictions NOT edited.",
        "by_proxy_strength": by_ps, "cells": cells}, indent=2))
    print(f"\nWrote {out_path.relative_to(REPO)} ({len(cells)} cells)")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mode", choices=["c3", "c1", "c2", "c4"], default="c3")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--seeds", type=int, default=N_SEEDS_DEFAULT)
    ap.add_argument("--n", type=int, default=N_DEFAULT)
    ap.add_argument("--proxy", type=float, default=None,
                    help="restrict to a single proxy_strength (ps-sharding / single-cell probe)")
    ap.add_argument("--lever", choices=["reweight", "subset", "both"], default="reweight",
                    help="C4 adversary lever: sample-reweight / feature-subset / both (the moat)")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    if args.smoke:
        proxy_grid, bisg_grid, seeds, n = (0.55, 0.70, 0.85), (0.85,), range(6), 3000
    else:
        proxy_grid, bisg_grid, seeds, n = PROXY_GRID, BISG_GRID, range(args.seeds), args.n
        if args.proxy is not None:
            proxy_grid = (args.proxy,)

    REPO_runs = REPO / "runs"
    REPO_runs.mkdir(exist_ok=True)
    if args.mode == "c1":
        out_path = (Path(args.out).resolve() if args.out else
                    REPO_runs / ("compliant_practice_c1_smoke.json" if args.smoke
                                 else "compliant_practice_c1_2026-05-24.json"))
        run_c1(proxy_grid, seeds, n, out_path, args.smoke)
    elif args.mode == "c2":
        # band-building dominates cost (~16k CART fits/band, x2/cell); smoke uses a
        # small 2-ps x 2-seed x small-n grid and skips SHAP/LIME.
        if args.smoke:
            proxy_grid, seeds, n = (0.55, 0.70), range(2), 2000
        out_path = (Path(args.out).resolve() if args.out else
                    REPO_runs / ("compliant_practice_c2_smoke.json" if args.smoke
                                 else "compliant_practice_c2_2026-05-24.json"))
        run_c2(proxy_grid, seeds, n, out_path, args.smoke)
    elif args.mode == "c4":
        if args.smoke:
            proxy_grid, seeds, n = (0.55, 0.70), range(2), 2000
        out_path = (Path(args.out).resolve() if args.out else
                    REPO_runs / ("compliant_practice_c4_smoke.json" if args.smoke
                                 else "compliant_practice_c4_2026-05-24.json"))
        run_c4(proxy_grid, seeds, n, out_path, args.smoke, lever=args.lever)
    else:
        out_path = (Path(args.out).resolve() if args.out else
                    REPO_runs / ("compliant_practice_smoke.json" if args.smoke
                                 else "compliant_practice_c3_2026-05-24.json"))
        run_c3(proxy_grid, bisg_grid, seeds, n, out_path, args.smoke)


if __name__ == "__main__":
    main()
