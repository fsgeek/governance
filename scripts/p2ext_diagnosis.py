#!/usr/bin/env python3
"""
Diagnose the P2-extended classifier accuracy drop (100% → 72%) in #12.

POST-HOC EXPLORATION — not pre-registered. Tony's question (2026-05-14):
is it seller_name, servicer_name, or both that drives the false-positive
rate when added to the saturation classifier? What's the pattern?
"""
from __future__ import annotations
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNS_DIR = REPO_ROOT / "runs"
VINTAGES = ["2018Q1", "2016Q1", "2008Q1"]

PROHIBITED_3 = {"property_state", "seller_name", "servicer_name"}


def feature_saturation(ufs: list[list[str]], features: set[str]) -> float:
    if not ufs:
        return 0.0
    return sum(1 for uf in ufs if any(f in uf for f in features)) / len(ufs)


def load_cells_with_ufs() -> list[dict]:
    out = []
    for v in VINTAGES:
        with open(RUNS_DIR / f"fm_rich_policy_vocab_adequacy_{v}.json") as f:
            d = json.load(f)
        for cell_id, cell in d["strata"]["S_rate"]["cells"].items():
            va = cell.get("variant_A_geography_admissible")
            vb = cell.get("variant_B_compliant_geography_prohibited")
            if not va or not vb: continue
            if va.get("verdict") != "ANALYZED" or vb.get("verdict") != "ANALYZED": continue
            na = va.get("n_distinct_used_feature_sets", 0)
            nb = vb.get("n_distinct_used_feature_sets", 0)
            if na < 2 or nb < 2: continue
            out.append({
                "vintage": v,
                "cell": cell_id,
                "ufs_A": va["distinct_used_feature_sets"],
                "n_A": na,
                "n_B": nb,
                "R2_A": va["R2_named"],
                "R2_B": vb["R2_named"],
            })
    return out


def load_reorganization_status() -> dict[tuple[str, str], bool]:
    d = json.load(open(RUNS_DIR / "silence_manufacture_2026-05-13.json"))
    return {(c["vintage"], c["cell"]): c["is_reorganized_primary"]
            for c in d["cells"] if c.get("in_scope")}


