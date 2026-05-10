"""HMDA (Home Mortgage Disclosure Act) public-data collector.

Loads a single-state, single-year slice of the FFIEC HMDA Loan Application
Register (LAR) modified file, filters to first-lien residential
purchase/refinance loans on owner-occupied properties (the regime targeted by
the thin demo policy graph), maps a minimal feature set, and exposes a binary
label from the regulatory ``action_taken`` field.

This is the *regulator-perspective* view: HMDA is what lenders are required to
report to the FFIEC under Regulation C. It is INTENTIONALLY DIFFERENT from the
LendingClub schema. In particular, **HMDA does not contain a credit score**
(there is an ``applicant_credit_score_type`` indicator field that records WHICH
score was used by the lender, but the score value itself is not disclosed).
This is the legally-mandated feature pool, not an underwriter-internal one.

See data/hmda/README.md for source URL, vintage, and geographic filter.

Schema mapping (HMDA -> wedge feature names):
    income (in $1000s)              -> applicant_income
    loan_amount (rounded to 1k$)    -> loan_amount
    loan_amount / income            -> loan_to_income (derived)
    debt_to_income_ratio            -> dti  (post-2018: banded ordinal string;
                                              numeric strings parsed to float;
                                              banded values preserved as
                                              ordinal codes 0..N)
    loan_to_value_ratio             -> ltv  (parsed to float; HMDA only emits
                                              one LTV column for modified LAR)
    loan_term  (months)             -> loan_term_months

Label mapping (action_taken -> label):
    1 (originated)         -> 0  (grant; analogous to "approve")
    3 (denied)             -> 1  (deny; the adverse outcome)
Other action_taken values are excluded (the modified-LAR query already filtered
to actions 1 and 3, so this is defensive).
"""

from __future__ import annotations

import uuid
from pathlib import Path

import pandas as pd

from wedge.types import Case


# HMDA LAR field codes (from FFIEC public LAR specification, 2022 vintage).
ACTION_ORIGINATED = 1
ACTION_DENIED = 3
ALLOWED_ACTIONS = {ACTION_ORIGINATED, ACTION_DENIED}

# loan_purpose: 1=Home purchase, 31=Refinance, 32=Cash-out refinance.
PURCHASE = 1
REFINANCE = 31
CASHOUT_REFINANCE = 32
ALLOWED_PURPOSES = {PURCHASE, REFINANCE, CASHOUT_REFINANCE}

LIEN_FIRST = 1
OCCUPANCY_PRINCIPAL_RESIDENCE = 1

# Required HMDA columns. Loader rejects files missing any of these.
REQUIRED_HMDA_COLUMNS = [
    "action_taken",
    "loan_purpose",
    "lien_status",
    "occupancy_type",
    "income",
    "loan_amount",
    "loan_to_value_ratio",
    "loan_term",
    "debt_to_income_ratio",
]

# DTI is published post-2018 as a mix of integer-string ("39") and banded
# strings ("30%-<36%"). We preserve as ordinal codes; the order encodes the
# implicit rank. Unknown / "Exempt" map to NaN.
_DTI_BAND_ORDER = [
    "<20%",
    "20%-<30%",
    "30%-<36%",
    "36",
    "37",
    "38",
    "39",
    "40",
    "41",
    "42",
    "43",
    "44",
    "45",
    "46",
    "47",
    "48",
    "49",
    "50%-60%",
    ">60%",
]
_DTI_BAND_RANK = {v: i for i, v in enumerate(_DTI_BAND_ORDER)}


def _parse_dti(s: pd.Series) -> pd.Series:
    """Map HMDA debt_to_income_ratio strings to ordinal codes (float)."""
    raw = s.astype(str).str.strip()
    return raw.map(_DTI_BAND_RANK).astype("float64")


def _parse_numeric(s: pd.Series) -> pd.Series:
    """Coerce a HMDA string column to numeric; non-numeric ('Exempt', 'NA') -> NaN."""
    return pd.to_numeric(s, errors="coerce")


# Output feature columns (post-mapping).
ORIGINATION_FEATURE_COLS = [
    "applicant_income",
    "loan_amount",
    "loan_to_income",
    "dti",
    "ltv",
    "loan_term_months",
]


