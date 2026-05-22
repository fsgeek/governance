"""Arm-1 codification-knob robustness recompute (adequacy threshold 0.30).

Pre-reg (FROZEN, OTS-stamped 2026-05-22, commit 02fc921):
    docs/superpowers/specs/2026-05-22-codification-knob-robustness-preregistration-note.md

Reflexive falsification of "discipline-not-structure": did the OTS freeze pin
the verdicts, or did it freeze predictions against an arbitrary inherited
constant (R2_named adequacy threshold = 0.30) that it never controlled?

Arm 1 sweeps the adequacy threshold over stored per-cell R2_named -- pure
re-threshold, NO re-fit. The verdict definitions recomputed here mirror the
originals exactly:
    adequacy(r2)        = r2 >= thr                       (silence #12: L78-81; hmda L524-527)
    verdict_differs(a,b)= adequacy(a) != adequacy(b)      (silence #12: L127; hmda L614)
    manufactured_silence= is_reorg_primary and verdict_differs   (silence #12: L130)

Run:  PYTHONPATH=. python scripts/knob_robustness_arm1.py
"""

from __future__ import annotations

import json
from pathlib import Path

RUNS = Path(__file__).resolve().parents[1] / "runs"

# Frozen sweep (pre-reg section 5).
SWEEP = [0.20, 0.25, 0.28, 0.30, 0.32, 0.35, 0.40]
ORIGINAL = 0.30


# ---- pure verdict logic (mirrors the original cycles) -----------------------

def adequacy(r2, thr):
    if r2 is None:
        return None
    return r2 >= thr


def verdict_differs(r2a, r2b, thr):
    a, b = adequacy(r2a, thr), adequacy(r2b, thr)
    if a is None or b is None:
        return False
    return a != b


def manufactured_silence(r2a, r2b, is_reorg, thr):
    return bool(is_reorg) and verdict_differs(r2a, r2b, thr)


def silence_active_interval(r2a, r2b):
    """Threshold band (lo, hi] on which verdict_differs is True for this pair."""
    return (min(r2a, r2b), max(r2a, r2b))


def flips(labels):
    """Number of True/False transitions across an ordered label list."""
    return sum(1 for i in range(1, len(labels)) if labels[i] != labels[i - 1])


def flip_fraction(cells, sweep):
    """Fraction of cells whose manufactured_silence label changes across the sweep."""
    if not cells:
        return 0.0
    n_flip = 0
    for c in cells:
        labels = [manufactured_silence(c["r2a"], c["r2b"], c["reorg"], t) for t in sweep]
        if flips(labels) > 0:
            n_flip += 1
    return n_flip / len(cells)


# ---- extraction adapters (per stored-JSON schema) ---------------------------

def _cells_silence_ab(d):
    """silence_manufacture_*.json and hmda_*.json: list of A/B cells."""
    rows = d.get("cells") or d.get("per_cell") or []
    out = []
    j_primary = d.get("j_primary") or d.get("j_threshold_primary")
    for c in rows:
        if not c.get("in_scope", True):
            continue
        r2a = c.get("R2_named_A")
        r2b = c.get("R2_named_B")
        if r2a is None or r2b is None:
            # frame_evocation nesting
            r2a = (c.get("variant_A") or {}).get("R2_named")
            r2b = (c.get("variant_B") or {}).get("R2_named")
        if r2a is None or r2b is None:
            continue
        if "is_reorganized_primary" in c:
            reorg = c["is_reorganized_primary"]
        elif c.get("jaccard_A_restricted_vs_B") is not None and j_primary is not None:
            reorg = c["jaccard_A_restricted_vs_B"] < j_primary
        else:
            reorg = None
        out.append({
            "cell": f'{c.get("vintage","")}/{c.get("cell","")}'.strip("/"),
            "r2a": r2a, "r2b": r2b, "reorg": reorg,
        })
    return out


