# Prototype Extension Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend the wedge prototype (`wedge/`) to implement the V1 mechanism spec's three May 23 deliverable targets on LendingClub V₂ (2015Q4): dual-set R_T(ε_T) / R_F(ε_F) construction with per-case I_pred emission (Target A); at least one Cat 2 detection with the structural-distinguishing feature articulated end-to-end (Target B); a single end-to-end run producing all artifacts including construction manifest (Target C).

**Architecture:** New modules added to `wedge/` for cost-asymmetric loss, dual-set construction, surprise model, set revision, Cat 1/Cat 2 detection, and construction manifest emission. Existing modules (`collectors/`, `models.py`, `attribution.py`, `rashomon.py`, `metrics.py`, `output.py`) extended where needed; not rewritten. TDD discipline: each module commits with tests against small synthetic fixtures before the larger run. The wedge's existing run orchestration (`run.py`) is extended to call the new modules in sequence; a single CLI invocation produces all May 23 artifacts.

**Tech Stack:** Python 3.14, pandas 2.x, scikit-learn 1.5+, numpy 1.26+, pytest 8.x. No new external dependencies.

**Spec dependency:** `docs/superpowers/specs/2026-05-10-mechanism-specification.md` V1 stabilized 2026-05-11 (commit `04c1b9b`).

**Scope note.** This plan implements the V1 spec targets for May 23. V1.1 spec work (OD-10 substrate-axis, OD-11+OD-15 §3.1 reframing + sensitivity reporting, OD-14 novelty positioning) is *not* part of this plan; those are spec edits running in parallel. OD-12 (post-fit split-use check) and OD-13 (collector standardization) are May-23-bearing and *are* in scope per the mechanism spec plan's Task 11 Steps 1–2.

**Out of scope:**
- HMDA cross-validation, Fannie Mae generalization (post-May-23).
- Multi-policy M&A sweep capability (post-May-23).
- Production-grade infrastructure (monitoring, on-call runbooks, performance tuning).
- Statistical-power-grade Cat 2 detection at population scale (Target B explicitly accepts ≥1 case with articulated structure; population validation is post-May-23).
- Sensitivity-reporting code support for OD-15 (V1.1; manifest emits V1 fields only).

---

## File Structure

New modules to be added:

```
wedge/
├── losses.py                  # Cost-asymmetric loss functions L_T, L_F, L_T', L_F'
├── dual_set.py                # Dual-set R_T(ε_T) / R_F(ε_F) construction
├── i_pred.py                  # Per-case I_pred(x) computation from set outputs
├── surprise.py                # Surprise model S: origination_features → outcome_surprise
├── categories.py              # Cat 1 / Cat 2 / ambiguous detection
├── manifest.py                # Construction manifest emission (V1 fields)
└── tests/
    ├── test_losses.py
    ├── test_dual_set.py
    ├── test_i_pred.py
    ├── test_surprise.py
    ├── test_categories.py
    └── test_manifest.py
```

Existing modules extended (not rewritten):

```
wedge/
├── collectors/
│   ├── lendingclub.py         # OD-13: derive_label flip
│   └── hmda.py                # OD-13: derive_label flip
├── rashomon.py                # OD-12: post-fit mandatory-feature split-use check
├── run.py                     # End-to-end orchestration including all new modules
└── tests/
    ├── test_lendingclub.py    # OD-13: update label assertions
    ├── test_hmda.py           # OD-13: update label assertions
    └── test_rashomon.py       # OD-12: add split-use check test
```

---

## Task 1: OD-13 — collector label-polarity standardization

**Files:**
- Modify: `wedge/collectors/lendingclub.py:85` (`derive_label`)
- Modify: `wedge/collectors/hmda.py:145` (`derive_label`)
- Modify: `wedge/tests/test_lendingclub.py`, `wedge/tests/test_hmda.py` (label assertions)
- Modify: `docs/superpowers/specs/2026-05-10-mechanism-specification.md` §2.7 OD-9a (remove adapter requirement; V1.1 changelog entry)

- [ ] **Step 1: Write failing test asserting new convention for LC**

In `wedge/tests/test_lendingclub.py`, add or modify a test asserting:

```python
def test_derive_label_grant_as_positive():
    """Fully Paid → label=1 (grant/favorable); Charged Off → label=0 (deny/adverse)."""
    from wedge.collectors.lendingclub import derive_label
    import pandas as pd

    statuses = pd.Series(["Fully Paid", "Charged Off", "Fully Paid"])
    labels = derive_label(statuses)
    assert labels.tolist() == [1, 0, 1]
```

- [ ] **Step 2: Run to verify it fails**

Run: `pytest wedge/tests/test_lendingclub.py::test_derive_label_grant_as_positive -v`
Expected: FAIL with assertion error (current `derive_label` returns `[0, 1, 0]`).

- [ ] **Step 3: Flip LC `derive_label`**

In `wedge/collectors/lendingclub.py:85`, change:

```python
def derive_label(loan_status: pd.Series) -> pd.Series:
    """Map terminal loan_status to binary label: charged_off=1, paid=0."""
    return (loan_status == CHARGED_OFF).astype(int)
```

