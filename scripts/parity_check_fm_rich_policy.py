"""Compare two fm_rich_policy_vocab_adequacy_{vintage}.json outputs cell-by-cell.

Use case: validate that the parallel runner (test_parallel.py) produces output
indistinguishable from the serial runner (test.py). Math should be byte-
identical given fixed seeds; the rounding the scripts apply before JSON-
encoding (round(x, 4) etc.) means equality is what we expect, but we allow
a tiny FP tolerance for robustness.

Volatile fields are excluded from comparison (timestamps, wall-clock seconds,
the parallel_runner block that only exists in the new output).

Usage:
    python scripts/parity_check_fm_rich_policy.py \\
        runs/fm_rich_policy_vocab_adequacy_2008Q1.json \\
        runs/fm_rich_policy_vocab_adequacy_2008Q1-parallel.json

Exit code: 0 if parity holds, 1 otherwise.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

# Field paths to skip during comparison. Patterns match against the
# dot/index-joined key path (e.g. "strata.S_rate.cells.rb00.seconds").
# Wildcards are not used — explicit prefix-match.
SKIP_PREFIXES = (
    "run_at",
    "total_seconds",
    "parallel_runner",
)
# Per-cell volatile fields (relative to cells.{cell_id}).
SKIP_PER_CELL = ("seconds",)

DEFAULT_TOL = 1e-9


def is_float(x):
    return isinstance(x, float) and not isinstance(x, bool)


def _should_skip(path: str) -> bool:
    for prefix in SKIP_PREFIXES:
        if path == prefix or path.startswith(prefix + ".") or path.startswith(prefix + "["):
            return True
    # Per-cell seconds: ...cells.{cell_id}.seconds
    for f in SKIP_PER_CELL:
        if path.endswith("." + f):
            return True
    return False


def compare(a, b, path: str, tol: float, diffs: list, warnings: list):
    """Recursive structural compare. Records diffs by path."""
    if _should_skip(path):
        return
    # Type mismatch (allowing int <-> float coercion).
    if type(a) is not type(b):
        if is_float(a) and isinstance(b, int) or is_float(b) and isinstance(a, int):
            a, b = float(a), float(b)
        else:
            diffs.append((path, f"type mismatch: {type(a).__name__} vs {type(b).__name__}",
                          repr(a)[:80], repr(b)[:80]))
            return
    if isinstance(a, dict):
        keys_a, keys_b = set(a.keys()), set(b.keys())
        for k in keys_a - keys_b:
            sub = f"{path}.{k}" if path else k
            if not _should_skip(sub):
                diffs.append((sub, "missing in B", repr(a[k])[:80], "<missing>"))
        for k in keys_b - keys_a:
            sub = f"{path}.{k}" if path else k
            if not _should_skip(sub):
                diffs.append((sub, "missing in A", "<missing>", repr(b[k])[:80]))
        for k in keys_a & keys_b:
            sub = f"{path}.{k}" if path else k
            compare(a[k], b[k], sub, tol, diffs, warnings)
    elif isinstance(a, list):
        if len(a) != len(b):
            diffs.append((path, f"list length {len(a)} vs {len(b)}",
                          repr(a)[:80], repr(b)[:80]))
            return
        for i, (x, y) in enumerate(zip(a, b)):
            compare(x, y, f"{path}[{i}]", tol, diffs, warnings)
    elif is_float(a):
        if math.isnan(a) and math.isnan(b):
            return
        if math.isinf(a) and math.isinf(b) and (a > 0) == (b > 0):
            return
        if abs(a - b) > tol:
            diffs.append((path, f"float diff > tol ({tol:g})", a, b))
        elif a != b:
            warnings.append((path, "float within tol but not equal", a, b))
    else:
        if a != b:
            diffs.append((path, "value mismatch", repr(a)[:120], repr(b)[:120]))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("ref", type=Path, help="reference (serial) JSON")
    ap.add_argument("new", type=Path, help="new (parallel) JSON")
    ap.add_argument("--tol", type=float, default=DEFAULT_TOL,
                    help=f"absolute float tolerance (default {DEFAULT_TOL:g})")
    ap.add_argument("--quiet", action="store_true",
                    help="suppress within-tolerance warnings")
    ap.add_argument("--max-diffs", type=int, default=50,
                    help="cap on diffs printed (still counts all)")
    args = ap.parse_args()

    a = json.loads(args.ref.read_text())
    b = json.loads(args.new.read_text())

    diffs, warnings = [], []
    compare(a, b, "", args.tol, diffs, warnings)

    print(f"REF: {args.ref}")
    print(f"NEW: {args.new}")
    print(f"tolerance: {args.tol:g}")
    print()

    if warnings and not args.quiet:
        print(f"=== {len(warnings)} within-tolerance differences ===")
        for path, reason, x, y in warnings[:args.max_diffs]:
            print(f"  {path}: {reason}: {x!r} vs {y!r}")
        if len(warnings) > args.max_diffs:
            print(f"  ... and {len(warnings) - args.max_diffs} more")
        print()

    if diffs:
        print(f"=== {len(diffs)} DIVERGENCES ===")
        for path, reason, x, y in diffs[:args.max_diffs]:
            print(f"  {path}: {reason}")
            print(f"    REF: {x!r}")
            print(f"    NEW: {y!r}")
        if len(diffs) > args.max_diffs:
            print(f"  ... and {len(diffs) - args.max_diffs} more")
        print()
        print(f"PARITY FAIL: {len(diffs)} divergence(s)")
        return 1

    print(f"PARITY OK ({len(warnings)} within-tol FP diffs, 0 divergences)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
