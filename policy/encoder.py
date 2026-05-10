"""Constraint encoder for policy-constrained Rashomon construction.

This module reads a policy-graph YAML (see ``policy/thin_demo_hmda.yaml`` for
the canonical demonstration shape) and emits a :class:`PolicyConstraints`
object that downstream Rashomon construction code consumes.

Three classes of constraint are extracted from the YAML:

1. **Monotonicity** — per-feature sign of effect on the *positive* class
   probability. ``direction: positive`` in the YAML means "higher feature
   value never decreases grant probability"; ``direction: negative`` means
   "higher feature value never increases grant probability".

2. **Mandatory features** — features that must appear in any model's
   factor support. Models in R(ε) that do not split on a mandatory feature
   are excluded.

3. **Prohibited features** — features that no model in R(ε) may use.

The encoder is deliberately minimal: it validates structure and returns a
typed object. It does not import sklearn or do model construction; that is
the policy-aware Rashomon constructor's job.

sklearn monotonicity convention
-------------------------------

scikit-learn's ``DecisionTreeClassifier`` accepts a ``monotonic_cst`` array
of length ``n_features`` with values in ``{-1, 0, 1}``. The sign is
interpreted relative to the *positive* class — defined by sklearn as the
**second class in ``classes_``** (i.e. ``classes_[1]``). For binary labels
encoded as ``{0, 1}`` (the wedge convention, see ``wedge/types.py``), this
makes ``1`` the positive class.

The mapping this encoder applies is:

- YAML ``direction: positive`` → sklearn ``+1``
  (feature ↑ ⇒ P(positive class) does not decrease)
- YAML ``direction: negative`` → sklearn ``-1``
  (feature ↑ ⇒ P(positive class) does not increase)
- feature not listed                    → sklearn ``0``
  (unconstrained)

In the HMDA thin demo the positive class is ``grant``. The YAML's
``direction`` is therefore stated relative to *grant probability*.
Downstream callers must ensure their label encoding matches this
convention; if they invert it, they must flip the signs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

REQUIRED_TOP_LEVEL_KEYS = ("name", "version", "status", "constraints", "nodes")
REQUIRED_CONSTRAINT_KEYS = ("monotonicity", "mandatory_features", "prohibited_features")
REQUIRED_NODE_KEYS = ("id", "type")
VALID_DIRECTIONS = {"positive": 1, "negative": -1}


class PolicyValidationError(ValueError):
    """Raised when a policy YAML is structurally malformed."""


@dataclass(frozen=True)
class PolicyConstraints:
    """Structured constraints extracted from a policy-graph YAML.

    Attributes
    ----------
    name, version, status:
        Identification fields lifted from the YAML; the encoder does not
        interpret them but downstream tooling logs them for provenance.
    monotonicity_map:
        Mapping ``feature_name -> {-1, +1}`` per the sklearn convention
        documented in the module docstring. Features absent from this
        map are unconstrained.
    mandatory_features:
        Features every admissible model must split on.
    prohibited_features:
        Features no admissible model may split on.
    applicable_regime:
        Pass-through of the YAML ``constraints.applicable_regime`` block.
        Out-of-regime cases route to manual review and are not scored.
    """

    name: str
    version: str
    status: str
    monotonicity_map: dict[str, int]
    mandatory_features: tuple[str, ...]
    prohibited_features: tuple[str, ...]
    applicable_regime: dict[str, Any] = field(default_factory=dict)

    def monotonic_cst(self, features: list[str]) -> list[int]:
        """Return the sklearn ``monotonic_cst`` array aligned to ``features``.

        Parameters
        ----------
        features:
            The feature ordering used to fit the model. The returned list
            has the same length and order; entry ``i`` is the constraint
            for ``features[i]``.

        Returns
        -------
        list[int]
            Values are ``+1`` (positive monotone), ``-1`` (negative
            monotone), or ``0`` (unconstrained), per sklearn's
            ``DecisionTreeClassifier(monotonic_cst=...)`` API. The sign
            is interpreted relative to ``classes_[1]`` (the positive
            class); see module docstring.

        Raises
        ------
        PolicyValidationError
            If a monotonicity-constrained feature is missing from the
            supplied feature list (silent dropping would cause the
            constraint to be unenforced without warning).
        """
        missing = [f for f in self.monotonicity_map if f not in features]
        if missing:
            raise PolicyValidationError(
                "Monotonicity-constrained features absent from feature list: "
                f"{missing}. Feature list provided: {features}."
            )
        return [self.monotonicity_map.get(f, 0) for f in features]

    def is_feature_subset_admissible(self, subset: tuple[str, ...]) -> bool:
        """Return True iff ``subset`` satisfies mandatory/prohibited constraints.

        A subset is admissible iff:

        - every feature in :attr:`mandatory_features` is present, AND
        - no feature in :attr:`prohibited_features` is present.

        Monotonicity is *not* checked here — that is enforced at fit time
        by sklearn via ``monotonic_cst``. This predicate is the gate the
        Rashomon hyperparameter sweep uses to skip inadmissible feature
        subsets before fitting.
        """
        s = set(subset)
        if not all(f in s for f in self.mandatory_features):
            return False
        if any(f in s for f in self.prohibited_features):
            return False
        return True


def _require_keys(obj: Any, keys: tuple[str, ...], where: str) -> None:
    if not isinstance(obj, dict):
        raise PolicyValidationError(f"{where}: expected mapping, got {type(obj).__name__}.")
    missing = [k for k in keys if k not in obj]
    if missing:
        raise PolicyValidationError(f"{where}: missing required keys {missing}.")


def _parse_monotonicity(entries: Any) -> dict[str, int]:
    if not isinstance(entries, list):
        raise PolicyValidationError(
            f"constraints.monotonicity: expected list, got {type(entries).__name__}."
        )
    out: dict[str, int] = {}
    for i, entry in enumerate(entries):
        where = f"constraints.monotonicity[{i}]"
        _require_keys(entry, ("feature", "direction"), where)
        feat = entry["feature"]
        direction = entry["direction"]
        if not isinstance(feat, str) or not feat:
            raise PolicyValidationError(f"{where}.feature: expected non-empty string.")
        if direction not in VALID_DIRECTIONS:
            raise PolicyValidationError(
                f"{where}.direction: expected one of {sorted(VALID_DIRECTIONS)}, "
                f"got {direction!r}."
            )
        if feat in out:
            raise PolicyValidationError(
                f"{where}.feature: duplicate monotonicity entry for {feat!r}."
            )
        out[feat] = VALID_DIRECTIONS[direction]
    return out


def _parse_string_list(value: Any, where: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise PolicyValidationError(f"{where}: expected list, got {type(value).__name__}.")
    for i, v in enumerate(value):
        if not isinstance(v, str) or not v:
            raise PolicyValidationError(f"{where}[{i}]: expected non-empty string.")
    return tuple(value)


def load_policy(path: str | Path) -> PolicyConstraints:
    """Load and validate a policy-graph YAML, returning :class:`PolicyConstraints`.

    Parameters
    ----------
    path:
        Path to a YAML file in the schema demonstrated by
        ``policy/thin_demo_hmda.yaml``.

    Raises
    ------
    FileNotFoundError
        If ``path`` does not exist.
    PolicyValidationError
        If the YAML is structurally malformed (missing required keys,
        wrong types, unknown monotonicity directions, etc.).
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Policy YAML not found: {p}")
    with p.open("r") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise PolicyValidationError(
            f"{p}: top-level YAML must be a mapping, got {type(data).__name__}."
        )

    _require_keys(data, REQUIRED_TOP_LEVEL_KEYS, where=str(p))
    constraints = data["constraints"]
    _require_keys(constraints, REQUIRED_CONSTRAINT_KEYS, where=f"{p}:constraints")

    nodes = data["nodes"]
    if not isinstance(nodes, list) or not nodes:
        raise PolicyValidationError(f"{p}:nodes: expected non-empty list.")
    for i, node in enumerate(nodes):
        _require_keys(node, REQUIRED_NODE_KEYS, where=f"{p}:nodes[{i}]")

    monotonicity_map = _parse_monotonicity(constraints["monotonicity"])
    mandatory = _parse_string_list(
        constraints["mandatory_features"], where=f"{p}:constraints.mandatory_features"
    )
    prohibited = _parse_string_list(
        constraints["prohibited_features"], where=f"{p}:constraints.prohibited_features"
    )

    overlap = set(mandatory) & set(prohibited)
    if overlap:
        raise PolicyValidationError(
            f"{p}: features cannot be both mandatory and prohibited: {sorted(overlap)}."
        )
    mono_prohibited = set(monotonicity_map) & set(prohibited)
    if mono_prohibited:
        raise PolicyValidationError(
            f"{p}: features cannot have monotonicity constraints and be prohibited: "
            f"{sorted(mono_prohibited)}."
        )

    applicable_regime = constraints.get("applicable_regime", {}) or {}
    if not isinstance(applicable_regime, dict):
        raise PolicyValidationError(
            f"{p}:constraints.applicable_regime: expected mapping or null, "
            f"got {type(applicable_regime).__name__}."
        )

    return PolicyConstraints(
        name=str(data["name"]),
        version=str(data["version"]),
        status=str(data["status"]),
        monotonicity_map=monotonicity_map,
        mandatory_features=mandatory,
        prohibited_features=prohibited,
        applicable_regime=applicable_regime,
    )
