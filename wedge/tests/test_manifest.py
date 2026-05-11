"""Tests for the construction manifest emitter (spec §3.6 V1)."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from policy.encoder import PolicyConstraints
from wedge.manifest import emit_manifest, write_manifest
from wedge.rashomon import EpsilonAdmissibleSet


def _make_eps_set(*, n_members: int, epsilon: float, score_label: str) -> EpsilonAdmissibleSet:
    """Build an EpsilonAdmissibleSet with `n_members` placeholder entries.

    Only `len(within_epsilon)`, `epsilon`, and `score_label` are read by the
    manifest emitter; the SweepResult contents are irrelevant here. Sentinel
    integers stand in for SweepResult to keep the test focused.
    """
    return EpsilonAdmissibleSet(
        within_epsilon=list(range(n_members)),  # type: ignore[arg-type]
        out_of_epsilon=[],
        global_best_value=0.42,
        epsilon=epsilon,
        score_label=score_label,
    )


@pytest.fixture
def policy() -> PolicyConstraints:
    return PolicyConstraints(
        name="thin_demo_hmda",
        version="0.1.0",
        status="draft",
        monotonicity_map={"fico_range_low": 1, "dti": -1},
        mandatory_features=("fico_range_low", "dti"),
        prohibited_features=(),
        applicable_regime={},
    )


@pytest.fixture
def R_T() -> EpsilonAdmissibleSet:
    return _make_eps_set(n_members=7, epsilon=0.05, score_label="L_T(w_T=1.5)")


@pytest.fixture
def R_F() -> EpsilonAdmissibleSet:
    return _make_eps_set(n_members=4, epsilon=0.05, score_label="L_F(w_F=1.5)")


@pytest.fixture
def surprise_meta() -> dict:
    return {
        "model_id": "gbc_isotonic_v1",
        "training_sample_id": "lc-2016Q1Q4-completed",
    }


def test_manifest_contains_required_v1_fields(R_T, R_F, policy, surprise_meta):
    """Spec §3.6 V1 required fields all present."""
    manifest = emit_manifest(
        R_T=R_T,
        R_F=R_F,
        policy_constraints=policy,
        w_T=1.5,
        w_F=1.5,
        surprise_model_metadata=surprise_meta,
        run_id="2026-05-22-target-c-smoke",
        training_sample_id="lc-2015Q4",
        hypothesis_space="depth-bounded CART with cost-asymmetric loss",
    )
    required = {
        "policy_name",
        "policy_version",
        "hypothesis_space",
        "training_sample_id",
        "w_T",
        "w_F",
        "epsilon_T",
        "epsilon_F",
        "n_R_T",
        "n_R_F",
        "surprise_model_id",
        "run_id",
    }
    assert required.issubset(set(manifest.keys()))


def test_manifest_values_match_inputs(R_T, R_F, policy, surprise_meta):
    """Emitted values match the EpsilonAdmissibleSet and policy in hand."""
    manifest = emit_manifest(
        R_T=R_T,
        R_F=R_F,
        policy_constraints=policy,
        w_T=1.5,
        w_F=1.5,
        surprise_model_metadata=surprise_meta,
        run_id="run-x",
        training_sample_id="lc-2015Q4",
        hypothesis_space="depth-bounded CART",
    )
    assert manifest["policy_name"] == "thin_demo_hmda"
    assert manifest["policy_version"] == "0.1.0"
    assert manifest["epsilon_T"] == 0.05
    assert manifest["epsilon_F"] == 0.05
    assert manifest["n_R_T"] == 7
    assert manifest["n_R_F"] == 4
    assert manifest["w_T"] == 1.5
    assert manifest["w_F"] == 1.5
    assert manifest["run_id"] == "run-x"
    assert manifest["training_sample_id"] == "lc-2015Q4"
    assert manifest["surprise_model_id"] == "gbc_isotonic_v1"


def test_manifest_records_score_labels_for_audit(R_T, R_F, policy, surprise_meta):
    """Score labels from R_T/R_F carry through so the manifest records which
    loss (and which prime/weighted variant) constructed each set."""
    manifest = emit_manifest(
        R_T=R_T,
        R_F=R_F,
        policy_constraints=policy,
        w_T=1.5,
        w_F=1.5,
        surprise_model_metadata=surprise_meta,
        run_id="run-x",
        training_sample_id="lc-2015Q4",
        hypothesis_space="hs",
    )
    assert manifest["score_label_T"] == "L_T(w_T=1.5)"
    assert manifest["score_label_F"] == "L_F(w_F=1.5)"


def test_manifest_distinguishes_prime_variant(policy, surprise_meta):
    """When R_T/R_F come from surprise-weighted L_T'/L_F', score_label
    carries the prime marker so audit consumers can tell the two
    constructions apart."""
    R_T_prime = _make_eps_set(
        n_members=5, epsilon=0.05, score_label="L_T'(w_T=1.5, weighted)"
    )
    R_F_prime = _make_eps_set(
        n_members=5, epsilon=0.05, score_label="L_F'(w_F=1.5, weighted)"
    )
    manifest = emit_manifest(
        R_T=R_T_prime,
        R_F=R_F_prime,
        policy_constraints=policy,
        w_T=1.5,
        w_F=1.5,
        surprise_model_metadata=surprise_meta,
        run_id="run-y",
        training_sample_id="lc-2015Q4",
        hypothesis_space="hs",
    )
    assert "L_T'" in manifest["score_label_T"]
    assert "L_F'" in manifest["score_label_F"]
    assert "weighted" in manifest["score_label_T"]


def test_manifest_lists_v1_1_deferred_items(R_T, R_F, policy, surprise_meta):
    """Spec §3.6 V1 manifest is required to name V1.1-deferred items so
    regulator auditors know what's not yet reported."""
    manifest = emit_manifest(
        R_T=R_T,
        R_F=R_F,
        policy_constraints=policy,
        w_T=1.5,
        w_F=1.5,
        surprise_model_metadata=surprise_meta,
        run_id="r",
        training_sample_id="s",
        hypothesis_space="hs",
    )
    deferred = manifest["v1_1_deferred"]
    assert any("OD-10" in d for d in deferred)
    assert any("OD-15" in d for d in deferred)


def test_write_manifest_round_trips(R_T, R_F, policy, surprise_meta, tmp_path):
    """write_manifest produces JSON that round-trips losslessly via json.load."""
    manifest = emit_manifest(
        R_T=R_T,
        R_F=R_F,
        policy_constraints=policy,
        w_T=1.5,
        w_F=1.5,
        surprise_model_metadata=surprise_meta,
        run_id="r",
        training_sample_id="s",
        hypothesis_space="hs",
    )
    out = tmp_path / "manifest.json"
    write_manifest(manifest, out)
    loaded = json.loads(out.read_text())
    assert loaded == manifest
