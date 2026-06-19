# wedge/tests/test_band_outcomes.py
import numpy as np
import pandas as pd
import pytest
from wedge.band_outcomes import approval_rate_gap, band_outcomes, margin_aware_gap

class _StubModel:
    # approves everyone in `approve_idx`, denies others — deterministic.
    def __init__(self, approve_mask):
        self._m = np.asarray(approve_mask, dtype=int)
        self.classes_ = (0, 1)
    def predict(self, X):
        return self._m
    def predict_proba(self, X):
        p1 = self._m.astype(float)
        return np.column_stack([1 - p1, p1])

def test_approval_rate_gap_signed():
    X = pd.DataFrame({"f": range(4)})
    protected = pd.Series([True, True, False, False])
    # approve both protected, neither unprotected -> gap = 1.0 - 0.0 = 1.0
    m = _StubModel([1, 1, 0, 0])
    assert approval_rate_gap(m, X, protected) == 1.0

def test_band_outcomes_C_A_B():
    X = pd.DataFrame({"f": range(4)})
    protected = pd.Series([True, True, False, False])
    clean = _StubModel([1, 0, 1, 0])    # gap 0.5-0.5 = 0.0  -> clean
    biased = _StubModel([1, 1, 0, 0])   # gap 1.0          -> not clean
    out = band_outcomes([clean, biased], X, protected, tau=0.02)
    assert out["C"] == 2
    assert out["A_plain"] == 1.0        # max(1.0) - min(0.0)
    assert out["B_plain"] is True       # clean member exists (min |gap| = 0 ≤ tau)


class _GradedStubModel:
    """Stub model returning caller-specified per-row approve-probabilities.

    Needed to test margin_aware_gap: _StubModel returns hard 0/1 so no row
    ever lands inside the ±0.10 band, making margin assertions vacuous.
    """
    classes_ = (0, 1)

    def __init__(self, probs):
        self._p = np.asarray(probs, dtype=float)

    def predict_proba(self, X):
        return np.column_stack([1.0 - self._p, self._p])

    def predict(self, X):
        return (self._p >= 0.5).astype(int)


def test_margin_aware_gap_graded_probs():
    """margin_aware_gap with known in-band/out-of-band rows.

    Fixture (6 rows, threshold=0.5, band=0.10):

      idx  protected  p      |p-0.5|  near?  pred
       0   True       0.55   0.05     yes     1
       1   True       0.45   0.05     yes     0
       2   True       0.05   0.45     no      excluded
       3   False      0.55   0.05     yes     1
       4   False      0.55   0.05     yes     1
       5   False      0.95   0.45     no      excluded

    In-band protected  (rows 0,1): mean(pred) = (1+0)/2 = 0.5
    In-band unprotected (rows 3,4): mean(pred) = (1+1)/2 = 1.0
    Expected gap = 0.5 - 1.0 = -0.5
    """
    X = pd.DataFrame({"f": range(6)})
    protected = pd.Series([True, True, True, False, False, False])
    probs = [0.55, 0.45, 0.05, 0.55, 0.55, 0.95]
    model = _GradedStubModel(probs)

    gap = margin_aware_gap(model, X, protected)
    assert gap == pytest.approx(-0.5), (
        f"Expected -0.5 but got {gap}; "
        "check that rows outside the band are excluded and in-band rates computed correctly"
    )


def test_margin_aware_gap_boundary_inclusive():
    """A row exactly `band` away (|p - threshold| == band) must be INCLUDED.

    Single row: p=0.40, threshold=0.5, band=0.10 → |0.40-0.5|=0.10 → near=True.
    We need at least one protected AND one unprotected near-row to avoid NaN,
    so we use two rows: one protected (p=0.40, approve=0), one unprotected (p=0.60, approve=1).
    Expected gap = 0.0 - 1.0 = -1.0  (the exact boundary row is included).
    """
    X = pd.DataFrame({"f": [0, 1]})
    protected = pd.Series([True, False])
    model = _GradedStubModel([0.40, 0.60])

    gap = margin_aware_gap(model, X, protected)
    assert gap == pytest.approx(-1.0), (
        f"Expected -1.0 but got {gap}; "
        "boundary p=0.40 (|0.40-0.5|=0.10) should be INCLUDED (<=, not <)"
    )
