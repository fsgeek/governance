"""Binding-record levels R0-R5 and recomputation from a record.

Pre-reg section 2a/2b (OTS bd47a9d). The central discipline: recomputation may
read ONLY the fields present in the record. Anything absent is resolved the way
a later examiner would resolve it -- by taking the then-current default. That
resolution is what the study measures, so it must never leak the original value.

The enforcement is structural, not a convention: `recompute` receives a
`BindingRecord`, and a field the record does not carry is simply not reachable
from it.
"""

from __future__ import annotations

import hashlib
import json
import platform
from dataclasses import asdict, dataclass, field
from typing import Any

import numpy as np

# Record levels, weakest to strongest. Each is a superset of the previous.
LEVELS = ("R0", "R1", "R2", "R3", "R4", "R5")

LEVEL_FIELDS: dict[str, tuple[str, ...]] = {
    "R0": ("case_id", "decision", "timestamp"),
    "R1": ("model_id", "model_version"),
    "R2": ("params_hash", "config_hash", "model_blob_ref"),
    "R3": ("method", "method_version", "value_function",
           "background_ref", "background_size", "sampling_params"),
    "R4": ("lib_versions", "os", "hardware_class", "thread_count"),
    "R5": ("seed",),
}


def fields_for(level: str) -> set[str]:
    """Cumulative field set at a record level (R3 includes R0-R2)."""
    if level not in LEVELS:
        raise ValueError(f"unknown record level {level!r}; expected one of {LEVELS}")
    out: set[str] = set()
    for lv in LEVELS[: LEVELS.index(level) + 1]:
        out |= set(LEVEL_FIELDS[lv])
    return out


@dataclass
class BindingRecord:
    """What was actually written down at decision time.

    A field set to None is a field the institution did NOT record. Recomputation
    must fall back to a current default for it -- that fallback is the object
    under study.
    """

    level: str
    payload: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def capture(cls, level: str, full_state: dict[str, Any]) -> "BindingRecord":
        """Project the complete decision-time state down to one record level.

        `full_state` is everything that was true at decision time. The record
        keeps only the subset the level mandates; the rest is discarded here and
        is genuinely unavailable downstream.
        """
        keep = fields_for(level)
        payload = {k: v for k, v in full_state.items() if k in keep}
        missing = keep - set(payload)
        if missing:
            raise ValueError(
                f"level {level} requires fields absent from full_state: {sorted(missing)}"
            )
        return cls(level=level, payload=payload)

    def get(self, name: str) -> Any:
        """Read a field. Returns None when this level did not record it."""
        return self.payload.get(name)

    def has(self, name: str) -> bool:
        return name in self.payload

    def to_json(self) -> str:
        return json.dumps(asdict(self), sort_keys=True, default=str)

    def size_bytes(self) -> int:
        """On-disk cost of this record, for the pre-reg's cost argument."""
        return len(self.to_json().encode("utf-8"))


def current_environment() -> dict[str, Any]:
    """The environment a recomputation runs in, used for R4 fields."""
    import sklearn

    mods: dict[str, str | None] = {
        "numpy": np.__version__,
        "sklearn": sklearn.__version__,
    }
    for name in ("shap", "lime", "xgboost", "scipy"):
        try:
            mods[name] = __import__(name).__version__
        except Exception:
            mods[name] = None
    return {
        "lib_versions": mods,
        "os": platform.platform(),
        "hardware_class": platform.machine(),
        "thread_count": _thread_count(),
    }


def _thread_count() -> int:
    import os

    for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
        if os.environ.get(var):
            try:
                return int(os.environ[var])
            except ValueError:
                pass
    return os.cpu_count() or 1


def hash_array(a: np.ndarray) -> str:
    """Stable content hash of an array, for params_hash / config_hash."""
    h = hashlib.sha256()
    h.update(str(a.dtype).encode())
    h.update(str(a.shape).encode())
    h.update(np.ascontiguousarray(a).tobytes())
    return h.hexdigest()


def hash_obj(o: Any) -> str:
    return hashlib.sha256(
        json.dumps(o, sort_keys=True, default=str).encode("utf-8")
    ).hexdigest()
