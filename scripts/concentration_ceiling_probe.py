#!/usr/bin/env python3
"""Does the POLICY-CONSTRAINED BAND suppress distributed disparity, or is distributed
disparity just intrinsically unconcentratable by any bounded model?

Established tonight (runs/attestation_d3_multiseed.json + DGP label arithmetic):
  - D4 injects a LABEL-level demographic-parity gap of ~0.12 (NOT near-G-blind;
    the boring "nothing to concentrate" story is REFUTED by arithmetic).
  - Yet the band's worst (max-profit) G-BLIND member surfaces only ~0.013 disparity.
  - On D1, injected 0.178 -> worst member 0.145 (~80% concentrated).
  - On D4, injected 0.120 -> worst member 0.013 (~11% concentrated). A 9x gap.

REMAINING FORK (the only deflation the arithmetic did NOT kill):
  R2-real:    the BAND (explainability + policy constraint) is what suppresses D4
              concentration. A G-AWARE / unconstrained model CAN concentrate it.
  intrinsic:  distributed sub-alpha signal is unconcentratable by ANY bounded model,
              G-aware or not. The band gets no special credit; the smear is the whole
              mechanism. "Policy-constrained band protects against distributed
              laundering" would be an OVERCLAIM.

This probe measures, per channel, the MAX disparity concentrable by:
  (a) CEILING_Gaware    : a model ALLOWED to use G directly (upper bound on
                          concentratable disparity for this model class).
  (b) CEILING_unconstr  : a flexible G-BLIND model with NO policy/depth constraint
                          (GradientBoosting deep) -- can a strong blind learner do it?
  (c) BAND_envelope     : MISLABELED -- this is a bare shallow G-blind CART sweep, NOT
                          the policy-constrained admissible band. On D4 it returns ~0.098,
                          ~8x the ACTUAL band worst-member (0.013 from the attestation
                          multiseed). A bare CART can split freely on c_fresh; the real
                          band (evaluate_policy + filter_to_epsilon loss-tie + feature-
                          subset admissibility) is what crushes D4 to 0.013. DO NOT read
                          this column as the band envelope. Rebuild with the real pipeline
                          before attributing distributed-disparity suppression to the band.
Disparity is measured as |P(grant|G=1) - P(grant|G=0)| at a fixed 30%-deny threshold,
matched across all three so the comparison is apples-to-apples.

FROZEN PREDICTION (frozen after the label-arithmetic, before this ran):
  P-R2-real  (0.45): on D4, CEILING_Gaware >> BAND_envelope (>=0.05 vs ~0.013) AND
                     CEILING_Gaware notably exceeds CEILING_unconstr -> it takes G
                     ITSELF to concentrate distributed disparity; the blind constraint
                     is what protects. Structural protection finding for the centerpiece.
  P-intrinsic(0.45): on D4, CEILING_Gaware also stays low (<=0.025) -> distributed
                     disparity is intrinsically unconcentratable; band gets no credit.
  P-mixed    (0.10): 0.025-0.05.
  CONTRAST: on D1 all three ceilings should be HIGH (~0.12-0.18) -- direct disparity
  is concentrable by everyone, so D1 is the positive control that the probe can
  detect concentration AT ALL.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split


def _load(mod, path):
    spec = importlib.util.spec_from_file_location(mod, path)
    assert spec is not None and spec.loader is not None
    m = importlib.util.module_from_spec(spec); sys.modules[mod] = m
    spec.loader.exec_module(m); return m


_DGP = _load("fairwash_frontier_dgp", str(Path(__file__).with_name("fairwash_frontier_dgp.py")))


def _pos_score(clf, X):
    """P(class=1), robust to a model that saw only one class (predict_proba then
    returns a single column). Returns the positive-class probability or, if the
    sole class is 0, a constant 0 vector."""
    p = clf.predict_proba(X)
    classes = list(clf.classes_)
    if 1 in classes:
        return p[:, classes.index(1)]
    return np.zeros(p.shape[0])


def _disparity_at_threshold(score, G, deny_frac=0.30):
    """|P(grant|G=1) - P(grant|G=0)| where grant = score below the deny_frac-quantile
    (low predicted default -> grant). Higher score = higher default risk."""
    thr = np.quantile(score, deny_frac)
    grant = (score < thr).astype(int)
    g1, g0 = G == 1, G == 0
    if not g1.any() or not g0.any():
        return float("nan")
    return float(abs(grant[g1].mean() - grant[g0].mean()))


def _max_disparity_over_thresholds(score, G):
    """The MOST disparity this score can concentrate at ANY deny threshold (the
    model's concentration CEILING, not tied to one operating point)."""
    return max(_disparity_at_threshold(score, G, f) for f in (0.2, 0.3, 0.4, 0.5))


def run(channel, *, n, seed):
    dgp = _DGP.generate(channel, n=n, seed=seed)
    fr = dgp.frame
    feat_blind = [c for c in fr.columns if c not in ("G", "Y")]
    X_blind = fr[feat_blind].to_numpy()
    X_aware = fr[feat_blind + ["G"]].to_numpy()   # G allowed
    Y = fr["Y"].to_numpy(); G = fr["G"].to_numpy()

    Xb_tr, Xb_te, Xa_tr, Xa_te, ytr, _yte, _Gtr, Gte = train_test_split(
        X_blind, X_aware, Y, G, test_size=0.4, random_state=0, stratify=Y)

    # (a) CEILING_Gaware: flexible model that may use G directly.
    clf_a = GradientBoostingClassifier(random_state=0, n_estimators=120, max_depth=4).fit(Xa_tr, ytr)
    ceil_gaware = _max_disparity_over_thresholds(_pos_score(clf_a, Xa_te), Gte)

    # (b) CEILING_unconstr: flexible G-BLIND model, no policy/depth limit.
    clf_u = GradientBoostingClassifier(random_state=0, n_estimators=120, max_depth=6).fit(Xb_tr, ytr)
    ceil_unconstr = _max_disparity_over_thresholds(_pos_score(clf_u, Xb_te), Gte)

    # (c) BAND_envelope: the MOST-disparate shallow explainable G-blind CART, swept
    #     over depth/leaf like the band (a proxy for the band's max-disparity member).
    band_disp = 0.0
    for depth in (4, 8):
        for leaf in (25, 100):
            t = DecisionTreeClassifier(max_depth=depth, min_samples_leaf=leaf,
                                       random_state=seed).fit(Xb_tr, ytr)
            band_disp = max(band_disp, _max_disparity_over_thresholds(_pos_score(t, Xb_te), Gte))

    return {
        "channel": channel, "seed": seed,
        "label_DP_gap": round(abs(_DGP.demographic_parity_gap(fr)), 4),
        "CEILING_Gaware": round(ceil_gaware, 4),
        "CEILING_unconstrained_blind": round(ceil_unconstr, 4),
        "BAND_envelope_blind": round(band_disp, 4),
    }


def verdict(rows):
    print(f"\n{'='*80}\nCONCENTRATION CEILING: does the CONSTRAINT suppress distributed disparity,\nor is it intrinsically unconcentratable? (disparity each model can MAXIMALLY concentrate)\n{'='*80}")
    print(f"\n{'ch':>3} {'label_inj':>10} {'Gaware':>8} {'unconstr_blind':>15} {'band_blind':>11}")
    print("-"*60)
    for r in rows:
        print(f"{r['channel']:>3} {r['label_DP_gap']:>10} {r['CEILING_Gaware']:>8} "
              f"{r['CEILING_unconstrained_blind']:>15} {r['BAND_envelope_blind']:>11}")
    print()
    for r in rows:
        ch = r["channel"]; ga = r["CEILING_Gaware"]; bb = r["BAND_envelope_blind"]
        un = r["CEILING_unconstrained_blind"]
        if ch == "D4":
            if ga >= 0.05 and ga > un + 0.015:
                print(f"  D4 => P-R2-REAL: G-aware concentrates {ga} (>>{bb} band, >{un} blind-unconstr).")
                print(f"        It takes G ITSELF to surface distributed disparity -> the BLIND CONSTRAINT")
                print(f"        is what protects. Distributed laundering: invisible to SHAP AND unconcentratable")
                print(f"        by the explainable band. Structural protection finding.")
            elif ga <= 0.025:
                print(f"  D4 => P-INTRINSIC: even G-aware stays at {ga} -> distributed disparity is")
                print(f"        unconcentratable by ANY bounded model. The band gets NO special credit;")
                print(f"        'policy-constrained band protects' would be an OVERCLAIM. Deflation stands.")
            else:
                print(f"  D4 => P-MIXED: G-aware={ga} (0.025-0.05). Partial concentration; report as gradient.")
        if ch == "D1":
            detected = ga >= 0.08
            print(f"  D1 (positive control): G-aware concentrates {ga} -- "
                  f"{'probe CAN detect concentration' if detected else 'WARNING: probe failed to concentrate even D1'}.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--channels", nargs="+", default=["D1", "D2", "D3", "D4"])
    ap.add_argument("--n", type=int, default=25000)
    ap.add_argument("--seeds", type=int, nargs="+", default=[101, 202, 303])
    ap.add_argument("--out", default="runs/concentration_ceiling.json")
    args = ap.parse_args()
    # average over seeds per channel for stability
    by_ch = {}
    for ch in args.channels:
        runs = [run(ch, n=args.n, seed=sd) for sd in args.seeds]
        agg = {"channel": ch, "n_seeds": len(runs)}
        for k in ("label_DP_gap", "CEILING_Gaware", "CEILING_unconstrained_blind", "BAND_envelope_blind"):
            agg[k] = round(float(np.mean([r[k] for r in runs])), 4)
        agg["_per_seed"] = runs
        by_ch[ch] = agg
    rows = list(by_ch.values())
    for r in rows:
        print(json.dumps({k: v for k, v in r.items() if k != "_per_seed"}, default=str))
    verdict(rows)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps({"args": vars(args), "rows": rows}, indent=2, sort_keys=True, default=str))
    print(f"\nwritten to {args.out}")


if __name__ == "__main__":
    main()
