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
