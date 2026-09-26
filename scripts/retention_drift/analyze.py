"""Score the retention-drift gate (pre-reg dc12f1a §5, §7). Reads saved arrays only.

Writes runs/retention_drift/results.json and prints the pair table and the gate verdict.
"""
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2] / "runs/retention_drift"
LABELS = ["v2021", "v2022", "v2023", "v2023p", "v2024", "v2025", "v2026"]
PRIMARY = {"v2021", "v2022", "v2023", "v2024", "v2025", "v2026"}
year = lambda v: int(v[1:5])
MODELS = ["gbc", "xgb"]
METHODS = ["tree", "kernel_pinned", "kernel_default", "lime"]
K, P_RBO, NBOOT, BOOT_SEED = 4, 0.9, 2000, 20260925


def reasons(row):
    """Top-K features pushing toward default; ties broken by feature index (stable sort)."""
    order = np.argsort(-row, kind="mergesort")
    return frozenset(int(i) for i in order[:K] if row[i] > 0)


def ordered(row):
    order = np.argsort(-row, kind="mergesort")
    return tuple(int(i) for i in order[:K] if row[i] > 0)


def rbo(a, b, p=P_RBO):
    ra, rb = np.argsort(-a, kind="mergesort"), np.argsort(-b, kind="mergesort")
    k = len(ra)
    sa, sb, s, X = set(), set(), 0.0, 0
    for d in range(1, k + 1):
        x, y = int(ra[d - 1]), int(rb[d - 1])
        if x == y:
            X += 1
        else:
            X += (x in sb) + (y in sa)
        sa.add(x); sb.add(y)
        s += (X / d) * p ** d
    return (X / k) * p ** k + (1 - p) / p * s


def load_cell(d, model, method):
    a = d / f"attr_{model}_{method}.npy"
    return (np.load(a), np.load(d / f"rows_{model}_{method}.npy")) if a.exists() else (None, None)


def compare(A, rowsA, B, rowsB, denied):
    ia = {int(r): i for i, r in enumerate(rowsA)}
    ib = {int(r): i for i, r in enumerate(rowsB)}
    idx = [int(r) for r in denied if int(r) in ia and int(r) in ib]
    a = np.stack([A[ia[r]] for r in idx]); b = np.stack([B[ib[r]] for r in idx])
    changed = np.array([reasons(x) != reasons(y) for x, y in zip(a, b)], dtype=float)
    ordm = np.mean([ordered(x) == ordered(y) for x, y in zip(a, b)])
    jac = np.mean([len(reasons(x) & reasons(y)) / max(1, len(reasons(x) | reasons(y)))
                   for x, y in zip(a, b)])
    rb = np.mean([rbo(x, y) for x, y in zip(a, b)])
    rng = np.random.RandomState(BOOT_SEED)
    boots = changed[rng.randint(0, len(changed), (NBOOT, len(changed)))].mean(axis=1)
    return {"n": len(idx), "R": float(changed.mean()),
            "R_ci": [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))],
            "ordered_match": float(ordm), "jaccard": float(jac), "rbo": float(rb),
            "max_abs_diff": float(np.abs(a - b).max())}


