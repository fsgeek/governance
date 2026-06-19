# Model-Class Band-Opening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend the `wedge` Rashomon construction to sweep three model classes (CART, sparse-linear, monotone-GBM) under one equivalent policy-admissibility semantic, and measure band cardinality (C), disparity spread (A), and clean-member existence (B) — under both plain and margin-aware disparity metrics across an ε-sweep — first on a synthetic positive control, then (gated) on real HMDA.

**Architecture:** Introduce a thin `FittedModel` protocol (`predict`, `predict_proba`, `feature_subset`, `used_features()`) so `SweepResult` holds a generic fitted model instead of a concrete `DecisionTreeClassifier`. Each model family supplies a `fit_*` function returning a `FittedModel` and a class-appropriate `used_features()`. The ε-band / policy / diversity core is already prediction-based and stays unchanged. A new `experiments/` harness computes C/A/B off the constructed band per class and emits a result manifest. Per-case attribution (`wedge/attribution.py`, leaf purity) is explicitly NOT touched — it is tree-only and not needed here.

**Tech Stack:** Python 3, scikit-learn (`DecisionTreeClassifier`, `LogisticRegression` with L1, `HistGradientBoostingClassifier` with `monotonic_cst`), pandas, numpy, pytest.

## Global Constraints

- Pre-registration is FROZEN and pushed: `docs/superpowers/specs/2026-06-18-model-class-band-opening-design.md`. Every constant below is copied verbatim from it; do NOT change any frozen constant to fit a result.
- ε sweep: relative band width `(loss − best)/best ≤ ε`, 8 points log-spaced from 0.005 to 0.05.
- τ (clean threshold for outcome B): disparity ≤ 0.02, applied to whichever metric is evaluated.
- Margin band (metric 2): applicants with predicted `P(approve)` within ±0.10 of the decision threshold (0.5).
- Verdict metric = plain approval-rate gap; margin-aware is reported alongside, never decides the verdict.
- The existing 33-file test suite must stay green. The CART arm is the baseline and MUST NOT regress: `used_features` behavior for trees, `evaluate_policy`, and all `test_rashomon.py` / `test_models.py` tests keep passing unchanged.
- Stage 2 (real HMDA) is GATED on Stage 1 (synthetic control) passing. Do not run or commit Stage-2 results before the control gate passes.
- Run tests with: `python -m pytest wedge/tests -q` (testpaths configured in pyproject.toml).
- Commit messages end with the repo's Co-Authored-By trailer (see existing commits). The post-commit hook auto-OTS-stamps; that is expected.

---

### Task 1: Introduce the `FittedModel` protocol and make `used_features` polymorphic

**Files:**
- Modify: `wedge/models.py` (add protocol + a `used_features()` method on `CartModel`)
- Modify: `wedge/rashomon.py:223-234` (make module-level `used_features` dispatch to the model)
- Test: `wedge/tests/test_models.py`

**Interfaces:**
- Consumes: existing `CartModel` (`wedge/models.py:32`), existing `used_features(fitted_tree, feature_names)` (`wedge/rashomon.py:223`).
- Produces:
  - `FittedModel` protocol (in `wedge/models.py`) with: `model_id: str`, `feature_subset: tuple[str, ...]`, `predict(X) -> np.ndarray`, `predict_proba(X) -> np.ndarray`, `used_features() -> set[str]`.
  - `CartModel.used_features() -> set[str]` returning the feature names the tree splits on.

- [ ] **Step 1: Write the failing test**

```python
# wedge/tests/test_models.py — append
def test_cartmodel_used_features_returns_split_features():
    import pandas as pd
    from wedge.models import fit_model
    # y depends only on f0; f1 is noise the tree may ignore.
    X = pd.DataFrame({"f0": [0, 0, 1, 1, 0, 1, 1, 0], "f1": [0, 1, 0, 1, 1, 0, 1, 0]})
    y = pd.Series([0, 0, 1, 1, 0, 1, 1, 0])
    m = fit_model(X, y, model_id="t", max_depth=2, min_samples_leaf=1,
                  feature_subset=("f0", "f1"))
    used = m.used_features()
    assert isinstance(used, set)
    assert "f0" in used  # the tree must split on the signal feature
    assert used.issubset({"f0", "f1"})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest wedge/tests/test_models.py::test_cartmodel_used_features_returns_split_features -v`
Expected: FAIL with `AttributeError: 'CartModel' object has no attribute 'used_features'`

- [ ] **Step 3: Write minimal implementation**

