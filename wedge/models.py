"""CART wrapper for the Rashomon wedge.

Each CartModel wraps a fitted sklearn DecisionTreeClassifier and adds:

  - per-case (T, F) emission from leaf class proportions
  - identification of the leaf the case lands in
  - the feature subset the model was fit on (so that downstream attribution
    can restrict its analysis to the model's features)

Decision-path walking and per-component attribution live in wedge.attribution,
not on CartModel itself.

For a binary classification leaf with class proportions (p_paid, p_charged):
  T = p_paid       (confidence in grant)
  F = p_charged    (concern; evidence supporting deny)

These satisfy T + F = 1 by construction in the wedge — see spec §7 for
why we accept this and what iteration 2's richer emission would do.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier


@dataclass
class CartModel:
    """A fitted CART with T/F emission helpers."""

    model_id: str
    tree: DecisionTreeClassifier
    feature_subset: tuple[str, ...]
    classes_: tuple[int, ...]  # sklearn's classes_, copied for clarity

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        return self.tree.predict(X[list(self.feature_subset)].to_numpy())

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        return self.tree.predict_proba(X[list(self.feature_subset)].to_numpy())

    def emit_for_case(self, case_features: dict[str, Any]) -> dict[str, Any]:
        """Return {'T', 'F', 'leaf', 'leaf_id'} for one case (a feature dict).

        T and F are leaf class proportions. leaf is a string label like
        "leaf_<node_id>"; leaf_id is the underlying integer node id.
        """
        x = np.asarray(
            [case_features[f] for f in self.feature_subset], dtype=float
        ).reshape(1, -1)
        leaf_id = int(self.tree.apply(x)[0])
        proba = self.tree.predict_proba(x)[0]  # in self.classes_ order
        # classes_ is sorted: 0 (paid) before 1 (charged_off) for our derive_label.
        class_order = list(self.classes_)
        if class_order == [0, 1]:
            t, f = float(proba[0]), float(proba[1])
        elif class_order == [1, 0]:
            t, f = float(proba[1]), float(proba[0])
        else:
            raise RuntimeError(
                f"unexpected class order {class_order!r}; wedge assumes binary 0/1"
            )
        return {"T": t, "F": f, "leaf": f"leaf_{leaf_id}", "leaf_id": leaf_id}


def fit_model(
    X: pd.DataFrame,
    y: pd.Series,
    *,
    model_id: str,
    max_depth: int,
    min_samples_leaf: int,
    feature_subset: tuple[str, ...],
    random_state: int = 0,
) -> CartModel:
    """Fit a single CART on the given data with the given hyperparameters.

    The feature_subset selects columns from X. Unused columns are ignored
    completely in fitting *and* in downstream emission.
    """
    cols = list(feature_subset)
    X_sub = X[cols].to_numpy()
    y_arr = y.to_numpy()
    tree = DecisionTreeClassifier(
        max_depth=max_depth,
        min_samples_leaf=min_samples_leaf,
        random_state=random_state,
    )
    tree.fit(X_sub, y_arr)
    return CartModel(
        model_id=model_id,
        tree=tree,
        feature_subset=tuple(cols),
        classes_=tuple(int(c) for c in tree.classes_),
    )
