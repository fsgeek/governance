"""Path-walk and per-component factor-support extraction.

For a fitted CART and a single case, walk the path from root to the
case's leaf, attribute information gain at each split to whichever
component (T or F) the chosen branch supports, and aggregate per-feature
to produce factor_support_T and factor_support_F.

Per-component split logic (spec §8 step 4):
  At each split, compare grant-purity and deny-purity of the chosen
  branch's subtree against the unchosen branch's subtree.
    - chosen_grant > unchosen_grant => attribute info gain to factor_support_T
    - chosen_deny  > unchosen_deny  => attribute info gain to factor_support_F
    - both         => attribute to both
    - neither      => attribute to neither (split is informational but
                      doesn't differentiate the components for this case).

This yields per-component differentiation: a feature can be in T-support
for one case (it routed the case toward grant-confident territory) and in
F-support for another case (it routed away from grant-confident territory).
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

import numpy as np

from wedge.models import CartModel
from wedge.types import FactorSupportEntry


# Class-index assumption: classes_ == (0, 1) so column 0 is the adverse
# outcome (label=0; deny-purity) and column 1 is the favorable outcome
# (label=1; grant-purity). Convention is grant-as-positive (label=1 ⇔ grant)
# per spec §2.7 OD-9a / OD-13; CartModel guarantees the (0, 1) ordering in
# fit_model because sklearn sorts classes_.
GRANT_CLASS_IDX = 1
DENY_CLASS_IDX = 0


def _subtree_purity(tree, node_id: int) -> tuple[float, float]:
    """Return (grant_purity, deny_purity) of all training samples reaching the
    subtree rooted at `node_id`. Computed from sklearn's tree.value array."""
    # tree.value has shape (n_nodes, 1, n_classes) and stores class-count per node.
    counts = tree.value[node_id, 0]
    total = counts.sum()
    if total == 0:
        return 0.0, 0.0
    grant = float(counts[GRANT_CLASS_IDX] / total)
    deny = float(counts[DENY_CLASS_IDX] / total)
    return grant, deny


def _node_info_gain(tree, node_id: int) -> float:
    """Information gain (impurity reduction) at a split node, weighted by the
    fraction of training samples reaching the node. Uses sklearn's stored
    impurity values."""
    if tree.children_left[node_id] == tree.children_right[node_id]:
        return 0.0
    parent_impurity = float(tree.impurity[node_id])
    n_parent = float(tree.n_node_samples[node_id])
    left = int(tree.children_left[node_id])
    right = int(tree.children_right[node_id])
    n_left = float(tree.n_node_samples[left])
    n_right = float(tree.n_node_samples[right])
    weighted_child = (
        (n_left / n_parent) * float(tree.impurity[left])
        + (n_right / n_parent) * float(tree.impurity[right])
    )
    gain = parent_impurity - weighted_child
    n_total = float(tree.n_node_samples[0])
    # Weight by fraction of training samples reaching this node.
    return gain * (n_parent / n_total)


def walk_path(model: CartModel, case_features: dict[str, Any]) -> list[dict[str, Any]]:
    """Walk root-to-leaf for one case, returning a list of split-decision dicts."""
    if model.classes_ != (0, 1):
        raise ValueError(
            f"attribution requires CartModel.classes_ == (0, 1); got {model.classes_!r}"
        )
    feature_names = list(model.feature_subset)
    x = np.asarray([case_features[f] for f in feature_names], dtype=float).reshape(1, -1)
    tree = model.tree.tree_
    node_id = 0
    path: list[dict[str, Any]] = []
    while tree.children_left[node_id] != tree.children_right[node_id]:  # internal node
        feat_idx = int(tree.feature[node_id])
        threshold = float(tree.threshold[node_id])
        feat_name = feature_names[feat_idx]
        x_val = float(x[0, feat_idx])
        if x_val <= threshold:
            chosen = int(tree.children_left[node_id])
            unchosen = int(tree.children_right[node_id])
            direction = "left"
        else:
            chosen = int(tree.children_right[node_id])
            unchosen = int(tree.children_left[node_id])
            direction = "right"
        chosen_grant, chosen_deny = _subtree_purity(tree, chosen)
        unchosen_grant, unchosen_deny = _subtree_purity(tree, unchosen)
        path.append({
            "feature": feat_name,
            "threshold": threshold,
            "direction": direction,
            "info_gain": _node_info_gain(tree, node_id),
            "chosen_grant_purity": chosen_grant,
            "chosen_deny_purity": chosen_deny,
            "unchosen_grant_purity": unchosen_grant,
            "unchosen_deny_purity": unchosen_deny,
        })
        node_id = chosen
    return path


def extract_factor_support(
    model: CartModel,
    case_features: dict[str, Any],
    *,
    top_k: int = 5,
) -> tuple[list[FactorSupportEntry], list[FactorSupportEntry]]:
    """Return (factor_support_T, factor_support_F) as sorted lists of
    FactorSupportEntry, truncated to top_k each."""
    path = walk_path(model, case_features)
    by_feature_T: dict[str, float] = defaultdict(float)
    by_feature_F: dict[str, float] = defaultdict(float)
    for step in path:
        feat = step["feature"]
        gain = step["info_gain"]
        if step["chosen_grant_purity"] > step["unchosen_grant_purity"]:
            by_feature_T[feat] += gain
        if step["chosen_deny_purity"] > step["unchosen_deny_purity"]:
            by_feature_F[feat] += gain

    def _top_k(d: dict[str, float]) -> list[FactorSupportEntry]:
        items = [(name, weight) for name, weight in d.items() if weight > 0]
        items.sort(key=lambda x: x[1], reverse=True)
        return [FactorSupportEntry(feature=n, weight=float(w)) for n, w in items[:top_k]]

    return _top_k(by_feature_T), _top_k(by_feature_F)
