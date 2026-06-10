#!/usr/bin/env python3
"""Who is in the shuffle-set? Is band-member disagreement the C3 floor with names?

GOAL (Tony, 2026-06-09): the floor result says discrimination has an irreducible
component; switching band members can't ELIMINATE it, only RELOCATE it. So the
band's tied-on-loss members are N different answers to "who absorbs the
irreducible disparity?" The SHUFFLE-SET -- borrowers whose decision flips across
tied members -- is the population over which that relocation happens.

THE TEST: build the policy-constrained band on a substrate with a KNOWN
protected attribute G and a KNOWN injected disparity (fairwash_frontier_dgp,
which has per-row G and D-channel disparity). Get per-borrower predictions from
each DISTINCT tied band member. Identify flippers (members disagree). Ask:
  - Is P(flip | G=1) > P(flip | G=0)?  (shuffle-set G-concentrated?)
  - Do flippers cluster near the decision boundary (where the C3 floor lives)?

FROZEN PREDICTION (committed before the run, in this docstring):
  H (prior 0.55): the shuffle-set is STRUCTURED and G-concentrated.
    P(flip|G=1) / P(flip|G=0) >= 1.3, and flippers concentrate at mid-range
    predicted probability (near the boundary). Reason: the injected disparity
    sits on G-correlated carriers; tied members route it differently, so the
    cases that move are the G-correlated near-boundary ones. If true: the
    shuffle-set IS the C3 floor made visible -- the same people get moved around
    regardless of which explainable model you pick. Tony's "shifting it around"
    intuition holds, with names.
  NULL (prior 0.45): flips are DIFFUSE -- P(flip|G=1) ~ P(flip|G=0) (ratio in
    [0.85,1.15]) and spread across the probability range. Disagreement is CART
    variance unrelated to the protected axis; the band members differ by chance,
    not by who-absorbs-the-disparity. Tony's intuition would be wrong; "pick one"
    shuffles random people, not a protected subpopulation.

  Tie-breaker quantity: ACROSS multiple band-member PAIRS, is it the SAME people
  who flip (stable shuffle-set = a real floor population) or different people
  each pair (unstable = noise)? Jaccard overlap of flipper-sets across member
  pairs. High overlap supports H even if the G-ratio is modest.

Single DGP channel = D2 (single-proxy: clean, one carrier) and D4 (distributed:
the fiendish case). G is ALWAYS dropped from the model (prohibited). Report
per-channel.
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
    SweepConfig,
    evaluate_policy,
    filter_to_epsilon_under_loss,
    hyperparameter_sweep,
)
from wedge.losses import grant_emphasis_loss


def _load(mod, path):
    spec = importlib.util.spec_from_file_location(mod, path)
    assert spec is not None and spec.loader is not None
    m = importlib.util.module_from_spec(spec)
    sys.modules[mod] = m
    spec.loader.exec_module(m)
    return m


_DGP = _load("fairwash_frontier_dgp", str(Path(__file__).with_name("fairwash_frontier_dgp.py")))


def policy() -> PolicyConstraints:
    # Prohibit G (the protected attribute) and the c_fresh carriers are admitted
    # -- exactly the laundering surface. Mandatory none.
    return PolicyConstraints(
        name="shuffle_set", version="1", status="active", monotonicity_map={},
        mandatory_features=(), prohibited_features=("G",), applicable_regime={},
    )


def _subsets(features: list[str], max_k: int) -> tuple[tuple[str, ...], ...]:
    out: list[tuple[str, ...]] = []
    for k in range(1, max_k + 1):
        out.extend(itertools.combinations(features, k))
    return tuple(out)


def _independent_margin(best_member, X_hold, consensus_p):
    """Graded margin from the best member's predict_proba on the holdout design,
    restricted to that member's feature subset. Independent of the band's
    disagreement (a single reference model's score). Falls back to consensus_p
    only if the fitted tree is unavailable."""
    tree = getattr(best_member, "fitted_tree", None)
    spec = getattr(best_member, "spec", None)
    subset = list(getattr(spec, "feature_subset", []) or [])
    if tree is None or not subset:
        raise RuntimeError("independent margin unavailable: no fitted_tree/subset")
    # X_hold rows are the SAME holdout rows as the member's stored predictions
    # (deterministic inner_split). Restrict to the member's subset and score.
    Xs = X_hold[subset].to_numpy()
    classes = list(tree.classes_)
    proba = tree.predict_proba(Xs)[:, classes.index(1)]
    return np.asarray(proba, dtype=float)


def run_channel(channel: str, *, n: int, seed: int, epsilon_frac: float, max_k: int) -> dict:
    dgp = _DGP.generate(channel, n=n, seed=seed)
    frame = dgp.frame
    G = frame["G"].to_numpy()
    Y = frame["Y"].astype(int)
    # model features: everything except G and Y (carriers admitted, G prohibited)
    feat_cols = [c for c in frame.columns if c not in ("G", "Y")]
    X = frame[feat_cols]

    cfg = SweepConfig(
        max_depths=(4, 6, 8, 10), min_samples_leafs=(25, 50, 100, 200),
        feature_subsets=_subsets(feat_cols, max_k), random_state=seed,
        holdout_fraction=0.30,
    )
    sweep = hyperparameter_sweep(X, Y, config=cfg)
    adm = evaluate_policy(sweep, policy_constraints=policy())
    if not adm.admissible:
        return {"channel": channel, "error": "no admissible models"}

    # Per-sample-normalised epsilon (the FIX from project_band_epsilon_inert):
    # tol = epsilon_frac * n_holdout, so the band is a genuine multi-member set.
    n_holdout = len(np.asarray(adm.admissible[0].holdout_y_true))
    tol = epsilon_frac * n_holdout
    loss_fn = lambda yt, yh: grant_emphasis_loss(yt, yh, w_T=1.5)
    band = filter_to_epsilon_under_loss(
        adm, loss_fn=loss_fn, loss_label="L_T(w_T=1.5)", epsilon=tol
    )
    members = band.within_epsilon
    # The holdout G/Y align row-for-row with each member's stored holdout preds
    # (same inner_split, same config). Recover the holdout mask via the first
    # member's stored y_true and the sweep's deterministic split is identical
    # across members -- so member predictions are mutually comparable per-row.
    if len(members) < 2:
        return {"channel": channel, "n_band": len(members),
                "note": "band < 2 members; widen epsilon_frac", "tol": tol}

    # Stack member holdout predictions: shape (n_members, n_holdout)
    preds = np.vstack([np.asarray(m.holdout_y_pred) for m in members])
    y_holdout = np.asarray(members[0].holdout_y_true)
    # Recover the holdout G: the sweep's inner_split is deterministic; reproduce it
    from wedge.rashomon import inner_split
    _, X_hold, _, y_hold_check = inner_split(X, Y, config=cfg)
    assert np.array_equal(np.asarray(y_hold_check), y_holdout), "holdout misalignment"
    G_holdout = G[np.asarray(X_hold.index)]

    # Flippers: borrowers where members DISAGREE (not all preds equal).
    flip = (preds.min(axis=0) != preds.max(axis=0))  # True where any disagreement
    n_flip = int(flip.sum())

    # G-concentration of the shuffle-set
    p_flip_g1 = float(flip[G_holdout == 1].mean()) if (G_holdout == 1).any() else float("nan")
    p_flip_g0 = float(flip[G_holdout == 0].mean()) if (G_holdout == 0).any() else float("nan")
    g_ratio = (p_flip_g1 / p_flip_g0) if p_flip_g0 > 0 else float("inf")

    # Boundary concentration: mean predicted prob of flippers vs non-flippers.
    # Use the fraction of members predicting grant as a band-consensus prob.
    consensus_p = preds.mean(axis=0)
    boundary_dist_flip = float(np.abs(consensus_p[flip] - 0.5).mean()) if n_flip else float("nan")
    boundary_dist_noflip = float(np.abs(consensus_p[~flip] - 0.5).mean()) if (~flip).any() else float("nan")

    # SHARPER TESTS (added after first run showed G-blind flip RATE):
    # (1) Flip DIRECTION: when a borrower flips, does the band-consensus lean
    #     correlate with G? A G-blind flip-rate can still hide G-correlated flip
    #     DIRECTION -- which IS the discrimination relocating. Measure: among
    #     flippers, corr(G, fraction-of-members-granting).
    flip_mask = flip
    if n_flip > 10:
        gf = G_holdout[flip_mask]
        cf = consensus_p[flip_mask]
        if gf.std() > 0 and cf.std() > 0:
            dir_corr = float(np.corrcoef(gf, cf)[0, 1])
        else:
            dir_corr = float("nan")
        # mean grant-fraction among flippers, by group: does G shift the lean?
        grant_lean_g1 = float(cf[gf == 1].mean()) if (gf == 1).any() else float("nan")
        grant_lean_g0 = float(cf[gf == 0].mean()) if (gf == 0).any() else float("nan")
    else:
        dir_corr = grant_lean_g1 = grant_lean_g0 = float("nan")

    # (2) THE MARGIN-CONTROLLED TEST (Fable's load-bearing point): flips
    #     concentrate at the boundary DEFINITIONALLY, so raw P(flip|G) and
    #     consensus-based boundary distance are confounded by where G sits. The
    #     claim that survives a referee is: at the SAME margin, do G-correlated
    #     borrowers flip MORE? Margin = |p_ref - 0.5| under a REFERENCE model
    #     (the best single member), independent of the band's disagreement.
    #     Stratify into margin bins; within each, compare P(flip|G1) vs P(flip|G0)
    #     and report the margin-pooled (Mantel-Haenszel-style) G effect.
    # INDEPENDENT graded margin: the best member's predict_proba on the holdout.
    # This is a REFERENCE model's score, NOT the band consensus -- so binning on
    # it does not mechanically saturate flip-rate (the consensus-bin circularity
    # I self-caught). Reconstruct the holdout design for the best member's subset.
    best_member = max(members, key=lambda m: m.holdout_auc)
    margin_axis = _independent_margin(best_member, X_hold, consensus_p)
    margin_bins = [(0.0, 0.2), (0.2, 0.4), (0.4, 0.6), (0.6, 0.8), (0.8, 1.0)]
    mh_num = mh_den = 0.0  # Mantel-Haenszel-style pooled ratio components
    bin_rows = []
    for lo, hi in margin_bins:
        m = (margin_axis >= lo) & (margin_axis < hi if hi < 1.0 else margin_axis <= hi)
        if m.sum() < 20:
            continue
        g1 = m & (G_holdout == 1); g0 = m & (G_holdout == 0)
        if not g1.any() or not g0.any():
            continue
        pf1 = float(flip[g1].mean()); pf0 = float(flip[g0].mean())
        bin_rows.append({"bin": f"[{lo},{hi})", "n": int(m.sum()),
                         "p_flip_G1": round(pf1, 3), "p_flip_G0": round(pf0, 3),
                         "diff": round(pf1 - pf0, 3)})
        # pool the within-bin difference weighted by bin size
        w = float(m.sum())
        mh_num += w * (pf1 - pf0); mh_den += w
    margin_pooled_g_diff = (mh_num / mh_den) if mh_den > 0 else float("nan")

    near = (consensus_p >= 0.25) & (consensus_p <= 0.75)
    if near.sum() > 10 and G_holdout[near].std() > 0:
        p_flip_g1_near = float(flip[near & (G_holdout == 1)].mean()) if (near & (G_holdout == 1)).any() else float("nan")
        p_flip_g0_near = float(flip[near & (G_holdout == 0)].mean()) if (near & (G_holdout == 0)).any() else float("nan")
        g_ratio_near = (p_flip_g1_near / p_flip_g0_near) if p_flip_g0_near > 0 else float("inf")
    else:
        p_flip_g1_near = p_flip_g0_near = g_ratio_near = float("nan")

    # Stability: across member PAIRS, is it the same people who flip? Jaccard.
    pair_flipsets = []
    for a, b in itertools.combinations(range(len(members)), 2):
        s = set(np.where(preds[a] != preds[b])[0].tolist())
        if s:
            pair_flipsets.append(s)
    jacc = []
    for s1, s2 in itertools.combinations(pair_flipsets, 2):
        u = len(s1 | s2)
        jacc.append(len(s1 & s2) / u if u else 0.0)
    mean_jaccard = float(np.mean(jacc)) if jacc else float("nan")

    return {
        "channel": channel, "n_holdout": n_holdout, "tol_cases": round(tol, 1),
        "n_band_members": len(members),
        "n_flip": n_flip, "flip_rate": round(n_flip / n_holdout, 4),
        "p_flip_G1": round(p_flip_g1, 4), "p_flip_G0": round(p_flip_g0, 4),
        "g_ratio": round(g_ratio, 3) if np.isfinite(g_ratio) else None,
        "boundary_dist_flip": round(boundary_dist_flip, 4),
        "boundary_dist_noflip": round(boundary_dist_noflip, 4),
        "mean_pairwise_jaccard": round(mean_jaccard, 4),
        "n_member_pairs_with_flips": len(pair_flipsets),
        # sharper G-structure tests
        "flip_direction_corr_G": round(dir_corr, 4) if np.isfinite(dir_corr) else None,
        "grant_lean_flip_G1": round(grant_lean_g1, 4) if np.isfinite(grant_lean_g1) else None,
        "grant_lean_flip_G0": round(grant_lean_g0, 4) if np.isfinite(grant_lean_g0) else None,
        "g_ratio_near_boundary": round(g_ratio_near, 3) if np.isfinite(g_ratio_near) else None,
        "p_flip_G1_near": round(p_flip_g1_near, 4) if np.isfinite(p_flip_g1_near) else None,
        "p_flip_G0_near": round(p_flip_g0_near, 4) if np.isfinite(p_flip_g0_near) else None,
        # MARGIN-CONTROLLED G-effect (Fable point 1): within-margin-bin P(flip|G1)-P(flip|G0),
        # size-pooled. ~0 => boundary concentration is mechanical, no residual G-effect.
        "margin_pooled_g_diff": round(margin_pooled_g_diff, 4) if np.isfinite(margin_pooled_g_diff) else None,
        "margin_bins": bin_rows,
    }


def verdict(rows: list[dict]) -> None:
    print(f"\n{'='*78}\nSHUFFLE-SET VERDICT\n{'='*78}")
    for r in rows:
        if "error" in r or "note" in r:
            print(f"  {r['channel']}: {r.get('error') or r.get('note')}")
            continue
        gr = r["g_ratio"]
        struct = []
        if gr is not None and gr >= 1.3:
            struct.append(f"G-concentrated (P(flip|G1)/P(flip|G0)={gr})")
        if r["boundary_dist_flip"] < r["boundary_dist_noflip"]:
            struct.append("boundary-concentrated (flippers nearer 0.5)")
        if r["mean_pairwise_jaccard"] >= 0.3:
            struct.append(f"STABLE shuffle-set (Jaccard={r['mean_pairwise_jaccard']})")
        tag = "STRUCTURED -> H" if len(struct) >= 2 else (
            "DIFFUSE -> NULL" if not struct else "MIXED")
        print(f"  {r['channel']}: {tag}")
        print(f"     band={r['n_band_members']} flip_rate={r['flip_rate']} "
              f"P(flip|G1)={r['p_flip_G1']} P(flip|G0)={r['p_flip_G0']} ratio={gr}")
        print(f"     boundary flip={r['boundary_dist_flip']} vs noflip={r['boundary_dist_noflip']}"
              f"  Jaccard={r['mean_pairwise_jaccard']}")
        for s in struct:
            print(f"       + {s}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=20260609)
    ap.add_argument("--n", type=int, default=20000)
    ap.add_argument("--epsilon-frac", type=float, default=0.01)
    ap.add_argument("--max-k", type=int, default=3)
    ap.add_argument("--channels", nargs="+", default=["D2", "D4"])
    ap.add_argument("--out", default="runs/shuffle_set_probe.json")
    args = ap.parse_args()

    rows = [run_channel(c, n=args.n, seed=args.seed, epsilon_frac=args.epsilon_frac,
                        max_k=args.max_k) for c in args.channels]
    for r in rows:
        print(json.dumps(r, default=str))
    verdict(rows)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"args": vars(args), "rows": rows}, indent=2,
                              sort_keys=True, default=str))
    print(f"\nwritten to {out}")


if __name__ == "__main__":
    main()