to:

```python
def derive_label(loan_status: pd.Series) -> pd.Series:
    """Map terminal loan_status to binary label: paid=1 (grant/favorable),
    charged_off=0 (deny/adverse). See spec §2.7 OD-9a for convention rationale."""
    return (loan_status == PAID).astype(int)
```

- [ ] **Step 4: Run LC test to verify pass**

Run: `pytest wedge/tests/test_lendingclub.py::test_derive_label_grant_as_positive -v`
Expected: PASS.

- [ ] **Step 5: Repeat Steps 1–4 for HMDA**

Add failing test in `wedge/tests/test_hmda.py`:

```python
def test_derive_label_grant_as_positive():
    """originated → label=1 (grant); denied → label=0 (deny). See spec §2.7 OD-9a."""
    from wedge.collectors.hmda import derive_label, ACTION_DENIED, ACTION_ORIGINATED
    import pandas as pd

    actions = pd.Series([ACTION_ORIGINATED, ACTION_DENIED, ACTION_ORIGINATED])
    labels = derive_label(actions)
    assert labels.tolist() == [1, 0, 1]
```

Then flip `wedge/collectors/hmda.py:145`:

```python
def derive_label(action_taken: pd.Series) -> pd.Series:
    """Map HMDA action_taken to binary label: originated=1 (grant),
    denied=0 (deny/adverse). See spec §2.7 OD-9a for convention rationale."""
    return (action_taken.astype(int) == ACTION_ORIGINATED).astype(int)
```

Run: `pytest wedge/tests/test_hmda.py::test_derive_label_grant_as_positive -v`
Expected: PASS.

- [ ] **Step 6: Run full wedge test suite; identify and update tests assuming old convention**

Run: `pytest wedge/tests/ -v`
Expected: failures in any test that asserted `label=1` for adverse outcomes. Update each: invert the expected label values. Document the change in a brief comment if the test's intent isn't clear after the flip.

- [ ] **Step 7: Re-run one vintage end-to-end to verify cliff structure translates**

Run: `python -m wedge.run --vintage 2015Q4 --output runs/post_od13_smoke.jsonl`
Expected: run completes; cliff structure (cases where all members are silent on one side) translates from the old "T-silent-all" / "F-silent-all" labels to the *opposite* labels under the new convention (cases that were T-silent-all on 2015Q4 should now appear as F-silent-all, and vice versa, because T and F flip their meaning). Verify with a quick comparison against `runs/2026-05-09T*.jsonl` if those are accessible.

- [ ] **Step 8: Update spec §2.7 OD-9a**

Edit `docs/superpowers/specs/2026-05-10-mechanism-specification.md` to:
- Change OD-9a's status to "Resolved 2026-05-11; collectors standardized to grant-as-positive."
- Note the V1.1 changelog entry: "OD-13 collector standardization: lendingclub.py and hmda.py derive_label flipped; adapter requirement at construction boundary removed; published findings re-interpreted in flipped convention."
- Append the V1.1 changelog entry to §0.1.

- [ ] **Step 9: Commit**

```bash
git add wedge/collectors/lendingclub.py wedge/collectors/hmda.py wedge/tests/ docs/superpowers/specs/2026-05-10-mechanism-specification.md
git commit -m "wedge: OD-13 collector standardization (label=1 ⇔ grant)"
```

---

## Task 2: OD-12 — post-fit mandatory-feature split-use check

**Files:**
- Modify: `wedge/rashomon.py` (add post-fit check to set-membership filter)
- Modify: `wedge/tests/test_rashomon.py` (new test)
- Modify: `docs/superpowers/specs/2026-05-10-mechanism-specification.md` §2.7 OD-9b

- [ ] **Step 1: Write failing test**

In `wedge/tests/test_rashomon.py`, add:

```python
def test_mandatory_feature_split_use_check():
    """A fitted model that does not split on a mandatory feature is excluded from R(ε)."""
    from wedge.rashomon import build_rashomon_set
    from policy.encoder import PolicyConstraints
    # Fixture: synthetic data where one model in the sweep is fit but doesn't split on the
    # mandatory feature (e.g., because the feature is constant or doesn't reduce loss).
    # The post-fit check should exclude that model from R(ε).
    constraints = PolicyConstraints(
        name="test", version="0", status="test",
        monotonicity_map={}, mandatory_features=("fico_range_low",),
        prohibited_features=(),
    )
    # Build R(ε) with a fixture that produces a no-split-on-fico model
    rashomon_set, excluded = build_rashomon_set(fixture_data, constraints, epsilon=0.05)
    # The excluded list should contain at least one model excluded for failing the
    # split-use check.
    excluded_reasons = [r for _, r in excluded]
    assert any("mandatory_feature_unused" in r for r in excluded_reasons)
```

- [ ] **Step 2: Run to verify it fails**

Run: `pytest wedge/tests/test_rashomon.py::test_mandatory_feature_split_use_check -v`
Expected: FAIL (current `build_rashomon_set` only checks pre-fit admissibility).

- [ ] **Step 3: Implement the post-fit check in rashomon.py**

