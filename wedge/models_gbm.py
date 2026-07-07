"""Monotone-constrained gradient-boosted model family for the Rashomon wedge.

The deployable class named in the 2026-05-07 design spec §5 as CART's successor
("closer to what Rudin's group publishes"). used_features() = features that
appear in any split across the ensemble — the GBM analog of tree split-usage.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier


@dataclass
class MonotoneGBMModel:
    model_id: str
    estimator: HistGradientBoostingClassifier
    feature_subset: tuple[str, ...]
    classes_: tuple[int, ...]

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        return self.estimator.predict(X[list(self.feature_subset)].to_numpy())

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        return self.estimator.predict_proba(X[list(self.feature_subset)].to_numpy())

    def used_features(self) -> set[str]:
        names = list(self.feature_subset)
        used: set[str] = set()
        # _predictors is a list (per boosting iteration) of lists (per class) of
        # TreePredictor; each has .nodes with a 'feature_idx' field for split nodes
        # ('is_leaf' == 0). This is the documented internal structure for
        # HistGradientBoosting; guarded so a sklearn change degrades to "all used".
        try:
            for iteration in self.estimator._predictors:
                for predictor in iteration:
                    nodes = predictor.nodes
                    for node in nodes:
                        if not node["is_leaf"]:
                            used.add(names[int(node["feature_idx"])])
        except (AttributeError, KeyError, IndexError):
            return set(names)
        return used


def fit_monotone_gbm(
    X: pd.DataFrame, y: pd.Series, *, model_id: str,
    feature_subset: tuple[str, ...],
    monotonic_cst: Optional[dict[str, int]] = None,
    max_iter: int = 100, random_state: int = 0,
) -> MonotoneGBMModel:
    cols = list(feature_subset)
    cst = None
    if monotonic_cst is not None:
        cst = [int(monotonic_cst.get(c, 0)) for c in cols]
    est = HistGradientBoostingClassifier(
        max_iter=max_iter, monotonic_cst=cst, random_state=random_state,
    )
    est.fit(X[cols].to_numpy(), y.to_numpy())
    return MonotoneGBMModel(
        model_id=model_id, estimator=est, feature_subset=tuple(cols),
        classes_=tuple(int(c) for c in est.classes_),
    )
