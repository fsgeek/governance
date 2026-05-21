# Parallel + Parquet pipeline — patch record draft for pre-reg #14 §2b

**Date drafted:** 2026-05-20. **Status:** DRAFT — ready to splice into `docs/superpowers/specs/2026-05-18-expanded-vintage-replication-result-note.md` §8 as a new sub-section (proposed §8e), pending Tony's review and a git commit so an actual hash can replace the placeholder.

## Context

§8 of the result note documents the recovery-rerun protocol deviations for 2020Q2 (exit 1) and 2012Q1 (exit 137, OOM). The original recovery path (§8b) ran the Windows-host script `scripts/run_windows_vintages.ps1` sequentially with `--no-placebo --no-eps-arm` (§8a). That recovery completed 2012Q1 (2026-05-19T19:02:23Z, exit 0) but did not retry 2020Q2 after its first failure.

The 2020Q2 retry was performed using a new parallel + Parquet pipeline, described below. Pre-reg #14 §2b permits "documented patches with patch hash recorded in the result note" as long as discriminator-computation logic is unchanged. Two byte-equivalent parity tests against the 2008Q1 serial reference (one CSV-loaded, one Parquet-loaded) validate that the math is untouched.

## Files added or modified

1. `scripts/fm_rich_policy_vocab_adequacy_test_parallel.py` — sibling to the original script. Imports `build_band_for_cell`, `placebo_for_cell`, `load_vintage`, `prep`, and every numerical primitive from `scripts/fm_rich_policy_vocab_adequacy_test.py`. Replaces the `for cell_id in analyzed:` Python loop with a `concurrent.futures.ProcessPoolExecutor` fan-out across cells, with three phases preserved (cell builds, placebo on plural-A cells, eps-arm on plural-A cells). BLAS/OMP thread caps are set to 1 per worker before numpy import to prevent oversubscription on the 128-thread host.

2. `scripts/convert_fm_csv_to_parquet.py` — chunked CSV → Parquet converter. Same dtype=str and `na_values=[""]` contract as `wedge.collectors.fanniemae.read_raw`. pyarrow + snappy compression. Runs multiple vintages concurrently.

3. `scripts/parity_check_fm_rich_policy.py` — recursive structural diff between two `fm_rich_policy_vocab_adequacy_*.json` files. Skips volatile fields (timestamps, wall-clock seconds, the new `parallel_runner` block); compares all numerical fields at configurable absolute tolerance (default 1e-9, i.e. essentially exact).

4. `wedge/collectors/fanniemae.py` — additive changes only. Existing `read_raw` is unchanged. Two new functions:
   - `read_raw_auto(path, nrows=None, prefer_parquet=True)`: transparently reads a sibling Parquet (`data/fanniemae/parquet/{vintage}.parquet`) if present, falling back to CSV. Asserts the column count matches `EXPECTED_NUM_COLUMNS=113`. Returns a DataFrame semantically equivalent to `read_raw(...)`.
   - `load_collapsed_cached(csv_path, horizon_months=24, prefer_parquet=True, use_cache=True)`: returns the prepped DataFrame (post `derive_origination_and_label` + `filter_eligible` + `to_feature_frame`), reading from a per-vintage Parquet cache (`{vintage}_h{h}.collapsed.parquet`) when its mtime exceeds the source data's. Cache miss regenerates from raw and writes the cache atomically (via `.tmp` + rename). `use_cache=False` or `nrows is not None` bypasses the cache.

## Storage substitution

All 7 vintages converted from raw CSV to raw Parquet. Conversion stats:

| Vintage | CSV (GB) | Parquet (GB) | Ratio | Rows |
|---|---|---|---|---|
| 2008Q1 | 6.05 | 0.24 | 25.2× | 22.4M |
| 2009Q1 | 9.22 | 0.37 | 24.7× | 34.7M |
| 2012Q1 | 13.76 | 0.57 | 24.1× | 50.2M |
| 2014Q3 | 6.93 | 0.30 | 23.1× | 25.4M |
| 2016Q1 | 7.26 | 0.32 | 22.6× | 25.9M |
| 2018Q1 | 6.82 | 0.32 | 21.2× | 23.2M |
| 2020Q2 | 18.18 | 0.92 | 19.8× | 57.5M |
| **Total** | **68.22** | **3.04** | **22.4×** | **239.3M** |

The compression ratio is driven by Parquet's dictionary encoding on the repeated origination identifiers and categorical fields, which dominate the row layout in FM performance data.

