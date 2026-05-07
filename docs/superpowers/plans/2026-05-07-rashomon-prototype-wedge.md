# Rashomon Prototype Wedge Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the smallest concrete starting wedge of the Rashomon-routed governance prototype: dual-collector data layer, R(ε) of decomposable trees over a single LendingClub vintage, per-component (T, F) emission with intrinsic factor-support attribution, jsonl output, and an inspection notebook that surfaces outcome-agreer factor-support overlap.

**Architecture:** A flat `wedge/` directory at the repo root, mirroring the `probes/` tool pattern. Each module has one responsibility (collectors, models, attribution, R(ε) construction, metrics, output, orchestration). All numerical work uses pandas + scikit-learn; tests use pytest with small hand-constructed fixtures so per-component attribution is checkable against known tree structure. Git commits after each task; OTS post-commit hook auto-stamps each one.

**Tech Stack:** Python 3.14, pandas 2.x, scikit-learn 1.5+, numpy 1.26+, pytest 8.x, Jupyter for the inspection notebook. Stdlib only for json, dataclasses, pathlib, argparse.

**Spec:** `docs/superpowers/specs/2026-05-07-rashomon-prototype-wedge-design.md`

**Scope note.** This plan implements the V₁ measurement only. The V₂ *predictive* extension (spec §10 — pre-registered factor-support shifts, fit on V₂, compare measured to predicted) is a follow-on experiment that *uses* the tooling this plan produces but is not itself built here. Designing it before V₁ has produced data would violate the project's research-design discipline (premature specification of late-stage components).

---

## File Structure

```
wedge/
├── README.md
├── __init__.py
├── types.py                  # Case, PerModelOutput, FactorSupportEntry dataclasses
├── collectors/
│   ├── __init__.py
│   ├── lendingclub.py        # Real-data collector (LendingClub historical)
│   └── synthetic.py          # Boundary-extending synthetic collector
├── models.py                 # CART wrapper with T/F leaf-purity emission
├── attribution.py            # Path walk + per-component split attribution
├── rashomon.py               # Hyperparameter sweep, ε-filter, member sampling
├── metrics.py                # Outcome-agreer detection, Jaccard overlap
├── output.py                 # jsonl writer with metadata sidecar
├── run.py                    # CLI orchestration (argparse)
├── tests/
│   ├── __init__.py
│   ├── fixtures.py           # Small synthetic datasets used across tests
│   ├── test_types.py
│   ├── test_lendingclub.py
│   ├── test_synthetic.py
│   ├── test_models.py
│   ├── test_attribution.py
│   ├── test_rashomon.py
│   ├── test_metrics.py
│   └── test_output.py
└── notebooks/
    └── inspection.ipynb
```

The `wedge/` directory is a regular Python package importable from the repo root. Tests run with `pytest wedge/tests/`. The CLI runs with `python -m wedge.run`.

`pyproject.toml` is updated to add the wedge's runtime deps (pandas, scikit-learn, numpy) and pytest. The wedge does not get its own pyproject; it lives inside the existing governance project.

---

## Task 1: Project scaffolding

**Files:**
- Create: `wedge/__init__.py`
- Create: `wedge/tests/__init__.py`
- Create: `wedge/tests/fixtures.py`
- Modify: `pyproject.toml`

- [ ] **Step 1: Add wedge dependencies to pyproject.toml**

Edit `pyproject.toml` so the `dependencies` list includes the wedge deps:

```toml
[project]
name = "governance"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
requires-python = ">=3.14"
dependencies = [
    "openpyxl>=3.1.5",
    "opentimestamps-client>=0.7.2",
    "pymupdf>=1.27.2.3",
    "python-docx>=1.2.0",
    "pandas>=2.0",
    "scikit-learn>=1.5",
    "numpy>=1.26",
    "pytest>=8.0",
]
```

- [ ] **Step 2: Sync deps**

Run: `uv sync`
Expected: deps install without error; `uv.lock` updates.

- [ ] **Step 3: Create empty package files**

Create `wedge/__init__.py` with content:

```python
"""Rashomon prototype wedge.

Smallest cut of the methodology described in the May-7 working note:
a dual-collector data layer, R(ε) of decomposable trees over a single
LendingClub vintage, per-component (T, F) emission with intrinsic
factor-support attribution, and inspection of outcome-agreer overlap.

See docs/superpowers/specs/2026-05-07-rashomon-prototype-wedge-design.md.
"""
```

Create `wedge/tests/__init__.py` empty.

- [ ] **Step 4: Create test fixtures module**

Create `wedge/tests/fixtures.py`:

```python
"""Hand-constructed small datasets for unit tests.

We keep fixtures small and deterministic so that test assertions can be
checked against known tree structure rather than against statistical
properties.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


FEATURE_COLS = ["fico_proxy", "dti_proxy", "income_proxy", "history_depth"]


def tiny_separable_dataset(seed: int = 0) -> pd.DataFrame:
    """100-row dataset where label is determined by a simple rule.

    Rule: label = 1 (charged_off) iff fico_proxy < 650 OR dti_proxy > 30.
    A CART with depth >= 2 should reconstruct this rule exactly.
    """
    rng = np.random.default_rng(seed)
    n = 100
    df = pd.DataFrame({
        "fico_proxy": rng.integers(580, 800, size=n),
        "dti_proxy": rng.integers(5, 50, size=n),
        "income_proxy": rng.integers(20000, 200000, size=n),
        "history_depth": rng.integers(1, 30, size=n),
    })
    df["label"] = ((df["fico_proxy"] < 650) | (df["dti_proxy"] > 30)).astype(int)
    return df


def tiny_noisy_dataset(seed: int = 0) -> pd.DataFrame:
    """Like tiny_separable_dataset but with 10% label noise."""
    df = tiny_separable_dataset(seed=seed)
    rng = np.random.default_rng(seed + 1)
    flip_mask = rng.random(len(df)) < 0.10
    df.loc[flip_mask, "label"] = 1 - df.loc[flip_mask, "label"]
    return df
```

- [ ] **Step 5: Verify package imports cleanly**

Run: `python -c "import wedge; print(wedge.__doc__[:60])"`
Expected: prints the first 60 chars of the wedge docstring.

- [ ] **Step 6: Run pytest to confirm test discovery works (no tests yet)**

Run: `pytest wedge/tests/ -v`
Expected: `no tests ran` exit code 5 (no failures).

- [ ] **Step 7: Commit**

```bash
git add pyproject.toml uv.lock wedge/__init__.py wedge/tests/__init__.py wedge/tests/fixtures.py
git commit -m "wedge: scaffold package and test fixtures"
```

---

## Task 2: Per-case data structures

**Files:**
- Create: `wedge/types.py`
- Create: `wedge/tests/test_types.py`

- [ ] **Step 1: Write the failing test for FactorSupportEntry round-trip**

Create `wedge/tests/test_types.py`:

```python
"""Tests for wedge.types — case schema and jsonl round-trip."""

from __future__ import annotations

import json

from wedge.types import (
    Case,
    FactorSupportEntry,
    PerModelOutput,
    case_from_json,
    case_to_json,
)


def test_factor_support_entry_round_trip():
    entry = FactorSupportEntry(feature="fico_proxy", weight=0.42)
    payload = json.dumps(entry.to_dict())
    restored = FactorSupportEntry.from_dict(json.loads(payload))
    assert restored == entry


def test_per_model_output_round_trip():
    pmo = PerModelOutput(
        model_id="tree_1",
        T=0.72,
        F=0.21,
        factor_support_T=[FactorSupportEntry("fico_proxy", 0.4)],
        factor_support_F=[FactorSupportEntry("dti_proxy", 0.5)],
        path=["fico_proxy > 680", "dti_proxy <= 30"],
        leaf="leaf_42",
    )
    payload = json.dumps(pmo.to_dict())
    restored = PerModelOutput.from_dict(json.loads(payload))
    assert restored == pmo


def test_case_round_trip_real():
    case = Case(
        case_id="abc-123",
        origin="real",
        synthetic_role=None,
        vintage="2015Q3",
        features={"fico_proxy": 720, "dti_proxy": 18},
        label=0,
        per_model=[
            PerModelOutput(
                model_id="tree_1",
                T=0.85,
                F=0.10,
                factor_support_T=[FactorSupportEntry("fico_proxy", 0.6)],
                factor_support_F=[],
                path=["fico_proxy > 680"],
                leaf="leaf_3",
            )
        ],
    )
    payload = case_to_json(case)
    restored = case_from_json(payload)
    assert restored == case


def test_case_round_trip_synthetic_no_label():
    case = Case(
        case_id="syn-1",
        origin="synthetic",
        synthetic_role="hypothetical-scenario",
        vintage="2015Q3",
        features={"fico_proxy": 600, "dti_proxy": 45},
        label=None,
        per_model=[],
    )
    payload = case_to_json(case)
    restored = case_from_json(payload)
    assert restored == case
    assert restored.label is None
    assert restored.synthetic_role == "hypothetical-scenario"
```

