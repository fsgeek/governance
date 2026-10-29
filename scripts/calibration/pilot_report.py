"""Calibration study: summarise the codebook pilot (plan §6). Pilot codes are never used in results.

Per item, the 5 samples are compared field by field. A field is `stable` on an item when every parsed sample gives
the same value for the item's first bet (values compared case-folded, whitespace-collapsed; `stated_forecast` and
`bet_id_line` are free text and only checked for UNDECIDABLE). Unparseable, empty and tool-call responses are
counted, never dropped. Every `UNDECIDABLE` reason and every `codebook_problems` entry is listed verbatim.

    uv run python scripts/calibration/pilot_report.py > runs/calibration/pilot/report.md
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

PILOT = Path(__file__).resolve().parents[2] / "runs/calibration/pilot"
CATEGORICAL = ["bettor", "forecast_type", "register", "provenance_category", "outcome_basis",
               "record_scoring_error", "observed_vs_descended"]
FREE = ["bet_id_line", "stated_forecast", "outcome_as_scored_by_record"]


def parse(text: str) -> dict | None:
    m = re.search(r"\{.*\}", text or "", re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


def norm(v) -> str:
    return re.sub(r"\s+", " ", str(v)).strip().casefold()


def head(v) -> str:
    """The value before any explanation: 'UNDECIDABLE: reason' -> 'undecidable'."""
    return norm(v).split(":")[0].split(" (")[0].split(" -")[0].strip()


def main() -> None:
    rows = [json.loads(line) for line in (PILOT / "codes.jsonl").read_text().splitlines() if line.strip()]
    items = {json.loads(line)["id"]: json.loads(line) for line in (PILOT / "items.jsonl").read_text().splitlines()}
    by_item = defaultdict(list)
    failures = Counter()
    for r in rows:
        if "error" in r:
            failures["request_error"] += 1
            continue
        if r.get("empty_or_tool_call"):
            failures["empty_or_tool_call"] += 1
            continue
        if r.get("finish_reason") == "length":
            failures["truncated"] += 1
        p = parse(r["text"])
        if p is None:
            failures["unparseable"] += 1
            continue
        by_item[r["id"]].append(p)

    stable, undec, values = Counter(), Counter(), defaultdict(Counter)
    nbets = defaultdict(list)
    problems, undec_reasons = [], []
    for i, ps in by_item.items():
        for p in ps:
            bets = p.get("bets") or []
            nbets[i].append(len(bets))
            for pr in p.get("codebook_problems") or []:
                problems.append((i, pr.get("field_or_rule", ""), pr.get("problem", "")))
            for b in bets:
                for f in CATEGORICAL + FREE:
                    if norm(b.get(f, "")).startswith("undecidable"):
                        undec[f] += 1
                        undec_reasons.append((i, f, str(b.get(f))))
        firsts = [(p.get("bets") or [{}])[0] for p in ps]
        for f in CATEGORICAL:
            vals = [head(b.get(f, "")) for b in firsts]
            for v in vals:
                values[f][v] += 1
            if len(ps) >= 2 and len(set(vals)) == 1:
                stable[f] += 1

    n = len(by_item)
    out = ["# Codebook pilot report (Phi-4; pilot codes never enter results)", "",
           f"Responses: {len(rows)}; parsed per item: "
           f"{sum(len(v) for v in by_item.values())}; failures: {dict(failures) or 'none'}.",
           f"Items with ≥1 parsed sample: {n} of {len(items)}.", "",
           "## Stability of categorical fields across the 5 samples (first bet per item)", "",
           "| field | items stable | values seen (count over samples) |", "|---|---|---|"]
    for f in CATEGORICAL:
        top = ", ".join(f"`{v or '∅'}` {c}" for v, c in values[f].most_common(8))
        out.append(f"| {f} | {stable[f]} / {n} | {top} |")
    out += ["", "## Bets found per file, across samples (disagreement = the unit of analysis is ambiguous)", ""]
    for i in sorted(nbets):
        out.append(f"- `{i}` ({items[i]['locator']}): {nbets[i]}")
    out += ["", "## UNDECIDABLE counts by field", ""] + [f"- {f}: {c}" for f, c in undec.most_common()]
    out += ["", "## UNDECIDABLE reasons, verbatim", ""] + [f"- `{i}` **{f}**: {t}" for i, f, t in undec_reasons]
    out += ["", "## codebook_problems, verbatim", ""] + [f"- `{i}` **{f}**: {t}" for i, f, t in problems]
    print("\n".join(out))


if __name__ == "__main__":
    main()
