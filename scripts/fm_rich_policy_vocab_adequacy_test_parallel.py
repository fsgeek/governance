"""Parallel runner for the #11 / #14 vocabulary-adequacy test.

Same math as scripts/fm_rich_policy_vocab_adequacy_test.py — the per-cell
function (`build_band_for_cell`), the per-cell placebo
(`placebo_for_cell`), and every numerical primitive are imported from the
serial script. This file changes orchestration only: the cell loop becomes
a `ProcessPoolExecutor` fan-out instead of a Python `for`.

Why: on the 128-thread workstation, the serial script saturates one logical
core (~0.8% on Task Manager) and leaves 127 cores idle. With ~10-35 analyzed
cells per vintage, a process-pool over cells trades wall-clock for cores.

Pre-reg #14 §2b allows documented patches with hash recorded in the result
note as long as discriminator-computation logic does not change. This file
adds no math; it changes only the loop that calls the math.

Parity validation: scripts/parity_check_fm_rich_policy.py compares output
JSON to an existing serial-run JSON cell-by-cell with a documented FP
tolerance.

Usage:
    PYTHONPATH=. python scripts/fm_rich_policy_vocab_adequacy_test_parallel.py \\
        --vintage 2008Q1 --strata rate --no-placebo --no-eps-arm --workers 16
"""
from __future__ import annotations

# BLAS / OMP thread-cap must happen before numpy / sklearn import, so workers
# (which inherit env) don't oversubscribe the 128 logical cores when we run
# many of them concurrently.
import os
for _k in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS",
           "BLIS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_k, "1")

import argparse
import datetime as dt
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np
import pandas as pd