- [ ] **Step 2: Run tests, verify they fail**

Run: `pytest wedge/tests/test_types.py -v`
Expected: FAIL with `ImportError: cannot import name 'Case' from 'wedge.types'`.

- [ ] **Step 3: Implement wedge/types.py**

Create `wedge/types.py`:

```python
"""Per-case schema for the Rashomon wedge.

Each Case records the origination-time features of one loan application,
the (T, F) emissions of every model in R(ε) on that case, and the
per-component factor support drawn from each model's intrinsic structure.

Synthetic cases carry origin="synthetic" and a synthetic_role tag per
the May-6 synthetic/real-data taxonomy. They do not carry labels (no
realized outcome) and the analysis layer must never elide the origin tag.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
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
```

- [ ] **Step 4: Run tests, verify they pass**

Run: `pytest wedge/tests/test_types.py -v`
Expected: 4 tests pass.

- [ ] **Step 5: Commit**

```bash
git add wedge/types.py wedge/tests/test_types.py
git commit -m "wedge: add Case schema with jsonl round-trip"
```

---

## Task 3: LendingClub real-data collector

**Files:**
- Create: `wedge/collectors/__init__.py`
- Create: `wedge/collectors/lendingclub.py`
- Create: `wedge/tests/test_lendingclub.py`

- [ ] **Step 1: Create the collectors package**

Create `wedge/collectors/__init__.py` empty.

- [ ] **Step 2: Write the failing test**

Create `wedge/tests/test_lendingclub.py`:

```python
"""Tests for wedge.collectors.lendingclub."""

from __future__ import annotations

import io

import pandas as pd

from wedge.collectors.lendingclub import (
    derive_label,
    filter_to_vintage,
    load_cases,
)


def _sample_csv() -> str:
    return (
        "issue_d,term,loan_status,fico_range_low,dti,annual_inc,emp_length\n"
        "Jul-2015, 36 months,Charged Off,640,28,55000, 5 years\n"
        "Aug-2015, 36 months,Fully Paid,720,15,90000,10 years\n"
        "Sep-2015, 36 months,Current,700,20,75000, 3 years\n"
        "Sep-2015, 60 months,Fully Paid,710,18,80000, 8 years\n"
        "Oct-2015, 36 months,Late (31-120 days),650,30,50000, 2 years\n"
    )


def test_filter_to_vintage_keeps_only_36mo_q3_2015_terminal():
    df = pd.read_csv(io.StringIO(_sample_csv()))
    filtered = filter_to_vintage(df, vintage="2015Q3", term="36 months")
    # Two rows match: Jul-2015 36mo Charged Off, Aug-2015 36mo Fully Paid.
    # Sep-2015 36mo is Current (not terminal), filtered out.
    # Sep-2015 60mo wrong term, filtered out.
    # Oct-2015 wrong quarter and Late, filtered out.
    assert len(filtered) == 2
    assert set(filtered["loan_status"]) == {"Charged Off", "Fully Paid"}


def test_derive_label_binary():
    df = pd.DataFrame({"loan_status": ["Charged Off", "Fully Paid"]})
    df["label"] = derive_label(df["loan_status"])
    assert df["label"].tolist() == [1, 0]


def test_load_cases_returns_case_objects(tmp_path):
    csv_path = tmp_path / "lc.csv"
    csv_path.write_text(_sample_csv())
    cases = load_cases(csv_path, vintage="2015Q3", term="36 months")
    assert len(cases) == 2
    for c in cases:
        assert c.origin == "real"
        assert c.synthetic_role is None
        assert c.vintage == "2015Q3"
        assert c.label in (0, 1)
        assert "fico_range_low" in c.features
        assert "dti" in c.features
```

- [ ] **Step 3: Run tests, verify they fail**

Run: `pytest wedge/tests/test_lendingclub.py -v`
Expected: FAIL with `ImportError`.

- [ ] **Step 4: Implement the collector**

Create `wedge/collectors/lendingclub.py`:

```python
"""LendingClub real-data collector.

Loads LendingClub historical loan-level data, filters to a single quarterly
vintage and term, derives the binary terminal-outcome label, and emits Case
objects with origin="real". Excludes loans without a terminal outcome
(Current, Late, In Grace Period) and any loan whose observation window
doesn't extend to loan_term + 6 months.

See docs/superpowers/specs/2026-05-07-rashomon-prototype-wedge-design.md
section 4.1 for design rationale (single-vintage scope, terminal-outcome
restriction, conditional-on-approval acknowledgment).
"""

from __future__ import annotations

import uuid
from pathlib import Path

import pandas as pd

from wedge.types import Case


TERMINAL_STATUSES = {"Fully Paid", "Charged Off"}
PAID = "Fully Paid"
CHARGED_OFF = "Charged Off"

# Origination-time features used by the wedge. Excludes any post-origination
# feature (payment history etc.) — those would leak.
ORIGINATION_FEATURE_COLS = [
    "fico_range_low",
    "dti",
    "annual_inc",
    "emp_length",
]


_QUARTER_MONTHS = {
    "Q1": {"Jan", "Feb", "Mar"},
    "Q2": {"Apr", "May", "Jun"},
    "Q3": {"Jul", "Aug", "Sep"},
    "Q4": {"Oct", "Nov", "Dec"},
}


def _parse_vintage(vintage: str) -> tuple[str, set[str]]:
    """Parse a vintage string like '2015Q3' into (year, set_of_month_abbrs)."""
    if len(vintage) != 6 or vintage[4] != "Q":
        raise ValueError(f"vintage must look like '2015Q3', got {vintage!r}")
    year, quarter_key = vintage[:4], vintage[4:]
    if quarter_key not in _QUARTER_MONTHS:
        raise ValueError(f"unknown quarter {quarter_key!r}")
    return year, _QUARTER_MONTHS[quarter_key]


def filter_to_vintage(df: pd.DataFrame, *, vintage: str, term: str) -> pd.DataFrame:
    """Keep rows whose issue_d falls in the named quarter, term matches, and
    loan_status is terminal (Fully Paid / Charged Off)."""
    year, months = _parse_vintage(vintage)
    issue_d = df["issue_d"].astype(str).str.strip()
    issue_month = issue_d.str.slice(0, 3)
    issue_year = issue_d.str.slice(-4)
    term_norm = df["term"].astype(str).str.strip()
    status = df["loan_status"].astype(str).str.strip()
    mask = (
        issue_month.isin(months)
        & (issue_year == year)
        & (term_norm == term)
        & status.isin(TERMINAL_STATUSES)
    )
    return df.loc[mask].reset_index(drop=True)


def derive_label(loan_status: pd.Series) -> pd.Series:
    """Map terminal loan_status to binary label: charged_off=1, paid=0."""
    return (loan_status.astype(str).str.strip() == CHARGED_OFF).astype(int)


def load_cases(
    csv_path: Path | str,
    *,
    vintage: str,
    term: str,
    feature_cols: list[str] | None = None,
) -> list[Case]:
    """Load LendingClub data from a CSV and emit Case objects for the vintage.

    Parameters
    ----------
    csv_path : path to LendingClub CSV (Kaggle mirror or original platform export).
    vintage  : e.g. "2015Q3". See _parse_vintage.
    term     : e.g. "36 months". Must exactly match the CSV's `term` field
               (LendingClub publishes this with a leading space; both " 36 months"
               and "36 months" are handled by the strip in filter_to_vintage).
    feature_cols : columns to retain as origination features. Defaults to
                   ORIGINATION_FEATURE_COLS.
    """
    feature_cols = feature_cols or ORIGINATION_FEATURE_COLS
    df = pd.read_csv(csv_path)
    df = filter_to_vintage(df, vintage=vintage, term=term)
    df["label"] = derive_label(df["loan_status"])
    cases: list[Case] = []
    for _, row in df.iterrows():
        features = {col: row[col] for col in feature_cols if col in df.columns}
        cases.append(
            Case(
                case_id=str(uuid.uuid4()),
                origin="real",
                synthetic_role=None,
                vintage=vintage,
                features=features,
                label=int(row["label"]),
                per_model=[],
            )
        )
    return cases
```

- [ ] **Step 5: Run tests, verify they pass**

Run: `pytest wedge/tests/test_lendingclub.py -v`
Expected: 3 tests pass.

- [ ] **Step 6: Commit**

```bash
git add wedge/collectors/__init__.py wedge/collectors/lendingclub.py wedge/tests/test_lendingclub.py
git commit -m "wedge: add LendingClub real-data collector"
```

---

## Task 4: Synthetic boundary-extending collector

**Files:**
- Create: `wedge/collectors/synthetic.py`
- Create: `wedge/tests/test_synthetic.py`

- [ ] **Step 1: Write the failing test**

Create `wedge/tests/test_synthetic.py`:

