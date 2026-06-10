"""Tests for the within-band disagreement audit quantity."""
from __future__ import annotations

import numpy as np

from wedge.band_disagreement import band_disagreement_summary
from wedge.rashomon import EpsilonAdmissibleSet


class _FakeMember:
    """Minimal stand-in carrying the two arrays the summary reads."""

    def __init__(self, y_pred, y_true):
        self.holdout_y_pred = np.asarray(y_pred)
        self.holdout_y_true = np.asarray(y_true)


def _band(members):
    return EpsilonAdmissibleSet(
        within_epsilon=members, out_of_epsilon=[], global_best_value=0.0,
        epsilon=0.02, score_label="L_T(w_T=1.5)",
    )


def test_flip_rate_counts_disagreeing_rows():
    yt = [1, 1, 0, 0]
    m1 = _FakeMember([1, 0, 0, 0], yt)
    m2 = _FakeMember([1, 1, 0, 1], yt)  # differs from m1 on rows 1 and 3
    out = band_disagreement_summary(_band([m1, m2]))
    assert out["n_members"] == 2
    assert out["n_holdout"] == 4
    assert out["n_flip"] == 2
    assert out["flip_rate"] == 0.5
    assert out["degenerate"] is False


def test_unanimous_band_has_zero_flip_rate():
    yt = [1, 0, 1]
    m1 = _FakeMember([1, 0, 1], yt)
    m2 = _FakeMember([1, 0, 1], yt)  # identical decisions
    out = band_disagreement_summary(_band([m1, m2]))
    assert out["n_flip"] == 0
    assert out["flip_rate"] == 0.0


def test_degenerate_band_single_member():
    out = band_disagreement_summary(_band([_FakeMember([1, 0], [1, 0])]))
    assert out["degenerate"] is True
    assert out["flip_rate"] == 0.0
    assert out["n_members"] == 1


def test_count_only_band_reports_unavailable_not_crash():
    # Members without holdout predictions (e.g. the count-only fixtures the
    # manifest tests use): the audit quantity is unavailable, not a fabricated 0.
    out = band_disagreement_summary(_band([1, 2, 3]))
    assert out["flip_rate"] is None
    assert out["n_flip"] is None
    assert out["n_members"] == 3
    assert "unavailable_reason" in out
