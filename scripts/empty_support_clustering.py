"""Empty-support clustering: are silent-attribution cases concentrated or scattered?

For each run, for each case we count how many of its N member models produce
an empty factor_support_T (and separately _F). The distribution of that count
across cases tells us whether silence is a property of *cases* (clustered:
some cases are unsayable, most are sayable by everyone) or of *members*
(scattered: each member has idiosyncratic blind spots).
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

# Vintage labels corrected 2026-05-09 against run metadata. Earlier
# version had 2014Q3 and 2015Q3 swapped; canonical truth is the meta.json
# adjacent to each jsonl, which is written by wedge/run.py at run time.
RUNS = {
    "2014Q3": "runs/2026-05-08T17-43-21Z.jsonl",
    "2015Q3": "runs/2026-05-08T00-00-09Z.jsonl",
    "2015Q4": "runs/2026-05-08T17-44-39Z.jsonl",
}


def analyze(path: Path) -> dict:
    n_members = None
    silent_t_counts: list[int] = []
    silent_f_counts: list[int] = []
    n_cases = 0
    for line in path.open():
        rec = json.loads(line)
        members = rec["per_model"]
        if n_members is None:
            n_members = len(members)
        n_cases += 1
        st = sum(1 for m in members if not m["factor_support_T"])
        sf = sum(1 for m in members if not m["factor_support_F"])
        silent_t_counts.append(st)
        silent_f_counts.append(sf)
    return {
        "n_cases": n_cases,
        "n_members": n_members,
        "t_dist": Counter(silent_t_counts),
        "f_dist": Counter(silent_f_counts),
    }


def fmt_dist(dist: Counter, n_members: int, n_cases: int) -> str:
    parts = []
    for k in range(n_members + 1):
        c = dist.get(k, 0)
        if c == 0:
            continue
        parts.append(f"  {k}/{n_members}: {c} cases ({100*c/n_cases:.2f}%)")
    return "\n".join(parts)


def main() -> None:
    for label, p in RUNS.items():
        r = analyze(Path(p))
        print(f"=== {label}  (N={r['n_cases']} cases, M={r['n_members']} members) ===")
        print("T-side (grant-supporting) silence distribution:")
        print(fmt_dist(r["t_dist"], r["n_members"], r["n_cases"]))
        any_silent_t = sum(c for k, c in r["t_dist"].items() if k > 0)
        all_silent_t = r["t_dist"].get(r["n_members"], 0)
        print(f"  any-member silent: {any_silent_t} ({100*any_silent_t/r['n_cases']:.2f}%)")
        print(f"  all-members silent: {all_silent_t} ({100*all_silent_t/r['n_cases']:.2f}%)")
        print("F-side (deny-supporting) silence distribution:")
        print(fmt_dist(r["f_dist"], r["n_members"], r["n_cases"]))
        any_silent_f = sum(c for k, c in r["f_dist"].items() if k > 0)
        all_silent_f = r["f_dist"].get(r["n_members"], 0)
        print(f"  any-member silent: {any_silent_f} ({100*any_silent_f/r['n_cases']:.2f}%)")
        print(f"  all-members silent: {all_silent_f} ({100*all_silent_f/r['n_cases']:.2f}%)")
        print()


if __name__ == "__main__":
    main()
