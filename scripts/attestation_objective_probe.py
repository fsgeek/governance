#!/usr/bin/env python3
"""Does the attestation carry the OBJECTIVE, or only the geometry?

The surviving claim from the profit/fairness arc ([[project_profit_fairness_c3_floor]])
is: the C3 floor forbids "free fairness", but the band makes the accuracy-disparity
FRONTIER VISIBLE AND ATTESTABLE -- the bank "owns its operating-point choice in the
open, disclosed like a capital ratio."

This probe attacks the word ATTESTABLE. A capital ratio works as a control because
the REGULATOR RECOMPUTES it; a disclosed number you merely chose is not a floor
anyone verifies you are above. So: take two banks on the SAME band.
  Bank-F selects the min-|disparity| member (fairness objective).
  Bank-P selects the max-profit member (profit objective).
Each emits the project's receipt: band size, within-band flip-rate, and the
operating point (its OWN member's disparity + profit). Then ask the decisive
question the memory embedded but never tested:

  Can an auditor who reads the receipt -- AND who can recompute member disparities
  on a held-out set WITH G (regulators hold G via HMDA/BISG; this DGP even ships
  Ghat_bisg) -- distinguish "I sat at the fairness floor" from "I maximized profit
  and called it a frontier point"?

FROZEN PREDICTION (frozen before this ran):
  P-attack  (0.55): the floor is NOT recomputable from what the bank attests; the
    receipts differ only in self-reported fields. A bank can report Bank-P's point
    while CLAIMING it is the disparity-minimizing one and nothing refutes it.
    Attestation certifies "a member of a real band", not "the fair member".
  P-defense (0.30): the auditor, holding G (true G or Ghat_bisg), recomputes EVERY
    member's disparity -> the min-disparity floor -> Bank-P's deviation (chosen
    disparity minus floor disparity) is MEASURABLE. The receipt's profit-point minus
    the recomputable floor IS the laundering signal. Attestation carries the objective.
  P-collapse(0.15): min-disparity member ~= max-profit member on these channels
    (C3 pins them together) -> no choice to launder; attack empty on this bench.

DECISIVE QUANTITIES per channel:
  - disparity_gap = |disp(Bank-P member)| - |disp(floor member)|   (the choice spread)
  - is that gap recomputable by an auditor holding ONLY (Ghat_bisg, X, the band)?
    i.e. does ranking members by Ghat-disparity recover the true min-disparity member?
  - rank_agreement(true G, Ghat_bisg) over members: if high, the regulator's recompute
    finds the same floor the bank could hide -> P-defense. If low, the BISG proxy is
    too noisy to pin the floor -> the attestation is NOT verifiable -> P-attack survives
    even when the regulator tries.
"""
from __future__ import annotations

import argparse
import importlib.util
import itertools
import json
import sys
from pathlib import Path

import numpy as np

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


def policy():
    return PolicyConstraints(
        name="attestation_objective", version="1", status="active", monotonicity_map={},
        mandatory_features=(), prohibited_features=("G",), applicable_regime={})


def _subsets(feat, max_k):
    out = []
    for k in range(1, max_k + 1):
        out.extend(itertools.combinations(feat, k))
    return tuple(out)


def member_profit(y_pred, y_true, r):
    grant = y_pred == 1
    return float(np.sum(np.where(grant, np.where(y_true == 1, r, -1.0), 0.0)))


def member_disparity(y_pred, attr):
    """P(grant|attr-high) - P(grant|attr-low). For continuous Ghat, split at median
    so the auditor's recompute uses the same shape as the true-G binary disparity."""
    if attr.dtype.kind == "f" and len(np.unique(attr)) > 2:
        hi = attr >= np.median(attr)
    else:
        hi = attr == 1
    lo = ~hi
    if not hi.any() or not lo.any():
        return float("nan")
    return float(y_pred[hi].mean() - y_pred[lo].mean())


