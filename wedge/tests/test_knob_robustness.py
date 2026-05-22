"""Tests for the Arm-1 codification-knob robustness recompute logic.

Pre-reg: docs/superpowers/specs/2026-05-22-codification-knob-robustness-preregistration-note.md

The logic under test mirrors the verdict definitions frozen in the original cycles:
    adequacy(r2, thr)        = r2 >= thr
    verdict_differs(a,b,thr) = (adequacy(a) != adequacy(b))   [both non-None]
    manufactured_silence     = is_reorg AND verdict_differs
(see scripts/silence_manufacture_test.py:125-130 and
 scripts/hmda_trimodal_replication.py:606-614)
"""

import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "knob_robustness_arm1",
    Path(__file__).resolve().parents[2] / "scripts" / "knob_robustness_arm1.py",
)
kr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(kr)


def test_adequacy_threshold_boundary_is_inclusive():
    # original scripts use `r2_named >= threshold`
    assert kr.adequacy(0.30, 0.30) is True
    assert kr.adequacy(0.2999, 0.30) is False
    assert kr.adequacy(None, 0.30) is None


def test_verdict_differs_true_only_when_threshold_splits_the_pair():
    # A=0.20, B=0.40: differs iff 0.20 < thr <= 0.40
    assert kr.verdict_differs(0.20, 0.40, 0.30) is True   # B adequate, A not
    assert kr.verdict_differs(0.20, 0.40, 0.15) is False  # both adequate
    assert kr.verdict_differs(0.20, 0.40, 0.45) is False  # both inadequate
    assert kr.verdict_differs(0.20, 0.40, 0.40) is True   # thr == max -> B still adequate, A not
    assert kr.verdict_differs(0.20, 0.40, 0.20) is False  # thr == min -> both adequate (>=)


def test_verdict_differs_false_when_either_r2_missing():
    assert kr.verdict_differs(None, 0.40, 0.30) is False
    assert kr.verdict_differs(0.40, None, 0.30) is False


def test_manufactured_silence_requires_reorg_and_divergence():
    # straddling pair, reorganized -> silence
    assert kr.manufactured_silence(0.20, 0.40, True, 0.30) is True
    # straddling pair, NOT reorganized -> no silence
    assert kr.manufactured_silence(0.20, 0.40, False, 0.30) is False
    # reorganized but not straddling -> no silence
    assert kr.manufactured_silence(0.20, 0.40, True, 0.10) is False


def test_silence_active_interval_is_the_open_min_closed_max_band():
    lo, hi = kr.silence_active_interval(0.20, 0.40)
    assert lo == 0.20 and hi == 0.40  # silence active for thr in (0.20, 0.40]


def test_cell_silence_is_robust_when_threshold_band_brackets_whole_sweep():
    # wide gap [0.05, 0.78], 0.30 sits inside, sweep all inside (lo,hi] -> constant True
    sweep = [0.20, 0.25, 0.28, 0.30, 0.32, 0.35, 0.40]
    labels = [kr.manufactured_silence(0.05, 0.78, True, t) for t in sweep]
    assert all(labels)  # never flips
    assert kr.flips(labels) == 0


def test_cell_silence_flips_when_a_sweep_point_crosses_an_r2():
    # pair straddles only part of the sweep: A=0.27, B=0.62
    # silence True where 0.27 < thr <= 0.62  -> thr in {0.28,0.30,0.32,0.35,0.40}; False at {0.20,0.25}
    sweep = [0.20, 0.25, 0.28, 0.30, 0.32, 0.35, 0.40]
    labels = [kr.manufactured_silence(0.27, 0.62, True, t) for t in sweep]
    assert labels == [False, False, True, True, True, True, True]
    assert kr.flips(labels) == 1  # one transition across the sweep


def test_flip_fraction_counts_cells_that_change_label_across_sweep():
    sweep = [0.20, 0.30, 0.40]
    cells = [
        # robust silence (wide gap brackets sweep)
        {"r2a": 0.05, "r2b": 0.90, "reorg": True},
        # fragile (flips)
        {"r2a": 0.27, "r2b": 0.35, "reorg": True},
        # never silent (not reorganized) -> constant False, not a flip
        {"r2a": 0.27, "r2b": 0.35, "reorg": False},
    ]
    frac = kr.flip_fraction(cells, sweep)
    assert abs(frac - (1 / 3)) < 1e-9
