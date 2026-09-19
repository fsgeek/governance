"""Arm G: record sufficiency on the LendingClub lending substrate.

Pre-reg bd47a9d section 2d. Arm B (synthetic benchmark) found TreeSHAP
deterministic from R2 up and SamplingSHAP sufficient only at R5. Arm G asks
whether that holds on the substrate the governance argument is actually about:
real underwriting features, a real credit decision, gradient-boosted trees
rather than a random forest.

Adds the model class the benchmark arm lacked: XGBoost, where histogram binning
and thread scheduling are plausible sources of the systems nondeterminism that
Arm B did not find.
"""
import json, os, sys
import numpy as np
import pandas as pd

from metrics import full_report
from records import BindingRecord, hash_obj, current_environment
from recompute import ExaminerDefaults, recompute_attribution

SEED = 20260918
N_TRAIN, N_EVAL = 40000, 200
LEVELS = ["R1", "R2", "R3", "R4", "R5"]
FEATURES = ["fico_range_low", "dti", "annual_inc", "loan_amnt", "term_months",
            "credit_age_months", "purpose_code"]


def load():
    cols = ["fico_range_low", "dti", "annual_inc", "loan_amnt", "term",
            "purpose", "loan_status", "issue_d", "earliest_cr_line", "grade"]
    df = pd.read_parquet("../../data/accepted_2007_to_2018Q4.parquet", columns=cols)
    df = df[df.loan_status.isin(["Fully Paid", "Charged Off", "Default"])].copy()
    df["y"] = (df.loan_status != "Fully Paid").astype(int)
    df["term_months"] = df.term.astype(str).str.extract(r"(\d+)").astype(float)
    iss = pd.to_datetime(df.issue_d, format="%b-%Y", errors="coerce")
    ecl = pd.to_datetime(df.earliest_cr_line, format="%b-%Y", errors="coerce")
    df["credit_age_months"] = (iss - ecl).dt.days / 30.44
    df["purpose_code"] = df.purpose.astype("category").cat.codes.astype(float)
    df = df.dropna(subset=FEATURES + ["y"])
    df = df.sample(n=min(N_TRAIN + N_EVAL, len(df)), random_state=SEED)
    X = df[FEATURES].to_numpy(dtype=np.float64)
    y = df["y"].to_numpy(dtype=int)
    return X[:N_EVAL], X[N_EVAL:], y[N_EVAL:]


def make_models(X_ref, y_ref):
    """Gradient boosting -- a different model class from Arm B's random forest.

    XGBoost was the first choice and is UNUSABLE here, which is itself a
    condition-(iii) datapoint worth reporting: shap 0.48.0 AND 0.49.1 both fail
    on xgboost 3.2.0 models with
        ValueError: could not convert string to float: '[1.98975E-1]'
    because xgboost now serializes `base_score` as a bracketed vector and shap's
    XGBTreeModelLoader still parses it as a scalar. A record that pinned model
    version, config, method and method version would be FULLY SUFFICIENT on
    paper and still not recomputable, because no available explainer version can
    read that model. Record sufficiency presupposes a working toolchain; the
    record cannot record that.
    """
    from sklearn.ensemble import GradientBoostingClassifier
    op = GradientBoostingClassifier(n_estimators=120, max_depth=5,
                                    learning_rate=0.1, random_state=SEED)
    op.fit(X_ref, y_ref)
    succ = GradientBoostingClassifier(n_estimators=300, max_depth=7,
                                      learning_rate=0.05, random_state=SEED + 1)
    succ.fit(X_ref, y_ref)
    return op, succ


def tree_attribute(model, X, background, seed=None, n_samples=None):
    import shap
    return shap.TreeExplainer(model).shap_values(X, check_additivity=False)


def sampling_attribute(model, X, background, seed=None, n_samples=2048):
    import shap
    if seed is not None:
        np.random.seed(seed)
    n = min(64, X.shape[0])
    return shap.SamplingExplainer(model.predict_proba, background).shap_values(
        X[:n], nsamples=min(n_samples, 512), silent=True)


def collapse(a):
    a = np.asarray(a)
    return a[:, :, 1] if a.ndim == 3 else a


def main():
    cond = os.environ.get("RS_CONDITION", "i")
    threads = os.environ.get("OMP_NUM_THREADS")
    X_eval, X_ref, y_ref = load()
    operative, successor = make_models(X_ref, y_ref)
    print(f"loaded: eval={X_eval.shape} ref={X_ref.shape} default_rate={y_ref.mean():.3f}",
          file=sys.stderr)

    full_state = {
        "case_id": "lc-0001", "decision": "priced", "timestamp": "2026-09-19T00:00:00Z",
        "model_id": "gbm-lc-underwriting", "model_version": "1.0.0",
        "params_hash": hash_obj(operative.get_params()),
        "config_hash": hash_obj({"n_estimators": 120, "max_depth": 5}),
        "model_blob_ref": "blob://operative",
        "method": "TreeSHAP", "method_version": __import__("shap").__version__,
        "value_function": "interventional", "background_ref": "bg://ref",
        "background_size": 100, "sampling_params": {"n_samples": 2048},
        "seed": SEED, **current_environment(),
    }
    store = {"blob://operative": operative, "bg://ref": X_ref[:100],
             "gbm-lc-underwriting@current": successor}

    results = {}
    for name, fn, n_rows in (("TreeSHAP", tree_attribute, N_EVAL),
                             ("SamplingSHAP", sampling_attribute, 64)):
        original = collapse(fn(operative, X_eval, store["bg://ref"], seed=SEED,
                               n_samples=2048))[:n_rows]
        again = collapse(fn(operative, X_eval, store["bg://ref"], seed=SEED,
                            n_samples=2048))[:n_rows]
        per = {"_baseline_stable": bool(np.allclose(original, again))}
        for lv in LEVELS:
            rec = BindingRecord.capture(lv, full_state)
            rc, prov = recompute_attribution(rec, store, X_eval, X_ref, y_ref, fn,
                                             defaults=ExaminerDefaults())
            per[lv] = {"report": full_report(original, collapse(rc)[:n_rows]),
                       "provenance": prov, "record_bytes": rec.size_bytes()}
        results[name] = per

    out = {"study": "record-sufficiency", "arm": "G_lendingclub",
           "cell": f"arm_g_condition_{cond}", "prereg_ots_commit": "bd47a9d",
           "condition": cond, "omp_threads": threads,
           "n_train": int(X_ref.shape[0]), "n_eval": int(X_eval.shape[0]),
           "features": FEATURES, "default_rate": float(y_ref.mean()),
           "environment": current_environment(), "results": results}
    print(json.dumps(out, indent=2, default=str))

    for m, per in results.items():
        print(f"\n--- Arm G {m} (cond {cond}, threads={threads}) ---", file=sys.stderr)
        if per.get("_baseline_stable") is False:
            print("  *** BASELINE UNSTABLE ***", file=sys.stderr)
        for lv, d in per.items():
            if lv.startswith("_"):
                continue
            p = d["report"]["primary"]
            print(f"  {lv}: Jacc={p['mean_jaccard']:.4f} frac={p['fraction_reproducing']:.3f} "
                  f"L2={d['report']['secondary_l2']['mean']:.5f} "
                  f"{'SUFF' if p['SUFFICIENT'] else 'not-suff':>8} "
                  f"route={d['provenance']['model_route']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
