#!/usr/bin/env python3
"""C4 gamma-sweep — the gap(gamma) operating-curve follow-on to the V2 C4 MISS.

Follow-on to the FROZEN V2 pre-reg (docs/.../2026-05-24-compliant-practice-disparate-impact-V2-preregistration-note.md,
commit 8fa7992). The C4 result note (2026-05-25) found V2_adv gate-bound at retained~=0.54
under the frozen gamma=0.02. gamma (the admissible AUC-gate tolerance, pre-reg sec 2h) is a
declared codification constant; sec 2h already sweeps tau_launder +/-50% by the same
declare-and-sweep discipline (knob-robustness). This driver sweeps gamma and reports the
OPERATING SURFACE, plus the new falsifiable object frozen in the gap-gamma prediction ledger:

    gap(gamma) = retained_excess_adv(gamma) - retained_compliant     (per cell)

where retained_compliant = adverse_excess(M_compliant)/adverse_excess(M_full) is the
gamma-INDEPENDENT honest baseline (M_compliant is an ungated standard fit). gap is the
audit-visible residue of intent. Predictions are frozen in the ledger BEFORE this is run
(proof-of-work). This script only *measures*.

Ledger handling rules implemented here:
  - gap conditioned on a VALID in-gate adversary (report-frame gate pass); gate_pass_rate
    co-primary (ledger sec 1b).
  - balanced panel = seeds non-degenerate at min-gamma, evaluated at every gamma (within-seed
    curve; ledger sec 1 balanced-panel + P-gamma-deg).
  - constant CMA budget across gamma (red-team A2): early-stop disabled, maxgen fixed via
    --budget-maxgen (default 70 -> 1120 evals ~= committed grid median 1104).
  - degenerate_start / sign-flip / near-floor-denominator diagnostics (A3/A4/A5).

SHARDING (128-core friendly; the balanced panel needs all cells, so compute is shardable but
aggregation is a single merge pass):
    # compute shards in parallel (each writes a {"cells":[...]} shard file)
    PYTHONPATH=. python3 scripts/c4_gamma_sweep.py --shard-only --proxy 0.85 \
        --gammas 0.0 --seeds-list 0 1 --out runs/c4-gamma-shards/ps085_g0.000_s0-1.json
    # then merge + aggregate
    PYTHONPATH=. python3 scripts/c4_gamma_sweep.py --merge runs/c4-gamma-shards/ps085_*.json \
        --proxy 0.85 --seeds 8 --out runs/c4_gamma_sweep_ps085.json
"""
from __future__ import annotations

import argparse
import glob
import importlib.util
import json
import sys
import time
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "compliant_practice_test", REPO / "scripts" / "compliant_practice_test.py")
eng = importlib.util.module_from_spec(_spec)
sys.modules["compliant_practice_test"] = eng
_spec.loader.exec_module(eng)

GAMMA_GRID = (0.0, 0.005, 0.01, 0.02, 0.04, 0.08, 0.15)


def _paired_ci(vals, reps=2000, seed=0):
    if len(vals) < 2:
        return None
    rng = np.random.default_rng(seed)
    boot = [np.mean(rng.choice(vals, size=len(vals), replace=True)) for _ in range(reps)]
    return [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))]


def compute_cells(proxy, seeds, gammas, n, lever, holdout):
    t0 = time.time()
    cells = []
    for g in gammas:
        for sd in seeds:
            c = eng.c4_cell(proxy, sd, n, smoke=False, lever=lever, gamma=g, holdout=holdout)
            rc = (c["ae_compliant"] / c["ae_full"]) if abs(c["ae_full"]) >= eng.EPSILON_EXCESS else None
            c["retained_compliant"] = (None if rc is None else float(rc))
            ra = c["retained_excess_adv"]
            c["gap"] = (None if (ra is None or rc is None) else float(ra - rc))
            c["degenerate_start"] = bool((not c["gate_admissible_pass"])
                                         and (c["auc_strict"] > c["auc_compliant"] + g))
            cells.append(c)
            gap_s = "None" if c["gap"] is None else f"{c['gap']:+.3f}"
            ra_s = "None" if ra is None else f"{ra:+.3f}"
            rc_s = "None" if rc is None else f"{rc:+.3f}"
            print(f"[{time.time()-t0:6.1f}s] ps={proxy} gamma={g:.3f} seed={sd} | "
                  f"retained_adv={ra_s} comp={rc_s} gap={gap_s} | "
                  f"gateA={c['gate_admissible_pass']} rungs={c['rungs_pass']} "
                  f"deg={c['degenerate_start']} | evals={c['cmaes_evals']}", flush=True)
    return cells


