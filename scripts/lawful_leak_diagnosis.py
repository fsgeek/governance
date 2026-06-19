#!/usr/bin/env python3
"""Why did adding the 'lawful' feature RAISE disparity? Leak, or the C3 floor?

Loop closure ([[2026-06-10-loop-closure-and-fable-corrections]]) showed the
band shrinks but disparity RISES when the lawful type-2 feature is added. Fable:
the linear orthogonalization is the weak operator. But with BINARY G, linear
residualization already removes the full E[feature|G] (group means) -- so the
leak, if any, is in the JOINT/score path, not the marginal feature path. Two
competing explanations:

  LEAK: the lawful SCORE f(X_orth) still predicts G nonlinearly from the joint of
        residualized features -> AUC(G ~ score) > 0.55 -> laundered, fixable by
        score-level orthogonalization.
  C3:   the score does NOT predict G (AUC_G ~ 0.5) yet disparity still rose ->
        the rise is NOT a leak. It's that adding ANY accurate predictor raises
        MEASURED group-disparity-in-grants when base DEFAULT RATES differ by G
        (a better model denies the higher-risk group more -- and risk correlates
        with G for lawful reasons). That is the C3 floor in its sharpest form and
        is NOT fixable by orthogonalization.

FROZEN PREDICTION:
  P1 (0.50): AUC(G~score) > 0.55 -> leak in the joint path.
  P2 (0.35): AUC(G~score) ~ 0.5 AND base default rate differs by G -> C3, not leak.
  P3 (0.15): score predicts G and score-orthogonalization fixes disparity -> operator.
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
import json
from pathlib import Path

import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LinearRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split


def _load(mod, path):
    spec = importlib.util.spec_from_file_location(mod, path)
    assert spec is not None and spec.loader is not None
    m = importlib.util.module_from_spec(spec); sys.modules[mod] = m
    spec.loader.exec_module(m); return m


_DGP = _load("fairwash_frontier_dgp", str(Path(__file__).with_name("fairwash_frontier_dgp.py")))


def run(channel, *, n, seed):
    dgp = _DGP.generate(channel, n=n, seed=seed)
    fr = dgp.frame
    feat = [c for c in fr.columns if c not in ("G", "Y")]
    X = fr[feat].to_numpy(); Y = fr["Y"].to_numpy(); G = fr["G"].to_numpy()

    Xtr, Xte, ytr, yte, Gtr, Gte = train_test_split(X, Y, G, test_size=0.4, random_state=0, stratify=Y)

    # lawful predictor on LINEARLY-G-orthogonalized features
    G2 = Gtr.reshape(-1, 1).astype(float)
    proj = LinearRegression().fit(G2, Xtr)
    Xtr_o = Xtr - proj.predict(G2)
    Xte_o = Xte - proj.predict(Gte.reshape(-1, 1).astype(float))
    clf = GradientBoostingClassifier(random_state=0, n_estimators=100, max_depth=3).fit(Xtr_o, ytr)
    score_te = clf.predict_proba(Xte_o)[:, 1]

    # 1) does the 'lawful' SCORE still predict G? (joint/nonlinear leak test)
    auc_g_from_score = float(roc_auc_score(Gte, score_te)) if len(np.unique(Gte)) > 1 else float("nan")
    # also: linear corr of score with G (should be ~0 by construction of inputs; check)
    corr_score_G = float(np.corrcoef(score_te, Gte)[0, 1])

    # 2) base default rate by G (the C3 driver): does P(default) differ by group?
    base_rate_g1 = float(yte[Gte == 1].mean()); base_rate_g0 = float(yte[Gte == 0].mean())

    # 3) the C3 mechanism directly: a THRESHOLD on the lawful score (deny worst risk)
    #    -> does grant-rate differ by G even though the score is (nearly) G-blind?
    thr = np.quantile(score_te, 0.3)  # deny the riskiest 30% by lawful score
    grant = (score_te < thr).astype(int)  # low default score -> grant
    grant_rate_g1 = float(grant[Gte == 1].mean()); grant_rate_g0 = float(grant[Gte == 0].mean())
    grant_disparity_from_lawful = grant_rate_g1 - grant_rate_g0

    return {
        "channel": channel,
        "AUC_G_from_lawful_score": round(auc_g_from_score, 4),
        "corr_score_G": round(corr_score_G, 4),
        "base_default_rate_G1": round(base_rate_g1, 4),
        "base_default_rate_G0": round(base_rate_g0, 4),
        "base_rate_gap": round(base_rate_g1 - base_rate_g0, 4),
        "grant_disparity_from_pure_lawful_threshold": round(grant_disparity_from_lawful, 4),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--channels", nargs="+", default=["D1", "D2", "D3", "D4"])
    ap.add_argument("--n", type=int, default=30000)
    ap.add_argument("--seed", type=int, default=20260610)
    ap.add_argument("--out", default="runs/lawful_leak_diagnosis.json")
    args = ap.parse_args()
    rows = [run(c, n=args.n, seed=args.seed) for c in args.channels]
    print(f"\n{'='*76}\nLAWFUL-FEATURE: LEAK or C3 FLOOR?\n{'='*76}")
    for r in rows:
        print(f"\n{r['channel']}:")
        print(f"  AUC(G ~ lawful score) = {r['AUC_G_from_lawful_score']}  (>0.55 => joint-path LEAK)")
        print(f"  corr(score, G)        = {r['corr_score_G']}")
        print(f"  base default rate: G1={r['base_default_rate_G1']} G0={r['base_default_rate_G0']} gap={r['base_rate_gap']}")
        print(f"  grant disparity from a PURE lawful-score threshold = {r['grant_disparity_from_pure_lawful_threshold']}")
        auc_g = r["AUC_G_from_lawful_score"]; gd = r["grant_disparity_from_pure_lawful_threshold"]
        if auc_g > 0.55:
            print("  => LEAK: the lawful score predicts G (joint/nonlinear path). Score-orthogonalization needed.")
        elif abs(gd) > 0.03 and r["base_rate_gap"] != 0:
            print("  => C3 FLOOR: score ~G-blind yet a pure-lawful threshold STILL creates grant disparity,")
            print("     because base default rates differ by G. NOT fixable by orthogonalization. The deep finding.")
        else:
            print("  => neither strongly: disparity rise may be band-construction noise; inspect.")
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps({"args": vars(args), "rows": rows}, indent=2, sort_keys=True))
    print(f"\nwritten to {args.out}")


if __name__ == "__main__":
    main()