```python
"""Tests for wedge.collectors.synthetic."""

from __future__ import annotations

import numpy as np

from wedge.collectors.synthetic import generate_boundary_cases
from wedge.tests.fixtures import tiny_separable_dataset


def test_generate_returns_synthetic_origin():
    real = tiny_separable_dataset(seed=0)
    syn = generate_boundary_cases(real, n=20, vintage="2015Q3", seed=0)
    assert len(syn) == 20
    for c in syn:
        assert c.origin == "synthetic"
        assert c.synthetic_role == "hypothetical-scenario"
        assert c.label is None
        assert c.vintage == "2015Q3"


def test_generate_extends_into_lower_fico_tail():
    """Boundary extension should produce some cases below the real-data floor."""
    real = tiny_separable_dataset(seed=0)
    real_fico_min = real["fico_proxy"].min()
    syn = generate_boundary_cases(real, n=200, vintage="2015Q3", seed=0)
    syn_fico = [c.features["fico_proxy"] for c in syn]
    # We deliberately extend; expect at least some synthetic cases below real min.
    below_count = sum(1 for x in syn_fico if x < real_fico_min)
    assert below_count > 0


def test_generate_marginal_features_present():
    real = tiny_separable_dataset(seed=0)
    syn = generate_boundary_cases(real, n=10, vintage="2015Q3", seed=0)
    for c in syn:
        # Must have all real-data feature columns except 'label'.
        for col in ["fico_proxy", "dti_proxy", "income_proxy", "history_depth"]:
            assert col in c.features


def test_generate_reproducible_with_seed():
    real = tiny_separable_dataset(seed=0)
    syn_a = generate_boundary_cases(real, n=10, vintage="2015Q3", seed=42)
    syn_b = generate_boundary_cases(real, n=10, vintage="2015Q3", seed=42)
    a = [c.features for c in syn_a]
    b = [c.features for c in syn_b]
    assert a == b
```

- [ ] **Step 2: Run tests, verify they fail**

Run: `pytest wedge/tests/test_synthetic.py -v`
Expected: FAIL with `ImportError`.

- [ ] **Step 3: Implement the synthetic collector**

Create `wedge/collectors/synthetic.py`:

```python
"""Boundary-extending synthetic collector.

For the wedge, the simplest realization of the synthetic-data pipeline:
sample each feature independently from the real-data marginal extended
into the rejected region by a configurable factor on the lower tail of
risk-relevant features. Real-data marginals preserve overall shape;
the lower-tail extension produces synthetic cases that look like
plausibly-rejected applicants.

This is *demonstration / hypothetical-scenario* validity-grade per the
May-6 synthetic/real-data taxonomy. It cannot support back-testing claims
or any claim that requires real outcome data. Each case is tagged
origin="synthetic", synthetic_role="hypothetical-scenario".

Better calibration (copulas, joint distribution preservation) is iteration 2.
"""

from __future__ import annotations

import uuid

import numpy as np
import pandas as pd

from wedge.types import Case


# Features for which we extend the lower tail (more risk-shaped values
# downward). For other features we sample from the real marginal directly.
RISK_FEATURES_LOWER_EXTENSION = ("fico_proxy",)
RISK_FEATURES_UPPER_EXTENSION = ("dti_proxy",)
DEFAULT_LOWER_EXTENSION_PCT = 0.10  # extend by 10% of feature range below real min
DEFAULT_UPPER_EXTENSION_PCT = 0.10  # extend by 10% above real max


def _extended_uniform(
    rng: np.random.Generator,
    n: int,
    real_min: float,
    real_max: float,
    *,
    lower_extension_pct: float = 0.0,
    upper_extension_pct: float = 0.0,
) -> np.ndarray:
    span = real_max - real_min
    lo = real_min - span * lower_extension_pct
    hi = real_max + span * upper_extension_pct
    return rng.uniform(lo, hi, size=n)


def generate_boundary_cases(
    real: pd.DataFrame,
    *,
    n: int,
    vintage: str,
    seed: int = 0,
    lower_extension_pct: float = DEFAULT_LOWER_EXTENSION_PCT,
    upper_extension_pct: float = DEFAULT_UPPER_EXTENSION_PCT,
) -> list[Case]:
    """Generate `n` synthetic cases calibrated to real's marginals, extending
    the lower tail of RISK_FEATURES_LOWER_EXTENSION and the upper tail of
    RISK_FEATURES_UPPER_EXTENSION.

    Parameters
    ----------
    real : the real-data DataFrame whose marginals we sample from.
    n    : number of synthetic cases to generate.
    vintage : vintage tag attached to each synthetic case (matches the real
              dataset's vintage; we are extending the same vintage's
              hypothetical population, not generating cross-vintage data).
    seed : RNG seed for reproducibility.
    """
    rng = np.random.default_rng(seed)
    feature_cols = [c for c in real.columns if c != "label"]
    samples = {}
    for col in feature_cols:
        real_col = real[col].astype(float)
        lower_pct = lower_extension_pct if col in RISK_FEATURES_LOWER_EXTENSION else 0.0
        upper_pct = upper_extension_pct if col in RISK_FEATURES_UPPER_EXTENSION else 0.0
        samples[col] = _extended_uniform(
            rng,
            n,
            real_min=float(real_col.min()),
            real_max=float(real_col.max()),
            lower_extension_pct=lower_pct,
            upper_extension_pct=upper_pct,
        )
    cases: list[Case] = []
    for i in range(n):
        features = {col: float(samples[col][i]) for col in feature_cols}
        cases.append(
            Case(
                case_id=str(uuid.uuid4()),
                origin="synthetic",
                synthetic_role="hypothetical-scenario",
                vintage=vintage,
                features=features,
                label=None,
                per_model=[],
            )
        )
    return cases
```

- [ ] **Step 4: Run tests, verify they pass**

Run: `pytest wedge/tests/test_synthetic.py -v`
Expected: 4 tests pass.

- [ ] **Step 5: Commit**

```bash
git add wedge/collectors/synthetic.py wedge/tests/test_synthetic.py
git commit -m "wedge: add boundary-extending synthetic collector"
```

---

## Task 5: CART wrapper with T/F leaf-purity emission

**Files:**
- Create: `wedge/models.py`
- Create: `wedge/tests/test_models.py`

- [ ] **Step 1: Write the failing tests**

Create `wedge/tests/test_models.py`:

```python
"""Tests for wedge.models — CART wrapper with T/F emission."""

from __future__ import annotations

import numpy as np

from wedge.models import CartModel, fit_model
from wedge.tests.fixtures import FEATURE_COLS, tiny_separable_dataset


def test_fit_model_reaches_full_accuracy_on_separable():
    df = tiny_separable_dataset(seed=0)
    model = fit_model(
        df[FEATURE_COLS],
        df["label"],
        model_id="m1",
        max_depth=4,
        min_samples_leaf=5,
        feature_subset=tuple(FEATURE_COLS),
        random_state=0,
    )
    preds = model.predict(df[FEATURE_COLS])
    assert (preds == df["label"]).mean() > 0.95


def test_emit_returns_T_plus_F_equal_one():
    df = tiny_separable_dataset(seed=0)
    model = fit_model(
        df[FEATURE_COLS],
        df["label"],
        model_id="m1",
        max_depth=4,
        min_samples_leaf=5,
        feature_subset=tuple(FEATURE_COLS),
        random_state=0,
    )
    sample = df.iloc[0:5][FEATURE_COLS]
    emissions = [model.emit_for_case(sample.iloc[i].to_dict()) for i in range(5)]
    for e in emissions:
        assert abs(e["T"] + e["F"] - 1.0) < 1e-9
        assert 0.0 <= e["T"] <= 1.0
        assert 0.0 <= e["F"] <= 1.0


def test_emit_T_high_for_low_risk_case():
    df = tiny_separable_dataset(seed=0)
    model = fit_model(
        df[FEATURE_COLS],
        df["label"],
        model_id="m1",
        max_depth=4,
        min_samples_leaf=5,
        feature_subset=tuple(FEATURE_COLS),
        random_state=0,
    )
    # Low-risk case per the rule: high FICO, low DTI -> label=0 -> T should be high.
    low_risk = {"fico_proxy": 750, "dti_proxy": 10, "income_proxy": 100000, "history_depth": 20}
    e = model.emit_for_case(low_risk)
    assert e["T"] > 0.7


def test_emit_F_high_for_high_risk_case():
    df = tiny_separable_dataset(seed=0)
    model = fit_model(
        df[FEATURE_COLS],
        df["label"],
        model_id="m1",
        max_depth=4,
        min_samples_leaf=5,
        feature_subset=tuple(FEATURE_COLS),
        random_state=0,
    )
    high_risk = {"fico_proxy": 600, "dti_proxy": 45, "income_proxy": 30000, "history_depth": 2}
    e = model.emit_for_case(high_risk)
    assert e["F"] > 0.7


def test_feature_subset_restricts_features():
    df = tiny_separable_dataset(seed=0)
    model = fit_model(
        df[FEATURE_COLS],
        df["label"],
        model_id="m_restricted",
        max_depth=4,
        min_samples_leaf=5,
        feature_subset=("fico_proxy", "dti_proxy"),
        random_state=0,
    )
    assert tuple(model.feature_subset) == ("fico_proxy", "dti_proxy")
    # Predict using only the subset columns; ignored columns should not affect output.
    case_a = {"fico_proxy": 750, "dti_proxy": 10, "income_proxy": 100000, "history_depth": 20}
    case_b = {"fico_proxy": 750, "dti_proxy": 10, "income_proxy": 30000, "history_depth": 2}
    e_a = model.emit_for_case(case_a)
    e_b = model.emit_for_case(case_b)
    assert e_a["T"] == e_b["T"]
    assert e_a["F"] == e_b["F"]
```