In `wedge/rashomon.py`, after fitting each candidate model and before adding to R(ε), inspect the fitted tree's used-feature set (sklearn's `tree_.feature` array filtered to non-leaf nodes). If any feature in `constraints.mandatory_features` is absent from the used-feature set, exclude the model with reason `"mandatory_feature_unused: {feature_name}"`. Return the exclusion record alongside R(ε).

Sketch:

```python
def _used_features(fitted_tree) -> set[str]:
    """Return feature names actually split on by the fitted tree."""
    feature_idx = fitted_tree.tree_.feature
    used = {feature_names[i] for i in feature_idx if i >= 0}  # -2 = leaf
    return used

def build_rashomon_set(data, constraints, epsilon, ...):
    candidates = []
    excluded = []
    for hp in hyperparameter_grid:
        if not constraints.is_feature_subset_admissible(hp.feature_subset):
            excluded.append((hp, "pre_fit_inadmissible"))
            continue
        model = fit(data, hp)
        used = _used_features(model)
        missing = [f for f in constraints.mandatory_features if f not in used]
        if missing:
            excluded.append((hp, f"mandatory_feature_unused: {missing}"))
            continue
        if loss(model) <= best_loss + epsilon:
            candidates.append(model)
    return candidates, excluded
```

- [ ] **Step 4: Run to verify pass**

Run: `pytest wedge/tests/test_rashomon.py::test_mandatory_feature_split_use_check -v`
Expected: PASS.

- [ ] **Step 5: Run full wedge tests to ensure no regression**

Run: `pytest wedge/tests/ -v`
Expected: all pass. If existing tests assumed all admissible models reached R(ε), they may now fail because the stricter check excludes some — update those tests to reflect the stricter contract.

- [ ] **Step 6: Update spec §2.7 OD-9b**

Edit `docs/superpowers/specs/2026-05-10-mechanism-specification.md`:
- Change OD-9b's status to "Resolved 2026-05-11; post-fit split-use check is V1.1 default."
- Append V1.1 changelog entry: "OD-12 post-fit split-use check: rashomon.build_rashomon_set inspects fitted trees and excludes models that fail to split on any mandatory feature."

- [ ] **Step 7: Commit**

```bash
git add wedge/rashomon.py wedge/tests/test_rashomon.py docs/superpowers/specs/2026-05-10-mechanism-specification.md
git commit -m "wedge: OD-12 post-fit mandatory-feature split-use check"
```

---

## Task 3: Cost-asymmetric loss functions (L_T, L_F)

**Files:**
- Create: `wedge/losses.py`
- Create: `wedge/tests/test_losses.py`

- [ ] **Step 1: Write failing test**

```python
def test_grant_emphasis_loss():
    """L_T weights missed grants (y=1, ŷ=0) more heavily than missed denies (y=0, ŷ=1)."""
    from wedge.losses import grant_emphasis_loss
    import numpy as np
    y = np.array([1, 0, 1, 0])
    y_hat = np.array([0, 1, 1, 0])  # one missed grant, one missed deny
    loss = grant_emphasis_loss(y, y_hat, w_T=2.0)
    expected = 2.0 * 1 + 1.0 * 1  # missed grant weighted 2x; missed deny weighted 1x
    assert loss == expected
```

- [ ] **Step 2: Run to verify fail**

Run: `pytest wedge/tests/test_losses.py::test_grant_emphasis_loss -v`
Expected: FAIL with `ImportError`.

- [ ] **Step 3: Implement**

In `wedge/losses.py`:

```python
"""Cost-asymmetric losses for dual-set Rashomon construction.

L_T (grant_emphasis_loss): weights missed grants heavier than missed denies.
L_F (deny_emphasis_loss): weights missed denies heavier than missed grants.

See spec §3.2, §3.3 for the contract these implement.
"""
import numpy as np

def grant_emphasis_loss(y: np.ndarray, y_hat: np.ndarray, w_T: float = 1.5) -> float:
    """L_T(y, ŷ) = w_T · 1[y=1, ŷ=0] + 1[y=0, ŷ=1]. Convention: y=1 ⇔ grant."""
    missed_grants = ((y == 1) & (y_hat == 0)).sum()
    missed_denies = ((y == 0) & (y_hat == 1)).sum()
    return float(w_T * missed_grants + missed_denies)


def deny_emphasis_loss(y: np.ndarray, y_hat: np.ndarray, w_F: float = 1.5) -> float:
    """L_F(y, ŷ) = 1[y=1, ŷ=0] + w_F · 1[y=0, ŷ=1]. Convention: y=1 ⇔ grant."""
    missed_grants = ((y == 1) & (y_hat == 0)).sum()
    missed_denies = ((y == 0) & (y_hat == 1)).sum()
    return float(missed_grants + w_F * missed_denies)
```

- [ ] **Step 4: Add the deny-emphasis test, run both, verify pass**

```python
def test_deny_emphasis_loss():
    from wedge.losses import deny_emphasis_loss
    import numpy as np
    y = np.array([1, 0, 1, 0])
    y_hat = np.array([0, 1, 1, 0])
    loss = deny_emphasis_loss(y, y_hat, w_F=2.0)
    expected = 1.0 * 1 + 2.0 * 1
    assert loss == expected
```

