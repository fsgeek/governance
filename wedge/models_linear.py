"""Sparse (L1-logistic) model family for the Rashomon wedge.

This is the LDA-search standard hypothesis class (Gillis/Meursault/Ustun search
over linear classifiers). used_features() = features with a nonzero coefficient,
the linear analog of "the tree splits on it".
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression


@dataclass
class SparseLinearModel:
    model_id: str
    estimator: LogisticRegression
    feature_subset: tuple[str, ...]
    classes_: tuple[int, ...]

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        return self.estimator.predict(X[list(self.feature_subset)].to_numpy())

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        return self.estimator.predict_proba(X[list(self.feature_subset)].to_numpy())

    def used_features(self) -> set[str]:
        coef = np.ravel(self.estimator.coef_)
        names = list(self.feature_subset)
        return {names[i] for i in range(len(names)) if abs(coef[i]) > 1e-8}


def fit_sparse_linear(
    X: pd.DataFrame, y: pd.Series, *, model_id: str, C: float,
    feature_subset: tuple[str, ...], random_state: int = 0,
) -> SparseLinearModel:
    cols = list(feature_subset)
    est = LogisticRegression(
        penalty="l1", solver="liblinear", C=C, random_state=random_state,
    )
    est.fit(X[cols].to_numpy(), y.to_numpy())
    return SparseLinearModel(
        model_id=model_id, estimator=est, feature_subset=tuple(cols),
        classes_=tuple(int(c) for c in est.classes_),
    )
