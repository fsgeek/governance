"""
Gradient analysis on the all-atypical tail.

For each vintage run:
  - bucket cases by k = number of R(epsilon) members flagging local_density direction='atypical'
  - report n, default rate, Wilson 95% CI, mean T, median T per bucket
  - real-only (synthetic excluded)

Output is a single table per vintage, no plots.
"""

from __future__ import annotations

import json
import math
import statistics
import sys
from pathlib import Path

RUNS = [
    ("2014Q3", "runs/2026-05-08T17-43-21Z.jsonl"),
    ("2015Q3", "runs/2026-05-08T16-26-41Z.jsonl"),
    ("2015Q4", "runs/2026-05-08T17-44-39Z.jsonl"),
]


def wilson_ci(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = (z / denom) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (center - half, center + half)


def atypical_count(per_model: list[dict]) -> int:
    c = 0
    for m in per_model:
        for ind in m.get("indeterminacy", []):
            if ind.get("species") == "local_density" and ind.get("direction") == "atypical":
                c += 1
                break
    return c


def mean_T(per_model: list[dict]) -> float:
    ts = [m["T"] for m in per_model if "T" in m]
    return sum(ts) / len(ts) if ts else float("nan")


def analyze(jsonl_path: Path) -> dict:
    buckets: dict[int, dict] = {}
    n_total = 0
    n_real = 0
    for line in jsonl_path.open():
        rec = json.loads(line)
        n_total += 1
        if rec.get("origin") != "real":
            continue
        n_real += 1
        n_members = len(rec["per_model"])
        k = atypical_count(rec["per_model"])
        b = buckets.setdefault(k, {"n": 0, "defaults": 0, "T": []})
        b["n"] += 1
        b["defaults"] += int(rec["label"])
        b["T"].append(mean_T(rec["per_model"]))
    return {"total": n_total, "real": n_real, "n_members": n_members, "buckets": buckets}


def fmt_pct(x: float) -> str:
    return f"{x*100:5.2f}%"


def main() -> None:
    repo = Path(__file__).resolve().parent.parent
    print()
    for vintage, rel in RUNS:
        path = repo / rel
        result = analyze(path)
        n_real = result["real"]
        n_members = result["n_members"]
        buckets = result["buckets"]

        all_defaults = sum(b["defaults"] for b in buckets.values())
        baseline_rate = all_defaults / n_real if n_real else 0.0
        all_T = [t for b in buckets.values() for t in b["T"]]
        baseline_T_mean = statistics.mean(all_T) if all_T else float("nan")
        baseline_T_median = statistics.median(all_T) if all_T else float("nan")

        print(f"=== {vintage} | real n={n_real:>6d} | members={n_members} | baseline default={fmt_pct(baseline_rate)} | baseline T mean={baseline_T_mean:.3f} median={baseline_T_median:.3f} ===")
        print(f"  k  |     n |  defaults  |  rate  |    Wilson 95%    |  T mean | T median |  share")
        for k in range(n_members + 1):
            b = buckets.get(k)
            if not b or b["n"] == 0:
                continue
            n = b["n"]
            d = b["defaults"]
            rate = d / n
            lo, hi = wilson_ci(d, n)
            tmean = statistics.mean(b["T"]) if b["T"] else float("nan")
            tmed = statistics.median(b["T"]) if b["T"] else float("nan")
            share = n / n_real
            print(f"  {k}  | {n:>5d} | {d:>5d} ({fmt_pct(rate)}) | {fmt_pct(rate)} | [{fmt_pct(lo)}, {fmt_pct(hi)}] |  {tmean:5.3f} |   {tmed:5.3f}  | {fmt_pct(share)}")
        print()


if __name__ == "__main__":
    main()
