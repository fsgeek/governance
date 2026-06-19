#!/usr/bin/env python3
"""Does mining the type-2 signal CLOSE the loop: shrink the band AND cut disparity?

The keystone of Tony's pitch. Premise established ([[2026-06-10-type2-research-
queue]]): the shuffle-set carries extractable LAWFUL default signal. This tests
the CLOSURE: extract that signal as a legitimate engineered feature, add it, and
check whether the rebuilt band has fewer coin-flips (lower flip_rate) and no more
disparity. If yes, "do well by doing right" is demonstrated end-to-end.

NO LEAKAGE: the lawful predictor is trained on a HELD-ASIDE split (X_engineer);
its score is applied as a feature on the MODELING split (X_model). The band is
built and measured on X_model. The engineered feature is the G-ORTHOGONAL
default predictor's score -- a lawful aggregate type-2 feature.

FROZEN PREDICTION (working note frozen before run):
  P1 (0.55): flip_rate DROPS and mean |disparity| drops/holds -> loop CLOSES.
  P2 (0.25): flip_rate drops, disparity RISES -> linear-orthogonality caveat bites.
  P3 (0.20): flip_rate unchanged -> arbitrariness wasn't about this signal.
  Decisive: (delta flip_rate, delta disparity). Use D1 (clean). If it doesn't
  close on D1 it closes nowhere.
"""
from __future__ import annotations

import argparse
import importlib.util
import itertools
import sys
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LinearRegression

from policy.encoder import PolicyConstraints
from wedge.rashomon import (
    SweepConfig, evaluate_policy, filter_to_epsilon_under_loss,
    hyperparameter_sweep, inner_split,
)
from wedge.losses import grant_emphasis_loss
from wedge.band_disagreement import band_disagreement_summary


def _load(mod, path):
    spec = importlib.util.spec_from_file_location(mod, path)
    assert spec is not None and spec.loader is not None
    m = importlib.util.module_from_spec(spec); sys.modules[mod] = m
    spec.loader.exec_module(m); return m


_DGP = _load("fairwash_frontier_dgp", str(Path(__file__).with_name("fairwash_frontier_dgp.py")))


def policy(prohibited=("G",)):
    return PolicyConstraints(
        name="loop_closure", version="1", status="active", monotonicity_map={},
        mandatory_features=(), prohibited_features=tuple(prohibited), applicable_regime={})


def _subsets(feat, max_k):
    out = []
    for k in range(1, max_k + 1):
        out.extend(itertools.combinations(feat, k))
    return tuple(out)


def build_and_measure(X, Y, G, feat, seed, eps_frac, max_k):
    cfg = SweepConfig(max_depths=(4, 6, 8, 10), min_samples_leafs=(25, 50, 100, 200),
                      feature_subsets=_subsets(feat, max_k), random_state=seed,
                      holdout_fraction=0.30)
    adm = evaluate_policy(hyperparameter_sweep(X[feat], Y, config=cfg), policy_constraints=policy())
    if not adm.admissible:
        return None
    nh = len(np.asarray(adm.admissible[0].holdout_y_true))
    tol = eps_frac * nh
    band = filter_to_epsilon_under_loss(
        adm, loss_fn=lambda yt, yh: grant_emphasis_loss(yt, yh, w_T=1.5),
        loss_label="L_T(w_T=1.5)", epsilon=tol)
    summ = band_disagreement_summary(band)
    members = band.within_epsilon
    # mean realized |disparity| across band members on the holdout
    _, X_hold, _, _ = inner_split(X[feat], Y, config=cfg)
    G_hold = G[np.asarray(X_hold.index)]
    disps = []
    for m in members:
        yp = np.asarray(m.holdout_y_pred)
        if (G_hold == 1).any() and (G_hold == 0).any():
            disps.append(abs(yp[G_hold == 1].mean() - yp[G_hold == 0].mean()))
    mean_absdisp = float(np.mean(disps)) if disps else float("nan")
    best_auc = max((m.holdout_auc for m in members), default=float("nan"))
    return {"n_band": summ["n_members"], "flip_rate": summ["flip_rate"],
            "mean_absdisp": round(mean_absdisp, 4), "best_auc": round(float(best_auc), 4)}


