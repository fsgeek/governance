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
    try:
        int(year)
    except ValueError:
        raise ValueError(f"vintage year {year!r} is not a valid integer in {vintage!r}")
    if quarter_key not in _QUARTER_MONTHS:
        raise ValueError(f"unknown quarter {quarter_key!r}")
    return year, _QUARTER_MONTHS[quarter_key]


def filter_to_vintage(df: pd.DataFrame, *, vintage: str, term: str) -> pd.DataFrame:
    """Keep rows whose issue_d falls in the named quarter, term matches, and
    loan_status is terminal (Fully Paid / Charged Off)."""
    required = {"issue_d", "term", "loan_status"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"CSV is missing required columns: {sorted(missing)!r}. "
            f"Found {len(df.columns)} columns; first 10: {list(df.columns[:10])}"
        )
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
    """Map terminal loan_status to binary label: paid=1 (grant/favorable),
    charged_off=0 (deny/adverse). See spec §2.7 OD-9a / OD-13 for the
    grant-as-positive convention rationale."""
    return (loan_status.astype(str).str.strip() == PAID).astype(int)


_EMP_LENGTH_MAP = {
    "< 1 year": 0.0,
    "1 year": 1.0,
    "2 years": 2.0,
    "3 years": 3.0,
    "4 years": 4.0,
    "5 years": 5.0,
    "6 years": 6.0,
    "7 years": 7.0,
    "8 years": 8.0,
    "9 years": 9.0,
    "10+ years": 10.0,
}


def normalize_emp_length(s: pd.Series) -> pd.Series:
    """Map LC emp_length strings to floats; unrecognized values -> NaN."""
    return s.astype(str).str.strip().map(_EMP_LENGTH_MAP)


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
    required_cols = {"issue_d", "term", "loan_status"}
    needed_cols = required_cols | set(feature_cols)
    df = pd.read_csv(csv_path, usecols=lambda c: c in needed_cols, low_memory=False)
    df = filter_to_vintage(df, vintage=vintage, term=term)
    df["label"] = derive_label(df["loan_status"])
    feature_cols_present = [c for c in feature_cols if c in df.columns]
    records = df[feature_cols_present].to_dict("records")
    labels = df["label"].tolist()
    cases = [
        Case(
            case_id=str(uuid.uuid4()),
            origin="real",
            synthetic_role=None,
            vintage=vintage,
            features={k: (None if pd.isna(v) else v) for k, v in rec.items()},
            label=int(lbl),
            per_model=[],
        )
        for rec, lbl in zip(records, labels)
    ]
    return cases
