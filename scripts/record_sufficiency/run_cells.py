"""Record levels R1-R5 x divergence conditions (i)-(iv). Pre-reg bd47a9d.

Conditions:
  (i)   same process, re-run
  (ii)  fresh process, same machine   [driver runs this file twice]
  (iii) different library minor version [driver swaps shap version]
  (iv)  different thread count / BLAS path
"""
import json, os, sys
import numpy as np
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier

from metrics import full_report
from records import BindingRecord, hash_obj, current_environment
from recompute import ExaminerDefaults, recompute_attribution, RecordInsufficient

SEED = 20260918
N_EVAL = 200
LEVELS = ["R1", "R2", "R3", "R4", "R5"]


def tree_attribute(model, X, background, seed=None, n_samples=None):
    import shap
    return shap.TreeExplainer(model).shap_values(X, check_additivity=False)


def sampling_attribute(model, X, background, seed=None, n_samples=2048):
    """Stochastic sampling explainer -- the seed/sampling axis actually bites here.

    NOTE (harness defect found 2026-09-19, worth reporting in the paper):
    `shap.SamplingExplainer.__init__` signature is `(self, model, data, **kwargs)`
    -- it has NO `seed` parameter. Passing seed=... is silently swallowed by
    **kwargs and ignored, so an earlier version of this harness reported every
    SamplingSHAP cell as unseeded while believing R5 was seeded. The RNG it
    actually consumes is the GLOBAL numpy random state.

    This is substantive, not incidental: the seed is not a parameter of the
    method, it is ambient process state. An institution intending to record
    "the seed" has nothing method-local to record, and a recomputation that
    sets a seed on the explainer gets no error and no effect. That is a
    record-design failure mode the paper should name.
    """
    import shap
    if seed is not None:
        np.random.seed(seed)
    nsub = min(64, X.shape[0])
    ex = shap.SamplingExplainer(model.predict_proba, background)
    return ex.shap_values(X[:nsub], nsamples=min(n_samples, 512), silent=True)


def collapse(a):
    a = np.asarray(a)
    return a[:, :, 1] if a.ndim == 3 else a


def build(condition_threads=None):
    rs = np.random.RandomState(SEED)
    X, y = make_classification(n_samples=2000, n_features=12, n_informative=6,
                               n_redundant=2, random_state=SEED)
    X_eval, X_ref, y_ref = X[:N_EVAL], X[N_EVAL:], y[N_EVAL:]
    operative = RandomForestClassifier(n_estimators=50, max_depth=6, random_state=SEED)
    operative.fit(X_ref, y_ref)

    # "current version under the same id" -- the retention scenario: the vendor
    # retired the operative model and something else now answers to that name.
    successor = RandomForestClassifier(n_estimators=120, max_depth=8, random_state=SEED + 1)
    successor.fit(X_ref, y_ref)

    full_state = {
        "case_id": "case-0001", "decision": "denied", "timestamp": "2026-09-18T06:00:00Z",
        "model_id": "rf-underwriting", "model_version": "1.0.0",
        "params_hash": hash_obj(operative.get_params()),
        "config_hash": hash_obj({"n_estimators": 50, "max_depth": 6}),
        "model_blob_ref": "blob://operative",
        "method": "TreeSHAP", "method_version": __import__("shap").__version__,
        "value_function": "interventional", "background_ref": "bg://ref",
        "background_size": 100, "sampling_params": {"n_samples": 2048},
        "seed": SEED, **current_environment(),
    }
    store = {"blob://operative": operative, "bg://ref": X_ref[:100],
             "rf-underwriting@current": successor}
    return X_eval, X_ref, y_ref, operative, full_state, store


def main():
    cond = os.environ.get("RS_CONDITION", "i")
    threads = os.environ.get("OMP_NUM_THREADS")
    X_eval, X_ref, y_ref, operative, full_state, store = build()

    results = {}
    for method_name, fn, n_rows in (("TreeSHAP", tree_attribute, N_EVAL),
                                    ("SamplingSHAP", sampling_attribute, 64)):
        # The ORIGINAL is the decision-time attribution: computed seeded, with
        # the operative model and background. Every recomputation is scored
        # against this.
        original = collapse(fn(operative, X_eval, store["bg://ref"], seed=SEED,
                               n_samples=2048))[:n_rows]
        # Guard: recomputing the original under identical conditions must return
        # it exactly. If this fails the comparison baseline is not stable and no
        # cell below means anything.
        _again = collapse(fn(operative, X_eval, store["bg://ref"], seed=SEED,
                             n_samples=2048))[:n_rows]
        baseline_stable = bool(np.allclose(original, _again))
        per_level = {}
        for lv in LEVELS:
            rec = BindingRecord.capture(lv, full_state)
            try:
                rc, prov = recompute_attribution(
                    rec, store, X_eval, X_ref, y_ref, fn,
                    defaults=ExaminerDefaults())
            except RecordInsufficient as e:
                per_level[lv] = {"error": str(e), "record_bytes": rec.size_bytes()}
                continue
            rep = full_report(original, collapse(rc)[:n_rows])
            per_level[lv] = {"report": rep, "provenance": prov,
                             "record_bytes": rec.size_bytes()}
        per_level["_baseline_stable"] = baseline_stable
        results[method_name] = per_level

    out = {"study": "record-sufficiency", "cell": f"condition_{cond}",
           "prereg_ots_commit": "bd47a9d", "condition": cond,
           "omp_threads": threads, "environment": current_environment(),
           "results": results}
    print(json.dumps(out, indent=2, default=str))

    for m, per in results.items():
        print(f"\n--- {m} (condition {cond}, threads={threads}) ---", file=sys.stderr)
        if per.get("_baseline_stable") is False:
            print("  *** BASELINE UNSTABLE -- cells below are void ***", file=sys.stderr)
        for lv, d in per.items():
            if lv.startswith("_"):
                continue
            if "error" in d:
                print(f"  {lv}: INSUFFICIENT-TO-ATTEMPT ({d['record_bytes']}B)", file=sys.stderr)
                continue
            p = d["report"]["primary"]
            print(f"  {lv}: Jacc={p['mean_jaccard']:.4f} frac={p['fraction_reproducing']:.3f} "
                  f"L2={d['report']['secondary_l2']['mean']:.4f} "
                  f"{'SUFF' if p['SUFFICIENT'] else 'not-suff':>8} "
                  f"route={d['provenance']['model_route']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