Run: `pytest wedge/tests/test_losses.py -v`
Expected: both PASS.

- [ ] **Step 5: Commit**

```bash
git add wedge/losses.py wedge/tests/test_losses.py
git commit -m "wedge: cost-asymmetric losses L_T (grant-emphasis) and L_F (deny-emphasis)"
```

---

## Task 4: Dual-set R_T(ε_T) / R_F(ε_F) construction

**Files:**
- Create: `wedge/dual_set.py`
- Create: `wedge/tests/test_dual_set.py`

- [ ] **Step 1: Write failing test**

```python
def test_dual_set_nondegenerate():
    """R_T(ε_T) and R_F(ε_F) are non-empty and not identical on a non-trivial fixture."""
    from wedge.dual_set import build_dual_set
    from policy.encoder import PolicyConstraints
    constraints = PolicyConstraints(
        name="test", version="0", status="test",
        monotonicity_map={"fico_range_low": 1, "dti": -1},
        mandatory_features=("fico_range_low", "dti"),
        prohibited_features=(),
    )
    # Fixture: synthetic data with a few hundred cases where grant/deny depends on
    # fico and dti, with some noise.
    R_T, R_F, manifest = build_dual_set(
        fixture_data, constraints,
        epsilon_T=0.05, epsilon_F=0.05,
        w_T=1.5, w_F=1.5,
    )
    assert len(R_T) > 0
    assert len(R_F) > 0
    # Non-degeneracy: at least one model in one set is not in the other (by hp signature)
    R_T_signatures = {m.hp_signature for m in R_T}
    R_F_signatures = {m.hp_signature for m in R_F}
    assert R_T_signatures != R_F_signatures
```

- [ ] **Step 2: Run to verify fail**

Run: `pytest wedge/tests/test_dual_set.py -v`
Expected: FAIL with `ImportError`.

- [ ] **Step 3: Implement**

In `wedge/dual_set.py`, build on `wedge/rashomon.py`'s sweep but with cost-asymmetric losses:

```python
"""Dual-set R_T(ε_T) / R_F(ε_F) construction per spec §3.

Each set is the wedge's existing ε-optimal-under-policy construction, but the loss
function is cost-asymmetric (L_T or L_F from wedge/losses.py) rather than symmetric
0/1 loss.
"""
from dataclasses import dataclass
from wedge.rashomon import _build_constrained_set  # existing internal helper
from wedge.losses import grant_emphasis_loss, deny_emphasis_loss


@dataclass(frozen=True)
class DualSetManifest:
    """Construction manifest per spec §3.6."""
    policy_name: str
    policy_version: str
    hypothesis_space: str  # textual description of H
    training_sample_id: str
    w_T: float
    w_F: float
    epsilon_T: float
    epsilon_F: float
    n_R_T: int
    n_R_F: int


def build_dual_set(data, constraints, *, epsilon_T, epsilon_F, w_T, w_F,
                   training_sample_id: str):
    """Build R_T(ε_T) and R_F(ε_F) per spec §3.2 and §3.3."""
    R_T = _build_constrained_set(
        data, constraints, epsilon=epsilon_T,
        loss_fn=lambda y, yh: grant_emphasis_loss(y, yh, w_T=w_T),
    )
    R_F = _build_constrained_set(
        data, constraints, epsilon=epsilon_F,
        loss_fn=lambda y, yh: deny_emphasis_loss(y, yh, w_F=w_F),
    )
    manifest = DualSetManifest(
        policy_name=constraints.name,
        policy_version=constraints.version,
        hypothesis_space="CART, depth ≤ 5, leaf size ≥ 50",  # parameterize later
        training_sample_id=training_sample_id,
        w_T=w_T, w_F=w_F,
        epsilon_T=epsilon_T, epsilon_F=epsilon_F,
        n_R_T=len(R_T), n_R_F=len(R_F),
    )
    return R_T, R_F, manifest
```

May require refactoring `wedge/rashomon.py` to expose `_build_constrained_set` with a pluggable loss; that refactor is part of this step.

- [ ] **Step 4: Run to verify pass**

Run: `pytest wedge/tests/test_dual_set.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add wedge/dual_set.py wedge/tests/test_dual_set.py wedge/rashomon.py
git commit -m "wedge: dual-set R_T/R_F construction with cost-asymmetric losses"
```

---

## Task 5: Per-case I_pred(x) emission

**Files:**
- Create: `wedge/i_pred.py`
- Create: `wedge/tests/test_i_pred.py`

- [ ] **Step 1: Write failing test**

```python
def test_i_pred_zero_when_sets_agree():
    """I_pred(x) = 0 when E[h_T(x)] = E[h_F(x)] (sets agree on predicted probability)."""
    from wedge.i_pred import i_pred
    # Mock: R_T and R_F both predict P(grant) = 0.8 on case x
    R_T_preds = [0.8, 0.8, 0.8]
    R_F_preds = [0.8, 0.8, 0.8]
    assert i_pred(R_T_preds, R_F_preds) == 0.0


def test_i_pred_max_when_sets_disagree_fully():
    """I_pred(x) = 1 when R_T predicts 1.0 and R_F predicts 0.0 (or vice versa)."""
    from wedge.i_pred import i_pred
    R_T_preds = [1.0, 1.0, 1.0]
    R_F_preds = [0.0, 0.0, 0.0]
    assert i_pred(R_T_preds, R_F_preds) == 1.0
```

