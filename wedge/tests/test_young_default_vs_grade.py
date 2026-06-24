import numpy as np
import pandas as pd

from wedge.young_default_vs_grade import (
    default_proxy, within_grade_default_gap, net_of_grade_young_default,
)


def _synth(n=40000, young_above_grade_pp=0.0, seed=0):
    """Synthetic: grade drives a base default rate; optionally the young default an extra
    `young_above_grade_pp` WITHIN grade (the under-grading signal to recover)."""
    rng = np.random.default_rng(seed)
    age = rng.uniform(18, 95, n)
    band = np.where(age < 25, 0, np.where(age < 45, 3, 5))
    grade = rng.choice(["A", "B", "C", "D"], n)
    base = {"A": 0.05, "B": 0.11, "C": 0.18, "D": 0.25}
    p = np.array([base[g] for g in grade]) + (band == 0) * (young_above_grade_pp / 100.0)
    loss = (rng.random(n) < np.clip(p, 0, 1)).astype(float)  # loss=1 if "defaulted"
    return pd.DataFrame(dict(age=age, age_band=band, grade=grade, loss=loss))


def test_default_proxy():
    df = pd.DataFrame(dict(loss=[0.0, 0.005, 0.5, 1.0]))
    assert list(default_proxy(df)) == [0, 0, 1, 1]


def test_no_under_grading_recovers_zero():
    """When the young default AT their grade, net-of-grade young coef ~0 (honest / L3)."""
    df = _synth(young_above_grade_pp=0.0, seed=1)
    r = net_of_grade_young_default(df)
    assert abs(r["young_above_grade_pp"]) < 1.0, f"spurious under-grading: {r['young_above_grade_pp']:.2f}pp"


def test_planted_under_grading_recovered():
    """Plant +3pp young-above-grade default; the estimator must recover it (anti-confabulation)."""
    df = _synth(young_above_grade_pp=3.0, seed=2)
    r = net_of_grade_young_default(df)
    assert 1.5 < r["young_above_grade_pp"] < 4.5, f"not recovered: {r['young_above_grade_pp']:.2f}pp"
    assert r["excludes_zero"] is True


def test_within_grade_gap_structure():
    """within_grade_default_gap returns per-grade young-vs-old gaps; planted young excess shows up."""
    df = _synth(young_above_grade_pp=3.0, seed=3)
    gaps = within_grade_default_gap(df)
    assert set(gaps) <= {"A", "B", "C", "D"}
    # average gap should be positive with a +3pp plant
    avg = np.mean([v["gap_pp"] for v in gaps.values()])
    assert avg > 1.0, f"planted gap not visible: avg {avg:.2f}pp"
