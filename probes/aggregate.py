#!/usr/bin/env python3
"""Aggregate findings across the 8 persona reviews into a single markdown.

Picks the latest JSONL per persona (so re-runs override earlier failed
attempts). Groups by severity (FATAL > MAJOR > MINOR) and within each
severity, by persona.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

REVIEWS_DIR = Path("/home/tony/projects/governance/probes/reviews")
OUT_PATH = Path("/home/tony/projects/governance/probes/findings_summary.md")


def load_latest_per_persona() -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    assessments: dict[str, str] = {}
    models: dict[str, str] = {}
    for persona_dir in sorted(REVIEWS_DIR.iterdir()):
        if not persona_dir.is_dir():
            continue
        jsonls = sorted(persona_dir.glob("review_*.jsonl"))
        if not jsonls:
            continue
        latest = jsonls[-1]
        findings = []
        assessment = ""
        model = ""
        with open(latest) as f:
            for line in f:
                r = json.loads(line)
                if r.get("record_type") == "finding":
                    findings.append(r)
                elif r.get("record_type") == "judge_result":
                    assessment = r.get("assessment", "") or ""
                    model = r.get("model_id", "") or ""
        out[persona_dir.name] = findings
        assessments[persona_dir.name] = assessment
        models[persona_dir.name] = model
    return out, assessments, models


def main():
    findings_by_persona, assessments, models = load_latest_per_persona()

    # Aggregate counts
    total = 0
    n_fatal = n_major = n_minor = 0
    for findings in findings_by_persona.values():
        for f in findings:
            total += 1
            sev = f.get("severity", "")
            if sev == "FATAL":
                n_fatal += 1
            elif sev == "MAJOR":
                n_major += 1
            elif sev == "MINOR":
                n_minor += 1

    lines = []
    lines.append("# FS AI RMF Position Paper — Persona Review Findings")
    lines.append("")
    lines.append(f"**Total findings:** {total} ({n_fatal} FATAL / {n_major} MAJOR / {n_minor} MINOR)")
    lines.append("")
    lines.append("## Per-persona summary")
    lines.append("")
    lines.append("| Persona | Model | F | M | m | Total |")
    lines.append("|---|---|---:|---:|---:|---:|")
    for persona, findings in sorted(findings_by_persona.items()):
        f = sum(1 for x in findings if x.get("severity") == "FATAL")
        m = sum(1 for x in findings if x.get("severity") == "MAJOR")
        i = sum(1 for x in findings if x.get("severity") == "MINOR")
        lines.append(f"| {persona} | `{models[persona]}` | {f} | {m} | {i} | {len(findings)} |")
    lines.append("")

    # FATAL findings first, in detail
    for severity in ("FATAL", "MAJOR", "MINOR"):
        flat = []
        for persona, findings in findings_by_persona.items():
            for f in findings:
                if f.get("severity") == severity:
                    flat.append((persona, f))
        if not flat:
            continue
        lines.append(f"## {severity} findings ({len(flat)})")
        lines.append("")
        for persona, f in flat:
            fid = f.get("finding_id", "?")
            loc = f.get("location", "?")
            claim = (f.get("claim", "") or "").strip()
            analysis = (f.get("analysis", "") or "").strip()
            suggestion = (f.get("suggestion", "") or "").strip()
            lines.append(f"### `{fid}` — {persona} @ {loc}")
            lines.append("")
            if claim:
                # Quote the claim block-style
                claim_q = "\n".join(f"> {ln}" for ln in claim.split("\n"))
                lines.append("**Paper claim:**")
                lines.append("")
                lines.append(claim_q)
                lines.append("")
            if analysis:
                lines.append("**Concern:** " + analysis)
                lines.append("")
            if suggestion:
                lines.append("**Suggested fix:** " + suggestion)
                lines.append("")

    # Assessments
    lines.append("## Persona overall assessments")
    lines.append("")
    for persona in sorted(assessments.keys()):
        a = assessments[persona].strip()
        if a:
            lines.append(f"### {persona} (`{models[persona]}`)")
            lines.append("")
            lines.append(a)
            lines.append("")

    OUT_PATH.write_text("\n".join(lines))
    print(f"Wrote {OUT_PATH} ({len(lines)} lines, {OUT_PATH.stat().st_size} bytes)")
    print(f"Total: {total} findings ({n_fatal} F / {n_major} M / {n_minor} m)")


if __name__ == "__main__":
    main()