def aggregate(cells, gammas, n_seeds):
    g0 = min(gammas)
    panel = sorted({c["seed"] for c in cells
                    if abs(c["gamma"] - g0) < 1e-12 and not c["degenerate_start"]
                    and c["gap"] is not None})
    g0cells = [c for c in cells if abs(c["gamma"] - g0) < 1e-12]
    panel_diag = {
        "n_panel": len(panel), "n_total_seeds": n_seeds,
        "auc_comp_minus_strict_included": [round(c["auc_compliant"] - c["auc_strict"], 4)
                                           for c in g0cells if c["seed"] in panel],
        "auc_comp_minus_strict_excluded": [round(c["auc_compliant"] - c["auc_strict"], 4)
                                           for c in g0cells if c["seed"] not in panel],
    }

    def _agg(rows):
        # gap over VALID in-gate adversaries only (report-frame gate pass; ledger sec 1b);
        # gate_pass_rate over all rows is co-primary.
        gate_rows = [c for c in rows if c["gate_admissible_pass"]]
        gaps = [c["gap"] for c in gate_rows if c["gap"] is not None]
        radv = [c["retained_excess_adv"] for c in gate_rows if c["retained_excess_adv"] is not None]
        rcomp = [c["retained_compliant"] for c in gate_rows if c["retained_compliant"] is not None]
        return {
            "n": len(rows), "n_gate_pass": len(gate_rows),
            "gate_pass_rate": (float(len(gate_rows) / len(rows)) if rows else None),
            "gap_mean": (float(np.mean(gaps)) if gaps else None),
            "gap_median": (float(np.median(gaps)) if gaps else None),
            "gap_ci": _paired_ci(np.array(gaps)) if len(gaps) > 1 else None,
            "retained_adv_mean": (float(np.mean(radv)) if radv else None),
            "retained_compliant_mean": (float(np.mean(rcomp)) if rcomp else None),
            "n_s_flip": sum(c.get("s_flip", False) for c in rows),
            "n_aefull_near_floor": sum(abs(c["ae_full"]) < 0.10 for c in rows),
            "evals_mean": float(np.mean([c["cmaes_evals"] for c in rows])) if rows else None,
        }

    by_gamma = {}
    for g in gammas:
        sub = [c for c in cells if abs(c["gamma"] - g) < 1e-12]
        clean = [c for c in sub if not c["degenerate_start"]]
        bal = [c for c in sub if c["seed"] in panel]
        by_gamma[f"{g:.3f}"] = {
            "n_total": len(sub), "n_degenerate_start": sum(c["degenerate_start"] for c in sub),
            "balanced_panel": _agg(bal),
            "per_gamma_clean": _agg(clean),
            "success_rate": float(np.mean([c["P_C4_success"] for c in sub])) if sub else None,
        }
    return panel, panel_diag, by_gamma


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--proxy", type=float, default=0.85)
    ap.add_argument("--seeds", type=int, default=8, help="range(seeds); aggregation panel size")
    ap.add_argument("--seeds-list", type=int, nargs="+", default=None,
                    help="explicit seeds for a compute shard (overrides --seeds)")
    ap.add_argument("--n", type=int, default=eng.N_DEFAULT)
    ap.add_argument("--lever", choices=["reweight", "subset", "both"], default="reweight")
    ap.add_argument("--gammas", type=float, nargs="+", default=list(GAMMA_GRID))
    ap.add_argument("--budget-maxgen", type=int, default=70,
                    help="constant CMA generations (x pop 16); 70 -> 1120 evals ~= committed median")
    ap.add_argument("--no-holdout", dest="holdout", action="store_false",
                    help="legacy test-selected eval (reproduces committed grid); default leak-free")
    ap.add_argument("--shard-only", action="store_true", help="compute+write cells, no aggregation")
    ap.add_argument("--merge", nargs="+", default=None, help="shard files to merge+aggregate")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    # constant budget across gamma (red-team A2): disable early-stop, fix maxgen
    eng.C4_CONV_PATIENCE = 10**9
    eng.C4_MAXGEN = args.budget_maxgen

    out_path = (Path(args.out).resolve() if args.out else
                REPO / "runs" / f"c4_gamma_sweep_ps{int(round(args.proxy*100)):03d}.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if args.merge:
        files = [f for pat in args.merge for f in glob.glob(pat)]
        cells = []
        for f in files:
            cells.extend(json.loads(Path(f).read_text())["cells"])
        cells.sort(key=lambda c: (c["gamma"], c["seed"]))
        panel, panel_diag, by_gamma = aggregate(cells, args.gammas, args.seeds)
        out_path.write_text(json.dumps({
            "experiment": "C4 gamma-sweep -- gap(gamma) operating surface + intent-residue test",
            "follow_on_to_pre_reg_commit": "8fa7992",
            "ledger": "docs/superpowers/specs/2026-05-25-c4-gamma-sweep-gap-preregistration-note.md",
            "proxy_strength": args.proxy, "lever": args.lever, "n": args.n, "seeds": args.seeds,
            "gamma_grid": list(args.gammas), "holdout": cells[0].get("holdout"),
            "budget_maxgen": args.budget_maxgen, "merged_from": files,
            "gap_definition": "gap = retained_excess_adv(gamma) - retained_compliant",
            "balanced_panel_seeds": panel, "balanced_panel_anchor_gamma": min(args.gammas),
            "panel_diag": panel_diag, "by_gamma": by_gamma, "cells": cells,
        }, indent=2))
        print(f"\nMerged {len(files)} shards -> {out_path.relative_to(REPO)} ({len(cells)} cells)")
        return

    seeds = args.seeds_list if args.seeds_list is not None else list(range(args.seeds))
    cells = compute_cells(args.proxy, seeds, args.gammas, args.n, args.lever, args.holdout)

    if args.shard_only:
        out_path.write_text(json.dumps({"shard": True, "proxy_strength": args.proxy,
                                        "gammas": args.gammas, "seeds": seeds,
                                        "holdout": args.holdout, "budget_maxgen": args.budget_maxgen,
                                        "cells": cells}, indent=2))
        print(f"\nShard -> {out_path.relative_to(REPO)} ({len(cells)} cells)")
        return

    panel, panel_diag, by_gamma = aggregate(cells, args.gammas, args.seeds)
    out_path.write_text(json.dumps({
        "experiment": "C4 gamma-sweep -- gap(gamma) operating surface + intent-residue test",
        "follow_on_to_pre_reg_commit": "8fa7992",
        "ledger": "docs/superpowers/specs/2026-05-25-c4-gamma-sweep-gap-preregistration-note.md",
        "proxy_strength": args.proxy, "lever": args.lever, "n": args.n, "seeds": args.seeds,
        "gamma_grid": list(args.gammas), "holdout": args.holdout, "budget_maxgen": args.budget_maxgen,
        "gap_definition": "gap = retained_excess_adv(gamma) - retained_compliant",
        "balanced_panel_seeds": panel, "balanced_panel_anchor_gamma": min(args.gammas),
        "panel_diag": panel_diag, "by_gamma": by_gamma, "cells": cells,
    }, indent=2))
    print(f"\nWrote {out_path.relative_to(REPO)} ({len(cells)} cells)")


if __name__ == "__main__":
    main()
