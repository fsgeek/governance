"""Calibration study: run the codebook pilot (plan §6). The pilot's codes are NEVER used in results.

Its job is to break the codebook: fields that don't decide, values missing, rules that conflict. Each item is coded
5 times at temperature 0.7 (arbiter seq 86); a field whose codes disagree across samples is a codebook ambiguity.

Per sampled bet file the coder gets the codebook (plan §2-§3 verbatim) and the file's frozen text. If the outcome
locator finds an outcome file mechanically (rules below) and it fits the context budget, the coder gets that too.
The locator is extraction, not judgment; every item records which rule fired, or `none`.

Outcome locator, first rule that yields a file wins; the file must first land after the freeze (`check_order`):
  same_dir   a sibling .md named like a result (result|analysis|scorecard|verdict|outcome), only when the bet's
             directory holds no other candidate bet file (a per-experiment directory);
  stem       in a shared directory, a sibling named like a result whose name contains the bet's topic (its file name
             without date prefix, pre-registration words, version and extension);
  cites_bet  a .md anywhere in the repo at HEAD, named like a result, whose text contains the bet file's name.
Ties go to the earliest-landing file; all hits are recorded.

    uv run python scripts/calibration/pilot_run.py prepare       # writes runs/calibration/pilot/items.jsonl
    uv run python scripts/calibration/pilot_run.py code --url http://127.0.0.1:8090
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import extract as X  # noqa: E402
import pilot_sample as S  # noqa: E402

HERE = Path(__file__).resolve().parents[2]
PLAN = HERE / "docs/superpowers/specs/2026-09-30-calibration-study-analysis-plan-DRAFT.md"
PILOT = HERE / "runs/calibration/pilot"
RESULT_NAME = re.compile(r"result|analysis|scorecard|verdict|outcome", re.IGNORECASE)
MAX_OUTCOME_CHARS = 18_000
SAMPLES, TEMPERATURE = 5, 0.7

FIELDS = ["bet_id_line", "bettor", "forecast_type", "stated_forecast", "register", "provenance_category",
          "outcome_as_scored_by_record", "outcome_basis", "record_scoring_error", "observed_vs_descended"]

INSTRUCTIONS = """You are coding one research file for a study, using the codebook below. Code ONLY from the text
given. A file may hold several bets; code each one. For every field give a value from the codebook, or
"UNDECIDABLE" with a short reason when the codebook's rules do not decide it from this text. If no outcome file is
given, code outcome fields "NO_OUTCOME_GIVEN". Then list every place where the codebook was ambiguous, missing a
value you needed, or where two rules conflicted.

Answer with JSON only, in this shape:
{"bets": [{"bet_id_line": "...", "bettor": "...", "forecast_type": "...", "stated_forecast": "...",
  "register": "...", "provenance_category": "...", "outcome_as_scored_by_record": "...", "outcome_basis": "...",
  "record_scoring_error": "...", "observed_vs_descended": "..."}],
 "not_a_bet_reason": "... or empty if the file holds bets",
 "codebook_problems": [{"field_or_rule": "...", "problem": "..."}]}

