#!/usr/bin/env python3
"""
Pre-reg #14 verdict aggregator (expanded-vintage replication).

Pre-reg: docs/superpowers/specs/2026-05-15-expanded-vintage-replication-preregistration-note.md
Commit: 24e20f8 (substantive) / f091480 (OTS)

Reads the unified 7-vintage frame_evocation output and grades the four
pre-registered predictions + the two graded adversarial self-checks. No new
compute on raw FM data; operates on saved discriminator scores + labels.

Prediction definitions are taken verbatim from the pre-reg §3 and the
post-hoc note (working_notes/2026-05-15-variant-asymmetry-posthoc-analysis.md):

  P1  named_diff structural pattern on FRESH cells (4 fresh vintages):
      fires on >=80% of silence (ALL if 1-2), <=20% of reorg-agreement
      (0 if 1-2), <=15% false-positive on no-reorg.
  P2  M2_mean silence-only AUC >= 0.95 on FULL corpus, perm p < 0.05.
      'silence-only' = silence (n+) vs all-non-silence (n-), per post-hoc note.
  P3  >= 1 silence cell in the 4 fresh vintages.
  P4  M3_max strictly beats M1 on the FULL-corpus primary binary
      (silence u reorg-agreement vs no-reorg) by AUC-diff >= 0.05, perm p < 0.05.
  4a  placebo: under silence-label shuffle, named_diff silence-only AUC
      exceeds 0.95 at rate <= 5%.
  4d  2009Q1 no-reorg named_diff fire-rate >= 5% (descriptive).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
from frame_evocation_test import auc, auc_diff_permutation  # noqa: E402

RUNS_DIR = REPO_ROOT / "runs"
FRAME_JSON = RUNS_DIR / "frame_evocation_2026-05-20.json"
OUTPUT = RUNS_DIR / "expanded_vintage_2026-05-20.json"

FRESH = {"2009Q1", "2014Q3", "2012Q1", "2020Q2"}
N_PERM = 10_000
SEED = 20260515


def label_of(c: dict) -> str:
    if c["label_silence"]:
        return "silence"
    if c["label_reorganized"]:
        return "reorg_agreement"
    return "no_reorg"


def grade_P1(fresh: list[dict]) -> dict:
    by = {"silence": [], "reorg_agreement": [], "no_reorg": []}
    for c in fresh:
        by[label_of(c)].append(c)

    def rate(cells):
        return (sum(c["named_diff"] for c in cells) / len(cells)) if cells else None

    n_sil, n_ra, n_nr = len(by["silence"]), len(by["reorg_agreement"]), len(by["no_reorg"])
    fired_sil = sum(c["named_diff"] for c in by["silence"])
    fired_ra = sum(c["named_diff"] for c in by["reorg_agreement"])

    # silence leg
    if n_sil == 0:
        sil_pass, sil_note = None, "N/A (no fresh silence cells)"
    elif n_sil <= 2:
        sil_pass = fired_sil == n_sil
        sil_note = f"small-n: fires on ALL? {fired_sil}/{n_sil}"
    else:
        sil_pass = (fired_sil / n_sil) >= 0.80
        sil_note = f"{fired_sil}/{n_sil} = {fired_sil/n_sil:.0%} (>=80%)"
    # reorg-agreement leg
    if n_ra == 0:
        ra_pass, ra_note = True, "N/A leg (no fresh reorg-agreement cells) -> vacuous pass"
    elif n_ra <= 2:
        ra_pass = fired_ra == 0
        ra_note = f"small-n: fires on 0? fired={fired_ra}/{n_ra}"
    else:
        ra_pass = (fired_ra / n_ra) <= 0.20
        ra_note = f"{fired_ra}/{n_ra} = {fired_ra/n_ra:.0%} (<=20%)"
    # false-positive leg
    fp_rate = rate(by["no_reorg"])
    fp_pass = (fp_rate is not None) and (fp_rate <= 0.15)

    if sil_pass is None:
        verdict = "N/A"
    else:
        verdict = "HIT" if (sil_pass and ra_pass and fp_pass) else "MISS"
    return {
        "verdict": verdict,
        "n_silence": n_sil, "n_reorg_agreement": n_ra, "n_no_reorg": n_nr,
        "named_diff_fire_rate_silence": rate(by["silence"]),
        "named_diff_fire_rate_reorg_agreement": rate(by["reorg_agreement"]),
        "named_diff_fire_rate_no_reorg": fp_rate,
        "silence_leg": {"pass": sil_pass, "note": sil_note},
        "reorg_agreement_leg": {"pass": ra_pass, "note": ra_note},
        "false_positive_leg": {"pass": fp_pass, "fp_rate": fp_rate, "threshold": 0.15},
    }


def silence_only_auc(cells: list[dict], score_key: str) -> float | None:
    """silence (1) vs all-non-silence (0); higher score = more unreliable."""
    scores = [c[score_key] for c in cells]
    labels = [int(c["label_silence"]) for c in cells]
    return auc(scores, labels)


def perm_p_single(cells: list[dict], score_key: str, n_perm: int, seed: int) -> dict:
    """Two-sided label-permutation p for a single discriminator's silence-only AUC."""
    scores = [c[score_key] for c in cells]
    labels = np.array([int(c["label_silence"]) for c in cells])
    obs = auc(scores, labels.tolist())
    if obs is None:
        return {"auc": None, "p_two_sided": None}
    rng = np.random.default_rng(seed)
    # two-sided around 0.5 (AUC null centre)
    null = np.empty(n_perm)
    for i in range(n_perm):
        a = auc(scores, rng.permutation(labels).tolist())
        null[i] = np.nan if a is None else a
    valid = null[~np.isnan(null)]
    p = float((np.abs(valid - 0.5) >= abs(obs - 0.5)).mean()) if valid.size else None
    exceed = float((valid > 0.95).mean()) if valid.size else None
    return {"auc": float(obs), "p_two_sided": p, "null_rate_gt_0.95": exceed}


