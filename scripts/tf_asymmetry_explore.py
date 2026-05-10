"""Exploratory analysis of the T/F asymmetry surfaced by the V1->V2
predictive test (2026-05-09 findings note).

The pre-registration assumed grant-supporting (factor_support_T) and
deny-supporting (factor_support_F) factor weights would shift symmetrically
under each anchoring claim. They did not. T-side held 4/5 directional
predictions; F-side failed 4/5.

This script tests cheap candidate explanations against the data on disk.

Status: post-hoc exploratory. Findings here are NOT promoted to predictions
of the methodology. They are observations about why the pre-registered
predictions split T vs F.
"""

from __future__ import annotations

import json
import statistics
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

V1 = Path("/home/tony/projects/governance/runs/2026-05-08T17-43-21Z.jsonl")
V2 = Path("/home/tony/projects/governance/runs/2026-05-08T17-44-39Z.jsonl")
V2_ALT = Path("/home/tony/projects/governance/runs/2026-05-08T16-26-41Z.jsonl")

FEATURES = ("fico_range_low", "dti", "annual_inc", "emp_length")


def load(p: Path) -> list[dict]:
    return [json.loads(line) for line in p.read_text().splitlines() if line.strip()]


def label_distribution(cases: list[dict]) -> dict:
    """How many paid (label=0) vs charged_off (label=1)?

    Restricted to real-origin cases only — synthetic cases have no real
    label outcome."""
    real = [c for c in cases if c.get("origin") == "real" and c.get("label") is not None]
    counts = Counter(c["label"] for c in real)
    return {
        "n_real": len(real),
        "n_paid": counts.get(0, 0),
        "n_charged_off": counts.get(1, 0),
        "charged_off_rate": counts.get(1, 0) / len(real) if real else 0.0,
    }


