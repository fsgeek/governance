"""Per-case I_pred(x): predictive disagreement between R_T and R_F.

Per spec §4.2:

    I_pred(x) = |E[h_T(x) | h_T ∈ R_T(ε_T)] − E[h_F(x) | h_F ∈ R_F(ε_F)]|

V1 default operates on the predicted-probability surface: each model's
`emit_for_case(x)["T"]` is its estimate of P(grant | x); the expectation
is the uniform mean across set members. The hard-label variant (each
model's argmax decision, averaged) is named in the spec but not V1.

This is the per-case routing signal for the dual-set construction:
cases with high I_pred(x) are those where the two policy-admissible
ε-bands disagree, i.e. where the cost-asymmetric loss orientation
materially changes the predicted outcome. These are the cases the
mechanism flags for further inspection (the Cat 1 / Cat 2 distinction
in §6 builds on this).

The function is intentionally model-class-agnostic: it requires only
that each model expose an `emit_for_case(case_features) -> dict` returning
a `T` field on [0, 1]. CartModel from wedge.models satisfies this contract;
test stubs do too.
"""

from __future__ import annotations

from typing import Any, Protocol


class _GrantEmitter(Protocol):
    """Structural type: anything with `emit_for_case(case) -> {'T': float, ...}`."""

    def emit_for_case(self, case_features: dict[str, Any]) -> dict[str, Any]: ...


def _mean_T(models: list[_GrantEmitter], case_features: dict[str, Any]) -> float:
    return sum(m.emit_for_case(case_features)["T"] for m in models) / len(models)


def compute_i_pred(
    R_T_models: list[_GrantEmitter],
    R_F_models: list[_GrantEmitter],
    case_features: dict[str, Any],
) -> float:
    """Return the V1-default I_pred(x) given two refit ε-band model sets.

    Computes the mean P(grant | x) under each set (uniform weighting over
    set members) and returns the absolute difference. Empty sets raise
    ValueError rather than returning NaN; downstream emission needs a
    well-defined number for every in-regime case.
    """
    if not R_T_models:
        raise ValueError("R_T_models is empty; cannot compute mean P(grant) under R_T")
    if not R_F_models:
        raise ValueError("R_F_models is empty; cannot compute mean P(grant) under R_F")
    t_under_T = _mean_T(R_T_models, case_features)
    t_under_F = _mean_T(R_F_models, case_features)
    return abs(t_under_T - t_under_F)
