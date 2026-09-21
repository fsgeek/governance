"""Stochastic-method generality: KernelSHAP and LIME alongside SamplingSHAP.

Pre-reg bd47a9d. "Stochastic methods are sufficient only at R5" currently rests
on ONE explainer. KernelSHAP samples coalitions and fits a weighted linear
model; LIME samples perturbations in a neighbourhood and fits its own local
model -- a different mechanism. If the seed is sufficient for all three, the
one-field claim generalises. If LIME needs more, the claim is method-indexed.

Also adds the randomized null baseline Hwang et al. use, which our R0
surrogate-refit control lacks: what Jaccard do two INDEPENDENT random rankings
of the same feature count produce? Every cell should be read against it.
"""
import json, os, sys
import numpy as np

from metrics import full_report, topk_jaccard, PRIMARY_K
from records import BindingRecord, hash_obj, current_environment
from recompute import ExaminerDefaults, recompute_attribution

SEED = 20260918
LEVELS = ["R1", "R2", "R3", "R4", "R5"]
N_EXPLAIN = 40


def random_null_jaccard(n_feat, k=PRIMARY_K, trials=20000, rng=None):
    """E[top-k Jaccard] for two independent uniform-random rankings.

    The principled reference point Hwang et al. derive. A cell scoring near this
    is indistinguishable from noise; a cell well above it is not necessarily
    'reproducing' -- it just is not random.
    """
    rng = rng or np.random.RandomState(0)
    a = np.argsort(rng.rand(trials, n_feat), axis=1)[:, :k]
    b = np.argsort(rng.rand(trials, n_feat), axis=1)[:, :k]
    inter = np.array([len(set(x) & set(y)) for x, y in zip(a, b)])
    return float((inter / (2 * k - inter)).mean())


def kernel_attribute(model, X, background, seed=None, n_samples=2048):
    import shap
    if seed is not None:
        np.random.seed(seed)
    n = min(N_EXPLAIN, X.shape[0])
    ex = shap.KernelExplainer(model.predict_proba, background)
    v = ex.shap_values(X[:n], nsamples=min(n_samples, 256), silent=True)
    return v


def lime_attribute(model, X, background, seed=None, n_samples=2048):
    from lime.lime_tabular import LimeTabularExplainer
    if seed is not None:
        np.random.seed(seed)
    n = min(N_EXPLAIN, X.shape[0])
    ex = LimeTabularExplainer(background, mode="classification",
                              discretize_continuous=False,
                              random_state=seed if seed is not None else None)
    out = np.zeros((n, X.shape[1]))
    for i in range(n):
        e = ex.explain_instance(X[i], model.predict_proba,
                                num_features=X.shape[1],
                                num_samples=min(n_samples, 500))
        for fidx, w in e.as_map()[1]:
            out[i, fidx] = w
    return out


def collapse(a):
    a = np.asarray(a)
    return a[:, :, 1] if a.ndim == 3 else a


def main():
    from run_arm_g import load, make_models, FEATURES
    cond = os.environ.get("RS_CONDITION", "i")
    X_eval, X_ref, y_ref = load()
    operative, successor = make_models(X_ref, y_ref)
    bg = X_ref[:50]

    null_j = random_null_jaccard(len(FEATURES))
    print(f"random-null top-{PRIMARY_K} Jaccard for {len(FEATURES)} features = {null_j:.4f}",
          file=sys.stderr)

    full_state = {
        "case_id": "lc-0001", "decision": "priced", "timestamp": "2026-09-19T00:00:00Z",
        "model_id": "gbm-lc-underwriting", "model_version": "1.0.0",
        "params_hash": hash_obj(operative.get_params()),
        "config_hash": hash_obj({"n_estimators": 120, "max_depth": 5}),
        "model_blob_ref": "blob://operative",
        "method": "varies", "method_version": __import__("shap").__version__,
        "value_function": "interventional", "background_ref": "bg://ref",
        "background_size": 50, "sampling_params": {"n_samples": 2048},
        "seed": SEED, **current_environment(),
    }
    store = {"blob://operative": operative, "bg://ref": bg,
             "gbm-lc-underwriting@current": successor}

    results = {"_random_null_jaccard": null_j}
    for name, fn in (("KernelSHAP", kernel_attribute), ("LIME", lime_attribute)):
        print(f"\n=== {name} ===", file=sys.stderr)
        original = collapse(fn(operative, X_eval, bg, seed=SEED, n_samples=2048))
        again = collapse(fn(operative, X_eval, bg, seed=SEED, n_samples=2048))
        stable = bool(np.allclose(original, again))
        per = {"_baseline_stable": stable}
        print(f"  baseline stable under identical conditions: {stable}", file=sys.stderr)
        for lv in LEVELS:
            rec = BindingRecord.capture(lv, full_state)
            rc, prov = recompute_attribution(rec, store, X_eval, X_ref, y_ref, fn,
                                             defaults=ExaminerDefaults())
            rep = full_report(original, collapse(rc))
            per[lv] = {"report": rep, "provenance": prov,
                       "record_bytes": rec.size_bytes()}
            p = rep["primary"]
            print(f"  {lv}: Jacc={p['mean_jaccard']:.4f} frac={p['fraction_reproducing']:.3f} "
                  f"L2={rep['secondary_l2']['mean']:.5f} "
                  f"{'SUFF' if p['SUFFICIENT'] else 'not-suff':>8} "
                  f"(null={null_j:.3f})", file=sys.stderr)
        results[name] = per

    out = {"study": "record-sufficiency", "arm": "G_methods",
           "cell": f"stochastic_methods_condition_{cond}",
           "prereg_ots_commit": "bd47a9d", "condition": cond,
           "n_explain": N_EXPLAIN, "features": FEATURES,
           "random_null_jaccard": null_j,
           "environment": current_environment(), "results": results}
    print(json.dumps(out, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
