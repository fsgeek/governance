"""Recompute an attribution from a binding record alone.

Pre-reg section 2b (OTS bd47a9d). `recompute` may read ONLY what the record
carries. Where a field is absent, it resolves the way a later examiner would:
the then-current default. Those defaults are collected in `ExaminerDefaults` so
that what an absent field costs is explicit and auditable, rather than buried.

The negative control R0 is the load-bearing test of the harness itself: a record
carrying only (case_id, decision, timestamp) identifies no model, so the
examiner must fit a plausible surrogate. If that "reproduces" the original
attribution, the harness is measuring nothing and no other cell counts.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from records import BindingRecord


@dataclass
class ExaminerDefaults:
    """What a later examiner reaches for when the record is silent.

    Each attribute stands in for one absent field. Changing these changes what
    "no record" means, so they are declared in one place rather than inlined.
    """

    surrogate_model_factory: Any = None   # absent model identity  -> refit something plausible
    current_background_size: int = 100    # absent background spec -> library-ish default
    current_seed: int | None = None       # absent seed            -> unseeded
    current_n_samples: int = 2048         # absent sampling params -> current default

    def describe(self) -> dict[str, Any]:
        return {
            "current_background_size": self.current_background_size,
            "current_seed": self.current_seed,
            "current_n_samples": self.current_n_samples,
            "surrogate": self.surrogate_model_factory is not None,
        }


class RecordInsufficient(Exception):
    """The record does not identify enough to attempt a recomputation at all."""


def resolve_model(record: BindingRecord, store: dict[str, Any],
                  defaults: ExaminerDefaults, X_ref: np.ndarray, y_ref: np.ndarray):
    """Get the model a recomputation will run against, using only the record.

    R0/R1 cannot reach the operative model:
      - R0 records no model identity at all.
      - R1 records an identifier and version but no parameter hash, so it can
        only reach whatever currently answers to that name -- which is the
        retention problem in `docs/recomputability-boundary-draft_1.md` section 6
        made executable: a pointer to a version nobody kept is not a record.
    """
    blob_ref = record.get("model_blob_ref")
    if blob_ref is not None and blob_ref in store:
        return store[blob_ref], "exact"

    model_id = record.get("model_id")
    if model_id is not None:
        current = store.get(f"{model_id}@current")
        if current is not None:
            return current, "current_version_under_same_id"

    if defaults.surrogate_model_factory is None:
        raise RecordInsufficient(
            f"record level {record.level} identifies no retrievable model and no "
            "surrogate was supplied"
        )
    return defaults.surrogate_model_factory(X_ref, y_ref), "refit_surrogate"


def resolve_background(record: BindingRecord, store: dict[str, Any],
                       defaults: ExaminerDefaults, X_ref: np.ndarray):
    """Background/reference set for the attribution, from the record or default."""
    ref = record.get("background_ref")
    if ref is not None and ref in store:
        return store[ref], "exact"
    size = record.get("background_size") or defaults.current_background_size
    rs = np.random.RandomState(record.get("seed"))
    idx = rs.choice(X_ref.shape[0], size=min(size, X_ref.shape[0]), replace=False)
    return X_ref[idx], "resampled_default"


def resolve_sampling(record: BindingRecord, defaults: ExaminerDefaults) -> dict[str, Any]:
    params = record.get("sampling_params")
    if params is not None:
        return dict(params)
    return {"n_samples": defaults.current_n_samples}


def recompute_attribution(record: BindingRecord, store: dict[str, Any],
                          X_eval: np.ndarray, X_ref: np.ndarray, y_ref: np.ndarray,
                          attribute_fn, defaults: ExaminerDefaults | None = None
                          ) -> tuple[np.ndarray, dict[str, Any]]:
    """Recompute attributions for X_eval using only what `record` carries.

    Returns (attributions, provenance) where provenance records how each absent
    field was resolved -- the audit trail for what the record failed to pin.
    """
    defaults = defaults or ExaminerDefaults()

    model, model_route = resolve_model(record, store, defaults, X_ref, y_ref)
    background, bg_route = resolve_background(record, store, defaults, X_ref)
    sampling = resolve_sampling(record, defaults)
    seed = record.get("seed") if record.has("seed") else defaults.current_seed

    attributions = attribute_fn(
        model=model, X=X_eval, background=background, seed=seed, **sampling
    )

    provenance = {
        "record_level": record.level,
        "record_bytes": record.size_bytes(),
        "model_route": model_route,
        "background_route": bg_route,
        "sampling": sampling,
        "seed_used": seed,
        "seed_from_record": record.has("seed"),
        "defaults_applied": defaults.describe(),
    }
    return np.asarray(attributions), provenance
