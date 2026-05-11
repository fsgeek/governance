"""Fannie Mae Single-Family Loan Performance Data collector.

Loads Fannie Mae's unified Loan Performance disclosure (113 pipe-delimited
positional fields per the CRT Glossary, no header), filters to first-lien
purchase/refi on owner-occupied properties, derives a binary label
("ever 90+ days delinquent within first 24 months" maps to label=0,
the adverse outcome; clean performance maps to label=1, the favorable
outcome) from the performance rows, and emits Case objects with origin="real".
Convention is grant-as-positive (label=1 ⇔ grant); see spec §2.7 OD-9a / OD-13.

Schema reference
----------------
File layout: 113 pipe-delimited fields per row, no header line, one row
per (loan, monthly_reporting_period). Origination-time fields are repeated
on every performance row for the same loan. The unified disclosure file
exposes every glossary position (CAS, CIRT, and SF Loan Performance);
fields not applicable to SF Loan Performance are present-but-empty.

Field positions encoded here are file indices, derived as
`file_pos = glossary_pos - 1` against `data/fanniemae/crt-file-layout-and-glossary.xlsx`
(zero-indexed). A position-reject test ensures we do not silently drop
new fields when extending.

Access
------
The Single-Family Loan Performance Data is behind a free registration
wall on capitalmarkets.fanniemae.com. See data/fanniemae/README.md for
the manual download steps. If the file is absent, load_fanniemae raises
FileNotFoundError pointing at the README. Tests use a synthetic fixture
matching the schema.

Field mapping (Fannie Mae name -> wedge feature; glossary_pos / file_idx)
-------------------------------------------------------------------------
- BORROWER_CREDIT_SCORE_AT_ORIGINATION (gloss 24 / idx 23) -> fico_range_low
- DEBT_TO_INCOME_RATIO                 (gloss 23 / idx 22) -> dti
- ORIGINAL_LOAN_TO_VALUE               (gloss 20 / idx 19) -> ltv
- ORIGINAL_LOAN_TERM                   (gloss 13 / idx 12) -> loan_term_months
- LOAN_PURPOSE                         (gloss 27 / idx 26) -> loan_purpose
- OCCUPANCY_STATUS                     (gloss 30 / idx 29) -> occupancy_status
- (lien position is implicit: dataset is first-lien only) -> lien_position=1
- annual_inc: NOT AVAILABLE — Fannie Mae does not release applicant
  income on the public dataset. The README documents this gap; the
  wedge will run without annual_inc on Fannie Mae data.
"""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Iterable, Optional

import pandas as pd

from wedge.types import Case


# ----------------------------------------------------------------------
# Positional schema for the unified disclosure file (113 columns; CRT
# Glossary). Only the positions the wedge consumes are listed.
# Indices are 0-based; comments show 1-based glossary position.
# ----------------------------------------------------------------------
FIELD_POSITIONS: dict[str, int] = {
    "loan_id": 1,                          # gloss 2  LOAN_IDENTIFIER
    "monthly_reporting_period": 2,         # gloss 3  MONTHLY_REPORTING_PERIOD
    "channel": 3,                          # gloss 4  CHANNEL
    "loan_term": 12,                       # gloss 13 ORIGINAL_LOAN_TERM
    "origination_date": 13,                # gloss 14 ORIGINATION_DATE  (MMYYYY)
    "first_payment_date": 14,              # gloss 15 FIRST_PAYMENT_DATE
    "ltv": 19,                             # gloss 20 ORIGINAL_LOAN_TO_VALUE
    "num_borrowers": 21,                   # gloss 22 NUMBER_OF_BORROWERS
    "dti": 22,                             # gloss 23 DEBT_TO_INCOME_RATIO
    "credit_score": 23,                    # gloss 24 BORROWER_CREDIT_SCORE_AT_ORIGINATION
    "first_time_buyer": 25,                # gloss 26 FIRST_TIME_HOME_BUYER_INDICATOR
    "loan_purpose": 26,                    # gloss 27 LOAN_PURPOSE  (P=purchase, C=cash-out refi, R=no-cash refi, U=refi)
    "property_type": 27,                   # gloss 28 PROPERTY_TYPE
    "num_units": 28,                       # gloss 29 NUMBER_OF_UNITS
    "occupancy": 29,                       # gloss 30 OCCUPANCY_STATUS  (P=primary, S=second, I=investor)
    "current_loan_delinquency_status": 39, # gloss 40 CURRENT_LOAN_DELINQUENCY_STATUS
    "zero_balance_code": 43,               # gloss 44 ZERO_BALANCE_CODE
}

EXPECTED_NUM_COLUMNS = 113

