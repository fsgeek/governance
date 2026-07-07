#!/usr/bin/env python3
"""Does the POLICY-CONSTRAINED BAND suppress distributed disparity BEYOND mere
G-blindness? (The 0.058 -> 0.013 mystery, measured honestly this time.)

Tonight's chain on D4 (distributed channel), disparity each model can concentrate:
  G-aware flexible      0.144   (~= injected label gap 0.12; G surfaces it fully)
  G-blind flexible (GB) 0.058   (blindness alone roughly halves it)
  bare shallow CART     0.098   (MISLABELED "band" in concentration_ceiling_probe -- a
                                 bare CART, 8x the real band; that probe's verdict is void)
  REAL admissible band  0.013   (from attestation multiseed -- BUT measured at the band
                                 members' OWN thresholds, NOT matched to the ceilings)

The 0.058 -> 0.013 drop is the whole question: is it the BAND CONSTRAINT (ε-loss-tie +
feature-subset admissibility) genuinely suppressing concentratable disparity below the
blindness floor -- a NOVEL centerpiece claim -- or an OPERATING-POINT ARTIFACT (the band
members just grant at a different rate, so their disparity isn't comparable to a ceiling
swept over thresholds)?

This probe removes the operating-point confound: it builds the REAL admissible band
(evaluate_policy + filter_to_epsilon_under_loss, identical to profit_disparity /
attestation probes), takes the band's MAX-disparity member and its grant rate, then
measures the G-blind-flexible and G-aware ceilings AT THE SAME GRANT RATE (matched
deny-fraction). Apples to apples.

FROZEN PREDICTION (frozen before this ran):
  P-band-protects (0.35): D4 real-band max-disparity member <= ~0.02 EVEN at matched
    grant rate, materially below the G-blind-flexible ceiling at that same rate
    (>= 0.04) -> the band suppresses distributed disparity BEYOND blindness. Novel claim.
  P-artifact (0.45): at matched grant rate, the band's max-disparity member ~= the
    G-blind-flexible ceiling -> the 0.013 was an operating-point/low-grant artifact;
    "band protects" collapses to "blindness protects". Deflation stands.
  P-mixed (0.20): partial, 0.02-0.04.
  CONTROL (D1): real band SHOULD concentrate direct disparity nearly as well as the
    blind ceiling (band ~0.12 vs blind-flex ~0.12) -- direct disparity is concentrable
    even under the constraint, so D1 shows the band does NOT indiscriminately suppress.
"""
from __future__ import annotations

import argparse
import importlib.util
import itertools
import json
import sys
from pathlib import Path

import numpy as np
from sklearn.ensemble import GradientBoostingClassifier

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
        name="band_vs_blindness", version="1", status="active", monotonicity_map={},
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


def _disparity_at_grant_rate(score, G, grant_rate):
    """Threshold a continuous default-risk score to achieve `grant_rate`, then the
    |disparity|. Grant = lowest-risk grant_rate fraction (deny the riskiest)."""
    if grant_rate <= 0 or grant_rate >= 1:
        return float("nan")
    thr = np.quantile(score, grant_rate)      # grant the grant_rate-fraction with LOWEST score
    grant = (score <= thr).astype(int)
    return _disparity(grant, G)


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
    band = filter_to_epsilon_under_loss(
        adm, loss_fn=lambda yt, yh: grant_emphasis_loss(yt, yh, w_T=1.5),
        loss_label="L_T(w_T=1.5)", epsilon=eps_frac * nh)
    members = band.within_epsilon
    if len(members) < 2:
        return {"channel": channel, "note": "band<2"}

    _, X_hold, _, _ = inner_split(X, Y, config=cfg)
    G_hold = G[np.asarray(X_hold.index)]

    # REAL band: max-disparity member + its grant rate (the honest operating point).
    band_disps, band_grant_rates = [], []
    for m in members:
        yp = np.asarray(m.holdout_y_pred)
        band_disps.append(_disparity(yp, G_hold))
        band_grant_rates.append(float(yp.mean()))
    band_disps = np.array(band_disps); band_grant_rates = np.array(band_grant_rates)
    worst_i = int(np.nanargmax(band_disps))
    band_max_disp = float(band_disps[worst_i])
    band_gr = float(band_grant_rates[worst_i])         # grant rate to MATCH the ceilings at

    # Ceilings, on the SAME holdout rows, measured AT THE BAND'S GRANT RATE.
    Xb = frame[feat].to_numpy(); Xa = frame[feat + ["G"]].to_numpy()
    Yv = frame["Y"].to_numpy()
    idx = np.asarray(X_hold.index)
    tr_mask = np.ones(len(Yv), bool); tr_mask[idx] = False
    clf_blind = GradientBoostingClassifier(random_state=0, n_estimators=120, max_depth=6).fit(Xb[tr_mask], Yv[tr_mask])
    clf_aware = GradientBoostingClassifier(random_state=0, n_estimators=120, max_depth=4).fit(Xa[tr_mask], Yv[tr_mask])
    s_blind = clf_blind.predict_proba(Xb[idx])[:, 1]   # risk score on the band's holdout
    s_aware = clf_aware.predict_proba(Xa[idx])[:, 1]
    blind_at_band_gr = _disparity_at_grant_rate(s_blind, G_hold, band_gr)
    aware_at_band_gr = _disparity_at_grant_rate(s_aware, G_hold, band_gr)

    return {
        "channel": channel, "seed": seed, "n_band": len(members),
        "label_DP_gap": round(abs(_DGP.demographic_parity_gap(frame)), 4),
        "band_max_disparity": round(band_max_disp, 4),
        "band_grant_rate": round(band_gr, 4),
        "blind_flex_at_band_grant_rate": round(blind_at_band_gr, 4),
        "aware_flex_at_band_grant_rate": round(aware_at_band_gr, 4),
        "band_below_blindness_by": round(blind_at_band_gr - band_max_disp, 4),
    }


