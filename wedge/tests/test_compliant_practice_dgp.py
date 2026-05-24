"""Structural-smoke / calibration contract for the V2 latent-G twin-world DGP.

Pre-reg (freeze candidate, rev-6):
    docs/superpowers/specs/2026-05-24-compliant-practice-disparate-impact-V2-preregistration-note.md

These are the VERIFY-THEN-FREEZE gate (§2d calibration + §2h pins). They test
substrate validity ONLY — no model family, no rung, no separation_auc, no
prediction is scored here. The forbidden thing (running R1-R6 on the real
substrate) is NOT done.

The construction under test (the matched-joint trick):
    World A (proxy):     c_fresh <- G -> Y     (G latent; Y depends on G)
    World B (legitimate): c_fresh -> Y          (Y drawn from World A's
                                                 observable regression p_obs,
                                                 so Y _||_ G | observables)
Both share P(V_named, c_fresh, Y); only the latent causal status differs.
"""
import importlib.util
import sys
from pathlib import Path

import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import cross_val_score

_spec = importlib.util.spec_from_file_location(
    "fairwash_frontier_dgp",
    Path(__file__).resolve().parents[2] / "scripts" / "fairwash_frontier_dgp.py",
)
dgp = importlib.util.module_from_spec(_spec)
sys.modules["fairwash_frontier_dgp"] = dgp
_spec.loader.exec_module(dgp)

N = 12_000
V_NAMED = [f"x{j}" for j in range(6)]
OBSERVABLE = [f"x{j}" for j in range(8)]  # x0..x7: V_named + declared_proxies are all audit-VISIBLE
CFRESH = ["cfresh_cont", "cfresh_cat", "cfresh_count"]


def _proxy_strength(frame):
    X = frame[CFRESH].values
    G = frame["G"].values
    lr = LogisticRegression(max_iter=200).fit(X, G)
    return roc_auc_score(G, lr.predict_proba(X)[:, 1])


def test_proxy_strength_knob_hits_grid_targets():
    # The dose knob must realize the requested proxy_strength within tolerance.
    for target in (0.55, 0.70, 0.85):
        r = dgp.generate_twin_world(proxy_strength=target, world="A", n=N, seed=0)
        ps = _proxy_strength(r.frame)
        assert abs(ps - target) <= 0.03, f"proxy_strength target {target}, realized {ps:.3f}"


def test_worlds_observationally_matched_without_G():
    # §2d: a without-G discriminator on the full observable joint cannot tell
    # World A from World B (<= 0.56 soft-pass; ideally <= 0.53).
    a = dgp.generate_twin_world(proxy_strength=0.70, world="A", n=N, seed=1)
    b = dgp.generate_twin_world(proxy_strength=0.70, world="B", n=N, seed=1)
    obs = OBSERVABLE + CFRESH + ["Y"]
    Xd = np.vstack([a.frame[obs].values, b.frame[obs].values])
    yd = np.r_[np.zeros(len(a.frame)), np.ones(len(b.frame))]
    clf = GradientBoostingClassifier(max_depth=3, n_estimators=120, subsample=0.8,
                                     random_state=0)
    acc = cross_val_score(clf, Xd, yd, cv=4, scoring="accuracy").mean()
    assert acc <= 0.56, f"without-G discriminator separated the worlds: acc={acc:.3f}"


def test_oracle_separates_via_conditional_dependence():
    # §2d (correct operationalization): the oracle separates the worlds by
    # detecting Y _||_ G | observables -- a CONDITIONAL-INDEPENDENCE property,
    # not per-row classification. In World A, adding G to an observables-only
    # model lifts Y-prediction (Y depends on G beyond obs); in World B, p_obs(obs)
    # was the data-generating mean, so G adds ~nothing.
    from sklearn.model_selection import train_test_split

    def g_lift(world):
        f = dgp.generate_twin_world(proxy_strength=0.70, world=world, n=N, seed=5).frame
        y = f["Y"].values
        obs = f[OBSERVABLE + CFRESH].values
        obsG = f[OBSERVABLE + CFRESH + ["G"]].values
        tr, te = train_test_split(np.arange(len(y)), test_size=0.4, random_state=0)
        def auc(Xc):
            m = GradientBoostingClassifier(max_depth=3, n_estimators=150,
                                           subsample=0.8, random_state=0).fit(Xc[tr], y[tr])
            return roc_auc_score(y[te], m.predict_proba(Xc[te])[:, 1])
        return auc(obsG) - auc(obs)

    lift_A, lift_B = g_lift("A"), g_lift("B")
    assert lift_A >= 0.02, f"World-A G-lift too small ({lift_A:.3f}); G should drive Y beyond obs"
    assert lift_A - lift_B >= 0.02, f"oracle cannot separate: lift_A={lift_A:.3f} lift_B={lift_B:.3f}"


def test_Ghat_bisg_hits_target_auc():
    # §2h rev-6: Ĝ_BISG is G + calibrated noise with AUC(Ĝ_BISG ~ G) ≈ target,
    # and must NOT use c_fresh.
    r = dgp.generate_twin_world(proxy_strength=0.70, world="A", n=N, seed=3,
                                bisg_auc=0.85)
    auc = roc_auc_score(r.frame["G"].values, r.frame["Ghat_bisg"].values)
    assert abs(auc - 0.85) <= 0.03, f"Ĝ_BISG AUC target 0.85, realized {auc:.3f}"


def test_Y_clean_has_less_disparity_than_Y():
    # §0/Item2: Y_clean zeroes the disparate term; its parity gap is below Y's.
    r = dgp.generate_twin_world(proxy_strength=0.70, world="A", n=N, seed=4)
    f = r.frame
    def gap(col):
        return abs(f.loc[f.G == 0, col].mean() - f.loc[f.G == 1, col].mean())
    assert gap("Y_clean") < gap("Y"), "Y_clean is not cleaner than Y"