- [ ] **Step 2: Run to verify fail**

Run: `pytest wedge/tests/test_i_pred.py -v`
Expected: FAIL.

- [ ] **Step 3: Implement**

```python
"""Per-case I_pred(x) per spec §4.2.

I_pred(x) = |E[h_T(x) | h_T ∈ R_T(ε_T)] − E[h_F(x) | h_F ∈ R_F(ε_F)]|

Expectations are over set members under uniform weighting. V1 default emits on the
predicted-probability surface; hard-label variant is named in the spec but not the V1
default.
"""
import numpy as np

def i_pred(R_T_preds: list[float], R_F_preds: list[float]) -> float:
    """V1 default: absolute difference of mean predicted probabilities."""
    return float(abs(np.mean(R_T_preds) - np.mean(R_F_preds)))
```

- [ ] **Step 4: Run to verify pass**

Run: `pytest wedge/tests/test_i_pred.py -v`
Expected: both PASS.

- [ ] **Step 5: Commit**

```bash
git add wedge/i_pred.py wedge/tests/test_i_pred.py
git commit -m "wedge: per-case I_pred emission from dual-set outputs"
```

---

## Task 6: Surprise model S and outcome surprise computation

**Files:**
- Create: `wedge/surprise.py`
- Create: `wedge/tests/test_surprise.py`

- [ ] **Step 1: Write failing test**

```python
def test_surprise_zero_when_outcome_matches_prediction():
    """outcome_surprise(x, y) ≈ 0 when realized outcome matches predicted probability."""
    from wedge.surprise import compute_outcome_surprise
    # Calibrated model predicts P(default)=0.1; realized outcome = paid (0 defaults).
    # Surprise should be ≈ 0 - 0.1 = -0.1 (slight pleasant surprise).
    surprise = compute_outcome_surprise(p_default=0.1, realized_default=0)
    assert abs(surprise - (-0.1)) < 1e-6


def test_surprise_high_when_unexpected_default():
    """Surprise is positive and large when a low-predicted-default case defaults."""
    from wedge.surprise import compute_outcome_surprise
    surprise = compute_outcome_surprise(p_default=0.05, realized_default=1)
    assert abs(surprise - 0.95) < 1e-6
```

- [ ] **Step 2: Run to verify fail**

Run: `pytest wedge/tests/test_surprise.py -v`
Expected: FAIL.

- [ ] **Step 3: Implement**

```python
"""Surprise model S per spec §5.2.

V1 default: outcome_surprise = realized_outcome − P̂(default | origination_features),
where P̂ is a calibrated probability model trained on a later-vintage cohort (LC-eval
proxy) or the bank's own historical lifecycle data (production version).

This module computes outcome_surprise given P̂ and the realized outcome. Training the
surprise model itself is in wedge/run.py orchestration.
"""

def compute_outcome_surprise(p_default: float, realized_default: int) -> float:
    """Per-case surprise: realized_outcome − predicted P(default).

    Positive surprise = case defaulted more than predicted.
    Negative surprise = case paid better than predicted.
    """
    return float(realized_default - p_default)


def train_surprise_model(origination_features, realized_outcomes, model_class="gbm"):
    """Train a calibrated probability model for P̂(default | x).

    V1 default: scikit-learn GradientBoostingClassifier with isotonic calibration. The
    surprise model is NOT policy-constrained — its purpose is to detect signal the
    policy-constrained models may have missed. (Protected-class proxies remain excluded
    from its feature set; the bank's policy YAML names these.)
    """
    from sklearn.ensemble import GradientBoostingClassifier
    from sklearn.calibration import CalibratedClassifierCV
    base = GradientBoostingClassifier(n_estimators=100, max_depth=3)
    model = CalibratedClassifierCV(base, method="isotonic", cv=5)
    model.fit(origination_features, realized_outcomes)
    return model
```

- [ ] **Step 4: Run to verify pass**

Run: `pytest wedge/tests/test_surprise.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add wedge/surprise.py wedge/tests/test_surprise.py
git commit -m "wedge: surprise model S and outcome_surprise computation"
```

---

## Task 7: Set revision under surprise-weighted loss

**Files:**
- Modify: `wedge/dual_set.py` (add `build_revised_dual_set`)
- Modify: `wedge/losses.py` (add surprise-weighted variants)
- Modify: `wedge/tests/test_dual_set.py` (new tests)

- [ ] **Step 1: Write failing test**

```python
def test_revised_dual_set_differs_from_original():
    """R_T'(ε_T) under surprise-weighted L_T' differs from R_T(ε_T) under L_T
    when surprise is non-uniform across training cases."""
    from wedge.dual_set import build_dual_set, build_revised_dual_set
    # ... fixture with non-uniform surprise ...
    R_T, R_F, _ = build_dual_set(...)
    R_T_prime, R_F_prime, _ = build_revised_dual_set(
        ..., surprise_weights=surprise_array
    )
    # At least one new entrant or exit
    assert {m.hp_signature for m in R_T_prime} != {m.hp_signature for m in R_T}
```