def _validate_columns(df: pd.DataFrame) -> None:
    missing = [c for c in REQUIRED_HMDA_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(
            f"HMDA file is missing required columns: {missing!r}. "
            f"Found {len(df.columns)} columns; first 10: {list(df.columns[:10])}"
        )


def filter_to_regime(df: pd.DataFrame) -> pd.DataFrame:
    """Keep first-lien purchase/refinance loans on owner-occupied properties
    with a terminal action_taken (originated or denied)."""
    _validate_columns(df)
    mask = (
        df["action_taken"].isin(ALLOWED_ACTIONS)
        & df["loan_purpose"].isin(ALLOWED_PURPOSES)
        & (df["lien_status"] == LIEN_FIRST)
        & (df["occupancy_type"] == OCCUPANCY_PRINCIPAL_RESIDENCE)
    )
    return df.loc[mask].reset_index(drop=True)


def derive_label(action_taken: pd.Series) -> pd.Series:
    """Map HMDA action_taken to binary label: denied=1, originated=0.

    Rationale: in the wedge's framing, "1" is the adverse outcome (analogous
    to charged_off in LendingClub). For lending decisions, denial is the
    adverse / consequential action that fair-lending review focuses on.
    """
    return (action_taken.astype(int) == ACTION_DENIED).astype(int)


def map_features(df: pd.DataFrame) -> pd.DataFrame:
    """Map HMDA fields to the wedge feature schema. Unmapped HMDA fields are
    intentionally dropped here (we keep only the documented mapping)."""
    _validate_columns(df)
    out = pd.DataFrame(index=df.index)
    out["applicant_income"] = _parse_numeric(df["income"])
    out["loan_amount"] = _parse_numeric(df["loan_amount"])
    # loan_to_income: guard against zero / negative income.
    income = out["applicant_income"]
    out["loan_to_income"] = out["loan_amount"] / income.where(income > 0)
    out["dti"] = _parse_dti(df["debt_to_income_ratio"])
    out["ltv"] = _parse_numeric(df["loan_to_value_ratio"])
    out["loan_term_months"] = _parse_numeric(df["loan_term"])
    return out


def _resolve_path(path: Path | str) -> Path:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(
            f"HMDA parquet not found at {p!s}. "
            "See data/hmda/README.md for the manual download step "
            "(FFIEC modified LAR filtered query)."
        )
    return p


def load_hmda(
    parquet_path: Path | str,
    *,
    feature_cols: list[str] | None = None,
    vintage: str = "2022",
) -> list[Case]:
    """Load HMDA cases from a parquet file.

    Parameters
    ----------
    parquet_path : path to a HMDA modified-LAR parquet (see
        data/hmda/README.md for how the file is produced).
    feature_cols : output feature names to retain. Defaults to
        ORIGINATION_FEATURE_COLS. Names not in ORIGINATION_FEATURE_COLS are
        rejected (we don't silently drop fields that haven't been mapped).
    vintage : vintage string stamped onto each Case (e.g. ``"2022"``).
    """
    feature_cols = list(feature_cols) if feature_cols else list(ORIGINATION_FEATURE_COLS)
    unknown = [c for c in feature_cols if c not in ORIGINATION_FEATURE_COLS]
    if unknown:
        raise ValueError(
            f"Unknown HMDA feature columns: {unknown!r}. "
            f"Allowed: {ORIGINATION_FEATURE_COLS!r}. "
            "Add an explicit mapping in wedge.collectors.hmda before requesting."
        )
    p = _resolve_path(parquet_path)
    df = pd.read_parquet(p)
    df = filter_to_regime(df)
    feats = map_features(df)
    labels = derive_label(df["action_taken"])
    records = feats[feature_cols].to_dict("records")
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
        for rec, lbl in zip(records, labels.tolist())
    ]
    return cases


def load_dataframe(parquet_path: Path | str) -> pd.DataFrame:
    """Load HMDA as a DataFrame, filtered and feature-mapped, with a ``label``
    column. Useful for tests and quick exploration without going through Case
    objects."""
    p = _resolve_path(parquet_path)
    df = pd.read_parquet(p)
    df = filter_to_regime(df)
    feats = map_features(df)
    feats["label"] = derive_label(df["action_taken"]).values
    return feats