```python
# wedge/models.py — add near top after imports
from typing import Protocol, runtime_checkable

@runtime_checkable
class FittedModel(Protocol):
    """The model-agnostic surface the Rashomon core depends on.

    CART, sparse-linear, and monotone-GBM families each implement this so the
    ε-band / policy / metric layers never touch a concrete model type.
    """
    model_id: str
    feature_subset: tuple[str, ...]
    def predict(self, X) -> "np.ndarray": ...
    def predict_proba(self, X) -> "np.ndarray": ...
    def used_features(self) -> set[str]: ...
```

```python
# wedge/models.py — add method to CartModel (after predict_proba)
    def used_features(self) -> set[str]:
        """Feature names this tree actually splits on (tree_.feature)."""
        feature_idx = self.tree.tree_.feature
        names = list(self.feature_subset)
        return {names[i] for i in feature_idx if i >= 0}
```

```python
# wedge/rashomon.py — replace the module-level used_features body (lines 223-234)
def used_features(fitted_model, feature_names: list[str]) -> set[str]:
    """Return the set of feature names a fitted model actually depends on.

    Dispatches to the model's own used_features() when available (the
    FittedModel protocol); falls back to reading tree_.feature for a raw
    sklearn DecisionTreeClassifier (backwards-compat for callers that still
    pass a bare tree, e.g. SweepResult.fitted_tree before Task 2).
    """
    if hasattr(fitted_model, "used_features"):
        return fitted_model.used_features()
    feature_idx = fitted_model.tree_.feature
    return {feature_names[i] for i in feature_idx if i >= 0}
```

- [ ] **Step 4: Run tests to verify pass + no regression**

Run: `python -m pytest wedge/tests/test_models.py wedge/tests/test_rashomon.py wedge/tests/test_categories.py -q`
Expected: PASS (new test passes; existing tree/categories tests still green — `categories.py` calls `used_features(sr.fitted_tree, ...)` on a raw tree, exercising the fallback branch).

- [ ] **Step 5: Commit**

```bash
git add wedge/models.py wedge/rashomon.py wedge/tests/test_models.py
git commit -m "wedge: FittedModel protocol + polymorphic used_features (CART arm unchanged)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: Generalize `SweepResult` to hold a `FittedModel`

**Files:**
- Modify: `wedge/rashomon.py:70-91` (`SweepResult`), `:178-215` (`hyperparameter_sweep`), `:301-309` (`evaluate_policy` gate 2)
- Modify: `wedge/categories.py` (any `sr.fitted_tree` reader)
- Test: `wedge/tests/test_rashomon.py`

**Interfaces:**
- Consumes: `FittedModel` (Task 1), existing `fit_model` (returns `CartModel`, which now satisfies `FittedModel`).
- Produces: `SweepResult.fitted_model: Optional[FittedModel]` (replaces `fitted_tree`). A read-only `@property fitted_tree` returning `self.fitted_model.tree if isinstance(self.fitted_model, CartModel) else None` is kept so existing tree-only consumers (categories, attribution) don't break.

- [ ] **Step 1: Write the failing test**

```python
# wedge/tests/test_rashomon.py — append
def test_sweepresult_carries_fitted_model_satisfying_protocol():
    from wedge.models import FittedModel
    from wedge.rashomon import SweepConfig, hyperparameter_sweep
    from wedge.tests.fixtures import FEATURE_COLS, tiny_noisy_dataset
    df = tiny_noisy_dataset()
    cfg = SweepConfig(max_depths=(2,), min_samples_leafs=(1,),
                      feature_subsets=(tuple(FEATURE_COLS),))
    results = hyperparameter_sweep(df[FEATURE_COLS], df["label"], config=cfg)
    assert results
    sr = results[0]
    assert isinstance(sr.fitted_model, FittedModel)
    assert callable(sr.fitted_model.used_features)
    # backwards-compat property still yields the raw tree for CART
    assert sr.fitted_tree is not None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest wedge/tests/test_rashomon.py::test_sweepresult_carries_fitted_model_satisfying_protocol -v`
Expected: FAIL with `AttributeError: 'SweepResult' object has no attribute 'fitted_model'`

- [ ] **Step 3: Write minimal implementation**

```python
# wedge/rashomon.py — replace SweepResult dataclass (lines 70-91)
@dataclass
class SweepResult:
    """One hyperparameter combo with its fit outcome.

    `fitted_model` is a FittedModel (CART, sparse-linear, or monotone-GBM).
    `fitted_tree` remains as a read-only convenience for tree-only consumers
    (categories, attribution); it is None for non-tree families.
    """
    spec: HyperparameterSpec
    holdout_auc: float
    fitted_model: Optional["FittedModel"] = None
    holdout_y_true: Optional[np.ndarray] = None
    holdout_y_pred: Optional[np.ndarray] = None

    @property
    def fitted_tree(self):
        from wedge.models import CartModel
        if isinstance(self.fitted_model, CartModel):
            return self.fitted_model.tree
        return None
