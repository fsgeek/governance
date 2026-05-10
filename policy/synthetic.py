"""Synthetic data generator for policy-constrained Rashomon experiments.

The generator produces loan-application records with features matching a
policy graph (e.g., policy/thin_demo_hmda.yaml) and binary default outcomes
under a known generative process. Because the data-generating mechanism
is known, this substrate enables:

1. **Methodology validation.** Verify that the constraint encoder produces
   R(ε) members that respect the monotonicity / mandatory / prohibited
   constraints from the policy graph.

2. **Controlled SHAP/LIME comparison.** Score post-hoc explainers against
   the true generative mechanism. SHAP/LIME on synthetic data have a
   ground-truth reference that real-data studies lack.

3. **Heterogeneity injection.** Optionally include a subpopulation
   following a shifted mechanism. The methodology's central claim — that
   within-Rashomon disagreement routes hard cases — is testable here
   because we know which cases come from the shifted mechanism.

4. **Pre-registration on known-truth.** Predictions made before generation
   can be tested cleanly against the realized data, with the additional
   property that the *generative parameters themselves* are committed.

Status: thin baseline implementation. The feature distributions are
plausible but illustrative; mechanism coefficients are reasonable starting
values but not calibrated against any real dataset. Treat as a substrate
for mechanism experiments, not as a model of any specific lender's book.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

import numpy as np
import pandas as pd

# -----------------------------------------------------------------------------
# Mechanism specification.
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class Mechanism:
    """Logistic default-propensity mechanism.

    Linear predictor:
        eta = beta_0
              - beta_fico   * (fico - 700) / 100      # higher FICO -> lower default
              + beta_dti    * (dti - 30)   / 10       # higher DTI  -> higher default
              + beta_ltv    * (ltv - 80)   / 10       # higher LTV  -> higher default
              - beta_income * log(income / 65000)     # higher income -> lower default
              - beta_emp    * (emp_length - 5) / 5    # longer tenure -> lower default

    Probability of default = sigmoid(eta).

    Coefficients are non-negative by convention so the sign in the linear
    predictor encodes the monotonicity direction matching the thin demo
    policy graph. The constraint encoder validates this alignment.
    """

    beta_0: float = -1.8
    beta_fico: float = 1.5
    beta_dti: float = 0.8
    beta_ltv: float = 0.5
    beta_income: float = 0.6
    beta_emp: float = 0.3

    def linear_predictor(self, df: pd.DataFrame) -> np.ndarray:
        return (
            self.beta_0
            - self.beta_fico * (df["fico_range_low"].to_numpy() - 700) / 100
            + self.beta_dti * (df["dti"].to_numpy() - 30) / 10
            + self.beta_ltv * (df["ltv"].to_numpy() - 80) / 10
            - self.beta_income * np.log(df["annual_inc"].to_numpy() / 65000)
            - self.beta_emp * (df["emp_length"].to_numpy() - 5) / 5
        )

    def default_probability(self, df: pd.DataFrame) -> np.ndarray:
        return 1.0 / (1.0 + np.exp(-self.linear_predictor(df)))


# Standard mechanism: balanced reliance on all features.
STANDARD = Mechanism()

# Shifted mechanism: DTI matters less, LTV matters more — a heterogeneous
# subpopulation behaves as if collateral risk dominates over leverage risk.
# Used when heterogeneity injection is enabled.
SHIFTED = Mechanism(
    beta_0=-2.0,
    beta_fico=1.5,
    beta_dti=0.2,
    beta_ltv=1.5,
    beta_income=0.6,
    beta_emp=0.3,
)


# -----------------------------------------------------------------------------
# Feature sampling.
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class GenerationConfig:
    n_cases: int = 10_000
    heterogeneity_fraction: float = 0.0  # 0.0 = homogeneous; 0.1 = 10% shifted
    seed: int = 0
    label_noise: float = 0.0  # symmetric label-flip rate after sampling
    correlate_fico_income: bool = True


def _sample_features(n: int, rng: np.random.Generator, *, correlate: bool) -> pd.DataFrame:
    """Sample feature values from plausible distributions."""
    # FICO: mixture (subprime tail at 580-660, prime mass at 660-780, super-prime
    # tail at 780-820). Mixture weights sum to 1.
    component = rng.choice([0, 1, 2], size=n, p=[0.15, 0.65, 0.20])
    fico = np.where(
        component == 0,
        rng.normal(620, 15, size=n).clip(580, 660),
        np.where(
            component == 1,
            rng.normal(720, 20, size=n).clip(660, 780),
            rng.normal(795, 10, size=n).clip(780, 820),
        ),
    )
    fico = np.round(fico).astype(int)

    # DTI: Beta-distributed in [10, 50]
    dti_raw = rng.beta(2.5, 4.0, size=n)
    dti = 10 + 40 * dti_raw

    # Annual income: log-normal, median ~65k, optionally correlated with FICO
    log_inc = rng.normal(np.log(65_000), 0.6, size=n)
    if correlate:
        # Higher FICO mildly raises expected income.
        log_inc = log_inc + 0.0008 * (fico - 700)
    annual_inc = np.exp(log_inc).clip(15_000, 500_000)

    # Employment length: integer 0-10, weighted toward longer tenure
    emp_length = rng.choice(
        np.arange(11),
        size=n,
        p=np.array([4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 6]) / 100.0,
    )

    # LTV: bimodal — purchase cluster near 80, refi spread 60-95
    is_purchase = rng.random(n) < 0.6
    ltv_purchase = rng.normal(80, 6, size=n).clip(60, 97)
    ltv_refi = rng.normal(75, 12, size=n).clip(45, 95)
    ltv = np.where(is_purchase, ltv_purchase, ltv_refi)

    return pd.DataFrame(
        {
            "fico_range_low": fico,
            "dti": dti,
            "annual_inc": annual_inc,
            "emp_length": emp_length,
            "ltv": ltv,
        }
    )


# -----------------------------------------------------------------------------
# Generation entry point.
# -----------------------------------------------------------------------------


def generate(
    config: GenerationConfig | None = None,
) -> tuple[pd.DataFrame, dict]:
    """Generate a synthetic loan-application dataset.

    Returns
    -------
    df : DataFrame
        Columns: fico_range_low, dti, annual_inc, emp_length, ltv,
        mechanism (str: 'standard' or 'shifted'), default_probability,
        label (int: 0=paid, 1=charged_off).
    metadata : dict
        Generative parameters and counts. Should be persisted alongside the
        data so reproducibility is preserved across sessions.
    """
    cfg = config or GenerationConfig()
    rng = np.random.default_rng(cfg.seed)

    df = _sample_features(cfg.n_cases, rng, correlate=cfg.correlate_fico_income)

    # Mechanism assignment.
    is_shifted = rng.random(cfg.n_cases) < cfg.heterogeneity_fraction
    df["mechanism"] = np.where(is_shifted, "shifted", "standard")

    p_default = np.where(
        is_shifted,
        SHIFTED.default_probability(df),
        STANDARD.default_probability(df),
    )
    df["default_probability"] = p_default

    # Sample binary outcome.
    label = (rng.random(cfg.n_cases) < p_default).astype(int)
    if cfg.label_noise > 0:
        flip = rng.random(cfg.n_cases) < cfg.label_noise
        label = np.where(flip, 1 - label, label)
    df["label"] = label

    metadata = {
        "config": {
            "n_cases": cfg.n_cases,
            "heterogeneity_fraction": cfg.heterogeneity_fraction,
            "seed": cfg.seed,
            "label_noise": cfg.label_noise,
            "correlate_fico_income": cfg.correlate_fico_income,
        },
        "mechanisms": {
            "standard": STANDARD.__dict__,
            "shifted": SHIFTED.__dict__,
        },
        "summary": {
            "n_total": int(cfg.n_cases),
            "n_shifted": int(is_shifted.sum()),
            "n_default": int(label.sum()),
            "default_rate": float(label.mean()),
        },
    }

    return df, metadata


if __name__ == "__main__":
    # Demonstration: generate small homogeneous and heterogeneous samples and
    # print summary statistics.
    for hf in (0.0, 0.10):
        df, meta = generate(GenerationConfig(n_cases=5_000, heterogeneity_fraction=hf, seed=42))
        print(f"=== heterogeneity_fraction={hf} ===")
        print(f"  n={meta['summary']['n_total']}, "
              f"n_shifted={meta['summary']['n_shifted']}, "
              f"default_rate={meta['summary']['default_rate']:.3f}")
        print(f"  fico mean={df['fico_range_low'].mean():.1f} "
              f"dti mean={df['dti'].mean():.1f} "
              f"income median={df['annual_inc'].median():.0f}")
        if hf > 0:
            std_rate = df.loc[df['mechanism'] == 'standard', 'label'].mean()
            shf_rate = df.loc[df['mechanism'] == 'shifted', 'label'].mean()
            print(f"  default rate by mechanism: standard={std_rate:.3f} shifted={shf_rate:.3f}")
        print()
