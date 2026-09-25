"""Archive or recompute explanations inside ONE vintage env (pre-reg dc12f1a §4).

  archive   <vintage> <outdir>                 train M1/M2 in this vintage, store models + attributions
  recompute <vintage> <archivedir> <outdir>    load ONLY files from archivedir, recompute, store

Must run unchanged on Python 3.9 / sklearn 0.24 / shap 0.39 through Python 3.14 / shap 0.52,
so: no 3.10+ syntax, explicit arguments everywhere the pre-reg names one, and every failure is
caught and recorded as a status rather than crashing the cell.
"""
import json
import os
import pickle
import platform
import sys
import time
import traceback
from pathlib import Path

import numpy as np

SEED = 20260925
FRAME = Path(__file__).resolve().parents[2] / "runs/retention_drift/frame"
METHODS = ["tree", "tree_altbg", "kernel_pinned", "kernel_default", "lime"]


def versions():
    v = {"python": platform.python_version()}
    for m in ["shap", "sklearn", "xgboost", "numpy", "scipy", "lime"]:
        try:
            v[m] = __import__(m).__version__
        except Exception as e:  # noqa
            v[m] = "ERR " + repr(e)[:80]
    return v


def load_frame():
    g = lambda n: np.load(FRAME / (n + ".npy"))
    return g("X_train"), g("y_train"), g("X_eval"), g("background"), g("background_alt")


def train(X, y):
    from sklearn.ensemble import GradientBoostingClassifier
    import xgboost as xgb
    m1 = GradientBoostingClassifier(n_estimators=200, max_depth=3, learning_rate=0.1,
                                    random_state=SEED).fit(X, y)
    m2 = xgb.XGBClassifier(n_estimators=200, max_depth=4, learning_rate=0.1, tree_method="hist",
                           random_state=SEED, use_label_encoder=False, eval_metric="logloss") \
        if _xgb_major() < 2 else \
        xgb.XGBClassifier(n_estimators=200, max_depth=4, learning_rate=0.1, tree_method="hist",
                          random_state=SEED, eval_metric="logloss")
    m2.fit(X, y)
    return {"gbc": m1, "xgb": m2}


def _xgb_major():
    import xgboost as xgb
    return int(xgb.__version__.split(".")[0])


def save_models(models, d):
    with open(d / "gbc.pkl", "wb") as f:
        pickle.dump(models["gbc"], f)
    models["xgb"].save_model(str(d / "xgb.json"))
    with open(d / "xgb.pkl", "wb") as f:
        pickle.dump(models["xgb"], f)


def load_models(d):
    """Returns {model: obj or None}, {model: status/detail}.

    pickle.load is deliberate: whether sklearn's documented persistence format survives the
    library moving is the thing under test. The archive is our own, written by archive mode.
    """
    out, st = {}, {}
    try:
        with open(d / "gbc.pkl", "rb") as f:
            out["gbc"] = pickle.load(f)
        st["gbc"] = {"status": "ok", "path": "pickle"}
    except Exception as e:
        out["gbc"] = None
        st["gbc"] = {"status": "UNLOADABLE", "path": "pickle", "error": repr(e)[:400]}
    import xgboost as xgb
    try:
        m = xgb.XGBClassifier()
        m.load_model(str(d / "xgb.json"))
        out["xgb"] = m
        st["xgb"] = {"status": "ok", "path": "json"}
    except Exception as e:
        st["xgb"] = {"status": "UNLOADABLE", "path": "json", "error": repr(e)[:400]}
        out["xgb"] = None
    try:  # secondary path, recorded only
        with open(d / "xgb.pkl", "rb") as f:
            pickle.load(f)
        st["xgb"]["pickle_secondary"] = "ok"
    except Exception as e:
        st["xgb"]["pickle_secondary"] = "FAIL " + repr(e)[:200]
    return out, st


def p_default(model, X):
    return model.predict_proba(X)[:, 1]