- [ ] **Step 2: Run tests, verify they fail**

Run: `pytest wedge/tests/test_models.py -v`
Expected: FAIL with `ImportError`.

- [ ] **Step 3: Implement the CART wrapper**

Create `wedge/models.py`:

```python
"""CART wrapper for the Rashomon wedge.

Each CartModel wraps a fitted sklearn DecisionTreeClassifier and adds:

  - per-case (T, F) emission from leaf class proportions
  - identification of the leaf the case lands in
  - the decision path the case took
  - the feature subset the model was fit on (so that downstream attribution
    can restrict its analysis to the model's features)

For a binary classification leaf with class proportions (p_paid, p_charged):
  T = p_paid       (confidence in grant)
  F = p_charged    (concern; evidence supporting deny)

These satisfy T + F = 1 by construction in the wedge — see spec §7 for
why we accept this and what iteration 2's richer emission would do.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier


@dataclass
class CartModel:
    """A fitted CART with T/F emission helpers."""

    model_id: str
    tree: DecisionTreeClassifier
    feature_subset: tuple[str, ...]
    classes_: tuple[int, ...]  # sklearn's classes_, copied for clarity

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        return self.tree.predict(X[list(self.feature_subset)].to_numpy())

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        return self.tree.predict_proba(X[list(self.feature_subset)].to_numpy())

    def emit_for_case(self, case_features: dict[str, Any]) -> dict[str, Any]:
        """Return {'T', 'F', 'leaf', 'leaf_id'} for one case (a feature dict).

        T and F are leaf class proportions. leaf is a string label like
        "leaf_<node_id>"; leaf_id is the underlying integer node id.
        """
        x = np.asarray(
            [case_features[f] for f in self.feature_subset], dtype=float
        ).reshape(1, -1)
        leaf_id = int(self.tree.apply(x)[0])
        proba = self.tree.predict_proba(x)[0]  # in self.classes_ order
        # classes_ is sorted: 0 (paid) before 1 (charged_off) for our derive_label.
        class_order = list(self.classes_)
        if class_order == [0, 1]:
            t, f = float(proba[0]), float(proba[1])
        elif class_order == [1, 0]:
            t, f = float(proba[1]), float(proba[0])
        else:
            raise RuntimeError(
                f"unexpected class order {class_order!r}; wedge assumes binary 0/1"
            )
        return {"T": t, "F": f, "leaf": f"leaf_{leaf_id}", "leaf_id": leaf_id}


def fit_model(
    X: pd.DataFrame,
    y: pd.Series,
    *,
    model_id: str,
    max_depth: int,
    min_samples_leaf: int,
    feature_subset: tuple[str, ...],
    random_state: int = 0,
) -> CartModel:
    """Fit a single CART on the given data with the given hyperparameters.

    The feature_subset selects columns from X. Unused columns are ignored
    completely in fitting *and* in downstream emission.
    """
    cols = list(feature_subset)
    X_sub = X[cols].to_numpy()
    y_arr = y.to_numpy()
    tree = DecisionTreeClassifier(
        max_depth=max_depth,
        min_samples_leaf=min_samples_leaf,
        random_state=random_state,
    )
    tree.fit(X_sub, y_arr)
    return CartModel(
        model_id=model_id,
        tree=tree,
        feature_subset=tuple(cols),
        classes_=tuple(int(c) for c in tree.classes_),
    )
```

- [ ] **Step 4: Run tests, verify they pass**

Run: `pytest wedge/tests/test_models.py -v`
Expected: 5 tests pass.

- [ ] **Step 5: Commit**

```bash
git add wedge/models.py wedge/tests/test_models.py
git commit -m "wedge: add CART wrapper with T/F leaf-purity emission"
```

---

## Task 6: Path-walk and per-component factor support

**Files:**
- Create: `wedge/attribution.py`
- Create: `wedge/tests/test_attribution.py`

- [ ] **Step 1: Write the failing tests**

Create `wedge/tests/test_attribution.py`:

```python
"""Tests for wedge.attribution — path walk + per-component split attribution."""

from __future__ import annotations

import pandas as pd

from wedge.attribution import (
    extract_factor_support,
    walk_path,
)
from wedge.models import fit_model
from wedge.tests.fixtures import FEATURE_COLS, tiny_separable_dataset


def _trained_model():
    df = tiny_separable_dataset(seed=0)
    return fit_model(
        df[FEATURE_COLS],
        df["label"],
        model_id="m_attr",
        max_depth=4,
        min_samples_leaf=5,
        feature_subset=tuple(FEATURE_COLS),
        random_state=0,
    )


def test_walk_path_returns_decisions_root_to_leaf():
    model = _trained_model()
    case = {"fico_proxy": 750, "dti_proxy": 10, "income_proxy": 100000, "history_depth": 20}
    path = walk_path(model, case)
    # At minimum, the path describes the splits the case took.
    assert len(path) >= 1
    for entry in path:
        assert "feature" in entry
        assert "threshold" in entry
        assert "direction" in entry  # 'left' or 'right'
        assert "info_gain" in entry
        assert "chosen_grant_purity" in entry
        assert "chosen_deny_purity" in entry
        assert "unchosen_grant_purity" in entry
        assert "unchosen_deny_purity" in entry


def test_factor_support_T_includes_features_routing_toward_grant():
    """For a strongly low-risk case the per-component split should attribute
    feature gain to T (factor_support_T should be non-empty)."""
    model = _trained_model()
    low_risk = {"fico_proxy": 780, "dti_proxy": 8, "income_proxy": 100000, "history_depth": 20}
    fst, fsf = extract_factor_support(model, low_risk, top_k=5)
    # We expect at least one feature to attribute to T because the case is routed
    # to a high-grant-purity leaf along splits that increased grant purity.
    assert len(fst) >= 1
    assert all(0.0 <= e.weight <= 1.0 + 1e-9 for e in fst)


def test_factor_support_F_includes_features_routing_toward_deny():
    model = _trained_model()
    high_risk = {"fico_proxy": 590, "dti_proxy": 45, "income_proxy": 25000, "history_depth": 1}
    fst, fsf = extract_factor_support(model, high_risk, top_k=5)
    assert len(fsf) >= 1
    assert all(0.0 <= e.weight <= 1.0 + 1e-9 for e in fsf)


def test_factor_support_top_k_truncates():
    model = _trained_model()
    case = {"fico_proxy": 720, "dti_proxy": 25, "income_proxy": 60000, "history_depth": 5}
    fst, fsf = extract_factor_support(model, case, top_k=1)
    assert len(fst) <= 1
    assert len(fsf) <= 1


def test_factor_support_weights_sorted_descending():
    model = _trained_model()
    case = {"fico_proxy": 600, "dti_proxy": 40, "income_proxy": 30000, "history_depth": 3}
    fst, fsf = extract_factor_support(model, case, top_k=10)
    for entries in (fst, fsf):
        weights = [e.weight for e in entries]
        assert weights == sorted(weights, reverse=True)
```

- [ ] **Step 2: Run tests, verify they fail**

Run: `pytest wedge/tests/test_attribution.py -v`
Expected: FAIL with `ImportError`.

- [ ] **Step 3: Implement attribution**

Create `wedge/attribution.py`:

