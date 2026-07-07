#!/usr/bin/env python3
"""Within the band, are profit and disparity the same axis? (Tony's pitch test)

Tony's reframe: "pick one" as a dice roll is the WASTEFUL use of the band. If
all members are tied on accuracy, the choice among them is free on the accuracy
axis -- so select on a SECOND objective at zero accuracy cost. The persuasive
bank pitch: "build the ensemble this way and you can INCREASE PROFITABILITY while
holding discrimination at the floor" -- do well by doing right.

This is TRUE iff, within the ε-band, PROFIT and DISPARITY are NOT the same axis.
If the profitable members are also the discriminatory ones (positive coupling),
the pitch dies: profit is bought WITH disparity. If orthogonal/negative, the
ensemble can select a high-profit low-disparity member that DOMINATES the random
pick on both axes.

Profit per decision (standard lending EV): grant+repaid = +r ; grant+default =
-1 ; deny = 0. Disparity(member) = P(grant|G=1) - P(grant|G=0) on its decisions.
G is the ground-truth protected attribute (synthetic substrate); G is PROHIBITED
as a model feature.

FROZEN PREDICTION (working note frozen before this ran):
  P1 (0.45): corr(profit, |disparity|) > 0 across band members -- pitch DIES.
  P2 (0.40): ~orthogonal -- pitch REAL, dominating corner exists.
  P3 (0.15): negative -- profit & fairness pull the same way.
  Decisive: is the random-pick (profit, disparity) INTERIOR to the band's Pareto
  frontier? If yes, the ensemble strictly beats the dice roll. And: is profit at
  the min-disparity (floor) member >= mean profit (does staying at the floor cost
  money)?
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

from policy.encoder import PolicyConstraints
from wedge.rashomon import (
    SweepConfig, evaluate_policy, filter_to_epsilon_under_loss,
    hyperparameter_sweep, inner_split,
)
from wedge.losses import grant_emphasis_loss


def _load(mod, path):
    spec = importlib.util.spec_from_file_location(mod, path)
    assert spec is not None and spec.loader is not None
    m = importlib.util.module_from_spec(spec); sys.modules[mod] = m
    spec.loader.exec_module(m); return m


_DGP = _load("fairwash_frontier_dgp", str(Path(__file__).with_name("fairwash_frontier_dgp.py")))


def policy():
    return PolicyConstraints(
        name="profit_disparity", version="1", status="active", monotonicity_map={},
        mandatory_features=(), prohibited_features=("G",), applicable_regime={})


def _subsets(feat, max_k):
    out = []
    for k in range(1, max_k + 1):
        out.extend(itertools.combinations(feat, k))
    return tuple(out)


def member_profit(y_pred, y_true, r):
    """Sum EV: grant(pred=1) & repaid(y=1) -> +r ; grant & default(y=0) -> -1 ;
    deny(pred=0) -> 0. Per-decision profit summed over holdout."""
    grant = y_pred == 1
    return float(np.sum(np.where(grant, np.where(y_true == 1, r, -1.0), 0.0)))


def member_disparity(y_pred, G):
    g1 = G == 1; g0 = G == 0
    if not g1.any() or not g0.any():
        return float("nan")
    return float(y_pred[g1].mean() - y_pred[g0].mean())


def run(channel, *, n, seed, eps_frac, max_k, r):
    dgp = _DGP.generate(channel, n=n, seed=seed)
    frame = dgp.frame
    Y = frame["Y"].astype(int)
    feat = [c for c in frame.columns if c not in ("G", "Y")]
    X = frame[feat]
    G = frame["G"].to_numpy()

    cfg = SweepConfig(max_depths=(4, 6, 8, 10), min_samples_leafs=(25, 50, 100, 200),
                      feature_subsets=_subsets(feat, max_k), random_state=seed,
                      holdout_fraction=0.30)
    adm = evaluate_policy(hyperparameter_sweep(X, Y, config=cfg), policy_constraints=policy())
    nh = len(np.asarray(adm.admissible[0].holdout_y_true))
    tol = eps_frac * nh
    band = filter_to_epsilon_under_loss(
        adm, loss_fn=lambda yt, yh: grant_emphasis_loss(yt, yh, w_T=1.5),
        loss_label="L_T(w_T=1.5)", epsilon=tol)
    members = band.within_epsilon
    if len(members) < 2:
        return {"channel": channel, "n_band": len(members), "note": "band<2"}

    _, X_hold, _, _ = inner_split(X, Y, config=cfg)
    G_hold = G[np.asarray(X_hold.index)]
    y_true = np.asarray(members[0].holdout_y_true)

    profits, disps = [], []
    for m in members:
        yp = np.asarray(m.holdout_y_pred)
        profits.append(member_profit(yp, y_true, r))
        disps.append(member_disparity(yp, G_hold))
    profits = np.array(profits); disps = np.array(disps); absd = np.abs(disps)

    corr_profit_absdisp = float(np.corrcoef(profits, absd)[0, 1]) if profits.std() > 0 and absd.std() > 0 else float("nan")

    # random-pick expectation (mean over members)
    rand_profit = float(profits.mean()); rand_absdisp = float(absd.mean())
    # floor = min |disparity| member; its profit
    floor_i = int(np.argmin(absd))
    floor_profit = float(profits[floor_i]); floor_absdisp = float(absd[floor_i])
    # max-profit member
    maxp_i = int(np.argmax(profits))
    # the SELECTABLE corner: among members within 1.05x of min |disparity|, the
    # highest-profit one (stay near the floor, maximize profit there)
    near_floor = absd <= (absd.min() + 0.02)
    sel_i = int(np.arange(len(profits))[near_floor][np.argmax(profits[near_floor])])
    sel_profit = float(profits[sel_i]); sel_absdisp = float(absd[sel_i])

    # does a member DOMINATE the random pick on BOTH axes (>= profit AND <= |disp|)?
    dominates = (profits >= rand_profit) & (absd <= rand_absdisp)
    n_dominating = int(dominates.sum())

    return {
        "channel": channel, "n_band": len(members),
        "r": r,
        "corr_profit_absdisparity": round(corr_profit_absdisp, 4),
        "profit_range": [round(float(profits.min()), 1), round(float(profits.max()), 1)],
        "absdisp_range": [round(float(absd.min()), 4), round(float(absd.max()), 4)],
        "random_pick": {"profit": round(rand_profit, 1), "absdisp": round(rand_absdisp, 4)},
        "floor_member": {"profit": round(floor_profit, 1), "absdisp": round(floor_absdisp, 4)},
        "max_profit_member": {"profit": round(float(profits[maxp_i]), 1), "absdisp": round(float(absd[maxp_i]), 4)},
        "selectable_corner_near_floor": {"profit": round(sel_profit, 1), "absdisp": round(sel_absdisp, 4)},
        "n_members_dominating_random": n_dominating,
        "floor_profit_vs_random": round(floor_profit - rand_profit, 1),
    }


def verdict(rows):
    print(f"\n{'='*76}\nPROFIT x DISPARITY FRONTIER (within the band)\n{'='*76}")
    for r in rows:
        if "note" in r:
            print(f"  {r['channel']}: {r['note']}"); continue
        c = r["corr_profit_absdisparity"]
        print(f"\n{r['channel']}  (band={r['n_band']}, r={r['r']})")
        print(f"  corr(profit, |disparity|) = {c}")
        print(f"  random pick:      profit={r['random_pick']['profit']:>8}  |disp|={r['random_pick']['absdisp']}")
        print(f"  floor member:     profit={r['floor_member']['profit']:>8}  |disp|={r['floor_member']['absdisp']}")
        print(f"  selectable corner:profit={r['selectable_corner_near_floor']['profit']:>8}  |disp|={r['selectable_corner_near_floor']['absdisp']}")
        print(f"  max-profit member:profit={r['max_profit_member']['profit']:>8}  |disp|={r['max_profit_member']['absdisp']}")
        print(f"  members dominating random (>=profit AND <=|disp|): {r['n_members_dominating_random']}")
        print(f"  floor profit - random profit = {r['floor_profit_vs_random']} "
              f"({'staying at floor is FREE/PROFITABLE' if r['floor_profit_vs_random'] >= 0 else 'staying at floor COSTS money'})")
        if c is not None:
            if c > 0.2:
                tag = "P1: profit POSITIVELY coupled to disparity -- pitch WEAKENED (profit bought with disparity)"
            elif c < -0.2:
                tag = "P3: profit NEGATIVELY coupled -- pitch STRONGER than asked (profit & fairness aligned)"
            else:
                tag = "P2: ~orthogonal -- pitch REAL (can select high-profit low-disparity)"
            print(f"  => {tag}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--channels", nargs="+", default=["D1", "D2", "D3", "D4"])
    ap.add_argument("--n", type=int, default=20000)
    ap.add_argument("--seed", type=int, default=20260610)
    ap.add_argument("--eps-frac", type=float, default=0.01)
    ap.add_argument("--max-k", type=int, default=3)
    ap.add_argument("--r", type=float, default=0.25, help="interest yield on a repaid loan")
    ap.add_argument("--out", default="runs/profit_disparity_frontier.json")
    args = ap.parse_args()
    rows = [run(c, n=args.n, seed=args.seed, eps_frac=args.eps_frac, max_k=args.max_k, r=args.r)
            for c in args.channels]
    for r in rows:
        print(json.dumps(r, default=str))
    verdict(rows)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps({"args": vars(args), "rows": rows}, indent=2, sort_keys=True, default=str))
    print(f"\nwritten to {args.out}")


if __name__ == "__main__":
    main()