CODEBOOK (study plan sections 2 and 3, verbatim):
"""


def codebook_text() -> str:
    t = PLAN.read_text()
    return t[t.index("## 2. Unit of analysis"):t.index("## 4. Detected-error records")]


def frozen_text(root: Path, sha: str, path: str) -> str:
    return X.git(root, "show", f"{sha}:{path}")


def landing(root: Path, path: str) -> str | None:
    cs = X.commits_for(root, path)
    return cs[0].sha if cs else None


PREREG_WORDS = re.compile(r"-?(pre-?registration|preregistration|prereg|pre-reg|note|freeze|proposal)", re.IGNORECASE)


def topic(name: str) -> str:
    s = re.sub(r"\.md$", "", name)
    s = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", s)
    s = re.sub(r"-v\d+(\.\d+)*$", "", s)
    return PREREG_WORDS.sub("", s).strip("-")


def locate_outcomes(root: Path, c: dict, bets_in_dir: int) -> tuple[str, list[str]]:
    bet = X.Candidate(**{k: c[k] for k in X.Candidate.__dataclass_fields__})
    tracked = [p for p in X.git(root, "ls-files").splitlines() if p.endswith(".md") and p != bet.path]
    named = [p for p in tracked if RESULT_NAME.search(Path(p).name)]
    after = lambda ps: [p for p in ps if X.check_order(root, bet, p) == "outcome_after_freeze"]  # noqa: E731
    parent = str(Path(bet.path).parent)
    siblings = [p for p in named if str(Path(p).parent) == parent]
    if bets_in_dir == 1:
        same = after(siblings)
        if same:
            return "same_dir", same
    else:
        key = topic(Path(bet.path).name)
        stem_hits = after([p for p in siblings if key and key in Path(p).name])
        if stem_hits:
            return "stem", stem_hits
    stem = Path(bet.path).name
    cites = [p for p in named if stem in (root / p).read_text(errors="replace")]
    cites = after(cites)
    if cites:
        return "cites_bet", cites
    # Bet and result landed in one commit: the record can't order them. Given to the coder, labelled.
    together = [p for p in siblings if bets_in_dir == 1 and X.check_order(root, bet, p) == "same_commit"]
    return ("same_dir:same_commit", together) if together else ("none", [])


def earliest(root: Path, paths: list[str]) -> str:
    order = X.git(root, "log", "--reverse", "--format=%H", "--diff-filter=A", "--", *paths).split()
    first_of = {}
    for sha in order:
        for p in X.git(root, "diff-tree", "--no-commit-id", "--name-only", "-r", sha).splitlines():
            first_of.setdefault(p, order.index(sha))
    return min(paths, key=lambda p: first_of.get(p, 10**9))


def prepare() -> None:
    from collections import Counter
    cands = [json.loads(line) for line in (HERE / "runs/calibration/candidates.jsonl").read_text().splitlines()]
    per_dir = Counter((c["project"], str(Path(c["path"]).parent)) for c in cands)
    items = []
    for line in (PILOT / "sample.jsonl").read_text().splitlines():
        c = json.loads(line)
        root = X.PROJECTS_ROOT / c["project"]
        rule, hits = locate_outcomes(root, c, per_dir[(c["project"], str(Path(c["path"]).parent))])
        outcome_path = earliest(root, hits) if hits else None
        outcome_text, outcome_note = None, rule
        if outcome_path:
            outcome_text = (root / outcome_path).read_text(errors="replace")
            if S.RESIDENT.search(outcome_text):   # plan §2: residents' words are never given to coders
                outcome_text, outcome_note = None, f"{rule}:names_resident"
            elif len(outcome_text) > MAX_OUTCOME_CHARS:
                outcome_text, outcome_note = None, f"{rule}:exceeds_context"
        items.append({"id": c["id"], "freeze_sha": c["freeze_sha"], "locator": outcome_note,
                      "outcome_hits": hits, "outcome_path": outcome_path if outcome_text else None,
                      "bet_text": frozen_text(root, c["freeze_sha"], c["path"]), "outcome_text": outcome_text})
    with open(PILOT / "items.jsonl", "w") as f:
        for it in items:
            f.write(json.dumps(it) + "\n")
    for it in items:
        print(it["id"], it["locator"], it["outcome_path"], len(it["outcome_hits"]), file=sys.stderr)


def user_message(it: dict) -> str:
    msg = f"FILE: {it['id']} (frozen at {it['freeze_sha'][:7]})\n\n{it['bet_text']}\n"
    if it["outcome_text"]:
        msg += f"\n\nOUTCOME FILE (located mechanically, rule {it['locator']}): {it['outcome_path']}\n\n{it['outcome_text']}\n"
    else:
        msg += f"\n\nNO OUTCOME FILE GIVEN (locator: {it['locator']}).\n"
    return msg


def call(url: str, system: str, user: str, seed: int) -> dict:
    body = {"messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "temperature": TEMPERATURE, "seed": seed, "max_tokens": 2048,
            "response_format": {"type": "json_object"}}
    req = urllib.request.Request(f"{url}/v1/chat/completions", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=900) as r:
        return json.loads(r.read())


def code(url: str) -> None:
    system = INSTRUCTIONS + codebook_text()
    out = PILOT / "codes.jsonl"
    done = set()
    if out.exists():
        done = {(r["id"], r["sample"]) for r in map(json.loads, out.read_text().splitlines())}
    items = [json.loads(line) for line in (PILOT / "items.jsonl").read_text().splitlines()]
    with open(out, "a") as f:
        for it in items:
            for s in range(SAMPLES):
                if (it["id"], s) in done:
                    continue
                t0 = time.time()
                try:
                    resp = call(url, system, user_message(it), seed=1000 + s)
                    msg = resp["choices"][0]["message"]
                    text = msg.get("content") or ""
                    rec = {"id": it["id"], "sample": s, "secs": round(time.time() - t0, 1), "text": text,
                           "empty_or_tool_call": not text.strip() or bool(msg.get("tool_calls")),
                           "finish_reason": resp["choices"][0].get("finish_reason"), "usage": resp.get("usage")}
                except Exception as e:  # recorded, never dropped silently
                    rec = {"id": it["id"], "sample": s, "secs": round(time.time() - t0, 1), "error": repr(e)}
                f.write(json.dumps(rec) + "\n")
                f.flush()
                print(it["id"], s, rec.get("secs"), rec.get("finish_reason", rec.get("error")), file=sys.stderr)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["prepare", "code"])
    ap.add_argument("--url", default="http://127.0.0.1:8090")
    a = ap.parse_args()
    prepare() if a.step == "prepare" else code(a.url)


if __name__ == "__main__":
    main()
