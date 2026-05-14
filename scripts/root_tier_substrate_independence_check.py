#!/usr/bin/env python3
"""
Substrate-independence sanity check for the explainer-root-tier discriminator.

Claim from 2026-05-14 LC post-hoc note §4: reorganization-flag operationalized
via explainer-root-feature-tier (named vs extension/prohibited) is substrate-
independent — works on both FM and LC.

This script tests the FM half: does the root-tier discriminator agree with
#12's Jaccard-based reorganization classification on the 29-cell FM corpus?

Also: chases the C1 dedup story by comparing #6 (tree-signature-dedup, the
saved data used in the LC post-hoc) to [[project_routable_population_result]]'s
used-feature-set dedup, if that data is available.

NOT pre-registered — sanity check on existing claim.
"""
from __future__ import annotations
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNS_DIR = REPO_ROOT / "runs"

VINTAGES = ["2018Q1", "2016Q1", "2008Q1"]
FM_EXTENSION_FEATURES = {"property_state", "seller_name", "servicer_name", "msa", "original_upb"}
FM_NAMED_FEATURES_BASE = {"fico_range_low", "dti", "ltv", "cltv", "mortgage_insurance_pct",
                          "loan_term_months", "loan_purpose", "num_units", "num_borrowers",
                          "first_time_homebuyer", "property_type", "amortization_type",
                          "occupancy_status"}


def fm_root_tier(root_feature: str, candidate_named: list[str], candidate_extension: list[str]) -> str:
    """Classify a root feature as 'named' or 'extension' based on the cell's candidate sets."""
    if root_feature in candidate_named:
        return "named"
    if root_feature in candidate_extension:
        return "extension"
    return f"unknown:{root_feature}"


def main():
    # Load #12's reorganization classification.
    sm = json.load(open(RUNS_DIR / "silence_manufacture_2026-05-13.json"))
    sm_lookup = {(c["vintage"], c["cell"]): c for c in sm["cells"] if c.get("in_scope")}

    print("=" * 110)
    print(f"{'vintage':<8} {'cell':<6} {'jacc_reorg':<12} {'rootA':<22} {'tierA':<11} {'rootB':<22} {'tierB':<11} {'root_disc':<10} {'agree?':<8}")
    print("=" * 110)

    agreements = 0
    disagreements = []
    for v in VINTAGES:
        with open(RUNS_DIR / f"fm_rich_policy_vocab_adequacy_{v}.json") as f:
            d = json.load(f)
        cells = d["strata"]["S_rate"]["cells"]
        for cell_id, cell in cells.items():
            key = (v, cell_id)
            if key not in sm_lookup: continue
            sm_cell = sm_lookup[key]
            is_reorg = sm_cell["is_reorganized_primary"]
            va = cell["variant_A_geography_admissible"]
            vb = cell["variant_B_compliant_geography_prohibited"]
            # The all-explainer's root is the right comparable signal because it's the explainer
            # over the band's CANDIDATE features (named + extension on A, named + remaining on B).
            rootA = va.get("explainer_all_root_feature")
            rootB = vb.get("explainer_all_root_feature")
            cand_named_A = va.get("candidate_named", [])
            cand_ext_A = va.get("candidate_extension", [])
            cand_named_B = vb.get("candidate_named", [])
            cand_ext_B = vb.get("candidate_extension", [])
            tierA = fm_root_tier(rootA, cand_named_A, cand_ext_A)
            tierB = fm_root_tier(rootB, cand_named_B, cand_ext_B)

            # Root-tier discriminator (proposed substrate-independent operationalization):
            # cell is "reorganized/carrier-extension-driven" iff variant-A's all-explainer roots on
            # a PROHIBITED feature (one that's in candidate_extension_A but NOT in candidate_extension_B).
            prohibited = set(cand_ext_A) - set(cand_ext_B)
            root_disc_reorg = rootA in prohibited

            agree = root_disc_reorg == is_reorg
            if agree:
                agreements += 1
            else:
                disagreements.append({
                    "vintage": v, "cell": cell_id, "jacc_reorg": is_reorg, "root_disc_reorg": root_disc_reorg,
                    "rootA": rootA, "rootB": rootB, "tierA": tierA, "tierB": tierB,
                    "prohibited": sorted(prohibited),
                    "R2_named_A": va.get("R2_named"), "R2_named_B": vb.get("R2_named"),
                })
            print(f"{v:<8} {cell_id:<6} {str(is_reorg):<12} {str(rootA)[:21]:<22} {tierA:<11} {str(rootB)[:21]:<22} {tierB:<11} {str(root_disc_reorg):<10} {'✓' if agree else '✗':<8}")

    print()
    print(f"Root-tier discriminator vs #12 Jaccard discriminator agreement: {agreements}/{len(sm_lookup)}")
    print()
    if disagreements:
        print("DISAGREEMENTS:")
        for d in disagreements:
            print(f"  {d['vintage']} {d['cell']}: jacc_reorg={d['jacc_reorg']}, root_disc_reorg={d['root_disc_reorg']}")
            print(f"    rootA={d['rootA']} (tier={d['tierA']}), rootB={d['rootB']} (tier={d['tierB']})")
            print(f"    prohibited features={d['prohibited']}, R²_named A={d['R2_named_A']:.3f} B={d['R2_named_B']:.3f}")
    else:
        print("CLEAN AGREEMENT — root-tier discriminator and Jaccard discriminator classify every cell identically.")

    # C1 dedup story
    print()
    print("=" * 110)
    print("C1 DEDUP STORY")
    print("=" * 110)
    # The #6 extension-admitted JSON has C1 under tree-signature dedup.
    ext = json.load(open(RUNS_DIR / "extension_admitted_band_test_results.json"))
    c1_ext = ext["grades"].get("C1")
    if c1_ext:
        print(f"#6 extension-admitted (tree-sig dedup):")
        print(f"  C1 n_distinct_ufs={c1_ext['n_distinct_used_feature_sets']}")
        print(f"  C1 R²_named (v1)={c1_ext['v1']['explainer_named']['cv_r2']:.3f}")
        print(f"  C1 root (v1 named+ext explainer)={c1_ext['v1']['explainer_named_plus_extension']['root_feature']}")
        top_imp_v1 = c1_ext['v1']['explainer_named_plus_extension']['top_importances']
        print(f"  C1 top importances v1: {top_imp_v1}")

    # routable_population_test has the used-feature-set dedup version
    rp_path = RUNS_DIR / "routable_population_test_results.json"
    if rp_path.exists():
        rp = json.load(open(rp_path))
        print()
        print(f"[[project_routable_population_result]] (used-feature-set dedup):")
        print(f"  top-level keys: {list(rp.keys())}")
        # Drill into grades structure if present
        grades = rp.get("grades")
        if isinstance(grades, dict) and "C1" in grades:
            c1_rp = grades["C1"]
            print(f"  C1 keys: {list(c1_rp.keys())[:30]}")
            # Find R²_named under uf-dedup
            for k, v in c1_rp.items():
                if isinstance(v, dict) and any(sub in k.lower() for sub in ('explainer', 'named', 'v1', 'v2', 'ufs', 'used_feat')):
                    print(f"    {k}: dict keys={list(v.keys())[:15]}")
                elif not isinstance(v, (dict, list)):
                    print(f"    {k}={v}")
                elif isinstance(v, list) and len(v) < 10:
                    print(f"    {k}={v}")


if __name__ == "__main__":
    main()
