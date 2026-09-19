"""Condition (iii): library-version drift. Pre-reg bd47a9d, P1's actual bet.

Two phases, run under DIFFERENT shap versions:
  --emit     compute the decision-time original, save to .npz
  --compare  recompute from each record level, score against the saved original

R4 is the level that records lib_versions. A record at R4+ tells the examiner
which shap version ran; below R4 it does not. But knowing is not the same as
HAVING -- this cell measures what happens when the examiner recomputes in the
environment they actually have.
"""
import argparse, json, sys
import numpy as np

from metrics import full_report
from records import BindingRecord, current_environment
from recompute import ExaminerDefaults, recompute_attribution
from run_cells import build, collapse, tree_attribute, sampling_attribute, SEED, LEVELS

METHODS = {"TreeSHAP": (tree_attribute, 200), "SamplingSHAP": (sampling_attribute, 64)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit"); ap.add_argument("--compare"); ap.add_argument("--out")
    a = ap.parse_args()
    X_eval, X_ref, y_ref, operative, full_state, store = build()

    if a.emit:
        payload = {}
        for name, (fn, n) in METHODS.items():
            payload[name] = collapse(fn(operative, X_eval, store["bg://ref"],
                                        seed=SEED, n_samples=2048))[:n]
        np.savez(a.emit, **payload)
        json.dump(current_environment(), open(a.emit + ".env.json", "w"), default=str)
        print(f"emitted under shap {__import__('shap').__version__}", file=sys.stderr)
        return 0

    base = np.load(a.compare)
    orig_env = json.load(open(a.compare + ".env.json"))
    here = current_environment()
    results = {}
    for name, (fn, n) in METHODS.items():
        original = base[name]
        per = {}
        for lv in LEVELS:
            rec = BindingRecord.capture(lv, full_state)
            rc, prov = recompute_attribution(rec, store, X_eval, X_ref, y_ref, fn,
                                             defaults=ExaminerDefaults())
            per[lv] = {"report": full_report(original, collapse(rc)[:n]),
                       "provenance": prov, "record_bytes": rec.size_bytes()}
        results[name] = per

    out = {"study": "record-sufficiency", "cell": "condition_iii_library_drift",
           "prereg_ots_commit": "bd47a9d", "condition": "iii",
           "original_environment": orig_env, "recompute_environment": here,
           "shap_original": orig_env["lib_versions"]["shap"],
           "shap_recompute": here["lib_versions"]["shap"], "results": results}
    json.dump(out, open(a.out, "w"), indent=2, default=str)

    print(f"\n=== (iii) shap {out['shap_original']} -> {out['shap_recompute']} ===",
          file=sys.stderr)
    for m, per in results.items():
        print(f"--- {m} ---", file=sys.stderr)
        for lv, d in per.items():
            p = d["report"]["primary"]
            print(f"  {lv}: Jacc={p['mean_jaccard']:.4f} frac={p['fraction_reproducing']:.3f} "
                  f"L2={d['report']['secondary_l2']['mean']:.4f} "
                  f"{'SUFF' if p['SUFFICIENT'] else 'not-suff':>8}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
