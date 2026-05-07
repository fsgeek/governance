"""jsonl run writer with metadata sidecar.

A run produces two files in the output directory:

  runs/<run_id>.jsonl       — one Case record per line
  runs/<run_id>-meta.json   — run metadata: vintage, epsilon, members, etc.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from wedge.types import Case, case_to_json


@dataclass
class RunMetadata:
    run_id: str
    vintage: str
    epsilon: float
    random_seed: int
    members: list[dict[str, Any]] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def write_run(
    cases: list[Case], meta: RunMetadata, *, output_dir: Path | str
) -> tuple[Path, Path]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = output_dir / f"{meta.run_id}.jsonl"
    meta_path = output_dir / f"{meta.run_id}-meta.json"
    with jsonl_path.open("w", encoding="utf-8") as f:
        for c in cases:
            f.write(case_to_json(c))
            f.write("\n")
    with meta_path.open("w", encoding="utf-8") as f:
        json.dump(meta.to_dict(), f, indent=2)
        f.write("\n")
    return jsonl_path, meta_path