- [ ] **Step 2: Run to verify fail**

Run: `pytest wedge/tests/test_dual_set.py::test_revised_dual_set_differs_from_original -v`
Expected: FAIL.

- [ ] **Step 3: Implement**

In `wedge/losses.py`, add surprise-weighted variants:

```python
def grant_emphasis_loss_weighted(y, y_hat, w_T, sample_weights):
    """L_T' = grant-emphasis loss with per-sample weights."""
    missed_grants = ((y == 1) & (y_hat == 0)) * sample_weights
    missed_denies = ((y == 0) & (y_hat == 1)) * sample_weights
    return float(w_T * missed_grants.sum() + missed_denies.sum())

def deny_emphasis_loss_weighted(y, y_hat, w_F, sample_weights):
    """L_F' = deny-emphasis loss with per-sample weights."""
    missed_grants = ((y == 1) & (y_hat == 0)) * sample_weights
    missed_denies = ((y == 0) & (y_hat == 1)) * sample_weights
    return float(missed_grants.sum() + w_F * missed_denies.sum())
```

In `wedge/dual_set.py`, add `build_revised_dual_set` that takes a surprise array and uses the weighted losses. The construction manifest gains fields for the revision (original set IDs, surprise model ID, weighting scheme).

- [ ] **Step 4: Run to verify pass**

Run: `pytest wedge/tests/test_dual_set.py -v`
Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add wedge/dual_set.py wedge/losses.py wedge/tests/
git commit -m "wedge: set revision under surprise-weighted loss (R_T', R_F')"
```

---

## Task 8: Cat 1 / Cat 2 / ambiguous detection

**Files:**
- Create: `wedge/categories.py`
- Create: `wedge/tests/test_categories.py`

- [ ] **Step 1: Write failing test**

```python
def test_cat_2_when_revised_set_recovers_outcome():
    """A case where original verdict was wrong, revised R_T' contains models predicting
    the correct outcome, and the new entrants share a distinguishing feature → Cat 2."""
    from wedge.categories import classify_case
    # Fixture: case x, original R_T predicted grant (y_hat=1), realized outcome y=0 (default).
    # Revised R_T' under surprise weighting includes a model that predicts deny for x and
    # weights some feature F differently.
    classification = classify_case(
        case_x=fixture_x,
        original_R_T=R_T_orig,
        revised_R_T=R_T_revised,
        realized_outcome=0,
    )
    assert classification.category == "Cat 2"
    assert classification.structural_distinguishing_feature is not None


def test_cat_1_when_no_admissible_model_predicts_correctly():
    """A case where even revised R_T' contains no model predicting the correct outcome → Cat 1."""
    from wedge.categories import classify_case
    classification = classify_case(...)
    assert classification.category == "Cat 1"
```

- [ ] **Step 2: Run to verify fail**

Run: `pytest wedge/tests/test_categories.py -v`
Expected: FAIL.

- [ ] **Step 3: Implement**

```python
"""Cat 1 / Cat 2 / ambiguous detection per spec §6.

Three-condition criterion for Cat 2:
  1. Original verdict differed from realized outcome
  2. Revised R_T'/R_F' contains a model that would have predicted the realized outcome
  3. The new-entrant models have an expressible structural-distinguishing feature

Fall through to Cat 1 if 1 holds but 2 or 3 fails.
Ambiguous if 2 holds but 3 is unclear under sensitivity perturbation.
"""
from dataclasses import dataclass

@dataclass
class CaseClassification:
    case_id: str
    category: str  # "Cat 1" | "Cat 2" | "ambiguous"
    cat_1_likelihood: float
    cat_2_likelihood: float
    structural_distinguishing_feature: str | None  # plain-text description
    new_entrant_count: int
    exit_count: int


def classify_case(case_x, original_R_T, revised_R_T, original_R_F, revised_R_F,
                  realized_outcome) -> CaseClassification:
    """Per spec §6.2 three-condition criterion."""
    # Condition 1: original verdict ≠ realized outcome
    original_pred = aggregate_predictions(original_R_T, original_R_F, case_x)
    if original_pred == realized_outcome:
        # Case is not a failure; nothing to classify
        return CaseClassification(..., category="not_failure", ...)

    # Condition 2: revised set contains a model predicting correctly
    revised_preds = [m.predict(case_x) for m in revised_R_T + revised_R_F]
    if not any(p == realized_outcome for p in revised_preds):
        # No admissible model recovers the outcome → Cat 1
        return CaseClassification(..., category="Cat 1", ...)

    # Condition 3: structural-distinguishing feature
    new_entrants = set_difference(revised_R_T, original_R_T) | set_difference(revised_R_F, original_R_F)
    exits = set_difference(original_R_T, revised_R_T) | set_difference(original_R_F, revised_R_F)
    feature = extract_distinguishing_feature(new_entrants, exits)

    if feature is None:
        # No expressible distinguishing feature → ambiguous
        return CaseClassification(..., category="ambiguous", ...)

    # All three conditions met → Cat 2
    return CaseClassification(..., category="Cat 2",
                              structural_distinguishing_feature=feature, ...)


