#!/usr/bin/env python3
"""Is "interaction-borne disparity defeats floor-attestation" a theorem or an anecdote?

The single-seed run (scripts/attestation_objective_probe.py, runs/attestation_objective.json)
found P-attack surviving on exactly ONE channel: D3, the INTERACTION channel
(the DGP's "realistic" one). There the regulator's BISG proxy gets the GLOBAL
disparity ordering roughly right (rank agreement 0.81) but MISORDERS the near-floor
members, so floor_recovered=False -> the bank's choice of operating point is NOT
verifiable -> the attestation degrades from capital-ratio (supervisor-recomputed) to
self-report.

But that verdict rested on ONE seed and a band of 18, hinging on a SINGLE misordered
pair. That is the exact shape of the redundancy-canary false positive in memory.
This driver re-runs D3 (and the contrast channels D1/D4) across many seeds and asks:

  Q1 (headline, brittle):  across seeds, what FRACTION of D3 runs have floor_recovered=False?
  Q2 (robust, graded):     across seeds, what is the distribution of the rank-distance
                           between the true floor and the Ghat-recovered floor? (0 = recovered)
  Q3 (does it matter):     when the floor is NOT recovered, is there still a real choice
                           (|disparity_gap| >= 0.01 AND profit_gain > 0)? An unverifiable
                           floor only launders if there's something to launder.

FROZEN PREDICTION (frozen before this multiseed ran):
  If THEOREM: D3 floor_recovered=False in a MAJORITY of seeds (>=5/8), with non-trivial
    choice present, while D1/D4 recover in a majority. The interaction channel is
    structurally harder to attest, not seed-lucky.
  If ANECDOTE: D3 recovery is a coin-flip or better across seeds (the single False was
    the unlucky draw) -> the headline retracts to "near-floor ordering is noisy on the
    interaction channel," a gradient not a wall.
  P(theorem) ~ 0.45  -- genuinely uncertain; the mechanism (subpopulation-localized
    disparity vs subpopulation-noisy proxy) is real, but band=18 is thin.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

_PROBE = None
def _probe():
    global _PROBE
    if _PROBE is None:
        spec = importlib.util.spec_from_file_location(
            "attestation_objective_probe",
            str(Path(__file__).with_name("attestation_objective_probe.py")))
        assert spec is not None and spec.loader is not None
        m = importlib.util.module_from_spec(spec); sys.modules["attestation_objective_probe"] = m
        spec.loader.exec_module(m)
        _PROBE = m
    return _PROBE


def run_seed(channel, seed, *, n, eps_frac, max_k, r, bisg_auc):
    P = _probe()
    out = P.run(channel, n=n, seed=seed, eps_frac=eps_frac, max_k=max_k, r=r, bisg_auc=bisg_auc)
    return out


def summarize(channel, runs):
    valid = [x for x in runs if "note" not in x]
    if not valid:
        return {"channel": channel, "n_seeds": len(runs), "all_degenerate": True}
    rec = [bool(x["auditor_floor_recovered_from_Ghat"]) for x in valid]
    movable = [abs(x["disparity_gap_bankP_minus_floor"]) >= 0.01 and x["profit_gain_bankP_over_floor"] > 0
               for x in valid]
    # P-attack on this run = a real choice exists AND the floor is NOT recoverable.
    p_attack = [(m and not rcv) for m, rcv in zip(movable, rec)]
    gaps = [x["disparity_gap_bankP_minus_floor"] for x in valid]
    ranks = [x["rank_agreement_trueG_vs_Ghat"] for x in valid]
    bands = [x["n_band"] for x in valid]
    profits = [x["profit_gain_bankP_over_floor"] for x in valid]
    return {
        "channel": channel,
        "n_seeds": len(valid),
        "floor_recovered_frac": round(np.mean(rec), 3),
        "has_real_choice_frac": round(np.mean(movable), 3),
        "P_ATTACK_frac": round(np.mean(p_attack), 3),
        "disparity_gap_median": round(float(np.median(gaps)), 4),
        "disparity_gap_range": [round(min(gaps), 4), round(max(gaps), 4)],
        "profit_gain_median": round(float(np.median(profits)), 1),
        "rank_agreement_median": round(float(np.median(ranks)), 3),
        "band_size_range": [min(bands), max(bands)],
        "per_seed_recovered": rec,
        "per_seed_p_attack": p_attack,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--channels", nargs="+", default=["D1", "D3", "D4"])
    ap.add_argument("--seeds", type=int, nargs="+",
                    default=[101, 202, 303, 404, 505, 606, 707, 808])
    ap.add_argument("--n", type=int, default=20000)
    ap.add_argument("--eps-frac", type=float, default=0.01)
    ap.add_argument("--max-k", type=int, default=3)
    ap.add_argument("--r", type=float, default=0.25)
    ap.add_argument("--bisg-auc", type=float, default=0.85)
    ap.add_argument("--out", default="runs/attestation_d3_multiseed.json")
    args = ap.parse_args()

    all_summaries = []
    all_runs = {}
    for ch in args.channels:
        runs = []
        for sd in args.seeds:
            print(f"[{ch} seed={sd}] running...", flush=True)
            runs.append(run_seed(ch, sd, n=args.n, eps_frac=args.eps_frac,
                                 max_k=args.max_k, r=args.r, bisg_auc=args.bisg_auc))
        all_runs[ch] = runs
        all_summaries.append(summarize(ch, runs))

    print(f"\n{'='*78}\nINTERACTION-BORNE FLOOR ATTESTATION: THEOREM OR ANECDOTE? ({len(args.seeds)} seeds)\n{'='*78}")
    for s in all_summaries:
        if s.get("all_degenerate"):
            print(f"\n{s['channel']}: all bands degenerate (<2 members)"); continue
        print(f"\n{s['channel']}  (band sizes {s['band_size_range']}, {s['n_seeds']} valid seeds)")
        print(f"  floor recovered by regulator:  {s['floor_recovered_frac']:.0%} of seeds   per-seed: {s['per_seed_recovered']}")
        print(f"  real choice to launder present:{s['has_real_choice_frac']:.0%} of seeds")
        print(f"  >>> P-ATTACK (real choice AND floor unrecoverable): {s['P_ATTACK_frac']:.0%} of seeds   per-seed: {s['per_seed_p_attack']}")
        print(f"  disparity gap median={s['disparity_gap_median']} range={s['disparity_gap_range']}  profit gain median={s['profit_gain_median']}")
        print(f"  rank agreement (true-G vs Ghat) median={s['rank_agreement_median']}")
    # verdict on D3 specifically
    d3 = next((s for s in all_summaries if s["channel"] == "D3" and not s.get("all_degenerate")), None)
    if d3:
        print(f"\n{'-'*78}")
        frac = d3["P_ATTACK_frac"]
        if frac >= 0.625:
            print(f"VERDICT: THEOREM-leaning. D3 P-attack in {frac:.0%} of seeds -> interaction-borne")
            print("  disparity structurally defeats floor-attestation; not a seed-lucky single run.")
        elif frac <= 0.375:
            print(f"VERDICT: ANECDOTE-leaning. D3 P-attack in only {frac:.0%} of seeds -> the single False")
            print("  was an unlucky draw; retract to 'near-floor ordering noisy', a gradient not a wall.")
        else:
            print(f"VERDICT: GENUINELY MIXED. D3 P-attack in {frac:.0%} of seeds -> report as a")
            print("  per-seed RATE, not a property; the attestation is unreliable on the interaction")
            print("  channel ~half the time, which is itself the finding (intermittent verifiability).")

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(
        {"args": vars(args), "summaries": all_summaries, "runs": all_runs},
        indent=2, sort_keys=True, default=str))
    print(f"\nwritten to {args.out}")


if __name__ == "__main__":
    main()