def score_cycle(name, path, arm, knob_provenance):
    p = RUNS / path
    if not p.exists():
        return {"cycle": name, "status": "MISSING", "path": path}
    d = json.load(open(p))
    cells = _cells_silence_ab(d)
    if not cells:
        return {"cycle": name, "status": "RECOMPUTE-INFEASIBLE", "path": path}

    have_reorg = all(c["reorg"] is not None for c in cells)
    # If reorg missing, fall back to verdict_differs (silence without the reorg gate).
    def label(c, t):
        if have_reorg:
            return manufactured_silence(c["r2a"], c["r2b"], c["reorg"], t)
        return verdict_differs(c["r2a"], c["r2b"], t)

    counts = {t: sum(label(c, t) for c in cells) for t in SWEEP}
    positives_at_orig = [c for c in cells if label(c, ORIGINAL)]
    fragile_positives = [
        c for c in positives_at_orig
        if flips([label(c, t) for t in SWEEP]) > 0
    ]
    return {
        "cycle": name,
        "arm": arm,
        "knob_provenance": knob_provenance,
        "verdict_metric": "manufactured_silence" if have_reorg else "verdict_differs (reorg unavailable)",
        "n_scored": len(cells),
        "n_positive_at_0.30": len(positives_at_orig),
        "n_positive_fragile": len(fragile_positives),
        "frac_positives_fragile": (len(fragile_positives) / len(positives_at_orig)) if positives_at_orig else None,
        "silence_count_by_threshold": {f"{t:.2f}": counts[t] for t in SWEEP},
        "silence_count_min_max": [min(counts.values()), max(counts.values())],
        "flip_fraction_all_cells": round(flip_fraction(
            [{"r2a": c["r2a"], "r2b": c["r2b"], "reorg": c["reorg"] if have_reorg else True} for c in cells], SWEEP), 4),
        "fragile_positive_cells": [
            {"cell": c["cell"], "r2a": round(c["r2a"], 4), "r2b": round(c["r2b"], 4),
             "gap": round(abs(c["r2a"] - c["r2b"]), 4)}
            for c in fragile_positives
        ][:20],
    }


# Frozen corpus (pre-reg section 3). knob_provenance per section-6 audit.
CORPUS = [
    ("variant-indexical-silence-#12", "silence_manufacture_2026-05-13.json", "treatment", "inherited-from-#11"),
    ("expanded-vintage-silence",       "silence_manufacture_2026-05-20.json", "treatment", "inherited-from-#11"),
    ("frame-evocation",                "frame_evocation_2026-05-15.json",     "treatment", "inherited-from-#11"),
    ("expanded-frame-evocation",       "frame_evocation_2026-05-20.json",     "treatment", "inherited-from-#11"),
    ("hmda-trimodal-replication",      "hmda_trimodal_replication_2026-05-14.json", "treatment", "inherited-from-#11 (transferred floor)"),
]


def main():
    results = [score_cycle(*c) for c in CORPUS]
    out = {
        "test": "codification-knob-robustness-arm1",
        "pre_reg": "docs/superpowers/specs/2026-05-22-codification-knob-robustness-preregistration-note.md",
        "pre_reg_commit": "02fc921",
        "knob": "adequacy_threshold_R2_named",
        "original_value": ORIGINAL,
        "sweep": SWEEP,
        "recompute_mode": "re-threshold stored per-cell R2_named (no re-fit)",
        "cycles": results,
    }
    outpath = RUNS / "knob_robustness_arm1_2026-05-22.json"
    json.dump(out, open(outpath, "w"), indent=2)

    print(f"\n=== Arm-1 knob robustness (adequacy threshold; sweep {SWEEP}) ===")
    for r in results:
        if r.get("status"):
            print(f"\n{r['cycle']}: {r['status']}")
            continue
        print(f"\n{r['cycle']}  [{r['arm']}, knob {r['knob_provenance']}]  metric={r['verdict_metric']}")
        print(f"  n_scored={r['n_scored']}  positives@0.30={r['n_positive_at_0.30']}  "
              f"fragile positives={r['n_positive_fragile']}  "
              f"frac_positives_fragile={r['frac_positives_fragile']}")
        print(f"  silence/divergence count by threshold: {r['silence_count_by_threshold']}")
        print(f"  count range across sweep: {r['silence_count_min_max']}")
        if r["fragile_positive_cells"]:
            print(f"  fragile positive cells (flip somewhere in sweep):")
            for c in r["fragile_positive_cells"]:
                print(f"    {c['cell']}: R2_A={c['r2a']} R2_B={c['r2b']} gap={c['gap']}")
    print(f"\nwrote {outpath}")
    return out


if __name__ == "__main__":
    main()
