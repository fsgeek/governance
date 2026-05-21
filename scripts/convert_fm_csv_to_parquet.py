"""Convert Fannie Mae loan-performance CSV vintages to raw Parquet.

This is step (1) of the two-layer Parquet plan: a byte-equivalent storage
substitution. Schema and NA handling match
``wedge.collectors.fanniemae.read_raw`` exactly — same column names (c0..c112),
same dtype=str, same na_values=[""], same column-count validation. A loader
that reads Parquet through the same contract gets the same DataFrame.

Step (2) (collapsed/prepped cache on top of this) is a separate script.

Reads are chunked so we don't OOM on the larger vintages (2020Q2 is 18 GB
CSV). Writes go through pyarrow.ParquetWriter so each chunk is appended to
the same .parquet file without re-buffering.

Usage:
    PYTHONPATH=. python scripts/convert_fm_csv_to_parquet.py \\
        --vintages 2008Q1,2009Q1,2012Q1,2014Q3,2016Q1,2018Q1,2020Q2 \\
        --workers 3
"""
from __future__ import annotations

import argparse
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

# Make the wedge package importable.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from wedge.collectors.fanniemae import EXPECTED_NUM_COLUMNS

CSV_DIR = Path("data/fanniemae")
PARQUET_DIR = Path("data/fanniemae/parquet")
CHUNK_ROWS = 1_000_000


def _validate_column_count(csv_path: Path) -> None:
    """Mirror read_raw's first-line column-count validation."""
    with open(csv_path, "r") as fh:
        first_line = ""
        for line in fh:
            if line.strip():
                first_line = line.rstrip("\n").rstrip("\r")
                break
    actual = first_line.count("|") + 1 if first_line else 0
    if actual != EXPECTED_NUM_COLUMNS:
        raise ValueError(
            f"Expected {EXPECTED_NUM_COLUMNS} pipe-delimited columns; "
            f"got {actual} in {csv_path}. Schema mismatch."
        )


def convert_one(csv_path: Path, parquet_path: Path, *, chunk_rows: int) -> dict:
    """Convert one CSV → Parquet. Returns timing/size stats."""
    _validate_column_count(csv_path)
    col_names = [f"c{i}" for i in range(EXPECTED_NUM_COLUMNS)]

    t0 = time.time()
    csv_bytes = csv_path.stat().st_size

    parquet_path.parent.mkdir(parents=True, exist_ok=True)
    # Write to a .tmp first so a crash doesn't leave a half-written file the
    # next run mistakes for complete.
    tmp_path = parquet_path.with_suffix(parquet_path.suffix + ".tmp")
    if tmp_path.exists():
        tmp_path.unlink()

    iter_chunks = pd.read_csv(
        csv_path, sep="|", header=None, names=col_names,
        dtype=str, chunksize=chunk_rows, low_memory=False,
        keep_default_na=False, na_values=[""],
    )
    writer = None
    rows_total = 0
    for chunk in iter_chunks:
        table = pa.Table.from_pandas(chunk, preserve_index=False)
        if writer is None:
            writer = pq.ParquetWriter(tmp_path, table.schema, compression="snappy")
        writer.write_table(table)
        rows_total += len(chunk)
    if writer is not None:
        writer.close()

    tmp_path.replace(parquet_path)
    parquet_bytes = parquet_path.stat().st_size
    elapsed = time.time() - t0

    return {
        "vintage_csv": str(csv_path), "parquet": str(parquet_path),
        "rows": rows_total, "csv_bytes": csv_bytes, "parquet_bytes": parquet_bytes,
        "compression_ratio": round(csv_bytes / parquet_bytes, 2) if parquet_bytes else None,
        "elapsed_s": round(elapsed, 1),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--vintages",
                    default="2008Q1,2009Q1,2012Q1,2014Q3,2016Q1,2018Q1,2020Q2",
                    help="comma-separated YYYYQN list")
    ap.add_argument("--csv-dir", type=Path, default=CSV_DIR)
    ap.add_argument("--parquet-dir", type=Path, default=PARQUET_DIR)
    ap.add_argument("--chunk-rows", type=int, default=CHUNK_ROWS)
    ap.add_argument("--workers", type=int, default=3,
                    help="how many vintages to convert in parallel "
                         "(disk-I/O-bound; 2-4 is a reasonable default)")
    ap.add_argument("--force", action="store_true",
                    help="re-convert even if Parquet output already exists")
    args = ap.parse_args()

    vintages = [v.strip() for v in args.vintages.split(",") if v.strip()]

    work = []
    for v in vintages:
        csv_path = args.csv_dir / f"{v}.csv"
        if not csv_path.exists():
            print(f"SKIP {v}: {csv_path} not found", flush=True)
            continue
        parquet_path = args.parquet_dir / f"{v}.parquet"
        if parquet_path.exists() and not args.force:
            print(f"SKIP {v}: {parquet_path} already exists "
                  f"({parquet_path.stat().st_size / 1e9:.2f} GB)", flush=True)
            continue
        work.append((csv_path, parquet_path))

    if not work:
        print("nothing to do.")
        return 0

    print(f"converting {len(work)} vintage(s) with workers={args.workers}:")
    for c, p in work:
        print(f"  {c.name} -> {p}")
    print()

    t_all = time.time()
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futures = {ex.submit(convert_one, c, p, chunk_rows=args.chunk_rows): c
                   for c, p in work}
        for fut in as_completed(futures):
            csv_path = futures[fut]
            try:
                stats = fut.result()
                print(f"OK  {csv_path.name}: {stats['rows']:,} rows, "
                      f"CSV {stats['csv_bytes']/1e9:.2f} GB -> "
                      f"Parquet {stats['parquet_bytes']/1e9:.2f} GB "
                      f"(ratio {stats['compression_ratio']}x) "
                      f"in {stats['elapsed_s']:.0f}s", flush=True)
            except Exception as e:
                print(f"FAIL {csv_path.name}: {e!r}", flush=True)
    print(f"\nall done in {time.time() - t_all:.0f}s wall")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
