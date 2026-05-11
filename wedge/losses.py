"""Cost-asymmetric loss functions for dual-set Rashomon construction.

Per spec §3.2 / §3.3:

  L_T(y, ŷ; w_T)  = w_T · |missed grants| + 1 · |missed denies|
                    "grant-emphasis": penalizes false denies (the bank-side
                    failure mode where a creditworthy applicant is rejected).
                    R_T(ε_T) is constructed as the ε-band of models minimizing
                    L_T under the policy.

  L_F(y, ŷ; w_F)  = 1 · |missed grants| + w_F · |missed denies|
                    "deny-emphasis": penalizes false grants (the bank-side
                    failure mode where a non-creditworthy applicant is
                    approved). R_F(ε_F) is the analogous ε-band.

Per spec §5 (retrospective trajectory operationalization), surprise-weighted
variants `L_T'` and `L_F'` accept per-sample weights derived from realized
outcome surprise; these drive set revision (R_T' / R_F').

Label convention (spec §2.7 OD-9a / OD-13): y=1 ⇔ grant (paid / originated);
y=0 ⇔ deny (charged_off / denied).
"""

from __future__ import annotations

import numpy as np


def _validate_binary_pair(y: np.ndarray, y_hat: np.ndarray) -> None:
    if y.shape != y_hat.shape:
        raise ValueError(
            f"y and y_hat must have matching shape; got y.shape={y.shape}, "
            f"y_hat.shape={y_hat.shape}."
        )
    for name, arr in (("y", y), ("y_hat", y_hat)):
        unique = np.unique(arr)
        if not set(int(v) for v in unique).issubset({0, 1}):
            raise ValueError(
                f"{name} must be binary {{0, 1}}; got unique values {sorted(unique.tolist())}."
            )


def _validate_sample_weights(y: np.ndarray, sample_weights: np.ndarray) -> None:
    if sample_weights.shape != y.shape:
        raise ValueError(
            f"sample_weights must match y.shape; got sample_weights.shape="
            f"{sample_weights.shape}, y.shape={y.shape}."
        )


def grant_emphasis_loss(
    y: np.ndarray, y_hat: np.ndarray, *, w_T: float = 1.5
) -> float:
    """L_T(y, ŷ) = w_T · 1[y=1, ŷ=0] + 1[y=0, ŷ=1]. Convention: y=1 ⇔ grant."""
    _validate_binary_pair(y, y_hat)
    missed_grants = int(((y == 1) & (y_hat == 0)).sum())
    missed_denies = int(((y == 0) & (y_hat == 1)).sum())
    return float(w_T * missed_grants + missed_denies)


def deny_emphasis_loss(
    y: np.ndarray, y_hat: np.ndarray, *, w_F: float = 1.5
) -> float:
    """L_F(y, ŷ) = 1[y=1, ŷ=0] + w_F · 1[y=0, ŷ=1]. Convention: y=1 ⇔ grant."""
    _validate_binary_pair(y, y_hat)
    missed_grants = int(((y == 1) & (y_hat == 0)).sum())
    missed_denies = int(((y == 0) & (y_hat == 1)).sum())
    return float(missed_grants + w_F * missed_denies)


def grant_emphasis_loss_weighted(
    y: np.ndarray,
    y_hat: np.ndarray,
    *,
    w_T: float,
    sample_weights: np.ndarray,
) -> float:
    """L_T'(y, ŷ; w) = sum_i w_i · (w_T · 1[miss grant_i] + 1[miss deny_i]).

    Used for surprise-weighted set revision per spec §5: sample_weights derive
    from realized-outcome surprise (cases the surprise model flagged as
    anomalous get higher weight). The unweighted L_T is the special case
    sample_weights = ones.
    """
    _validate_binary_pair(y, y_hat)
    _validate_sample_weights(y, sample_weights)
    missed_grants = ((y == 1) & (y_hat == 0)).astype(float)
    missed_denies = ((y == 0) & (y_hat == 1)).astype(float)
    return float(
        (sample_weights * (w_T * missed_grants + missed_denies)).sum()
    )


def deny_emphasis_loss_weighted(
    y: np.ndarray,
    y_hat: np.ndarray,
    *,
    w_F: float,
    sample_weights: np.ndarray,
) -> float:
    """L_F'(y, ŷ; w) = sum_i w_i · (1[miss grant_i] + w_F · 1[miss deny_i])."""
    _validate_binary_pair(y, y_hat)
    _validate_sample_weights(y, sample_weights)
    missed_grants = ((y == 1) & (y_hat == 0)).astype(float)
    missed_denies = ((y == 0) & (y_hat == 1)).astype(float)
    return float(
        (sample_weights * (missed_grants + w_F * missed_denies)).sum()
    )
