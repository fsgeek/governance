"""Tests for wedge.collectors.hmda."""

from __future__ import annotations

import math

import pandas as pd
import pytest

from wedge.collectors.hmda import (
    ORIGINATION_FEATURE_COLS,
    REQUIRED_HMDA_COLUMNS,
    derive_label,
    filter_to_regime,
    load_dataframe,
    load_hmda,
    map_features,
)


def _sample_df() -> pd.DataFrame:
    """A small synthetic HMDA-shaped frame covering the filter cases."""
    rows = [
        # row 0: keep — first-lien purchase, owner-occupied, originated
        dict(action_taken=1, loan_purpose=1, lien_status=1, occupancy_type=1,
             income=80, loan_amount=200000, loan_to_value_ratio="80.0",
             loan_term=360, debt_to_income_ratio="30%-<36%"),
        # row 1: keep — first-lien refi, owner-occupied, denied
        dict(action_taken=3, loan_purpose=31, lien_status=1, occupancy_type=1,
             income=50, loan_amount=180000, loan_to_value_ratio="95.5",
             loan_term=360, debt_to_income_ratio="50%-60%"),
        # row 2: keep — first-lien cash-out refi, owner-occupied, originated
        dict(action_taken=1, loan_purpose=32, lien_status=1, occupancy_type=1,
             income=120, loan_amount=300000, loan_to_value_ratio="60.0",
             loan_term=360, debt_to_income_ratio="39"),
        # row 3: drop — second lien
        dict(action_taken=1, loan_purpose=1, lien_status=2, occupancy_type=1,
             income=80, loan_amount=50000, loan_to_value_ratio="80.0",
             loan_term=180, debt_to_income_ratio="39"),
        # row 4: drop — investment property (occupancy_type=3)
        dict(action_taken=1, loan_purpose=1, lien_status=1, occupancy_type=3,
             income=200, loan_amount=400000, loan_to_value_ratio="70.0",
             loan_term=360, debt_to_income_ratio="39"),
        # row 5: drop — home improvement (loan_purpose=2, not 1/31/32)
        dict(action_taken=1, loan_purpose=2, lien_status=1, occupancy_type=1,
             income=80, loan_amount=20000, loan_to_value_ratio="40.0",
             loan_term=120, debt_to_income_ratio="39"),
        # row 6: drop — preapproval-denied (action_taken=7), not in {1,3}
        dict(action_taken=7, loan_purpose=1, lien_status=1, occupancy_type=1,
             income=80, loan_amount=200000, loan_to_value_ratio="80.0",
             loan_term=360, debt_to_income_ratio="39"),
    ]
    return pd.DataFrame(rows)


def test_required_columns_match_module_constant():
    df = _sample_df()
    for c in REQUIRED_HMDA_COLUMNS:
        assert c in df.columns, f"sample fixture missing required column {c}"


def test_filter_to_regime_keeps_first_lien_owner_occupied_purchase_or_refi():
    df = _sample_df()
    out = filter_to_regime(df)
    assert len(out) == 3
    assert set(out["loan_purpose"]) == {1, 31, 32}
    assert (out["lien_status"] == 1).all()
    assert (out["occupancy_type"] == 1).all()
    assert set(out["action_taken"]).issubset({1, 3})


def test_filter_to_regime_raises_on_missing_required_column():
    df = _sample_df().drop(columns=["debt_to_income_ratio"])
    with pytest.raises(ValueError, match="debt_to_income_ratio"):
        filter_to_regime(df)


def test_derive_label_grant_as_positive():
    """originated (action=1) -> label=1 (grant); denied (action=3) -> label=0 (deny).
    See spec §2.7 OD-9a / OD-13 for convention rationale."""
    s = pd.Series([1, 3, 1, 3])
    out = derive_label(s)
    assert out.tolist() == [1, 0, 1, 0]


def test_map_features_emits_expected_columns_and_derives_loan_to_income():
    df = filter_to_regime(_sample_df())
    feats = map_features(df)
    assert list(feats.columns) == ORIGINATION_FEATURE_COLS
    # row 0: loan_amount=200000 / income=80 = 2500
    assert feats["loan_to_income"].iloc[0] == pytest.approx(2500.0)
    # ltv parses numerically
    assert feats["ltv"].iloc[1] == pytest.approx(95.5)
    # dti banded -> ordinal float (deterministic, not NaN)
    assert not math.isnan(feats["dti"].iloc[0])
    # numeric-string dti also resolves
    assert not math.isnan(feats["dti"].iloc[2])


def test_map_features_handles_zero_or_missing_income():
    df = filter_to_regime(_sample_df()).copy()
    df.loc[0, "income"] = 0
    feats = map_features(df)
    # division-by-zero produces NaN, not inf
    assert math.isnan(feats["loan_to_income"].iloc[0])


def test_load_hmda_rejects_unmapped_feature_request(tmp_path):
    # Even before we check the file, the unknown-column guard should fire.
    with pytest.raises(ValueError, match="Unknown HMDA feature"):
        load_hmda(tmp_path / "nope.parquet", feature_cols=["fico_range_low"])


def test_load_hmda_raises_informative_error_for_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError, match="data/hmda/README.md"):
        load_hmda(tmp_path / "absent.parquet")


def test_load_hmda_end_to_end_via_parquet(tmp_path):
    parquet_path = tmp_path / "hmda_sample.parquet"
    _sample_df().to_parquet(parquet_path, index=False)
    cases = load_hmda(parquet_path, vintage="2022")
    assert len(cases) == 3
    for c in cases:
        assert c.origin == "real"
        assert c.synthetic_role is None
        assert c.vintage == "2022"
        assert c.label in (0, 1)
        assert set(c.features.keys()) == set(ORIGINATION_FEATURE_COLS)


def test_load_dataframe_attaches_label(tmp_path):
    parquet_path = tmp_path / "hmda_sample.parquet"
    _sample_df().to_parquet(parquet_path, index=False)
    df = load_dataframe(parquet_path)
    assert "label" in df.columns
    assert set(df["label"].unique()).issubset({0, 1})
    assert len(df) == 3