# Make sibling scripts (this dir) and the repo root (parent dir) importable.
# The repo root must be on sys.path so `from policy.encoder import ...` resolves.
_SCRIPTS_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _SCRIPTS_DIR.parent
for _p in (str(_REPO_ROOT), str(_SCRIPTS_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from fm_rich_policy_vocab_adequacy_test import (
    DEPTHS, DTI_CEIL, EPSILON, EPS_ARM, FICO_FLOOR, FM_DATA_DIR,
    GEOGRAPHY_LENDER_PROHIBITED,
    HOLDOUT_FRAC, LEAF_MINS, LTV_CEIL, MIN_CELL_LOANS, PLURALITY_RHO_MAX,
    POLICY_PATH,
    _now_iso,
    build_band_for_cell, placebo_for_cell,
    llpa_cell_labels, load_vintage, prep, rate_band_labels, usable_features,
)
from policy.encoder import load_policy
from wedge.collectors.fanniemae import (
    derive_origination_and_label, filter_eligible,
    load_collapsed_cached, read_raw_auto, to_feature_frame,
)


def load_vintage_auto(vintage: str, *, nrows=None, prefer_parquet: bool = True,
                      use_cache: bool = True):
    """Load + collapse + filter + feature_frame for one vintage.

    Tries (in order):
      1. The collapsed-prep Parquet cache (load_collapsed_cached) — skips
         the whole load+derive+filter pipeline. Disabled when nrows is set
         (row-limited reads aren't a meaningful cache key) or use_cache=False.
      2. Raw-Parquet sibling via read_raw_auto, then the full pipeline.
      3. CSV via read_raw, then the full pipeline.
    """
    fm_csv = FM_DATA_DIR / f"{vintage}.csv"
    if not fm_csv.exists():
        raise FileNotFoundError(f"{fm_csv} not found")

    cache_eligible = use_cache and nrows is None
    if cache_eligible:
        t0 = time.time()
        feats, src = load_collapsed_cached(
            fm_csv, prefer_parquet=prefer_parquet, use_cache=True)
        elapsed = time.time() - t0
        print(f"[{_now_iso()}] loaded FM {vintage} via {src} in {elapsed:.1f}s; "
              f"eligible rows: {len(feats)}", flush=True)
        return feats, src

    src = "parquet" if prefer_parquet and (
        fm_csv.parent / "parquet" / f"{vintage}.parquet").exists() else "csv"
    print(f"[{_now_iso()}] loading FM {vintage} via {src} "
          f"(nrows={nrows}, cache disabled)...", flush=True)
    t0 = time.time()
    raw = read_raw_auto(fm_csv, nrows=nrows, prefer_parquet=prefer_parquet)
    collapsed = derive_origination_and_label(raw)
    eligible = filter_eligible(collapsed)
    feats = to_feature_frame(eligible).copy()
    print(f"[{_now_iso()}] loaded+collapsed in {time.time()-t0:.0f}s "
          f"({src}); eligible rows: {len(feats)}", flush=True)
    return feats, src


# ---------------------------------------------------------------------------
# Worker functions. Top-level (picklable) so ProcessPoolExecutor can spawn on
# Windows-spawn as well as POSIX-fork.
# ---------------------------------------------------------------------------
def _process_cell(payload):
    """One unit of work: build variants A and B for one cell.

    Returns (cell_id, cell_record_dict) matching the serial output shape.
    """
    (cell_id, cell, named, ext, mono_A,
     named_B, ext_B, mono_B,
     max_subset_size, epsilon) = payload
    t0 = time.time()
    recA = build_band_for_cell(cell, named, ext, mono_A,
                               epsilon=epsilon, max_subset_size=max_subset_size)
    recB = build_band_for_cell(cell, named_B, ext_B, mono_B,
                               epsilon=epsilon, max_subset_size=max_subset_size)
    return cell_id, {
        "n": int(len(cell)),
        "variant_A_geography_admissible": recA,
        "variant_B_compliant_geography_prohibited": recB,
        "seconds": round(time.time() - t0, 1),
    }


def _process_placebo(payload):
    """One placebo unit: C-random + C-scrambled for one plural-A cell."""
    cell_id, cell, named, ext, max_subset_size, rng_seed = payload
    t0 = time.time()
    out = placebo_for_cell(cell, named, ext,
                           max_subset_size=max_subset_size, rng_seed=rng_seed)
    return cell_id, out, round(time.time() - t0, 1)


def _process_eps(payload):
    """One eps-arm unit: rerun build_band_for_cell at one non-default epsilon."""
    cell_id, eps, cell, named, ext, mono_A, max_subset_size = payload
    rec = build_band_for_cell(cell, named, ext, mono_A,
                              epsilon=eps, max_subset_size=max_subset_size)
    return cell_id, eps, {
        "verdict": rec.get("verdict"), "plural": rec.get("plural"),
        "R2_named": rec.get("R2_named"), "R2_all": rec.get("R2_all"),
        "dR2_ext": rec.get("dR2_ext"), "gap_recurs": rec.get("gap_recurs"),
        "n_distinct_uf": rec.get("n_distinct_uf_members"),
    }


# ---------------------------------------------------------------------------
def run_stratum_parallel(df, *, stratum, cell_col, named, ext,
                         mono_default_A, max_subset_size, min_cell_loans,
                         do_placebo, do_eps_arm, probe, executor,
                         only_cell=None):
    """Parallel analog of run_stratum() in the serial script. Same outputs."""
    cells = df[cell_col].value_counts().sort_index()
    analyzed = [c for c, n in cells.items() if n >= min_cell_loans]
    if only_cell is not None:
        if only_cell not in analyzed:
            raise ValueError(f"--only-cell {only_cell!r} not in analyzable cells "
                             f"for {stratum}: {analyzed}")
        analyzed = [only_cell]
    elif probe and analyzed:
        analyzed = [analyzed[len(analyzed) // 2]]

    print(f"[{_now_iso()}] stratum {stratum}: {len(cells)} cells, "
          f"{len(analyzed)} >= {min_cell_loans} loans"
          f"{' (PROBE: one cell)' if probe else ''}: {analyzed}", flush=True)

    prohibited_B = set(GEOGRAPHY_LENDER_PROHIBITED)
    named_B = named
    ext_B = [f for f in ext if f not in prohibited_B]
    mono_default_B = {f: v for f, v in mono_default_A.items() if f in named_B}

    out = {"stratum": stratum, "cell_col": cell_col,
           "cell_loan_counts": {str(k): int(v) for k, v in cells.items()},
           "analyzed_cells": analyzed, "min_cell_loans": min_cell_loans,
           "cells": {}}

    # --- Phase 1: per-cell band builds (variant A + B together) ------------
    payloads = []
    for cell_id in analyzed:
        cell = df[df[cell_col] == cell_id].reset_index(drop=True)
        payloads.append((cell_id, cell, named, ext, mono_default_A,
                         named_B, ext_B, mono_default_B,
                         max_subset_size, EPSILON))

    t_stratum = time.time()
    futures = {executor.submit(_process_cell, p): p[0] for p in payloads}
    completed = 0
    for fut in as_completed(futures):
        cell_id, cell_rec = fut.result()
        out["cells"][cell_id] = cell_rec
        completed += 1
        a = cell_rec["variant_A_geography_admissible"]
        b = cell_rec["variant_B_compliant_geography_prohibited"]
        msg = (f"  [{completed}/{len(payloads)}] {cell_id}: "
               f"n={cell_rec['n']} A:[{a.get('verdict')}"
               + (f" plural={a.get('plural')} R2n={a.get('R2_named')} "
                  f"R2a={a.get('R2_all')} dR2={a.get('dR2_ext')} "
                  f"rung={a.get('rung_classification')} "
                  f"uf={a.get('n_distinct_uf_members')}"
                  if a.get('verdict') == 'ANALYZED' else f" {a.get('reason','')}")
               + f"] B:[{b.get('verdict')}"
               + (f" R2n={b.get('R2_named')} R2a={b.get('R2_all')}"
                  if b.get('verdict') == 'ANALYZED' else "")
               + f"] ({cell_rec['seconds']}s)")
        print(msg, flush=True)
    print(f"[{_now_iso()}] stratum {stratum} cell phase done in "
          f"{time.time() - t_stratum:.0f}s wall", flush=True)

    # Order cells by analyzed_cells (which is sorted); JSON preserves insertion.
    out["cells"] = {cid: out["cells"][cid] for cid in analyzed if cid in out["cells"]}

    plural_A = [cid for cid in analyzed
                if out["cells"][cid]["variant_A_geography_admissible"].get("plural")]
    out["plural_cells_variant_A"] = plural_A

    # --- Phase 2: placebo on plural-A cells -------------------------------
    if do_placebo and not probe and plural_A:
        plac_payloads = []
        for pi, cell_id in enumerate(plural_A):
            cell = df[df[cell_col] == cell_id].reset_index(drop=True)
            plac_payloads.append((cell_id, cell, named, ext,
                                  max_subset_size, 100_000 + pi * 31))
        t_p = time.time()
        plac_futures = {executor.submit(_process_placebo, p): p[0]
                        for p in plac_payloads}
        for fut in as_completed(plac_futures):
            cell_id, plac, elapsed = fut.result()
            out["cells"][cell_id]["placebo"] = plac
            print(f"  [placebo] {cell_id}: "
                  f"C-random R2_mean={plac.get('C_random', {}).get('R2_random_named_mean')} "
                  f"C-scrambled R2={plac.get('C_scrambled', {}).get('R2_scrambled_named')} "
                  f"scrambled_band_uf={plac.get('C_scrambled', {}).get('band_distinct_uf')} "
                  f"({elapsed}s)", flush=True)
        print(f"[{_now_iso()}] stratum {stratum} placebo phase done in "
              f"{time.time() - t_p:.0f}s wall", flush=True)

    # --- Phase 3: eps-arm on plural-A cells -------------------------------
    if do_eps_arm and not probe and plural_A:
        eps_payloads = []
        eps_results: dict = {cid: {} for cid in plural_A}
        for cell_id in plural_A:
            cell = df[df[cell_col] == cell_id].reset_index(drop=True)
            for eps in EPS_ARM:
                if eps == EPSILON:
                    # Reuse the result computed in phase 1.
                    rec = out["cells"][cell_id]["variant_A_geography_admissible"]
                    eps_results[cell_id][str(eps)] = {
                        "verdict": rec.get("verdict"), "plural": rec.get("plural"),
                        "R2_named": rec.get("R2_named"), "R2_all": rec.get("R2_all"),
                        "dR2_ext": rec.get("dR2_ext"), "gap_recurs": rec.get("gap_recurs"),
                        "n_distinct_uf": rec.get("n_distinct_uf_members"),
                    }
                    continue
                eps_payloads.append((cell_id, eps, cell, named, ext,
                                     mono_default_A, max_subset_size))
        t_e = time.time()
        eps_futures = {executor.submit(_process_eps, p): (p[0], p[1])
                       for p in eps_payloads}
        for fut in as_completed(eps_futures):
            cell_id, eps, rec = fut.result()
            eps_results[cell_id][str(eps)] = rec
        for cell_id in plural_A:
            per_eps = eps_results[cell_id]
            gaps = {e: v.get("gap_recurs") for e, v in per_eps.items()
                    if v.get("verdict") == "ANALYZED"}
            per_eps["verdict_stable_across_eps"] = (
                (len(set(gaps.values())) <= 1) if gaps else None)
            print(f"  [eps-arm] {cell_id}: " +
                  ", ".join(f"eps={e}:gap={v.get('gap_recurs')},"
                            f"R2n={v.get('R2_named')}"
                            for e, v in per_eps.items()
                            if isinstance(v, dict) and 'gap_recurs' in v),
                  flush=True)
        out["eps_arm_on_plural_variant_A"] = eps_results
        print(f"[{_now_iso()}] stratum {stratum} eps-arm phase done in "
              f"{time.time() - t_e:.0f}s wall", flush=True)

    return out


# ---------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(
        description="#11/#14 vocab-adequacy test, parallel cell loop.")
    ap.add_argument("--vintage", default="2018Q1",
                    help="FM acquisition quarter; reads data/fanniemae/{vintage}.csv")
    ap.add_argument("--n-rate-bands", type=int, default=10)
    ap.add_argument("--min-cell-loans", type=int, default=MIN_CELL_LOANS)
    ap.add_argument("--max-subset-size", type=int, default=7)
    ap.add_argument("--strata", default="rate,llpa")
    ap.add_argument("--no-placebo", action="store_true")
    ap.add_argument("--no-eps-arm", action="store_true")
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--only-cell", default=None)
    ap.add_argument("--nrows", type=int, default=None)
    ap.add_argument("--output-dir", type=Path, default=Path("runs"))
    ap.add_argument("--output-suffix", default="-parallel",
                    help="suffix on output filename (default: -parallel, "
                         "so we don't overwrite the serial reference)")
    ap.add_argument("--workers", type=int, default=None,
                    help="ProcessPoolExecutor max_workers (default: min(32, cells))")
    ap.add_argument("--no-parquet", action="store_true",
                    help="force CSV path even if a sibling Parquet exists "
                         "(default: prefer Parquet for the load step)")
    ap.add_argument("--no-cache", action="store_true",
                    help="bypass the collapsed-prep cache (always regenerate "
                         "from raw; do not write the cache either)")
    args = ap.parse_args()

    strata = [s.strip() for s in args.strata.split(",") if s.strip()]
    do_placebo = not args.no_placebo and not args.probe
    do_eps_arm = not args.no_eps_arm and not args.probe

    t_start = time.time()
    feats, load_source = load_vintage_auto(args.vintage, nrows=args.nrows,
                                           prefer_parquet=not args.no_parquet,
                                           use_cache=not args.no_cache)
    df, prep_meta = prep(feats)
    drop = list(prep_meta.get("near_constant_dropped", [])) + ["occupancy_status"]
    named, ext = usable_features(df, drop)
    print(f"[{_now_iso()}] usable named ({len(named)}): {named}\n"
          f"  usable extension ({len(ext)}): {ext}\n"
          f"  dropped: {sorted(set(drop))}", flush=True)
    pc = load_policy(POLICY_PATH)
    mono_default_A = {f: -v for f, v in pc.monotonicity_map.items() if f in named}
    print(f"  policy '{pc.name}' v{pc.version}: mandatory(exposed)={named}; "
          f"mono(default-conv)={mono_default_A}", flush=True)

    if "rate" in strata:
        df["s_rate"] = rate_band_labels(df["orig_interest_rate"], args.n_rate_bands)
    if "llpa" in strata:
        df["s_llpa"] = llpa_cell_labels(df["fico_range_low"], df["ltv"])

    results = {
        "pre_reg": "docs/superpowers/specs/2026-05-12-fm-rich-policy-vocab-adequacy-preregistration-note.md",
        "test": "fm-rich-policy-vocab-adequacy-#11", "substrate": f"FM-{args.vintage}",
        "run_at": _now_iso(), "policy": pc.name, "policy_version": pc.version,
        "policy_status": pc.status,
        "regime_envelope": {"fico_floor": FICO_FLOOR, "dti_ceiling": DTI_CEIL,
                            "ltv_ceiling": LTV_CEIL,
                            "conforming_upb": "auto-satisfied (FM acquisitions are conforming)"},
        "prep": prep_meta, "named_features_exposed": named,
        "extension_features_exposed": ext, "dropped_features": sorted(set(drop)),
        "monotonic_cst_default_convention": mono_default_A,
        "band_params": {"epsilon": EPSILON, "depths": list(DEPTHS),
                        "leaf_mins": list(LEAF_MINS), "seed": 0,
                        "holdout_frac": HOLDOUT_FRAC,
                        "plurality_rho_max": PLURALITY_RHO_MAX,
                        "max_subset_size": args.max_subset_size,
                        "dedup": "used-feature-set (highest-holdout-AUC representative)",
                        "candidate_set": "named-policy features UNION extension features (orig_interest_rate excluded -- defines the rate stratum)"},
        "explainer_params": {"max_depth": 3, "min_samples_leaf": 50,
                             "cv_folds": 5, "r2_good": 0.30, "dr2_ext_min": 0.15},
        "placebo_params": {"n_random_draws": 5, "seller_servicer_topk": 20,
                           "msa_topk": 40},
        "eps_arm": list(EPS_ARM), "min_cell_loans": args.min_cell_loans,
        "probe": bool(args.probe), "strata": {},
        "parallel_runner": {
            "workers": args.workers,
            "blas_threads_per_worker": int(os.environ.get("OPENBLAS_NUM_THREADS", "?")),
            "load_source": load_source,
        },
    }

    # Single executor reused across strata, since cells in different strata
    # can compete for workers but never conflict (independent cell DataFrames).
    n_cells_estimate = 0
    if "rate" in strata and "s_rate" in df.columns:
        n_cells_estimate += int((df["s_rate"].value_counts() >= args.min_cell_loans).sum())
    if "llpa" in strata and "s_llpa" in df.columns:
        n_cells_estimate += int((df["s_llpa"].value_counts() >= args.min_cell_loans).sum())
    max_workers = args.workers if args.workers else min(32, max(1, n_cells_estimate))
    print(f"[{_now_iso()}] launching ProcessPoolExecutor with max_workers={max_workers} "
          f"(estimated {n_cells_estimate} cells across strata)", flush=True)

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        if "rate" in strata:
            results["strata"]["S_rate"] = run_stratum_parallel(
                df, stratum="S-rate (orig_interest_rate deciles)", cell_col="s_rate",
                named=named, ext=ext, mono_default_A=mono_default_A,
                max_subset_size=args.max_subset_size,
                min_cell_loans=args.min_cell_loans,
                do_placebo=do_placebo, do_eps_arm=do_eps_arm, probe=args.probe,
                executor=executor, only_cell=args.only_cell)
        if "llpa" in strata and not args.probe and args.only_cell is None:
            results["strata"]["S_llpa"] = run_stratum_parallel(
                df, stratum="S-llpa (FICO x LTV grid cells)", cell_col="s_llpa",
                named=named, ext=ext, mono_default_A=mono_default_A,
                max_subset_size=args.max_subset_size,
                min_cell_loans=args.min_cell_loans,
                do_placebo=do_placebo, do_eps_arm=False, probe=False,
                executor=executor)

    results["total_seconds"] = round(time.time() - t_start, 1)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    if args.probe:
        suffix = "-probe" + args.output_suffix
    elif args.only_cell is not None:
        suffix = f"-{args.only_cell}-ms{args.max_subset_size}{args.output_suffix}"
    else:
        suffix = args.output_suffix
    out_path = args.output_dir / f"fm_rich_policy_vocab_adequacy_{args.vintage}{suffix}.json"
    out_path.write_text(json.dumps(results, indent=2, default=str))
    print(f"\n[{_now_iso()}] wrote {out_path} ({results['total_seconds']}s total)",
          flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
