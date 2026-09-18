"""R0 negative control -- pre-reg P5 (prior 0.99).

A record carrying only (case_id, decision, timestamp) identifies no model. The
examiner must refit a surrogate. If that "reproduces" the original attribution
under the frozen rank primary, the harness measures nothing and every other cell
is void.

This is the FIRST thing run, before any real substrate, deliberately.
"""
import json
import sys
import numpy as np
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier

from metrics import full_report
from records import BindingRecord, hash_array, hash_obj, current_environment
from recompute import ExaminerDefaults, recompute_attribution

SEED = 20260918
N_EVAL = 200


def tree_attribute(model, X, background, seed=None, n_samples=None):
    """Exact tree-path attribution. Deterministic given (model, X)."""
    import shap
    return shap.TreeExplainer(model).shap_values(X, check_additivity=False)


def collapse(a):
    """shap may return (n,f,classes) or a list per class -- take class 1."""
    a = np.asarray(a)
    if a.ndim == 3:
        return a[:, :, 1]
    return a


def main():
    rs = np.random.RandomState(SEED)
    X, y = make_classification(n_samples=2000, n_features=12, n_informative=6,
                               n_redundant=2, random_state=SEED)
    X_eval, X_ref, y_ref = X[:N_EVAL], X[N_EVAL:], y[N_EVAL:]

    operative = RandomForestClassifier(n_estimators=50, max_depth=6, random_state=SEED)
    operative.fit(X_ref, y_ref)

    original = collapse(tree_attribute(operative, X_eval, None))

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
    store = {"blob://operative": operative, "bg://ref": X_ref[:100]}

    def surrogate_factory(Xr, yr):
        """What an examiner with no model identity would fit: a plausible model."""
        m = RandomForestClassifier(n_estimators=50, max_depth=6,
                                   random_state=rs.randint(1 << 30))
        m.fit(Xr, yr)
        return m

    r0 = BindingRecord.capture("R0", full_state)
    recomputed, prov = recompute_attribution(
        r0, store, X_eval, X_ref, y_ref, tree_attribute,
        defaults=ExaminerDefaults(surrogate_model_factory=surrogate_factory))
    rep = full_report(original, collapse(recomputed))

    # R5 positive control: full record, exact model -- must reproduce.
    r5 = BindingRecord.capture("R5", full_state)
    recomputed5, prov5 = recompute_attribution(
        r5, store, X_eval, X_ref, y_ref, tree_attribute,
        defaults=ExaminerDefaults(surrogate_model_factory=surrogate_factory))
    rep5 = full_report(original, collapse(recomputed5))

    out = {
        "study": "record-sufficiency", "cell": "negative_control_R0_plus_R5_sanity",
        "prereg": "docs/superpowers/specs/2026-09-18-record-sufficiency-preregistration-note.md",
        "prereg_ots_commit": "bd47a9d", "seed": SEED, "n_eval": N_EVAL,
        "R0": {"provenance": prov, "report": rep, "record_bytes": r0.size_bytes()},
        "R5": {"provenance": prov5, "report": rep5, "record_bytes": r5.size_bytes()},
        "environment": current_environment(),
    }
    print(json.dumps(out, indent=2, default=str))

    p5_holds = not rep["primary"]["SUFFICIENT"]
    r5_ok = rep5["primary"]["SUFFICIENT"]
    print("\n" + "=" * 62, file=sys.stderr)
    print(f"P5 (R0 must NOT reproduce): {'HOLDS' if p5_holds else '*** VIOLATED ***'}",
          file=sys.stderr)
    print(f"  R0 mean top-5 Jaccard = {rep['primary']['mean_jaccard']:.4f} "
          f"(frac reproducing {rep['primary']['fraction_reproducing']:.3f})", file=sys.stderr)
    print(f"  R0 L2 mean            = {rep['secondary_l2']['mean']:.4f}", file=sys.stderr)
    print(f"  R0 record size        = {r0.size_bytes()} bytes", file=sys.stderr)
    print(f"R5 sanity (must reproduce): {'OK' if r5_ok else '*** HARNESS BROKEN ***'}",
          file=sys.stderr)
    print(f"  R5 mean top-5 Jaccard = {rep5['primary']['mean_jaccard']:.4f}", file=sys.stderr)
    print(f"  R5 record size        = {r5.size_bytes()} bytes", file=sys.stderr)
    print("=" * 62, file=sys.stderr)
    return 0 if (p5_holds and r5_ok) else 1


if __name__ == "__main__":
    raise SystemExit(main())
