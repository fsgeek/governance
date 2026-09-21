"""Is 'sufficient at R2' circular? Test: serialize, kill, reload, recompute.

The objection: the harness resolves R2+ by pulling the SAME in-memory object
out of a dict, so 'sufficiency' may be 'we kept the model' dressed as a result.

The honest test is whether a model RECONSTRUCTED from a persisted artifact --
what an institution would actually retain -- reproduces the attribution. That is
what the binding record points AT. If reload->recompute diverges, R2 sufficiency
is an artifact of holding a live object and the finding collapses.

Also tests whether REFITTING with identical hyperparameters and seed suffices,
which is what an institution that recorded config-but-not-weights could do.
"""
import pickle, subprocess, sys, json, os
import numpy as np
from metrics import full_report

SEED = 20260918
HERE = os.path.dirname(os.path.abspath(__file__))


def phase_emit(path):
    from run_arm_g import load, make_models
    X_eval, X_ref, y_ref = load()
    op, _ = make_models(X_ref, y_ref)
    import shap
    orig = np.asarray(shap.TreeExplainer(op).shap_values(X_eval, check_additivity=False))
    if orig.ndim == 3: orig = orig[:, :, 1]
    with open(path, "wb") as fh:
        pickle.dump({"model": op, "X_eval": X_eval, "X_ref": X_ref,
                     "y_ref": y_ref, "orig": orig}, fh)
    print(f"emitted {orig.shape}", file=sys.stderr)


def phase_reload(path):
    """Fresh process, fresh interpreter: unpickle and recompute."""
    import shap
    d = pickle.load(open(path, "rb"))
    v = np.asarray(shap.TreeExplainer(d["model"]).shap_values(
        d["X_eval"], check_additivity=False))
    if v.ndim == 3: v = v[:, :, 1]
    rep = full_report(d["orig"], v)
    print(json.dumps({"arm": "reload_from_pickle", "report": rep}), flush=True)


def phase_refit(path):
    """Refit from recorded hyperparameters + seed, then recompute.

    This is the R2-minus case: the institution recorded config and seed but not
    the weights. If refit reproduces, weights need not be retained and the
    record shrinks further. If it does not, weight retention is load-bearing.
    """
    import shap
    from sklearn.ensemble import GradientBoostingClassifier
    d = pickle.load(open(path, "rb"))
    m = GradientBoostingClassifier(n_estimators=120, max_depth=5,
                                   learning_rate=0.1, random_state=SEED)
    m.fit(d["X_ref"], d["y_ref"])
    v = np.asarray(shap.TreeExplainer(m).shap_values(d["X_eval"],
                                                     check_additivity=False))
    if v.ndim == 3: v = v[:, :, 1]
    rep = full_report(d["orig"], v)
    ident = bool(np.allclose(
        m.predict_proba(d["X_eval"]), d["model"].predict_proba(d["X_eval"])))
    print(json.dumps({"arm": "refit_from_config_and_seed",
                      "predictions_identical": ident, "report": rep}), flush=True)


if __name__ == "__main__":
    ph, path = sys.argv[1], sys.argv[2]
    {"emit": phase_emit, "reload": phase_reload, "refit": phase_refit}[ph](path)
