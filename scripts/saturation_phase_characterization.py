#!/usr/bin/env python3
"""
Saturation-phase characterization — post-hoc.

POST-HOC, NOT pre-registered. The 5:50 AM 2026-05-14 root-tier substrate-
independence addendum mentioned "~50% property_state penetration" for the
2 reorganized-but-verdict-agreeing FM cells; this script characterizes the
full FM-cell saturation distribution in light of that and finds the
distribution is TRIMODAL with sharp gaps, not the continuous monotone I
naively expected. Also computes the property_state vs prohibited_3
contrast which the previous analyses did not do.

Input: runs/silence_manufacture_2026-05-13.json (#12 result data).
Output: runs/saturation_phase_characterization.json + stdout tables.
"""
from __future__ import annotations
import json
import math
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNS_DIR = REPO_ROOT / "runs"
IN_PATH = RUNS_DIR / "silence_manufacture_2026-05-13.json"
OUT_PATH = RUNS_DIR / "saturation_phase_characterization.json"


def rank(xs):
    sorted_xs = sorted(enumerate(xs), key=lambda t: t[1])
    ranks = [0] * len(xs)
    i = 0
    while i < len(xs):
        j = i
        while j + 1 < len(xs) and sorted_xs[j + 1][1] == sorted_xs[i][1]:
            j += 1
        avg_rank = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranks[sorted_xs[k][0]] = avg_rank
        i = j + 1
    return ranks


def pearson(xs, ys):
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    if sxx * syy == 0:
        return float("nan")
    return sxy / math.sqrt(sxx * syy)


def spearman(xs, ys):
    return pearson(rank(xs), rank(ys))


def partial_spearman(xs, ys, zs):
    """Partial Spearman: residualize ranks of x,y on ranks of z, correlate."""
    rx, ry, rz = rank(xs), rank(ys), rank(zs)
    n = len(rz)
    mz = sum(rz) / n
    szz = sum((r - mz) ** 2 for r in rz)
    if szz == 0:
        return float("nan")

    def resid(r):
        mr = sum(r) / n
        cov = sum((r[i] - mr) * (rz[i] - mz) for i in range(n))
        alpha = cov / szz
        beta = mr - alpha * mz
        return [r[i] - alpha * rz[i] - beta for i in range(n)]

    return pearson(resid(rx), resid(ry))


