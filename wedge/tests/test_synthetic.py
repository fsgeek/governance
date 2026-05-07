"""Tests for wedge.collectors.synthetic."""

from __future__ import annotations

import numpy as np

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