def extract_distinguishing_feature(new_entrants, exits) -> str | None:
    """Identify a feature whose weight or split-frequency systematically differs
    between new_entrants and exits. V1 default: compare feature-usage frequency
    across the two model groups; return the feature with the largest gap if it
    exceeds a threshold. Returns plain-text description for the manifest.
    """
    # Implementation: for each feature, compute the fraction of new_entrant models
    # that split on it vs the fraction of exit models. Largest absolute gap above
    # 0.5 → distinguishing.
    ...
```

- [ ] **Step 4: Run to verify pass**

Run: `pytest wedge/tests/test_categories.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add wedge/categories.py wedge/tests/test_categories.py
git commit -m "wedge: Cat 1 / Cat 2 / ambiguous detection per spec §6.2"
```

---

## Task 9: Construction manifest emission

**Files:**
- Create: `wedge/manifest.py`
- Create: `wedge/tests/test_manifest.py`

- [ ] **Step 1: Write failing test**

```python
def test_manifest_contains_required_v1_fields():
    """Construction manifest emits all V1 fields per spec §3.6."""
    from wedge.manifest import emit_manifest
    manifest_dict = emit_manifest(
        dual_set_manifest=dual_set_manifest_fixture,
        surprise_model_metadata=surprise_metadata_fixture,
        run_id="2026-05-20-target-c-smoke",
    )
    required_fields = {
        "policy_name", "policy_version", "hypothesis_space",
        "training_sample_id", "w_T", "w_F", "epsilon_T", "epsilon_F",
        "n_R_T", "n_R_F", "surprise_model_id", "run_id",
    }
    assert required_fields.issubset(set(manifest_dict.keys()))
```

- [ ] **Step 2: Run to verify fail**

Run: `pytest wedge/tests/test_manifest.py -v`
Expected: FAIL.

- [ ] **Step 3: Implement**

```python
"""Construction manifest emission per spec §3.6.

V1 fields: policy_name, policy_version, hypothesis_space description, training_sample_id,
cost weights w_T and w_F, tolerances epsilon_T and epsilon_F, set sizes n_R_T and n_R_F,
surprise_model_id, run_id. Sensitivity reporting (OD-15) is V1.1; not emitted at V1.
"""
import json
from pathlib import Path

def emit_manifest(dual_set_manifest, surprise_model_metadata, run_id) -> dict:
    """Build the manifest dictionary per spec §3.6 V1 contract."""
    return {
        "schema_version": "v1",
        "run_id": run_id,
        "policy_name": dual_set_manifest.policy_name,
        "policy_version": dual_set_manifest.policy_version,
        "hypothesis_space": dual_set_manifest.hypothesis_space,
        "training_sample_id": dual_set_manifest.training_sample_id,
        "w_T": dual_set_manifest.w_T,
        "w_F": dual_set_manifest.w_F,
        "epsilon_T": dual_set_manifest.epsilon_T,
        "epsilon_F": dual_set_manifest.epsilon_F,
        "n_R_T": dual_set_manifest.n_R_T,
        "n_R_F": dual_set_manifest.n_R_F,
        "surprise_model_id": surprise_model_metadata.get("model_id"),
        "surprise_model_training_sample": surprise_model_metadata.get("training_sample_id"),
        "v1_1_deferred": ["OD-10 substrate-axis", "OD-15 sensitivity reporting"],
    }


def write_manifest(manifest_dict: dict, output_path: Path) -> None:
    output_path.write_text(json.dumps(manifest_dict, indent=2, sort_keys=True))
