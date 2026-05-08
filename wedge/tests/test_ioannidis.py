"""Unit tests for the ioannidis-suspicion indeterminacy battery."""

from __future__ import annotations

import math

from wedge.indeterminacy.ioannidis import (
    DTI_THRESHOLDS,
    compute_battery,
    compute_round_numbers,
    compute_threshold_hugging,
)


# ---------- round-numbers ----------

def test_irregular_income_scores_zero():
    comp = compute_round_numbers({"annual_inc": 47823.0})
    assert comp.species == "ioannidis_round_numbers"
    assert comp.score == 0.0
    assert comp.direction == "irregular"
    assert comp.factor_support == []


def test_multiple_of_25k_top_tier():
    comp = compute_round_numbers({"annual_inc": 50000.0})
    # 50000 is also a multiple of 10000 and 5000, but tiers order to 25000 first
    assert comp.score == 1.0
    assert comp.direction == "multiple_of_25000"


def test_multiple_of_10k_not_25k():
    comp = compute_round_numbers({"annual_inc": 60000.0})
    # 60000 = 25000 * 2.4, not a multiple of 25k; is multiple of 10k
    assert comp.score == 0.6
    assert comp.direction == "multiple_of_10000"


def test_multiple_of_5k_not_10k():
    comp = compute_round_numbers({"annual_inc": 65000.0})
    assert comp.score == 0.3
    assert comp.direction == "multiple_of_5000"


def test_multiple_of_1k_not_5k():
    comp = compute_round_numbers({"annual_inc": 67000.0})
    assert comp.score == 0.1
    assert comp.direction == "multiple_of_1000"


def test_missing_income_returns_missing():
    comp = compute_round_numbers({"annual_inc": None})
    assert comp.score == 0.0
    assert comp.direction == "missing"


def test_nan_income_returns_missing():
    comp = compute_round_numbers({"annual_inc": float("nan")})
    assert comp.direction == "missing"


def test_zero_income_returns_missing():
    comp = compute_round_numbers({"annual_inc": 0.0})
    assert comp.direction == "missing"


def test_float_noise_tolerated():
    """LC stores income as float; tiny noise around an integer should still match."""
    comp = compute_round_numbers({"annual_inc": 50000.0001})
    assert comp.score == 1.0
    assert comp.direction == "multiple_of_25000"


# ---------- threshold-hugging ----------

def test_dti_at_exact_threshold_fires():
    comp = compute_threshold_hugging({"dti": 30.0})
    assert comp.species == "ioannidis_threshold_hugging"
    assert comp.score == 1.0
    assert comp.direction == "at_threshold_30"


def test_dti_within_tolerance_fires():
    comp = compute_threshold_hugging({"dti": 36.04})
    assert comp.score == 1.0
    assert comp.direction == "at_threshold_36"


def test_dti_off_threshold_zero():
    comp = compute_threshold_hugging({"dti": 32.7})
    assert comp.score == 0.0
    assert comp.direction == "off_threshold"


def test_dti_missing_returns_missing():
    comp = compute_threshold_hugging({"dti": None})
    assert comp.score == 0.0
    assert comp.direction == "missing"


def test_dti_nan_returns_missing():
    comp = compute_threshold_hugging({"dti": math.nan})
    assert comp.direction == "missing"


def test_all_known_thresholds_fire():
    """Every threshold in DTI_THRESHOLDS should fire on its exact value."""
    for t in DTI_THRESHOLDS:
        comp = compute_threshold_hugging({"dti": t})
        assert comp.score == 1.0, f"threshold {t} did not fire"
        assert comp.direction == f"at_threshold_{t:.0f}"


# ---------- battery ----------

def test_battery_returns_two_components():
    comps = compute_battery({"annual_inc": 50000.0, "dti": 30.0})
    species = {c.species for c in comps}
    assert species == {"ioannidis_round_numbers", "ioannidis_threshold_hugging"}


def test_battery_handles_missing_features():
    """Battery should still emit a component per test even when inputs are absent."""
    comps = compute_battery({})
    assert len(comps) == 2
    for c in comps:
        assert c.score == 0.0
        assert c.direction == "missing"
