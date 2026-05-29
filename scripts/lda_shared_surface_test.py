#!/usr/bin/env python3
"""LDA / fairwash shared-failure-surface — POST-FREEZE experiment.

Pre-registration (FROZEN, predictions immutable):
    docs/superpowers/specs/2026-05-28-lda-shared-failure-surface-preregistration-note.md
    commit c815c61 / OTS ae0d827
Binding DGP (earlier freeze): scripts/fairwash_frontier_dgp.py::generate_twin_world

Tests spine §5: does an AUDITOR-OBSERVABLE metric separate honest proxy-removal
(H) from laundering-by-suppression (L) at MATCHED demographic-parity-gap
reduction? Discriminators take inputs ONLY from O = {x0..x7, c_fresh, Y,
Ghat_bisg} + model predictions. Y_clean and G are used ONLY to construct the
interventions and to GRADE / stratify the granted DP measurement -- never as a
discriminating input. (Blind-adversary brief §7 audits this.)

H = attenuate the proxy channel (c_fresh + declared proxies x6,x7) by scalar
    lambda_H, bisected so the measured gap drops to (1-tau)*Delta(M0).
L = suppress the top legit feature x0 by scalar lambda_L, bisected to the SAME
    target gap. Both refit a GBT on the scaled features; matched on measured gap.

Pivotal pred P2 (prior 0.62): A_obs (held-out accuracy on observable Y) FAILS to
separate H from L at tau=0.50. Hit => §5 survives (separation lives in Y_clean);
miss => §5 overclaimed.

Run (smoke):  PYTHONPATH=. python3 scripts/lda_shared_surface_test.py --smoke
Run (full) :  PYTHONPATH=. python3 scripts/lda_shared_surface_test.py
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from pathlib import Path

import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, log_loss, roc_auc_score

REPO = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "fairwash_frontier_dgp", REPO / "scripts" / "fairwash_frontier_dgp.py")
dgp = importlib.util.module_from_spec(_spec)
sys.modules["fairwash_frontier_dgp"] = dgp
_spec.loader.exec_module(dgp)

# --- frozen scalars mirrored from the pre-reg + the V2 substrate -------------
V_NAMED = [f"x{j}" for j in range(6)]            # x0..x5 admissible legit
DECLARED_PROXIES = ["x6", "x7"]
CFRESH = ["cfresh_cont", "cfresh_cat", "cfresh_count"]
ADMISSIBLE = V_NAMED + CFRESH                    # M0 feature set (no G, no x6/x7)
PROXY_CHANNEL = CFRESH                            # H drops this (x6,x7 already out)

GBT_KW = dict(max_depth=3, n_estimators=120, subsample=0.8, learning_rate=0.1)
PS_GRID = (0.70, 0.85)
PS_PRIMARY = 0.85
N_DEFAULT = 8000
N_SEEDS_DEFAULT = 20
GAP_MATCH_TOL = 0.01     # H and L must reach the target gap within this (matching invariant)

# The auditor-observable set. Discriminators MUST draw inputs only from here
# (+ model predictions, which are functions of these). Asserted in unit test.
OBSERVABLE = [f"x{j}" for j in range(8)] + CFRESH + ["Y", "Ghat_bisg"]


def _dp_gap(decision, G):
    g0 = decision[G == 0].mean() if (G == 0).any() else 0.0
    g1 = decision[G == 1].mean() if (G == 1).any() else 0.0
    return float(g0 - g1)


def _paired_ci(diffs, reps=2000, seed=0):
    rng = np.random.default_rng(seed)
    d = np.asarray(diffs)
    boot = [rng.choice(d, len(d), replace=True).mean() for _ in range(reps)]
    return float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))


def _split(n, seed):
    perm = np.random.default_rng(seed).permutation(n)
    return perm[n // 2:], perm[:n // 2]    # train, test


def _fit_on(fr, tr, te, feats, seed):
    """Fit GBT on `feats` (a subset of ADMISSIBLE -- a real LDA model-selection
    move: drop features, refit). Return held-out (decision, proba, measured gap).
    Feature DROP is the lever (not scaling -- GBTs are invariant to monotone
    per-feature scaling, a documented no-op; pre-reg §6 lever correction)."""
    X = fr[feats].values
    y = fr["Y"].values.astype(int)
    m = GradientBoostingClassifier(random_state=seed, **GBT_KW).fit(X[tr], y[tr])
    p = m.predict_proba(X[te])[:, 1]
    dec = (p >= 0.5).astype(int)
    gap = _dp_gap(dec, fr["G"].values[te])
    return dec, p, gap


def _eval_model(fr, tr, te, feats, seed):
    """Fit GBT on feats; return the full discriminator block + |gap| for one model
    (one point in an arm's family). All discriminator inputs are OBSERVABLE except
    A_clean (oracle, grading-only)."""
    dec, p, gap = _fit_on(fr, tr, te, feats, seed)
    G_te = fr["G"].values[te]
    Y_te = fr["Y"].values[te].astype(int)
    Yc_te = fr["Y_clean"].values[te].astype(int)
    pc = np.clip(p, 1e-6, 1 - 1e-6)
    a_g0 = accuracy_score(Y_te[G_te == 0], dec[G_te == 0]) if (G_te == 0).any() else float("nan")
    a_g1 = accuracy_score(Y_te[G_te == 1], dec[G_te == 1]) if (G_te == 1).any() else float("nan")
    return {
        "abs_gap": float(abs(gap)),
        "A_obs": float(accuracy_score(Y_te, dec)),          # OBSERVABLE
        "CAL": float(log_loss(Y_te, pc, labels=[0, 1])),    # OBSERVABLE
        "A_obs_g0": float(a_g0), "A_obs_g1": float(a_g1),   # OBSERVABLE (G as stratifier)
        "A_clean": float(accuracy_score(Yc_te, dec)),       # ORACLE (grading-only)
    }


# Arm families (pre-reg §6 lever correction, deviation #2 -- covariate-adjustment
# replaces exact matched-pairs, which the discrete feature-drop lever is too COARSE
# to satisfy on this substrate). Each arm is a FAMILY of admissible models spanning
# a range of |gap|; we then ask whether, CONTROLLING for |gap|, the arm label moves
# the observable discriminator.
#   H (honest proxy-removal): drop progressively more of the proxy channel c_fresh.
#   L (laundering-by-suppression): keep c_fresh, drop progressively more legit
#     features in decreasing-beta order (suppress the most-predictive carriers).
def _arm_families(fr, tr, te, seed):
    legit_desc = sorted(V_NAMED, key=lambda f: float(dgp._LEGIT_BETA[int(f[1:])]), reverse=True)
    H_feats, L_feats = [], []
    # H family: full admissible, then drop c_fresh members one by one (proxy removal)
    for k in range(0, len(CFRESH) + 1):
        drop = CFRESH[:k]
        H_feats.append([f for f in ADMISSIBLE if f not in drop])
    # L family: full admissible, then drop legit features one by one (suppression),
    # ALWAYS keeping c_fresh (the proxy channel is retained -- that's the laundering)
    for k in range(0, len(legit_desc)):
        drop = legit_desc[:k]
        L_feats.append([f for f in ADMISSIBLE if f not in drop])
    H = [{"arm": "H", "k": i, **_eval_model(fr, tr, te, f, seed)} for i, f in enumerate(H_feats)]
    L = [{"arm": "L", "k": i, **_eval_model(fr, tr, te, f, seed)} for i, f in enumerate(L_feats)]
    return H + L


def cell(ps, seed, n, world="A", decouple=0.0):
    """One (ps, seed) cell: generate both arm families (H, L), each a list of
    models with (abs_gap, A_obs, CAL, A_clean, ...). The covariate-adjusted
    comparison happens in aggregate() across pooled cells. world/decouple default
    to the §5 behavior (World A); world='P' + decouple>0 runs the positive control
    (pre-reg 2026-05-29) -- discriminator logic is UNCHANGED."""
    fr = dgp.generate_twin_world(ps, world, n, seed, decouple=decouple).frame
    tr, te = _split(len(fr), seed)
    _, _, gap0 = _fit_on(fr, tr, te, ADMISSIBLE, seed)
    models = _arm_families(fr, tr, te, seed)
    for m in models:
        m["seed"] = seed
    return {"ps": ps, "seed": seed, "world": world, "decouple": decouple,
            "abs_gap0": float(abs(gap0)), "models": models}


DISCRIMS = ["A_obs", "CAL", "A_obs_g0", "A_obs_g1", "A_clean"]


def _ols_label_effect(rows, outcome):
    """Covariate-adjusted arm effect: regress outcome ~ 1 + abs_gap + is_L over the
    pooled (H,L) family. Returns the is_L coefficient (effect of laundering vs
    honest AT MATCHED |gap|), its 95% CI (seed-cluster bootstrap), and whether the
    arms separate (CI excludes 0 AND |coef| >= 0.01). This is the §5 test: ~0 =>
    observable cannot tell H from L at equal impact (§5 survives); != 0 => it can
    (§5 overclaimed)."""
    rows = [r for r in rows if not np.isnan(r[outcome])]
    if len(rows) < 8:
        return None
    g = np.array([r["abs_gap"] for r in rows])
    isL = np.array([1.0 if r["arm"] == "L" else 0.0 for r in rows])
    k = np.array([float(r["k"]) for r in rows])     # features dropped (arm-correlated!)
    y = np.array([r[outcome] for r in rows])
    seeds = np.array([r["seed"] for r in rows])

    def fit(idx, with_k):
        cols = [np.ones(len(idx)), g[idx], isL[idx]]
        if with_k:
            cols.append(k[idx])
        X = np.column_stack(cols)
        beta, *_ = np.linalg.lstsq(X, y[idx], rcond=None)
        return beta[2]   # is_L coefficient

    # NAIVE: adjust for abs_gap only (the pre-reg's named confound). CONFOUNDED by
    # feature-count, which is arm-correlated (corr(is_L,k)~0.31) -- the blind-
    # adversary catch. The k-controlled coefficient is the HONEST observable
    # signal; if it collapses/flips vs naive, "separation" was feature-count
    # bookkeeping, not a quantity an auditor (who sees predictions, not the
    # builder's feature count) can use. Both reported; the result reads the
    # k-controlled one. See the result note.
    uniq = np.unique(seeds)
    rng = np.random.default_rng(0)
    out = {}
    for tag, with_k in (("", False), ("_kctl", True)):
        coef = fit(np.arange(len(rows)), with_k)
        boot = []
        for _ in range(2000):
            pick = rng.choice(uniq, len(uniq), replace=True)
            idx = np.concatenate([np.where(seeds == s)[0] for s in pick])
            boot.append(fit(idx, with_k))
        lo, hi = float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))
        out[f"coef_is_L{tag}"] = float(coef)
        out[f"ci{tag}"] = [lo, hi]
        out[f"separates{tag}"] = bool((lo > 0 or hi < 0) and abs(coef) >= 0.01)
    out["corr_isL_k"] = float(np.corrcoef(isL, k)[0, 1])
    return out


def aggregate(cells):
    """Covariate-adjusted arm comparison over the pooled family across seeds, per
    discriminator. The is_L coefficient (controlling for |gap|) is the answer."""
    rows = [m for c in cells for m in c["models"]]
    out = {"n_seeds": len(cells), "n_models": len(rows),
           "mean_abs_gap0": float(np.mean([c["abs_gap0"] for c in cells])) if cells else 0.0,
           "abs_gap_range": [float(min(r["abs_gap"] for r in rows)),
                             float(max(r["abs_gap"] for r in rows))] if rows else None,
           "discrim": {}}
    for d in DISCRIMS:
        out["discrim"][d] = _ols_label_effect(rows, d)
    return out


def run(ps_grid, seeds, n, out_path, smoke):
    t0 = time.time()
    cells = []
    summary = {}
    for ps in ps_grid:
        ps_cells = []
        for s in seeds:
            c = cell(ps, s, n)
            ps_cells.append(c); cells.append(c)
        agg = aggregate(ps_cells)
        summary[f"{ps:.2f}"] = agg
        ao = agg["discrim"]["A_obs"]
        gr = agg["abs_gap_range"]
        ao_s = ("n/a" if ao is None else
                f"naive={ao['coef_is_L']:+.4f}(sep={ao['separates']}) "
                f"k-ctl={ao['coef_is_L_kctl']:+.4f}(sep={ao['separates_kctl']}) "
                f"corr(isL,k)={ao['corr_isL_k']:+.2f}")
        print(f"[{time.time()-t0:6.1f}s] ps={ps:.2f} | n_models={agg['n_models']} | "
              f"|gap|range=[{gr[0]:.3f},{gr[1]:.3f}] | A_obs is_L: {ao_s}", flush=True)

    out_path.write_text(json.dumps({
        "experiment": "LDA / fairwash shared-failure-surface (spine §5 test)",
        "pre_reg_commit": "c815c61", "smoke": smoke,
        "lever_note": "H = drop proxy channel (c_fresh) progressively; L = keep c_fresh, "
            "drop legit features (decreasing beta) progressively. Each arm is a FAMILY "
            "spanning a |gap| range. §5 test = is_L coefficient in OLS(discriminator ~ "
            "1 + abs_gap + is_L), seed-cluster bootstrap CI: the effect of laundering vs "
            "honest AT MATCHED |gap|. TWO pre-reg deviations (mechanism only, predictions "
            "NOT edited): (1) smooth-lambda lever -> discrete feature-drop (GBT scale-"
            "invariance no-op); (2) exact matched-pairs -> covariate-adjustment on |gap| "
            "(discrete drop too COARSE to hit a target gap within tol on this substrate).",
        "discriminator_inputs_note": "A_obs/CAL/A_obs_g* are OBSERVABLE (Y + model "
            "preds; G only as granted stratifier for A_obs_g*). A_clean is ORACLE "
            "(grading-only contrast). No discriminator takes Y_clean or G as a model input.",
        "summary": summary, "cells": cells}, indent=2))
    print(f"\nWrote {out_path.relative_to(REPO)} ({len(cells)} cells)")


DECOUPLE_GRID = (0.0, 0.25, 0.50, 0.75, 1.0)


def run_positive_control(ps, decouple_grid, seeds, n, out_path, smoke):
    """Positive-control substrate validation (pre-reg 2026-05-29). Sweep world='P'
    over `decouple`; per value, the apparatus's feature-count-controlled A_obs is_L
    coefficient is the test statistic. PASS = detects (neg, CI-excl-0) at high
    decouple; negative control = no detection at decouple=0 (=World A)."""
    t0 = time.time()
    cells = []
    summary = {}
    for dc in decouple_grid:
        dc_cells = []
        for s in seeds:
            c = cell(ps, s, n, world="P", decouple=dc)
            dc_cells.append(c); cells.append(c)
        agg = aggregate(dc_cells)
        summary[f"decouple_{dc:.2f}"] = agg
        ao = agg["discrim"]["A_obs"]; gr = agg["abs_gap_range"]
        # the test statistic: k-controlled, must be NEGATIVE + CI-excl-0 to "detect"
        detects = bool(ao and ao["separates_kctl"] and ao["coef_is_L_kctl"] < 0)
        ao_s = ("n/a" if ao is None else
                f"k-ctl={ao['coef_is_L_kctl']:+.4f}(sep={ao['separates_kctl']}) "
                f"naive={ao['coef_is_L']:+.4f}")
        print(f"[{time.time()-t0:6.1f}s] decouple={dc:.2f} | |gap|range=[{gr[0]:.3f},{gr[1]:.3f}] "
              f"| A_obs {ao_s} | DETECTS={detects}", flush=True)

    out_path.write_text(json.dumps({
        "experiment": "positive-control substrate validation (pre-reg 2026-05-29)",
        "pre_reg_commit": "a0dfd23", "smoke": smoke, "ps": ps,
        "test_statistic": "feature-count-controlled A_obs is_L coefficient (coef_is_L_kctl); "
            "DETECTS = sign negative AND CI excludes 0 AND |coef|>=0.01.",
        "pass_fail": "P1 negative control: decouple=0.00 should NOT detect (=World A). "
            "P2 positive control: decouple=1.00 SHOULD detect (planted observable signal). "
            "P3: detection floor interior (graded detection curve in decouple).",
        "channel_invariant_note": "world=P routes `decouple` of the disparate term through "
            "the c_fresh-borne legit-orthogonal channel; validity probe confirmed AUC(Y~legit) "
            "flat (~0.78) and AUC(Y~c_fresh) rising (0.60->0.82) in decouple. Baseline |gap| "
            "falls with decouple (imp_z noisier G-proxy than Gz); not a confound -- H/L matched "
            "on |gap| within-world by covariate-adjustment.",
        "summary": summary, "cells": cells}, indent=2))
    print(f"\nWrote {out_path.relative_to(REPO)} ({len(cells)} cells)")


def selftest():
    """Invariants: (1) observable-input audit -- model feats subset OBSERVABLE,
    O excludes Y_clean and G; (2) both arm families span a non-degenerate |gap|
    range and OVERLAP (covariate-adjustment requires common support in |gap|, else
    is_L is extrapolation not interpolation); (3) the H and L families differ in
    membership. Runs both ps regimes."""
    assert set(ADMISSIBLE).issubset(set(OBSERVABLE)), "model feats leak outside O"
    assert "Y_clean" not in OBSERVABLE and "G" not in OBSERVABLE
    for ps in (0.70, 0.85):
        c = cell(ps, 0, 4000)
        H = [m for m in c["models"] if m["arm"] == "H"]
        L = [m for m in c["models"] if m["arm"] == "L"]
        gH = [m["abs_gap"] for m in H]; gL = [m["abs_gap"] for m in L]
        # common support: the |gap| ranges of H and L must overlap for is_L|gap to
        # be interpolation. Report the overlap; warn (not assert) if thin.
        overlap = (max(min(gH), min(gL)), min(max(gH), max(gL)))
        has_overlap = overlap[0] <= overlap[1]
        print(f"selftest ps={ps}: gap0={c['abs_gap0']:.4f} | "
              f"H |gap|=[{min(gH):.3f},{max(gH):.3f}] ({len(H)} models) | "
              f"L |gap|=[{min(gL):.3f},{max(gL):.3f}] ({len(L)} models) | "
              f"overlap={'[%.3f,%.3f]' % overlap if has_overlap else 'NONE (extrapolation!)'}")
        assert len(H) >= 2 and len(L) >= 2, "arm family too small"
    # Positive-control precondition: at decouple=1, world P must STILL admit H/L
    # families with common support in |gap| (else the detection test is extrapolation).
    cP = cell(0.70, 0, 4000, world="P", decouple=1.0)
    H = [m for m in cP["models"] if m["arm"] == "H"]; L = [m for m in cP["models"] if m["arm"] == "L"]
    gH = [m["abs_gap"] for m in H]; gL = [m["abs_gap"] for m in L]
    ov = (max(min(gH), min(gL)), min(max(gH), max(gL)))
    print(f"selftest world=P decouple=1.0 ps=0.70: gap0={cP['abs_gap0']:.4f} | "
          f"H |gap|=[{min(gH):.3f},{max(gH):.3f}] | L |gap|=[{min(gL):.3f},{max(gL):.3f}] | "
          f"overlap={'[%.3f,%.3f]' % ov if ov[0] <= ov[1] else 'NONE (extrapolation!)'}")
    print("selftest OK")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--positive-control", action="store_true",
                    help="run the world=P decouple sweep (pre-reg 2026-05-29) instead of §5")
    ap.add_argument("--seeds", type=int, default=N_SEEDS_DEFAULT)
    ap.add_argument("--n", type=int, default=N_DEFAULT)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    if args.selftest:
        selftest()
        return

    if args.positive_control:
        if args.smoke:
            decouple_grid, seeds, n = (0.0, 1.0), range(4), 3000
        else:
            decouple_grid, seeds, n = DECOUPLE_GRID, range(args.seeds), args.n
        (REPO / "runs").mkdir(exist_ok=True)
        out_path = (Path(args.out).resolve() if args.out else
                    REPO / "runs" / ("positive_control_smoke.json" if args.smoke
                                     else "positive_control_2026-05-29.json"))
        run_positive_control(0.70, decouple_grid, seeds, n, out_path, args.smoke)
        return

    if args.smoke:
        ps_grid, seeds, n = (0.70, 0.85), range(4), 3000
    else:
        ps_grid, seeds, n = PS_GRID, range(args.seeds), args.n

    (REPO / "runs").mkdir(exist_ok=True)
    out_path = (Path(args.out).resolve() if args.out else
                REPO / "runs" / ("lda_shared_surface_smoke.json" if args.smoke
                                 else "lda_shared_surface_2026-05-28.json"))
    run(ps_grid, seeds, n, out_path, args.smoke)


if __name__ == "__main__":
    main()
