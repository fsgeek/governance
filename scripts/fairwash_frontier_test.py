#!/usr/bin/env python3
"""Fairwashing-vs-reorganization frontier experiment (the synthetic 1-2 punch).

Pre-registration (FROZEN, predictions immutable):
    docs/superpowers/specs/2026-05-23-fairwash-reorganization-frontier-preregistration-note.md
    commit daf032d / OTS 9e8abe7

Binding DGP spec (frozen in the same commit):
    scripts/fairwash_frontier_dgp.py

This script is the POST-FREEZE experiment. It fits the discriminatory model M,
applies the fairwashing transforms T_naive / T_adv, builds the published Rashomon
ensemble, and scores the four audit rungs + the remediated-control family.

ARCHITECTURE DECISION (where the frozen spec underdetermined the model<->band
coupling; resolved by §2f rung-3b's "judges the SUBMITTED model on its own
structure"):
    The published Rashomon ensemble is a policy-legible SURROGATE of the
    submitted model's decisions -- build_refinement_band over (audit-X on
    V_named u V_ext, label = T(M)'s 0/1 decisions). The literal "(data, pool)"
    reading (band on the true Y, independent of T(M)) is rejected: an
    independent band cannot see T(M)'s laundering, which would make rungs 2/3a
    untestable. So:
        rung 1 (SHAP/LIME) -> on T(M) directly
        rung 2 (disagreement) -> cross-member 0/1 disagreement of the surrogate band
        rung 3a (set reorganization) -> variant_A vs variant_B surrogate bands
        rung 3b (weight-aware oracle) -> c_fresh realized importance in T(M)
    This is the load-bearing interpretive choice; documented here, not buried.

NOTE: predictions/priors/numerics live in the pre-reg and are NOT re-decided
here. Frozen scalars are read from the DGP module + mirrored from §2h below.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from dataclasses import dataclass, asdict, field
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from wedge.refinement_set import build_refinement_band, RefinementMember, refit_member  # noqa: E402


def _load_by_path(mod_name: str, rel: str):
    if mod_name in sys.modules:
        return sys.modules[mod_name]
    spec = importlib.util.spec_from_file_location(mod_name, REPO_ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod  # register before exec so @dataclass can resolve __module__
    spec.loader.exec_module(mod)
    return mod


dgp = _load_by_path("fairwash_frontier_dgp", "scripts/fairwash_frontier_dgp.py")
sm = _load_by_path("silence_manufacture_test", "scripts/silence_manufacture_test.py")
restrict = sm.restrict
classify_reorganized = sm.classify_reorganized

# --- Frozen scalars (pre-reg §2h; DGP scalars come from the dgp module) ------
N_TRAIN, N_VAL, N_TEST = dgp.N_TRAIN, dgp.N_VAL, dgp.N_TEST
CHANNELS = dgp.CHANNELS
DELTA_MIN = dgp.DELTA_MIN                  # 0.10
AUC_LOW, AUC_HIGH = 0.78, 0.90             # compliant-model AUC band
GAMMA = 0.02                               # AUC tolerance for T
RETENTION_FLOOR = 0.05                     # below this = debiasing, not laundering
KILL_RETENTION = 0.50                      # killing-condition retention
N_SEEDS = 40
EPSILON = 0.02                             # ensemble e-AUC band
LEAF_MINS = (25, 50, 100)
DEPTHS = (1, 2, 3)
MAX_SUBSET_SIZE = 7                        # lossless for depth<=3 (2^3-1)
RUNG1_TOPK = 5
RUNG1_PHI = 0.02                           # attribution floor (frozen in code)
N_BG = 100                                 # SHAP/LIME background
SHAP_NSAMPLES = 2048
RUNG3A_JTHRESH = 0.4
RUNG3B_NULL_PCT = 95                       # flag if realized importance > qth pct of null
ALPHA_FP = 0.05                            # family-wide control false-positive ceiling
R_BINS = tuple(round(x, 3) for x in np.linspace(0.05, 1.0, 10))  # operating curve

LEGIT_FEATURES = [f"x{j}" for j in range(dgp.N_LEGIT)]
CFRESH_FEATURES = ["cfresh_cont", "cfresh_cat", "cfresh_count"]
# PROVISIONAL substrate roles (verification stage, pending the amendment freeze).
# declared_proxies = the few in-pool features the policy names as off-limits proxies;
# the fresh-carrier threat routes onto carriers OUTSIDE this set. Fixed, NOT derived
# from DGP wiring (deriving it = the case-1 trivial collapse the smoke exposed).
DECLARED_PROXIES = ["x6", "x7"]
V_NAMED = [f for f in LEGIT_FEATURES if f not in DECLARED_PROXIES]
V_EXT = list(CFRESH_FEATURES)
BAND_POOL = list(LEGIT_FEATURES) + V_EXT           # all observable features are in the audit pool
PROHIBITED_IN_POOL = list(DECLARED_PROXIES)        # G is protected -> never in the pool


# ---------------------------------------------------------------------------
# Substrate / model fitting
# ---------------------------------------------------------------------------
@dataclass
class Substrate:
    train: pd.DataFrame
    val: pd.DataFrame
    test: pd.DataFrame
    legit_coeffs: dict[str, float]
    channel: str
    proxies: list[str]          # DGP-declared legit features wired to G (band-pool members)
    all_protected: list[str]    # proxies + G (the rung-1 "protected proxy" set)
    seed: int


def make_substrate(channel: str, seed: int, *, n_total: int | None = None) -> Substrate:
    n = n_total if n_total is not None else (N_TRAIN + N_VAL + N_TEST)
    r = dgp.generate(channel, n=n, seed=seed)
    f = r.frame
    # split sizes scale with n_total for smoke runs
    if n_total is None:
        ntr, nva = N_TRAIN, N_VAL
    else:
        ntr, nva = int(0.4 * n), int(0.1 * n)
    train = f.iloc[:ntr].reset_index(drop=True)
    val = f.iloc[ntr:ntr + nva].reset_index(drop=True)
    test = f.iloc[ntr + nva:].reset_index(drop=True)
    proxies = []
    if r.proxy_feature:
        proxies.append(r.proxy_feature)
    if r.interaction_feature:
        proxies.append(r.interaction_feature)
    proxies.extend(r.distributed_features)
    proxies = [p for p in proxies if p in BAND_POOL]
    return Substrate(train=train, val=val, test=test, legit_coeffs=r.legitimate_coefficients,
                     channel=channel, proxies=proxies, all_protected=proxies + ["G"], seed=seed)


def _gbt(seed: int) -> GradientBoostingClassifier:
    return GradientBoostingClassifier(max_depth=3, n_estimators=150, learning_rate=0.1,
                                      subsample=0.8, random_state=seed)


def fit_discriminatory_M(sub: Substrate) -> GradientBoostingClassifier:
    """The deployed discriminatory model: uses the legitimate features AND G
    (overt access to protected status -- the disparate channel is reproducible)."""
    feats = LEGIT_FEATURES + ["G"]
    m = _gbt(sub.seed)
    m.fit(sub.train[feats].values, sub.train["Y"].values)
    m._feats = feats  # noqa: SLF001 -- stash the feature order for prediction
    return m


def decisions(model, frame: pd.DataFrame) -> np.ndarray:
    feats = model._feats  # noqa: SLF001
    proba = model.predict_proba(frame[feats].values)[:, 1]
    return (proba >= 0.5).astype(int)


def proba(model, frame: pd.DataFrame) -> np.ndarray:
    feats = model._feats  # noqa: SLF001
    return model.predict_proba(frame[feats].values)[:, 1]


def dp_gap(decision: np.ndarray, G: np.ndarray) -> float:
    """Demographic-parity gap on a 0/1 decision vector: P(d=1|G=0)-P(d=1|G=1)."""
    g0 = decision[G == 0].mean() if (G == 0).any() else 0.0
    g1 = decision[G == 1].mean() if (G == 1).any() else 0.0
    return float(g0 - g1)


def auc_of(model, frame: pd.DataFrame) -> float:
    return float(roc_auc_score(frame["Y"].values, proba(model, frame)))


# ---------------------------------------------------------------------------
# Fairwashing transforms
# ---------------------------------------------------------------------------
@dataclass
class TransformResult:
    model: object
    feats: list[str]
    r_retained: float
    auc: float
    delta: float
    label: str
    routing: dict[str, float] = field(default_factory=dict)
    valid: bool = True
    note: str = ""


def _fit_surrogate(train: pd.DataFrame, target: np.ndarray, feats: list[str],
                   seed: int):
    m = _gbt(seed)
    m.fit(train[feats].values, target)
    m._feats = feats  # noqa: SLF001
    return m


class LaunderedModel:
    """A fairwashed model: a legitimate base + the disparate residual rerouted
    through admissible carriers, p = clip(base_p + Sum_k w_k * corr_k(carrier_k)).

    This is §2d's two-step laundering made explicit: the base reproduces the
    legitimate decision shape; the per-carrier correctors carry the G-driven
    residual the base drops, so the disparate effect survives on *admissible*
    features (c_fresh) rather than on G or the named proxies. Weights distribute
    the residual across carriers (uniform = naive; CMA-ES-optimized = adversarial).
    """

    def __init__(self, base, base_feats, correctors, carrier_feats, weights, joint=False):
        self.base = base
        self.base_feats = list(base_feats)
        self.correctors = list(correctors)
        self.carrier_feats = list(carrier_feats)
        self.weights = np.asarray(weights, dtype=float)
        self.joint = joint        # joint=True: ONE multivariate corrector over all carriers
        self._feats = list(self.base_feats) + [c for c in self.carrier_feats
                                               if c not in self.base_feats]
        self._bidx = [self._feats.index(f) for f in self.base_feats]
        self._cidx = [self._feats.index(f) for f in self.carrier_feats]

    def _p(self, arr):
        arr = np.asarray(arr, dtype=float)
        p = self.base.predict_proba(arr[:, self._bidx])[:, 1]
        if self.joint:
            # single corrector sees ALL carrier columns jointly; weights[0] = scalar gain
            p = p + self.weights[0] * self.correctors[0].predict(arr[:, self._cidx])
        else:
            for k, ci in enumerate(self._cidx):
                p = p + self.weights[k] * self.correctors[k].predict(arr[:, [ci]])
        return np.clip(p, 1e-6, 1 - 1e-6)

    def predict_proba(self, arr):
        p = self._p(arr)
        return np.column_stack([1 - p, p])

    @property
    def feature_importances_(self):
        """Contribution-magnitude importance over self._feats: the base's split
        importances (scaled by its output spread) plus each carrier's weighted
        corrector spread. c_fresh shows high importance exactly when it carries
        the laundered residual -- the rung-3b signal."""
        imp = {f: 0.0 for f in self._feats}
        bspread = float(np.std(getattr(self, "_base_p_cache", [0.0])))
        bi = self.base.feature_importances_
        for f, v in zip(self.base_feats, bi):
            imp[f] += float(v) * (bspread + 1e-9)
        if self.joint:
            # distribute the joint corrector's own split-importances across carriers,
            # scaled by the gain * the joint corrector's output spread
            jspread = self.weights[0] * float(getattr(self, "_carr_spread", [0.0])[0])
            for c, v in zip(self.carrier_feats, self.correctors[0].feature_importances_):
                imp[c] += float(v) * jspread
        else:
            for k, c in enumerate(self.carrier_feats):
                spread = self.weights[k] * float(getattr(self, "_carr_spread", [0.0] * len(self.carrier_feats))[k])
                imp[c] += spread
        arr = np.array([imp[f] for f in self._feats])
        s = arr.sum()
        return arr / s if s > 0 else arr


def _build_laundered(M, sub: Substrate, base_feats, carrier_feats, weights,
                     corrector_mode="univariate"):
    """corrector_mode='univariate' (default, byte-identical): one low-capacity GBR per
    carrier (depth-2/80), residual SPREAD across carriers (the D4-evasion architecture).
    corrector_mode='joint': ONE higher-capacity GBR (depth-3/150) over ALL carriers
    jointly -- the capacity probe for whether the laundering's dominance vs reweighting
    is an artifact of the univariate parameterization."""
    from sklearn.ensemble import GradientBoostingRegressor
    tr = sub.train
    target = decisions(M, tr)
    base = _gbt(sub.seed)
    base.fit(tr[base_feats].values, target)
    base_p = base.predict_proba(tr[base_feats].values)[:, 1]
    residual = proba(M, tr) - base_p
    if corrector_mode == "joint":
        reg = GradientBoostingRegressor(max_depth=3, n_estimators=150, random_state=sub.seed)
        reg.fit(tr[carrier_feats].values, residual)
        spreads = [float(np.std(reg.predict(tr[carrier_feats].values)))]
        T = LaunderedModel(base, base_feats, [reg], carrier_feats, weights, joint=True)
    else:
        correctors, spreads = [], []
        for c in carrier_feats:
            reg = GradientBoostingRegressor(max_depth=2, n_estimators=80, random_state=sub.seed)
            reg.fit(tr[[c]].values, residual)
            correctors.append(reg)
            spreads.append(float(np.std(reg.predict(tr[[c]].values))))
        T = LaunderedModel(base, base_feats, correctors, carrier_feats, weights)
    T._base_p_cache = base_p          # noqa: SLF001 -- for importance scaling
    T._carr_spread = spreads          # noqa: SLF001
    return T


def transform_naive(M, sub: Substrate) -> TransformResult:
    """T_naive: legitimate base (legit minus named proxies) + uniform residual
    rerouting onto the c_fresh portfolio. Non-adaptive: does not optimize against
    any rung."""
    base_feats = [f for f in LEGIT_FEATURES if f not in sub.proxies]
    carrier_feats = list(CFRESH_FEATURES)
    weights = np.ones(len(carrier_feats))
    T = _build_laundered(M, sub, base_feats, carrier_feats, weights)
    return _score_transform(T, M, sub, "T_naive")


def _score_transform(T, M, sub: Substrate, label: str, routing=None) -> TransformResult:
    d_M = dp_gap(decisions(M, sub.test), sub.test["G"].values)
    d_T = dp_gap(decisions(T, sub.test), sub.test["G"].values)
    r = float(d_T / d_M) if abs(d_M) > 1e-9 else 0.0
    auc = auc_of(T, sub.test)
    return TransformResult(model=T, feats=T._feats, r_retained=r, auc=auc, delta=d_T,  # noqa: SLF001
                           label=label, routing=routing or {})


def transform_adv(M, sub: Substrate, *, patience_W: int = 50, ceiling: int = 1000,
                  auc_M: float | None = None) -> TransformResult:
    """T_adv: CMA-ES over a routing vector w on the admissible carriers, optimized
    white-box to drive rung-3b (c_fresh realized importance) below the legitimate
    null while holding retained effect r and AUG. Distributing the laundered
    signal across carriers is the D4-frontier evasion. 3a is auto-evaded (routing
    stays on admissible carriers, prohibited set untouched).

    Implementation: the laundering target re-projects M's G-aligned decision
    component onto admissible carriers weighted by softmax(w); a surrogate is
    refit to that target. Objective minimizes max c_fresh permutation-importance
    while penalizing retention shortfall and AUC violation. cmaes is used per the
    frozen §2d search-method pin.
    """
    import cmaes

    base_feats = [f for f in LEGIT_FEATURES if f not in sub.proxies]
    # carriers: c_fresh + low-coefficient admissible legit features, so the
    # residual can be SPREAD (the D4-frontier move that thins per-carrier weight).
    low_coef = sorted(base_feats, key=lambda f: sub.legit_coeffs.get(f, 0.0))[:2]
    carrier_feats = list(CFRESH_FEATURES) + low_coef

    def build_T(w: np.ndarray):
        sw = np.exp(w - w.max()); sw = sw / sw.sum()
        T = _build_laundered(M, sub, base_feats, carrier_feats, sw)
        return T, sw

    def objective(w: np.ndarray) -> float:
        T, _ = build_T(w)
        res = _score_transform(T, M, sub, "T_adv_trial")
        pen = 0.0
        if res.r_retained < RETENTION_FLOOR:
            pen += 10.0 * (RETENTION_FLOOR - res.r_retained)
        if auc_M is not None and res.auc < auc_M - GAMMA:
            pen += 10.0 * (auc_M - GAMMA - res.auc)
        cfresh_imp = _cfresh_importance(T, sub, estimator="split_gain")
        max_cf = max(cfresh_imp.values()) if cfresh_imp else 0.0
        # minimize max c_fresh importance (evade rung 3b) while maximizing retention
        return float(max_cf - 0.5 * res.r_retained + pen)

    dim = len(carrier_feats)
    opt = cmaes.CMA(mean=np.zeros(dim), sigma=1.0, seed=sub.seed)
    best_w, best_obj, best_r = np.zeros(dim), float("inf"), 0.0
    stall, step = 0, 0
    # Never START a generation that would push evaluations past the safety ceiling,
    # so the reported step count respects the frozen budget exactly.
    while stall < patience_W and step + opt.population_size <= ceiling:
        sols = []
        for _ in range(opt.population_size):
            w = opt.ask()
            val = objective(w)
            sols.append((w, val))
            if val < best_obj - 1e-6:
                best_obj, best_w = val, w
                stall = -1  # reset; +=1 below makes it 0 for this improving gen
            step += 1
        opt.tell(sols)
        stall += 1
        if opt.should_stop():
            break
    T, sw = build_T(best_w)
    routing = {f: float(sw[k]) for k, f in enumerate(carrier_feats)}
    res = _score_transform(T, M, sub, "T_adv", routing=routing)
    res.note = f"cmaes steps={step} stall={stall}"
    return res


# ---------------------------------------------------------------------------
# Published Rashomon ensemble (surrogate of the submitted model's decisions)
# ---------------------------------------------------------------------------
def build_surrogate_band(audit: pd.DataFrame, submitted_decisions: np.ndarray,
                         feature_pool: list[str], *, seed: int):
    X = audit[feature_pool].values
    return build_refinement_band(
        X, submitted_decisions, feature_names=feature_pool, monotonic_cst_map={},
        epsilon=EPSILON, depths=DEPTHS, leaf_mins=LEAF_MINS,
        max_subset_size=MAX_SUBSET_SIZE, seed=seed)


def member_used_features(member: RefinementMember) -> list[str]:
    """Features the fitted member actually splits on, from its tree signature
    (subset, ((local_feat_idx, threshold), ...)) -- no refit needed."""
    subset, nodes = member.tree_signature
    return sorted({subset[fi] for (fi, _thr) in nodes if fi < len(subset)})


def band_used_feature_sets(band) -> list[list[str]]:
    return [member_used_features(m) for m in band.distinct_members]


# ---------------------------------------------------------------------------
# Importance (rung 3b)
# ---------------------------------------------------------------------------
def _cfresh_importance(model, sub: Substrate, *, estimator: str = "split_gain") -> dict[str, float]:
    feats = model._feats  # noqa: SLF001
    cf = [c for c in CFRESH_FEATURES if c in feats]
    if not cf:
        return {c: 0.0 for c in CFRESH_FEATURES}
    if estimator == "split_gain":
        imp = dict(zip(feats, model.feature_importances_))
        return {c: float(imp.get(c, 0.0)) for c in CFRESH_FEATURES}
    # permutation importance on the validation split
    X = sub.val[feats].values
    y = sub.val["Y"].values
    pi = permutation_importance(model, X, y, n_repeats=5, random_state=sub.seed,
                                scoring="roc_auc")
    imp = dict(zip(feats, pi.importances_mean))
    return {c: float(max(0.0, imp.get(c, 0.0))) for c in CFRESH_FEATURES}


# ---------------------------------------------------------------------------
# Remediated-control family (§2g)
# ---------------------------------------------------------------------------
def build_controls(sub: Substrate) -> dict[str, object]:
    """C_drop / C_resid / C_oracle / C_null, each a model with Delta ~ 0 expected."""
    tr = sub.train
    y = tr["Y"].values
    out: dict[str, object] = {}

    # C_drop: drop G + features with |corr to G| > D4 alpha
    keep = []
    for f in LEGIT_FEATURES + CFRESH_FEATURES:
        c = abs(np.corrcoef(tr[f].values, tr["G"].values)[0, 1])
        if c <= dgp.D4_ALPHA:
            keep.append(f)
    out["C_drop"] = _fit_surrogate(tr, y, keep or LEGIT_FEATURES, sub.seed)

    # C_resid: residualize each feature against G, then train
    resid = tr.copy()
    Gc = tr["G"].values.astype(float)
    Gc = (Gc - Gc.mean())
    for f in LEGIT_FEATURES + CFRESH_FEATURES:
        v = tr[f].values.astype(float)
        b = float(np.dot(Gc, v) / (np.dot(Gc, Gc) + 1e-12))
        resid[f] = v - b * Gc
    cr = _gbt(sub.seed)
    feats_r = LEGIT_FEATURES + CFRESH_FEATURES
    cr.fit(resid[feats_r].values, y); cr._feats = feats_r  # noqa: SLF001
    out["C_resid"] = cr

    # C_oracle / C_null are Delta~0 BY CONSTRUCTION: trained on a clean target drawn
    # from the legitimate coefficients only (no disparate term), so they qualify on
    # EVERY channel (the §2g floor of 2). C_oracle sees legit features; C_null sees
    # all features but the target carries no protected signal.
    beta = np.array([sub.legit_coeffs[f"x{j}"] for j in range(dgp.N_LEGIT)])
    legit_logit = tr[LEGIT_FEATURES].values @ beta
    rng = np.random.default_rng(sub.seed + 12345)
    y_clean = rng.binomial(1, 1.0 / (1.0 + np.exp(-legit_logit)))
    out["C_oracle"] = _fit_surrogate(tr, y_clean, LEGIT_FEATURES, sub.seed)
    out["C_null"] = _fit_surrogate(tr, y_clean, LEGIT_FEATURES + CFRESH_FEATURES, sub.seed)
    return out


def control_cfresh_null(controls: dict, sub: Substrate, estimator: str) -> list[float]:
    vals = []
    for name, m in controls.items():
        for c, v in _cfresh_importance(m, sub, estimator=estimator).items():
            vals.append(v)
    return vals


# ---------------------------------------------------------------------------
# Rungs
# ---------------------------------------------------------------------------
def rung1_shap_lime(T, sub: Substrate) -> dict:
    """SHAP/LIME 'clean' check on the submitted model. evade=True iff no
    declared protected-proxy appears in the top-k by global mean-|attribution|
    AND attribution to G-correlated named features is below phi."""
    import shap
    from lime.lime_tabular import LimeTabularExplainer

    feats = T._feats  # noqa: SLF001
    audit = sub.test.sample(n=min(400, len(sub.test)), random_state=sub.seed)
    bg = shap.kmeans(sub.train[feats].values, N_BG)
    f = lambda data: T.predict_proba(data)[:, 1]  # noqa: E731
    expl = shap.KernelExplainer(f, bg)
    sv = expl.shap_values(audit[feats].values, nsamples=SHAP_NSAMPLES, silent=True)
    sv = np.asarray(sv)
    shap_mean = dict(zip(feats, np.abs(sv).mean(axis=0)))

    lime_expl = LimeTabularExplainer(sub.train[feats].values, feature_names=feats,
                                     discretize_continuous=True, random_state=sub.seed,
                                     mode="classification")
    lime_acc = {ff: 0.0 for ff in feats}
    n_lime = min(50, len(audit))
    for i in range(n_lime):
        e = lime_expl.explain_instance(audit[feats].values[i], T.predict_proba,
                                       num_features=len(feats))
        for fi, wt in e.as_map()[1]:
            lime_acc[feats[fi]] += abs(wt)
    lime_mean = {ff: v / n_lime for ff, v in lime_acc.items()}

    def topk(d):
        return [k for k, _ in sorted(d.items(), key=lambda kv: -kv[1])[:RUNG1_TOPK]]

    proxies_present = set(sub.all_protected) & set(feats)
    shap_top, lime_top = topk(shap_mean), topk(lime_mean)
    shap_clean = not (proxies_present & set(shap_top)) and all(
        shap_mean.get(p, 0.0) < RUNG1_PHI for p in proxies_present)
    lime_clean = not (proxies_present & set(lime_top))
    evade = bool(shap_clean and lime_clean)
    return {"P1_shap_lime_evade": evade, "shap_top": shap_top, "lime_top": lime_top,
            "shap_mean": {k: float(v) for k, v in shap_mean.items()},
            "proxies_present": sorted(proxies_present)}


def rung2_disagreement(band, sub: Substrate, submitted_decisions: np.ndarray,
                       feature_pool: list[str]) -> dict:
    """Cross-member 0/1 prediction disagreement of the surrogate band on the
    audit sample (fraction of member-pairs disagreeing, mean over rows)."""
    members = band.distinct_members
    if len(members) < 2:
        return {"disagreement": 0.0, "n_members": len(members)}
    audit = sub.test
    Xfull = sub.train[feature_pool].values
    yfull = submitted_decisions
    preds = []
    name_to_col = {f: i for i, f in enumerate(feature_pool)}
    for m in members:
        tree = refit_member(m, Xfull, yfull, feature_names=feature_pool, seed=sub.seed)
        cols = [name_to_col[f] for f in m.feature_subset]
        preds.append(tree.predict(audit[feature_pool].values[:, cols]))
    P = np.vstack(preds)  # (n_members, n_rows)
    # mean over rows of (fraction of members predicting 1) closeness to 0.5
    frac1 = P.mean(axis=0)
    disagreement = float(np.mean(2 * frac1 * (1 - frac1)))  # 0 = unanimous, 0.5 = max split
    return {"disagreement": disagreement, "n_members": len(members)}


def rung3a(band_full, band_restricted, prohibited: set[str]) -> dict:
    ufs_A = band_used_feature_sets(band_full)
    B_set = {frozenset(u) for u in band_used_feature_sets(band_restricted)}
    A_restricted = restrict(ufs_A, prohibited)
    is_reorg, reason, j = classify_reorganized(A_restricted, B_set, RUNG3A_JTHRESH)
    return {"P3a_reorg_catch": bool(is_reorg), "reason": reason, "jaccard": float(j),
            "prohibited": sorted(prohibited)}


def rung3b(T, sub: Substrate, null_vals: list[float], *, estimator="split_gain") -> dict:
    """Weight-aware oracle reference: flag c_fresh if its realized importance in
    the submitted model exceeds the 95th pct of the legitimate-importance null
    (assembled from the control family). Legitimate c_fresh importance ~ 0 by
    construction (c_fresh not load-bearing for Y in the base DGP)."""
    realized = _cfresh_importance(T, sub, estimator=estimator)
    null = np.asarray(null_vals) if null_vals else np.array([0.0])
    thresh = float(np.percentile(null, RUNG3B_NULL_PCT))
    flagged = {c: bool(v > thresh) for c, v in realized.items()}
    catch = any(flagged.values())
    return {"P3b_reorg_catch": bool(catch), "realized": realized,
            "null_95": thresh, "flagged": flagged, "estimator": estimator}


# ---------------------------------------------------------------------------
# Per-cell orchestration
# ---------------------------------------------------------------------------
def run_cell(channel: str, seed: int, *, smoke: bool = False) -> dict:
    n_total = 2000 if smoke else None
    sub = make_substrate(channel, seed, n_total=n_total)
    G_test = sub.test["G"].values
    M = fit_discriminatory_M(sub)
    d_M = dp_gap(decisions(M, sub.test), G_test)
    auc_M = auc_of(M, sub.test)
    valid = abs(d_M) >= DELTA_MIN and AUC_LOW <= auc_M <= AUC_HIGH

    controls = build_controls(sub)
    null_sg = control_cfresh_null(controls, sub, "split_gain")
    control_deltas = {name: dp_gap(decisions(m, sub.test), G_test) for name, m in controls.items()}

    # FIXED declared off-limits set -- NOT the DGP wiring (sub.proxies). Deriving
    # prohibited from the actual carrier was the case-1 collapse that made 3a
    # trivially catch; the fresh-carrier threat routes onto carriers outside this set.
    prohibited = set(PROHIBITED_IN_POOL)
    band_kw = dict(seed=seed)

    rows = []
    transforms = [transform_naive(M, sub)]
    if not smoke:
        transforms.append(transform_adv(M, sub, auc_M=auc_M))
    else:
        transforms.append(transform_adv(M, sub, patience_W=3, ceiling=12, auc_M=auc_M))

    for T in transforms:
        dec_T = decisions(T.model, sub.test)
        # surrogate bands of T's decisions (on the audit/train split)
        train_dec = decisions(T.model, sub.train)
        band_full = build_surrogate_band(sub.train, train_dec, BAND_POOL, **band_kw)
        restricted_pool = [f for f in BAND_POOL if f not in prohibited]
        band_restr = build_surrogate_band(sub.train, train_dec, restricted_pool, **band_kw)

        r1 = rung1_shap_lime(T.model, sub) if not smoke else {"P1_shap_lime_evade": None,
                                                              "note": "skipped in smoke"}
        r2 = rung2_disagreement(band_full, sub, train_dec, BAND_POOL)
        r3a = rung3a(band_full, band_restr, prohibited)
        r3b = rung3b(T.model, sub, null_sg, estimator="split_gain")
        rows.append({
            "channel": channel, "seed": seed, "transform": T.label,
            "r_retained": T.r_retained, "auc_M": auc_M, "auc_T": T.auc, "delta_M": d_M,
            "delta_T": T.delta, "valid": valid,
            "P1_shap_lime_evade": r1.get("P1_shap_lime_evade"),
            "P2_disagreement": r2["disagreement"], "n_band_members": r2["n_members"],
            "P3a_reorg_catch": r3a["P3a_reorg_catch"], "jaccard_3a": r3a["jaccard"],
            "P3b_reorg_catch": r3b["P3b_reorg_catch"], "rung3b": r3b,
            "routing": T.routing, "note": T.note,
        })
    return {"channel": channel, "seed": seed, "valid_run": valid, "delta_M": d_M,
            "auc_M": auc_M, "control_deltas": control_deltas,
            "control_cfresh_null_95_splitgain": float(np.percentile(null_sg, RUNG3B_NULL_PCT)),
            "rows": rows}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--channels", nargs="+", default=list(CHANNELS))
    ap.add_argument("--seeds", type=int, default=N_SEEDS)
    ap.add_argument("--smoke", action="store_true", help="tiny n, few seeds, skip SHAP/LIME")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    seeds = range(2 if args.smoke else args.seeds)
    out_path = Path(args.out).resolve() if args.out else (
        REPO_ROOT / "runs" / ("fairwash_frontier_smoke.json" if args.smoke
                              else "fairwash_frontier_2026-05-23.json"))
    cells, t0 = [], time.time()
    for ch in args.channels:
        for s in seeds:
            print(f"[{time.time()-t0:6.1f}s] {ch} seed={s} ...", flush=True)
            cells.append(run_cell(ch, s, smoke=args.smoke))
    out = {"experiment": "fairwash-reorganization frontier (synthetic)",
           "pre_reg": "docs/superpowers/specs/2026-05-23-fairwash-reorganization-frontier-preregistration-note.md",
           "pre_reg_commit": "daf032d", "smoke": args.smoke,
           "n_cells": len(cells), "cells": cells}
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, default=str))
    try:
        shown = out_path.relative_to(REPO_ROOT)
    except ValueError:
        shown = out_path
    print(f"\nWrote {shown} ({len(cells)} cells)")


if __name__ == "__main__":
    main()
