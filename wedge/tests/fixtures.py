"""Hand-constructed small datasets for unit tests.

We keep fixtures small and deterministic so that test assertions can be
checked against known tree structure rather than against statistical
properties.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


FEATURE_COLS = ["fico_proxy", "dti_proxy", "income_proxy", "history_depth"]


def tiny_separable_dataset(seed: int = 0) -> pd.DataFrame:
    """100-row dataset where label is determined by a simple rule.

    Rule (grant-as-positive convention; spec §2.7 OD-9a / OD-13):
        label = 1 (grant) iff fico_proxy >= 650 AND dti_proxy <= 30.
    Equivalently: label = 0 (deny) iff fico_proxy < 650 OR dti_proxy > 30.
    A CART with depth >= 2 should reconstruct this rule exactly.
    """
    rng = np.random.default_rng(seed)
    n = 100
    df = pd.DataFrame({
        "fico_proxy": rng.integers(580, 800, size=n),
        "dti_proxy": rng.integers(5, 50, size=n),
        "income_proxy": rng.integers(20000, 200000, size=n),
        "history_depth": rng.integers(1, 30, size=n),
    })
    df["label"] = ((df["fico_proxy"] >= 650) & (df["dti_proxy"] <= 30)).astype(int)
    return df


def tiny_noisy_dataset(seed: int = 0) -> pd.DataFrame:
    """Like tiny_separable_dataset but with 10% label noise."""
    df = tiny_separable_dataset(seed=seed)
    rng = np.random.default_rng(seed + 1)
    flip_mask = rng.random(len(df)) < 0.10
    df.loc[flip_mask, "label"] = 1 - df.loc[flip_mask, "label"]
    return df