def run(channel, *, n, seed, eps_frac, max_k):
    dgp = _DGP.generate(channel, n=n, seed=seed)
    frame = dgp.frame.reset_index(drop=True)
    base_feat = [c for c in frame.columns if c not in ("G", "Y")]

    # split: engineer (train the lawful predictor) vs model (build/measure band)
    rng = np.random.default_rng(seed)
    idx = np.arange(len(frame)); rng.shuffle(idx)
    half = len(idx) // 2
    eng, mod = idx[:half], idx[half:]

    Xe, Ye, Ge = frame.loc[eng, base_feat], frame.loc[eng, "Y"].astype(int).to_numpy(), frame.loc[eng, "G"].to_numpy()
    Xm = frame.loc[mod, base_feat].reset_index(drop=True)
    Ym = frame.loc[mod, "Y"].astype(int).reset_index(drop=True)
    Gm = frame.loc[mod, "G"].to_numpy()

    # ROUND 0: band on base features (modeling split)
    r0 = build_and_measure(Xm, Ym, Gm, base_feat, seed, eps_frac, max_k)

    # MINING: train a LAWFUL (G-orthogonal) default predictor on the ENGINEER split,
    # apply its score as a new feature on the MODELING split. G-orthogonal: residualize
    # features against G before fitting, so the learned signal is the lawful component.
    Xe_arr = Xe.to_numpy()
    G2e = Ge.reshape(-1, 1).astype(float)
    res = LinearRegression().fit(G2e, Xe_arr)
    Xe_orth = Xe_arr - res.predict(G2e)
    clf = GradientBoostingClassifier(random_state=0, n_estimators=100, max_depth=3)
    clf.fit(Xe_orth, Ye)
    # apply to modeling split: residualize Xm against G using the SAME projector, score
    Xm_arr = Xm.to_numpy()
    G2m = Gm.reshape(-1, 1).astype(float)
    Xm_orth = Xm_arr - res.predict(G2m)  # reuse engineer-split projector (no leak)
    lawful_score = clf.predict_proba(Xm_orth)[:, 1]
    Xm2 = Xm.copy()
    Xm2["lawful_type2"] = lawful_score
    feat2 = base_feat + ["lawful_type2"]

    # ROUND 1: band WITH the lawful feature
    r1 = build_and_measure(Xm2, Ym, Gm, feat2, seed, eps_frac, max_k)

    return {"channel": channel, "round0": r0, "round1": r1,
            "delta_flip_rate": round(r1["flip_rate"] - r0["flip_rate"], 4) if (r0 and r1) else None,
            "delta_absdisp": round(r1["mean_absdisp"] - r0["mean_absdisp"], 4) if (r0 and r1) else None,
            "delta_best_auc": round(r1["best_auc"] - r0["best_auc"], 4) if (r0 and r1) else None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--channels", nargs="+", default=["D1", "D4"])
    ap.add_argument("--n", type=int, default=30000)
    ap.add_argument("--seed", type=int, default=20260610)
    ap.add_argument("--eps-frac", type=float, default=0.01)
    ap.add_argument("--max-k", type=int, default=3)
    ap.add_argument("--out", default="runs/loop_closure.json")
    args = ap.parse_args()
    rows = [run(c, n=args.n, seed=args.seed, eps_frac=args.eps_frac, max_k=args.max_k)
            for c in args.channels]
    print(f"\n{'='*72}\nLOOP CLOSURE: mine type-2 -> rebuild band\n{'='*72}")
    for r in rows:
        print(f"\n{r['channel']}:")
        print(f"  round0 (base):       {r['round0']}")
        print(f"  round1 (+lawful):    {r['round1']}")
        print(f"  delta flip_rate={r['delta_flip_rate']}  delta |disparity|={r['delta_absdisp']}  delta best_auc={r['delta_best_auc']}")
        df, dd = r["delta_flip_rate"], r["delta_absdisp"]
        if df is not None and dd is not None:
            if df < -0.005 and dd <= 0.005:
                print("  => P1 CLOSES: band SHRINKS and disparity holds/drops. Do-well-by-doing-right demonstrated.")
            elif df < -0.005 and dd > 0.005:
                print("  => P2: band shrinks but disparity RISES (nonlinear-G residue) -- partial closure.")
            else:
                print("  => P3: flip_rate not reduced -- arbitrariness wasn't about this signal.")
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps({"args": vars(args), "rows": rows}, indent=2, sort_keys=True, default=str))
    print(f"\nwritten to {args.out}")


if __name__ == "__main__":
    main()
