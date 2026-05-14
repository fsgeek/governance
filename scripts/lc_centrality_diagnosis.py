#!/usr/bin/env python3
"""
LC named+extension band centrality-vs-presence — post-hoc characterization.

NOT PRE-REGISTERED. The author peeked at top-3 saturation and top-5 importance
in `runs/extension_admitted_band_test_results.json` before attempting a
pre-registration; that contaminates the would-be predictions. This script does
the FULL quantitative analysis to characterize the pattern, transparently
labeled as post-hoc.

Input: runs/extension_admitted_band_test_results.json (#6 extension-admitted-band
test, named∪extension band per grade, v1=2015Q3 build).

Output: runs/lc_centrality_diagnosis_2026-05-14.json + stdout tables.
"""
from __future__ import annotations
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNS_DIR = REPO_ROOT / "runs"
OUT = RUNS_DIR / "lc_centrality_diagnosis_2026-05-14.json"

EXTENSION_FEATURES = {"revol_util", "open_acc", "inq_last_6mths", "delinq_2yrs",
                      "total_acc", "mort_acc", "loan_amnt", "revol_bal", "pub_rec"}
COLLAPSERS = {"C2", "C5", "D4"}  # from project_routable_population_result memory
PRIMES = {"A1", "A5", "B1"}


def analyze_grade(grade: str, g: dict) -> dict:
    bdm = g["band_distinct_members"]
    n_using_ext = g["n_distinct_members_using_extension"]
    counts = g["extension_feature_member_counts"]
    plural = g["plural"]
    n_distinct_ufs = g["n_distinct_used_feature_sets"]

    # Saturation per extension feature: count / band_distinct_members.
    saturation = {f: c / bdm for f, c in counts.items()}
    # Within-extension-using saturation: count / n_using_ext.
    sat_in_ext = {f: c / n_using_ext if n_using_ext else 0.0 for f, c in counts.items()}

    # Top by saturation.
    sat_sorted = sorted(saturation.items(), key=lambda x: -x[1])
    top_sat_feat, top_sat_value = sat_sorted[0] if sat_sorted else (None, 0.0)
    second_sat = sat_sorted[1][1] if len(sat_sorted) >= 2 else 0.0
    dominance_ratio = top_sat_value / second_sat if second_sat > 0 else float("inf")

    # Importance from v1 explainer_named_plus_extension.
    imp_v1 = dict(g["v1"]["explainer_named_plus_extension"]["top_importances"])
    imp_v2 = dict(g["v2"]["explainer_named_plus_extension"]["top_importances"])

    # Importance of EACH extension feature in v1's explainer (may be 0 if not in top).
    ext_imp_v1 = {f: imp_v1.get(f, 0.0) for f in EXTENSION_FEATURES}
    ext_imp_v2 = {f: imp_v2.get(f, 0.0) for f in EXTENSION_FEATURES}

    # Top extension feature by importance v1.
    ext_imp_v1_sorted = sorted(ext_imp_v1.items(), key=lambda x: -x[1])
    top_imp_v1_feat, top_imp_v1_value = ext_imp_v1_sorted[0]

    # Centrality-presence agreement.
    sat_imp_agree_v1 = (top_sat_feat == top_imp_v1_feat) and top_imp_v1_value > 0

    # Root feature of the disagreement explainer (full, not just extension).
    root_v1 = g["v1"]["explainer_named_plus_extension"]["root_feature"]
    root_v2 = g["v2"]["explainer_named_plus_extension"]["root_feature"]
    root_is_extension_v1 = root_v1 in EXTENSION_FEATURES

    # R²_named and R²_ext from v1.
    r2_named_v1 = g["v1"]["explainer_named"]["cv_r2"]
    r2_ext_v1 = g["v1"]["explainer_named_plus_extension"]["cv_r2"]
    delta_r2_v1 = g["v1"]["delta_r2"]

    return {
        "grade": grade,
        "band_distinct_members": bdm,
        "n_using_extension": n_using_ext,
        "n_distinct_ufs": n_distinct_ufs,
        "plural": plural,
        "tier": "collapser" if grade in COLLAPSERS else ("prime" if grade in PRIMES else "other"),
        "saturation_per_extension": dict(sat_sorted),
        "top_sat_feature": top_sat_feat,
        "top_sat_value": top_sat_value,
        "dominance_ratio_top_vs_second": dominance_ratio,
        "ext_importance_v1": dict(ext_imp_v1_sorted),
        "top_ext_imp_v1_feature": top_imp_v1_feat,
        "top_ext_imp_v1_value": top_imp_v1_value,
        "sat_imp_agree_v1": sat_imp_agree_v1,
        "explainer_root_v1": root_v1,
        "explainer_root_v2": root_v2,
        "root_is_extension_v1": root_is_extension_v1,
        "R2_named_v1": r2_named_v1,
        "R2_named_plus_ext_v1": r2_ext_v1,
        "delta_R2_v1": delta_r2_v1,
    }