def main():
    with IN_PATH.open() as f:
        data = json.load(f)

    cells = data["cells"]
    rows = []
    for c in cells:
        rows.append({
            "vintage": c["vintage"],
            "cell": c["cell"],
            "sat_ps": c["property_state_saturation_A"],
            "sat_p3": c["prohibited_3_saturation_A"],
            "r2_A": c["R2_named_A"],
            "r2_B": c["R2_named_B"],
            "r2_gap": abs(c["R2_named_A"] - c["R2_named_B"]),
            "verdict_differs": bool(c["verdict_differs"]),
            "reorg": bool(c["is_reorganized_primary"]),
            "silence": bool(c["manufactured_silence"]),
            "jaccard": c["jaccard_primary"],
        })

    n = len(rows)
    sat_ps = [r["sat_ps"] for r in rows]
    sat_p3 = [r["sat_p3"] for r in rows]
    r2_gap = [r["r2_gap"] for r in rows]
    silence = [1.0 if r["silence"] else 0.0 for r in rows]
    reorg = [1.0 if r["reorg"] else 0.0 for r in rows]

    # 1. Marginal Spearman
    marg = {
        "property_state_vs_r2_gap": spearman(sat_ps, r2_gap),
        "prohibited_3_vs_r2_gap": spearman(sat_p3, r2_gap),
        "property_state_vs_silence": spearman(sat_ps, silence),
        "prohibited_3_vs_silence": spearman(sat_p3, silence),
        "property_state_vs_reorg": spearman(sat_ps, reorg),
        "prohibited_3_vs_reorg": spearman(sat_p3, reorg),
        "property_state_vs_prohibited_3": spearman(sat_ps, sat_p3),
    }

    # 2. Partial Spearman
    partial = {
        "property_state_given_prohibited_3_vs_r2_gap": partial_spearman(sat_ps, r2_gap, sat_p3),
        "prohibited_3_given_property_state_vs_r2_gap": partial_spearman(sat_p3, r2_gap, sat_ps),
        "property_state_given_prohibited_3_vs_silence": partial_spearman(sat_ps, silence, sat_p3),
        "prohibited_3_given_property_state_vs_silence": partial_spearman(sat_p3, silence, sat_ps),
    }

    # 3. By-regime
    by_regime = {}
    for vintage in ["2008Q1", "2016Q1", "2018Q1"]:
        sub = [r for r in rows if r["vintage"] == vintage]
        if len(sub) < 3:
            continue
        s_ps = [r["sat_ps"] for r in sub]
        s_p3 = [r["sat_p3"] for r in sub]
        rg = [r["r2_gap"] for r in sub]
        by_regime[vintage] = {
            "n": len(sub),
            "property_state_vs_r2_gap": spearman(s_ps, rg),
            "prohibited_3_vs_r2_gap": spearman(s_p3, rg),
        }

    # 4. Phase-structure: sorted distribution + threshold contingency
    sorted_rows = sorted(rows, key=lambda r: r["sat_ps"])
    phase_table = [{
        "vintage": r["vintage"], "cell": r["cell"],
        "sat_ps": r["sat_ps"], "sat_p3": r["sat_p3"],
        "r2_gap": r["r2_gap"], "jaccard": r["jaccard"],
        "reorg": r["reorg"], "silence": r["silence"],
    } for r in sorted_rows]

    thresholds = []
    for thr in [0.30, 0.40, 0.49, 0.50, 0.51, 0.60, 0.70, 0.99, 1.00]:
        above = [r for r in rows if r["sat_ps"] >= thr]
        below = [r for r in rows if r["sat_ps"] < thr]
        thresholds.append({
            "thr": thr,
            "n_above": len(above),
            "reorg_above": sum(1 for r in above if r["reorg"]),
            "silence_above": sum(1 for r in above if r["silence"]),
            "n_below": len(below),
            "reorg_below": sum(1 for r in below if r["reorg"]),
            "silence_below": sum(1 for r in below if r["silence"]),
        })

    # 5. Carrier-asymmetry: cells where prohibited_3 > property_state
    carrier_asym = []
    for r in rows:
        gap = r["sat_p3"] - r["sat_ps"]
        if gap > 0.15:
            carrier_asym.append({
                "vintage": r["vintage"], "cell": r["cell"],
                "sat_ps": r["sat_ps"], "sat_p3": r["sat_p3"],
                "carrier_gap": gap,
                "r2_gap": r["r2_gap"],
                "reorg": r["reorg"], "silence": r["silence"],
            })

    # 6. Identify the phase clusters explicitly
    phase_clusters = {
        "phase_0_no_reorg": [
            (r["vintage"], r["cell"], r["sat_ps"])
            for r in sorted_rows if r["sat_ps"] < 0.50
        ],
        "phase_1_reorg_no_silence": [
            (r["vintage"], r["cell"], r["sat_ps"])
            for r in sorted_rows if 0.50 <= r["sat_ps"] < 1.00
        ],
        "phase_2_manufactured_silence": [
            (r["vintage"], r["cell"], r["sat_ps"])
            for r in sorted_rows if r["sat_ps"] >= 1.00
        ],
    }

    out = {
        "label": "post-hoc characterization",
        "input": str(IN_PATH.relative_to(REPO_ROOT)),
        "n_cells": n,
        "marginal_spearman": marg,
        "partial_spearman": partial,
        "by_regime": by_regime,
        "thresholds": thresholds,
        "carrier_asymmetry_cells_p3_minus_ps_gt_0_15": carrier_asym,
        "phase_clusters": phase_clusters,
        "phase_table": phase_table,
    }

    OUT_PATH.write_text(json.dumps(out, indent=2))

    # Stdout summary
    print(f"N = {n} cells across 3 FM vintages")
    print()
    print("MARGINAL Spearman ρ:")
    for k, v in marg.items():
        print(f"  {k}: {v:+.3f}")
    print()
    print("PARTIAL Spearman ρ (controlling for the other predictor):")
    for k, v in partial.items():
        print(f"  {k}: {v:+.3f}")
    print()
    print("BY-REGIME:")
    for v, info in by_regime.items():
        print(f"  {v} (n={info['n']}): property_state ρ={info['property_state_vs_r2_gap']:+.3f}, "
              f"prohibited_3 ρ={info['prohibited_3_vs_r2_gap']:+.3f}")
    print()
    print("PHASE CLUSTERS (by property_state_saturation_A):")
    for k, v in phase_clusters.items():
        print(f"  {k}: n={len(v)}")
        for vintage, cell, sps in v[:5]:
            print(f"    {vintage} {cell}: sat_ps={sps:.2f}")
        if len(v) > 5:
            print(f"    ... +{len(v)-5} more")
    print()
    print(f"Written: {OUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
