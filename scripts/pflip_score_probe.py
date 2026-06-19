#!/usr/bin/env python3
"""Per-applicant P(flip) over the sampler: set -> score (Fable's reframe).

Three documents converged on this: the shuffle-SET membership is seed-jittery
(weak across-seed conservation), but the flip-REGION is structural (margin-
driven, seed-invariant). So the stable, individually-meaningful, due-process-
attachable object is the per-applicant flip PROBABILITY over the sampler
distribution, not the set. This probe builds it and tests whether it is stable
(structured) or flat (noise).

It also MEASURES the across-seed flip-set conservation that the earlier note
FALSELY asserted via the within-band Jaccard column (which measured member-pair
overlap, not across-seed membership). This corrects that error with evidence.

FROZEN PREDICTION (before run):
  (a) across-seed flip-set Jaccard (restricted to commonly-held-out applicants)
      is LOW (~0.2-0.35): membership weakly conserved.
  (b) per-applicant P_flip(i) is STRUCTURED, not flat: bimodal-ish, and rises
      with margin-ambiguity (|true_p - 0.5| small -> P_flip high). If P_flip
      tracks the seed-INVARIANT true margin, the score is stable even though the
      set is jittery -> set->score reframe vindicated.
  (c) if P_flip is ~uniform / margin-independent, the reframe loses its punch.
  prior on (a)&(b) jointly: 0.7.
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


def policy() -> PolicyConstraints:
    return PolicyConstraints(
        name="pflip", version="1", status="active", monotonicity_map={},
        mandatory_features=(), prohibited_features=("G",), applicable_regime={})


def _subsets(features, max_k):
    out = []
    for k in range(1, max_k + 1):
        out.extend(itertools.combinations(features, k))
    return tuple(out)


def true_margin(channel: str, n: int, seed: int) -> np.ndarray:
    """Seed-INVARIANT margin: reconstruct the DGP's generative p, distance to 0.5.
    The DGP is deterministic given (channel, seed-of-DGP); we fix the DGP seed so
    the frame and true p are identical across SAMPLER seeds."""
    dgp = _DGP.generate(channel, n=n, seed=seed)
    # Recompute legit_logit + disp is internal; approximate true p by the base
    # rate structure is not exposed -> use Y's local mean is noisy. Instead use a
    # high-capacity reference (kitchen-sink deep tree) proba as a stable margin
    # proxy that does NOT depend on the sampler seed (fixed here).
    return dgp  # caller extracts frame; margin computed below


def flip_mask_for_seed(X, Y, feat, seed, epsilon_frac, max_k):
    """Return (holdout_global_index, flip_bool) for one sampler seed."""
    cfg = SweepConfig(max_depths=(4, 6, 8, 10), min_samples_leafs=(25, 50, 100, 200),
                      feature_subsets=_subsets(feat, max_k), random_state=seed,
                      holdout_fraction=0.30)
    sweep = hyperparameter_sweep(X, Y, config=cfg)
    adm = evaluate_policy(sweep, policy_constraints=policy())
    if len(adm.admissible) == 0:
        return None, None
    nh = len(np.asarray(adm.admissible[0].holdout_y_true))
    tol = epsilon_frac * nh
    band = filter_to_epsilon_under_loss(
        adm, loss_fn=lambda yt, yh: grant_emphasis_loss(yt, yh, w_T=1.5),
        loss_label="L_T(w_T=1.5)", epsilon=tol)
    members = band.within_epsilon
    _, X_hold, _, _ = inner_split(X, Y, config=cfg)
    holdout_idx = np.asarray(X_hold.index)
    if len(members) < 2:
        return holdout_idx, np.zeros(len(holdout_idx), dtype=bool)
    preds = np.vstack([np.asarray(m.holdout_y_pred) for m in members])
    flip = preds.min(axis=0) != preds.max(axis=0)
    return holdout_idx, flip


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--channel", default="D4")
    ap.add_argument("--n", type=int, default=20000)
    ap.add_argument("--dgp-seed", type=int, default=20260609)
    ap.add_argument("--sampler-seeds", type=int, nargs="+",
                    default=[1, 2, 3, 4, 5, 6, 7, 8])
    ap.add_argument("--epsilon-frac", type=float, default=0.01)
    ap.add_argument("--max-k", type=int, default=3)
    ap.add_argument("--min-coverage", type=int, default=3)
    ap.add_argument("--out", default="runs/pflip_score_probe.json")
    args = ap.parse_args()

    dgp = _DGP.generate(args.channel, n=args.n, seed=args.dgp_seed)
    frame = dgp.frame
    Y = frame["Y"].astype(int)
    feat = [c for c in frame.columns if c not in ("G", "Y")]
    X = frame[feat]
    G = frame["G"].to_numpy()

    # Seed-invariant margin proxy: a fixed deep reference tree on the FULL frame
    # (no sampler seed) -> predicted proba, distance to 0.5. Same for all seeds.
    from sklearn.tree import DecisionTreeClassifier
    ref = DecisionTreeClassifier(max_depth=10, min_samples_leaf=50, random_state=0)
    ref.fit(X.to_numpy(), Y.to_numpy())
    ref_p = ref.predict_proba(X.to_numpy())[:, list(ref.classes_).index(1)]
    margin = np.abs(ref_p - 0.5)  # small = ambiguous

    n = len(frame)
    flip_count = np.zeros(n)
    seen_count = np.zeros(n)
    per_seed_sets = {}
    per_seed_holdout = {}
    for sd in args.sampler_seeds:
        idx, flip = flip_mask_for_seed(X, Y, feat, sd, args.epsilon_frac, args.max_k)
        if idx is None:
            continue
        seen_count[idx] += 1
        flip_count[idx[flip]] += 1
        per_seed_sets[sd] = set(idx[flip].tolist())
        per_seed_holdout[sd] = set(idx.tolist())

    scored = seen_count >= args.min_coverage
    p_flip = np.full(n, np.nan)
    p_flip[scored] = flip_count[scored] / seen_count[scored]

    # (a) across-seed flip-set conservation, restricted to commonly-held-out rows
    jaccs = []
    seeds = list(per_seed_sets.keys())
    for a, b in itertools.combinations(seeds, 2):
        # restrict to rows BOTH seeds held out -- else Jaccard measures split
        # disjointness, not membership conservation.
        common = per_seed_holdout[a] & per_seed_holdout[b]
        sa = per_seed_sets[a] & common
        sb = per_seed_sets[b] & common
        u = len(sa | sb)
        if u:
            jaccs.append(len(sa & sb) / u)
    across_seed_jaccard = float(np.mean(jaccs)) if jaccs else float("nan")

    # (b) is P_flip structured? distribution + margin relationship
    ps = p_flip[scored]
    # bimodality proxy: fraction near 0 or near 1 vs middle
    frac_extreme = float(((ps < 0.15) | (ps > 0.85)).mean())
    frac_middle = float(((ps >= 0.4) & (ps <= 0.6)).mean())
    # margin relationship: corr(P_flip, -margin) -> positive means ambiguous flip more
    mscored = margin[scored]
    margin_corr = float(np.corrcoef(ps, -mscored)[0, 1]) if ps.std() > 0 else float("nan")
    # G relationship on the SCORE (re-confirm protected-blindness at score level)
    gscored = G[scored]
    pflip_g1 = float(ps[gscored == 1].mean()); pflip_g0 = float(ps[gscored == 0].mean())

    out = {
        "channel": args.channel, "n_scored": int(scored.sum()),
        "across_seed_flip_set_jaccard": round(across_seed_jaccard, 4),
        "p_flip_mean": round(float(np.nanmean(p_flip)), 4),
        "p_flip_frac_extreme_0or1": round(frac_extreme, 4),
        "p_flip_frac_middle_0.4_0.6": round(frac_middle, 4),
        "p_flip_vs_margin_corr": round(margin_corr, 4),
        "p_flip_G1": round(pflip_g1, 4), "p_flip_G0": round(pflip_g0, 4),
        "p_flip_G_diff": round(pflip_g1 - pflip_g0, 4),
        "deciles": [round(float(np.nanpercentile(p_flip, q)), 3) for q in range(0, 101, 10)],
    }
    print(json.dumps(out, indent=2))
    print(f"\n{'='*72}\nREADING\n{'='*72}")
    print(f"across-seed flip-SET Jaccard: {out['across_seed_flip_set_jaccard']} "
          f"(LOW => membership weakly conserved, the SET is jittery)")
    print(f"P_flip frac extreme(0/1)={out['p_flip_frac_extreme_0or1']} "
          f"middle(.4-.6)={out['p_flip_frac_middle_0.4_0.6']}")
    print(f"P_flip vs (-margin) corr={out['p_flip_vs_margin_corr']} "
          f"(POSITIVE => ambiguous applicants flip more; score tracks seed-invariant margin)")
    print(f"P_flip protected-blindness at SCORE level: G_diff={out['p_flip_G_diff']}")
    print(f"deciles of P_flip: {out['deciles']}")

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, indent=2, sort_keys=True))
    print(f"\nwritten to {args.out}")


if __name__ == "__main__":
    main()