# Occupancy / loan-purpose codes per Fannie Mae glossary.
OCCUPANCY_OWNER = "P"  # principal residence
PURPOSE_PURCHASE = "P"
PURPOSE_REFI_CODES = {"C", "R", "U"}  # cash-out, no-cash-out, refinance (unspecified)

# Delinquency status: "00"-"XX" string. "X" means unknown. Numeric strings
# are months delinquent. 90+ days = numeric value >= 3.
DELINQUENCY_THRESHOLD_MONTHS = 3
DEFAULT_LABEL_HORIZON_MONTHS = 24


# ----------------------------------------------------------------------
# Schema mapping: position-aware reject of unmapped field requests.
# ----------------------------------------------------------------------
def map_fields(requested: Iterable[str]) -> dict[str, int]:
    """Return {wedge_feature_name: column_position} for every requested name.

    Raises ValueError if any requested name is not in FIELD_POSITIONS.
    This is the "rejects unmapped fields rather than silently dropping"
    contract.
    """
    requested = list(requested)
    unknown = [r for r in requested if r not in FIELD_POSITIONS]
    if unknown:
        raise ValueError(
            f"Unmapped Fannie Mae fields requested: {unknown!r}. "
            f"Known fields: {sorted(FIELD_POSITIONS)!r}"
        )
    return {r: FIELD_POSITIONS[r] for r in requested}


# ----------------------------------------------------------------------
# Raw file ingestion (pipe-delimited, no header).
# ----------------------------------------------------------------------
def read_raw(path: Path | str, *, nrows: Optional[int] = None) -> pd.DataFrame:
    """Read a raw Fannie Mae loan-performance file.

    The file is pipe-delimited with no header. We assign positional column
    names of the form 'c0'..'c112' so downstream selection is by index.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(
            f"Fannie Mae loan-performance file not found at {p}. "
            "See data/fanniemae/README.md for the manual download steps "
            "(registration required at capitalmarkets.fanniemae.com)."
        )
    # Validate column count from the first non-empty line independently
    # of pandas (pandas would silently pad missing columns with NaN when
    # `names=` is supplied).
    with open(p, "r") as fh:
        first_line = ""
        for line in fh:
            if line.strip():
                first_line = line.rstrip("\n").rstrip("\r")
                break
    actual_cols = first_line.count("|") + 1 if first_line else 0
    if actual_cols != EXPECTED_NUM_COLUMNS:
        raise ValueError(
            f"Expected {EXPECTED_NUM_COLUMNS} pipe-delimited columns; "
            f"got {actual_cols} in {p}. The file may be a different "
            "vintage of the schema; see data/fanniemae/README.md."
        )
    col_names = [f"c{i}" for i in range(EXPECTED_NUM_COLUMNS)]
    df = pd.read_csv(
        p,
        sep="|",
        header=None,
        names=col_names,
        dtype=str,
        nrows=nrows,
        low_memory=False,
        keep_default_na=False,
        na_values=[""],
    )
    return df


# ----------------------------------------------------------------------
# Origination-row extraction & filtering.
# ----------------------------------------------------------------------
def _to_int(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce").astype("Int64")


def _delinquency_to_int(s: pd.Series) -> pd.Series:
    """Map delinquency-status strings to integer months delinquent.

    'X' / unknown / non-numeric become <NA>.
    """
    return pd.to_numeric(s, errors="coerce").astype("Int64")


def derive_origination_and_label(
    raw: pd.DataFrame,
    *,
    horizon_months: int = DEFAULT_LABEL_HORIZON_MONTHS,
) -> pd.DataFrame:
    """Collapse multi-row performance data to one row per loan, with label.

    For each loan_id:
      - Take the first reporting row's origination fields (these are
        invariant across the loan's rows).
      - Compute label = 0 if any of the first `horizon_months` reporting
        rows shows current_loan_delinquency_status >= 3 (90+ DPD); else
        label = 1. Convention: grant-as-positive (clean = grant = 1).
      - If the loan has fewer than `horizon_months` reporting rows AND
        no terminal zero_balance_code by then, the loan is dropped
        (insufficient observation window for the label).
    """
    df = raw.copy()
    df["loan_id"] = df[f"c{FIELD_POSITIONS['loan_id']}"]
    df["delinquency_int"] = _delinquency_to_int(
        df[f"c{FIELD_POSITIONS['current_loan_delinquency_status']}"]
    )
    df["zero_balance_code"] = df[f"c{FIELD_POSITIONS['zero_balance_code']}"]
    # monthly_reporting_period is MMYYYY; sort lexicographically by
    # (year, month) — convert to a sortable key.
    mrp = df[f"c{FIELD_POSITIONS['monthly_reporting_period']}"].astype(str)
    # MMYYYY -> YYYYMM for sort. Tolerate non-conforming values.
    df["_mrp_key"] = mrp.str.slice(2, 6) + mrp.str.slice(0, 2)

    df = df.sort_values(["loan_id", "_mrp_key"]).reset_index(drop=True)
    df["_row_within_loan"] = df.groupby("loan_id").cumcount()

    # Origination snapshot = first row per loan.
    first_rows = df[df["_row_within_loan"] == 0].copy()

    # Label: ever-90+DPD within first horizon_months reporting rows.
    horizon_rows = df[df["_row_within_loan"] < horizon_months]
    label_series = (
        horizon_rows.groupby("loan_id")["delinquency_int"]
        .apply(
            lambda s: int(
                not (s.dropna() >= DELINQUENCY_THRESHOLD_MONTHS).any()
            )
        )
    )
    label_series.name = "label"

    # Observation window check: drop loans with fewer than horizon_months
    # rows AND no terminal zero_balance_code in their history.
    counts = df.groupby("loan_id").size()
    counts.name = "n_rows"
    terminal_flag = df["zero_balance_code"].notna() & (df["zero_balance_code"].astype(str) != "")
    has_terminal = df.assign(_t=terminal_flag).groupby("loan_id")["_t"].any()
    has_terminal.name = "has_terminal"

    out = (
        first_rows.set_index("loan_id")
        .join(label_series)
        .join(counts)
        .join(has_terminal)
    )
    out = out[(out["n_rows"] >= horizon_months) | (out["has_terminal"])]
    return out.reset_index()


def filter_eligible(df: pd.DataFrame) -> pd.DataFrame:
    """Keep first-lien (always true for this dataset) purchase/refi on
    owner-occupied properties (occupancy=P)."""
    occ = df[f"c{FIELD_POSITIONS['occupancy']}"].astype(str).str.strip().str.upper()
    purp = df[f"c{FIELD_POSITIONS['loan_purpose']}"].astype(str).str.strip().str.upper()
    eligible_purposes = {PURPOSE_PURCHASE} | PURPOSE_REFI_CODES
    mask = (occ == OCCUPANCY_OWNER) & purp.isin(eligible_purposes)
    return df.loc[mask].reset_index(drop=True)


# ----------------------------------------------------------------------
# Public entry point.
# ----------------------------------------------------------------------
WEDGE_FEATURES = {
    "fico_range_low": "credit_score",
    "dti": "dti",
    "ltv": "ltv",
    "loan_term_months": "loan_term",
    "loan_purpose": "loan_purpose",
    "occupancy_status": "occupancy",
}


def to_feature_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Project the eligible-loan frame onto the wedge feature names.

    Adds lien_position=1 (dataset is first-lien only). Does NOT add
    annual_inc — Fannie Mae does not release applicant income.
    """
    out = pd.DataFrame()
    out["loan_id"] = df["loan_id"] if "loan_id" in df.columns else df[f"c{FIELD_POSITIONS['loan_id']}"]
    for wedge_name, fm_name in WEDGE_FEATURES.items():
        col = f"c{FIELD_POSITIONS[fm_name]}"
        out[wedge_name] = df[col]
    # Numeric coercion for the numeric features.
    for c in ("fico_range_low", "dti", "ltv", "loan_term_months"):
        out[c] = pd.to_numeric(out[c], errors="coerce")
    out["lien_position"] = 1
    if "label" in df.columns:
        out["label"] = df["label"].astype(int)
    return out


