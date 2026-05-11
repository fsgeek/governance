"""Outcome surprise model S (spec §5.2).

The surprise model is a calibrated probability model trained on a
lifecycle-completed cohort (different from the wedge's target vintage) that
predicts P(grant | origination_features). Its purpose is to detect signal
the policy-constrained dual-set models may have *missed*: cases where the
surprise model and the wedge models disagree on the predicted outcome are
candidates for retrospective set revision (spec §5; Task 7).

Under the grant-as-positive convention (spec §2.7 OD-9a / OD-13):
  - predicted P(grant) is `predict_proba()[:, label=1 column]`.
  - outcome_surprise = realized_label - predicted_p_grant.
    Positive surprise: case got a *better* outcome than predicted.
    Negative surprise: case got a *worse* outcome than predicted.
  - |outcome_surprise| is the natural weight for set revision (spec §5.3):
    cases where the original model's predicted probability diverged most
    from the realized outcome get the highest weight under L_T' / L_F'.

The surprise model is intentionally NOT policy-constrained — its job is to
flag where the policy-respecting models may have been blind. (Protected-class
proxies remain excluded from its feature set by data hygiene; the bank's
policy YAML names these and the data loader enforces.)

V1 default: scikit-learn GradientBoostingClassifier with isotonic calibration
(CalibratedClassifierCV). The choice is named here, not in code consumer
sites, so the surprise-model class can be swapped without touching the
dual-set construction pipeline.
"""

from __future__ import annotations

from typing import Union

import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import GradientBoostingClassifier


_ArrayLike = Union[float, np.ndarray, pd.Series]


def train_surprise_model(
    X: pd.DataFrame,
    y: pd.Series,
    *,
    random_state: int = 0,
    n_estimators: int = 100,
    max_depth: int = 3,
    calibration_cv: int = 5,
):
    """Fit a calibrated probability model on a lifecycle-completed cohort.

    Returns the trained calibrator (a CalibratedClassifierCV wrapping a
    GradientBoostingClassifier base). The caller queries `predict_proba(X)`
    or `predict_p_grant(model, X)` to extract P(grant).

    Parameters
    ----------
    X : DataFrame of origination features.
    y : Series of binary labels (grant-as-positive: 1=grant, 0=deny).
    random_state : seed for both the base estimator and the calibration CV.
    n_estimators, max_depth : passed to GradientBoostingClassifier.
    calibration_cv : K for CalibratedClassifierCV's stratified split.
    """
    base = GradientBoostingClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        random_state=random_state,
    )
    model = CalibratedClassifierCV(
        base, method="isotonic", cv=calibration_cv
    )
    model.fit(X, y)
    return model


def predict_p_grant(model, X: pd.DataFrame) -> np.ndarray:
    """Return P(grant | x) = P(label=1 | x) for each row of X.

    Convention: grant-as-positive (spec §2.7 OD-9a / OD-13). sklearn's
    `classes_` is sorted, so for binary {0, 1} the grant column is index 1.
    Defensive lookup against `model.classes_` to handle reorderings.
    """
    proba = model.predict_proba(X)
    classes = list(model.classes_)
    grant_idx = classes.index(1)
    return np.asarray(proba[:, grant_idx])


def compute_outcome_surprise(
    *,
    p_grant: _ArrayLike,
    realized_label: _ArrayLike,
) -> _ArrayLike:
    """Per-case outcome surprise: `realized_label - p_grant`.

    Scalar and array-like inputs both supported (broadcast via numpy). For
    arrays, returns a numpy array of the same shape; for scalar inputs,
    returns a scalar float.

    Positive surprise (realized > predicted) means the case got a *better*
    outcome than the surprise model predicted. Negative surprise means
    *worse*. The magnitude |surprise| is bounded in [0, 1].
    """
    p_arr = np.asarray(p_grant)
    if np.any(p_arr < 0.0) or np.any(p_arr > 1.0):
        raise ValueError(
            "p_grant must be a probability in [0, 1]; got values outside that "
            f"range (min={float(np.min(p_arr))}, max={float(np.max(p_arr))})."
        )
    return np.asarray(realized_label) - p_arr
