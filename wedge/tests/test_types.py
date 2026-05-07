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
