"""Characterize cases where ALL members are silent on T or F.

V1 has none. V2 has ~0.6% on each side. What distinguishes those cases?
We compare feature distributions, label rates, and predicted-probability
distributions of all-silent cases vs the rest.
"""
from __future__ import annotations

import json
import statistics as st
from pathlib import Path

RUNS = {
    "V1_2014Q3": "runs/2026-05-08T00-00-09Z.jsonl",
    "V2alt_2015Q3": "runs/2026-05-08T17-43-21Z.jsonl",
    "V2_2015Q4": "runs/2026-05-08T17-44-39Z.jsonl",
}

FEATURES = ["fico_range_low", "dti", "annual_inc", "emp_length"]


def summarize(values: list[float]) -> str:
    vals = [v for v in values if v is not None]
    if not vals:
        return "n=0"
    if len(vals) < 2:
        return f"n={len(vals)} mean={vals[0]:.2f}"
    return (
        f"n={len(vals)} mean={st.mean(vals):.2f} median={st.median(vals):.2f} "
        f"sd={st.pstdev(vals):.2f}"
    )


def analyze(path: Path, label: str) -> None:
    print(f"=== {label} ===")
    cases = [json.loads(line) for line in path.open()]
    M = len(cases[0]["per_model"])

    def silent_all_t(rec):
        return all(not m["factor_support_T"] for m in rec["per_model"])

    def silent_all_f(rec):
        return all(not m["factor_support_F"] for m in rec["per_model"])

    for side, pred in (("T-silent-all", silent_all_t), ("F-silent-all", silent_all_f)):
        sil = [c for c in cases if pred(c)]
        rest = [c for c in cases if not pred(c)]
        print(f"-- {side}: {len(sil)} silent / {len(rest)} rest")
        if not sil:
            print("   (no silent cases — V1 baseline)\n")
            continue
        # label rate
        sil_lab = [c["label"] for c in sil if c["label"] is not None]
        rest_lab = [c["label"] for c in rest if c["label"] is not None]
        sil_y = sum(sil_lab) / len(sil_lab) if sil_lab else float("nan")
        rest_y = sum(rest_lab) / len(rest_lab) if rest_lab else float("nan")
        print(
            f"   charge-off rate:  silent={sil_y:.3f} (n={len(sil_lab)})  "
            f"rest={rest_y:.3f} (n={len(rest_lab)})"
        )
        # mean predicted T over members
        sil_T = [st.mean(m["T"] for m in c["per_model"]) for c in sil]
        rest_T = [st.mean(m["T"] for m in c["per_model"]) for c in rest]
        print(f"   mean predicted T: silent={st.mean(sil_T):.3f}  rest={st.mean(rest_T):.3f}")
        # feature distributions
        for f in FEATURES:
            sv = [c["features"][f] for c in sil if c["features"][f] is not None]
            rv = [c["features"][f] for c in rest if c["features"][f] is not None]
            sil_pct_null = 1 - len(sv) / len(sil)
            rest_pct_null = 1 - len(rv) / len(rest)
            sm = st.mean(sv) if sv else float("nan")
            rm = st.mean(rv) if rv else float("nan")
            print(
                f"   {f:18s} silent mean={sm:.2f} (null {sil_pct_null:.1%})   "
                f"rest mean={rm:.2f} (null {rest_pct_null:.1%})"
            )
        # disagreement among members (variance of T) on silent cases
        sil_var = [st.pvariance([m["T"] for m in c["per_model"]]) for c in sil]
        rest_var = [st.pvariance([m["T"] for m in c["per_model"]]) for c in rest]
        print(
            f"   member T-variance: silent mean={st.mean(sil_var):.4f}  "
            f"rest mean={st.mean(rest_var):.4f}"
        )
        # leaf agreement: are all members landing in the same leaf?
        same_leaf = sum(
            1 for c in sil if len({m["leaf"] for m in c["per_model"]}) == 1
        )
        print(f"   same-leaf-across-members: {same_leaf}/{len(sil)}")
        print()


def main() -> None:
    for lab, p in RUNS.items():
        analyze(Path(p), lab)


if __name__ == "__main__":
    main()