def verdict(rows):
    print(f"\n{'='*82}\nBAND vs BLINDNESS: does the constraint suppress distributed disparity BEYOND blindness?\n(all measured at the BAND's grant rate -- operating-point matched)\n{'='*82}")
    print(f"\n{'ch':>3} {'inj':>7} {'band_max':>9} {'blind@gr':>9} {'aware@gr':>9} {'band<blind':>11}")
    print("-"*60)
    for r in rows:
        if "note" in r:
            print(f"{r['channel']:>3}  {r['note']}"); continue
        print(f"{r['channel']:>3} {r['label_DP_gap']:>7} {r['band_max_disparity']:>9} "
              f"{r['blind_flex_at_band_grant_rate']:>9} {r['aware_flex_at_band_grant_rate']:>9} "
              f"{r['band_below_blindness_by']:>11}")
    print()
    for r in rows:
        if "note" in r:
            continue
        ch = r["channel"]; bm = r["band_max_disparity"]; bl = r["blind_flex_at_band_grant_rate"]
        gap = r["band_below_blindness_by"]
        if ch == "D4":
            if bm <= 0.025 and gap >= 0.02:
                print(f"  D4 => P-BAND-PROTECTS: band max disp {bm} << blind ceiling {bl} at the SAME grant rate")
                print(f"        (band is {gap} below blindness). The CONSTRAINT suppresses distributed")
                print(f"        disparity beyond mere G-blindness. NOVEL centerpiece claim earned.")
            elif abs(gap) < 0.015:
                print(f"  D4 => P-ARTIFACT: band max disp {bm} ~= blind ceiling {bl} at matched grant rate.")
                print(f"        The 0.013 was operating-point; 'band protects' collapses to 'blindness protects'.")
            else:
                print(f"  D4 => P-MIXED: band {bm} vs blind {bl} (gap {gap}). Partial; report as gradient.")
        if ch == "D1":
            print(f"  D1 (control): band max disp {bm} vs blind ceiling {bl} -- "
                  f"{'band concentrates direct disparity too (NOT indiscriminate suppression)' if bm >= 0.05 else 'WARNING: band suppresses even DIRECT disparity -> it may just grant uniformly'}.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--channels", nargs="+", default=["D1", "D4"])
    ap.add_argument("--n", type=int, default=20000)
    ap.add_argument("--seeds", type=int, nargs="+", default=[101, 202, 303])
    ap.add_argument("--eps-frac", type=float, default=0.01)
    ap.add_argument("--max-k", type=int, default=3)
    ap.add_argument("--out", default="runs/band_vs_blindness.json")
    args = ap.parse_args()
    rows = []
    for ch in args.channels:
        per = [run(ch, n=args.n, seed=sd, eps_frac=args.eps_frac, max_k=args.max_k) for sd in args.seeds]
        valid = [r for r in per if "note" not in r]
        if not valid:
            rows.append({"channel": ch, "note": "all bands <2"}); continue
        agg = {"channel": ch, "n_seeds": len(valid)}
        for k in ("label_DP_gap", "band_max_disparity", "band_grant_rate",
                  "blind_flex_at_band_grant_rate", "aware_flex_at_band_grant_rate",
                  "band_below_blindness_by"):
            agg[k] = round(float(np.mean([r[k] for r in valid])), 4)
        agg["_per_seed"] = valid
        rows.append(agg)
    for r in rows:
        print(json.dumps({k: v for k, v in r.items() if k != "_per_seed"}, default=str))
    verdict(rows)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps({"args": vars(args), "rows": rows}, indent=2, sort_keys=True, default=str))
    print(f"\nwritten to {args.out}")


if __name__ == "__main__":
    main()
