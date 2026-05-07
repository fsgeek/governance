"""Tests for wedge.collectors.synthetic."""

from __future__ import annotations

import pandas as pd

from wedge.collectors.synthetic import generate_boundary_cases
from wedge.tests.fixtures import tiny_separable_dataset


def test_generate_returns_synthetic_origin():
    real = tiny_separable_dataset(seed=0)
    syn = generate_boundary_cases(real, n=20, vintage="2015Q3", seed=0)
    assert len(syn) == 20
    for c in syn:
        assert c.origin == "synthetic"
        assert c.synthetic_role == "hypothetical-scenario"
        assert c.label is None
        assert c.vintage == "2015Q3"


def test_generate_extends_into_lower_fico_tail():
    """Boundary extension should produce some cases below the real-data floor."""
    real = tiny_separable_dataset(seed=0)
    real_fico_min = real["fico_proxy"].min()
    syn = generate_boundary_cases(real, n=200, vintage="2015Q3", seed=0)
    syn_fico = [c.features["fico_proxy"] for c in syn]
    # We deliberately extend; expect at least some synthetic cases below real min.
    below_count = sum(1 for x in syn_fico if x < real_fico_min)
    assert below_count > 0


def test_generate_marginal_features_present():
    real = tiny_separable_dataset(seed=0)
    syn = generate_boundary_cases(real, n=10, vintage="2015Q3", seed=0)
    for c in syn:
        # Must have all real-data feature columns except 'label'.
        for col in ["fico_proxy", "dti_proxy", "income_proxy", "history_depth"]:
            assert col in c.features


def test_generate_reproducible_with_seed():
    real = tiny_separable_dataset(seed=0)
    syn_a = generate_boundary_cases(real, n=10, vintage="2015Q3", seed=42)
    syn_b = generate_boundary_cases(real, n=10, vintage="2015Q3", seed=42)
    a = [c.features for c in syn_a]
    b = [c.features for c in syn_b]
    assert a == b


def test_generate_raises_on_empty_dataframe():
    empty = pd.DataFrame(columns=["fico_proxy", "dti_proxy"])
    try:
        generate_boundary_cases(empty, n=5, vintage="2015Q3", seed=0)
    except ValueError as e:
        assert "empty" in str(e).lower()
        return
    raise AssertionError("expected ValueError for empty real DataFrame")


def test_generate_extends_into_lower_real_lc_fico_range_low():
    """The default lower-extension list must include the real LC column name
    'fico_range_low' so that running on real LC data actually extends, not
    silently degrades to plain marginal sampling."""
    real = pd.DataFrame({
        "fico_range_low": [620, 650, 700, 750, 780],
        "dti": [10, 15, 20, 25, 30],
        "annual_inc": [40000, 50000, 60000, 70000, 80000],
        "emp_length": [1, 3, 5, 7, 10],
    })
    real_min = real["fico_range_low"].min()
    syn = generate_boundary_cases(real, n=200, vintage="2015Q3", seed=0)
    below = sum(1 for c in syn if c.features["fico_range_low"] < real_min)
    assert below > 0, "default lower extension should fire for real LC column 'fico_range_low'"
