"""Within-tier disagreement as a routing signal -- orchestration (follow-on to #6).

Pre-registration: docs/superpowers/specs/2026-05-12-disagreement-routing-preregistration-note.md.

For the load-bearing 2015H2 `dti` burst (Burst D of #6): build on V1 = 2015Q3,
route-evaluate on V2 = 2015Q4. For each Cat-2-(pricing) sub-grade flagged in V1,
rebuild the policy-constrained refinement epsilon-band (`wedge.refinement_set`,
same params as #6), refit its distinct members on the full V1 grade, then on V2:

  d(x)    = std over band members of their predicted-default probability on x
  p_bar(x)= mean over band members of that probability
  terciles of d(x) -> low / middle / high disagreement

and the four pre-registered routing metrics (`wedge.routing`):
  1. within-tercile mean member AUC vs a grade-size-aware shuffle null
  2. Spearman of (disagreement-decile index, |mean realized default - mean p_bar|)
  3. consensus Brier high-tercile minus low-tercile
  4. operational lift: ECE on all of V2's grade-G loans vs on low+middle terciles
     only (high-disagreement tercile routed to manual review)
plus a feature-space-outlier diagnostic (is the high-d tercile extrapolated-on?).

The pre-registered verdict aggregates over the *plural* grades of Burst D
(median pairwise ranking-Spearman < 0.9 in #6: A5, B1, C1, C5, D4 -- rederived
here, not hardcoded): "disagreement is a valid routing signal" holds iff metrics
1-3 point the routing way on a majority of the plural grades, with metric 4's
lift non-negative on a majority. A robustness arm reports the same metrics
in-sample on V1.

Usage:
    PYTHONPATH=. python scripts/disagreement_routing_test.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer

from policy.encoder import load_policy
from wedge.collectors.lendingclub import (
    derive_label,
    filter_to_vintage,
    normalize_emp_length,
)
from wedge.refinement_set import (
    build_refinement_band,
    pairwise_ranking_spearman,
    refit_member,
    used_feature_set,
)
from wedge.routing import (
    brier_by_tercile,
    calibration_gap_vs_disagreement,
    consensus_scores,
    feature_space_outlierness,
    grade_routing_verdict,
    operational_lift,
    per_borrower_disagreement,
    tercile_labels,
    within_tercile_member_auc,
)

LC_CSV = Path("data/accepted_2007_to_2018Q4.csv")
TERM = "36 months"
POLICY_PATH = "policy/thin_demo_hmda.yaml"
SWEEP_SUMMARY = Path("runs/pricing-lc-sweep-36mo-summary.json")
OUT = Path("runs/disagreement_routing_test_results.json")

# Burst D of #6: the load-bearing 2015H2 `dti` burst.
V1, V2 = "2015Q3", "2015Q4"

NAMED_FEATURES = ["fico_range_low", "dti", "annual_inc", "emp_length"]

# Same band construction as #6 (so the bands here ARE the #6 bands).
EPSILON = 0.02
DEPTHS = (1, 2, 3)
LEAF_MINS = (25, 50, 100)
SEED = 0
PLURALITY_RHO_MAX = 0.9  # #6's plurality cutoff on median pairwise ranking-Spearman

# Routing metrics.
N_PERM = 500
NULL_PCT = 95
N_DECILE = 10


def _coerce_numeric(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s.astype(str).str.strip().str.rstrip("%"), errors="coerce")


def _prep(raw: pd.DataFrame, vintage: str) -> pd.DataFrame:
    df = filter_to_vintage(raw.copy(), vintage=vintage, term=TERM)
    if df.empty:
        return df
    df["label"] = derive_label(df["loan_status"])
    if "emp_length" in df.columns:
        df["emp_length"] = normalize_emp_length(df["emp_length"])
    for c in NAMED_FEATURES:
        if c in df.columns:
            df[c] = _coerce_numeric(df[c])
    df = df.dropna(subset=["label", "sub_grade"]).reset_index(drop=True)
    keep = df["sub_grade"].apply(
        lambda s: isinstance(s, str) and len(s) == 2 and s[0] in "ABCDEFG" and s[1] in "12345"
    )
    return df[keep].reset_index(drop=True)


def _flagged_grades(vintage: str) -> list[str]:
    summ = json.loads(SWEEP_SUMMARY.read_text())
    for row in summ.get("vintages", []):
        if row["vintage"] == vintage:
            return sorted(g for g, c in row["grade_classification"].items()
                          if c == "Cat 2 (pricing)")
    return []


def _grade_xy(df: pd.DataFrame, grade: str, cols: list[str]) -> tuple[np.ndarray, np.ndarray]:
    sub = df[df["sub_grade"] == grade]
    X = sub[cols].to_numpy(dtype=float)
    y = (sub["label"] == 0).to_numpy(dtype=int)  # 1 = default
    return X, y


def _subset(X: np.ndarray, feature_names: list[str], subset: tuple[str, ...]) -> np.ndarray:
    idx = {f: i for i, f in enumerate(feature_names)}
    return X[:, [idx[f] for f in subset]]


def _score_matrix(refit_models: list, members: list, X: np.ndarray,
                  feature_names: list[str]) -> np.ndarray:
    """(n_members, n_rows) predicted-default probabilities; each member predicts
    on its own feature subset of X (X aligned to `feature_names`)."""
    rows = [mdl.predict_proba(_subset(X, feature_names, m.feature_subset))[:, 1]
            for mdl, m in zip(refit_models, members)]
    return np.vstack(rows)


def _routing_metrics(M: np.ndarray, y: np.ndarray, X_ref: np.ndarray, X_eval: np.ndarray,
                     *, rng_seed: int) -> dict:
    """All four routing metrics + the outlier diagnostic on one (score matrix,
    labels, eval features) triple; `X_ref` is the V1 feature matrix the band was
    fit on (the Mahalanobis reference). Returns a JSON-able dict including the
    routing-relevant booleans."""
    d = per_borrower_disagreement(M)
    p = consensus_scores(M)
    terc = tercile_labels(d)
    m1 = within_tercile_member_auc(M, y, terc, n_perm=N_PERM, percentile=NULL_PCT, rng_seed=rng_seed)
    m2 = calibration_gap_vs_disagreement(d, p, y, n_bins=N_DECILE)
    m3 = brier_by_tercile(p, y, terc)
    m4 = operational_lift(p, y, terc, n_bins=N_DECILE)
    out = feature_space_outlierness(X_eval, X_ref, terc)
    verdict = grade_routing_verdict(metric1=m1, metric2=m2, metric3=m3, metric4=m4)
    return {
        "n": int(y.size), "n_default": int(y.sum()),
        "disagreement_summary": {"min": round(float(d.min()), 6), "median": round(float(np.median(d)), 6),
                                 "max": round(float(d.max()), 6), "mean": round(float(d.mean()), 6)},
        "tercile_sizes": {int(t): int((terc == t).sum()) for t in (0, 1, 2)},
        "metric1_tercile_member_auc": m1,
        "metric2_calibration_gap_vs_disagreement": m2,
        "metric3_consensus_brier_by_tercile": m3,
        "metric4_operational_lift": m4,
        "diagnostic_feature_space_outlierness": out,
        "routing_relevant": verdict,
    }


def _count_routing(grade_recs: dict, plural_grades: list[str]) -> dict:
    """Roll up the routing-relevant booleans over the plural grades (pre-reg §3)."""
    def tally(arm: str, key: str) -> tuple[int, int]:
        yes = no = 0
        for g in plural_grades:
            rr = grade_recs.get(g, {}).get(arm, {}).get("routing_relevant", {})
            v = rr.get(key)
            if v is True:
                yes += 1
            elif v is False:
                no += 1
        return yes, no
    arm = "v2_forward"
    n = len(plural_grades)
    m1y, m1n = tally(arm, "m1_tercile_predictability_routing")
    m2y, m2n = tally(arm, "m2_calibration_gap_routing")
    m3y, m3n = tally(arm, "m3_brier_routing")
    m4y, m4n = tally(arm, "m4_operational_lift_nonneg")
    maj = n / 2
    metrics_123_routing = (m1y > maj) and (m2y > maj) and (m3y > maj)
    metrics_123_falsified = (m1n >= maj) and (m2n >= maj) and (m3n >= maj)
    return {
        "n_plural_grades": n, "plural_grades": plural_grades,
        "metric1_routing_yes_no": [m1y, m1n], "metric2_routing_yes_no": [m2y, m2n],
        "metric3_routing_yes_no": [m3y, m3n], "metric4_lift_nonneg_yes_no": [m4y, m4n],
        "metrics_1_2_3_routing_majority": bool(metrics_123_routing),
        "metrics_1_2_3_falsified_majority": bool(metrics_123_falsified),
        "metric4_lift_nonneg_majority": bool(m4y > maj),
        "valid_routing_signal": bool(metrics_123_routing and m4y > maj),
        "deflated_no_routing_signal": bool(metrics_123_falsified),
    }


def main() -> int:
    print(f"Reading {LC_CSV} (columns only)...", flush=True)
    needed = ["issue_d", "term", "loan_status", "sub_grade", *NAMED_FEATURES]
    raw = pd.read_csv(LC_CSV, usecols=lambda c: c in needed, low_memory=False)
    print(f"  raw rows: {len(raw)}", flush=True)

    pc = load_policy(POLICY_PATH)
    avail_named = [f for f in NAMED_FEATURES if f in raw.columns]
    # Encoder states monotonicity w.r.t. GRANT prob; refinements predict DEFAULT
    # prob -> negate. (Same wiring as #6.)
    mono_default = {f: -v for f, v in pc.monotonicity_map.items() if f in avail_named}
    print(f"  policy '{pc.name}': named in LC = {avail_named}; "
          f"monotonic_cst (default-convention) = {mono_default}", flush=True)

    df1, df2 = _prep(raw, V1), _prep(raw, V2)
    flagged = _flagged_grades(V1)
    print(f"\n{'='*78}\nBurst D: build on {V1} ({len(df1)} loans), route-eval on {V2} "
          f"({len(df2)} loans)\n  flagged Cat-2 grades in {V1}: {flagged}\n{'='*78}", flush=True)

    results: dict = {
        "pre_reg": "docs/superpowers/specs/2026-05-12-disagreement-routing-preregistration-note.md",
        "burst": "D_2015H2_dti", "v1": V1, "v2": V2, "policy": pc.name,
        "monotonic_cst_default_convention": mono_default, "named_features": avail_named,
        "band_params": {"epsilon": EPSILON, "depths": list(DEPTHS), "leaf_mins": list(LEAF_MINS),
                        "seed": SEED, "plurality_rho_max": PLURALITY_RHO_MAX},
        "routing_params": {"n_perm": N_PERM, "null_percentile": NULL_PCT, "n_deciles": N_DECILE},
        "flagged_grades_v1": flagged, "grades": {},
    }

    plural_grades: list[str] = []
    for gi, g in enumerate(flagged):
        X1, y1 = _grade_xy(df1, g, avail_named)
        X2, y2 = _grade_xy(df2, g, avail_named)
        if y1.size < 50 or y1.min() == y1.max() or y2.size < 50 or y2.min() == y2.max():
            print(f"  {g}: SKIP (degenerate / too few)", flush=True)
            results["grades"][g] = {"verdict": "SKIP"}
            continue
        imp = SimpleImputer(strategy="median").fit(X1)
        X1i, X2i = imp.transform(X1), imp.transform(X2)

        band = build_refinement_band(X1i, y1, feature_names=avail_named,
                                     monotonic_cst_map=mono_default, epsilon=EPSILON,
                                     depths=DEPTHS, leaf_mins=LEAF_MINS, seed=SEED)
        distinct = band.distinct_members
        if len(distinct) < 2:
            print(f"  {g}: SKIP (band has <2 distinct members)", flush=True)
            results["grades"][g] = {"verdict": "SKIP", "band_distinct_members": len(distinct)}
            continue

        refit = [refit_member(m, _subset(X1i, avail_named, m.feature_subset), y1,
                              feature_names=list(m.feature_subset), seed=SEED) for m in distinct]
        used_sets = [frozenset(used_feature_set(mdl, m.feature_subset)) for mdl, m in zip(refit, distinct)]
        n_used_sets = len({u for u in used_sets if u})
        v1_scores = [mdl.predict_proba(_subset(X1i, avail_named, m.feature_subset))[:, 1]
                     for mdl, m in zip(refit, distinct)]
        med_rho, min_rho = pairwise_ranking_spearman(v1_scores)
        non_trivial = len(distinct) >= 3
        plural = (n_used_sets >= 2) and (med_rho < PLURALITY_RHO_MAX)
        if plural:
            plural_grades.append(g)

        M2 = _score_matrix(refit, distinct, X2i, avail_named)
        M1 = np.vstack(v1_scores)
        v2_arm = _routing_metrics(M2, y2, X1i, X2i, rng_seed=10_000 + gi * 17)
        v1_arm = _routing_metrics(M1, y1, X1i, X1i, rng_seed=50_000 + gi * 17)

        rec = {
            "n_v1": int(y1.size), "n_v2": int(y2.size),
            "default_rate_v1": round(float(y1.mean()), 4), "default_rate_v2": round(float(y2.mean()), 4),
            "band_members_within_eps": len(band.members), "band_distinct_members": len(distinct),
            "best_holdout_auc": round(band.best_holdout_auc, 4) if band.best_holdout_auc else None,
            "n_distinct_used_feature_sets": n_used_sets,
            "median_pairwise_spearman_v1": round(med_rho, 4), "min_pairwise_spearman_v1": round(min_rho, 4),
            "non_trivial": bool(non_trivial), "plural": bool(plural),
            "v2_forward": v2_arm, "v1_insample": v1_arm,
        }
        results["grades"][g] = rec
        rr = v2_arm["routing_relevant"]
        m1lo = v2_arm["metric1_tercile_member_auc"][0]["mean_member_auc"]
        m1hi = v2_arm["metric1_tercile_member_auc"][2]["mean_member_auc"]
        print(f"  {g}: n_v2={y1.size:5d}/{y2.size:5d}  band={len(band.members)}/{len(distinct)}  "
              f"plural={plural} (med_rho={med_rho:.3f})  | V2: "
              f"m1AUC lo/hi={m1lo}/{m1hi}  m2rho={v2_arm['metric2_calibration_gap_vs_disagreement']['spearman_rho']}  "
              f"m3 hi-lo={v2_arm['metric3_consensus_brier_by_tercile']['high_minus_low']}  "
              f"m4 lift={v2_arm['metric4_operational_lift']['lift']}  outlier hi/lo="
              f"{v2_arm['diagnostic_feature_space_outlierness']['high_over_low']}  -> "
              f"m1={rr['m1_tercile_predictability_routing']} m2={rr['m2_calibration_gap_routing']} "
              f"m3={rr['m3_brier_routing']} m4={rr['m4_operational_lift_nonneg']}", flush=True)

    # ---- Verdict (over the plural grades of Burst D) ----
    roll = _count_routing(results["grades"], plural_grades)
    results["plural_grades"] = plural_grades
    results["verdict_v2_forward"] = roll
    # Robustness: same roll-up on the in-sample arm.
    def tally_arm(arm: str, key: str) -> list[int]:
        yes = no = 0
        for g in plural_grades:
            v = results["grades"].get(g, {}).get(arm, {}).get("routing_relevant", {}).get(key)
            if v is True:
                yes += 1
            elif v is False:
                no += 1
        return [yes, no]
    results["verdict_v1_insample"] = {
        "n_plural_grades": len(plural_grades),
        "metric1_routing_yes_no": tally_arm("v1_insample", "m1_tercile_predictability_routing"),
        "metric2_routing_yes_no": tally_arm("v1_insample", "m2_calibration_gap_routing"),
        "metric3_routing_yes_no": tally_arm("v1_insample", "m3_brier_routing"),
        "metric4_lift_nonneg_yes_no": tally_arm("v1_insample", "m4_operational_lift_nonneg"),
    }
    # The most-disagreeing grade (B1 in #6) — call it out.
    if plural_grades:
        most_dis = min(plural_grades, key=lambda g: results["grades"][g]["median_pairwise_spearman_v1"])
        results["most_disagreeing_grade"] = {
            "grade": most_dis,
            "median_pairwise_spearman_v1": results["grades"][most_dis]["median_pairwise_spearman_v1"],
            "v2_routing_relevant": results["grades"][most_dis]["v2_forward"]["routing_relevant"],
        }

    summary = (
        f"Disagreement-as-routing on Burst D ({V1}->{V2}), {len(plural_grades)} plural grades "
        f"{plural_grades}: metrics 1/2/3 routing-yes counts = "
        f"{roll['metric1_routing_yes_no'][0]}/{roll['metric2_routing_yes_no'][0]}/{roll['metric3_routing_yes_no'][0]} of "
        f"{len(plural_grades)}; metric-4 lift>=0 on {roll['metric4_lift_nonneg_yes_no'][0]}/{len(plural_grades)}. "
        + ("VALID routing signal (1-3 majority + metric-4 majority)."
           if roll["valid_routing_signal"]
           else ("DEFLATED: routing signal not valid (1-3 fail on a majority)."
                 if roll["deflated_no_routing_signal"]
                 else "MIXED: neither the validity nor the deflation criterion is met on a clean majority."))
    )
    results["summary"] = summary
    print(f"\n{'#'*78}\n{summary}\n{'#'*78}", flush=True)

    OUT.write_text(json.dumps(results, indent=2))
    print(f"\nwrote {OUT}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