```

```python
# wedge/rashomon.py — in hyperparameter_sweep, change the SweepResult construction
# (was fitted_tree=model.tree) to:
                        fitted_model=model,
```

```python
# wedge/rashomon.py — add import at top
from wedge.models import CartModel, FittedModel, fit_model
```

```python
# wedge/rashomon.py — evaluate_policy gate 2 (around line 301-309): replace the
# fitted_tree None-check and used_features call
        if sr.fitted_model is None:
            raise ValueError(
                "evaluate_policy with non-None policy_constraints requires "
                "SweepResult.fitted_model to be populated. Did hyperparameter_sweep "
                "run successfully?"
            )
        used = sr.fitted_model.used_features()
```

- [ ] **Step 4: Run full suite to verify pass + no regression**

Run: `python -m pytest wedge/tests -q`
Expected: PASS. (If `categories.py` or `attribution.py` referenced `sr.fitted_tree` directly, the kept property covers them. If any test referenced the `fitted_tree=` kwarg by name in construction, update those call sites to `fitted_model=` — grep first: `grep -rn "fitted_tree=" wedge/`.)

- [ ] **Step 5: Commit**

```bash
git add wedge/rashomon.py wedge/categories.py wedge/tests/test_rashomon.py
git commit -m "wedge: SweepResult holds generic FittedModel; fitted_tree kept as property

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 3: Add the sparse-linear model family

**Files:**
- Create: `wedge/models_linear.py`
- Test: `wedge/tests/test_models_linear.py`

**Interfaces:**
- Consumes: `FittedModel` protocol (Task 1).
- Produces: `fit_sparse_linear(X, y, *, model_id, C, feature_subset, random_state=0) -> SparseLinearModel` where `SparseLinearModel` satisfies `FittedModel`. `used_features()` returns features with `|coef| > 1e-8`. `C` is the inverse-regularization strength (smaller C = sparser).

- [ ] **Step 1: Write the failing test**

```python
# wedge/tests/test_models_linear.py
import pandas as pd
from wedge.models import FittedModel
from wedge.models_linear import fit_sparse_linear

def test_sparse_linear_satisfies_protocol_and_used_features_drops_noise():
    # f0 perfectly separates; f1, f2 are pure noise. Strong L1 should zero them.
    X = pd.DataFrame({
        "f0": [0, 0, 0, 1, 1, 1, 0, 1] * 4,
        "f1": [0, 1, 0, 1, 0, 1, 1, 0] * 4,
        "f2": [1, 0, 1, 0, 1, 0, 0, 1] * 4,
    })
    y = pd.Series([0, 0, 0, 1, 1, 1, 0, 1] * 4)
    m = fit_sparse_linear(X, y, model_id="lin", C=0.05,
                          feature_subset=("f0", "f1", "f2"))
    assert isinstance(m, FittedModel)
    used = m.used_features()
    assert "f0" in used            # signal feature retained
    assert used.issubset({"f0", "f1", "f2"})
    proba = m.predict_proba(X)
    assert proba.shape == (len(X), 2)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest wedge/tests/test_models_linear.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'wedge.models_linear'`

- [ ] **Step 3: Write minimal implementation**

```python
# wedge/models_linear.py
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest wedge/tests/test_models_linear.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add wedge/models_linear.py wedge/tests/test_models_linear.py
git commit -m "wedge: sparse-linear (L1-logistic) model family + used_features by nonzero coef

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 4: Add the monotone-GBM model family

**Files:**
- Create: `wedge/models_gbm.py`
- Test: `wedge/tests/test_models_gbm.py`

**Interfaces:**
- Consumes: `FittedModel` protocol (Task 1).
- Produces: `fit_monotone_gbm(X, y, *, model_id, feature_subset, monotonic_cst=None, max_iter=100, random_state=0) -> MonotoneGBMModel`. `monotonic_cst` is a dict `{feature_name: +1|-1|0}` (sign of allowed monotone direction per the policy's monotonicity constraints); converted to the per-column int list `HistGradientBoostingClassifier` expects. `used_features()` returns features whose column index appears in any node split across the ensemble (via the fitted estimator's per-iteration predictors).

- [ ] **Step 1: Write the failing test**

```python
# wedge/tests/test_models_gbm.py
import pandas as pd
from wedge.models import FittedModel
from wedge.models_gbm import fit_monotone_gbm