def main():
    res = {"prereg": "dc12f1a", "pairs": {}, "positive_control": {}}
    for o in LABELS:
        arch = ROOT / f"archive/{o}"
        am = json.load(open(arch / "manifest.json"))
        denied = {m: np.load(arch / f"denied_{m}.npy") for m in MODELS}
        # positive control: archived tree vs archived tree_altbg (different background)
        for m in MODELS:
            A, rA = load_cell(arch, m, "tree"); B, rB = load_cell(arch, m, "tree_altbg")
            res["positive_control"][f"{o}_{m}"] = (compare(A, rA, B, rB, denied[m])
                                                     if A is not None and B is not None
                                                     else "UNAVAILABLE")
        for c in LABELS:
            if c != o and year(c) <= year(o):
                continue
            d = ROOT / f"recompute/{o}_{c}"
            tag = "primary" if (o in PRIMARY and c in PRIMARY) else "secondary_A1"
            if not (d / "manifest.json").exists():
                res["pairs"][f"{o}_{c}"] = "MISSING"; continue
            cm = json.load(open(d / "manifest.json"))
            pair = {"delta": year(c) - year(o), "arm": tag, "load": cm["load"], "cells": {}}
            for m in MODELS:
                if cm["load"][m]["status"] != "ok":
                    for meth in METHODS:
                        pair["cells"][f"{m}_{meth}"] = {"status": "UNLOADABLE"}
                    continue
                if "predict" in cm["load"][m]:  # amendment A2: loaded, then failed on predict
                    for meth in METHODS:
                        pair["cells"][f"{m}_{meth}"] = {"status": "UNCOMPUTABLE", "stage": "predict",
                                                        "error": cm["load"][m]["predict"]}
                    continue
                pa, pc = np.load(arch / f"p_{m}.npy"), np.load(d / f"p_{m}.npy")
                new_denied = set(np.argsort(-pc, kind="mergesort")[:len(denied[m])].tolist())
                pair[f"{m}_pred"] = {"max_abs_dp": float(np.abs(pa - pc).max()),
                                     "denied_flips": int(len(set(denied[m].tolist()) ^ new_denied) // 2)}
                for meth in METHODS:
                    key = f"{m}_{meth}"
                    if am["cells"].get(key, {}).get("status") != "ok":
                        pair["cells"][key] = {"status": "ORIGIN_UNCOMPUTABLE"}; continue
                    if cm["cells"].get(key, {}).get("status") != "ok":
                        pair["cells"][key] = {"status": "UNCOMPUTABLE",
                                              "error": cm["cells"].get(key, {}).get("error")}
                        continue
                    A, rA = load_cell(arch, m, meth); B, rB = load_cell(d, m, meth)
                    pair["cells"][key] = {"status": "ok", **compare(A, rA, B, rB, denied[m])}
            res["pairs"][f"{o}_{c}"] = pair
    # excess over noise floor
    for key, pair in res["pairs"].items():
        if not isinstance(pair, dict):
            continue
        o, c = key.split("_")
        for ck, cell in pair["cells"].items():
            if cell.get("status") != "ok":
                continue
            floors = []
            for v in (o, c):
                rep = res["pairs"].get(f"{v}_{v}", {})
                rc = rep.get("cells", {}).get(ck, {}) if isinstance(rep, dict) else {}
                floors.append(rc)
            if all(f.get("status") == "ok" for f in floors):
                cell["R_repeat_max"] = max(f["R"] for f in floors)
                cell["R_repeat_ci_hi"] = max(f["R_ci"][1] for f in floors)
                cell["R_excess"] = cell["R"] - cell["R_repeat_max"]
    res["gate"] = gate(res)
    json.dump(res, open(ROOT / "results.json", "w"), indent=2)
    report(res)
    print("\nGATE (pre-reg §7, primary vintages, 1 <= delta <= 2):", json.dumps(res["gate"], indent=1))


def gate(res):
    """Pre-reg §7, evaluated mechanically on PRIMARY pairs with 1 <= delta <= 2."""
    pc = [v for v in res["positive_control"].values() if isinstance(v, dict)]
    if not pc or any(v["R"] == 0 for v in pc):
        return {"verdict": "VOID", "why": "positive control R == 0 somewhere (or unavailable everywhere)"}
    strong, weak, all_small, ambiguous = [], [], True, []
    for key, pair in res["pairs"].items():
        if not isinstance(pair, dict) or pair["arm"] != "primary" or not 1 <= pair["delta"] <= 2:
            continue
        for ck, cell in pair["cells"].items():
            st = cell.get("status")
            if st in ("UNLOADABLE", "UNCOMPUTABLE"):
                weak.append(f"{key}:{ck}:{st}"); all_small = False
            elif st == "ok":
                ex = cell.get("R_excess")
                if ex is None:
                    ambiguous.append(f"{key}:{ck}:no-noise-floor"); all_small = False; continue
                if ex >= 0.05 and cell["R_ci"][0] > cell["R_repeat_ci_hi"]:
                    strong.append(f"{key}:{ck}:R_excess={ex:.3f}")
                if ex >= 0.01:
                    all_small = False
                    if not (ex >= 0.05 and cell["R_ci"][0] > cell["R_repeat_ci_hi"]):
                        ambiguous.append(f"{key}:{ck}:R_excess={ex:.3f}")
    if strong:
        v = "STRONG_GO"
    elif weak:
        v = "WEAK_GO"
    elif all_small:
        v = "NO_GO"
    else:
        v = "AMBIGUOUS"
    return {"verdict": v, "strong": strong, "weak": weak, "ambiguous": ambiguous}


def report(res):
    print("POSITIVE CONTROL (tree vs tree w/ different background, R must be > 0):")
    for k, v in res["positive_control"].items():
        print(f"  {k}: " + (f"R={v['R']:.3f}" if isinstance(v, dict) else v))
    print("\npair         delta cell                 status        R      CI            excess  ordm  jac   rbo")
    for key, pair in res["pairs"].items():
        if not isinstance(pair, dict):
            print(key, pair); continue
        for ck, cell in pair["cells"].items():
            if cell.get("status") == "ok":
                ex = cell.get("R_excess")
                print(f"{key:12s} {pair['delta']:>3d}   {ck:20s} ok     {cell['R']:.3f} "
                      f"[{cell['R_ci'][0]:.3f},{cell['R_ci'][1]:.3f}] "
                      f"{'   n/a' if ex is None else f'{ex:+.3f}'}  {cell['ordered_match']:.2f}  "
                      f"{cell['jaccard']:.2f}  {cell['rbo']:.2f}")
            else:
                print(f"{key:12s} {pair['delta']:>3d}   {ck:20s} {cell['status']}")
        for m in MODELS:
            if f"{m}_pred" in pair:
                pp = pair[f"{m}_pred"]
                print(f"{key:12s}       {m} predictions: max|dP|={pp['max_abs_dp']:.2e} denied flips={pp['denied_flips']}")


if __name__ == "__main__":
    main()
