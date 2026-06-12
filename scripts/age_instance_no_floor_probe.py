#!/usr/bin/env python3
"""The AGE instance: does the band launder disparity when there is NO base-rate alibi?

Forensic motivation (Tony, 2026-06-11): live age-discrimination-by-AI hiring suits
exist and the field has no accepted analysis models. Age differs from lending in the
ONE way that matters for the C3 floor: in lending, real default risk lawfully
correlates with the protected attribute (base rates differ), so a defendant can say
"the disparity is the regrettable base-rate floor, we're partly trapped." AGE HAS NO
SUCH STORY -- there is no lawful "older applicants are worse at the job" base rate.
Age enters hiring models ONLY through facially-neutral proxies (years-since-degree,
"digital native", tenure, salary expectation, resume gaps). So:

  This probe removes BOTH lawful mechanisms the lending bench bakes in --
    (1) the base-rate gap by G  (lending: gap -0.12..-0.18)
    (2) the G<->x0 legit entanglement (lending: corr +0.25)
  -- and injects disparity ONLY through the c_fresh PROXY carriers (G-correlated,
  Y-irrelevant by construction). Then it runs tonight's EXACT band-vs-blindness
  comparison (scripts/band_vs_blindness_probe.py), so the age result is directly
  comparable to the lending result.

The cross-examination question: with no base-rate alibi, does a G-blind "explainable"
policy-constrained band STILL contain a high-disparity member (tonight's amplification
finding), making "we used an explainable model" a fig leaf -- or does the disparity
collapse, meaning lending's disparity was mostly the C3 floor (then the age laundering
claim is real but small, an argument about magnitude)?

FROZEN PREDICTION (frozen before this ran):
  P-laundering-exposed (0.55): band still concentrates/amplifies age-disparity with
    ZERO base-rate alibi -- band max-disparity member materially exceeds the disparity
    a fair selector would pick, AND exceeds ~0.03 absolute. 100% attributable to proxy
    laundering. The damning, court-ready result.
  P-floor-was-load-bearing (0.30): with base rates equal, band disparity collapses
    toward ~0 -- lending disparity was mostly the C3 floor; proxy-only laundering is
    weak. Age claim is HARDER (magnitude argument), worth knowing pre-deposition.
  P-mixed (0.15): proxy disparity present but amplification doesn't survive equal rates.

DISCIPLINE NOTE: the opposing expert is a paid blind adversary. Controls: (a) verify
base-rate gap ~0 and corr(G, legit) ~0 in the generated substrate (the alibi really is
removed); (b) report the FAIR-selector disparity (min over band) alongside the worst,
so the claim is "worst-vs-fair spread", not "worst alone"; (c) a proxy-strength sweep
so the result is a curve, not a single point a deposition could pick apart.
"""
from __future__ import annotations

import argparse
import importlib.util
import itertools
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier

from policy.encoder import PolicyConstraints
from wedge.rashomon import (
    SweepConfig, evaluate_policy, filter_to_epsilon_under_loss,
    hyperparameter_sweep, inner_split,
)
from wedge.losses import grant_emphasis_loss

N_LEGIT = 8
_LEGIT_BETA = np.array([0.90, 0.55, 0.80, 0.45, 0.70, 0.40, 0.60, 0.35])
G_PREVALENCE = 0.30


