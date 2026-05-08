"""
For near-unanimous-atypical cases (k in {1, 4}), identify which model is the
"odd one out" — the disagreer.

If a single model dominates the disagreer role, the consensus framing reduces
to "all models except model X agree" and the equally-good-models claim weakens.

If disagreer-identity is roughly uniform across models, consensus is a real
structural property of R(epsilon) rather than a euphemism for the peculiarity
of one model.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

RUNS = [
    ("2014Q3", "runs/2026-05-08T17-43-21Z.jsonl"),
    ("2015Q3", "runs/2026-05-08T16-26-41Z.jsonl"),
    ("2015Q4", "runs/2026-05-08T17-44-39Z.jsonl"),
]


def is_atypical(model_record: dict) -> bool:
    for ind in model_record.get("indeterminacy", []):
        if ind.get("species") == "local_density" and ind.get("direction") == "atypical":
            return True
    return False


def analyze_run(path: Path) -> tuple[Counter, Counter, int, int]:
    flag_alone = Counter()  # k=1: which model is the lone flagger
    abstain_alone = Counter()  # k=4: which model is the lone non-flagger
    n_k1 = 0
    n_k4 = 0
    for line in path.open():
        rec = json.loads(line)
        if rec.get("origin") != "real":
            continue
        models = rec["per_model"]
        flags = [(m["model_id"], is_atypical(m)) for m in models]
        flagged = [mid for mid, f in flags if f]
        not_flagged = [mid for mid, f in flags if not f]
        if len(flagged) == 1:
            n_k1 += 1
            flag_alone[flagged[0]] += 1
        elif len(flagged) == len(flags) - 1:
            n_k4 += 1
            abstain_alone[not_flagged[0]] += 1
    return flag_alone, abstain_alone, n_k1, n_k4


def main() -> None:
    repo = Path(__file__).resolve().parent.parent
    print()
    for vintage, rel in RUNS:
        flag_alone, abstain_alone, n_k1, n_k4 = analyze_run(repo / rel)
        print(f"=== {vintage} ===")
        if n_k1:
            print(f"  k=1 (lone flagger), n={n_k1}: distribution over models")
            for mid, ct in sorted(flag_alone.items()):
                pct = 100 * ct / n_k1
                bar = "#" * int(pct // 2)
                print(f"    {mid:>10}: {ct:>5d} ({pct:5.1f}%) {bar}")
        if n_k4:
            print(f"  k=4 (lone abstainer), n={n_k4}: distribution over models")
            for mid, ct in sorted(abstain_alone.items()):
                pct = 100 * ct / n_k4
                bar = "#" * int(pct // 2)
                print(f"    {mid:>10}: {ct:>5d} ({pct:5.1f}%) {bar}")
        print()


if __name__ == "__main__":
    main()