def load_fanniemae(
    path: Path | str,
    *,
    horizon_months: int = DEFAULT_LABEL_HORIZON_MONTHS,
    nrows: Optional[int] = None,
    vintage: str = "fanniemae",
) -> list[Case]:
    """Load Fannie Mae loan-performance data and emit Case objects.

    Parameters
    ----------
    path : Path to the pipe-delimited Fannie Mae file (one acquisition
           quarter, post-Oct-2020 unified layout, 108 columns, no header).
    horizon_months : Label horizon for ever-90+DPD (default 24).
    nrows : Optional cap on raw rows read (testing / sampling).
    vintage : String tag stored on each Case (e.g. "FM-2018Q1").

    Raises FileNotFoundError with a pointer to the manual-download README
    if the file is absent.
    """
    raw = read_raw(path, nrows=nrows)
    collapsed = derive_origination_and_label(raw, horizon_months=horizon_months)
    eligible = filter_eligible(collapsed)
    feats = to_feature_frame(eligible)

    cases: list[Case] = []
    for _, row in feats.iterrows():
        feature_keys = [
            "fico_range_low", "dti", "ltv", "loan_term_months",
            "loan_purpose", "occupancy_status", "lien_position",
        ]
        features = {}
        for k in feature_keys:
            v = row[k]
            if isinstance(v, float) and v != v:  # NaN
                features[k] = None
            elif pd.isna(v):
                features[k] = None
            else:
                features[k] = v.item() if hasattr(v, "item") else v
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