def run_method(method, model, X_eval, denied_idx, X_train, bg, bg_alt):
    """Returns (attr array aligned to rows explained, rows explained) or raises."""
    import shap
    if method in ("tree", "tree_altbg"):
        data = bg if method == "tree" else bg_alt
        ex = shap.TreeExplainer(model, data=data, feature_perturbation="interventional")
        sv = ex.shap_values(X_eval)
        if isinstance(sv, list):  # older binary-classifier API
            sv = sv[1] if len(sv) == 2 else sv[0]
        sv = np.asarray(sv)
        if sv.ndim == 3:
            sv = sv[..., 1]
        return sv, np.arange(len(X_eval))
    Xd = X_eval[denied_idx]
    if method.startswith("kernel"):
        f = lambda Z: model.predict_proba(Z)[:, 1]
        ex = shap.KernelExplainer(f, bg[:50])
        np.random.seed(SEED)
        if method == "kernel_pinned":
            sv = ex.shap_values(Xd, nsamples=2048, l1_reg=False, silent=True)
        else:
            sv = ex.shap_values(Xd, nsamples=2048, silent=True)
        sv = np.asarray(sv)
        if sv.ndim == 3:
            sv = sv[..., 0]
        return sv, denied_idx
    if method == "lime":
        from lime.lime_tabular import LimeTabularExplainer
        ex = LimeTabularExplainer(X_train, mode="classification", discretize_continuous=True,
                                  random_state=SEED)
        k = X_train.shape[1]
        rows = []
        for x in Xd:
            e = ex.explain_instance(x, model.predict_proba, num_features=k, num_samples=5000,
                                    labels=(1,))
            w = np.zeros(k)
            for fi, wt in e.as_map()[1]:
                w[fi] = wt
            rows.append(w)
        return np.vstack(rows), denied_idx
    raise ValueError(method)


def explain_all(models, d, X_train, X_eval, bg, bg_alt, denied, manifest):
    for mname, model in models.items():
        if model is None:
            continue
        p = p_default(model, X_eval)
        np.save(d / f"p_{mname}.npy", p)
        for method in METHODS:
            key = f"{mname}_{method}"
            t0 = time.time()
            try:
                sv, rows = run_method(method, model, X_eval, denied[mname], X_train, bg, bg_alt)
                np.save(d / f"attr_{key}.npy", sv)
                np.save(d / f"rows_{key}.npy", rows)
                manifest["cells"][key] = {"status": "ok", "secs": round(time.time() - t0, 1)}
            except Exception as e:
                manifest["cells"][key] = {"status": "UNCOMPUTABLE", "error": repr(e)[:400],
                                          "trace": traceback.format_exc()[-800:]}
            print(key, manifest["cells"][key]["status"], flush=True)


def main():
    mode, vintage = sys.argv[1], sys.argv[2]
    X_train, y_train, X_eval, bg, bg_alt = load_frame()
    manifest = {"mode": mode, "vintage": vintage, "versions": versions(), "prereg": "dc12f1a",
                "omp_threads": os.environ.get("OMP_NUM_THREADS"), "cells": {}}
    if mode == "archive":
        out = Path(sys.argv[3]); out.mkdir(parents=True, exist_ok=True)
        models = train(X_train, y_train)
        save_models(models, out)
        denied = {}
        for m, model in models.items():
            p = p_default(model, X_eval)
            denied[m] = np.sort(np.argsort(-p, kind="mergesort")[:int(0.2 * len(p))])
            np.save(out / f"denied_{m}.npy", denied[m])
        manifest["load"] = {"gbc": {"status": "trained"}, "xgb": {"status": "trained"}}
        explain_all(models, out, X_train, X_eval, bg, bg_alt, denied, manifest)
    else:
        arch, out = Path(sys.argv[3]), Path(sys.argv[4]); out.mkdir(parents=True, exist_ok=True)
        models, st = load_models(arch)
        manifest["load"] = st
        manifest["origin"] = json.load(open(arch / "manifest.json"))["vintage"]
        denied = {m: np.load(arch / f"denied_{m}.npy") for m in ("gbc", "xgb")}
        explain_all(models, out, X_train, X_eval, bg, bg_alt, denied, manifest)
    json.dump(manifest, open(out / "manifest.json", "w"), indent=2)


if __name__ == "__main__":
    main()
