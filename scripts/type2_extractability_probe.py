#!/usr/bin/env python3
"""Is the shuffle-set a type-2 research queue or type-1 noise? (Tony's feedback loop)

Tony's reframe: the "maybe" band splits into TYPE-(1) -- unforeseeable macro
default risk, no extractable signal -- and TYPE-(2) -- individual properties
invisible per-case but visible IN AGGREGATE, on LAWFUL grounds. If the shuffle-
set carries type-2 LAWFUL signal, it is a RESEARCH QUEUE: mine it, fold the new
lawful feature into the next model, and the marginal band shrinks toward
correctly-priced loans (profit) with arbitrariness replaced by justified pricing
(fairness). If it is type-1 noise, the loop is empty: "these are genuinely
unpredictable; stop discriminating in the guess."

TEST: identify the shuffle-set (band members disagree). Fit a default predictor on
shuffle-set TRAIN, score default-AUC on shuffle-set TEST, in two feature regimes:
  (L) LAWFUL: features residualized against G (G-orthogonal component only).
  (F) FULL: all admitted features (may carry G-aligned proxy signal).
Reference (B): the UNANIMOUS population's default-AUC (already-solved cases).

FROZEN PREDICTION (working note frozen before this ran):
  P1 (0.50): AUC_L > 0.55 -> extractable LAWFUL signal -> loop REAL.
  P2 (0.30): AUC_L ~ 0.5 -> type-1 noise -> loop EMPTY.
  P3 (0.20): AUC_L ~ 0.5 but AUC_F >> 0.5 -> predictability is UNLAWFUL proxy only
             -> mining = laundering (D4 trap generalized).
  Decisive: gap AUC_F - AUC_L. Expect D1 small gap (lawful), D4 large gap (proxy).
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
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

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
        name="type2", version="1", status="active", monotonicity_map={},
        mandatory_features=(), prohibited_features=("G",), applicable_regime={})


def _subsets(feat, max_k):
    out = []
    for k in range(1, max_k + 1):
        out.extend(itertools.combinations(feat, k))
    return tuple(out)


def residualize_against_G(Xmat, G):
    """Return the G-orthogonal component of each feature: X - E[X|G] via linear
    projection on G. The lawful (type-2) signal is what's LEFT after removing
    everything linearly predictable from the protected attribute."""
    G2 = G.reshape(-1, 1).astype(float)
    lr = LinearRegression().fit(G2, Xmat)
    return Xmat - lr.predict(G2)


def safe_auc(y, s):
    if len(np.unique(y)) < 2:
        return float("nan")
    return float(roc_auc_score(y, s))


def run(channel, *, n, seed, eps_frac, max_k):
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
        return {"channel": channel, "note": "band<2"}

    # holdout rows (where member predictions live), aligned to original frame index
    _, X_hold, _, _ = inner_split(X, Y, config=cfg)
    hold_idx = np.asarray(X_hold.index)
    preds = np.vstack([np.asarray(m.holdout_y_pred) for m in members])
    flip = preds.min(axis=0) != preds.max(axis=0)  # shuffle-set mask within holdout

    # design matrices on the HOLDOUT (so default labels = realized Y on holdout)
    Xh = X_hold.to_numpy()
    yh = Y.to_numpy()[hold_idx]
    Gh = G[hold_idx]

    def fit_eval(mask, residualize):
        Xs = Xh[mask]; ys = yh[mask]; Gs = Gh[mask]
        if mask.sum() < 200 or len(np.unique(ys)) < 2:
            return float("nan"), int(mask.sum())
        Xin = residualize_against_G(Xs, Gs) if residualize else Xs
        Xtr, Xte, ytr, yte = train_test_split(Xin, ys, test_size=0.4, random_state=0, stratify=ys)
        if len(np.unique(ytr)) < 2 or len(np.unique(yte)) < 2:
            return float("nan"), int(mask.sum())
        clf = GradientBoostingClassifier(random_state=0, n_estimators=100, max_depth=3)
        clf.fit(Xtr, ytr)
        return safe_auc(yte, clf.predict_proba(Xte)[:, 1]), int(mask.sum())

    auc_L, n_shuf = fit_eval(flip, residualize=True)    # lawful (G-orthogonal) on shuffle-set
    auc_F, _ = fit_eval(flip, residualize=False)         # full features on shuffle-set
    auc_B, n_unan = fit_eval(~flip, residualize=False)   # unanimous reference

    return {
        "channel": channel, "n_band": len(members),
        "n_shuffle": n_shuf, "n_unanimous": n_unan,
        "AUC_lawful_shuffle": round(auc_L, 4) if np.isfinite(auc_L) else None,
        "AUC_full_shuffle": round(auc_F, 4) if np.isfinite(auc_F) else None,
        "AUC_full_unanimous_ref": round(auc_B, 4) if np.isfinite(auc_B) else None,
        "gap_full_minus_lawful": round(auc_F - auc_L, 4) if (np.isfinite(auc_F) and np.isfinite(auc_L)) else None,
    }


def verdict(rows):
    print(f"\n{'='*76}\nTYPE-2 EXTRACTABILITY IN THE SHUFFLE-SET\n{'='*76}")
    for r in rows:
        if "note" in r:
            print(f"  {r['channel']}: {r['note']}"); continue
        L = r["AUC_lawful_shuffle"]; F = r["AUC_full_shuffle"]; gap = r["gap_full_minus_lawful"]
        print(f"\n{r['channel']}  (band={r['n_band']}, n_shuffle={r['n_shuffle']}, n_unanimous={r['n_unanimous']})")
        print(f"  AUC lawful (G-orthogonal) on shuffle-set: {L}")
        print(f"  AUC full features on shuffle-set:         {F}")
        print(f"  AUC full on UNANIMOUS (reference):        {r['AUC_full_unanimous_ref']}")
        print(f"  gap (full - lawful):                      {gap}")
        if L is None:
            print("  => insufficient data"); continue
        if L > 0.55:
            print(f"  => P1: LAWFUL signal extractable (AUC_L={L}>0.55) -> shuffle-set is a TYPE-2 RESEARCH QUEUE, loop REAL.")
        elif F is not None and F > 0.55 and L <= 0.55:
            print(f"  => P3: predictability is UNLAWFUL-only (AUC_F={F}>0.55, AUC_L={L}~0.5) -> mining = laundering (D4 trap).")
        else:
            print(f"  => P2: ~type-1 NOISE (AUC_L={L}~0.5, AUC_F={F}) -> loop EMPTY; honest 'stop guessing'.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--channels", nargs="+", default=["D1", "D2", "D3", "D4"])
    ap.add_argument("--n", type=int, default=30000)
    ap.add_argument("--seed", type=int, default=20260610)
    ap.add_argument("--eps-frac", type=float, default=0.01)
    ap.add_argument("--max-k", type=int, default=3)
    ap.add_argument("--out", default="runs/type2_extractability.json")
    args = ap.parse_args()
    rows = [run(c, n=args.n, seed=args.seed, eps_frac=args.eps_frac, max_k=args.max_k)
            for c in args.channels]
    for r in rows:
        print(json.dumps(r, default=str))
    verdict(rows)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps({"args": vars(args), "rows": rows}, indent=2, sort_keys=True, default=str))
    print(f"\nwritten to {args.out}")


if __name__ == "__main__":
    main()