def per_member_tf_concentration(cases: list[dict]) -> dict:
    """For each model, distribution of T values (lower = leaning F)."""
    by_model: dict[str, list[float]] = defaultdict(list)
    for c in cases:
        for m in c["per_model"]:
            by_model[m["model_id"]].append(m["T"])
    out = {}
    for mid, ts in sorted(by_model.items()):
        ts_sorted = sorted(ts)
        out[mid] = {
            "n": len(ts),
            "mean_T": statistics.mean(ts),
            "median_T": statistics.median(ts),
            "p10_T": ts_sorted[len(ts) // 10] if ts else 0,
            "p90_T": ts_sorted[len(ts) * 9 // 10] if ts else 0,
            "frac_T_lt_0.5": sum(1 for t in ts if t < 0.5) / len(ts) if ts else 0,
        }
    return out


def factor_support_emptiness(cases: list[dict]) -> dict:
    """How often is factor_support_T or factor_support_F empty?

    An empty support list is a model saying "no feature contributed to
    explaining this side of the prediction." If F-supports are
    systematically more empty in V2, that's a structural reason F-side
    weights shift erratically — there's less signal to begin with.
    """
    n_total = 0
    n_empty_T = 0
    n_empty_F = 0
    for c in cases:
        for m in c["per_model"]:
            n_total += 1
            if not m["factor_support_T"]:
                n_empty_T += 1
            if not m["factor_support_F"]:
                n_empty_F += 1
    return {
        "n_total": n_total,
        "frac_empty_T": n_empty_T / n_total if n_total else 0,
        "frac_empty_F": n_empty_F / n_total if n_total else 0,
    }


def support_size(cases: list[dict]) -> dict:
    """Mean size of factor_support_T and factor_support_F lists."""
    sizes_T: list[int] = []
    sizes_F: list[int] = []
    for c in cases:
        for m in c["per_model"]:
            sizes_T.append(len(m["factor_support_T"]))
            sizes_F.append(len(m["factor_support_F"]))
    return {
        "mean_size_T": statistics.mean(sizes_T) if sizes_T else 0,
        "mean_size_F": statistics.mean(sizes_F) if sizes_F else 0,
        "median_size_T": statistics.median(sizes_T) if sizes_T else 0,
        "median_size_F": statistics.median(sizes_F) if sizes_F else 0,
    }


def feature_appearance_rate(cases: list[dict], side: str) -> dict[str, float]:
    """For each feature, fraction of (case, member) pairs where feature
    appears in the named factor support list (regardless of weight)."""
    counts: dict[str, int] = defaultdict(int)
    n = 0
    for c in cases:
        for m in c["per_model"]:
            n += 1
            for entry in m[side]:
                counts[entry["feature"]] += 1
    return {f: counts[f] / n for f in FEATURES}


def per_feature_weight_when_present(cases: list[dict], side: str) -> dict[str, float]:
    """Mean weight of each feature *conditional on it being present* in
    the factor support. Disentangles 'feature appears more often' from
    'feature carries more weight when it does appear'."""
    sums: dict[str, float] = defaultdict(float)
    counts: dict[str, int] = defaultdict(int)
    for c in cases:
        for m in c["per_model"]:
            for entry in m[side]:
                f = entry["feature"]
                sums[f] += entry["weight"]
                counts[f] += 1
    return {f: (sums[f] / counts[f] if counts[f] else 0.0) for f in FEATURES}


def main() -> None:
    runs = [("V1 (2014Q3)", V1), ("V2 (2015Q4)", V2), ("V2_alt (2015Q3)", V2_ALT)]
    data = {name: load(p) for name, p in runs}

    print("# T/F asymmetry exploration\n")

    # H1: Label imbalance
    print("## H1 — Label imbalance shift\n")
    print("If V2 has dramatically fewer charged_offs than V1, F-side")
    print("weights are noisier simply because there's less F-side data.\n")
    print("| run | n_real | n_paid | n_charged_off | CO_rate |")
    print("|---|---|---|---|---|")
    for name, _ in runs:
        d = label_distribution(data[name])
        print(f"| {name} | {d['n_real']} | {d['n_paid']} | {d['n_charged_off']} | {d['charged_off_rate']:.3f} |")
    print()

    # T-distribution
    print("## Per-member T-value distribution\n")
    print("If models are confidently predicting grant on most cases, F-leaves")
    print("are visited rarely — small sample for F-side attribution.\n")
    for name, _ in runs:
        print(f"### {name}\n")
        print("| model | n | mean_T | median_T | p10 | p90 | frac T<0.5 |")
        print("|---|---|---|---|---|---|---|")
        for mid, s in per_member_tf_concentration(data[name]).items():
            print(f"| {mid} | {s['n']} | {s['mean_T']:.3f} | {s['median_T']:.3f} | "
                  f"{s['p10_T']:.3f} | {s['p90_T']:.3f} | {s['frac_T_lt_0.5']:.3f} |")
        print()

    # Empty-support rate
    print("## Factor support emptiness\n")
    print("Fraction of (case, member) pairs where the named support list is empty.\n")
    print("| run | frac empty T | frac empty F |")
    print("|---|---|---|")
    for name, _ in runs:
        e = factor_support_emptiness(data[name])
        print(f"| {name} | {e['frac_empty_T']:.3f} | {e['frac_empty_F']:.3f} |")
    print()

    # Support size
    print("## Factor support list size\n")
    print("| run | mean size T | mean size F | median size T | median size F |")
    print("|---|---|---|---|---|")
    for name, _ in runs:
        s = support_size(data[name])
        print(f"| {name} | {s['mean_size_T']:.2f} | {s['mean_size_F']:.2f} | "
              f"{s['median_size_T']} | {s['median_size_F']} |")
    print()

    # Feature appearance rate
    print("## Feature appearance rate (fraction of case-member pairs where feature is in support)\n")
    print("If a feature appears less often in F support in V2 than V1, that's")
    print("structural — independent of the weight when it does appear.\n")
    for side, label in [("factor_support_T", "T"), ("factor_support_F", "F")]:
        print(f"### {label} side\n")
        print("| feature | V1 | V2_alt(2015Q3) | V2 |")
        print("|---|---|---|---|")
        v1_a = feature_appearance_rate(data["V1 (2014Q3)"], side)
        v2_a = feature_appearance_rate(data["V2 (2015Q4)"], side)
        v2alt_a = feature_appearance_rate(data["V2_alt (2015Q3)"], side)
        for f in FEATURES:
            print(f"| {f} | {v1_a[f]:.3f} | {v2alt_a[f]:.3f} | {v2_a[f]:.3f} |")
        print()

    # Per-feature weight conditional on presence
    print("## Per-feature mean weight *conditional on feature being present in support*\n")
    print("If a feature's weight-when-present differs between V1 and V2, that's")
    print("attribution intensity, not just frequency.\n")
    for side, label in [("factor_support_T", "T"), ("factor_support_F", "F")]:
        print(f"### {label} side\n")
        print("| feature | V1 | V2_alt(2015Q3) | V2 |")
        print("|---|---|---|---|")
        v1_w = per_feature_weight_when_present(data["V1 (2014Q3)"], side)
        v2_w = per_feature_weight_when_present(data["V2 (2015Q4)"], side)
        v2alt_w = per_feature_weight_when_present(data["V2_alt (2015Q3)"], side)
        for f in FEATURES:
            print(f"| {f} | {v1_w[f]:.6f} | {v2alt_w[f]:.6f} | {v2_w[f]:.6f} |")
        print()


if __name__ == "__main__":
    main()