def generate_no_floor(n, seed, *, proxy_strength):
    """Age substrate: G INDEPENDENT of legit features, base rates EQUAL by G, disparity
    injected ONLY through 3 c_fresh proxy carriers (G-correlated, Y-irrelevant).

    proxy_strength scales how strongly the proxies carry G (the laundering channel).
    Returns (frame, diagnostics).
    """
    rng = np.random.default_rng(seed)
    z = rng.standard_normal((n, N_LEGIT))
    X = z.copy()
    X[:, 1] = 0.85 * z[:, 0] + np.sqrt(1 - 0.85**2) * z[:, 1]
    X[:, 3] = 0.80 * z[:, 2] + np.sqrt(1 - 0.80**2) * z[:, 3]

    # G INDEPENDENT of X (no lawful entanglement): draw G from pure noise.
    g_latent = rng.standard_normal(n)
    G = (g_latent > np.quantile(g_latent, 1 - G_PREVALENCE)).astype(int)

    # Y from legit features ONLY, NO G term -> base rates equal by G (no C3 floor).
    legit_logit = X @ _LEGIT_BETA
    p = 1.0 / (1.0 + np.exp(-legit_logit))
    Y = rng.binomial(1, p)

    # c_fresh PROXY carriers: correlated with G, NOT used to generate Y (pure proxies).
    gz = (G - G.mean()) / (G.std() + 1e-12)
    a = proxy_strength
    cont = a * gz + rng.standard_normal(n)
    cat = rng.binomial(1, np.clip(0.08 + 0.12 * a * G, 0.0, 0.95)).astype(float)
    rate = np.exp(0.1 + 0.30 * a * G + 0.3 * rng.standard_normal(n))
    count = rng.poisson(rate).astype(float)

    cols = {f"x{j}": X[:, j] for j in range(N_LEGIT)}
    cols.update({"cfresh_cont": cont, "cfresh_cat": cat, "cfresh_count": count})
    cols["G"] = G; cols["Y"] = Y
    frame = pd.DataFrame(cols)

    # DISCIPLINE controls: confirm the alibi is actually removed.
    br1, br0 = Y[G == 1].mean(), Y[G == 0].mean()
    max_legit_corr = max(abs(np.corrcoef(X[:, j], G)[0, 1]) for j in range(N_LEGIT))
    proxy_corr = abs(np.corrcoef(cont, G)[0, 1])
    diag = {
        "base_rate_gap": round(float(br1 - br0), 4),         # MUST be ~0
        "max_legit_G_corr": round(float(max_legit_corr), 4), # MUST be ~0
        "proxy_G_corr": round(float(proxy_corr), 4),         # the injected laundering channel
    }
    return frame, diag


def policy():
    return PolicyConstraints(
        name="age_no_floor", version="1", status="active", monotonicity_map={},
        mandatory_features=(), prohibited_features=("G",), applicable_regime={})


def _subsets(feat, max_k):
    out = []
    for k in range(1, max_k + 1):
        out.extend(itertools.combinations(feat, k))
    return tuple(out)


def _disparity(grant, G):
    g1, g0 = G == 1, G == 0
    if not g1.any() or not g0.any():
        return float("nan")
    return float(abs(grant[g1].mean() - grant[g0].mean()))


def _disp_at_grant_rate(score, G, grant_rate):
    if grant_rate <= 0 or grant_rate >= 1:
        return float("nan")
    thr = np.quantile(score, grant_rate)
    return _disparity((score <= thr).astype(int), G)


def run(proxy_strength, *, n, seed, eps_frac, max_k):
    frame, diag = generate_no_floor(n, seed, proxy_strength=proxy_strength)
    Y = frame["Y"].astype(int)
    feat = [c for c in frame.columns if c not in ("G", "Y")]
    X = frame[feat]; G = frame["G"].to_numpy()

    cfg = SweepConfig(max_depths=(4, 6, 8, 10), min_samples_leafs=(25, 50, 100, 200),
                      feature_subsets=_subsets(feat, max_k), random_state=seed,
                      holdout_fraction=0.30)
    adm = evaluate_policy(hyperparameter_sweep(X, Y, config=cfg), policy_constraints=policy())
    nh = len(np.asarray(adm.admissible[0].holdout_y_true))
    band = filter_to_epsilon_under_loss(
        adm, loss_fn=lambda yt, yh: grant_emphasis_loss(yt, yh, w_T=1.5),
        loss_label="L_T(w_T=1.5)", epsilon=eps_frac * nh)
    members = band.within_epsilon
    if len(members) < 2:
        return {"proxy_strength": proxy_strength, "note": "band<2", **diag}

    _, X_hold, _, _ = inner_split(X, Y, config=cfg)
    G_hold = G[np.asarray(X_hold.index)]
    disps, grant_rates = [], []
    for m in members:
        yp = np.asarray(m.holdout_y_pred)
        disps.append(_disparity(yp, G_hold)); grant_rates.append(float(yp.mean()))
    disps = np.array(disps); grant_rates = np.array(grant_rates)
    worst_i = int(np.nanargmax(disps)); fair_i = int(np.nanargmin(disps))
    band_worst = float(disps[worst_i]); band_fair = float(disps[fair_i])
    band_gr = float(grant_rates[worst_i])

    # blind-flexible ceiling at the band's grant rate (apples-to-apples, like tonight).
    Xb = frame[feat].to_numpy(); Yv = frame["Y"].to_numpy()
    idx = np.asarray(X_hold.index); tr = np.ones(len(Yv), bool); tr[idx] = False
    clf = GradientBoostingClassifier(random_state=0, n_estimators=120, max_depth=6).fit(Xb[tr], Yv[tr])
    s = clf.predict_proba(Xb[idx])[:, 1]
    blind_at_gr = _disp_at_grant_rate(s, G_hold, band_gr)

    return {
        "proxy_strength": proxy_strength, "n_band": len(members), **diag,
        "band_worst_disparity": round(band_worst, 4),
        "band_fair_disparity": round(band_fair, 4),
        "worst_minus_fair_spread": round(band_worst - band_fair, 4),
        "blind_flex_at_band_grant_rate": round(blind_at_gr, 4),
        "band_grant_rate": round(band_gr, 4),
    }


