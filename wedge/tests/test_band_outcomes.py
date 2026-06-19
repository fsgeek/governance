# wedge/tests/test_band_outcomes.py
import numpy as np
import pandas as pd
from wedge.band_outcomes import approval_rate_gap, band_outcomes

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
