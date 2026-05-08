"""
Within-T-bin comparison of k=5 (all-atypical) vs k=0 (no-atypical) default rates.

If the k=5 defaults-LESS effect persists when conditioned on T (mean predicted-
grant probability across R(epsilon) members), the consensus-atypicality signal
carries information beyond what the trees' own predicted-grant probability
captures — methodology survives.

If the effect collapses inside T bins, the headline "all-atypical defaults less"
reduces to "all-atypical cases have higher T" and the structural-special claim
weakens.

Reports per vintage, then pooled.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

RUNS = [
    ("2014Q3", "runs/2026-05-08T17-43-21Z.jsonl"),
    ("2015Q3", "runs/2026-05-08T16-26-41Z.jsonl"),
    ("2015Q4", "runs/2026-05-08T17-44-39Z.jsonl"),
]

N_T_BINS = 5  # quintiles


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


def load(path: Path) -> list[dict]:
    out = []
    for line in path.open():
        rec = json.loads(line)
        if rec.get("origin") != "real":
            continue
        out.append(
            {
                "T": mean_T(rec["per_model"]),
                "k": atypical_count(rec["per_model"]),
                "label": int(rec["label"]),
            }
        )
    return out


def quintile_edges(values: list[float], n_bins: int) -> list[float]:
    s = sorted(values)
    edges = []
    for i in range(1, n_bins):
        idx = int(len(s) * i / n_bins)
        edges.append(s[idx])
    return edges


def assign_bin(t: float, edges: list[float]) -> int:
    for i, e in enumerate(edges):
        if t < e:
            return i
    return len(edges)


def fmt_pct(x: float) -> str:
    return f"{x*100:5.2f}%"


def report(label: str, cases: list[dict]) -> None:
    Ts = [c["T"] for c in cases]
    edges = quintile_edges(Ts, N_T_BINS)
    bins = [[] for _ in range(N_T_BINS)]
    for c in cases:
        bins[assign_bin(c["T"], edges)].append(c)

    print(f"=== {label} | n={len(cases)} | T quintile edges: {[round(e,3) for e in edges]} ===")
    print(f"  bin |   T range   |        k=0 (n / def / rate)        |       k=5 (n / def / rate)        |  k5 - k0")
    for i, b in enumerate(bins):
        if i == 0:
            t_lo = min(Ts)
            t_hi = edges[0]
        elif i == N_T_BINS - 1:
            t_lo = edges[-1]
            t_hi = max(Ts)
        else:
            t_lo = edges[i - 1]
            t_hi = edges[i]
        k0 = [c for c in b if c["k"] == 0]
        k5 = [c for c in b if c["k"] == 5]
        n0 = len(k0)
        d0 = sum(c["label"] for c in k0)
        r0 = d0 / n0 if n0 else 0.0
        n5 = len(k5)
        d5 = sum(c["label"] for c in k5)
        r5 = d5 / n5 if n5 else 0.0
        diff = r5 - r0 if (n0 and n5) else float("nan")
        diff_str = f"{diff*100:+6.2f}pp" if not math.isnan(diff) else "   n/a"
        lo, hi = wilson_ci(d5, n5)
        print(f"  {i+1:>2}  | [{t_lo:.3f},{t_hi:.3f}] | {n0:>5d} / {d0:>4d} / {fmt_pct(r0)}            | {n5:>4d} / {d5:>3d} / {fmt_pct(r5)} [{fmt_pct(lo)},{fmt_pct(hi)}] | {diff_str}")
    print()


def main() -> None:
    repo = Path(__file__).resolve().parent.parent
    pooled = []
    for vintage, rel in RUNS:
        cases = load(repo / rel)
        report(vintage, cases)
        pooled.extend(cases)
    report("POOLED (3 vintages)", pooled)


if __name__ == "__main__":
    main()
