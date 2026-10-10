"""Every check is tested on a constructed case before it touches real data (closing note, process lessons)."""
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import extract as X


def sh(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True).stdout.strip()


def commit(repo, msg, files):
    for name, text in files.items():
        p = repo / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
        sh(repo, "add", name)
    sh(repo, "commit", "-q", "-m", msg)
    return sh(repo, "rev-parse", "HEAD")


def stamp(repo, sha, anchored=False):
    d = "timestamps/anchored" if anchored else "timestamps"
    return commit(repo, f"ots: stamp {sha}", {f"{d}/{sha}": sha, f"{d}/{sha}.ots": "proof"})


@pytest.fixture
def repo(tmp_path, monkeypatch):
    r = tmp_path / "proj"
    r.mkdir()
    sh(r, "init", "-q")
    sh(r, "config", "user.email", "t@example.com")
    sh(r, "config", "user.name", "t")
    sh(r, "config", "commit.gpgsign", "false")
    monkeypatch.setitem(X.INCLUDE, "proj", ["prereg/*.md"])
    return r


def only(repo):
    [c] = X.extract("proj", repo)
    return c


def test_stamped_freeze_found_in_both_locations(repo):
    a = commit(repo, "prereg A", {"prereg/a.md": "bet"})
    stamp(repo, a, anchored=True)
    c = only(repo)
    assert c.freeze_sha == a and c.stamped and c.stamp_note == "stamped" and c.id == "proj:prereg/a.md"


def test_unstamped_is_unstamped(repo):
    commit(repo, "prereg A", {"prereg/a.md": "bet"})
    assert only(repo).stamp_note == "unstamped"


def test_file_added_inside_ots_commit_is_hook_gap_not_avoidance(repo):
    commit(repo, "ots: upgrade 3 timestamp(s)", {"prereg/a.md": "bet"})
    c = only(repo)
    assert not c.stamped and c.stamp_note == "unstamped_hook_gap"


def test_bet_first_landing_in_a_merge_is_unstamped_merge(repo):
    commit(repo, "base", {"README": "x"})
    sh(repo, "checkout", "-q", "-b", "side")
    commit(repo, "side", {"other.txt": "y"})
    sh(repo, "checkout", "-q", "-")
    commit(repo, "main", {"main.txt": "z"})
    sh(repo, "merge", "-q", "--no-ff", "--no-commit", "side")
    (repo / "prereg").mkdir()
    (repo / "prereg" / "a.md").write_text("bet")
    sh(repo, "add", "prereg/a.md")
    sh(repo, "commit", "-q", "-m", "merge side, with a bet")
    assert only(repo).stamp_note == "unstamped_merge"


def test_edit_after_freeze_flagged(repo):
    a = commit(repo, "prereg A", {"prereg/a.md": "bet"})
    stamp(repo, a)
    b = commit(repo, "clarify A", {"prereg/a.md": "bet, clarified"})
    c = only(repo)
    assert c.freeze_sha == a and "edited_after_freeze" in c.flags and c.edited_after_freeze == [b[:7]]


def test_same_commit_outcome_is_caught(repo):
    commit(repo, "prereg and result", {"prereg/a.md": "bet", "results/a.md": "outcome"})
    assert X.check_order(repo, only(repo), "results/a.md") == "same_commit"


def test_outcome_before_freeze_is_caught(repo):
    commit(repo, "result first", {"results/a.md": "outcome"})
    commit(repo, "prereg after", {"prereg/a.md": "bet"})
    assert X.check_order(repo, only(repo), "results/a.md") == "outcome_before_freeze"


def test_outcome_after_freeze_passes(repo):
    commit(repo, "prereg", {"prereg/a.md": "bet"})
    commit(repo, "result", {"results/a.md": "outcome"})
    assert X.check_order(repo, only(repo), "results/a.md") == "outcome_after_freeze"


def test_results_appended_to_bet_file_go_to_a_coder(repo):
    commit(repo, "prereg", {"prereg/a.md": "bet"})
    commit(repo, "append results", {"prereg/a.md": "bet\n## Results"})
    assert X.check_order(repo, only(repo), "prereg/a.md") == "outcome_in_bet_file"


def test_override_moves_freeze_to_enacting_commit(repo, monkeypatch):
    commit(repo, "draft", {"prereg/a.md": "draft"})
    e = commit(repo, "approve", {"prereg/a.md": "frozen"})
    monkeypatch.setitem(X.FREEZE_OVERRIDE, ("proj", "prereg/a.md"), e)
    c = only(repo)
    assert c.freeze_sha == e and c.freeze_rule == "override" and "edited_after_freeze" not in c.flags


def test_excluded_paths_never_listed(repo, monkeypatch):
    monkeypatch.setitem(X.INCLUDE, "proj", ["*.md"])
    monkeypatch.setitem(X.EXCLUDE, "proj", ["community/*"])
    commit(repo, "home", {"community/elder/words.md": "a resident's words", "prereg/a.md": "bet"})
    assert X.list_candidates("proj", repo) == ["prereg/a.md"]


def test_results_file_with_bet_suffix_is_not_a_bet(repo, monkeypatch):
    monkeypatch.setitem(X.INCLUDE, "proj", ["formal/*/PROBE.md"])
    commit(repo, "probe", {"formal/p9/PROBE.md": "bet", "formal/p9/RESULTS-PROBE.md": "outcome"})
    assert X.list_candidates("proj", repo) == ["formal/p9/PROBE.md"]


def test_slashless_pattern_matches_name_only(repo, monkeypatch):
    monkeypatch.setitem(X.INCLUDE, "proj", ["*prereg*.md"])
    commit(repo, "x", {"prereg-notes/summary.md": "not a bet", "docs/a-prereg.md": "bet"})
    assert X.list_candidates("proj", repo) == ["docs/a-prereg.md"]


def test_per_file_ots_is_reported_not_called_unstamped(repo):
    commit(repo, "prereg", {"prereg/a.md": "bet", "prereg/a.md.ots": "proof"})
    assert only(repo).stamp_note == "file_stamp_only"


def test_unqualified_ids_are_refused():
    with pytest.raises(ValueError):
        X.assert_qualified(["governance:obs-0001", "obs-0001"])


GOV = X.PROJECTS_ROOT / "governance/ledger/observations.jsonl"
LEV = X.PROJECTS_ROOT / "levadura_salvaje/ledger/observations.jsonl"


@pytest.mark.skipif(not (GOV.exists() and LEV.exists()), reason="sibling ledgers not present")
def test_real_obs_0001_collision_is_disambiguated():
    raw_g = {i.split(":", 1)[1] for i in X.load_ledger_ids("governance", GOV)}
    raw_l = {i.split(":", 1)[1] for i in X.load_ledger_ids("levadura_salvaje", LEV)}
    assert "obs-0001" in raw_g & raw_l                       # the real collision exists
    ids = X.load_ledger_ids("governance", GOV) + X.load_ledger_ids("levadura_salvaje", LEV)
    X.assert_qualified(ids)
    assert len(ids) == len(set(ids))                         # and qualification removes it
