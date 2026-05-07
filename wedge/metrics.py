"""Outcome-agreer detection and pairwise Jaccard overlap of factor supports.

Outcome-agreement (spec §9):
  All models predict the same direction (argmax T vs F is the same), AND
  max(T) - min(T) <= t_spread_max.

Pairwise factor-support overlap:
  For each model pair (i, j) on a given case, compute Jaccard overlap of
  their top-k factor_support_T (and separately factor_support_F) feature
  sets. Aggregate to the per-case mean across (n choose 2) pairs.
"""

from __future__ import annotations

from itertools import combinations

from wedge.types import PerModelOutput


def is_outcome_agreer(
    per_model: list[PerModelOutput], *, t_spread_max: float = 0.10
) -> bool:
    if len(per_model) < 2:
        return False
    directions = {("grant" if p.T > p.F else "deny") for p in per_model}
    if len(directions) != 1:
        return False
    ts = [p.T for p in per_model]
    return (max(ts) - min(ts)) <= t_spread_max


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def pairwise_factor_support_overlap(
    per_model: list[PerModelOutput],
) -> tuple[float, float]:
    """Return (mean pairwise Jaccard on factor_support_T, mean on factor_support_F).

    Jaccard is computed over the *feature names* in the support (weights are
    ignored at this layer; weight-aware overlap is iteration 2).
    """
    if len(per_model) < 2:
        return 0.0, 0.0
    overlaps_T: list[float] = []
    overlaps_F: list[float] = []
    for a, b in combinations(per_model, 2):
        a_T = {e.feature for e in a.factor_support_T}
        b_T = {e.feature for e in b.factor_support_T}
        a_F = {e.feature for e in a.factor_support_F}
        b_F = {e.feature for e in b.factor_support_F}
        overlaps_T.append(_jaccard(a_T, b_T))
        overlaps_F.append(_jaccard(a_F, b_F))
    return (
        sum(overlaps_T) / len(overlaps_T),
        sum(overlaps_F) / len(overlaps_F),
    )
