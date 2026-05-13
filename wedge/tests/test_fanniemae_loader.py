"""Tests for wedge.collectors.fanniemae.

Use a synthetic pipe-delimited fixture (EXPECTED_NUM_COLUMNS fields per
row, per the unified CRT Glossary layout) to validate schema mapping,
filtering, label derivation, and entry-point shape without requiring
the actual Fannie Mae file (which is behind a registration wall — see
data/fanniemae/README.md).
"""

from __future__ import annotations

import io

import pandas as pd
import pytest

from wedge.collectors.fanniemae import (
    EXPECTED_NUM_COLUMNS,
    FIELD_POSITIONS,
    WEDGE_CATEGORICAL_FEATURES,
    WEDGE_NUMERIC_FEATURES,
    bucket_high_cardinality,
    derive_origination_and_label,
    filter_eligible,
    load_fanniemae,
    map_fields,
    read_raw,
    to_feature_frame,
)


def _row(
    *,
    loan_id: str,
    mrp: str,
    fico: str = "740",
    ltv: str = "75",
    occupancy: str = "P",
    purpose: str = "P",
    dti: str = "32",
    term: str = "360",
    delinq: str = "00",
    zero_balance: str = "",
    cltv: str = "",
    mi_pct: str = "",
    upb: str = "",
    num_units: str = "",
    num_borrowers: str = "",
    channel: str = "",
    fthb: str = "",
    property_type: str = "",
    amort: str = "",
    state: str = "",
    msa: str = "",
    seller: str = "",
    servicer: str = "",
) -> str:
    """Build one pipe-delimited row of EXPECTED_NUM_COLUMNS fields with
    the listed positions populated and all other positions empty."""
    cols = [""] * EXPECTED_NUM_COLUMNS
    cols[FIELD_POSITIONS["loan_id"]] = loan_id
    cols[FIELD_POSITIONS["monthly_reporting_period"]] = mrp
    cols[FIELD_POSITIONS["credit_score"]] = fico
    cols[FIELD_POSITIONS["ltv"]] = ltv
    cols[FIELD_POSITIONS["occupancy"]] = occupancy
    cols[FIELD_POSITIONS["loan_purpose"]] = purpose
    cols[FIELD_POSITIONS["dti"]] = dti
    cols[FIELD_POSITIONS["loan_term"]] = term
    cols[FIELD_POSITIONS["current_loan_delinquency_status"]] = delinq
    cols[FIELD_POSITIONS["zero_balance_code"]] = zero_balance
    cols[FIELD_POSITIONS["cltv"]] = cltv
    cols[FIELD_POSITIONS["mortgage_insurance_pct"]] = mi_pct
    cols[FIELD_POSITIONS["original_upb"]] = upb
    cols[FIELD_POSITIONS["num_units"]] = num_units
    cols[FIELD_POSITIONS["num_borrowers"]] = num_borrowers
    cols[FIELD_POSITIONS["channel"]] = channel
    cols[FIELD_POSITIONS["first_time_buyer"]] = fthb
    cols[FIELD_POSITIONS["property_type"]] = property_type
    cols[FIELD_POSITIONS["amortization_type"]] = amort
    cols[FIELD_POSITIONS["property_state"]] = state
    cols[FIELD_POSITIONS["msa"]] = msa
    cols[FIELD_POSITIONS["seller_name"]] = seller
    cols[FIELD_POSITIONS["servicer_name"]] = servicer
    return "|".join(cols)


def _fixture_file(tmp_path, rows: list[str]):
    p = tmp_path / "fm_sample.txt"
    p.write_text("\n".join(rows) + "\n")
    return p


