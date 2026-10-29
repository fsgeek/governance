"""Constructed cases for the pilot sampler, run before the draw."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pilot_sample as S


def cand(flags=()):
    return {"project": "p", "flags": list(flags)}


def test_exclusions_in_order():
    assert S.exclusion(cand(["before_cutoff_claim_not_bet"]), "x") == "before_cutoff"
    assert S.exclusion(cand(), "the door:elder said") == "names_resident"
    assert S.exclusion(cand(), "Sut'i wrote") == "names_resident"
    assert S.exclusion(cand(), "a" * (S.MAX_CHARS + 1)) == "exceeds_context"
    assert S.exclusion(cand(), "P(pass) = 0.7") is None


def test_resident_match_is_word_bounded():
    assert S.exclusion(cand(), "Lunar orbit, markers, elderly") is None


def test_allocation_min_one_and_total():
    a = S.allocate({"big": 156, "mid": 39, "small": 6, "tiny": 1}, 0.10)
    assert all(v >= 1 for v in a.values())
    assert a["tiny"] == 1
    assert sum(a.values()) == round(0.10 * 202)
    assert a["big"] > a["mid"] > a["small"] - 1


def test_allocation_never_exceeds_population():
    a = S.allocate({"x": 1, "y": 2}, 0.9)
    assert a["x"] <= 1 and a["y"] <= 2


def test_draw_is_deterministic_and_order_independent():
    e1 = {"a": ["a:3", "a:1", "a:2"], "b": ["b:1", "b:2"]}
    e2 = {"b": ["b:2", "b:1"], "a": ["a:2", "a:3", "a:1"]}
    al = {"a": 2, "b": 1}
    assert S.draw(e1, al, 7) == S.draw(e2, al, 7)