```

- [ ] **Step 4: Run to verify pass**

Run: `pytest wedge/tests/test_manifest.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add wedge/manifest.py wedge/tests/test_manifest.py
git commit -m "wedge: construction manifest emission (V1 fields)"
```

---

## Task 10: End-to-end run on V₂ — Target C integration

**Files:**
- Modify: `wedge/run.py` (add dual-set extension orchestration)
- Add new CLI subcommand: `python -m wedge.run dual-set --vintage 2015Q4 ...`

- [ ] **Step 1: Wire end-to-end orchestration in `wedge/run.py`**

Add a function or subcommand that does the following in sequence on V₂ = 2015Q4:
1. Load V₂ data via the standardized collector.
2. Train surprise model S on 2016Q1–2016Q4 LC originations with completed terminal observations.
3. Compute outcome_surprise for each V₂ case using S applied to V₂ origination features.
4. Build R_T(ε_T) and R_F(ε_F) on V₂ with declared w_T = w_F = 1.5, ε_T = ε_F = 0.05.
5. Emit per-case I_pred for all in-regime V₂ cases.
6. Build R_T'(ε_T) and R_F'(ε_F) under surprise-weighted L_T'/L_F'.
7. For each V₂ case where original verdict differs from realized outcome, classify via `wedge/categories.classify_case`.
8. Emit construction manifest.
9. Emit jsonl of per-case records (case_id, in_regime, original_pred, I_pred, realized_outcome, classification).

- [ ] **Step 2: Run on V₂ smoke**

Run: `python -m wedge.run dual-set --vintage 2015Q4 --surprise-vintage 2016 --output runs/2026-05-22-target-c.jsonl --manifest runs/2026-05-22-target-c-manifest.json`
Expected: completes; jsonl and manifest files written.

- [ ] **Step 3: Sanity-check the run**

Verify Target A: count cases with I_pred > 0.2 (or chosen threshold); expect ≥ 1% of in-regime cases.

Verify Target B: filter jsonl for `classification.category == "Cat 2"`; pick one case with the largest `cat_2_likelihood`; record case_id and structural_distinguishing_feature.

Verify Target C: all four artifacts exist (manifest, per-case jsonl, R_T/R_F member descriptors, set-revision record).

- [ ] **Step 4: Commit**

```bash
git add wedge/run.py
git commit -m "wedge: end-to-end dual-set run orchestration"
```

---

## Task 11: Worked Cat 2 case writeup

**Files:**
- Create: `docs/superpowers/specs/2026-05-22-target-b-cat2-worked-case.md` (date adjusts to actual run date)

- [ ] **Step 1: Pick the case**

From the V₂ run, pick the highest-likelihood Cat 2 case. Record: case_id, original verdict, realized outcome, surprise score, structural-distinguishing feature, the specific R_T'/R_F' new-entrant model's feature weights.

- [ ] **Step 2: Write the findings note**

Findings note with the following structure:
- Frontmatter: Status, Authority (canonical), Depends on (this spec, the run jsonl, the manifest), Invalidated by (none yet), Last reconciled with code (today's date).
- §1: Case identification (anonymized features summary).
- §2: Original verdict and why it was wrong (realized outcome).
- §3: Revised set's recovery — which new-entrant model predicted correctly and what feature weighting it used.
- §4: Structural-distinguishing feature articulated in text.
- §5: What this case demonstrates about the mechanism (one paragraph; not a generalization claim).

- [ ] **Step 3: Commit**

```bash
git add docs/superpowers/specs/2026-05-22-target-b-cat2-worked-case.md
git commit -m "spec: worked Cat 2 case from V₂ dual-set run (Target B)"
```

---

## Self-Review of This Plan

**1. Spec coverage.** Targets A, B, C from §7.2 of the mechanism spec each map to tasks:
- Target A (dual-set demonstration): Tasks 3, 4, 5, 10
- Target B (Cat 2 case): Tasks 6, 7, 8, 10, 11
- Target C (integration story): Task 10 ties everything together; Task 9 produces the manifest

May-23-bearing V1.1 items mapped:
- OD-13 (collector standardization): Task 1
- OD-12 (post-fit split-use check): Task 2

V1.1 items *not* in this plan (out of scope per the scope note): OD-10, OD-11, OD-14, OD-15.

**2. Placeholder scan.** Sketched implementations in Tasks 4, 7, 8 use `...` for fixture data and helper functions. Each `...` is bounded — the wedge has the supporting infrastructure (existing collectors produce fixture data; `wedge/rashomon.py` has the hyperparameter sweep) — but a fresh engineer reading this plan would need to look at the existing modules. This is acceptable for a plan that lives alongside the existing codebase; not acceptable for a plan written for a greenfield project.

**3. Type consistency.** R_T / R_F used throughout. Cost weights w_T / w_F. Tolerances ε_T / ε_F. I_pred for the V1 default measurement. Classifications "Cat 1" / "Cat 2" / "ambiguous". Names match the spec.

**4. Scope.** This plan is bounded to the May 23 deliverable: instantiation of the mechanism, not validation across substrates or generalization. The plan's scope note names this explicitly.

**5. Revision provisions.** As code reveals gaps in the spec (which it will), spec edits land as separate commits with V1.1 changelog entries. The plan does not pre-specify what those edits will be.

---

## Execution

Inline execution recommended. Subagent dispatch per task is also reasonable; each task is sufficiently self-contained that a fresh subagent could pick up the task description without the full conversation context, given the spec and the existing wedge code as ground truth.

Sequence is mostly linear: Task 1 (OD-13) must precede everything else (subsequent tasks assume the standardized convention); Tasks 3–6 can run in parallel if the development environment supports it; Tasks 7–9 depend on 3–6; Task 10 depends on all; Task 11 depends on 10's run output.

Estimated timeline against the 12-day May 23 window:
- Tasks 1–2 (V1.1 May-23-bearing items): 2 days
- Tasks 3–6 (modules with tests): 3 days
- Task 7 (set revision): 1 day
- Task 8 (Cat 1/Cat 2 detection): 2 days (this is the most novel module; expect debugging)
- Task 9 (manifest): 0.5 day
- Task 10 (end-to-end run + sanity check): 2 days (includes re-running if numbers look off)
- Task 11 (worked case writeup): 0.5 day

Total: ~11 days. One day of slack. If something blocks, the natural cut is to defer Task 11's findings-note polish (the run output itself is the Target B evidence; the note is documentation).
