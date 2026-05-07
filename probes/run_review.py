#!/usr/bin/env python3
"""Rikuy reviewer runner for the FS AI RMF position paper.

Generates a seeded random assignment of 8 personas to 8 distinct models,
sampled from the 10-model survivor set in scores.md. Then invokes rikuy
once per persona with the assigned model. Each persona's review goes to
its own output subdirectory.

Per-persona reference grounding (probes/reference_block.md inlined in
each persona prompt) is what dissolves the disclaim/confab eligibility
constraint — see handoff.md decision #2.

Usage:
  python run_review.py --plan        # write assignment.json, no API calls
  python run_review.py --dry-run     # show prompts, no API calls
  python run_review.py --only=NAME   # run a single persona only
  python run_review.py               # full paid run (8 calls)
"""
from __future__ import annotations

import json
import random
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

SEED = 20260506

MODELS_DISCLAIM = [
    "anthropic/claude-haiku-4.5",
    "moonshotai/kimi-k2.6",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "x-ai/grok-4.3",
    "xiaomi/mimo-v2.5-pro",
    "z-ai/glm-5.1",
]
MODELS_CONFAB = [
    "deepseek/deepseek-v4-pro",
    "mistralai/mistral-large-2512",
    "openai/gpt-oss-120b",
    "qwen/qwen3.6-plus",
]
MODELS = MODELS_DISCLAIM + MODELS_CONFAB

PERSONAS = [
    "examiner",
    "vendor",
    "compliance_officer",
    "civil_rights_attorney",
    "technical_reviewer",
    "frame_skeptic",
    "sympathetic_regulator",
    "self_examiner",
]

GOV_ROOT = Path("/home/tony/projects/governance")
PERSONAS_DIR = GOV_ROOT / "probes" / "personas"
CONFIGS_DIR = GOV_ROOT / "probes" / "configs"
ASSIGN_FILE = GOV_ROOT / "probes" / "assignment.json"
REVIEWS_DIR = GOV_ROOT / "probes" / "reviews"

RIKUY_BIN = "/home/tony/projects/rikuy/.venv/bin/paper-review"


def make_assignment() -> dict:
    rng = random.Random(SEED)
    chosen = rng.sample(MODELS, k=len(PERSONAS))
    assignment = dict(zip(PERSONAS, chosen))
    return {
        "seed": SEED,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "models_pool": MODELS,
        "models_unused": [m for m in MODELS if m not in chosen],
        "personas": PERSONAS,
        "assignment": assignment,
    }


def write_config_for_persona(persona_name: str, model: str) -> Path:
    config = {
        "project": {"name": f"FS AI RMF - {persona_name}"},
        "document": {
            "format": "latex",
            "path": str(GOV_ROOT),
            "preferred_order": [
                "section1.tex",
                "section2.tex",
                "section3.tex",
                "section4.tex",
                "section5.tex",
                "section6.tex",
                "section7.tex",
            ],
        },
        "venue": {
            "name": "arXiv preprint",
            "type": "position paper / tech report",
            "description": "researcher-to-regulator position paper on FS AI RMF",
        },
        "models": {"default": model, "temperature": 0.3},
        "judges": [
            {
                "adversarial": {
                    "personas": [persona_name],
                    "persona_search_dirs": [str(PERSONAS_DIR)],
                }
            }
        ],
        "output": {"directory": str(REVIEWS_DIR / persona_name)},
    }
    config_path = CONFIGS_DIR / f"{persona_name}.yaml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w") as f:
        yaml.safe_dump(config, f, sort_keys=False)
    return config_path


def main():
    args = set(sys.argv[1:])
    plan_only = "--plan" in args
    dry_run = "--dry-run" in args
    only = None
    for a in sys.argv[1:]:
        if a.startswith("--only="):
            only = a.split("=", 1)[1]

    record = make_assignment()
    ASSIGN_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(ASSIGN_FILE, "w") as f:
        json.dump(record, f, indent=2)
    print(f"Assignment written to {ASSIGN_FILE}")
    print(f"Seed: {record['seed']}")
    for persona, model in record["assignment"].items():
        mark = "*" if (only is None or persona == only) else " "
        print(f"  {mark} {persona:25s} -> {model}")
    print(f"Unused models: {record['models_unused']}")

    if plan_only:
        return 0

    targets = (
        [(only, record["assignment"][only])]
        if only
        else list(record["assignment"].items())
    )

    for persona, model in targets:
        config_path = write_config_for_persona(persona, model)
        cmd = [RIKUY_BIN, "-c", str(config_path), "review"]
        if dry_run:
            cmd.append("--dry-run")
        print(f"\n>>> {persona} ({model})")
        print(f"    {' '.join(cmd)}")
        result = subprocess.run(cmd)
        if result.returncode != 0:
            print(f"    !! exit code {result.returncode}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