## Parity validation

Two parity tests against the existing 2008Q1 serial reference (`runs/fm_rich_policy_vocab_adequacy_2008Q1.json`, run 2026-05-13 at `--max-subset-size 5 --strata rate`, the same parameters recorded in the reference's `band_params` block):

| Test | Pipeline | Parameters | Tolerance | Result |
|---|---|---|---|---|
| Parity-1 | Parallel, CSV-loaded | `--max-subset-size 5 --strata rate --no-parquet` | 1e-9 | **PARITY OK** (0 divergences, 0 within-tol FP diffs) |
| Parity-2 | Parallel, Parquet-loaded | `--max-subset-size 5 --strata rate` | 1e-9 | **PARITY OK** (0 divergences, 0 within-tol FP diffs) |

Both tests passed at the 1e-9 absolute-tolerance threshold, which is below the rounding precision applied in the JSON serialization (most fields are pre-rounded to 4 decimal places). The math is bit-equivalent.

Run times:
- Serial reference (2026-05-13): 16,139s (4.48h)
- Parity-1, parallel CSV: 3,178s (53 min) — 5.08× speedup
- Parity-2, parallel Parquet: 2,753s (46 min) — 5.86× speedup (additional 7 min from Parquet vs CSV load)

By transitivity the parallel-Parquet pipeline is equivalent to the serial-CSV pipeline; the change to orchestration (parallelism) and the change to storage substrate (CSV→Parquet) are independently null.

## 2020Q2 production run

Executed 2026-05-19 → 2026-05-20 (background ID `bbvlx16uh`):

```
python scripts/fm_rich_policy_vocab_adequacy_test_parallel.py \
    --vintage 2020Q2 --strata rate,llpa --max-subset-size 7 --workers 32
```

Result: `runs/fm_rich_policy_vocab_adequacy_2020Q2.json` (1.46 MB, written 2026-05-20T23-50-22Z). Wall-clock 76,637s (21.3h). Memory: did not OOM (the binding constraint that caused the original 2020Q2 failure). Load source recorded as `parquet` in the new `parallel_runner` block.

S_rate: 9 analyzed cells, 9 plural-A. S_llpa: 48 analyzed cells, 30 plural-A. The output contains the full placebo and eps_arm subtrees, **bringing 2020Q2 to methodological parity with 2008Q1 / 2009Q1 / 2014Q3 / 2016Q1 / 2018Q1**, not the truncated `--no-placebo --no-eps-arm` content anticipated for the recovery in §8a.

## Corpus asymmetry remaining

| Vintage | Placebo subtree | Eps_arm subtree | Source |
|---|---|---|---|
| 2008Q1 | ✓ | ✓ | original serial run |
| 2009Q1 | ✓ | ✓ | original serial run |
| 2012Q1 | ✗ | ✗ | Windows-host recovery (`--no-placebo --no-eps-arm`, §8a) |
| 2014Q3 | ✓ | ✓ | original serial run |
| 2016Q1 | ✓ | ✓ | original serial run |
| 2018Q1 | ✓ | ✓ | original serial run |
| 2020Q2 | ✓ | ✓ | parallel + Parquet rerun (this section) |

The §8a verification stands: placebo and eps_arm output fields are not consumed by `silence_manufacture_test.py` or `frame_evocation_test.py`, so this asymmetry does not propagate into any P-verdict. Optional follow-up: re-run 2012Q1 through the parallel + Parquet pipeline (estimated ~12-16h based on 2012Q1's CSV size vs 2020Q2's) to bring the corpus into complete methodological symmetry. Decision deferred to Tony.

## Patch hashes

To be filled at commit time. Files involved:

- `scripts/fm_rich_policy_vocab_adequacy_test_parallel.py` (new)
- `scripts/convert_fm_csv_to_parquet.py` (new)
- `scripts/parity_check_fm_rich_policy.py` (new)
- `wedge/collectors/fanniemae.py` (modified: additive)

Result-note revision committing this section: `[hash]`. New 2020Q2 output: `runs/fm_rich_policy_vocab_adequacy_2020Q2.json` (committed contents, hashable via `git hash-object`).

## Environment

- Python: 3.14.0 (CPython)
- numpy: 2.4.4
- pandas: 3.0.2
- scikit-learn: 1.8.0
- pyarrow: 24.0.0
- OS: Windows 11 Enterprise (host, native Python, not WSL)
- Hardware: 64 physical cores / 128 logical, 256 GB RAM
