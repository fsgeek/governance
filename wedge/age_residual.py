"""Age-residual pricing analysis: does the young-end overcharge survive lawful-risk controls?

Pure statistics, no file I/O. The runner (scripts/age_pricing_residual.py) handles loading.
See docs/superpowers/specs/2026-06-20-age-pricing-residual-design.md for the design and the
frozen prediction ledger.
"""
from __future__ import annotations

AGE_BANDS: list[tuple[float, float]] = [
    (18, 25), (25, 30), (30, 35), (35, 40), (40, 45),
    (45, 50), (50, 55), (55, 60), (60, 70), (70, 95),
]
# [45,50) is the reference band for residuals (0-indexed -> 5).
REFERENCE_BAND_INDEX = next(i for i, b in enumerate(AGE_BANDS) if b == (45, 50))


def band_label(i: int) -> str:
    lo, hi = AGE_BANDS[i]
    return f"[{int(lo)},{int(hi)})"


def assign_age_band(age: float) -> int:
    """Return band index 0..9, or -1 if age is outside [18, 95].

    Left-closed bands; the final band [70,95] is right-inclusive so age==95 lands in it.
    """
    if age < AGE_BANDS[0][0] or age > AGE_BANDS[-1][1]:
        return -1
    for i, (lo, hi) in enumerate(AGE_BANDS):
        if lo <= age < hi or (i == len(AGE_BANDS) - 1 and age == hi):
            return i
    return -1