def test_monotone_gbm_satisfies_protocol_and_respects_monotone_sign():
    # y increases with f0; enforce +1 monotonicity on f0.
    X = pd.DataFrame({
        "f0": [0, 1, 2, 3, 4, 5, 6, 7] * 6,
        "f1": [3, 1, 4, 1, 5, 9, 2, 6] * 6,
    })
    y = pd.Series([0, 0, 0, 0, 1, 1, 1, 1] * 6)
    m = fit_monotone_gbm(X, y, model_id="gbm", feature_subset=("f0", "f1"),
                         monotonic_cst={"f0": 1, "f1": 0}, max_iter=50)
    assert isinstance(m, FittedModel)
    used = m.used_features()
    assert "f0" in used
    assert used.issubset({"f0", "f1"})
    # monotone +1 on f0: increasing f0 (others fixed) must not DECREASE P(approve)
    lo = pd.DataFrame({"f0": [0], "f1": [4]})
    hi = pd.DataFrame({"f0": [7], "f1": [4]})
    p_lo = m.predict_proba(lo)[0, list(m.classes_).index(1)]
    p_hi = m.predict_proba(hi)[0, list(m.classes_).index(1)]
    assert p_hi >= p_lo - 1e-9
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest wedge/tests/test_models_gbm.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'wedge.models_gbm'`

- [ ] **Step 3: Write minimal implementation**

```python
# wedge/models_gbm.py
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest wedge/tests/test_models_gbm.py -v`
Expected: PASS. (If the `_predictors`/`nodes` introspection raises in this sklearn version, the test's `used` assertion still passes via the `set(names)` fallback, but the fallback is lossy — note it and verify the sklearn version's node dtype before relying on per-family `used_features` strictness. Check: `python -c "import sklearn; print(sklearn.__version__)"`.)

- [ ] **Step 5: Commit**

```bash
git add wedge/models_gbm.py wedge/tests/test_models_gbm.py
git commit -m "wedge: monotone-GBM model family + used_features by ensemble split-usage

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 5: Multi-family sweep entry point

**Files:**
- Create: `wedge/sweep_families.py`
- Test: `wedge/tests/test_sweep_families.py`

**Interfaces:**
- Consumes: `hyperparameter_sweep`/`SweepResult`/`SweepConfig` (rashomon.py), `fit_sparse_linear` (Task 3), `fit_monotone_gbm` (Task 4), `evaluate_policy` (rashomon.py).
- Produces: `sweep_family(X, y, *, family, grid, feature_subsets, random_state=0, holdout_fraction=0.3) -> list[SweepResult]` where `family in {"cart", "linear", "gbm"}` and `grid` is a family-specific dict of hyperparameter tuples. Reuses `inner_split` for an identical holdout across families so AUCs are commensurable.

- [ ] **Step 1: Write the failing test**

```python
# wedge/tests/test_sweep_families.py
import pandas as pd
from wedge.rashomon import SweepResult, evaluate_policy
from wedge.sweep_families import sweep_family
from wedge.tests.fixtures import FEATURE_COLS, tiny_noisy_dataset

def test_sweep_family_runs_all_three_and_yields_admissible_under_no_policy():
    df = tiny_noisy_dataset()
    X, y = df[FEATURE_COLS], df["label"]
    fs = (tuple(FEATURE_COLS),)
    grids = {
        "cart": {"max_depths": (2, 3), "min_samples_leafs": (1,)},
        "linear": {"Cs": (0.05, 1.0)},
        "gbm": {"max_iters": (30,)},
    }
    for fam, grid in grids.items():
        results = sweep_family(X, y, family=fam, grid=grid, feature_subsets=fs)
        assert results and all(isinstance(r, SweepResult) for r in results)
        assert all(r.fitted_model is not None for r in results)
        pa = evaluate_policy(results, policy_constraints=None)
        assert len(pa.admissible) == len(results)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest wedge/tests/test_sweep_families.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'wedge.sweep_families'`

- [ ] **Step 3: Write minimal implementation**

```python
# wedge/sweep_families.py
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
```

- [ ] **Step 4: Run test to verify it passes + no regression**

Run: `python -m pytest wedge/tests/test_sweep_families.py wedge/tests -q`
Expected: PASS (new test green; full suite still green).

- [ ] **Step 5: Commit**

