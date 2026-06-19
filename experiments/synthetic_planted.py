"""Planted-clean-member DGP for the Stage-1 positive control (pre-reg §5).

Label y depends on two legitimate features (legit_a, legit_b). A protected
attribute is correlated with a third proxy feature (protected_proxy) that is
PROHIBITED by policy. A model that uses only legitimate features and excludes
the proxy achieves |approval-rate gap| <= tau BY CONSTRUCTION — that is the
planted clean member the harness must recover. If the harness cannot, it is
broken (gate fails) and Stage 2 must not run.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from policy.encoder import PolicyConstraints


def make_planted_dataset(n: int = 4000, random_state: int = 0):
    rng = np.random.default_rng(random_state)
    legit_a = rng.normal(size=n)
    legit_b = rng.normal(size=n)
    # legitimate score drives the label
    score = 1.2 * legit_a + 0.8 * legit_b
    y = (score > np.median(score)).astype(int)
    # protected attribute correlated with a PROXY but NOT with the label given legit feats
    protected = rng.random(n) < 0.4
    protected_proxy = protected.astype(float) + rng.normal(scale=0.5, size=n)
    X = pd.DataFrame({
        "legit_a": legit_a, "legit_b": legit_b, "protected_proxy": protected_proxy,
    })
    monotonic_cst = {"legit_a": 1, "legit_b": 1, "protected_proxy": 0}
    policy = PolicyConstraints(
        name="planted-control",
        version="1",
        status="frozen",
        monotonicity_map={},
        mandatory_features=("legit_a",),
        prohibited_features=("protected_proxy",),
    )
    return X, pd.Series(y), pd.Series(protected), monotonic_cst, policy