def run(channel, *, n, seed, eps_frac, max_k, r, bisg_auc):
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

    # holdout alignment: recover the same holdout rows the band members predict on,
    # so G_hold and Ghat_hold line up with holdout_y_pred row-for-row.
    _, X_hold, _, _ = inner_split(X, Y, config=cfg)
    hold_idx = np.asarray(X_hold.index)
    G_hold = G[hold_idx]
    # Build the regulator's BISG proxy of G on the FULL frame, then slice to holdout.
    # _bisg_estimate needs g_latent; reconstruct the same latent the DGP used is not
    # exposed for the D-channels, so approximate the regulator estimate directly from
    # true G + calibrated noise to hit the target AUC (the regulator's measurement model).
    ghat_full = _bisg_proxy(G, bisg_auc, seed)
    Ghat_hold = ghat_full[hold_idx]
    y_true = np.asarray(members[0].holdout_y_true)

    profits, disp_trueG, disp_ghat = [], [], []
    for m in members:
        yp = np.asarray(m.holdout_y_pred)
        profits.append(member_profit(yp, y_true, r))
        disp_trueG.append(member_disparity(yp, G_hold))
        disp_ghat.append(member_disparity(yp, Ghat_hold))
    profits = np.array(profits)
    disp_trueG = np.array(disp_trueG); abs_trueG = np.abs(disp_trueG)
    disp_ghat = np.array(disp_ghat); abs_ghat = np.abs(disp_ghat)

    # The two banks' selections.
    floor_i_true = int(np.argmin(abs_trueG))     # the real fairness floor
    bankP_i = int(np.argmax(profits))            # the profit-maximizer
    # The auditor, holding only Ghat, recomputes the floor:
    floor_i_ghat = int(np.argmin(abs_ghat))

    # DECISIVE 1: the choice spread the bank can hide (true G).
    disparity_gap = float(abs_trueG[bankP_i] - abs_trueG[floor_i_true])
    profit_gain   = float(profits[bankP_i] - profits[floor_i_true])

    # DECISIVE 2: can the auditor RECOMPUTE the floor? Does the Ghat-ranked floor
    # match the true-G floor member? And does the auditor's measured disparity for
    # Bank-P's chosen member exceed the auditor's measured floor (-> deviation visible)?
    floor_recovered = bool(floor_i_ghat == floor_i_true)
    auditor_gap_for_bankP = float(abs_ghat[bankP_i] - abs_ghat[floor_i_ghat])
    # rank agreement between true-G and Ghat disparity orderings (Spearman).
    rank_agreement = _spearman(abs_trueG, abs_ghat)

    # DECISIVE 3: the receipts. What the project's manifest emits per chosen member.
    bd = band_disagreement_summary(band)
    def receipt(i):
        return {
            "member_index": i,
            "self_reported_disparity_trueG": round(float(disp_trueG[i]), 4),
            "self_reported_profit": round(float(profits[i]), 1),
            "band_size": bd["n_members"],
            "within_band_flip_rate": bd.get("flip_rate"),
        }

    return {
        "channel": channel,
        "n_band": len(members),
        "bisg_auc_target": bisg_auc,
        "floor_member_trueG": {"i": floor_i_true, "absdisp": round(float(abs_trueG[floor_i_true]), 4),
                               "profit": round(float(profits[floor_i_true]), 1)},
        "bankP_member": {"i": bankP_i, "absdisp": round(float(abs_trueG[bankP_i]), 4),
                         "profit": round(float(profits[bankP_i]), 1)},
        "disparity_gap_bankP_minus_floor": round(disparity_gap, 4),
        "profit_gain_bankP_over_floor": round(profit_gain, 1),
        "auditor_floor_recovered_from_Ghat": floor_recovered,
        "auditor_measured_gap_for_bankP": round(auditor_gap_for_bankP, 4),
        "rank_agreement_trueG_vs_Ghat": round(rank_agreement, 4),
        "receipt_bankF": receipt(floor_i_true),
        "receipt_bankP": receipt(bankP_i),
    }


def _bisg_proxy(G, target_auc, seed):
    """Regulator's noisy estimate of G with AUC(estimate ~ G) ~= target_auc.
    Built from true G + calibrated Gaussian noise (the regulator's measurement model).
    Returns a continuous score in (0,1)."""
    from sklearn.metrics import roc_auc_score
    rng = np.random.default_rng(seed + 777)
    gz = (G - G.mean()) / (G.std() + 1e-12)
    noise = rng.standard_normal(len(G))
    lo, hi = 0.0, 40.0
    for _ in range(40):
        s = 0.5 * (lo + hi)
        if roc_auc_score(G, gz + s * noise) > target_auc:
            lo = s
        else:
            hi = s
    s = 0.5 * (lo + hi)
    score = gz + s * noise
    return 1.0 / (1.0 + np.exp(-(score - score.mean()) / (score.std() + 1e-9)))