```bash
git add wedge/sweep_families.py wedge/tests/test_sweep_families.py
git commit -m "wedge: multi-family sweep entry point (cart|linear|gbm), shared holdout

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 6: C/A/B outcome metrics over a constructed band

**Files:**
- Create: `wedge/band_outcomes.py`
- Test: `wedge/tests/test_band_outcomes.py`

**Interfaces:**
- Consumes: `SweepResult`, `EpsilonAdmissibleSet`, `filter_to_epsilon_under_loss` (rashomon.py). A `protected: pd.Series` (boolean, group membership) and an evaluation frame `X_eval, y_eval`.
- Produces:
  - `approval_rate_gap(model, X, protected) -> float` — `P(approve|protected) − P(approve|~protected)` using `model.predict`.
  - `margin_aware_gap(model, X, protected, *, threshold=0.5, band=0.10) -> float` — same gap restricted to rows whose `predict_proba` approve-prob is within `band` of `threshold`.
  - `band_outcomes(members, X_eval, protected, *, tau=0.02, threshold=0.5, margin_band=0.10) -> dict` returning `{"C": int, "A_plain": float, "A_margin": float, "B_plain": bool, "B_margin": bool, "min_gap_plain": float, "min_gap_margin": float}` where C = len(members), A_* = max−min gap across members, B_* = (min |gap| ≤ tau).

- [ ] **Step 1: Write the failing test**

```python
# wedge/tests/test_band_outcomes.py
import numpy as np
import pandas as pd
from wedge.band_outcomes import approval_rate_gap, band_outcomes

class _StubModel:
    # approves everyone in `approve_idx`, denies others — deterministic.
    def __init__(self, approve_mask):
        self._m = np.asarray(approve_mask, dtype=int)
        self.classes_ = (0, 1)
    def predict(self, X):
        return self._m
    def predict_proba(self, X):
        p1 = self._m.astype(float)
        return np.column_stack([1 - p1, p1])

def test_approval_rate_gap_signed():
    X = pd.DataFrame({"f": range(4)})
    protected = pd.Series([True, True, False, False])
    # approve both protected, neither unprotected -> gap = 1.0 - 0.0 = 1.0
    m = _StubModel([1, 1, 0, 0])
    assert approval_rate_gap(m, X, protected) == 1.0

def test_band_outcomes_C_A_B():
    X = pd.DataFrame({"f": range(4)})
    protected = pd.Series([True, True, False, False])
    clean = _StubModel([1, 0, 1, 0])    # gap 0.5-0.5 = 0.0  -> clean
    biased = _StubModel([1, 1, 0, 0])   # gap 1.0          -> not clean
    out = band_outcomes([clean, biased], X, protected, tau=0.02)
    assert out["C"] == 2
    assert out["A_plain"] == 1.0        # max(1.0) - min(0.0)
    assert out["B_plain"] is True       # clean member exists (min |gap| = 0 ≤ tau)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest wedge/tests/test_band_outcomes.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'wedge.band_outcomes'`

- [ ] **Step 3: Write minimal implementation**

```python
# wedge/band_outcomes.py
"""C/A/B outcome metrics for a constructed Rashomon band (pre-reg 2026-06-18).

C = cardinality (room to choose). A = disparity spread across members (harm a
selector could choose). B = a clean member (|gap| <= tau) exists in the band.
Both plain approval-rate gap and margin-aware gap are computed; the verdict
metric is the plain gap (margin only adds evidence — see spec §6).
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def _approve_prob(model, X) -> np.ndarray:
    return model.predict_proba(X)[:, list(model.classes_).index(1)]


def approval_rate_gap(model, X: pd.DataFrame, protected: pd.Series) -> float:
    pred = np.asarray(model.predict(X)).astype(float)
    p = np.asarray(protected, dtype=bool)
    if p.sum() == 0 or (~p).sum() == 0:
        return float("nan")
    return float(pred[p].mean() - pred[~p].mean())


def margin_aware_gap(model, X: pd.DataFrame, protected: pd.Series, *,
                     threshold: float = 0.5, band: float = 0.10) -> float:
    ap = _approve_prob(model, X)
    near = np.abs(ap - threshold) <= band
    pred = (ap >= threshold).astype(float)
    p = np.asarray(protected, dtype=bool) & near
    u = (~np.asarray(protected, dtype=bool)) & near
    if p.sum() == 0 or u.sum() == 0:
        return float("nan")
    return float(pred[p].mean() - pred[u].mean())


def band_outcomes(members, X_eval: pd.DataFrame, protected: pd.Series, *,
                  tau: float = 0.02, threshold: float = 0.5,
                  margin_band: float = 0.10) -> dict:
    plain = [approval_rate_gap(m, X_eval, protected) for m in members]
    marg = [margin_aware_gap(m, X_eval, protected, threshold=threshold, band=margin_band)
            for m in members]
    plain_v = [g for g in plain if not np.isnan(g)]
    marg_v = [g for g in marg if not np.isnan(g)]

    def spread(vs):
        return float(max(vs) - min(vs)) if vs else float("nan")

    def min_abs(vs):
        return float(min(abs(g) for g in vs)) if vs else float("nan")

    return {
        "C": len(members),
        "A_plain": spread(plain_v),
        "A_margin": spread(marg_v),
        "min_gap_plain": min_abs(plain_v),
        "min_gap_margin": min_abs(marg_v),
        "B_plain": bool(plain_v) and min_abs(plain_v) <= tau,
        "B_margin": bool(marg_v) and min_abs(marg_v) <= tau,
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest wedge/tests/test_band_outcomes.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add wedge/band_outcomes.py wedge/tests/test_band_outcomes.py
git commit -m "wedge: C/A/B band-outcome metrics (plain + margin-aware gap) per pre-reg

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 7: Stage-1 synthetic positive-control harness (THE GATE)

**Files:**
- Create: `experiments/band_opening_control.py`
- Create: `experiments/synthetic_planted.py` (planted-clean-member DGP)
- Test: `wedge/tests/test_synthetic_planted.py`

**Interfaces:**
- Consumes: `sweep_family` (Task 5), `evaluate_policy`/`filter_to_epsilon_under_loss` (rashomon.py), `band_outcomes` (Task 6).
- Produces:
  - `make_planted_dataset(n=4000, random_state=0) -> (X, y, protected, monotonic_cst, policy)` — a DGP where a policy-admissible model with disparity ≤ τ provably exists (label depends on legitimate features only; protected attribute is correlated with a legitimate feature but the clean model that uses only legitimate features achieves |gap| ≤ τ).
  - `run_control() -> dict` — sweeps all three families, builds the ε-band, computes `band_outcomes`, and asserts the GATE: `B_plain is True` for at least the linear and CART families on the planted data (a clean member is recoverable). Returns the full per-family outcome dict and a boolean `gate_passed`.

- [ ] **Step 1: Write the failing test**

```python
# wedge/tests/test_synthetic_planted.py
from experiments.synthetic_planted import make_planted_dataset

