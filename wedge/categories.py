"""Cat 1 / Cat 2 / ambiguous detection per spec §6.2.

The Cat 1 / Cat 2 distinction is the load-bearing diagnostic of the
mechanism: it differentiates "the policy excluded a model that could have
gotten this right" (Cat 2 — actionable) from "no admissible model would
have predicted this outcome" (Cat 1 — the policy is genuinely binding).

Three-condition criterion for Cat 2:
  1. The original ensemble's verdict differs from the realized outcome
     (the case is a failure of the original construction).
  2. The revised ensemble's verdict matches the realized outcome (set
     revision under surprise-weighted loss recovers it).
  3. The new-entrant models (in revised but not original) share an
     expressible structural-distinguishing feature — a feature whose
     split-usage frequency systematically differs between new-entrants
     and exits.

Fall-throughs:
  - "Cat 1"      : condition 1 holds, condition 2 fails (no admissible
                   model would have recovered).
  - "ambiguous"  : conditions 1 and 2 hold, condition 3 fails (revised
                   recovers but no clear feature explains why).
  - "not_failure": condition 1 fails (original got it right).

Set membership comparison is by HyperparameterSpec equality (deterministic
re-fit produces the same model from the same spec). The "structural-
distinguishing feature" is computed from split-usage frequencies on the
fitted trees retained by SweepResult.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Optional

from wedge.models import CartModel
from wedge.rashomon import HyperparameterSpec, SweepResult, used_features


Category = Literal["Cat 1", "Cat 2", "ambiguous", "not_failure"]


@dataclass(frozen=True)
class RefitSet:
    """A bundle of SweepResults (for spec-based set comparison) paired with
    refit CartModels (for case prediction). `results[i]` corresponds to
    `models[i]`; the caller maintains alignment.
    """

    results: list[SweepResult]
    models: list[CartModel]

    def specs(self) -> list[HyperparameterSpec]:
        return [r.spec for r in self.results]


@dataclass(frozen=True)
class CaseClassification:
    """Per-case audit record for the Cat 1 / Cat 2 / ambiguous distinction."""

    case_id: str
    category: Category
    original_pred: float
    revised_pred: float
    realized_outcome: int
    structural_distinguishing_feature: Optional[str]
    new_entrant_count: int
    exit_count: int


def _mean_T(models: list[CartModel], case_features: dict[str, Any]) -> float:
    return sum(m.emit_for_case(case_features)["T"] for m in models) / len(models)


def _set_difference_by_spec(
    a: RefitSet, b: RefitSet
) -> list[SweepResult]:
    """Members of `a` whose spec is not in `b`."""
    b_specs = set(b.specs())
    return [r for r in a.results if r.spec not in b_specs]


def extract_distinguishing_feature(
    new_entrants: list[SweepResult],
    exits: list[SweepResult],
    *,
    threshold: float = 0.5,
) -> Optional[str]:
    """Find the feature with the largest split-usage gap between new-entrants
    and exits, if any gap exceeds `threshold`.

    For each feature in the union of new-entrant and exit feature subsets,
    compute:
        usage_new  = fraction of new-entrant models that split on it
        usage_exit = fraction of exit models that split on it
    Gap = |usage_new - usage_exit|. Return the feature with maximum gap iff
    the maximum gap exceeds `threshold`; else return None.

    Empty `new_entrants` or empty `exits` yields None (no comparison possible).
    """
    if not new_entrants or not exits:
        return None

    all_features: set[str] = set()
    for sr in new_entrants:
        all_features.update(sr.spec.feature_subset)
    for sr in exits:
        all_features.update(sr.spec.feature_subset)

    def _usage_fraction(group: list[SweepResult], feature: str) -> float:
        if not group:
            return 0.0
        n_using = 0
        for sr in group:
            if sr.fitted_tree is None:
                continue
            feature_names = list(sr.spec.feature_subset)
            if feature not in feature_names:
                continue
            if feature in used_features(sr.fitted_tree, feature_names):
                n_using += 1
        return n_using / len(group)

    best_feature: Optional[str] = None
    best_gap = 0.0
    for f in all_features:
        new_frac = _usage_fraction(new_entrants, f)
        exit_frac = _usage_fraction(exits, f)
        gap = abs(new_frac - exit_frac)
        if gap > best_gap:
            best_gap = gap
            best_feature = f
    return best_feature if best_gap >= threshold else None


def classify_case(
    case_features: dict[str, Any],
    case_id: str,
    *,
    original_set: RefitSet,
    revised_set: RefitSet,
    realized_outcome: int,
    distinguishing_feature_threshold: float = 0.5,
) -> CaseClassification:
    """Per spec §6.2 three-condition Cat 2 criterion.

    `original_set` is the wedge's R_T ∪ R_F selected members at first pass;
    `revised_set` is R_T' ∪ R_F' under surprise-weighted loss. Both bundle
    SweepResults (for spec-based set comparison) and refit CartModels (for
    case prediction). `realized_outcome` is the binary realized label
    (1=grant, 0=deny under the grant-as-positive convention).

    The decision threshold for "ensemble verdict" is 0.5 on mean T. A
    sharper threshold can be plugged in later (spec §6.2 mentions
    sensitivity reporting); V1 default is the natural midpoint.
    """
    orig_pred = _mean_T(original_set.models, case_features)
    rev_pred = _mean_T(revised_set.models, case_features)
    orig_decision = 1 if orig_pred >= 0.5 else 0
    rev_decision = 1 if rev_pred >= 0.5 else 0

    new_entrants = _set_difference_by_spec(revised_set, original_set)
    exits = _set_difference_by_spec(original_set, revised_set)

    if orig_decision == realized_outcome:
        return CaseClassification(
            case_id=case_id,
            category="not_failure",
            original_pred=orig_pred,
            revised_pred=rev_pred,
            realized_outcome=realized_outcome,
            structural_distinguishing_feature=None,
            new_entrant_count=len(new_entrants),
            exit_count=len(exits),
        )

    # Condition 1 holds (original was wrong). Check condition 2.
    if rev_decision != realized_outcome:
        return CaseClassification(
            case_id=case_id,
            category="Cat 1",
            original_pred=orig_pred,
            revised_pred=rev_pred,
            realized_outcome=realized_outcome,
            structural_distinguishing_feature=None,
            new_entrant_count=len(new_entrants),
            exit_count=len(exits),
        )

    # Conditions 1 and 2 hold. Check condition 3.
    feature = extract_distinguishing_feature(
        new_entrants, exits, threshold=distinguishing_feature_threshold
    )
    category: Category = "Cat 2" if feature is not None else "ambiguous"
    return CaseClassification(
        case_id=case_id,
        category=category,
        original_pred=orig_pred,
        revised_pred=rev_pred,
        realized_outcome=realized_outcome,
        structural_distinguishing_feature=feature,
        new_entrant_count=len(new_entrants),
        exit_count=len(exits),
    )
