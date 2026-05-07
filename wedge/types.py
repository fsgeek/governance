"""Per-case schema for the Rashomon wedge.

Each Case records the origination-time features of one loan application,
the (T, F) emissions of every model in R(ε) on that case, and the
per-component factor support drawn from each model's intrinsic structure.

Synthetic cases carry origin="synthetic" and a synthetic_role tag per
the May-6 synthetic/real-data taxonomy. They do not carry labels (no
realized outcome) and the analysis layer must never elide the origin tag.

Mutability: Case and PerModelOutput are intentionally mutable because
the wedge's pipeline assembles per_model outputs incrementally. Producers
build then hand off; downstream consumers (metrics, output) must not
mutate after assembly. FactorSupportEntry is frozen because it is a
pure value object passed through unchanged.

Wire-format note on `label`: the schema requires the `label` key to be
present in serialized form for both real (int) and synthetic (null)
cases. from_dict uses .get() and tolerates a missing key as None, which
collapses the distinction between an absent key and an explicit null.
Producers must always emit the key.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass(frozen=True)
class FactorSupportEntry:
    """One (feature, weight) pair within factor_support_T or factor_support_F."""

    feature: str
    weight: float

    def to_dict(self) -> dict[str, Any]:
        return {"feature": self.feature, "weight": self.weight}

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "FactorSupportEntry":
        return cls(feature=d["feature"], weight=d["weight"])


@dataclass
class PerModelOutput:
    """One model's emission for one case."""

    model_id: str
    T: float
    F: float
    factor_support_T: list[FactorSupportEntry]
    factor_support_F: list[FactorSupportEntry]
    path: list[str]
    leaf: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_id": self.model_id,
            "T": self.T,
            "F": self.F,
            "factor_support_T": [e.to_dict() for e in self.factor_support_T],
            "factor_support_F": [e.to_dict() for e in self.factor_support_F],
            "path": list(self.path),
            "leaf": self.leaf,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "PerModelOutput":
        return cls(
            model_id=d["model_id"],
            T=d["T"],
            F=d["F"],
            factor_support_T=[FactorSupportEntry.from_dict(e) for e in d["factor_support_T"]],
            factor_support_F=[FactorSupportEntry.from_dict(e) for e in d["factor_support_F"]],
            path=list(d["path"]),
            leaf=d["leaf"],
        )


@dataclass
class Case:
    """One origination-time feature vector plus per-model emissions."""

    case_id: str
    origin: str  # "real" | "synthetic"
    synthetic_role: Optional[str]  # None for real cases; "hypothetical-scenario" for synthetic
    vintage: str
    features: dict[str, Any]
    label: Optional[int]  # None for synthetic
    per_model: list[PerModelOutput] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "origin": self.origin,
            "synthetic_role": self.synthetic_role,
            "vintage": self.vintage,
            "features": dict(self.features),
            "label": self.label,
            "per_model": [pmo.to_dict() for pmo in self.per_model],
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Case":
        return cls(
            case_id=d["case_id"],
            origin=d["origin"],
            synthetic_role=d.get("synthetic_role"),
            vintage=d["vintage"],
            features=dict(d["features"]),
            label=d.get("label"),
            per_model=[PerModelOutput.from_dict(p) for p in d.get("per_model", [])],
        )


def case_to_json(case: Case) -> str:
    return json.dumps(case.to_dict())


def case_from_json(payload: str) -> Case:
    return Case.from_dict(json.loads(payload))