def _spearman(a, b):
    if len(a) < 2 or np.std(a) == 0 or np.std(b) == 0:
        return float("nan")
    ar = np.argsort(np.argsort(a)); br = np.argsort(np.argsort(b))
    return float(np.corrcoef(ar, br)[0, 1])


def verdict(rows):
    print(f"\n{'='*78}\nDOES THE ATTESTATION CARRY THE OBJECTIVE? (frontier visible != attestable)\n{'='*78}")
    for r in rows:
        if "note" in r:
            print(f"  {r['channel']}: {r['note']}"); continue
        gap = r["disparity_gap_bankP_minus_floor"]
        gain = r["profit_gain_bankP_over_floor"]
        rec = r["auditor_floor_recovered_from_Ghat"]
        ra = r["rank_agreement_trueG_vs_Ghat"]
        print(f"\n{r['channel']}  (band={r['n_band']}, BISG AUC~{r['bisg_auc_target']})")
        print(f"  fairness floor:  member {r['floor_member_trueG']['i']:>2}  |disp|={r['floor_member_trueG']['absdisp']}  profit={r['floor_member_trueG']['profit']}")
        print(f"  Bank-P (profit): member {r['bankP_member']['i']:>2}  |disp|={r['bankP_member']['absdisp']}  profit={r['bankP_member']['profit']}")
        print(f"  CHOICE SPREAD the bank can move: disparity_gap={gap:+.4f}  for profit_gain={gain:+.1f}")
        if abs(gap) < 0.01:
            print("  => P-COLLAPSE signal: floor ~= profit-max member; little to launder on this channel.")
        print(f"  auditor (Ghat AUC~{r['bisg_auc_target']}) recovers the true floor member? {rec}")
        print(f"  auditor's measured gap for Bank-P = {r['auditor_measured_gap_for_bankP']:+.4f}  "
              f"(>0 => deviation visible to regulator)")
        print(f"  rank agreement (true-G vs Ghat disparity ordering) = {ra}")
        if rec and abs(r['auditor_measured_gap_for_bankP']) > 0.01:
            print("  => P-DEFENSE on this channel: regulator RECOMPUTES the floor; Bank-P's deviation is visible.")
        elif not rec:
            print("  => P-ATTACK on this channel: regulator's Ghat does NOT pin the floor; the choice is NOT verifiable.")
    # cross-channel summary
    real = [r for r in rows if "note" not in r]
    if real:
        movable = [r for r in real if abs(r["disparity_gap_bankP_minus_floor"]) >= 0.01]
        verifiable = [r for r in movable if r["auditor_floor_recovered_from_Ghat"]]
        print(f"\n{'-'*78}")
        print(f"channels with a real choice to launder (|gap|>=0.01): {len(movable)}/{len(real)}")
        print(f"  of those, regulator recomputes the floor (P-defense): {len(verifiable)}/{len(movable)}")
        print(f"  remaining (P-attack survives even with a trying regulator): {len(movable)-len(verifiable)}/{len(movable)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--channels", nargs="+", default=["D1", "D2", "D3", "D4"])
    ap.add_argument("--n", type=int, default=20000)
    ap.add_argument("--seed", type=int, default=20260610)
    ap.add_argument("--eps-frac", type=float, default=0.01)
    ap.add_argument("--max-k", type=int, default=3)
    ap.add_argument("--r", type=float, default=0.25)
    ap.add_argument("--bisg-auc", type=float, default=0.85,
                    help="AUC of the regulator's BISG proxy for G (HMDA-realistic ~0.85)")
    ap.add_argument("--out", default="runs/attestation_objective.json")
    args = ap.parse_args()
    rows = [run(c, n=args.n, seed=args.seed, eps_frac=args.eps_frac, max_k=args.max_k,
                r=args.r, bisg_auc=args.bisg_auc) for c in args.channels]
    for r in rows:
        print(json.dumps(r, default=str))
    verdict(rows)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps({"args": vars(args), "rows": rows}, indent=2, sort_keys=True, default=str))
    print(f"\nwritten to {args.out}")


if __name__ == "__main__":
    main()
