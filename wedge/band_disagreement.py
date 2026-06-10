"""Within-band disagreement summary: the audited quantity for selection discretion.

A policy-constrained Rashomon band frequently contains many models that are
TIED on loss (the ε-band) yet DISAGREE per-borrower. "Pick one from the
explainable set" is therefore an unaudited discretionary choice
(working_notes/2026-06-09-pick-one-hides-the-choice.md). The flip-rate -- the
fraction of holdout cases on which band members disagree -- is the first-class
audit quantity that makes that discretion visible in the construction manifest.

Empirical context (working_notes/2026-06-09 .. 2026-06-10):
  - The shuffle-set (disagreeing cases) is margin-driven and protected-BLIND
    (pooled g_diff ~= 0, seed-robust); the harm is ARBITRARINESS toward
    marginal applicants, broader than disparate impact.
  - flip-rate is ε-sensitive (no knee) and sampler-sensitive in MAGNITUDE, so
    it must be read as a curve / distribution, never a single point. This module
    reports the point for ONE band; the manifest records it alongside ε so the
    (ε, flip_rate) pair is auditable, and a caller sweeping ε produces the curve.

All members of an EpsilonAdmissibleSet share the same holdout (one
train_test_split), so `holdout_y_pred` vectors are row-aligned and the flip
computation is well-defined without refitting.
"""
from __future__ import annotations

from typing import Any

import numpy as np

from wedge.rashomon import EpsilonAdmissibleSet


def band_disagreement_summary(band: EpsilonAdmissibleSet) -> dict[str, Any]:
    """Flip-rate and member count for one ε-band.

    flip_rate = fraction of holdout rows on which at least two band members
    disagree (the shuffle-set size, normalised). Returns n_members, n_holdout,
    n_flip, flip_rate. With < 2 members the band offers no choice: flip_rate 0,
    n_flip 0 (a degenerate band cannot manufacture or hide a choice).
    """
    members = band.within_epsilon
    n_members = len(members)
    if n_members < 2:
        return {
            "n_members": n_members,
            "n_holdout": _holdout_len(members),
            "n_flip": 0,
            "flip_rate": 0.0,
            "degenerate": True,
        }
    # Members must carry holdout predictions to compute disagreement. If they
    # don't (e.g. a count-only band), the audit quantity is UNAVAILABLE -- report
    # that honestly rather than fabricate a 0 or crash the manifest.
    if any(getattr(m, "holdout_y_pred", None) is None for m in members):
        return {
            "n_members": n_members,
            "n_holdout": _holdout_len(members),
            "n_flip": None,
            "flip_rate": None,
            "unavailable_reason": "members lack holdout predictions",
        }
    preds = np.vstack([np.asarray(m.holdout_y_pred) for m in members])
    flip = preds.min(axis=0) != preds.max(axis=0)
    n_holdout = preds.shape[1]
    n_flip = int(flip.sum())
    return {
        "n_members": n_members,
        "n_holdout": n_holdout,
        "n_flip": n_flip,
        "flip_rate": round(n_flip / n_holdout, 6) if n_holdout else 0.0,
        "degenerate": False,
    }


def _holdout_len(members: list) -> int:
    if not members:
        return 0
    yt = getattr(members[0], "holdout_y_true", None)
    return int(len(np.asarray(yt))) if yt is not None else 0