def main():
    ext = json.load(open(RUNS_DIR / "extension_admitted_band_test_results.json"))
    rows = []
    for grade, g in ext["grades"].items():
        rows.append(analyze_grade(grade, g))

    # Pattern characterizations.
    # (1) Saturation × Importance agreement
    agree_count = sum(1 for r in rows if r["sat_imp_agree_v1"])
    # (2) Carrier identity across collapsers
    collapser_carriers = [r for r in rows if r["tier"] == "collapser"]
    collapser_top_sat = {r["grade"]: r["top_sat_feature"] for r in collapser_carriers}
    collapser_top_imp = {r["grade"]: r["top_ext_imp_v1_feature"] for r in collapser_carriers}
    # (3) Saturation distribution by tier
    prime_top_sats = [r["top_sat_value"] for r in rows if r["tier"] == "prime"]
    collapser_top_sats = [r["top_sat_value"] for r in rows if r["tier"] == "collapser"]
    # (4) Root-is-extension distribution by tier
    root_ext_collapsers = sum(1 for r in collapser_carriers if r["root_is_extension_v1"])
    root_ext_primes = sum(1 for r in rows if r["tier"] == "prime" and r["root_is_extension_v1"])

    summary = {
        "n_grades": len(rows),
        "n_sat_imp_agree": agree_count,
        "collapser_top_sat_features": collapser_top_sat,
        "collapser_top_imp_features": collapser_top_imp,
        "same_top_sat_across_collapsers": len(set(collapser_top_sat.values())) == 1,
        "same_top_imp_across_collapsers": len(set(collapser_top_imp.values())) == 1,
        "prime_top_sat_mean": sum(prime_top_sats) / len(prime_top_sats) if prime_top_sats else None,
        "collapser_top_sat_mean": sum(collapser_top_sats) / len(collapser_top_sats) if collapser_top_sats else None,
        "root_is_extension_collapsers": f"{root_ext_collapsers}/{len(collapser_carriers)}",
        "root_is_extension_primes": f"{root_ext_primes}/{len([r for r in rows if r['tier']=='prime'])}",
    }

    OUT.write_text(json.dumps({"summary": summary, "grades": rows}, indent=2, default=str))
    print(f"Wrote {OUT.relative_to(REPO_ROOT)}\n")

    print("=" * 100)
    print(f"{'grade':<6} {'tier':<10} {'plural':<7} {'top_sat':<18} {'top_imp_ext':<18} {'agree':<6} {'root_v1':<22} {'R²_n':<6} {'ΔR²ext':<6}")
    print("=" * 100)
    for r in rows:
        plural_str = str(r["plural"])
        top_sat = f"{r['top_sat_feature']}={r['top_sat_value']:.2f}"
        top_imp = f"{r['top_ext_imp_v1_feature']}={r['top_ext_imp_v1_value']:.2f}"
        agree = "✓" if r["sat_imp_agree_v1"] else "✗"
        print(f"{r['grade']:<6} {r['tier']:<10} {plural_str:<7} {top_sat:<18} {top_imp:<18} {agree:<6} {r['explainer_root_v1']:<22} {r['R2_named_v1']:.2f}   {r['delta_R2_v1']:.2f}")
    print()

    print(f"SAT × IMP AGREEMENT (top-by-saturation == top-extension-by-importance): {agree_count}/{len(rows)}")
    print()
    print(f"COLLAPSER carriers (top-by-saturation):  {collapser_top_sat}")
    print(f"COLLAPSER carriers (top-by-importance):  {collapser_top_imp}")
    print(f"  same top-sat across all 3 collapsers? {summary['same_top_sat_across_collapsers']}")
    print(f"  same top-imp across all 3 collapsers? {summary['same_top_imp_across_collapsers']}")
    print()
    prime_list = [(r['grade'], round(r['top_sat_value'], 2)) for r in rows if r['tier']=='prime']
    coll_list = [(r['grade'], round(r['top_sat_value'], 2)) for r in rows if r['tier']=='collapser']
    print(f"TOP-SAT DISTRIBUTION:")
    print(f"  prime mean: {summary['prime_top_sat_mean']:.3f}    (per-grade: {prime_list})")
    print(f"  collapser mean: {summary['collapser_top_sat_mean']:.3f}    (per-grade: {coll_list})")
    print()
    print(f"ROOT IS EXTENSION FEATURE (in the disagreement explainer):")
    print(f"  collapsers: {summary['root_is_extension_collapsers']}")
    print(f"  primes:     {summary['root_is_extension_primes']}")


if __name__ == "__main__":
    main()
