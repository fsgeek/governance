"""V1 -> V2 predictive test runner.

Implements the comparison protocol from
docs/superpowers/specs/2026-05-09-v1-v2-predictive-test-pre-registration.md §6.

For each prediction P1-P5, computes the comparison statistic against the
pre-committed hit criteria (§5) and classifies as hit / near-hit / miss /
indeterminate. No prediction is reinterpreted post-hoc; if a prediction
misses, that is the result.

V1 = 2014Q3, V2 = 2015Q4. Optional secondary V2_alt = 2015Q3 for trajectory.

Outputs a markdown findings note to stdout.
"""

from __future__ import annotations

import json
import statistics
from collections import defaultdict
from itertools import combinations
from pathlib import Path

V1_PATH = Path("/home/tony/projects/governance/runs/2026-05-08T17-43-21Z.jsonl")
V2_PATH = Path("/home/tony/projects/governance/runs/2026-05-08T17-44-39Z.jsonl")
V2_ALT_PATH = Path("/home/tony/projects/governance/runs/2026-05-08T16-26-41Z.jsonl")

FEATURES = ("fico_range_low", "dti", "annual_inc", "emp_length")


def load(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def mean_factor_support_per_feature(
    cases: list[dict], side: str
) -> dict[str, float]:
    """Mean weight per feature across (case, member) pairs.

    side: "factor_support_T" or "factor_support_F". Members where a feature
    is absent contribute 0 for that feature.
    """
    sums: dict[str, float] = defaultdict(float)
    n = 0
    for case in cases:
        for member in case["per_model"]:
            entries = {e["feature"]: e["weight"] for e in member[side]}
            for feature in FEATURES:
                sums[feature] += entries.get(feature, 0.0)
            n += 1
    return {f: sums[f] / n for f in FEATURES}


def jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def median_pairwise_overlap(cases: list[dict], side: str) -> float:
    """Median (across cases) of mean pairwise Jaccard overlap on feature names."""
    per_case_means: list[float] = []
    for case in cases:
        members = case["per_model"]
        if len(members) < 2:
            continue
        feature_sets = [{e["feature"] for e in m[side]} for m in members]
        pair_overlaps = [jaccard(a, b) for a, b in combinations(feature_sets, 2)]
        if pair_overlaps:
            per_case_means.append(sum(pair_overlaps) / len(pair_overlaps))
    return statistics.median(per_case_means) if per_case_means else 0.0


def classify_directional(v1: float, v2: float, expected_dir: str) -> tuple[str, float]:
    """Classify P1-P3 result.

    expected_dir: "increase" or "decrease"
    Returns (verdict, relative_effect_size_vs_v1_baseline).
    """
    if v1 == 0:
        rel = float("inf") if v2 != v1 else 0.0
    else:
        rel = (v2 - v1) / v1

    observed_dir = "increase" if v2 > v1 else ("decrease" if v2 < v1 else "no_change")

    if observed_dir == "no_change":
        return "indeterminate", rel
    if observed_dir != expected_dir:
        return "miss", rel
    if abs(rel) >= 0.05:
        return "hit", rel
    return "near-hit", rel


def classify_undirected(v1: float, v2: float) -> tuple[str, float]:
    """Classify P4: hit if shift >= 5% in either direction."""
    if v1 == 0:
        rel = float("inf") if v2 != v1 else 0.0
    else:
        rel = (v2 - v1) / v1
    if abs(rel) >= 0.05:
        return "hit", rel
    return "miss", rel


def classify_overlap(o1: float, o2: float) -> tuple[str, float]:
    """Classify P5. Hit: o2 < o1 by >= 0.05 absolute. Near-hit: 0.01-0.05.
    Miss: o2 >= o1.
    """
    delta = o2 - o1  # negative is "lower in V2"
    if delta >= 0:
        return "miss", delta
    if abs(delta) >= 0.05:
        return "hit", delta
    if abs(delta) >= 0.01:
        return "near-hit", delta
    return "near-hit", delta  # delta < 0.01 still counts as near-hit per spec wording


def main() -> None:
    v1_cases = load(V1_PATH)
    v2_cases = load(V2_PATH)
    v2_alt_cases = load(V2_ALT_PATH) if V2_ALT_PATH.exists() else []

    v1_T = mean_factor_support_per_feature(v1_cases, "factor_support_T")
    v2_T = mean_factor_support_per_feature(v2_cases, "factor_support_T")
    v1_F = mean_factor_support_per_feature(v1_cases, "factor_support_F")
    v2_F = mean_factor_support_per_feature(v2_cases, "factor_support_F")

    v1_overlap_T = median_pairwise_overlap(v1_cases, "factor_support_T")
    v2_overlap_T = median_pairwise_overlap(v2_cases, "factor_support_T")
    v1_overlap_F = median_pairwise_overlap(v1_cases, "factor_support_F")
    v2_overlap_F = median_pairwise_overlap(v2_cases, "factor_support_F")

    if v2_alt_cases:
        v2alt_T = mean_factor_support_per_feature(v2_alt_cases, "factor_support_T")
        v2alt_overlap_T = median_pairwise_overlap(v2_alt_cases, "factor_support_T")
    else:
        v2alt_T = None
        v2alt_overlap_T = None

    print("# V1 -> V2 Predictive Test — Results\n")
    print(f"V1 (2014Q3): {len(v1_cases)} cases. V2 (2015Q4): {len(v2_cases)} cases.")
    if v2_alt_cases:
        print(f"V2_alt (2015Q3): {len(v2_alt_cases)} cases.\n")
    else:
        print()

    print("## Mean factor_support_T weight per feature (across all case-member pairs)\n")
    print("| feature | V1 (2014Q3) | V2 (2015Q4) | rel Δ |")
    print("|---|---|---|---|")
    for f in FEATURES:
        rel = (v2_T[f] - v1_T[f]) / v1_T[f] if v1_T[f] else float("nan")
        print(f"| {f} | {v1_T[f]:.6f} | {v2_T[f]:.6f} | {rel:+.2%} |")
    print()

    print("## Mean factor_support_F weight per feature\n")
    print("| feature | V1 | V2 | rel Δ |")
    print("|---|---|---|---|")
    for f in FEATURES:
        rel = (v2_F[f] - v1_F[f]) / v1_F[f] if v1_F[f] else float("nan")
        print(f"| {f} | {v1_F[f]:.6f} | {v2_F[f]:.6f} | {rel:+.2%} |")
    print()

    print("## Median pairwise factor-support overlap across R(ε) members\n")
    print(f"- factor_support_T: V1={v1_overlap_T:.3f}, V2={v2_overlap_T:.3f}, Δ={v2_overlap_T - v1_overlap_T:+.3f}")
    print(f"- factor_support_F: V1={v1_overlap_F:.3f}, V2={v2_overlap_F:.3f}, Δ={v2_overlap_F - v1_overlap_F:+.3f}")
    if v2alt_overlap_T is not None:
        print(f"- factor_support_T V2_alt (2015Q3): {v2alt_overlap_T:.3f}")
    print()

    print("## Prediction classifications\n")

    p1_T = classify_directional(v1_T["annual_inc"], v2_T["annual_inc"], "increase")
    p1_F = classify_directional(v1_F["annual_inc"], v2_F["annual_inc"], "increase")
    print(f"**P1** (annual_inc support increases V1→V2):")
    print(f"  - factor_support_T: **{p1_T[0]}** (rel Δ = {p1_T[1]:+.2%})")
    print(f"  - factor_support_F: **{p1_F[0]}** (rel Δ = {p1_F[1]:+.2%})")
    print()

    p2_T = classify_directional(v1_T["fico_range_low"], v2_T["fico_range_low"], "decrease")
    p2_F = classify_directional(v1_F["fico_range_low"], v2_F["fico_range_low"], "decrease")
    print(f"**P2** (fico_range_low support decreases V1→V2):")
    print(f"  - factor_support_T: **{p2_T[0]}** (rel Δ = {p2_T[1]:+.2%})")
    print(f"  - factor_support_F: **{p2_F[0]}** (rel Δ = {p2_F[1]:+.2%})")
    print()

    p3_T = classify_directional(v1_T["dti"], v2_T["dti"], "decrease")
    p3_F = classify_directional(v1_F["dti"], v2_F["dti"], "decrease")
    print(f"**P3** (dti support decreases V1→V2):")
    print(f"  - factor_support_T: **{p3_T[0]}** (rel Δ = {p3_T[1]:+.2%})")
    print(f"  - factor_support_F: **{p3_F[0]}** (rel Δ = {p3_F[1]:+.2%})")
    print()

    p4_T = classify_undirected(v1_T["emp_length"], v2_T["emp_length"])
    p4_F = classify_undirected(v1_F["emp_length"], v2_F["emp_length"])
    print(f"**P4** (emp_length support shifts V1→V2, direction undirected):")
    print(f"  - factor_support_T: **{p4_T[0]}** (rel Δ = {p4_T[1]:+.2%})")
    print(f"  - factor_support_F: **{p4_F[0]}** (rel Δ = {p4_F[1]:+.2%})")
    print()

    p5_T = classify_overlap(v1_overlap_T, v2_overlap_T)
    p5_F = classify_overlap(v1_overlap_F, v2_overlap_F)
    print(f"**P5** (median pairwise factor-support overlap decreases V1→V2):")
    print(f"  - factor_support_T: **{p5_T[0]}** (Δ = {p5_T[1]:+.3f})")
    print(f"  - factor_support_F: **{p5_F[0]}** (Δ = {p5_F[1]:+.3f})")
    print()


if __name__ == "__main__":
    main()