def verdict(rows):
    print(f"\n{'='*84}\nAGE INSTANCE (no base-rate alibi): does the band launder disparity through PROXIES ONLY?\n{'='*84}")
    print(f"\n{'proxy':>6} {'base_gap':>9} {'legit_corr':>11} {'proxy_corr':>11} {'band_worst':>11} {'band_fair':>10} {'spread':>8} {'blind@gr':>9}")
    print("-"*84)
    for r in rows:
        if "note" in r:
            print(f"{r['proxy_strength']:>6}  {r['note']}  (base_gap={r.get('base_rate_gap')}, legit_corr={r.get('max_legit_G_corr')})")
            continue
        print(f"{r['proxy_strength']:>6} {r['base_rate_gap']:>9} {r['max_legit_G_corr']:>11} "
              f"{r['proxy_G_corr']:>11} {r['band_worst_disparity']:>11} {r['band_fair_disparity']:>10} "
              f"{r['worst_minus_fair_spread']:>8} {r['blind_flex_at_band_grant_rate']:>9}")
    print()
    real = [r for r in rows if "note" not in r]
    if not real:
        print("  all bands degenerate -- inconclusive."); return
    # control check
    bad = [r for r in real if abs(r["base_rate_gap"]) > 0.03 or r["max_legit_G_corr"] > 0.05]
    if bad:
        print(f"  CONTROL FAIL: {len(bad)} rows have residual base-rate gap or legit-G corr -> alibi NOT cleanly removed; results suspect.")
    else:
        print("  CONTROL OK: base-rate gap ~0 and legit-G corr ~0 across rows -> the lawful alibi IS removed.")
    worsts = [r["band_worst_disparity"] for r in real]
    spreads = [r["worst_minus_fair_spread"] for r in real]
    peak = max(real, key=lambda r: r["band_worst_disparity"])
    print(f"  band WORST-member disparity ranges [{min(worsts):.3f}, {max(worsts):.3f}]; worst-minus-fair spread up to {max(spreads):.3f}")
    if max(worsts) >= 0.03 and max(spreads) >= 0.02:
        print(f"  => P-LAUNDERING-EXPOSED: at proxy={peak['proxy_strength']}, a G-blind 'explainable' band still")
        print(f"     contains a member at {peak['band_worst_disparity']} age-disparity vs a fair member at")
        print(f"     {peak['band_fair_disparity']} -- with ZERO base-rate alibi. 'We used an explainable model'")
        print(f"     is a fig leaf: the band manufactured a discriminatory member, selection unaudited.")
    elif max(worsts) < 0.03:
        print("  => P-FLOOR-WAS-LOAD-BEARING: with equal base rates, band disparity stays small -> lending")
        print("     disparity was mostly the C3 floor; proxy-only age laundering is weak (magnitude argument).")
    else:
        print("  => P-MIXED: proxy disparity present but spread modest; report as a gradient.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--proxy-strengths", type=float, nargs="+", default=[0.5, 1.0, 1.5, 2.0])
    ap.add_argument("--n", type=int, default=20000)
    ap.add_argument("--seed", type=int, default=20260611)
    ap.add_argument("--eps-frac", type=float, default=0.01)
    ap.add_argument("--max-k", type=int, default=3)
    ap.add_argument("--out", default="runs/age_instance_no_floor.json")
    args = ap.parse_args()
    rows = [run(ps, n=args.n, seed=args.seed, eps_frac=args.eps_frac, max_k=args.max_k)
            for ps in args.proxy_strengths]
    for r in rows:
        print(json.dumps(r, default=str))
    verdict(rows)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps({"args": vars(args), "rows": rows}, indent=2, sort_keys=True, default=str))
    print(f"\nwritten to {args.out}")


if __name__ == "__main__":
    main()
