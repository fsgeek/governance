#!/usr/bin/env python3
"""Does floor-band multiplicity grow with encoding redundancy k? (the canary test)

Pre-registration: working_notes/2026-06-10-redundancy-mechanism-prereg.md (FROZEN).
Fable's conjecture: detection-difficulty and floor-multiplicity share a common
cause -- REDUNDANT encoding. "Individually innocent, jointly disparate" spreads
the disparity across k weak exchangeable proxies; exchangeability generates
model multiplicity. If true, band>1 at the tightest epsilon is a DISTRIBUTED-
SIGNAL DETECTOR (a fairwash canary), reborn from the failed protected-detector.

Clean purpose-built toy (the frozen fairwash DGP's D4_K is a fixed constant and
the DGP is OTS-frozen, so we do NOT touch it). Here k is a first-class knob and
TOTAL disparity is held FIXED across k -- only the SPREAD changes -- so flip-rate
moves with redundancy, not effect size (covariate-adjust-all-arm-correlates).

FROZEN PREDICTION (from the pre-reg, restated):
  P1 (0.65): floor flip-rate rises monotonically with k.
  P3 guard (0.25): non-monotone/threshold instead of smooth.
  (P2 cross-family is a separate build, flagged.)
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd

from policy.encoder import PolicyConstraints
from wedge.rashomon import (
    SweepConfig, evaluate_policy, filter_to_epsilon_under_loss, hyperparameter_sweep,
)
from wedge.losses import grant_emphasis_loss
from wedge.band_disagreement import band_disagreement_summary


def make_redundant_dgp(k: int, *, n: int, seed: int, total_disparity: float):
    """Disparity of FIXED total magnitude spread across k weak proxies.

    G is the protected attribute. The disparity signal s = total_disparity * (G -
    mean) is distributed across k carriers c_1..c_k, each carrying s/k plus noise
    (so per-carrier |corr(c_j, G)| shrinks as k grows -> 'individually innocent').
    Two legit features x0,x1 carry honest risk. Y depends on x0,x1 AND the SUM of
    carriers (= the full disparity, magnitude FIXED across k). G is prohibited;
    carriers are admitted. As k rises the SAME total disparity is encoded more
    redundantly -- the only thing that changes."""
    rng = np.random.default_rng(seed)
    x0 = rng.standard_normal(n)
    x1 = rng.standard_normal(n)
    G = (rng.random(n) < 0.3).astype(int)
    g_c = G - G.mean()
    s = total_disparity * g_c  # fixed-magnitude disparity signal

    carriers = {}
    # each carrier gets s/k of the signal + independent noise. CRITICAL: scale
    # per-carrier noise so the SUMMED noise variance is k-INVARIANT (k carriers
    # each with sd b/sqrt(k) sum to variance b^2). Otherwise summed noise grows
    # with k and dilutes the realized disparity = an effect-size confound (the
    # first run's guard caught exactly this). Holds total disparity fixed across k.
    noise_sd = 0.8 / np.sqrt(k)
    for j in range(k):
        carriers[f"c{j}"] = (s / k) + noise_sd * rng.standard_normal(n)
    carrier_sum = np.sum([carriers[f"c{j}"] for j in range(k)], axis=0)
    # Y logit: honest risk + the full disparity (carrier_sum reconstructs s in
    # expectation since the k carriers sum to s + noise). Coefficient on
    # carrier_sum scaled by k so the EXPECTED disparity contribution is k-invariant.
    logit = 0.8 * x0 + 0.6 * x1 + (1.0 / 1.0) * carrier_sum
    p = 1.0 / (1.0 + np.exp(-logit))
    Y = (rng.random(n) < p).astype(int)

    cols = {"x0": x0, "x1": x1, **carriers, "G": G, "Y": Y}
    frame = pd.DataFrame(cols)
    feat = ["x0", "x1"] + [f"c{j}" for j in range(k)]
    return frame, feat


def policy():
    return PolicyConstraints(
        name="redundancy_canary", version="1", status="active", monotonicity_map={},
        mandatory_features=(), prohibited_features=("G",), applicable_regime={})


def _subsets(feat, max_k):
    out = []
    for kk in range(1, max_k + 1):
        out.extend(itertools.combinations(feat, kk))
    return tuple(out)


def floor_flip_rate(k: int, *, n, seed, total_disparity, max_subset_k, eps_frac):
    frame, feat = make_redundant_dgp(k, n=n, seed=seed, total_disparity=total_disparity)
    Y = frame["Y"].astype(int)
    X = frame[feat]
    cfg = SweepConfig(max_depths=(4, 6, 8), min_samples_leafs=(50, 100, 200),
                      feature_subsets=_subsets(feat, max_subset_k),
                      random_state=seed, holdout_fraction=0.30)
    adm = evaluate_policy(hyperparameter_sweep(X, Y, config=cfg), policy_constraints=policy())
    if not adm.admissible:
        return {"k": k, "error": "no admissible"}
    nh = len(np.asarray(adm.admissible[0].holdout_y_true))
    tol = eps_frac * nh
    band = filter_to_epsilon_under_loss(
        adm, loss_fn=lambda yt, yh: grant_emphasis_loss(yt, yh, w_T=1.5),
        loss_label="L_T(w_T=1.5)", epsilon=tol)
    summ = band_disagreement_summary(band)
    # measure realized disparity magnitude (to confirm it's k-invariant)
    G = frame["G"].to_numpy()
    base = Y.to_numpy()
    disparity = float(base[G == 1].mean() - base[G == 0].mean())
    return {"k": k, "n_band": summ["n_members"], "flip_rate": summ["flip_rate"],
            "realized_grant_gap_G": round(disparity, 4),
            "n_admissible": len(adm.admissible)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=12000)
    ap.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3])
    ap.add_argument("--ks", type=int, nargs="+", default=[1, 2, 3, 5, 8])
    ap.add_argument("--total-disparity", type=float, default=2.0)
    ap.add_argument("--eps-frac", type=float, default=0.001, help="tightest band")
    ap.add_argument("--max-subset-k", type=int, default=3)
    ap.add_argument("--out", default="runs/redundancy_canary_probe.json")
    args = ap.parse_args()

    rows = []
    for k in args.ks:
        frs, gaps, bands = [], [], []
        for sd in args.seeds:
            r = floor_flip_rate(k, n=args.n, seed=sd, total_disparity=args.total_disparity,
                                max_subset_k=args.max_subset_k, eps_frac=args.eps_frac)
            if "error" not in r:
                frs.append(r["flip_rate"]); gaps.append(r["realized_grant_gap_G"]); bands.append(r["n_band"])
        rows.append({"k": k, "mean_flip_rate": round(float(np.mean(frs)), 4) if frs else None,
                     "flip_rates": frs, "mean_band": round(float(np.mean(bands)), 1) if bands else None,
                     "mean_realized_gap_G": round(float(np.mean(gaps)), 4) if gaps else None})

    print(f"\n{'='*70}\nREDUNDANCY CANARY: floor flip-rate vs k (total disparity FIXED)\n{'='*70}")
    print(f"{'k':>3} {'mean_band':>10} {'mean_flip_rate':>15} {'realized_gap_G':>15}")
    for r in rows:
        print(f"{r['k']:>3} {str(r['mean_band']):>10} {str(r['mean_flip_rate']):>15} {str(r['mean_realized_gap_G']):>15}")

    frs = [r["mean_flip_rate"] for r in rows if r["mean_flip_rate"] is not None]
    print(f"\n{'='*70}\nVERDICT\n{'='*70}")
    if len(frs) >= 2:
        monotone = all(frs[i] <= frs[i + 1] + 1e-9 for i in range(len(frs) - 1))
        rising = frs[-1] > frs[0]
        gaps = [r["mean_realized_gap_G"] for r in rows if r["mean_realized_gap_G"] is not None]
        gap_stable = (max(gaps) - min(gaps)) < 0.05 if gaps else False
        print(f"flip-rate by k: {frs}")
        print(f"realized disparity gap by k: {gaps} (stable={gap_stable} -- must be ~fixed)")
        if not gap_stable:
            print("WARNING: disparity gap NOT k-invariant -- effect-size confound, fix DGP scaling.")
        if monotone and rising:
            print("P1 HELD: floor flip-rate rises monotonically with k at FIXED disparity.")
            print("=> redundancy is a common cause; band>1 at floor is a distributed-signal CANARY.")
        elif rising:
            print("P3: flip-rate rises but NON-monotonically -- common cause supported, calibration noisy.")
        else:
            print("P1 REFUTED: flip-rate does NOT rise with k -- redundancy is not the multiplicity driver.")

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps({"args": vars(args), "rows": rows}, indent=2, sort_keys=True))
    print(f"\nwritten to {args.out}")


if __name__ == "__main__":
    main()