def test_planted_dataset_has_recoverable_clean_signal():
    X, y, protected, mono, policy = make_planted_dataset(n=2000, random_state=0)
    assert len(X) == 2000 and set(y.unique()) <= {0, 1}
    assert protected.dtype == bool
    # the label must be predictable from legitimate features (signal exists)
    from sklearn.tree import DecisionTreeClassifier
    legit = [c for c in X.columns if c != "protected_proxy"]
    clf = DecisionTreeClassifier(max_depth=3, random_state=0).fit(X[legit], y)
    assert clf.score(X[legit], y) > 0.8
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest wedge/tests/test_synthetic_planted.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'experiments.synthetic_planted'`

- [ ] **Step 3: Write minimal implementation**

```python
# experiments/__init__.py  (empty — make it a package)
```

```python
# experiments/synthetic_planted.py
"""Planted-clean-member DGP for the Stage-1 positive control (pre-reg §5).

Label y depends on two legitimate features (legit_a, legit_b). A protected
attribute is correlated with a third proxy feature (protected_proxy) that is
PROHIBITED by policy. A model that uses only legitimate features and excludes
the proxy achieves |approval-rate gap| <= tau BY CONSTRUCTION — that is the
planted clean member the harness must recover. If the harness cannot, it is
broken (gate fails) and Stage 2 must not run.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from policy.encoder import PolicyConstraints


def make_planted_dataset(n: int = 4000, random_state: int = 0):
    rng = np.random.default_rng(random_state)
    legit_a = rng.normal(size=n)
    legit_b = rng.normal(size=n)
    # legitimate score drives the label
    score = 1.2 * legit_a + 0.8 * legit_b
    y = (score > np.median(score)).astype(int)
    # protected attribute correlated with a PROXY but NOT with the label given legit feats
    protected = rng.random(n) < 0.4
    protected_proxy = protected.astype(float) + rng.normal(scale=0.5, size=n)
    X = pd.DataFrame({
        "legit_a": legit_a, "legit_b": legit_b, "protected_proxy": protected_proxy,
    })
    monotonic_cst = {"legit_a": 1, "legit_b": 1, "protected_proxy": 0}
    policy = PolicyConstraints(
        name="planted-control", version="1", status="frozen",
        mandatory_features=("legit_a",),
        prohibited_features=("protected_proxy",),
        monotonic_features={},
    )
    return X, pd.Series(y), pd.Series(protected), monotonic_cst, policy
```

NOTE: confirm the exact `PolicyConstraints` constructor signature first —
`grep -n "class PolicyConstraints" -A 30 policy/encoder.py` — and match field
names/types precisely (the kwargs above are illustrative; use the real ones).

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest wedge/tests/test_synthetic_planted.py -v`
Expected: PASS

- [ ] **Step 5: Write the control runner (no new test; it IS the gate assertion)**

```python
# experiments/band_opening_control.py
"""Stage-1 control runner. Run directly: python -m experiments.band_opening_control
Prints per-family C/A/B and asserts the gate. Stage 2 is forbidden until this passes.
"""
from __future__ import annotations

from functools import partial

from wedge.band_outcomes import band_outcomes
from wedge.losses import grant_emphasis_loss
from wedge.rashomon import evaluate_policy, filter_to_epsilon_under_loss
from wedge.sweep_families import sweep_family
from experiments.synthetic_planted import make_planted_dataset

EPS = 0.05  # control uses the loose end of the frozen sweep; full sweep in Stage 2

def run_control(random_state: int = 0) -> dict:
    X, y, protected, mono, policy = make_planted_dataset(random_state=random_state)
    feature_subsets = (("legit_a", "legit_b"),)  # the clean subset (proxy excluded)
    grids = {"cart": {"max_depths": (2, 3, 4), "min_samples_leafs": (20,)},
             "linear": {"Cs": (0.05, 0.2, 1.0)},
             "gbm": {"max_iters": (50,)}}
    out = {}
    for fam, grid in grids.items():
        results = sweep_family(X, y, family=fam, grid=grid,
                               feature_subsets=feature_subsets, monotonic_cst=mono)
        pa = evaluate_policy(results, policy_constraints=policy)
        band = filter_to_epsilon_under_loss(
            pa, loss_fn=partial(grant_emphasis_loss), loss_label="L_T", epsilon=EPS)
        members = [m.fitted_model for m in band.within_epsilon]
        out[fam] = band_outcomes(members, X, protected, tau=0.02)
    gate_passed = bool(out["cart"]["B_plain"] and out["linear"]["B_plain"])
    out["gate_passed"] = gate_passed
    return out

if __name__ == "__main__":
    res = run_control()
    for fam in ("cart", "linear", "gbm"):
        print(fam, res[fam])
    print("GATE PASSED:", res["gate_passed"])
    assert res["gate_passed"], (
        "CONTROL FAILED: harness did not recover a planted clean member. "
        "Fix the harness before Stage 2. Do NOT run real data.")
```

- [ ] **Step 6: Run the control + full suite, commit**

Run: `python -m experiments.band_opening_control` (expect `GATE PASSED: True`)
Then: `python -m pytest wedge/tests -q` (expect all green)

```bash
git add experiments/__init__.py experiments/synthetic_planted.py experiments/band_opening_control.py wedge/tests/test_synthetic_planted.py
git commit -m "experiment: Stage-1 synthetic positive-control gate (planted clean member)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

**GATE:** If `gate_passed` is False, STOP. The defect is in the harness, not the science. Debug `used_features`/admissibility/band construction until the planted clean member is recovered. Do not write or run Stage 2.

---

### Task 8: Stage-2 real-HMDA harness (RUN ONLY AFTER TASK 7 GATE PASSES)

**Files:**
- Create: `experiments/band_opening_hmda.py`
- Reference (read first): `wedge/tests/test_hmda_loader.py`, the HMDA loader it exercises, `policy/encoder.py` for the real HMDA policy.

**Interfaces:**
- Consumes: the existing HMDA loader (find via `grep -rn "def.*hmda" wedge/`), `sweep_family`, `evaluate_policy`, `filter_to_epsilon_under_loss`, `band_outcomes`.
- Produces: `run_hmda(*, vintage, random_state=0) -> dict` — sweeps all three families over the real HMDA policy/features, runs the full 8-point ε-sweep (0.005→0.05 log-spaced, frozen), computes `band_outcomes` per (family, ε), and writes a result manifest to `runs/band_opening_hmda_<vintage>_2026-06-18.json`. Protected axis = race/sex (from HMDA fields). Prints the C/A/B table mapped against the frozen interpretation table (spec §6).

- [ ] **Step 1: Read the loader + policy, confirm field names**

Run: `grep -rn "def.*hmda\|race\|ethnicity\|sex\|action_taken" wedge/ policy/ | head -40`
Confirm: the HMDA loader function name, the approve/deny label field (`action_taken`), and the protected-group fields. Record the exact vintage/geography to freeze.

- [ ] **Step 2: Write the harness (no unit test — it is an experiment runner; the unit-tested pieces are sweep_family + band_outcomes)**

```python
# experiments/band_opening_hmda.py
"""Stage-2 real-data run. GATED on experiments.band_opening_control passing.
Run: python -m experiments.band_opening_hmda
Writes runs/band_opening_hmda_<vintage>_2026-06-18.json and prints the
C/A/B table against the frozen interpretation table (spec §6).
"""
from __future__ import annotations

import json
from functools import partial

import numpy as np

from experiments.band_opening_control import run_control
from wedge.band_outcomes import band_outcomes
from wedge.losses import grant_emphasis_loss
from wedge.rashomon import evaluate_policy, filter_to_epsilon_under_loss
from wedge.sweep_families import sweep_family
# from wedge.<hmda_loader> import load_hmda   # fill from Step 1

EPS_SWEEP = tuple(np.geomspace(0.005, 0.05, 8))
VINTAGE = "FILL_FROM_STEP_1"

def run_hmda(*, vintage: str = VINTAGE, random_state: int = 0) -> dict:
    control = run_control(random_state=random_state)
    if not control["gate_passed"]:
        raise SystemExit("Stage-1 control gate FAILED — Stage 2 forbidden (spec §5).")

    # X, y, protected, mono, policy, feature_subsets = load_hmda(vintage)  # Step 1
    # grids per family (CART depth/leaf, linear Cs, gbm max_iters)
    # for each family: sweep_family -> evaluate_policy -> for eps in EPS_SWEEP:
    #     band = filter_to_epsilon_under_loss(pa, loss_fn=partial(grant_emphasis_loss),
    #                                         loss_label="L_T", epsilon=eps)
    #     members = [m.fitted_model for m in band.within_epsilon]
    #     record band_outcomes(members, X_eval, protected, tau=0.02)
    # assemble result dict keyed by (family, eps); write JSON to runs/.
    raise NotImplementedError("complete after Step 1 field confirmation")

if __name__ == "__main__":
    res = run_hmda()
    out_path = f"runs/band_opening_hmda_{VINTAGE}_2026-06-18.json"
    with open(out_path, "w") as fh:
        json.dump(res, fh, indent=2, default=float)
    print("wrote", out_path)
```

- [ ] **Step 3: Complete the harness body** using the confirmed loader/field names from Step 1. Keep all four frozen constants (EPS_SWEEP, tau=0.02, margin_band=0.10, threshold=0.5) exactly as the spec states — do not tune.

- [ ] **Step 4: Run the experiment**

Run: `python -m experiments.band_opening_hmda`
Expected: writes `runs/band_opening_hmda_<vintage>_2026-06-18.json`; prints C/A/B per (family, ε).

- [ ] **Step 5: Map the result against the frozen interpretation table (spec §6) — do NOT improvise a new interpretation.** Write a short `runs/band_opening_hmda_2026-06-18.md` stating which interpretation-table row the result lands on, and whether each §7 prediction was confirmed or falsified. Commit results + readout.

```bash
git add runs/band_opening_hmda_*.json runs/band_opening_hmda_2026-06-18.md experiments/band_opening_hmda.py
git commit -m "experiment: Stage-2 HMDA band-opening result + interpretation-table readout

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Self-Review

**Spec coverage:** §3 three classes → Tasks 1,3,4,5. §3 frozen admissibility dispatch → Tasks 1,3,4 (per-family `used_features`). §4 C/A/B → Task 6. §4a both metrics → Task 6. §4b ε-sweep → Tasks 7 (loose ε) + 8 (full 8-point). §5 control gate → Task 7. §5 Stage-2 HMDA race/sex → Task 8. §6 interpretation table → Task 8 Step 5 (explicitly forbids improvising). §7 predictions confirmed/falsified → Task 8 Step 5. §8 engineering scope (generalize fitted field, per-family dispatch, no attribution) → Tasks 1,2. §9 out-of-scope (no attribution for non-tree, no age, no whole-space attestation) → respected (attribution untouched; age absent; no attestation task). **No gaps.**

**Placeholder scan:** Two deliberate, flagged placeholders in Task 8 (`VINTAGE = "FILL_FROM_STEP_1"`, loader import) — these are gated on reading real field names in Step 1 and are explicitly NOT frozen science; the spec constants they sit beside ARE concrete. Task 7 Step 3 flags that `PolicyConstraints(...)` kwargs must be confirmed against `policy/encoder.py` before use. No vague "add error handling" placeholders.

**Type consistency:** `FittedModel` surface (`predict`, `predict_proba`, `feature_subset`, `used_features`, `classes_`) is identical across `CartModel` (Task 1), `SparseLinearModel` (Task 3), `MonotoneGBMModel` (Task 4). `SweepResult.fitted_model` (Task 2) consumed by `sweep_family` (Task 5) and `band_outcomes` members (Task 6, via `m.fitted_model`). `band_outcomes` return keys (`C/A_plain/A_margin/B_plain/B_margin/min_gap_*`) consumed identically in Tasks 7–8. Consistent.

**Known risk to watch (not a plan defect):** Task 4's GBM `used_features` reads sklearn internals (`_predictors`/`nodes`); the fallback returns all-features-used if the dtype differs by version. If that fallback fires, GBM admissibility is lenient — Step 4 flags verifying the sklearn version. This does not block CART/linear arms.
