#!/usr/bin/env python3
"""Synthetic DGP for the fairwashing-vs-reorganization frontier experiment.

BINDING SPEC for the pre-registration:
    docs/superpowers/specs/2026-05-23-fairwash-reorganization-frontier-preregistration-note.md

This module generates the DATA SUBSTRATE ONLY. It fits no models, applies no
fairwashing transform T, and runs no audit rung. Those are the post-freeze
experiment (scripts/fairwash_frontier_test.py). Freezing this generator WITH
the pre-reg closes the post-freeze DGP-tuning degree of freedom (§2h): the
covariance, coefficients, and channel wiring are fixed here, deterministically.

Channels (the D1-D4 difficulty ladder, §2b), ordered by signal concentration:
    D1 additive    : direct G penalty                       (concentrated, easy)
    D2 single-proxy: over-reliance on one G-correlated legit feature
    D3 interaction : G modulates a risk factor (G x x_k)    (realistic)
    D4 distributed : low-rank smear across K>=5 features, each |corr(.,G)|<=alpha
                     (individually innocent, jointly disparate -- fiendish)

The c_fresh portfolio (3 distributional families, §2c) provides admissible
laundering carriers correlated with G but NOT load-bearing for Y in the base
DGP -- T (post-freeze) is what routes effect onto them.

`legitimate_coefficients` in the returned metadata is the ground-truth
importance the rung-3b ORACLE reference (§2f) is calibrated against.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

# --- Frozen scalars (pre-reg §2h) -------------------------------------------
N_TRAIN, N_VAL, N_TEST = 20_000, 5_000, 25_000
G_PREVALENCE = 0.30
N_LEGIT = 8
D4_ALPHA = 0.15        # per-feature |corr(feature, G)| cap defining "distributed"
D4_K = 5               # min features carrying signal in the distributed channel
DELTA_MIN = 0.10       # min demographic-parity gap for a valid run
CHANNELS = ("D1", "D2", "D3", "D4")

# Legitimate-risk coefficients (frozen). Moderate magnitudes -> AUC ~0.78-0.85
# once a model is fit (validity-checked post-freeze, not here).
_LEGIT_BETA = np.array([0.90, 0.55, 0.80, 0.45, 0.70, 0.40, 0.60, 0.35])
_INTERCEPT = 0.0
# Per-channel disparate magnitude, calibrated so each lands in Δ∈[0.12,0.20]
# (the INDEPENDENT variable -- magnitude of injected discrimination -- not the
# outcome; verified structurally in __main__). FROZEN once calibrated.
_DELTA = {"D1": 2.00, "D2": 3.20, "D3": 3.50, "D4": 6.00}


@dataclass(frozen=True)
class DGPResult:
    frame: pd.DataFrame              # X (8 legit) + c_fresh_* + G + Y
    legitimate_coefficients: dict[str, float]   # 3b oracle reference
    channel: str
    proxy_feature: str | None        # D2 carrier
    interaction_feature: str | None  # D3 carrier
    distributed_features: list[str]  # D4 carriers
    cfresh_features: list[str]
    seed: int


def _legit_design(rng: np.random.Generator, n: int) -> tuple[np.ndarray, np.ndarray]:
    """8 legitimate features with 2 deliberately collinear pairs + a latent G.

    G is correlated with x0 (a legitimate risk factor): protected status and
    genuine risk are entangled, which is precisely the condition that makes
    laundering possible (and disparate-impact defenses hard).
    Returns (X[n,8], G[n]).
    """
    z = rng.standard_normal((n, N_LEGIT))
    X = z.copy()
    # Collinear pair 1: x1 := 0.85*x0 + small noise ; pair 2: x3 := 0.80*x2 + noise
    X[:, 1] = 0.85 * z[:, 0] + np.sqrt(1 - 0.85**2) * z[:, 1]
    X[:, 3] = 0.80 * z[:, 2] + np.sqrt(1 - 0.80**2) * z[:, 3]
    # G driven by x0 (entanglement) -- modest, so it still enables proxy laundering
    # but does not cancel a direct disparate penalty. corr(G, x0) ~ 0.25.
    g_latent = 0.35 * X[:, 0] + rng.standard_normal(n)
    cut = np.quantile(g_latent, 1 - G_PREVALENCE)
    G = (g_latent > cut).astype(int)
    return X, G


def _cfresh_portfolio(rng: np.random.Generator, n: int, G: np.ndarray) -> dict[str, np.ndarray]:
    """3 admissible laundering carriers across distributional families (§2c).

    Each is correlated with G (so it CAN carry G-signal) but is not used to
    generate Y here. Fresh: none is a mapped carrier or a transform of one.
    """
    gz = (G - G.mean()) / (G.std() + 1e-12)
    # continuous, moderate cardinality
    cont = 0.5 * gz + rng.standard_normal(n)
    # sparse categorical (mostly 0): P(1) rises with G
    p_cat = 0.05 + 0.15 * G
    cat = rng.binomial(1, p_cat)
    # heavy-tailed count: NegBinomial-like via Poisson-Gamma, rate rises with G
    rate = np.exp(0.2 + 0.4 * G + 0.3 * rng.standard_normal(n))
    count = rng.poisson(rate)
    return {"cfresh_cont": cont, "cfresh_cat": cat.astype(float), "cfresh_count": count.astype(float)}


def _disparate_term(channel: str, X: np.ndarray, G: np.ndarray,
                    rng: np.random.Generator) -> tuple[np.ndarray, dict]:
    """Return (additive logit contribution, channel-metadata) for the channel."""
    d = _DELTA[channel]
    meta: dict = {"proxy_feature": None, "interaction_feature": None,
                  "distributed_features": []}
    if channel == "D1":
        return -d * G, meta
    if channel == "D2":
        # Over-reliance on the single legit feature most correlated with G.
        corrs = [abs(np.corrcoef(X[:, j], G)[0, 1]) for j in range(N_LEGIT)]
        j = int(np.argmax(corrs))
        meta["proxy_feature"] = f"x{j}"
        return -d * X[:, j], meta
    if channel == "D3":
        # G modulates a risk factor via a high-risk INDICATOR: the protected-group
        # high-risk subgroup is penalized specifically (G=1 AND x_j above its
        # median). Directional, stable mean shift, doesn't fight the linear term.
        # "This risk factor counts against you only if you're also in group G."
        j = 4
        meta["interaction_feature"] = f"x{j}"
        high_risk = (X[:, j] > 0.0).astype(float)
        return -d * G * high_risk, meta
    if channel == "D4":
        # Low-rank smear: K features each with |corr to G| <= alpha, same-signed,
        # so individually innocent but jointly disparate.
        gz = (G - G.mean()) / (G.std() + 1e-12)
        feats, used = [], []
        contrib = np.zeros(len(G))
        for j in range(2, N_LEGIT):          # avoid x0/x1 (high G-corr) and the pairs' anchors
            # nudge feature toward G weakly, capped under alpha
            cand = X[:, j] + 0.12 * gz
            c = abs(np.corrcoef(cand, G)[0, 1])
            if c <= D4_ALPHA:
                X[:, j] = cand
                contrib += cand
                feats.append(f"x{j}")
            if len(feats) >= D4_K:
                break
        meta["distributed_features"] = feats
        used = feats
        if len(used) < D4_K:
            raise RuntimeError(f"D4 could not place {D4_K} sub-alpha carriers (got {len(used)})")
        return -(d / len(used)) * contrib, meta
    raise ValueError(f"unknown channel {channel}")


def generate(channel: str, n: int, seed: int) -> DGPResult:
    """Generate one (channel, seed) substrate. Deterministic given (channel, seed)."""
    if channel not in CHANNELS:
        raise ValueError(f"channel must be one of {CHANNELS}")
    rng = np.random.default_rng(seed)
    X, G = _legit_design(rng, n)
    legit_logit = _INTERCEPT + X @ _LEGIT_BETA
    disp, meta = _disparate_term(channel, X, G, rng)
    p = 1.0 / (1.0 + np.exp(-(legit_logit + disp)))
    Y = rng.binomial(1, p)

    cols = {f"x{j}": X[:, j] for j in range(N_LEGIT)}
    cols.update(_cfresh_portfolio(rng, n, G))
    cols["G"] = G
    cols["Y"] = Y
    frame = pd.DataFrame(cols)
    return DGPResult(
        frame=frame,
        legitimate_coefficients={f"x{j}": float(_LEGIT_BETA[j]) for j in range(N_LEGIT)},
        channel=channel,
        proxy_feature=meta["proxy_feature"],
        interaction_feature=meta["interaction_feature"],
        distributed_features=meta["distributed_features"],
        cfresh_features=["cfresh_cont", "cfresh_cat", "cfresh_count"],
        seed=seed,
    )


def demographic_parity_gap(frame: pd.DataFrame) -> float:
    """Δ = P(Y=1 | G=0) - P(Y=1 | G=1) on the generated labels (validity check)."""
    g0 = frame.loc[frame.G == 0, "Y"].mean()
    g1 = frame.loc[frame.G == 1, "Y"].mean()
    return float(g0 - g1)


# ===========================================================================
# V2 latent-G twin-world substrate (compliant-practice pre-reg, rev-6)
#   World A (proxy):      c_fresh <- G -> Y      (G latent; Y depends on G)
#   World B (legitimate): c_fresh -> Y           (Y ~ World A's observable
#                                                 regression p_obs => Y _||_ G | obs)
# Both share the observable joint P(x0..x7, c_fresh, Y); only the latent causal
# status of c_fresh differs (the cited confounding-vs-causation non-identifiability).
# G is emitted for the EXPERIMENTER only (disparate-impact, proxy_strength); the
# audit/discriminator never sees it (except R4's Ĝ_BISG estimate).
# ===========================================================================
_TWIN_DISP = 2.5        # disparate logit weight on standardized latent G (World A)
OBSERVABLE_FEATURES = [f"x{j}" for j in range(N_LEGIT)]  # x0..x7 audit-visible
CFRESH_PORTFOLIO = ["cfresh_cont", "cfresh_cat", "cfresh_count"]


@dataclass(frozen=True)
class TwinWorldResult:
    frame: pd.DataFrame
    proxy_strength_target: float
    coupling: float
    world: str
    bisg_auc_target: float
    seed: int


def _twin_base(rng: np.random.Generator, n: int):
    """Legit design x0..x7 (2 collinear pairs) + latent G driven by x0."""
    z = rng.standard_normal((n, N_LEGIT))
    X = z.copy()
    X[:, 1] = 0.85 * z[:, 0] + np.sqrt(1 - 0.85**2) * z[:, 1]
    X[:, 3] = 0.80 * z[:, 2] + np.sqrt(1 - 0.80**2) * z[:, 3]
    g_latent = 0.35 * X[:, 0] + rng.standard_normal(n)
    G = (g_latent > np.quantile(g_latent, 1 - G_PREVALENCE)).astype(int)
    return X, G, g_latent


def _cfresh_coupled(rng: np.random.Generator, G: np.ndarray, a: float) -> dict[str, np.ndarray]:
    """3-family c_fresh portfolio coupled to G with scalar strength `a`."""
    gz = (G - G.mean()) / (G.std() + 1e-12)
    cont = a * gz + rng.standard_normal(len(G))
    cat = rng.binomial(1, np.clip(0.08 + 0.12 * a * G, 0.0, 0.95)).astype(float)
    rate = np.exp(0.1 + 0.30 * a * G + 0.3 * rng.standard_normal(len(G)))
    count = rng.poisson(rate).astype(float)
    return {"cfresh_cont": cont, "cfresh_cat": cat, "cfresh_count": count}


def _portfolio_auc_for_G(cf: dict[str, np.ndarray], G: np.ndarray) -> float:
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import roc_auc_score
    X = np.column_stack([cf[k] for k in CFRESH_PORTFOLIO])
    lr = LogisticRegression(max_iter=200).fit(X, G)
    return float(roc_auc_score(G, lr.predict_proba(X)[:, 1]))


def _coupling_for_proxy_strength(target: float, seed: int) -> float:
    """Bisect the scalar coupling `a` so AUC(G ~ c_fresh portfolio) ≈ target.
    Monotone in `a`; calibrated on a fixed reference sample (deterministic)."""
    if target <= 0.505:
        return 0.0
    rng = np.random.default_rng(seed + 9_000)
    _, G, _ = _twin_base(rng, 6000)
    lo, hi = 0.0, 4.0
    for _ in range(22):
        mid = 0.5 * (lo + hi)
        cf = _cfresh_coupled(np.random.default_rng(seed + 9_001), G, mid)
        if _portfolio_auc_for_G(cf, G) < target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def _bisg_estimate(G: np.ndarray, g_latent: np.ndarray, target_auc: float,
                   rng: np.random.Generator) -> np.ndarray:
    """Ĝ_BISG: continuous regulator estimate of G with AUC(Ĝ ~ G) ≈ target_auc.
    Built from the latent G-signal + independent noise ONLY -- never c_fresh."""
    from sklearn.metrics import roc_auc_score
    gz = (g_latent - g_latent.mean()) / (g_latent.std() + 1e-12)
    noise = rng.standard_normal(len(G))
    lo, hi = 0.0, 40.0
    for _ in range(40):
        s = 0.5 * (lo + hi)
        if roc_auc_score(G, gz + s * noise) > target_auc:
            lo = s          # too informative -> add noise
        else:
            hi = s
    s = 0.5 * (lo + hi)
    score = gz + s * noise
    return 1.0 / (1.0 + np.exp(-(score - score.mean()) / (score.std() + 1e-9)))


def generate_twin_world(proxy_strength: float, world: str, n: int, seed: int,
                        *, bisg_auc: float = 0.85) -> TwinWorldResult:
    """One (proxy_strength, world, seed) latent-G twin-world substrate.

    World A and World B share inputs (x0..x7, c_fresh) deterministically given
    `seed`; they differ only in how Y is generated:
      World A: Y ~ Bernoulli(sigmoid(legit_logit + disp * G_z))   (G drives Y)
      World B: Y ~ Bernoulli(p_obs(observables))                  (c_fresh drives Y)
    where p_obs is World A's observable regression E[Y_A | x0..x7, c_fresh],
    so the observable joint matches by construction and Y_B _||_ G | observables.
    """
    if world not in ("A", "B"):
        raise ValueError("world must be 'A' or 'B'")
    rng = np.random.default_rng(seed)
    X, G, g_latent = _twin_base(rng, n)
    Gz = (G - G.mean()) / (G.std() + 1e-12)
    legit_logit = _INTERCEPT + X @ _LEGIT_BETA

    a = _coupling_for_proxy_strength(proxy_strength, seed)
    cf = _cfresh_coupled(rng, G, a)

    # World A labels (Y depends on latent G); also the basis for p_obs.
    pA = 1.0 / (1.0 + np.exp(-(legit_logit + _TWIN_DISP * Gz)))
    YA = rng.binomial(1, pA)
    y_clean = rng.binomial(1, 1.0 / (1.0 + np.exp(-legit_logit)))

    if world == "A":
        Y = YA
    else:
        # World B: draw Y from World A's OBSERVABLE regression (no G).
        from sklearn.ensemble import GradientBoostingRegressor
        obs = np.column_stack([X] + [cf[k] for k in CFRESH_PORTFOLIO])
        p_obs = GradientBoostingRegressor(max_depth=3, n_estimators=200,
                                          learning_rate=0.05, subsample=0.8,
                                          random_state=seed).fit(obs, YA).predict(obs)
        p_obs = np.clip(p_obs, 1e-4, 1 - 1e-4)
        Y = rng.binomial(1, p_obs)

    ghat = _bisg_estimate(G, g_latent, bisg_auc, rng)

    cols = {f"x{j}": X[:, j] for j in range(N_LEGIT)}
    cols.update(cf)
    cols["G"] = G
    cols["Y"] = Y
    cols["Y_clean"] = y_clean
    cols["Ghat_bisg"] = ghat
    cols["world"] = world
    return TwinWorldResult(frame=pd.DataFrame(cols), proxy_strength_target=proxy_strength,
                           coupling=a, world=world, bisg_auc_target=bisg_auc, seed=seed)


if __name__ == "__main__":
    # STRUCTURAL sanity only (valid-run checklist, §2h) -- no models, no hypothesis.
    for ch in CHANNELS:
        r = generate(ch, n=N_TEST, seed=0)
        gap = demographic_parity_gap(r.frame)
        # D4: confirm each distributed carrier is individually sub-alpha.
        sub_alpha = all(
            abs(np.corrcoef(r.frame[f], r.frame.G)[0, 1]) <= D4_ALPHA
            for f in r.distributed_features
        ) if r.distributed_features else True
        print(f"{ch}: n={len(r.frame)} Gprev={r.frame.G.mean():.3f} "
              f"Δ={gap:+.3f} (>= {DELTA_MIN}? {abs(gap) >= DELTA_MIN}) "
              f"proxy={r.proxy_feature} inter={r.interaction_feature} "
              f"distK={len(r.distributed_features)} sub_alpha={sub_alpha}")
