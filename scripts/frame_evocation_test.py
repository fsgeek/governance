#!/usr/bin/env python3
"""
Frame-evocation vs subset-membership as adequacy discriminator on the FM #12 corpus.

Pre-reg: docs/superpowers/specs/2026-05-15-frame-evocation-preregistration-note.md
Pre-reg commit: 991a2d9 / OTS f469fcf

Operates on saved #11 and #12 JSONs in runs/. No new compute on raw data; no
model fits. Outputs runs/frame_evocation_2026-05-15.json with per-cell scores,
aggregate AUCs, and permutation p-values.

Three discriminators tested on the n=29 FM band corpus:

  M1 (R²-proximity)        = -|R²_named - 0.30|       per variant; max over variants
  M2 (subset-membership)   = -mandatory_feature_usage_share  per variant; max over variants
  M3 (frame-coherence)     = -max_feat |ρ(d, feature)|       per variant; max over variants
       sensitivity arms:    M3_top2 = -top2_sum |ρ|; M3_entropy = entropy(|ρ| dist)

Higher score = more unreliable. AUC = Mann-Whitney U / (n_pos × n_neg) for
predicting the primary binary label (non-trivial = silence ∪ reorg-agreement
vs trivial = no-reorg).

Permutation p-values: 10,000 label shuffles, two-sided.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import mannwhitneyu

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNS_DIR = REPO_ROOT / "runs"
SILENCE_JSON = RUNS_DIR / "silence_manufacture_2026-05-13.json"
FM11_JSON = {v: RUNS_DIR / f"fm_rich_policy_vocab_adequacy_{v}.json"
             for v in ("2018Q1", "2016Q1", "2008Q1")}
OUTPUT = RUNS_DIR / "frame_evocation_2026-05-15.json"

VARIANT_A_KEY = "variant_A_geography_admissible"
VARIANT_B_KEY = "variant_B_compliant_geography_prohibited"

ADEQUACY_THRESHOLD = 0.30
REGULATED_THREE = frozenset({"fico_range_low", "dti", "ltv"})
N_PERMUTATIONS = 10_000
SEED = 20260515

PRE_REG_COMMIT = "991a2d9"
PRE_REG_OTS = "f469fcf"


# ---- metric primitives -----------------------------------------------------

def m1_proximity(r2_named: float | None) -> float | None:
    if r2_named is None:
        return None
    return -abs(r2_named - ADEQUACY_THRESHOLD)


def m2_mean(usage_share_dict: dict[str, float] | None) -> float | None:
    """Subset-membership (primary): -mean over mandatory features of usage share."""
    if not usage_share_dict:
        return None
    vals = list(usage_share_dict.values())
    if not vals:
        return None
    return -sum(vals) / len(vals)


def m2_min(usage_share_dict: dict[str, float] | None) -> float | None:
    """Subset-membership (sensitivity arm): -min usage share over mandatory features."""
    if not usage_share_dict:
        return None
    vals = list(usage_share_dict.values())
    if not vals:
        return None
    return -min(vals)


def m2_n_zero(usage_share_dict: dict[str, float] | None) -> float | None:
    """Subset-membership (sensitivity arm): count of mandatory features with zero usage.
    Higher count = more unreliable."""
    if not usage_share_dict:
        return None
    return float(sum(1 for v in usage_share_dict.values() if v == 0))


def _extract_rho(ρ_dict: dict[str, dict] | None,
                 keep_features: set[str] | None) -> dict[str, float]:
    """Extract scalar spearman_rho from the per-feature dict, optionally filtering."""
    if not ρ_dict:
        return {}
    out: dict[str, float] = {}
    for feat, val in ρ_dict.items():
        if keep_features is not None and feat not in keep_features:
            continue
        if isinstance(val, dict) and "spearman_rho" in val:
            r = val["spearman_rho"]
            if r is not None:
                out[feat] = float(r)
    return out


def m3_max(ρ_extracted: dict[str, float]) -> float | None:
    if not ρ_extracted:
        return None
    return -max(abs(v) for v in ρ_extracted.values())


def m3_top2_sum(ρ_extracted: dict[str, float]) -> float | None:
    if not ρ_extracted:
        return None
    sorted_abs = sorted((abs(v) for v in ρ_extracted.values()), reverse=True)
    return -sum(sorted_abs[:2])


def m3_entropy(ρ_extracted: dict[str, float]) -> float | None:
    """Entropy of normalized |ρ| distribution. Higher = more diffuse = more unreliable.
    Returns entropy directly (no negation) so that 'higher = unreliable' convention holds."""
    if not ρ_extracted:
        return None
    absvals = list(ρ_extracted.values())
    absvals = [abs(v) for v in absvals]
    total = sum(absvals)
    if total <= 0:
        return None
    probs = [v / total for v in absvals]
    return -sum(p * math.log(p) for p in probs if p > 0)


def max_rho_feature(ρ_extracted: dict[str, float]) -> str | None:
    if not ρ_extracted:
        return None
    return max(ρ_extracted, key=lambda k: abs(ρ_extracted[k]))


# ---- AUC + permutation -----------------------------------------------------

def auc(scores: list[float | None], labels: list[int]) -> float | None:
    """AUC via Mann-Whitney U; labels are 0/1. Returns None if a class is empty
    or all scores are None."""
    paired = [(s, l) for s, l in zip(scores, labels) if s is not None]
    if not paired:
        return None
    pos = [s for s, l in paired if l == 1]
    neg = [s for s, l in paired if l == 0]
    if not pos or not neg:
        return None
    u, _ = mannwhitneyu(pos, neg, alternative="two-sided")
    return float(u / (len(pos) * len(neg)))


def auc_diff_permutation(scores_a: list[float | None],
                         scores_b: list[float | None],
                         labels: list[int],
                         n_perm: int,
                         seed: int) -> dict[str, float]:
    """Two-sided permutation test on AUC(a) - AUC(b). Permutes labels."""
    rng = np.random.default_rng(seed)
    auc_a = auc(scores_a, labels)
    auc_b = auc(scores_b, labels)
    if auc_a is None or auc_b is None:
        return {"auc_a": auc_a, "auc_b": auc_b, "obs_diff": None, "p_two_sided": None}
    obs_diff = auc_a - auc_b
    labels_arr = np.array(labels)
    null_diffs = np.empty(n_perm)
    for i in range(n_perm):
        perm = rng.permutation(labels_arr).tolist()
        a_i = auc(scores_a, perm)
        b_i = auc(scores_b, perm)
        if a_i is None or b_i is None:
            null_diffs[i] = np.nan
        else:
            null_diffs[i] = a_i - b_i
    valid = null_diffs[~np.isnan(null_diffs)]
    p = float((np.abs(valid) >= abs(obs_diff)).mean()) if valid.size else None
    return {
        "auc_a": float(auc_a),
        "auc_b": float(auc_b),
        "obs_diff": float(obs_diff),
        "p_two_sided": p,
        "n_perm_valid": int(valid.size),
    }


# ---- data loading ----------------------------------------------------------

def load_corpus() -> tuple[list[dict], dict[tuple[str, str], dict], set[str]]:
    """Returns (silence_cells, fm11_cells, named_features_set)."""
    silence_data = json.loads(SILENCE_JSON.read_text())
    silence_cells = [c for c in silence_data["cells"] if c.get("in_scope")]
    fm11: dict[tuple[str, str], dict] = {}
    named_features_union: set[str] = set()
    for vintage, path in FM11_JSON.items():
        d = json.loads(path.read_text())
        named_features_union.update(d.get("named_features_exposed", []))
        s_rate = d["strata"]["S_rate"]
        for cell_id, cell in s_rate["cells"].items():
            fm11[(vintage, cell_id)] = cell
    return silence_cells, fm11, named_features_union


def cell_metrics(silence_cell: dict, fm11_variant_a: dict, fm11_variant_b: dict,
                 named_features: set[str]) -> dict:
    """Compute all per-variant + cell-level scores for one cell.
    Cell-level = max over variants ('worst single-variant reading')."""
    def per_variant(va: dict) -> dict:
        r2 = va.get("R2_named")
        usage = (va.get("mandatory_feature_enforcement") or {}).get("mandatory_feature_usage_share")
        ρ_d_raw = va.get("univariate_spearman_d")
        ρ_named = _extract_rho(ρ_d_raw, keep_features=named_features)
        ρ_ext = _extract_rho(ρ_d_raw, keep_features=None)  # all features
        # extension-only: subtract named
        ρ_ext_only = {f: v for f, v in ρ_ext.items() if f not in named_features}
        return {
            "R2_named": r2,
            "M1": m1_proximity(r2),
            "M2_mean": m2_mean(usage),
            "M2_min": m2_min(usage),
            "M2_n_zero": m2_n_zero(usage),
            "M3_max": m3_max(ρ_named),
            "M3_top2": m3_top2_sum(ρ_named),
            "M3_entropy": m3_entropy(ρ_named),
            "M3_max_ext": m3_max(ρ_ext_only),  # bonus: max |ρ| on extension features only
            "max_rho_feature_named": max_rho_feature(ρ_named),
            "max_rho_feature_all": max_rho_feature(ρ_ext),
            "n_named_features_present": len(ρ_named),
            "n_extension_features_present": len(ρ_ext_only),
        }

    va_a = per_variant(fm11_variant_a)
    va_b = per_variant(fm11_variant_b)

    def cell_max(key: str) -> float | None:
        vals = [va_a[key], va_b[key]]
        clean = [v for v in vals if v is not None]
        return max(clean) if clean else None

    return {
        "vintage": silence_cell["vintage"],
        "cell": silence_cell["cell"],
        "label_silence": bool(silence_cell.get("manufactured_silence")),
        "label_reorganized": bool(silence_cell.get("is_reorganized_primary")),
        "label_nontrivial": bool(silence_cell.get("is_reorganized_primary")),
        "verdict_differs": bool(silence_cell.get("verdict_differs")),
        "variant_A": va_a,
        "variant_B": va_b,
        "M1_cell": cell_max("M1"),
        "M2_mean_cell": cell_max("M2_mean"),
        "M2_min_cell": cell_max("M2_min"),
        "M2_n_zero_cell": cell_max("M2_n_zero"),
        "M3_max_cell": cell_max("M3_max"),
        "M3_top2_cell": cell_max("M3_top2"),
        "M3_entropy_cell": cell_max("M3_entropy"),
        "M3_max_ext_cell": cell_max("M3_max_ext"),
    }


# ---- main analysis ---------------------------------------------------------

def main() -> int:
    silence_cells, fm11, named_features = load_corpus()
    print(f"named_features ({len(named_features)}): {sorted(named_features)}")
    per_cell = []
    for sc in silence_cells:
        key = (sc["vintage"], sc["cell"])
        if key not in fm11:
            print(f"warn: ({key}) missing in #11 corpus; skipping", flush=True)
            continue
        cell11 = fm11[key]
        va_a = cell11.get(VARIANT_A_KEY) or {}
        va_b = cell11.get(VARIANT_B_KEY) or {}
        per_cell.append(cell_metrics(sc, va_a, va_b, named_features))

    # primary binary: non-trivial (silence ∪ reorg-agreement) vs trivial (no-reorg)
    labels_primary = [int(c["label_nontrivial"]) for c in per_cell]
    # secondary binary: silence-only vs no-reorg (drops reorg-agreement)
    secondary_mask = [c["label_silence"] or not c["label_reorganized"] for c in per_cell]
    labels_secondary = [int(c["label_silence"]) for c, m in zip(per_cell, secondary_mask) if m]

    n_silence = sum(c["label_silence"] for c in per_cell)
    n_reorg = sum(c["label_reorganized"] for c in per_cell)
    n_nontrivial = sum(labels_primary)
    n_trivial = len(per_cell) - n_nontrivial
    print(f"corpus: n_cells={len(per_cell)} "
          f"silence={n_silence} reorganized={n_reorg} "
          f"nontrivial={n_nontrivial} trivial={n_trivial}")

    metric_names = ["M1_cell", "M2_mean_cell", "M2_min_cell", "M2_n_zero_cell",
                    "M3_max_cell", "M3_top2_cell", "M3_entropy_cell", "M3_max_ext_cell"]
    scores = {m: [c[m] for c in per_cell] for m in metric_names}
    aucs_primary = {m: auc(scores[m], labels_primary) for m in metric_names}
    print("AUCs (primary, non-trivial vs trivial):")
    for m, a in aucs_primary.items():
        print(f"  {m:18s} = {a}" if a is not None else f"  {m:18s} = N/A")

    # P1: M3_max > M2_mean (primary); P2: M3_max > M1
    print(f"\npermutation tests (n_perm={N_PERMUTATIONS}, seed={SEED}, primary labels)...")
    pairs = [
        ("P1_M3max_vs_M2mean", "M3_max_cell", "M2_mean_cell"),
        ("P2_M3max_vs_M1", "M3_max_cell", "M1_cell"),
        ("P1_M3max_vs_M2min", "M3_max_cell", "M2_min_cell"),
        ("P1_M3max_vs_M2nzero", "M3_max_cell", "M2_n_zero_cell"),
        ("P1_M3top2_vs_M2mean", "M3_top2_cell", "M2_mean_cell"),
        ("P1_M3entropy_vs_M2mean", "M3_entropy_cell", "M2_mean_cell"),
        ("P2_M3top2_vs_M1", "M3_top2_cell", "M1_cell"),
        ("P2_M3entropy_vs_M1", "M3_entropy_cell", "M1_cell"),
    ]
    perm_results = {}
    for name, a, b in pairs:
        res = auc_diff_permutation(scores[a], scores[b], labels_primary,
                                   N_PERMUTATIONS, SEED)
        perm_results[name] = res
        print(f"  {name:24s}  obs_diff={res['obs_diff']:+.4f}  p={res['p_two_sided']:.4f}")

    # secondary (silence-only vs trivial)
    secondary_scores = {m: [c[m] for c, k in zip(per_cell, secondary_mask) if k]
                        for m in metric_names}
    aucs_secondary = {m: auc(secondary_scores[m], labels_secondary)
                      for m in metric_names}
    perm_secondary = {}
    for name, a, b in pairs:
        res = auc_diff_permutation(secondary_scores[a], secondary_scores[b],
                                   labels_secondary, N_PERMUTATIONS, SEED + 1)
        perm_secondary[name] = res

    # P3: among silence cells, max_rho_feature_named in BOTH variants ∉ REGULATED_THREE
    p3_cells = []
    for c in per_cell:
        if not c["label_silence"]:
            continue
        f_a = c["variant_A"]["max_rho_feature_named"]
        f_b = c["variant_B"]["max_rho_feature_named"]
        both_off = (f_a is not None and f_a not in REGULATED_THREE and
                    f_b is not None and f_b not in REGULATED_THREE)
        # bonus: extension-feature concentration
        f_a_all = c["variant_A"]["max_rho_feature_all"]
        f_b_all = c["variant_B"]["max_rho_feature_all"]
        p3_cells.append({
            "vintage": c["vintage"], "cell": c["cell"],
            "max_rho_feature_named_A": f_a, "max_rho_feature_named_B": f_b,
            "both_off_regulated_three": both_off,
            "max_rho_feature_all_A": f_a_all, "max_rho_feature_all_B": f_b_all,
        })
    p3_all = bool(p3_cells) and all(c["both_off_regulated_three"] for c in p3_cells)
    print(f"\nP3 silence-cell features:")
    for c in p3_cells:
        print(f"  {c['vintage']} {c['cell']}: named A={c['max_rho_feature_named_A']} "
              f"B={c['max_rho_feature_named_B']}  off-regulated-three={c['both_off_regulated_three']}")
        print(f"    all-features peak: A={c['max_rho_feature_all_A']} B={c['max_rho_feature_all_B']}")
    print(f"P3 verdict (all silence cells both off regulated-three): {p3_all}")

    output = {
        "test": "frame-evocation vs subset-membership vs R²-proximity (#13)",
        "pre_reg_commit": PRE_REG_COMMIT,
        "pre_reg_ots_commit": PRE_REG_OTS,
        "pre_reg_path": "docs/superpowers/specs/2026-05-15-frame-evocation-preregistration-note.md",
        "adequacy_threshold_R2_named": ADEQUACY_THRESHOLD,
        "regulated_three": sorted(REGULATED_THREE),
        "n_permutations": N_PERMUTATIONS,
        "seed": SEED,
        "n_cells_in_scope": len(per_cell),
        "n_silence": n_silence,
        "n_reorganized": n_reorg,
        "n_nontrivial_primary": n_nontrivial,
        "n_trivial_primary": n_trivial,
        "aucs_primary": aucs_primary,
        "aucs_secondary_silence_only": aucs_secondary,
        "permutation_primary": perm_results,
        "permutation_secondary": perm_secondary,
        "P3_silence_cells": p3_cells,
        "P3_all_off_regulated_three": p3_all,
        "per_cell": per_cell,
    }
    OUTPUT.write_text(json.dumps(output, indent=2, default=str))
    print(f"\nwrote {OUTPUT.relative_to(REPO_ROOT)}")
    return 0


# ---- unit tests ------------------------------------------------------------

def _test() -> None:
    # M3 max on a synthetic fixture
    assert m3_max({"a": 0.5, "b": -0.7, "c": 0.1}) == -0.7
    assert m3_top2_sum({"a": 0.5, "b": -0.7, "c": 0.1}) == -(0.7 + 0.5)
    # entropy of uniform is log(n)
    e = m3_entropy({"a": 1.0, "b": 1.0, "c": 1.0})
    assert abs(e - math.log(3)) < 1e-9, e
    # AUC on a tiny labeled set: perfect separation = 1.0
    a = auc([0.1, 0.2, 0.9, 0.8], [0, 0, 1, 1])
    assert a == 1.0, a
    # AUC on inverted: 0.0
    a = auc([0.9, 0.8, 0.1, 0.2], [0, 0, 1, 1])
    assert a == 0.0, a
    # Permutation pipeline with fixed seed reproducibility
    r = auc_diff_permutation([0.1, 0.2, 0.9, 0.8], [0.2, 0.1, 0.8, 0.9],
                             [0, 0, 1, 1], n_perm=200, seed=42)
    r2 = auc_diff_permutation([0.1, 0.2, 0.9, 0.8], [0.2, 0.1, 0.8, 0.9],
                              [0, 0, 1, 1], n_perm=200, seed=42)
    assert r == r2, "permutation should be reproducible with same seed"
    # M3 features missing-handling
    assert m3_max(None) is None
    assert m3_max({}) is None
    print("unit tests OK")


if __name__ == "__main__":
    import sys
    if "--test" in sys.argv:
        _test()
        sys.exit(0)
    _test()  # always run sanity tests
    sys.exit(main())
