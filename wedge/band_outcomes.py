# wedge/band_outcomes.py
"""C/A/B outcome metrics for a constructed Rashomon band (pre-reg 2026-06-18).

C = cardinality (room to choose). A = disparity spread across members (harm a
selector could choose). B = a clean member (|gap| <= tau) exists in the band.
Both plain approval-rate gap and margin-aware gap are computed; the verdict
metric is the plain gap (margin only adds evidence — see spec §6).
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def _approve_prob(model, X) -> np.ndarray:
    return model.predict_proba(X)[:, list(model.classes_).index(1)]


def approval_rate_gap(model, X: pd.DataFrame, protected: pd.Series) -> float:
    pred = np.asarray(model.predict(X)).astype(float)
    p = np.asarray(protected, dtype=bool)
    if p.sum() == 0 or (~p).sum() == 0:
        return float("nan")
    return float(pred[p].mean() - pred[~p].mean())


def margin_aware_gap(model, X: pd.DataFrame, protected: pd.Series, *,
                     threshold: float = 0.5, band: float = 0.10) -> float:
    ap = _approve_prob(model, X)
    near = np.abs(ap - threshold) <= band
    pred = (ap >= threshold).astype(float)
    p = np.asarray(protected, dtype=bool) & near
    u = (~np.asarray(protected, dtype=bool)) & near
    if p.sum() == 0 or u.sum() == 0:
        return float("nan")
    return float(pred[p].mean() - pred[u].mean())


def band_outcomes(members, X_eval: pd.DataFrame, protected: pd.Series, *,
                  tau: float = 0.02, threshold: float = 0.5,
                  margin_band: float = 0.10) -> dict:
    plain = [approval_rate_gap(m, X_eval, protected) for m in members]
    marg = [margin_aware_gap(m, X_eval, protected, threshold=threshold, band=margin_band)
            for m in members]
    plain_v = [g for g in plain if not np.isnan(g)]
    marg_v = [g for g in marg if not np.isnan(g)]

    def spread(vs):
        return float(max(vs) - min(vs)) if vs else float("nan")

    def min_abs(vs):
        return float(min(abs(g) for g in vs)) if vs else float("nan")

    return {
        "C": len(members),
        "A_plain": spread(plain_v),
        "A_margin": spread(marg_v),
        "min_gap_plain": min_abs(plain_v),
        "min_gap_margin": min_abs(marg_v),
        "B_plain": bool(plain_v) and min_abs(plain_v) <= tau,
        "B_margin": bool(marg_v) and min_abs(marg_v) <= tau,
    }
