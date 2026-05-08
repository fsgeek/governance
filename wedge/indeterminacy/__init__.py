"""Indeterminacy (I) species computations.

Per the 2026-05-08 indeterminacy operationalization memo, I is a vector over
species rather than a scalar. This package holds one module per species:

  - local_density: per-(model, case) — distance from leaf centroid in feature space.
    Captures the "doesn't fit" tail of the memo's conceptual definition. The
    "fits too well" tail is acknowledged at the case level (suspicious typicality
    in a single case is structurally hard to distinguish from ordinary central
    cases without a set-level null model) and deferred.
  - multivariate_coherence (TODO): per-case — corpus-wide joint density anomaly.
  - ioannidis (TODO): per-case — round-numbers, threshold-hugging, internal
    inconsistencies, Benford-style fingerprints.
  - retrospective (TODO): per-case — surprise model trained on later vintages.

Model-dependent species attach to PerModelOutput.indeterminacy. Model-independent
species attach to Case.case_indeterminacy.
"""

from wedge.indeterminacy.ioannidis import (
    compute_battery as compute_ioannidis_battery,
    compute_round_numbers,
    compute_threshold_hugging,
)
from wedge.indeterminacy.local_density import LeafStatistics, compute_local_density

__all__ = [
    "LeafStatistics",
    "compute_local_density",
    "compute_ioannidis_battery",
    "compute_round_numbers",
    "compute_threshold_hugging",
]