def main():
    cells = load_cells_with_ufs()
    reorg = load_reorganization_status()

    rows = []
    for c in cells:
        key = (c["vintage"], c["cell"])
        is_reorg = reorg.get(key, False)
        sat_p = feature_saturation(c["ufs_A"], {"property_state"})
        sat_s = feature_saturation(c["ufs_A"], {"seller_name"})
        sat_v = feature_saturation(c["ufs_A"], {"servicer_name"})
        sat_3 = feature_saturation(c["ufs_A"], PROHIBITED_3)
        rows.append({
            **c,
            "is_reorganized": is_reorg,
            "sat_property_state": sat_p,
            "sat_seller_name": sat_s,
            "sat_servicer_name": sat_v,
            "sat_3_prohib": sat_3,
        })

    print("=" * 100)
    print(f"{'vintage':<8} {'cell':<6} {'reorg':<6} {'sat_p':<7} {'sat_s':<7} {'sat_v':<7} {'sat_3':<7}  P2_predicts  P2ext_predicts")
    print("=" * 100)

    # All cells, sorted by sat_3 descending to see the false-positive band clearly.
    rows.sort(key=lambda r: (-r["sat_3_prohib"], r["vintage"], r["cell"]))
    p2_correct = p2ext_correct = 0
    p2ext_fp = []  # false positives: P2ext predicts reorganized, actually censored
    p2ext_fn = []  # false negatives: P2ext predicts censored, actually reorganized
    for r in rows:
        p2_pred = r["sat_property_state"] >= 0.5
        p2ext_pred = r["sat_3_prohib"] >= 0.5
        p2_match = "✓" if p2_pred == r["is_reorganized"] else "✗"
        p2ext_match = "✓" if p2ext_pred == r["is_reorganized"] else "✗"
        if p2_pred == r["is_reorganized"]: p2_correct += 1
        if p2ext_pred == r["is_reorganized"]: p2ext_correct += 1
        if p2ext_pred and not r["is_reorganized"]:
            p2ext_fp.append(r)
        if not p2ext_pred and r["is_reorganized"]:
            p2ext_fn.append(r)
        flag = " <-- FP" if (p2ext_pred and not r["is_reorganized"]) else (
               " <-- reorg" if r["is_reorganized"] else "")
        print(f"{r['vintage']:<8} {r['cell']:<6} {str(r['is_reorganized']):<6} "
              f"{r['sat_property_state']:.2f}    {r['sat_seller_name']:.2f}    {r['sat_servicer_name']:.2f}    "
              f"{r['sat_3_prohib']:.2f}     "
              f"{'reorg' if p2_pred else 'cens':<6}{p2_match}      "
              f"{'reorg' if p2ext_pred else 'cens':<6}{p2ext_match}{flag}")

    print()
    print(f"P2 accuracy: {p2_correct}/29 = {p2_correct/29:.1%}")
    print(f"P2-ext accuracy: {p2ext_correct}/29 = {p2ext_correct/29:.1%}")
    print()
    print(f"P2-ext false positives (predicted reorganized, actually censored): {len(p2ext_fp)}")
    print(f"P2-ext false negatives: {len(p2ext_fn)}")
    print()

    # For each FP, attribute to seller vs servicer.
    print("=" * 100)
    print("FALSE POSITIVE ATTRIBUTION (cells P2-ext misclassifies as reorganized)")
    print("=" * 100)
    seller_only_drives = 0
    servicer_only_drives = 0
    both_drive = 0
    neither_alone = 0
    for r in p2ext_fp:
        # Would seller_name alone (added to property_state) push it over?
        sat_p_s = feature_saturation(r["ufs_A"], {"property_state", "seller_name"})
        sat_p_v = feature_saturation(r["ufs_A"], {"property_state", "servicer_name"})
        seller_pushes = sat_p_s >= 0.5
        servicer_pushes = sat_p_v >= 0.5
        if seller_pushes and not servicer_pushes:
            attr = "seller_name alone pushes over threshold"
            seller_only_drives += 1
        elif servicer_pushes and not seller_pushes:
            attr = "servicer_name alone pushes over threshold"
            servicer_only_drives += 1
        elif seller_pushes and servicer_pushes:
            attr = "either alone pushes over"
            both_drive += 1
        else:
            attr = "only the combination pushes over (neither alone)"
            neither_alone += 1
        print(f"\n  {r['vintage']} {r['cell']}: sat_p={r['sat_property_state']:.2f} sat_s={r['sat_seller_name']:.2f} sat_v={r['sat_servicer_name']:.2f} sat_3={r['sat_3_prohib']:.2f}")
        print(f"    sat(p+s)={sat_p_s:.2f}  sat(p+v)={sat_p_v:.2f}")
        print(f"    attribution: {attr}")
        print(f"    R²_named A={r['R2_A']:.3f} B={r['R2_B']:.3f}; n_ufs_A={r['n_A']}")
        # Show the specific ufs containing seller/servicer
        sel_ufs = [uf for uf in r["ufs_A"] if "seller_name" in uf]
        srv_ufs = [uf for uf in r["ufs_A"] if "servicer_name" in uf]
        if sel_ufs:
            print(f"    A_ufs containing seller_name ({len(sel_ufs)}/{r['n_A']}, first 4):")
            for uf in sel_ufs[:4]:
                print(f"      {sorted(uf)}")
        if srv_ufs:
            print(f"    A_ufs containing servicer_name ({len(srv_ufs)}/{r['n_A']}, first 4):")
            for uf in srv_ufs[:4]:
                print(f"      {sorted(uf)}")

    print()
    print("=" * 100)
    print(f"FALSE POSITIVE DRIVER SUMMARY (n={len(p2ext_fp)}):")
    print(f"  seller_name alone pushes (servicer doesn't): {seller_only_drives}")
    print(f"  servicer_name alone pushes (seller doesn't): {servicer_only_drives}")
    print(f"  both/either alone push: {both_drive}")
    print(f"  only combination pushes (interaction): {neither_alone}")


if __name__ == "__main__":
    main()
