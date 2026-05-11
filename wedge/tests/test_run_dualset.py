"""End-to-end smoke for the V_2 dual-set orchestration (plan Task 10).

These tests exercise the integration: surprise model trained on one cohort,
dual-set + revised dual-set built on a target cohort, per-case I_pred and
classification emitted, manifest written. They run against the synthetic
`tiny_noisy_dataset` fixture so they exercise the artifact shape without
needing real LC data.
"""
from __future__ import annotations

import json
from pathlib import Path

from wedge.orchestration import run_dual_set_target_c
from wedge.rashomon import SweepConfig
from wedge.tests.fixtures import FEATURE_COLS, tiny_noisy_dataset


def _small_sweep_config(feature_cols, seed: int) -> SweepConfig:
    return SweepConfig(
        max_depths=(3, 5),
        min_samples_leafs=(5, 10),
        feature_subsets=(tuple(feature_cols),),
        random_state=seed,
        holdout_fraction=0.30,
    )


def test_run_dual_set_target_c_writes_artifacts(tmp_path):
    """Orchestration writes jsonl + manifest; record count matches out-of-sample split size."""
    df_target = tiny_noisy_dataset(seed=0)
    df_surprise = tiny_noisy_dataset(seed=42)  # different cohort, same schema
    cfg = _small_sweep_config(FEATURE_COLS, seed=0)

    summary = run_dual_set_target_c(
        df_target=df_target,
        df_surprise_train=df_surprise,
        feature_cols=FEATURE_COLS,
        target_vintage_label="synthetic-V2",
        surprise_vintage_label="synthetic-S",
        output_dir=tmp_path,
        sweep_config=cfg,
        n_members=3,
    )

    jsonl_path = Path(summary["jsonl_path"])
    manifest_path = Path(summary["manifest_path"])
    assert jsonl_path.exists()
    assert manifest_path.exists()

    lines = jsonl_path.read_text().strip().splitlines()
    assert len(lines) == summary["n_oos_cases"]


def test_run_dual_set_records_have_required_fields(tmp_path):
    """Each per-case record names case_id, realized_outcome, i_pred (or null),
    and classification.category - the V1 contract for Target B consumers."""
    df = tiny_noisy_dataset(seed=0)
    cfg = _small_sweep_config(FEATURE_COLS, seed=0)
    summary = run_dual_set_target_c(
        df_target=df,
        df_surprise_train=tiny_noisy_dataset(seed=42),
        feature_cols=FEATURE_COLS,
        target_vintage_label="V2",
        surprise_vintage_label="S",
        output_dir=tmp_path,
        sweep_config=cfg,
        n_members=3,
    )
    valid_categories = {"Cat 1", "Cat 2", "ambiguous", "not_failure"}
    with Path(summary["jsonl_path"]).open() as fh:
        for line in fh:
            record = json.loads(line)
            assert "case_id" in record
            assert "realized_outcome" in record
            assert record["realized_outcome"] in (0, 1)
            assert "i_pred" in record
            assert "classification" in record
            assert record["classification"]["category"] in valid_categories


def test_run_dual_set_classification_counts_partition_oos(tmp_path):
    """category_counts is a partition of the out-of-sample set."""
    df = tiny_noisy_dataset(seed=0)
    cfg = _small_sweep_config(FEATURE_COLS, seed=0)
    summary = run_dual_set_target_c(
        df_target=df,
        df_surprise_train=tiny_noisy_dataset(seed=42),
        feature_cols=FEATURE_COLS,
        target_vintage_label="V2",
        surprise_vintage_label="S",
        output_dir=tmp_path,
        sweep_config=cfg,
        n_members=3,
    )
    counts = summary["category_counts"]
    assert sum(counts.values()) == summary["n_oos_cases"]


def test_run_dual_set_manifest_carries_revised_summary(tmp_path):
    """Manifest records both original (V1 required) and revised-set fields so
    downstream audit can tell the two constructions apart."""
    df = tiny_noisy_dataset(seed=0)
    cfg = _small_sweep_config(FEATURE_COLS, seed=0)
    summary = run_dual_set_target_c(
        df_target=df,
        df_surprise_train=tiny_noisy_dataset(seed=42),
        feature_cols=FEATURE_COLS,
        target_vintage_label="V2",
        surprise_vintage_label="S",
        output_dir=tmp_path,
        sweep_config=cfg,
        n_members=3,
    )
    manifest = json.loads(Path(summary["manifest_path"]).read_text())
    assert "revised_set_summary" in manifest
    rev = manifest["revised_set_summary"]
    assert rev["score_label_T_prime"].startswith("L_T'")
    assert rev["score_label_F_prime"].startswith("L_F'")
    assert "weighted" in rev["score_label_T_prime"]


def test_run_dual_set_summary_reports_set_sizes(tmp_path):
    """Summary surfaces |R_T|, |R_F|, |R_T'|, |R_F'| so callers can see at
    a glance whether the surprise weighting changed the set composition."""
    df = tiny_noisy_dataset(seed=0)
    cfg = _small_sweep_config(FEATURE_COLS, seed=0)
    summary = run_dual_set_target_c(
        df_target=df,
        df_surprise_train=tiny_noisy_dataset(seed=42),
        feature_cols=FEATURE_COLS,
        target_vintage_label="V2",
        surprise_vintage_label="S",
        output_dir=tmp_path,
        sweep_config=cfg,
        n_members=3,
    )
    for k in ("n_R_T", "n_R_F", "n_R_T_prime", "n_R_F_prime"):
        assert k in summary
        assert summary[k] >= 0