def main() -> int:
    fe = json.loads(FRAME_JSON.read_text())
    per_cell = fe["per_cell"]
    fresh = [c for c in per_cell if c["vintage"] in FRESH]

    # --- P1 (fresh cells) ---
    p1 = grade_P1(fresh)

    # --- P2 (full corpus, silence vs all-non-silence) ---
    m2 = perm_p_single(per_cell, "M2_mean_cell", N_PERM, SEED)
    p2_verdict = "HIT" if (m2["auc"] is not None and m2["auc"] >= 0.95
                           and m2["p_two_sided"] is not None and m2["p_two_sided"] < 0.05) else "MISS"

    # --- P3 (>=1 fresh silence cell) ---
    n_fresh_silence = sum(c["label_silence"] for c in fresh)
    p3_verdict = "HIT" if n_fresh_silence >= 1 else "MISS"

    # --- P4 (full corpus primary binary: M3_max vs M1, diff >= 0.05, p < 0.05) ---
    primary_labels = [int(c["label_nontrivial"]) for c in per_cell]
    m3 = [c["M3_max_cell"] for c in per_cell]
    m1 = [c["M1_cell"] for c in per_cell]
    p4 = auc_diff_permutation(m3, m1, primary_labels, N_PERM, SEED)
    p4_verdict = "HIT" if (p4["obs_diff"] is not None and p4["obs_diff"] >= 0.05
                           and p4["p_two_sided"] is not None and p4["p_two_sided"] < 0.05) else "MISS"

    # --- 4a placebo (named_diff silence-only AUC under null) ---
    nd = perm_p_single(per_cell, "named_diff", N_PERM, SEED)
    a4_pass = (nd["null_rate_gt_0.95"] is not None) and (nd["null_rate_gt_0.95"] <= 0.05)

    # --- 4d (2009Q1 no-reorg named_diff fire rate) ---
    q09_nr = [c for c in per_cell if c["vintage"] == "2009Q1" and label_of(c) == "no_reorg"]
    q09_rate = (sum(c["named_diff"] for c in q09_nr) / len(q09_nr)) if q09_nr else None

    out = {
        "source_frame_json": FRAME_JSON.name,
        "n_cells_full": len(per_cell),
        "n_cells_fresh": len(fresh),
        "P1_named_diff_fresh": p1,
        "P2_M2mean_silence_only_full": {
            "verdict": p2_verdict, "auc": m2["auc"], "p_two_sided": m2["p_two_sided"],
            "threshold_auc": 0.95},
        "P3_silence_outside_2016Q1": {
            "verdict": p3_verdict, "n_fresh_silence_cells": int(n_fresh_silence)},
        "P4_M3max_vs_M1_full_primary": {
            "verdict": p4_verdict, "obs_diff": p4["obs_diff"], "p_two_sided": p4["p_two_sided"],
            "auc_M3max": p4["auc_a"], "auc_M1": p4["auc_b"], "threshold_diff": 0.05},
        "adv_4a_placebo_named_diff": {
            "pass": a4_pass, "obs_auc": nd["auc"], "null_rate_gt_0.95": nd["null_rate_gt_0.95"]},
        "adv_4d_2009Q1_no_reorg_named_diff_rate": {
            "rate": q09_rate, "n_no_reorg": len(q09_nr), "flag_ge_5pct": (q09_rate or 0) >= 0.05},
    }
    OUTPUT.write_text(json.dumps(out, indent=2, default=str))

    # console scorecard
    print("=" * 64)
    print("PRE-REG #14 SCORECARD (expanded 7-vintage corpus)")
    print("=" * 64)
    print(f"corpus: n_full={len(per_cell)}  n_fresh={len(fresh)}  fresh_silence={int(n_fresh_silence)}")
    print()
    print(f"P1 named_diff (FRESH, prior 0.30):  {p1['verdict']}")
    print(f"    silence:        {p1['named_diff_fire_rate_silence']}  [{p1['silence_leg']['note']}] pass={p1['silence_leg']['pass']}")
    print(f"    reorg-agreement:{p1['named_diff_fire_rate_reorg_agreement']}  [{p1['reorg_agreement_leg']['note']}] pass={p1['reorg_agreement_leg']['pass']}")
    print(f"    no-reorg (FP):  {p1['named_diff_fire_rate_no_reorg']}  (<=0.15) pass={p1['false_positive_leg']['pass']}")
    print()
    print(f"P2 M2_mean silence-only AUC (FULL, prior 0.40):  {p2_verdict}")
    print(f"    AUC={m2['auc']:.4f}  perm p={m2['p_two_sided']:.4f}  (need >=0.95, p<0.05)")
    print()
    print(f"P3 silence outside 2016Q1 (prior 0.45):  {p3_verdict}  ({int(n_fresh_silence)} fresh silence cells)")
    print()
    print(f"P4 M3_max vs M1 (FULL primary, prior 0.30):  {p4_verdict}")
    print(f"    AUC M3_max={p4['auc_a']:.4f}  M1={p4['auc_b']:.4f}  diff={p4['obs_diff']:+.4f}  perm p={p4['p_two_sided']:.4f}")
    print()
    print(f"4a placebo (named_diff null AUC>0.95 rate <=5%):  pass={a4_pass}  (obs AUC={nd['auc']:.4f}, null>0.95 rate={nd['null_rate_gt_0.95']:.4f})")
    print(f"4d 2009Q1 no-reorg named_diff rate:  {q09_rate}  (n={len(q09_nr)}, flag>=5%={out['adv_4d_2009Q1_no_reorg_named_diff_rate']['flag_ge_5pct']})")
    print()
    print(f"wrote {OUTPUT.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