```python
"""Path-walk and per-component factor-support extraction.

For a fitted CART and a single case, walk the path from root to the
case's leaf, attribute information gain at each split to whichever
component (T or F) the chosen branch supports, and aggregate per-feature
to produce factor_support_T and factor_support_F.

Per-component split logic (spec §8 step 4):
  At each split, compare grant-purity and deny-purity of the chosen
  branch's subtree against the unchosen branch's subtree.
    - chosen_grant > unchosen_grant => attribute info gain to factor_support_T
    - chosen_deny  > unchosen_deny  => attribute info gain to factor_support_F
    - both         => attribute to both
    - neither      => attribute to neither (split is informational but
                      doesn't differentiate the components for this case).

This yields per-component differentiation: a feature can be in T-support
for one case (it routed the case toward grant-confident territory) and in
F-support for another case (it routed away from grant-confident territory).
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

import numpy as np

from wedge.models import CartModel
from wedge.types import FactorSupportEntry


# Class-index assumption: classes_ == (0, 1) so column 0 is paid (grant-purity)
# and column 1 is charged_off (deny-purity). CartModel guarantees this in fit_model.
GRANT_CLASS_IDX = 0
DENY_CLASS_IDX = 1


def _subtree_purity(tree, node_id: int) -> tuple[float, float]:
    """Return (grant_purity, deny_purity) of all training samples reaching the
    subtree rooted at `node_id`. Computed from sklearn's tree.value array."""
    # tree.value has shape (n_nodes, 1, n_classes) and stores class-count per node.
    counts = tree.value[node_id, 0]
    total = counts.sum()
    if total == 0:
        return 0.0, 0.0
    grant = float(counts[GRANT_CLASS_IDX] / total)
    deny = float(counts[DENY_CLASS_IDX] / total)
    return grant, deny


def _node_info_gain(tree, node_id: int) -> float:
    """Information gain (impurity reduction) at a split node, weighted by the
    fraction of training samples reaching the node. Uses sklearn's stored
    impurity values."""
    if tree.children_left[node_id] == tree.children_right[node_id]:
        return 0.0
    parent_impurity = float(tree.impurity[node_id])
    n_parent = float(tree.n_node_samples[node_id])
    left = int(tree.children_left[node_id])
    right = int(tree.children_right[node_id])
    n_left = float(tree.n_node_samples[left])
    n_right = float(tree.n_node_samples[right])
    weighted_child = (
        (n_left / n_parent) * float(tree.impurity[left])
        + (n_right / n_parent) * float(tree.impurity[right])
    )
    gain = parent_impurity - weighted_child
    n_total = float(tree.n_node_samples[0])
    # Weight by fraction of training samples reaching this node.
    return gain * (n_parent / n_total)


def walk_path(model: CartModel, case_features: dict[str, Any]) -> list[dict[str, Any]]:
    """Walk root-to-leaf for one case, returning a list of split-decision dicts."""
    feature_names = list(model.feature_subset)
    x = np.asarray([case_features[f] for f in feature_names], dtype=float).reshape(1, -1)
    tree = model.tree.tree_
    node_id = 0
    path: list[dict[str, Any]] = []
    while tree.children_left[node_id] != tree.children_right[node_id]:  # internal node
        feat_idx = int(tree.feature[node_id])
        threshold = float(tree.threshold[node_id])
        feat_name = feature_names[feat_idx]
        x_val = float(x[0, feat_idx])
        if x_val <= threshold:
            chosen = int(tree.children_left[node_id])
            unchosen = int(tree.children_right[node_id])
            direction = "left"
        else:
            chosen = int(tree.children_right[node_id])
            unchosen = int(tree.children_left[node_id])
            direction = "right"
        chosen_grant, chosen_deny = _subtree_purity(tree, chosen)
        unchosen_grant, unchosen_deny = _subtree_purity(tree, unchosen)
        path.append({
            "feature": feat_name,
            "threshold": threshold,
            "direction": direction,
            "info_gain": _node_info_gain(tree, node_id),
            "chosen_grant_purity": chosen_grant,
            "chosen_deny_purity": chosen_deny,
            "unchosen_grant_purity": unchosen_grant,
            "unchosen_deny_purity": unchosen_deny,
        })
        node_id = chosen
    return path


def extract_factor_support(
    model: CartModel,
    case_features: dict[str, Any],
    *,
    top_k: int = 5,
) -> tuple[list[FactorSupportEntry], list[FactorSupportEntry]]:
    """Return (factor_support_T, factor_support_F) as sorted lists of
    FactorSupportEntry, truncated to top_k each."""
    path = walk_path(model, case_features)
    by_feature_T: dict[str, float] = defaultdict(float)
    by_feature_F: dict[str, float] = defaultdict(float)
    for step in path:
        feat = step["feature"]
        gain = step["info_gain"]
        if step["chosen_grant_purity"] > step["unchosen_grant_purity"]:
            by_feature_T[feat] += gain
        if step["chosen_deny_purity"] > step["unchosen_deny_purity"]:
            by_feature_F[feat] += gain

    def _top_k(d: dict[str, float]) -> list[FactorSupportEntry]:
        items = [(name, weight) for name, weight in d.items() if weight > 0]
        items.sort(key=lambda x: x[1], reverse=True)
        return [FactorSupportEntry(feature=n, weight=float(w)) for n, w in items[:top_k]]

    return _top_k(by_feature_T), _top_k(by_feature_F)
```

- [ ] **Step 4: Run tests, verify they pass**

Run: `pytest wedge/tests/test_attribution.py -v`
Expected: 5 tests pass.

- [ ] **Step 5: Commit**

```bash
git add wedge/attribution.py wedge/tests/test_attribution.py
git commit -m "wedge: add path walk and per-component factor support"
```

---

## Task 7: R(ε) construction (sweep, filter, sample)

**Files:**
- Create: `wedge/rashomon.py`
- Create: `wedge/tests/test_rashomon.py`

- [ ] **Step 1: Write the failing tests**

Create `wedge/tests/test_rashomon.py`:

```python
"""Tests for wedge.rashomon — sweep, ε-filter, member sampling."""

from __future__ import annotations

import pandas as pd

from wedge.rashomon import (
    HyperparameterSpec,
    SweepConfig,
    build_rashomon_set,
    hyperparameter_sweep,
    select_diverse_members,
)
from wedge.tests.fixtures import FEATURE_COLS, tiny_noisy_dataset


def test_hyperparameter_sweep_returns_one_record_per_combo():
    df = tiny_noisy_dataset(seed=0)
    cfg = SweepConfig(
        max_depths=(3, 5),
        min_samples_leafs=(5, 10),
        feature_subsets=(tuple(FEATURE_COLS),),
        random_state=0,
        holdout_fraction=0.3,
    )
    results = hyperparameter_sweep(df[FEATURE_COLS], df["label"], config=cfg)
    assert len(results) == 4  # 2 depths * 2 leaf-mins * 1 subset
    for r in results:
        assert 0.0 <= r.holdout_auc <= 1.0
        assert isinstance(r.spec, HyperparameterSpec)


def test_build_rashomon_set_respects_epsilon():
    df = tiny_noisy_dataset(seed=0)
    cfg = SweepConfig(
        max_depths=(3, 5, 7),
        min_samples_leafs=(5, 10, 20),
        feature_subsets=(tuple(FEATURE_COLS),),
        random_state=0,
        holdout_fraction=0.3,
    )
    members = build_rashomon_set(
        df[FEATURE_COLS], df["label"], config=cfg, epsilon=0.05, n_members=5
    )
    assert len(members) <= 5
    assert len(members) >= 1
    # All members within epsilon of the best AUC observed in the sweep.
    aucs = [m.holdout_auc for m in members]
    best = max(aucs)
    for auc in aucs:
        assert best - auc <= 0.05 + 1e-9


def test_select_diverse_members_picks_distinct_specs():
    df = tiny_noisy_dataset(seed=0)
    cfg = SweepConfig(
        max_depths=(3, 5, 7),
        min_samples_leafs=(5, 10, 20),
        feature_subsets=(tuple(FEATURE_COLS),),
        random_state=0,
        holdout_fraction=0.3,
    )
    sweep_results = hyperparameter_sweep(df[FEATURE_COLS], df["label"], config=cfg)
    diverse = select_diverse_members(sweep_results, n=3)
    assert len(diverse) == 3
    specs = {(d.spec.max_depth, d.spec.min_samples_leaf, d.spec.feature_subset) for d in diverse}
    assert len(specs) == 3  # all distinct
```

- [ ] **Step 2: Run tests, verify they fail**

Run: `pytest wedge/tests/test_rashomon.py -v`
Expected: FAIL with `ImportError`.

- [ ] **Step 3: Implement R(ε) construction**

Create `wedge/rashomon.py`:

```python
"""R(ε) construction: hyperparameter sweep, ε filter, diversity-weighted selection.

The wedge fits a sweep of single-CART hyperparameter combinations on a
hold-out from the train set, defines ε = best_holdout_AUC - epsilon_tolerance,
and selects n_members from the within-ε candidates by farthest-point
selection in (depth, leaf_min, feature_subset) space — explicitly preferring
diversity of inductive bias over diversity of data fit.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

from wedge.models import CartModel, fit_model


@dataclass(frozen=True)
class HyperparameterSpec:
    max_depth: int
    min_samples_leaf: int
    feature_subset: tuple[str, ...]


@dataclass
class SweepResult:
    spec: HyperparameterSpec
    holdout_auc: float


@dataclass
class SweepConfig:
    max_depths: tuple[int, ...]
    min_samples_leafs: tuple[int, ...]
    feature_subsets: tuple[tuple[str, ...], ...]
    random_state: int = 0
    holdout_fraction: float = 0.3


def hyperparameter_sweep(
    X: pd.DataFrame, y: pd.Series, *, config: SweepConfig
) -> list[SweepResult]:
    X_fit, X_holdout, y_fit, y_holdout = train_test_split(
        X, y, test_size=config.holdout_fraction, random_state=config.random_state, stratify=y
    )
    results: list[SweepResult] = []
    for depth in config.max_depths:
        for leaf_min in config.min_samples_leafs:
            for subset in config.feature_subsets:
                model = fit_model(
                    X_fit,
                    y_fit,
                    model_id=f"sweep_d{depth}_l{leaf_min}_s{hash(subset) & 0xFFFF}",
                    max_depth=depth,
                    min_samples_leaf=leaf_min,
                    feature_subset=subset,
                    random_state=config.random_state,
                )
                proba = model.predict_proba(X_holdout)[:, list(model.classes_).index(1)]
                auc = float(roc_auc_score(y_holdout, proba))
                results.append(
                    SweepResult(
                        spec=HyperparameterSpec(
                            max_depth=depth,
                            min_samples_leaf=leaf_min,
                            feature_subset=subset,
                        ),
                        holdout_auc=auc,
                    )
                )
    return results


def select_diverse_members(
    sweep_results: list[SweepResult], *, n: int
) -> list[SweepResult]:
    """Greedy farthest-point selection in spec space.

    Encodes each spec as a numeric vector (max_depth, min_samples_leaf,
    len(feature_subset)) and picks members iteratively: start with the
    highest-AUC candidate, then repeatedly add the candidate maximizing
    minimum L2 distance to already-selected specs. Ties broken by AUC.
    """
    if n <= 0 or not sweep_results:
        return []
    candidates = sorted(sweep_results, key=lambda r: r.holdout_auc, reverse=True)
    selected = [candidates[0]]
    remaining = candidates[1:]

    def _vec(r: SweepResult) -> np.ndarray:
        return np.array(
            [r.spec.max_depth, r.spec.min_samples_leaf, len(r.spec.feature_subset)],
            dtype=float,
        )

    while len(selected) < n and remaining:
        best_idx = None
        best_score = -1.0
        for i, cand in enumerate(remaining):
            min_dist = min(np.linalg.norm(_vec(cand) - _vec(s)) for s in selected)
            if min_dist > best_score or (
                abs(min_dist - best_score) < 1e-12
                and (best_idx is None or cand.holdout_auc > remaining[best_idx].holdout_auc)
            ):
                best_score = min_dist
                best_idx = i
        if best_idx is None:
            break
        selected.append(remaining.pop(best_idx))
    return selected


def build_rashomon_set(
    X: pd.DataFrame,
    y: pd.Series,
    *,
    config: SweepConfig,
    epsilon: float,
    n_members: int,
) -> list[SweepResult]:
    """Run the sweep, filter to within-ε of best AUC, select diverse members.

    Returns up to n_members SweepResults whose specs are the ones the caller
    will then re-fit on the full training set for emission.
    """
    sweep = hyperparameter_sweep(X, y, config=config)
    if not sweep:
        return []
    best = max(r.holdout_auc for r in sweep)
    in_epsilon = [r for r in sweep if best - r.holdout_auc <= epsilon + 1e-9]
    return select_diverse_members(in_epsilon, n=n_members)


def refit_members(
    X: pd.DataFrame, y: pd.Series, *, members: list[SweepResult], random_state: int = 0
) -> list[CartModel]:
    """Re-fit each selected member on the full (X, y), assigning final model_ids."""
    out: list[CartModel] = []
    for i, m in enumerate(members):
        out.append(
            fit_model(
                X,
                y,
                model_id=f"tree_{i+1}",
                max_depth=m.spec.max_depth,
                min_samples_leaf=m.spec.min_samples_leaf,
                feature_subset=m.spec.feature_subset,
                random_state=random_state,
            )
        )
    return out
```

- [ ] **Step 4: Run tests, verify they pass**

Run: `pytest wedge/tests/test_rashomon.py -v`
Expected: 3 tests pass.

- [ ] **Step 5: Commit**

```bash
git add wedge/rashomon.py wedge/tests/test_rashomon.py
git commit -m "wedge: add R(epsilon) construction and diversity-weighted member selection"
```

---

## Task 8: Outcome-agreer detection and Jaccard overlap

**Files:**
- Create: `wedge/metrics.py`
- Create: `wedge/tests/test_metrics.py`

- [ ] **Step 1: Write the failing tests**

Create `wedge/tests/test_metrics.py`:

```python
"""Tests for wedge.metrics."""

from __future__ import annotations

from wedge.metrics import (
    is_outcome_agreer,
    pairwise_factor_support_overlap,
)
from wedge.types import FactorSupportEntry, PerModelOutput


def _pmo(model_id, T, F, fs_T_features=(), fs_F_features=()):
    return PerModelOutput(
        model_id=model_id,
        T=T,
        F=F,
        factor_support_T=[FactorSupportEntry(f, 0.5) for f in fs_T_features],
        factor_support_F=[FactorSupportEntry(f, 0.5) for f in fs_F_features],
        path=[],
        leaf="leaf_x",
    )


def test_outcome_agreer_all_grant_with_tight_spread():
    pmos = [
        _pmo("m1", T=0.80, F=0.20),
        _pmo("m2", T=0.78, F=0.22),
        _pmo("m3", T=0.75, F=0.25),
    ]
    assert is_outcome_agreer(pmos, t_spread_max=0.10) is True


def test_outcome_agreer_split_decisions_returns_false():
    pmos = [
        _pmo("m1", T=0.80, F=0.20),
        _pmo("m2", T=0.40, F=0.60),  # this one votes deny
    ]
    assert is_outcome_agreer(pmos, t_spread_max=0.10) is False


def test_outcome_agreer_tspread_too_wide_returns_false():
    pmos = [
        _pmo("m1", T=0.95, F=0.05),
        _pmo("m2", T=0.55, F=0.45),  # same direction (>0.5) but spread = 0.40
    ]
    assert is_outcome_agreer(pmos, t_spread_max=0.10) is False


def test_pairwise_overlap_identical_supports_returns_one():
    pmos = [
        _pmo("m1", T=0.8, F=0.2, fs_T_features=("a", "b", "c")),
        _pmo("m2", T=0.8, F=0.2, fs_T_features=("a", "b", "c")),
    ]
    overlap_T, overlap_F = pairwise_factor_support_overlap(pmos)
    assert abs(overlap_T - 1.0) < 1e-9


def test_pairwise_overlap_disjoint_supports_returns_zero():
    pmos = [
        _pmo("m1", T=0.8, F=0.2, fs_T_features=("a", "b")),
        _pmo("m2", T=0.8, F=0.2, fs_T_features=("c", "d")),
    ]
    overlap_T, overlap_F = pairwise_factor_support_overlap(pmos)
    assert overlap_T == 0.0


def test_pairwise_overlap_partial():
    pmos = [
        _pmo("m1", T=0.8, F=0.2, fs_T_features=("a", "b", "c")),
        _pmo("m2", T=0.8, F=0.2, fs_T_features=("b", "c", "d")),
    ]
    overlap_T, _ = pairwise_factor_support_overlap(pmos)
    # Jaccard({a,b,c}, {b,c,d}) = |{b,c}| / |{a,b,c,d}| = 2/4 = 0.5
    assert abs(overlap_T - 0.5) < 1e-9


def test_pairwise_overlap_three_models_averages_pairs():
    pmos = [
        _pmo("m1", T=0.8, F=0.2, fs_T_features=("a", "b")),
        _pmo("m2", T=0.8, F=0.2, fs_T_features=("a", "b")),
        _pmo("m3", T=0.8, F=0.2, fs_T_features=("c", "d")),
    ]
    overlap_T, _ = pairwise_factor_support_overlap(pmos)
    # Pairs: (m1,m2)=1.0, (m1,m3)=0.0, (m2,m3)=0.0  -> mean = 1/3
    assert abs(overlap_T - 1.0 / 3.0) < 1e-9
```

- [ ] **Step 2: Run tests, verify they fail**

Run: `pytest wedge/tests/test_metrics.py -v`
Expected: FAIL with `ImportError`.

- [ ] **Step 3: Implement metrics**

Create `wedge/metrics.py`:

```python
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
```

- [ ] **Step 4: Run tests, verify they pass**

Run: `pytest wedge/tests/test_metrics.py -v`
Expected: 7 tests pass.

- [ ] **Step 5: Commit**

```bash
git add wedge/metrics.py wedge/tests/test_metrics.py
git commit -m "wedge: add outcome-agreer detection and pairwise Jaccard overlap"
```

---

## Task 9: jsonl writer with metadata sidecar

**Files:**
- Create: `wedge/output.py`
- Create: `wedge/tests/test_output.py`

- [ ] **Step 1: Write the failing tests**

Create `wedge/tests/test_output.py`:

