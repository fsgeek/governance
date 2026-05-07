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


def test_load_cases_replaces_nan_features_with_none(tmp_path):
    """A row with NaN in a feature column must serialize cleanly to JSON;
    NaN serializes as the bare token 'NaN' which is invalid JSON per RFC 8259."""
    import json
    csv_path = tmp_path / "lc_with_nan.csv"
    csv_path.write_text(
        "issue_d,term,loan_status,fico_range_low,dti,annual_inc,emp_length\n"
        "Jul-2015, 36 months,Charged Off,640,,55000, 5 years\n"
        "Aug-2015, 36 months,Fully Paid,720,15,,10 years\n"
    )
    cases = load_cases(csv_path, vintage="2015Q3", term="36 months")
    assert len(cases) == 2
    # Confirm NaN became None (not a NaN float).
    for c in cases:
        for v in c.features.values():
            assert not (isinstance(v, float) and v != v), f"got NaN in features: {c.features}"
    # Confirm features serialize to valid JSON (no 'NaN' token).
    for c in cases:
        payload = json.dumps(c.features)
        assert "NaN" not in payload


def test_filter_to_vintage_raises_on_missing_required_column():
    df = pd.DataFrame({"term": [" 36 months"], "loan_status": ["Fully Paid"]})
    try:
        filter_to_vintage(df, vintage="2015Q3", term="36 months")
    except ValueError as e:
        assert "issue_d" in str(e)
        return
    raise AssertionError("expected ValueError for missing issue_d column")


def test_parse_vintage_rejects_non_integer_year():
    from wedge.collectors.lendingclub import _parse_vintage
    try:
        _parse_vintage("20l5Q3")  # lowercase L instead of 1
    except ValueError as e:
        assert "year" in str(e).lower()
        return
    raise AssertionError("expected ValueError for non-integer year")
