#!/usr/bin/env python3
"""
Silence-manufacture analysis across the FM #11 band corpus.

Pre-reg: docs/superpowers/specs/2026-05-13-variant-indexical-silence-manufacture-preregistration-note.md
Commit: 9dd642b (substantive) / 3a8959f (OTS)

Operates on saved #11 JSONs in runs/. No new compute, no model fits.
Outputs runs/silence_manufacture_2026-05-13.json with full per-cell and
aggregate results.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from collections import defaultdict

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNS_DIR = REPO_ROOT / "runs"
OUTPUT = RUNS_DIR / "silence_manufacture_2026-05-13.json"

VINTAGES = ["2018Q1", "2016Q1", "2008Q1"]
J_THRESHOLDS = [0.3, 0.4, 0.5, 0.6, 0.7]
J_PRIMARY = 0.5
ADEQUACY_R2_NAMED = 0.30  # pre-registered: R²_named >= 0.30 = vocab-adequate


def _input_path(vintage: str) -> Path:
    return RUNS_DIR / f"fm_rich_policy_vocab_adequacy_{vintage}.json"


def jaccard_set_of_frozensets(A: set[frozenset], B: set[frozenset]) -> float:
    if not A and not B:
        return 1.0
    inter = len(A & B)
    union = len(A | B)
    return inter / union if union else 0.0


def restrict(ufs: list[list[str]], prohibited: set[str]) -> set[frozenset]:
    """Restrict each uf to non-prohibited features; return set-of-frozensets.

    Empty frozenset ∈ result means at least one uf used only prohibited features.
    """
    return {frozenset(uf) - frozenset(prohibited) for uf in ufs}


def classify_reorganized(A_restricted: set[frozenset], B_set: set[frozenset], j_thresh: float) -> tuple[bool, str, float]:
    """Return (is_reorganized, reason, jaccard)."""
    j = jaccard_set_of_frozensets(A_restricted, B_set)
    if frozenset() in A_restricted:
        return True, "empty-uf-in-A-restricted", j
    if j < j_thresh:
        return True, f"jaccard<{j_thresh}", j
    return False, "censored", j


def property_state_saturation(ufs: list[list[str]]) -> float:
    """Fraction of variant-A ufs that contain `property_state`."""
    if not ufs:
        return 0.0
    n = sum(1 for uf in ufs if "property_state" in uf)
    return n / len(ufs)


def restricted_saturation(ufs: list[list[str]], features: set[str]) -> float:
    """Fraction of ufs that contain any feature in `features`."""
    if not ufs:
        return 0.0
    n = sum(1 for uf in ufs if any(f in uf for f in features))
    return n / len(ufs)


def adequacy(r2_named: float | None) -> str | None:
    if r2_named is None:
        return None
    return "adequate" if r2_named >= ADEQUACY_R2_NAMED else "inadequate"


def analyze_cell(cell_id: str, cell: dict, vintage: str) -> dict | None:
    """Return per-cell analysis dict, or None if cell is out of scope."""
    va = cell.get("variant_A_geography_admissible")
    vb = cell.get("variant_B_compliant_geography_prohibited")
    if not va or not vb:
        return None
    if va.get("verdict") != "ANALYZED" or vb.get("verdict") != "ANALYZED":
        return {"vintage": vintage, "cell": cell_id, "in_scope": False,
                "reason_out": f"verdict A={va.get('verdict')} B={vb.get('verdict')}"}

    na = va.get("n_distinct_used_feature_sets", 0)
    nb = vb.get("n_distinct_used_feature_sets", 0)
    if na < 2 or nb < 2:
        return {"vintage": vintage, "cell": cell_id, "in_scope": False,
                "reason_out": f"n_ufs A={na} B={nb}"}

    # Defensive prohibited-features computation per cell.
    cand_ext_A = set(va.get("candidate_extension", []))
    cand_ext_B = set(vb.get("candidate_extension", []))
    prohibited = cand_ext_A - cand_ext_B

    ufs_A = va.get("distinct_used_feature_sets", [])
    ufs_B = vb.get("distinct_used_feature_sets", [])

    A_restricted = restrict(ufs_A, prohibited)
    B_set = {frozenset(uf) for uf in ufs_B}

    # Classify at all J thresholds.
    classifications = {}
    for j_thresh in J_THRESHOLDS:
        is_reorg, reason, j = classify_reorganized(A_restricted, B_set, j_thresh)
        classifications[f"j_thresh_{j_thresh}"] = {
            "reorganized": is_reorg, "reason": reason, "jaccard": j,
        }

    # Primary verdict at J_PRIMARY.
    is_reorg_primary, reason_primary, j_primary = classify_reorganized(A_restricted, B_set, J_PRIMARY)

    # Verdict pair.
    r2_A = va.get("R2_named")
    r2_B = vb.get("R2_named")
    adq_A = adequacy(r2_A)
    adq_B = adequacy(r2_B)
    verdict_differs = (adq_A != adq_B) if (adq_A and adq_B) else False

    # Manufactured silence (primary J).
    manufactured_silence = is_reorg_primary and verdict_differs

    # P2 predictors.
    p_sat_A = property_state_saturation(ufs_A)
    p_sat_A_3prohib = restricted_saturation(ufs_A, {"property_state", "seller_name", "servicer_name"})

    # Auxiliary info for the result note.
    rung = va.get("rung_classification") or vb.get("rung_classification")
    plural_A = va.get("plural", False)
    plural_B = vb.get("plural", False)

    return {
        "vintage": vintage,
        "cell": cell_id,
        "in_scope": True,
        "n_distinct_ufs_A": na,
        "n_distinct_ufs_B": nb,
        "prohibited_features": sorted(prohibited),
        "R2_named_A": r2_A,
        "R2_named_B": r2_B,
        "adequacy_A": adq_A,
        "adequacy_B": adq_B,
        "verdict_differs": verdict_differs,
        "plural_A": plural_A,
        "plural_B": plural_B,
        "rung_classification": rung,
        "property_state_saturation_A": p_sat_A,
        "prohibited_3_saturation_A": p_sat_A_3prohib,
        "jaccard_primary": j_primary,
        "is_reorganized_primary": is_reorg_primary,
        "reorganization_reason_primary": reason_primary,
        "manufactured_silence": manufactured_silence,
        "j_threshold_sensitivity": classifications,
        "ufs_A_restricted_repr": sorted([sorted(s) for s in A_restricted]),
        "ufs_B_repr": sorted([sorted(uf) for uf in ufs_B]) if len(ufs_B) <= 20 else f"<{len(ufs_B)} ufs>",
    }


def aggregate(cells: list[dict]) -> dict:
    in_scope = [c for c in cells if c.get("in_scope")]
    n = len(in_scope)
    if n == 0:
        return {"n_in_scope": 0}

    reorganized = [c for c in in_scope if c["is_reorganized_primary"]]
    censored = [c for c in in_scope if not c["is_reorganized_primary"]]
    manufactured_silence_cells = [c for c in in_scope if c["manufactured_silence"]]

    # P1: reorganization rate
    p1_rate = len(reorganized) / n
    p1_hit = len(reorganized) >= 5  # >= 15% of 29 cells means >= 5

    # P2: property_state saturation classifies reorganization
    p2_correct = 0
    for c in in_scope:
        predicted_reorg = c["property_state_saturation_A"] >= 0.5
        actual_reorg = c["is_reorganized_primary"]
        if predicted_reorg == actual_reorg:
            p2_correct += 1
    p2_accuracy = p2_correct / n
    p2_hit = p2_accuracy >= 0.80

    # P2-extended: 3-prohibited saturation
    p2ext_correct = 0
    for c in in_scope:
        predicted_reorg = c["prohibited_3_saturation_A"] >= 0.5
        actual_reorg = c["is_reorganized_primary"]
        if predicted_reorg == actual_reorg:
            p2ext_correct += 1
    p2ext_accuracy = p2ext_correct / n

    # P3: verdict divergence among reorganized cells
    if reorganized:
        p3_diverge_rate = sum(1 for c in reorganized if c["verdict_differs"]) / len(reorganized)
    else:
        p3_diverge_rate = None
    p3_hit = (p3_diverge_rate is not None) and (p3_diverge_rate >= 0.60)

    # P4: manufactured silence count
    p4_count = len(manufactured_silence_cells)
    p4_hit = p4_count >= 4

    # P5: reorganized vs censored verdict-divergence ratio
    if censored:
        cens_diverge_rate = sum(1 for c in censored if c["verdict_differs"]) / len(censored)
    else:
        cens_diverge_rate = None
    if reorganized and censored and cens_diverge_rate > 0:
        p5_ratio = p3_diverge_rate / cens_diverge_rate
    elif reorganized and censored and cens_diverge_rate == 0:
        p5_ratio = float("inf")
    else:
        p5_ratio = None
    p5_hit = (p5_ratio is not None) and (p5_ratio >= 3.0)

    # Sensitivity over J thresholds.
    sensitivity = {}
    for j_thresh in J_THRESHOLDS:
        key = f"j_thresh_{j_thresh}"
        reorg_at_j = [c for c in in_scope if c["j_threshold_sensitivity"][key]["reorganized"]]
        ms_at_j = [c for c in reorg_at_j if c["verdict_differs"]]
        sensitivity[key] = {
            "n_reorganized": len(reorg_at_j),
            "reorganization_rate": len(reorg_at_j) / n,
            "n_manufactured_silence": len(ms_at_j),
        }

    return {
        "n_in_scope": n,
        "n_reorganized": len(reorganized),
        "n_censored": len(censored),
        "n_manufactured_silence": p4_count,
        "manufactured_silence_cells": [(c["vintage"], c["cell"]) for c in manufactured_silence_cells],
        "P1_reorganization_rate": p1_rate,
        "P1_HIT": p1_hit,
        "P2_classifier_accuracy_property_state": p2_accuracy,
        "P2_HIT": p2_hit,
        "P2_extended_classifier_accuracy_3prohib": p2ext_accuracy,
        "P3_verdict_divergence_on_reorganized": p3_diverge_rate,
        "P3_HIT": p3_hit,
        "P4_manufactured_silence_count": p4_count,
        "P4_HIT": p4_hit,
        "P5_divergence_ratio_reorg_over_censored": p5_ratio,
        "P5_censored_divergence_rate": cens_diverge_rate,
        "P5_HIT": p5_hit,
        "j_threshold_sensitivity": sensitivity,
    }


def selftest():
    """Synthetic-fixture self-tests for the Jaccard discriminator."""
    # Fixture 1: pure censoring (variant B = variant A minus prohibited).
    ufs_A = [["fico", "property_state"], ["dti", "property_state"]]
    ufs_B = [["fico"], ["dti"]]
    prohibited = {"property_state"}
    A_r = restrict(ufs_A, prohibited)
    B_s = {frozenset(uf) for uf in ufs_B}
    j = jaccard_set_of_frozensets(A_r, B_s)
    assert j == 1.0, f"pure censoring: expected J=1.0, got {j}"
    is_reorg, _, _ = classify_reorganized(A_r, B_s, 0.5)
    assert not is_reorg, "pure censoring should be classified censored"

    # Fixture 2: pure reorganization (variant B uses different features).
    ufs_A = [["dti", "property_state"], ["dti", "loan_purpose", "property_state"]]
    ufs_B = [["fico"], ["fico", "cltv"]]
    A_r = restrict(ufs_A, prohibited)
    B_s = {frozenset(uf) for uf in ufs_B}
    j = jaccard_set_of_frozensets(A_r, B_s)
    assert j == 0.0, f"pure reorganization: expected J=0.0, got {j}"
    is_reorg, _, _ = classify_reorganized(A_r, B_s, 0.5)
    assert is_reorg, "pure reorganization should be classified reorganized"

    # Fixture 3: empty-uf short-circuit (variant A uf used only prohibited).
    ufs_A = [["property_state"], ["fico"]]
    ufs_B = [["fico"], ["fico", "cltv"]]
    A_r = restrict(ufs_A, prohibited)
    # A_r should contain frozenset() (from ["property_state"] minus prohibited).
    assert frozenset() in A_r, "empty-uf should be in A_restricted"
    is_reorg, reason, j = classify_reorganized(A_r, B_s, 0.5)
    assert is_reorg, "empty-uf-in-A-restricted should classify reorganized"
    assert reason == "empty-uf-in-A-restricted", f"reason: {reason}"

    # Fixture 4: borderline Jaccard (3 shared, 3 unique each → J = 3/9 = 0.333).
    ufs_A = [["a"], ["b"], ["c"], ["d"], ["e"], ["f"]]
    ufs_B = [["a"], ["b"], ["c"], ["g"], ["h"], ["i"]]
    A_r = {frozenset(uf) for uf in ufs_A}  # no prohibited
    B_s = {frozenset(uf) for uf in ufs_B}
    j = jaccard_set_of_frozensets(A_r, B_s)
    assert abs(j - 3 / 9) < 1e-9, f"borderline: expected J=0.333, got {j}"
    # J = 0.333 < 0.5 → reorganized; >= 0.3 → not reorganized.
    is_reorg_05, _, _ = classify_reorganized(A_r, B_s, 0.5)
    is_reorg_03, _, _ = classify_reorganized(A_r, B_s, 0.3)
    assert is_reorg_05 and not is_reorg_03, "borderline threshold sensitivity"

    print("selftest: 4 fixtures OK")


def main():
    selftest()

    all_cells = []
    for vintage in VINTAGES:
        path = _input_path(vintage)
        if not path.exists():
            print(f"WARN: {path} not found", file=sys.stderr)
            continue
        with open(path) as f:
            d = json.load(f)
        cells = d["strata"]["S_rate"]["cells"]
        for cell_id, cell in cells.items():
            result = analyze_cell(cell_id, cell, vintage)
            if result is not None:
                all_cells.append(result)

    agg = aggregate([c for c in all_cells if c.get("in_scope")])

    output = {
        "test": "silence-manufacture variant-indexicality (#12)",
        "pre_reg_commit": "9dd642b",
        "pre_reg_ots_commit": "3a8959f",
        "pre_reg_path": "docs/superpowers/specs/2026-05-13-variant-indexical-silence-manufacture-preregistration-note.md",
        "j_threshold_primary": J_PRIMARY,
        "j_thresholds_sensitivity": J_THRESHOLDS,
        "adequacy_threshold_R2_named": ADEQUACY_R2_NAMED,
        "n_cells_considered": len(all_cells),
        "aggregate": agg,
        "cells": all_cells,
    }

    OUTPUT.write_text(json.dumps(output, indent=2, default=str))
    print(f"\nWrote {OUTPUT.relative_to(REPO_ROOT)}")
    print(f"\n=== AGGREGATE SCORECARD ===")
    print(f"  n in scope: {agg['n_in_scope']}")
    print(f"  reorganized: {agg['n_reorganized']} ({agg['P1_reorganization_rate']:.1%})")
    print(f"  censored:    {agg['n_censored']}")
    print(f"  manufactured silence cells: {agg['n_manufactured_silence']}")
    for v, c in agg["manufactured_silence_cells"]:
        print(f"    - {v} {c}")
    print()
    print(f"  P1 (reorg rate >=15%, >=5 cells): {'HIT' if agg['P1_HIT'] else 'MISS'} (rate={agg['P1_reorganization_rate']:.1%}, n={agg['n_reorganized']})")
    print(f"  P2 (property_state classifier >=80%): {'HIT' if agg['P2_HIT'] else 'MISS'} (acc={agg['P2_classifier_accuracy_property_state']:.1%})")
    print(f"      P2-ext (3-prohib saturation classifier): acc={agg['P2_extended_classifier_accuracy_3prohib']:.1%}")
    p3rate = agg["P3_verdict_divergence_on_reorganized"]
    print(f"  P3 (verdict divergence on reorg >=60%): {'HIT' if agg['P3_HIT'] else 'MISS'} (rate={'N/A' if p3rate is None else f'{p3rate:.1%}'})")
    print(f"  P4 (manufactured silence count >=4): {'HIT' if agg['P4_HIT'] else 'MISS'} (n={agg['P4_manufactured_silence_count']})")
    p5r = agg["P5_divergence_ratio_reorg_over_censored"]
    print(f"  P5 (reorg/cens divergence ratio >=3): {'HIT' if agg['P5_HIT'] else 'MISS'} (ratio={p5r})")
    print(f"      censored divergence rate: {agg['P5_censored_divergence_rate']}")
    print()
    print(f"  J-threshold sensitivity (reorg rate, ms count):")
    for j_key, vals in agg["j_threshold_sensitivity"].items():
        print(f"    {j_key}: reorg={vals['n_reorganized']}/{agg['n_in_scope']} ({vals['reorganization_rate']:.1%}), ms={vals['n_manufactured_silence']}")


if __name__ == "__main__":
    main()
