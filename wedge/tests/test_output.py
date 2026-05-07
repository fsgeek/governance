"""Tests for wedge.output."""

from __future__ import annotations

import json

from wedge.output import RunMetadata, write_run
from wedge.types import Case


def _case(case_id, label=0):
    return Case(
        case_id=case_id,
        origin="real",
        synthetic_role=None,
        vintage="2015Q3",
        features={"fico_proxy": 720, "dti_proxy": 18},
        label=label,
        per_model=[],
    )


def test_write_run_creates_jsonl_and_meta(tmp_path):
    cases = [_case("a"), _case("b", label=1)]
    meta = RunMetadata(
        run_id="2026-05-07T12:00:00Z",
        vintage="2015Q3",
        epsilon=0.02,
        random_seed=0,
        members=[
            {"model_id": "tree_1", "max_depth": 5, "min_samples_leaf": 50, "feature_subset": ["a", "b"]},
        ],
        notes="wedge first run",
    )
    out_jsonl, out_meta = write_run(cases, meta, output_dir=tmp_path)
    # Files exist.
    assert out_jsonl.exists()
    assert out_meta.exists()
    # jsonl: one record per case.
    lines = out_jsonl.read_text().strip().split("\n")
    assert len(lines) == 2
    parsed = [json.loads(line) for line in lines]
    assert {p["case_id"] for p in parsed} == {"a", "b"}
    # Meta sidecar carries the run metadata.
    meta_payload = json.loads(out_meta.read_text())
    assert meta_payload["run_id"] == "2026-05-07T12:00:00Z"
    assert meta_payload["vintage"] == "2015Q3"
    assert meta_payload["epsilon"] == 0.02


def test_write_run_filenames_use_run_id_safely(tmp_path):
    meta = RunMetadata(
        run_id="2026-05-07T12-00-00Z",  # safe characters only
        vintage="2015Q3",
        epsilon=0.02,
        random_seed=0,
        members=[],
    )
    out_jsonl, out_meta = write_run([], meta, output_dir=tmp_path)
    assert "2026-05-07T12-00-00Z" in out_jsonl.name
    assert "2026-05-07T12-00-00Z" in out_meta.name
