"""Tests for wedge.metrics."""

from __future__ import annotations

from wedge.metrics import (
    is_outcome_agreer,
    pairwise_factor_support_overlap,
)
from wedge.types import FactorSupportEntry, PerModelOutput


def _pmo(model_id, T, F, fs_T_features=(), fs_F_features=()):
    return PerModelOutput(
        model_id=model_id,
        T=T,
        F=F,
        factor_support_T=[FactorSupportEntry(f, 0.5) for f in fs_T_features],
        factor_support_F=[FactorSupportEntry(f, 0.5) for f in fs_F_features],
        path=[],
        leaf="leaf_x",
    )


def test_outcome_agreer_all_grant_with_tight_spread():
    pmos = [
        _pmo("m1", T=0.80, F=0.20),
        _pmo("m2", T=0.78, F=0.22),
        _pmo("m3", T=0.75, F=0.25),
    ]
    assert is_outcome_agreer(pmos, t_spread_max=0.10) is True


def test_outcome_agreer_split_decisions_returns_false():
    pmos = [
        _pmo("m1", T=0.80, F=0.20),
        _pmo("m2", T=0.40, F=0.60),  # this one votes deny
    ]
    assert is_outcome_agreer(pmos, t_spread_max=0.10) is False


def test_outcome_agreer_tspread_too_wide_returns_false():
    pmos = [
        _pmo("m1", T=0.95, F=0.05),
        _pmo("m2", T=0.55, F=0.45),  # same direction (>0.5) but spread = 0.40
    ]
    assert is_outcome_agreer(pmos, t_spread_max=0.10) is False


def test_pairwise_overlap_identical_supports_returns_one():
    pmos = [
        _pmo("m1", T=0.8, F=0.2, fs_T_features=("a", "b", "c")),
        _pmo("m2", T=0.8, F=0.2, fs_T_features=("a", "b", "c")),
    ]
    overlap_T, overlap_F = pairwise_factor_support_overlap(pmos)
    assert abs(overlap_T - 1.0) < 1e-9


def test_pairwise_overlap_disjoint_supports_returns_zero():
    pmos = [
        _pmo("m1", T=0.8, F=0.2, fs_T_features=("a", "b")),
        _pmo("m2", T=0.8, F=0.2, fs_T_features=("c", "d")),
    ]
    overlap_T, overlap_F = pairwise_factor_support_overlap(pmos)
    assert overlap_T == 0.0


def test_pairwise_overlap_partial():
    pmos = [
        _pmo("m1", T=0.8, F=0.2, fs_T_features=("a", "b", "c")),
        _pmo("m2", T=0.8, F=0.2, fs_T_features=("b", "c", "d")),
    ]
    overlap_T, _ = pairwise_factor_support_overlap(pmos)
    # Jaccard({a,b,c}, {b,c,d}) = |{b,c}| / |{a,b,c,d}| = 2/4 = 0.5
    assert abs(overlap_T - 0.5) < 1e-9


def test_pairwise_overlap_three_models_averages_pairs():
    pmos = [
        _pmo("m1", T=0.8, F=0.2, fs_T_features=("a", "b")),
        _pmo("m2", T=0.8, F=0.2, fs_T_features=("a", "b")),
        _pmo("m3", T=0.8, F=0.2, fs_T_features=("c", "d")),
    ]
    overlap_T, _ = pairwise_factor_support_overlap(pmos)
    # Pairs: (m1,m2)=1.0, (m1,m3)=0.0, (m2,m3)=0.0  -> mean = 1/3
    assert abs(overlap_T - 1.0 / 3.0) < 1e-9