def _make_loan_history(loan_id, n_rows, *, delinq_at=None, **kw):
    """Build n_rows monthly reporting rows for one loan. If delinq_at
    is given, set delinquency='03' at that 0-indexed row."""
    rows = []
    for i in range(n_rows):
        month = (i % 12) + 1
        year = 2018 + (i // 12)
        mrp = f"{month:02d}{year}"
        d = "03" if (delinq_at is not None and i == delinq_at) else "00"
        rows.append(_row(loan_id=loan_id, mrp=mrp, delinq=d, **kw))
    return rows


# ----------------------------------------------------------------------


def test_map_fields_returns_positions_for_known():
    out = map_fields(["credit_score", "dti", "ltv"])
    assert out == {
        "credit_score": FIELD_POSITIONS["credit_score"],
        "dti": FIELD_POSITIONS["dti"],
        "ltv": FIELD_POSITIONS["ltv"],
    }


def test_map_fields_rejects_unmapped():
    with pytest.raises(ValueError, match="Unmapped"):
        map_fields(["credit_score", "applicant_income"])


def test_read_raw_requires_expected_columns(tmp_path):
    bad = tmp_path / "bad.txt"
    bad.write_text("a|b|c\n")
    with pytest.raises(ValueError, match=str(EXPECTED_NUM_COLUMNS)):
        read_raw(bad)


def test_read_raw_missing_file_points_at_readme(tmp_path):
    with pytest.raises(FileNotFoundError, match="data/fanniemae/README.md"):
        read_raw(tmp_path / "does_not_exist.txt")


def test_filter_eligible_keeps_owner_occupied_purchase_or_refi(tmp_path):
    rows = (
        _make_loan_history("L1", 24, occupancy="P", purpose="P")
        + _make_loan_history("L2", 24, occupancy="I", purpose="P")  # investor — drop
        + _make_loan_history("L3", 24, occupancy="P", purpose="C")  # cash-out refi — keep
        + _make_loan_history("L4", 24, occupancy="P", purpose="X")  # unknown purpose — drop
    )
    p = _fixture_file(tmp_path, rows)
    raw = read_raw(p)
    collapsed = derive_origination_and_label(raw)
    eligible = filter_eligible(collapsed)
    kept_loan_ids = set(eligible["loan_id"])
    assert kept_loan_ids == {"L1", "L3"}


def test_label_ever_90dpd_within_horizon(tmp_path):
    rows = (
        _make_loan_history("CLEAN", 24)                            # never delinquent
        + _make_loan_history("BAD", 24, delinq_at=10)              # 90+ DPD inside horizon
        + _make_loan_history("LATE_BAD", 30, delinq_at=27)         # 90+ DPD AFTER horizon
    )
    p = _fixture_file(tmp_path, rows)
    raw = read_raw(p)
    collapsed = derive_origination_and_label(raw, horizon_months=24)
    labels = dict(zip(collapsed["loan_id"], collapsed["label"]))
    # Grant-as-positive convention (spec §2.7 OD-9a / OD-13): clean = grant = 1,
    # 90+ DPD inside horizon = adverse = 0.
    assert labels["CLEAN"] == 1
    assert labels["BAD"] == 0
    assert labels["LATE_BAD"] == 1  # delinquency outside horizon doesn't count


def test_short_history_without_terminal_dropped(tmp_path):
    # 12 rows, no zero_balance_code -> insufficient observation window.
    rows = _make_loan_history("SHORT", 12, zero_balance="")
    p = _fixture_file(tmp_path, rows)
    raw = read_raw(p)
    collapsed = derive_origination_and_label(raw, horizon_months=24)
    assert "SHORT" not in set(collapsed["loan_id"])


def test_short_history_with_terminal_kept(tmp_path):
    # 12 rows but loan paid off (zero_balance_code populated on last row).
    rows = _make_loan_history("PAID", 11, zero_balance="")
    rows.append(_row(loan_id="PAID", mrp="122018", zero_balance="01"))
    p = _fixture_file(tmp_path, rows)
    raw = read_raw(p)
    collapsed = derive_origination_and_label(raw, horizon_months=24)
    assert "PAID" in set(collapsed["loan_id"])


def test_to_feature_frame_columns_and_fico_range(tmp_path):
    rows = (
        _make_loan_history("A", 24, fico="720", ltv="80", dti="35", term="360")
        + _make_loan_history("B", 24, fico="640", ltv="95", dti="42", term="180")
    )
    p = _fixture_file(tmp_path, rows)
    raw = read_raw(p)
    collapsed = derive_origination_and_label(raw)
    eligible = filter_eligible(collapsed)
    feats = to_feature_frame(eligible)
    expected_cols = {
        "loan_id", "fico_range_low", "dti", "ltv", "loan_term_months",
        "loan_purpose", "occupancy_status", "lien_position", "label",
    }
    assert expected_cols.issubset(set(feats.columns))
    # FICO must be in plausible range.
    fico_vals = feats["fico_range_low"].dropna()
    assert ((fico_vals >= 300) & (fico_vals <= 850)).all()
    # Lien position is always 1 (dataset is first-lien only).
    assert (feats["lien_position"] == 1).all()


def test_load_fanniemae_returns_case_objects(tmp_path):
    rows = (
        _make_loan_history("L1", 24, fico="700", delinq_at=5)
        + _make_loan_history("L2", 24, fico="780")
    )
    p = _fixture_file(tmp_path, rows)
    cases = load_fanniemae(p, horizon_months=24, vintage="FM-test")
    assert len(cases) == 2
    for c in cases:
        assert c.origin == "real"
        assert c.synthetic_role is None
        assert c.vintage == "FM-test"
        assert c.label in (0, 1)
        assert "fico_range_low" in c.features
        assert "dti" in c.features
        assert "ltv" in c.features
        assert "loan_term_months" in c.features
        assert "loan_purpose" in c.features
        assert "occupancy_status" in c.features
        assert c.features["lien_position"] == 1
        # annual_inc deliberately absent: Fannie Mae does not release income.
        assert "annual_inc" not in c.features
    # Grant-as-positive convention: L1 was 90+ DPD -> label 0 (adverse);
    # L2 clean -> label 1 (grant).
    by_fico = {c.features["fico_range_low"]: c.label for c in cases}
    assert by_fico[700] == 0
    assert by_fico[780] == 1


def test_load_fanniemae_missing_file_raises_with_readme_pointer(tmp_path):
    with pytest.raises(FileNotFoundError, match="data/fanniemae/README.md"):
        load_fanniemae(tmp_path / "nope.txt")


# ----------------------------------------------------------------------
# Extended named-policy + extension features (the #11 rich-policy collector
# extension: cltv / mortgage_insurance_pct / original_upb / num_units /
# num_borrowers / channel / first_time_homebuyer / property_type /
# amortization_type / property_state / msa / seller_name / servicer_name).
# ----------------------------------------------------------------------


def test_new_field_positions_distinct_and_in_range():
    # Adding fields must not collide with an existing position or run off
    # the end of the 113-column layout (the "no silent drop" contract).
    positions = list(FIELD_POSITIONS.values())
    assert len(positions) == len(set(positions)), "duplicate column position in FIELD_POSITIONS"
    assert all(0 <= p < EXPECTED_NUM_COLUMNS for p in positions)
    for name in ("cltv", "mortgage_insurance_pct", "original_upb", "num_units",
                 "num_borrowers", "channel", "first_time_buyer", "property_type",
                 "amortization_type", "property_state", "msa", "seller_name",
                 "servicer_name"):
        assert name in FIELD_POSITIONS


def test_map_fields_accepts_new_named_and_extension_fields():
    out = map_fields(["cltv", "mortgage_insurance_pct", "original_upb", "property_state",
                      "seller_name", "servicer_name", "msa", "amortization_type"])
    assert set(out) == {"cltv", "mortgage_insurance_pct", "original_upb", "property_state",
                        "seller_name", "servicer_name", "msa", "amortization_type"}


def test_to_feature_frame_emits_extended_features_with_types(tmp_path):
    rows = (
        _make_loan_history("A", 24, fico="780", ltv="65", dti="28", term="360",
                           cltv="65", mi_pct="", upb="453000.00", num_units="1",
                           num_borrowers="1", channel="R", fthb="N",
                           property_type="PU", amort="FRM", state="OH", msa="18140",
                           seller="Quicken Loans, Llc", servicer="Quicken Loans Inc.")
        + _make_loan_history("B", 24, fico="660", ltv="95", dti="44", term="180",
                             cltv="97", mi_pct="30", upb="210000.00", num_units="2",
                             num_borrowers="2", channel="B", fthb="Y",
                             property_type="SF", amort="FRM", state="TX", msa="",
                             seller="Wells Fargo Bank, N.A.", servicer="Wells Fargo Bank, N.A.")
    )
    p = _fixture_file(tmp_path, rows)
    raw = read_raw(p)
    collapsed = derive_origination_and_label(raw)
    eligible = filter_eligible(collapsed)
    feats = to_feature_frame(eligible)

    # Every numeric and categorical wedge feature is present.
    for c in WEDGE_NUMERIC_FEATURES:
        assert c in feats.columns, f"missing numeric feature {c}"
    for c in WEDGE_CATEGORICAL_FEATURES:
        assert c in feats.columns, f"missing categorical feature {c}"

    by_loan = feats.set_index("loan_id")
    # Numerics are numeric-coerced.
    assert by_loan.loc["A", "cltv"] == 65
    assert by_loan.loc["A", "original_upb"] == 453000.0
    assert by_loan.loc["A", "num_units"] == 1
    assert by_loan.loc["B", "num_borrowers"] == 2
    assert by_loan.loc["B", "mortgage_insurance_pct"] == 30
    # Empty MI percentage (LTV<=80, no MI) -> NaN, not 0.
    assert pd.isna(by_loan.loc["A", "mortgage_insurance_pct"])
    # Empty MSA (rural) -> NaN.
    assert pd.isna(by_loan.loc["B", "msa"])
    # Categoricals stay as strings.
    assert by_loan.loc["A", "property_type"] == "PU"
    assert by_loan.loc["A", "amortization_type"] == "FRM"
    assert by_loan.loc["A", "property_state"] == "OH"
    assert by_loan.loc["B", "channel"] == "B"
    assert by_loan.loc["A", "seller_name"] == "Quicken Loans, Llc"


def test_bucket_high_cardinality_keeps_top_k_and_other():
    s = pd.Series(["X"] * 10 + ["Y"] * 5 + ["Z"] * 3 + ["W"] * 1 + [None] * 2)
    out = bucket_high_cardinality(s, top_k=2)
    assert set(out.dropna().unique()) == {"X", "Y", "__other__"}
    # The kept values keep their label; rarer ones collapse.
    assert (out[s == "X"] == "X").all()
    assert (out[s == "Z"] == "__other__").all()
    # Missing stays missing.
    assert out.isna().sum() == 2


def test_bucket_high_cardinality_all_missing_returns_unchanged():
    s = pd.Series([None, None, None], dtype=object)
    out = bucket_high_cardinality(s, top_k=5)
    assert out.isna().all()
