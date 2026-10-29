"""Calibration study: draw the codebook-pilot sample (plan §6, "Both, in order").

Mechanical, no judgment, no outcomes read. From the extracted candidates it drops, and counts per project:
- `before_cutoff_claim_not_bet` (hamutay before 8c144c0: claims, not bets);
- files whose frozen text names a resident (plan §2, excluded by speaker; for the pilot the whole file is left out
  rather than redacted, which is conservative and is reported);
- files longer than the pilot coder's context budget (plan §6: Phi-4, 16K context; left out and counted).
Then it draws about 10% of the eligible files, stratified by project, at least one per project, with a seed that is
committed and stamped before the draw. The pilot's codes are never used in results.

    uv run python scripts/calibration/pilot_sample.py > runs/calibration/pilot/sample.jsonl
"""
from __future__ import annotations

import json
import random
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

PROJECTS_ROOT = Path("/home/tony/projects")
CANDIDATES = Path(__file__).resolve().parents[2] / "runs/calibration/candidates.jsonl"

SEED = 20261028        # fixed in the commit before the draw; never changed after it
FRACTION = 0.10
MAX_CHARS = 28_000     # ~7-8K tokens of bet text, leaving room for the codebook prompt and the answer

# Resident names (plan §2 r2: door:elder, door:fable / Sut'i, door:heartbeat, door:qwen, Marker, the Lunas).
# "qwen" also matches the model; a pilot can afford the false positives.
RESIDENT = re.compile(r"door:\w+|Sut'i|\bMarker\b|\bLuna\b|\belder\b|\bheartbeat\b|\bqwen\b", re.IGNORECASE)


def frozen_text(c: dict) -> str:
    root = PROJECTS_ROOT / c["project"]
    return subprocess.run(["git", "-C", str(root), "show", f"{c['freeze_sha']}:{c['path']}"],
                          capture_output=True, text=True, check=True).stdout


def exclusion(c: dict, text: str) -> str | None:
    if "before_cutoff_claim_not_bet" in c["flags"]:
        return "before_cutoff"
    if RESIDENT.search(text):
        return "names_resident"
    if len(text) > MAX_CHARS:
        return "exceeds_context"
    return None


def allocate(counts: dict[str, int], fraction: float) -> dict[str, int]:
    """Largest-remainder proportional allocation, at least one per project, never more than it has."""
    total = round(fraction * sum(counts.values()))
    quota = {p: fraction * n for p, n in counts.items()}
    alloc = {p: max(1, min(n, int(quota[p]))) for p, n in counts.items()}
    for p in sorted(counts, key=lambda p: (quota[p] - int(quota[p]), p), reverse=True):
        if sum(alloc.values()) >= total:
            break
        if alloc[p] < counts[p]:
            alloc[p] += 1
    return alloc


def draw(eligible: dict[str, list[str]], alloc: dict[str, int], seed: int) -> list[str]:
    rng = random.Random(seed)
    out = []
    for p in sorted(eligible):
        out += rng.sample(sorted(eligible[p]), alloc[p])
    return out


def main() -> None:
    cands = [json.loads(line) for line in CANDIDATES.read_text().splitlines() if line.strip()]
    eligible, excluded = defaultdict(list), Counter()
    by_id = {}
    for c in cands:
        why = exclusion(c, frozen_text(c))
        if why:
            excluded[(c["project"], why)] += 1
        else:
            eligible[c["project"]].append(c["id"])
            by_id[c["id"]] = c
    alloc = allocate({p: len(v) for p, v in eligible.items()}, FRACTION)
    for i in draw(eligible, alloc, SEED):
        print(json.dumps(by_id[i]))
    report = {"seed": SEED, "fraction": FRACTION, "max_chars": MAX_CHARS,
              "eligible": {p: len(v) for p, v in sorted(eligible.items())}, "allocated": dict(sorted(alloc.items())),
              "excluded": {f"{p}:{w}": n for (p, w), n in sorted(excluded.items())}}
    print(json.dumps(report), file=sys.stderr)


if __name__ == "__main__":
    main()
