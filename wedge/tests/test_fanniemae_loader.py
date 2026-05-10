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
    assert labels["CLEAN"] == 0
    assert labels["BAD"] == 1
    assert labels["LATE_BAD"] == 0  # delinquency outside horizon doesn't count


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
    # Specifically: L1 was 90+ DPD -> label 1; L2 clean -> label 0.
    by_fico = {c.features["fico_range_low"]: c.label for c in cases}
    assert by_fico[700] == 1
    assert by_fico[780] == 0


def test_load_fanniemae_missing_file_raises_with_readme_pointer(tmp_path):
    with pytest.raises(FileNotFoundError, match="data/fanniemae/README.md"):
        load_fanniemae(tmp_path / "nope.txt")
