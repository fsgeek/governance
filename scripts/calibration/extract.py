"""Calibration study: mechanical extraction of candidate bets (plan §2, §4a, §6).

Extraction, not judgment. For each project it lists candidate bet files, the freeze commit under that
project's own convention, whether the freeze commit carries an OpenTimestamps stamp, and later edits.
It never reads an outcome's content and never scores. `check_order` verifies, for a (bet, outcome file)
pair a coder supplies, that the outcome first landed in a later commit than the freeze.

Every id it emits is project-qualified (`project:path`, `project:obs-0001`): ledgers share local numbering.

    uv run python scripts/calibration/extract.py > runs/calibration/candidates.jsonl
"""
from __future__ import annotations

import fnmatch
import json
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

PROJECTS_ROOT = Path("/home/tony/projects")

# Never listed, whatever a glob matches (plan §2 exclusions; owners' consent replies).
EXCLUDE = {
    "*": ["timestamps/*", "*.ots", "*.ots.bak", "*/scratch/*", "scratch/*"],
    "hamutay": ["community/*", "deploy/plaza/*", "docs/retraction-taxonomy-20260930/*", "*/rows/*"],
    "tessera": ["docs/exploration-*", "*/READ-*", "READ-*", "docs/travelog.md", "*/diagnostic*/*"],
    "quantumos": ["*surveillance*"],
    "levadura_salvaje": ["data/pilot-v1-raw-logs*"],
    "governance": ["*TEMPLATE*", "*template*", "*/README.md"],
}

# Candidate bet files, by each project's own naming (scout inventories, 2026-10-07).
INCLUDE = {
    "governance": ["*pre-reg*.md", "*prereg*.md", "*preregistration*.md", "*pre-registration*.md"],
    "levadura_salvaje": ["predictions/*.md"],
    "tessera": ["docs/phase-0-prereg.md", "formal/*PREDICTIONS*.md", "formal/*/PROBE.md"],
    "quantumos": ["docs/superpowers/specs/*prereg*.md", "docs/superpowers/specs/2026-07-10-s1-run-note.md",
                  "docs/superpowers/specs/2026-07-23-pool-retry-sweep-note.md"],
    "yupi": ["docs/*prereg*.md", "docs/*-freeze-*.md", "docs/held-out-laws-proposal*.md"],
    "hamutay": ["*PRE_REGISTRATION.md", "docs/*preregistration*.md", "experiments/*preregistration*.md"],
}

# Freeze is not the first-add commit for these files. Each entry cites where the record says so.
FREEZE_OVERRIDE = {
    # quantumos: 4706425 is the draft; ca26217 "approve" is the freeze (scout, 2026-10-07).
    ("quantumos", "docs/superpowers/specs/2026-07-13-hedged-placement-stage1-prereg.md"): "ca26217",
    # yupi: added 7dd65e1, enacted 8cd73ed (stamp commit 7564482).
    ("yupi", "docs/held-out-laws-proposal-v0.1.md"): "8cd73ed",
}

# hamutay: claims count as bets only from 8c144c0 (custodian's consent reply).
HAMUTAY_CUTOFF = "8c144c0"


def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=True).stdout


@dataclass
class Commit:
    sha: str
    date: str
    signed: str
    parents: str
    subject: str


@dataclass
class Candidate:
    id: str
    project: str
    path: str
    freeze_sha: str | None
    freeze_date: str | None
    freeze_rule: str
    stamped: bool
    stamp_note: str
    edited_after_freeze: list[str] = field(default_factory=list)
    flags: list[str] = field(default_factory=list)


def qualify(project: str, local_id: str) -> str:
    return f"{project}:{local_id}"


def assert_qualified(ids) -> None:
    bad = [i for i in ids if ":" not in i]
    if bad:
        raise ValueError(f"unqualified ids (ledgers share local numbering): {bad[:5]}")


def matches(path: str, patterns) -> bool:
    """A pattern with a slash matches the path; one without matches the file name only."""
    return any(fnmatch.fnmatch(path if "/" in p else Path(path).name, p) for p in patterns)


