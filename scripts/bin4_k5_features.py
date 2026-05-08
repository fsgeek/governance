"""
What kind of borrower is the bin-4 k=5 case?

For each vintage, restrict to T-bin 4 (the bin where the k=5 effect concentrates),
then compare feature distributions for k=5 vs k=0. If the unusual-but-strong story
holds, k=5 cases should be identifiable as a kind of person — not just statistically
different in default rate.
"""

from __future__ import annotations

import json
import math
import statistics
from pathlib import Path

RUNS = [
    ("2014Q3", "runs/2026-05-08T17-43-21Z.jsonl"),
    ("2015Q3", "runs/2026-05-08T16-26-41Z.jsonl"),
    ("2015Q4", "runs/2026-05-08T17-44-39Z.jsonl"),
]

FEATURES = ["fico_range_low", "dti", "annual_inc", "emp_length"]
N_T_BINS = 5


def is_atypical(model_record: dict) -> bool:
    for ind in model_record.get("indeterminacy", []):
        if ind.get("species") == "local_density" and ind.get("direction") == "atypical":
            return True
    return False


def load(path: Path) -> list[dict]:
    out = []
    for line in path.open():
        rec = json.loads(line)
        if rec.get("origin") != "real":
            continue
        Ts = [m["T"] for m in rec["per_model"]]
        out.append(
            {
                "T": sum(Ts) / len(Ts),
                "k": sum(1 for m in rec["per_model"] if is_atypical(m)),
                "label": int(rec["label"]),
                "features": rec["features"],
            }
        )
    return out


def quintile_edges(values: list[float], n: int) -> list[float]:
    s = sorted(values)
    return [s[int(len(s) * i / n)] for i in range(1, n)]


def assign_bin(t: float, edges: list[float]) -> int:
    for i, e in enumerate(edges):
        if t < e:
            return i
    return len(edges)


def summary(values: list[float]) -> str:
    vs = [v for v in values if v is not None and not (isinstance(v, float) and math.isnan(v))]
    if not vs:
        return "        n=0"
    n = len(vs)
    med = statistics.median(vs)
    p25 = statistics.quantiles(vs, n=4)[0] if n >= 4 else med
    p75 = statistics.quantiles(vs, n=4)[2] if n >= 4 else med
    mean = statistics.mean(vs)
    return f"n={n:>4} median={med:>9.2f} p25={p25:>9.2f} p75={p75:>9.2f} mean={mean:>9.2f}"


def main() -> None:
    repo = Path(__file__).resolve().parent.parent
    print()
    for vintage, rel in RUNS:
        cases = load(repo / rel)
        edges = quintile_edges([c["T"] for c in cases], N_T_BINS)
        for which_bin, label in [(0, "bin-1 (low T, k=5 didn't help)"), (3, "bin-4 (where the effect concentrates)")]:
            bucket = [c for c in cases if assign_bin(c["T"], edges) == which_bin]
            k5 = [c for c in bucket if c["k"] == 5]
            k0 = [c for c in bucket if c["k"] == 0]
            t_lo = min(c["T"] for c in bucket)
            t_hi = max(c["T"] for c in bucket)
            print(f"=== {vintage} | {label} | T [{t_lo:.3f}, {t_hi:.3f}] | k=5 n={len(k5)} | k=0 n={len(k0)} ===")
            for feat in FEATURES:
                k5_vals = [c["features"].get(feat) for c in k5]
                k0_vals = [c["features"].get(feat) for c in k0]
                k5_n_null = sum(1 for v in k5_vals if v is None)
                k0_n_null = sum(1 for v in k0_vals if v is None)
                print(f"  {feat:>16}")
                print(f"    k=5 (atypical): {summary(k5_vals)}  null={k5_n_null}")
                print(f"    k=0 (ordinary): {summary(k0_vals)}  null={k0_n_null}")
            print()


if __name__ == "__main__":
    main()
