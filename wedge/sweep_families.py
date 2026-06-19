"""Multi-family hyperparameter sweep producing commensurable SweepResults.

All families share one inner_split holdout (so holdout_auc is comparable
across families) and emit the same SweepResult shape, so the existing
evaluate_policy / filter_to_epsilon / select_diverse_members core consumes
them unchanged.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

from wedge.models import fit_model
from wedge.models_gbm import fit_monotone_gbm
from wedge.models_linear import fit_sparse_linear
from wedge.rashomon import HyperparameterSpec, SweepConfig, SweepResult, inner_split


def _score(model, X_holdout, y_holdout) -> tuple[float, np.ndarray, np.ndarray]:
    proba = model.predict_proba(X_holdout)[:, list(model.classes_).index(1)]
    auc = float(roc_auc_score(y_holdout, proba))
    y_pred = model.predict(X_holdout)
    return auc, np.asarray(y_holdout), y_pred


def sweep_family(
    X: pd.DataFrame, y: pd.Series, *, family: str, grid: dict,
    feature_subsets, random_state: int = 0, holdout_fraction: float = 0.3,
    monotonic_cst: dict | None = None,
) -> list[SweepResult]:
    cfg = SweepConfig(max_depths=(), min_samples_leafs=(), feature_subsets=(),
                      random_state=random_state, holdout_fraction=holdout_fraction)
    X_fit, X_holdout, y_fit, y_holdout = inner_split(X, y, config=cfg)
    results: list[SweepResult] = []

    for si, subset in enumerate(feature_subsets):
        if family == "cart":
            for depth in grid["max_depths"]:
                for leaf_min in grid["min_samples_leafs"]:
                    m = fit_model(X_fit, y_fit, model_id=f"cart_d{depth}_l{leaf_min}_s{si}",
                                  max_depth=depth, min_samples_leaf=leaf_min,
                                  feature_subset=subset, random_state=random_state)
                    auc, yt, yp = _score(m, X_holdout, y_holdout)
                    results.append(SweepResult(
                        spec=HyperparameterSpec(depth, leaf_min, subset),
                        holdout_auc=auc, fitted_model=m, holdout_y_true=yt, holdout_y_pred=yp))
        elif family == "linear":
            for C in grid["Cs"]:
                m = fit_sparse_linear(X_fit, y_fit, model_id=f"lin_C{C}_s{si}",
                                      C=C, feature_subset=subset, random_state=random_state)
                auc, yt, yp = _score(m, X_holdout, y_holdout)
                # depth/leaf are tree-only; record 0 so the spec key stays valid.
                results.append(SweepResult(
                    spec=HyperparameterSpec(0, 0, subset),
                    holdout_auc=auc, fitted_model=m, holdout_y_true=yt, holdout_y_pred=yp))
        elif family == "gbm":
            for it in grid["max_iters"]:
                m = fit_monotone_gbm(X_fit, y_fit, model_id=f"gbm_it{it}_s{si}",
                                     feature_subset=subset, monotonic_cst=monotonic_cst,
                                     max_iter=it, random_state=random_state)
                auc, yt, yp = _score(m, X_holdout, y_holdout)
                results.append(SweepResult(
                    spec=HyperparameterSpec(0, 0, subset),
                    holdout_auc=auc, fitted_model=m, holdout_y_true=yt, holdout_y_pred=yp))
        else:
            raise ValueError(f"unknown family {family!r}; expected cart|linear|gbm")
    return results