```python
"""Tests for wedge.output."""

from __future__ import annotations

import json

from wedge.output import RunMetadata, write_run
from wedge.types import Case


def _case(case_id, label=0):
    return Case(
        case_id=case_id,
        origin="real",
        synthetic_role=None,
        vintage="2015Q3",
        features={"fico_proxy": 720, "dti_proxy": 18},
        label=label,
        per_model=[],
    )


def test_write_run_creates_jsonl_and_meta(tmp_path):
    cases = [_case("a"), _case("b", label=1)]
    meta = RunMetadata(
        run_id="2026-05-07T12:00:00Z",
        vintage="2015Q3",
        epsilon=0.02,
        random_seed=0,
        members=[
            {"model_id": "tree_1", "max_depth": 5, "min_samples_leaf": 50, "feature_subset": ["a", "b"]},
        ],
        notes="wedge first run",
    )
    out_jsonl, out_meta = write_run(cases, meta, output_dir=tmp_path)
    # Files exist.
    assert out_jsonl.exists()
    assert out_meta.exists()
    # jsonl: one record per case.
    lines = out_jsonl.read_text().strip().split("\n")
    assert len(lines) == 2
    parsed = [json.loads(line) for line in lines]
    assert {p["case_id"] for p in parsed} == {"a", "b"}
    # Meta sidecar carries the run metadata.
    meta_payload = json.loads(out_meta.read_text())
    assert meta_payload["run_id"] == "2026-05-07T12:00:00Z"
    assert meta_payload["vintage"] == "2015Q3"
    assert meta_payload["epsilon"] == 0.02


def test_write_run_filenames_use_run_id_safely(tmp_path):
    meta = RunMetadata(
        run_id="2026-05-07T12-00-00Z",  # safe characters only
        vintage="2015Q3",
        epsilon=0.02,
        random_seed=0,
        members=[],
    )
    out_jsonl, out_meta = write_run([], meta, output_dir=tmp_path)
    assert "2026-05-07T12-00-00Z" in out_jsonl.name
    assert "2026-05-07T12-00-00Z" in out_meta.name
```

- [ ] **Step 2: Run tests, verify they fail**

Run: `pytest wedge/tests/test_output.py -v`
Expected: FAIL with `ImportError`.

- [ ] **Step 3: Implement output**

Create `wedge/output.py`:

```python
"""jsonl run writer with metadata sidecar.

A run produces two files in the output directory:

  runs/<run_id>.jsonl       — one Case record per line
  runs/<run_id>-meta.json   — run metadata: vintage, epsilon, members, etc.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from wedge.types import Case, case_to_json


@dataclass
class RunMetadata:
    run_id: str
    vintage: str
    epsilon: float
    random_seed: int
    members: list[dict[str, Any]] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def write_run(
    cases: list[Case], meta: RunMetadata, *, output_dir: Path | str
) -> tuple[Path, Path]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = output_dir / f"{meta.run_id}.jsonl"
    meta_path = output_dir / f"{meta.run_id}-meta.json"
    with jsonl_path.open("w", encoding="utf-8") as f:
        for c in cases:
            f.write(case_to_json(c))
            f.write("\n")
    with meta_path.open("w", encoding="utf-8") as f:
        json.dump(meta.to_dict(), f, indent=2)
    return jsonl_path, meta_path
```

- [ ] **Step 4: Run tests, verify they pass**

Run: `pytest wedge/tests/test_output.py -v`
Expected: 2 tests pass.

- [ ] **Step 5: Commit**

```bash
git add wedge/output.py wedge/tests/test_output.py
git commit -m "wedge: add jsonl writer with metadata sidecar"
```

---

## Task 10: CLI orchestration

**Files:**
- Create: `wedge/run.py`

- [ ] **Step 1: Implement the orchestration script**

Create `wedge/run.py`:

```python
"""CLI orchestration for the Rashomon wedge.

Pipeline:
  1. Load real data via the LendingClub collector for the given vintage.
  2. Optionally generate synthetic boundary cases via the synthetic collector.
  3. Build R(ε): hyperparameter sweep on the train hold-out, ε filter,
     diversity-weighted selection of n members.
  4. Re-fit the selected members on the full training set.
  5. For each eval case (real + synthetic), emit per-model (T, F, leaf)
     and extract per-component factor support (top-k features).
  6. Write the resulting Case records to a jsonl + metadata sidecar.

Usage:
  python -m wedge.run \\
      --csv path/to/lendingclub.csv \\
      --vintage 2015Q3 \\
      --term '36 months' \\
      --epsilon 0.02 \\
      --n-members 5 \\
      --top-k 5 \\
      --synthetic-n 200 \\
      --output-dir runs/
"""

from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from wedge.attribution import extract_factor_support
from wedge.collectors.lendingclub import (
    ORIGINATION_FEATURE_COLS,
    derive_label,
    filter_to_vintage,
)
from wedge.collectors.synthetic import generate_boundary_cases
from wedge.output import RunMetadata, write_run
from wedge.rashomon import SweepConfig, build_rashomon_set, refit_members
from wedge.types import Case, PerModelOutput


def _now_iso() -> str:
    return dt.datetime.now(tz=dt.timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")


def _to_case_real(row, vintage, feature_cols) -> Case:
    import uuid
    features = {col: row[col] for col in feature_cols}
    return Case(
        case_id=str(uuid.uuid4()),
        origin="real",
        synthetic_role=None,
        vintage=vintage,
        features=features,
        label=int(row["label"]),
        per_model=[],
    )


def _emit_per_model(model, case_features, top_k):
    e = model.emit_for_case(case_features)
    fst, fsf = extract_factor_support(model, case_features, top_k=top_k)
    return PerModelOutput(
        model_id=model.model_id,
        T=e["T"],
        F=e["F"],
        factor_support_T=fst,
        factor_support_F=fsf,
        path=[],  # spec §11 keeps path optional in jsonl; populating it is iteration 2
        leaf=e["leaf"],
    )


def main() -> int:
    p = argparse.ArgumentParser(description="Run the Rashomon wedge.")
    p.add_argument("--csv", type=Path, required=True, help="LendingClub CSV path")
    p.add_argument("--vintage", default="2015Q3")
    p.add_argument("--term", default="36 months")
    p.add_argument("--epsilon", type=float, default=0.02)
    p.add_argument("--n-members", type=int, default=5)
    p.add_argument("--top-k", type=int, default=5)
    p.add_argument("--synthetic-n", type=int, default=200)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--output-dir", type=Path, default=Path("runs"))
    args = p.parse_args()

    # 1. Load real data.
    df = pd.read_csv(args.csv)
    df = filter_to_vintage(df, vintage=args.vintage, term=args.term)
    df["label"] = derive_label(df["loan_status"])
    feature_cols = [c for c in ORIGINATION_FEATURE_COLS if c in df.columns]

    # 2. Train/eval split.
    train_df, eval_df = train_test_split(
        df, test_size=0.30, random_state=args.seed, stratify=df["label"]
    )
    X_train, y_train = train_df[feature_cols], train_df["label"]
    X_eval, y_eval = eval_df[feature_cols], eval_df["label"]

    # 3. Build R(ε).
    cfg = SweepConfig(
        max_depths=(4, 6, 8, 10, 12),
        min_samples_leafs=(25, 50, 100, 200, 400),
        feature_subsets=(tuple(feature_cols),),
        random_state=args.seed,
        holdout_fraction=0.30,
    )
    members = build_rashomon_set(
        X_train, y_train, config=cfg, epsilon=args.epsilon, n_members=args.n_members
    )
    fitted = refit_members(X_train, y_train, members=members, random_state=args.seed)

    # 4. Build eval cases (real + synthetic).
    real_cases: list[Case] = []
    for _, row in eval_df.iterrows():
        real_cases.append(_to_case_real(row, args.vintage, feature_cols))
    synthetic_cases = generate_boundary_cases(
        train_df[feature_cols + ["label"]],
        n=args.synthetic_n,
        vintage=args.vintage,
        seed=args.seed + 7,
    )

    # 5. Emit per-model outputs for every eval case.
    for case in [*real_cases, *synthetic_cases]:
        for model in fitted:
            case.per_model.append(_emit_per_model(model, case.features, args.top_k))

    # 6. Write run.
    meta = RunMetadata(
        run_id=_now_iso(),
        vintage=args.vintage,
        epsilon=args.epsilon,
        random_seed=args.seed,
        members=[
            {
                "model_id": m.model_id,
                "max_depth": m.tree.max_depth,
                "min_samples_leaf": m.tree.min_samples_leaf,
                "feature_subset": list(m.feature_subset),
            }
            for m in fitted
        ],
        notes=f"vintage={args.vintage} term={args.term} epsilon={args.epsilon}",
    )
    jsonl_path, meta_path = write_run(
        real_cases + synthetic_cases, meta, output_dir=args.output_dir
    )
    print(f"wrote {jsonl_path}")
    print(f"wrote {meta_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Smoke test the CLI on a tiny synthetic CSV**

Build a tiny LendingClub-shaped CSV and run the CLI. From the repo root:

```bash
python - <<'PY'
import pandas as pd
import numpy as np
from pathlib import Path
rng = np.random.default_rng(0)
n = 200
df = pd.DataFrame({
    "issue_d": ["Jul-2015"] * n,
    "term": [" 36 months"] * n,
    "loan_status": rng.choice(["Fully Paid", "Charged Off"], size=n, p=[0.85, 0.15]),
    "fico_range_low": rng.integers(620, 800, size=n),
    "dti": rng.integers(5, 45, size=n),
    "annual_inc": rng.integers(20000, 200000, size=n),
    "emp_length": rng.choice([1, 3, 5, 10], size=n),
})
out = Path("/tmp/lc_smoke.csv")
df.to_csv(out, index=False)
print(out)
PY
```

Then:

```bash
python -m wedge.run \
    --csv /tmp/lc_smoke.csv \
    --vintage 2015Q3 \
    --term '36 months' \
    --epsilon 0.10 \
    --n-members 3 \
    --top-k 3 \
    --synthetic-n 20 \
    --output-dir /tmp/wedge_runs