def list_candidates(project: str, root: Path) -> list[str]:
    excl = EXCLUDE["*"] + EXCLUDE.get(project, [])
    out = []
    for p in git(root, "ls-files").splitlines():
        if matches(p, INCLUDE[project]) and not any(fnmatch.fnmatch(p, e) for e in excl):
            out.append(p)
    return sorted(out)


def commits_for(root: Path, path: str, signed: bool = False) -> list[Commit]:
    """Oldest first. No --follow: copy detection reports wrong add commits (hamutay scout)."""
    fmt = "%H%x1f%aI%x1f" + ("%G?" if signed else "-") + "%x1f%P%x1f%s"
    rows = git(root, "log", "--reverse", f"--format={fmt}", "--", path).splitlines()
    return [Commit(*r.split("\x1f", 4)) for r in rows if r]


def stamp_index(root: Path) -> set[str]:
    return set(git(root, "ls-tree", "-r", "--name-only", "HEAD", "timestamps").splitlines())


def is_stamped(stamps: set[str], sha: str) -> bool:
    return f"timestamps/{sha}.ots" in stamps or f"timestamps/anchored/{sha}.ots" in stamps


def resolve(root: Path, ref: str) -> str:
    return git(root, "rev-parse", ref).strip()


def is_ancestor(root: Path, a: str, b: str) -> bool:
    return subprocess.run(["git", "-C", str(root), "merge-base", "--is-ancestor", a, b]).returncode == 0


def extract(project: str, root: Path) -> list[Candidate]:
    stamps = stamp_index(root)
    tracked = set(git(root, "ls-files").splitlines())   # pre-hook per-file proofs sit beside the file as <path>.ots
    cutoff = resolve(root, HAMUTAY_CUTOFF) if project == "hamutay" else None
    out = []
    for path in list_candidates(project, root):
        cs = commits_for(root, path, signed=(project == "tessera"))
        if not cs:
            continue
        flags, rule, freeze = [], "first_add", cs[0]
        if (project, path) in FREEZE_OVERRIDE:
            want = resolve(root, FREEZE_OVERRIDE[(project, path)])
            hit = [c for c in cs if c.sha == want]
            freeze, rule = (hit[0], "override") if hit else (freeze, "override_missing")
        elif project == "tessera":
            signed = [c for c in cs if c.signed in ("G", "U", "X", "Y", "E")]
            freeze, rule = (signed[0], "first_signed") if signed else (cs[0], "no_signed_commit")
        if cutoff and not is_ancestor(root, cutoff, freeze.sha):
            flags.append("before_cutoff_claim_not_bet")
        stamped = is_stamped(stamps, freeze.sha)
        note = "stamped" if stamped else (
            "unstamped_hook_gap" if freeze.subject.startswith("ots:") else
            "unstamped_merge" if len(freeze.parents.split()) > 1 else
            "file_stamp_only" if f"{path}.ots" in tracked else "unstamped")
        later = [c.sha[:7] for c in cs[cs.index(freeze) + 1:]]   # git order, not date strings (mixed timezones)
        if later:
            flags.append("edited_after_freeze")
        out.append(Candidate(qualify(project, path), project, path, freeze.sha, freeze.date, rule,
                             stamped, note, later, flags))
    return out


def check_order(root: Path, bet: Candidate, outcome_path: str) -> str:
    """Mechanical ordering for a coder-supplied outcome file. Never reads the outcome's content."""
    cs = commits_for(root, outcome_path)
    if not cs or bet.freeze_sha is None:
        return "no_outcome_commit"
    first = cs[0].sha
    if outcome_path == bet.path:
        return "outcome_in_bet_file"           # e.g. results appended below the frozen text: coder checks the diff
    if first == bet.freeze_sha:
        return "same_commit"
    if is_ancestor(root, bet.freeze_sha, first):
        return "outcome_after_freeze"
    return "outcome_before_freeze"


def load_ledger_ids(project: str, ledger: Path) -> list[str]:
    ids = [json.loads(line)["id"] for line in ledger.read_text().splitlines() if line.strip()]
    return [qualify(project, i) for i in ids]


def main(argv: list[str]) -> None:
    projects = argv or list(INCLUDE)
    for project in projects:
        for c in extract(project, PROJECTS_ROOT / project):
            print(json.dumps(asdict(c)))


if __name__ == "__main__":
    main(sys.argv[1:])
