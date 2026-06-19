"""Tests for the Stage-1 dirty-arm exclusion gate (review fix).

Verifies that:
  1. The dirty arm correctly detects and excludes proxy-using models.
  2. assert_gate raises on a fabricated failed result.
  3. The full control gate passes end-to-end (both arms).
"""
from __future__ import annotations

import pytest

from experiments.band_opening_control import (
    assert_gate,
    run_control,
    run_dirty_arm,
    run_full_control,
)


def test_dirty_arm_excluded_proxy_users():
    """All swept models that use protected_proxy must be excluded, not admissible."""
    result = run_dirty_arm(random_state=0)
    assert result["excluded_proxy_users"] is True, (
        f"Proxy-using models found in admissible set. dirty arm result: {result}"
    )


def test_dirty_arm_valid():
    """dirty_arm_valid must be True: exclusion works AND proxy is a real threat."""
    result = run_dirty_arm(random_state=0)
    assert result["dirty_arm_valid"] is True, (
        f"Dirty arm invalid. excluded_proxy_users={result['excluded_proxy_users']}, "
        f"dirty_gap_max={result['dirty_gap_max']:.4f}, "
        f"n_proxy_users_swept={result['n_proxy_users_swept']}"
    )


def test_dirty_arm_gap_exceeds_tau():
    """The max |approval_rate_gap| among proxy-using models must exceed tau=0.02."""
    TAU = 0.02
    result = run_dirty_arm(random_state=0)
    assert result["dirty_gap_max"] > TAU, (
        f"Proxy threat is inert: dirty_gap_max={result['dirty_gap_max']:.4f} <= tau={TAU}. "
        "The DGP may not produce a real proxy threat -- investigate synthetic_planted.py."
    )


def test_dirty_arm_exclusion_reason_mentions_proxy():
    """All exclusion records for proxy-including subsets must cite 'protected_proxy'."""
    result = run_dirty_arm(random_state=0)
    assert result["excluded_reason_ok"] is True, (
        "Some exclusion reasons do not mention 'protected_proxy'."
    )


def test_assert_gate_raises_on_failure():
    """assert_gate must raise RuntimeError when gate_passed is False."""
    fake_result = {
        "gate_passed": False,
        "clean_arm_passed": False,
        "both_arms": True,  # sentinel required for full-control result
        "dirty": {
            "excluded_proxy_users": False,
            "dirty_gap_max": 0.0,
            "dirty_arm_valid": False,
        }
    }
    with pytest.raises(RuntimeError, match="STAGE-1 CONTROL GATE FAILED"):
        assert_gate(fake_result)


def test_assert_gate_passes_on_success():
    """assert_gate must not raise when gate_passed is True."""
    fake_result = {"gate_passed": True, "both_arms": True}
    assert_gate(fake_result)  # should not raise


def test_assert_gate_rejects_partial_result():
    """assert_gate must reject a clean-arm-only result (missing both_arms sentinel)."""
    # Simulate what run_control returns (no both_arms key)
    partial_result = {"gate_passed": True, "cart": {}, "linear": {}, "gbm": {}}
    with pytest.raises(RuntimeError, match="requires a full-control result"):
        assert_gate(partial_result)

    # Also test an explicitly clean-arm result from run_control()
    clean_only = run_control(random_state=0)
    assert "both_arms" not in clean_only, "run_control must not include both_arms sentinel"
    with pytest.raises(RuntimeError, match="requires a full-control result"):
        assert_gate(clean_only)


def test_full_control_gate_passes():
    """End-to-end: run_full_control must pass with gate_passed=True."""
    result = run_full_control(random_state=0)
    assert result["gate_passed"] is True, (
        f"Full control gate failed. clean_arm_passed={result.get('clean_arm_passed')}, "
        f"dirty={result.get('dirty')}"
    )
    # Should not raise
    assert_gate(result)