```

Expected: prints two `wrote ...` lines; `/tmp/wedge_runs/<id>.jsonl` exists with non-empty content; `/tmp/wedge_runs/<id>-meta.json` records `vintage=2015Q3` and `epsilon=0.1`.

If the smoke test fails, investigate (most likely: column-name mismatch with real LendingClub data, which the real CSV will surface). Capture findings and revise.

- [ ] **Step 3: Commit**

```bash
git add wedge/run.py
git commit -m "wedge: add CLI orchestration script"
```

---

## Task 11: Inspection notebook

**Files:**
- Create: `wedge/notebooks/inspection.ipynb`

- [ ] **Step 1: Create the notebook scaffold**

Create `wedge/notebooks/inspection.ipynb` as a fresh Jupyter notebook with the cells below. (If converting from .py: write `.py` content first, then `jupytext --to ipynb` if jupytext is available; otherwise hand-author the JSON.)

Cell 1 (markdown):

```markdown
# Wedge Inspection — Outcome-Agreer Factor-Support Overlap

Loads a wedge run jsonl, computes outcome-agreer set, plots the distribution
of pairwise Jaccard overlap on factor_support_T and factor_support_F, and
surfaces hand-inspection candidates from the low-overlap and high-overlap
ends.

Tests the primary hypothesis: among outcome-agreers, factor-support overlap
varies non-trivially. A bimodal or low-skewed distribution with low-end
mass below 0.3 supports the hypothesis; a unimodal distribution at high
overlap (median > 0.7) falsifies it.
```

Cell 2 (code):

```python
import json
from pathlib import Path
import pandas as pd

from wedge.types import Case
from wedge.metrics import is_outcome_agreer, pairwise_factor_support_overlap

RUN_JSONL = Path("runs/<replace-with-run-id>.jsonl")  # set to the latest run before running

cases: list[Case] = []
with RUN_JSONL.open() as f:
    for line in f:
        cases.append(Case.from_dict(json.loads(line)))

print(f"loaded {len(cases)} cases from {RUN_JSONL}")
```

Cell 3 (code):

```python
records = []
for c in cases:
    if not c.per_model:
        continue
    agreer = is_outcome_agreer(c.per_model)
    overlap_T, overlap_F = pairwise_factor_support_overlap(c.per_model)
    records.append({
        "case_id": c.case_id,
        "origin": c.origin,
        "label": c.label,
        "outcome_agreer": agreer,
        "overlap_T": overlap_T,
        "overlap_F": overlap_F,
        "mean_T": sum(p.T for p in c.per_model) / len(c.per_model),
    })
df = pd.DataFrame(records)
df.head()
```

Cell 4 (code):

```python
agreers = df[df["outcome_agreer"]]
print("Outcome-agreer count:", len(agreers))
print("Median overlap_T among agreers:", agreers["overlap_T"].median())
print("Median overlap_F among agreers:", agreers["overlap_F"].median())
agreers["overlap_T"].hist(bins=20)
```

Cell 5 (code):

```python
# Hand-inspection candidates from the low-overlap end (most surprising).
low_T = agreers.sort_values("overlap_T").head(10)
print("Lowest overlap_T outcome-agreers:")
print(low_T[["case_id", "origin", "mean_T", "overlap_T", "overlap_F"]])
```

Cell 6 (code):

```python
# Hand-inspection candidates from the high-overlap end (control).
high_T = agreers.sort_values("overlap_T", ascending=False).head(10)
print("Highest overlap_T outcome-agreers:")
print(high_T[["case_id", "origin", "mean_T", "overlap_T", "overlap_F"]])
```

Cell 7 (markdown):

```markdown
## What to look at

1. Pick 3 cases from `low_T` (low-overlap-T outcome-agreers) and 3 from `high_T` (high-overlap-T).
2. For each, look up the case in `cases` and print each model's `factor_support_T` features.
3. Check whether low-overlap cases show genuinely distinct reasoning (different feature sets) or merely synonyms-of-the-same-signal.
4. Record observations in a separate markdown file alongside the run; do not rationalize the result post-hoc.
```

- [ ] **Step 2: Verify the notebook executes end-to-end**

Run the smoke-test CLI from Task 10, set `RUN_JSONL` to the produced file, and run all notebook cells. They should execute without error and produce a histogram plus the two hand-inspection tables.

- [ ] **Step 3: Commit**

```bash
git add wedge/notebooks/inspection.ipynb
git commit -m "wedge: add inspection notebook"
```

---

## Task 12: Wedge README

**Files:**
- Create: `wedge/README.md`

- [ ] **Step 1: Write the README**

Create `wedge/README.md`:

```markdown
# Rashomon Prototype Wedge

Smallest concrete starting cut of the Rashomon-routed governance prototype.

**Spec:** `docs/superpowers/specs/2026-05-07-rashomon-prototype-wedge-design.md`
**Plan:** `docs/superpowers/plans/2026-05-07-rashomon-prototype-wedge.md`

## What this tests

The primary hypothesis: among outcome-agreers in R(ε), factor-support
varies non-trivially across models. Same outcome reached via different
feature paths.

Falsification: if pairwise Jaccard overlap among outcome-agreers is
consistently high (median > 0.7), the methodology's distinction between
outcome agreement and reasoning agreement collapses.

## Layout

- `types.py` — Case, PerModelOutput, FactorSupportEntry dataclasses
- `collectors/lendingclub.py` — LendingClub real-data loader
- `collectors/synthetic.py` — boundary-extending synthetic generator
- `models.py` — CART wrapper with T/F leaf-purity emission
- `attribution.py` — path walk, per-component split attribution
- `rashomon.py` — hyperparameter sweep, ε filter, diversity-weighted selection
- `metrics.py` — outcome-agreer detection, Jaccard overlap
- `output.py` — jsonl writer with metadata sidecar
- `run.py` — CLI orchestration
- `notebooks/inspection.ipynb` — interactive analysis
- `tests/` — unit tests; run with `pytest wedge/tests/`

## How to run

```bash
# 1. Place a LendingClub CSV at <path>. The wedge expects the standard
#    LendingClub schema with at least: issue_d, term, loan_status,
#    fico_range_low, dti, annual_inc, emp_length.
python -m wedge.run \
    --csv <path-to-lc.csv> \
    --vintage 2015Q3 \
    --term '36 months' \
    --epsilon 0.02 \
    --n-members 5 \
    --top-k 5 \
    --synthetic-n 200 \
    --output-dir runs/

# 2. Open notebooks/inspection.ipynb, set RUN_JSONL to the produced jsonl,
#    run all cells. Hand-inspect the low-overlap and high-overlap tails.
```

## Limitations

Single dataset, single vintage, single model class, deferred I, partial
reject inference, demonstration-grade synthetic data only. See spec §12.

The validity bound on synthetic-collector output is *hypothetical-scenario*;
it cannot support back-testing or any claim that requires real-data outcomes.
```

- [ ] **Step 2: Commit**

```bash
git add wedge/README.md
git commit -m "wedge: add README"
```

---

## Final verification

After all 12 tasks complete:

- [ ] **Run the full test suite**

Run: `pytest wedge/tests/ -v`
Expected: all tests pass.

- [ ] **Confirm the smoke-test still works**

Re-run the Task 10 smoke test on the tiny synthetic CSV. Expected: jsonl + meta sidecar produced.

- [ ] **Confirm the notebook runs end-to-end**

Open `wedge/notebooks/inspection.ipynb`, set `RUN_JSONL` to the smoke-test output, run all cells. Expected: histogram + two hand-inspection tables.

- [ ] **Run the wedge on a real LendingClub vintage if data available**

If the LendingClub historical data is on disk, run the CLI with `--vintage 2015Q3 --term '36 months' --epsilon 0.02 --n-members 5 --synthetic-n 200`. Expected: a meaningful jsonl. If column-name mismatches surface (very likely on first contact with real data), capture them, fix the collector, commit the fix as `wedge: fix LendingClub column-name mismatches`, then re-run.

The wedge is complete when the inspection notebook can produce the overlap distribution and hand-inspection candidates on a real-data run.
