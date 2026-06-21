import numpy as np
import pandas as pd
import pytest

from wedge.age_residual import (
    assign_age_band,
    band_label,
    AGE_BANDS,
    REFERENCE_BAND_INDEX,
)


def test_assign_age_band_boundaries():
    assert assign_age_band(18) == 0
    assert assign_age_band(24.9) == 0
    assert assign_age_band(25) == 1
    assert assign_age_band(47) == 5          # [45,50) is the 6th band, index 5
    assert assign_age_band(70) == 9          # [70,95]
    assert assign_age_band(95) == 9          # right edge inclusive on last band
    assert assign_age_band(17) == -1
    assert assign_age_band(96) == -1


def test_reference_band_is_45_50():
    lo, hi = AGE_BANDS[REFERENCE_BAND_INDEX]
    assert (lo, hi) == (45, 50)
    assert band_label(REFERENCE_BAND_INDEX) == "[45,50)"
