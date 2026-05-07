#!/usr/bin/env python3
"""Recovery run: reassign and retry the 3 personas that failed in the
first paid run.

Original assignment (seed 20260506):
  examiner             -> nvidia/nemotron-3-super-120b-a12b:free  [empty response]
  civil_rights_attorney -> moonshotai/kimi-k2.6                   [content: null]
  technical_reviewer   -> xiaomi/mimo-v2.5-pro                    [content: null]

Reassignment: pull from the 2 unused models (deepseek, qwen), and dual-
use claude-haiku-4.5 for the third. Recorded here, not via the seed,
because this is a recovery — the seeded assignment is the primary
record and stays in assignment.json.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from run_review import write_config_for_persona, RIKUY_BIN  # noqa: E402

import subprocess  # noqa: E402

RECOVERY = {
    "examiner": "deepseek/deepseek-v4-pro",
    "civil_rights_attorney": "qwen/qwen3.6-plus",
    "technical_reviewer": "anthropic/claude-haiku-4.5",
}


def main():
    for persona, model in RECOVERY.items():
        config_path = write_config_for_persona(persona, model)
        cmd = [RIKUY_BIN, "-c", str(config_path), "review"]
        print(f"\n>>> {persona} ({model})")
        print(f"    {' '.join(cmd)}")
        subprocess.run(cmd)


if __name__ == "__main__":
    main()
