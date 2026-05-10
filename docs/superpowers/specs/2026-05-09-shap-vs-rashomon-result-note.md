# SHAP vs. Rashomon — Result Note

**Date:** 2026-05-09.
**Status:** First-pass head-to-head on LendingClub V₁/V₂_alt/V₂. Pre-registered design and predictions in `2026-05-09-shap-vs-rashomon-preregistration-note.md` (OTS-stamped before this experiment ran).
**Script:** `scripts/shap_vs_rashomon.py`. Results: `runs/shap_vs_rashomon_results.json`.

---

## 1. Headline

**Rashomon's set-level apparatus is non-inferiority-survived against SHAP for outlier identification on this data.** None of the four pre-registered SHAP-silence criteria recover the T-silent-all population per-case (max Jaccard 0.008 on 2015Q4), reproduce the U-shaped regime signature (14 → 0 → 154 across vintages), or flag a population with elevated charge-off rate (T-silent-all charge-off 0.292 vs base 0.148; SHAP-silent populations at 0.125–0.168, near base rate).

The pre-registered falsification criterion (§5 of the pre-registration) required a SHAP-silence criterion to satisfy *all three* of: per-case Jaccard > 0.5, regime-shift > 5× across vintages, and charge-off rate ≥ 0.292 at p < 0.05. **Zero criteria meet any one of those three conditions, let alone all three.**

## 2. Per-case overlap (V₂ = 2015Q4)

Rashomon T-silent-all: 154 real cases (0.58%), charge-off rate 0.292 vs base 0.148.

| SHAP-silence criterion | n flagged | Charge-off rate | Jaccard with T-silent-all | Pre-reg prediction | Hit? |
|---|---|---|---|---|---|
| Magnitude (bottom decile) | 2661 (10.00%) | 0.150 | 0.000 | < 0.1 | ✓ |
| Concentration (bottom decile) | 2661 (10.00%) | 0.168 | 0.008 | [0.1, 0.3] | ✗ overestimated |
| Instability (top-3 sign flips ≥6/10 neighbors) | 4070 (15.30%) | 0.147 | 0.003 | [0.2, 0.5] | ✗ overestimated |
| Baseline-dominance (after zero-out, |Δp| ≤ 0.05) | 26457 (99.46%) | 0.148 | 0.006 | < 0.1 | ✓ |

**Reading:** I expected partial per-case recovery on instability and concentration (Jaccard 0.1–0.5). Got essentially zero across all four criteria. SHAP cases flagged as low-attribution-quality are not the same cases the policy-constrained Rashomon set fails to articulate on. They are different populations entirely.

The baseline-dominance criterion is degenerate at 99.46% — the underlying xgboost model's predictions are rarely far from base rate (consistent with the ~0.62 holdout AUC from the wedge meta), so zeroing top features almost always returns predictions to base rate. This criterion gives no useful signal as constructed; would need a tighter ε or a different formulation.

## 3. Regime-shift signature

Rashomon T-silent-all by vintage (chronological):

| Vintage | Cases | Rate |
|---|---|---|
| 2014Q3 | 14 | 0.11% |
| 2015Q3 | 0 | 0.00% |
| 2015Q4 | 154 | 0.58% |

U-shaped — present, absent, then re-emerges at scale.

SHAP-silence rates by vintage and criterion:

| Criterion | 2014Q3 | 2015Q3 | 2015Q4 | Pattern |
|---|---|---|---|---|
| Magnitude | 10.00% | 10.00% | 10.00% | Flat (decile threshold; degenerate by construction) |
| Concentration | 10.00% | 10.00% | 10.00% | Flat (decile threshold; degenerate by construction) |
| Instability | 26.26% | 15.88% | 15.30% | Decreasing — *opposite* direction from T-silent-all |
| Baseline-dominance | 96.47% | 99.83% | 99.46% | Saturated; no useful variation |

**No SHAP-silence criterion reproduces the U-shaped regime signature.** Magnitude and concentration cannot, by construction (decile thresholds force a constant rate). Instability moves in the *wrong direction* across vintages. Baseline-dominance is saturated.

## 4. What the four criteria miss, and what would be a fairer test

Two of the four criteria (magnitude, concentration) are **degenerate by construction** because they use within-vintage decile thresholds. A 10th-percentile cutoff necessarily flags 10% of cases regardless of vintage. The cross-vintage signature comparison was therefore impossible to perform for those two criteria — the test was already dead before the data was loaded. This is a methodological flaw in the pre-registration, not a property of SHAP.

A fairer next-iteration would use **absolute thresholds**: pick the magnitude / concentration cutoffs from V₁ training data and hold them fixed across V₂ vintages. Then cross-vintage rate variation becomes possible. Worth re-running with absolute thresholds before claiming the SHAP-criteria battery is exhausted.

The instability criterion *did* have cross-vintage variability (26 → 16 → 15%), but moved in the opposite direction from Rashomon's signal. So even if absolute-threshold magnitude or concentration produced a U-shape, the instability result is independent evidence that SHAP-silence (as I defined it) and Rashomon-silence are not the same phenomenon.

## 5. Why this is the expected result, structurally

The structural argument from the strategic discussion was:

> SHAP is single-model by construction. T-silent-all is defined by *all M=5 admissible Rashomon members failing simultaneously to articulate*. SHAP cannot see plurality phenomena because it has no plurality input.

The empirical result is consistent with that structural argument: SHAP-silence-on-one-model and silence-of-all-five-Rashomon-members appear to be unrelated populations. Per-case Jaccard near zero is what you'd expect if the two populations have different generative mechanisms.

The U-shaped regime signature is also consistent: regime-level changes in admissible-model-class structure (which is what produces 14 → 0 → 154 T-silent-all) are not visible to a single-model SHAP attribution because the deployed model's per-case attribution behavior is largely a function of its own training data, not of what other admissible models would have said.

## 6. What this does and does not show

**Shown:**
- For the *outlier-population identification* problem under SR 26-2 §III aggregate-model-risk language, Rashomon catches a population SHAP does not, by any of four reasonable SHAP-silence definitions.
- The gap is large (Jaccard 0.000–0.008, charge-off rates differ by 2×), not marginal.
- The pre-registered falsification criterion is not met.

**Not shown:**
- Whether absolute-threshold versions of magnitude / concentration would close the gap. Worth re-running.
- Whether a more clever SHAP-derived signal (e.g., interaction-attribution variance, Shapley-Lorenz curves, MetaSHAP) would close the gap. The pre-registration did not enumerate those.
- Whether SHAP wins the *per-case post-hoc adverse-action* comparison, which it should structurally — the per-case post-hoc validation arm in pre-registration §7 was deferred and remains open.
- Whether the result generalizes beyond LendingClub. Fannie Mae generalization arm remains the next test.

## 7. Calibration of pre-registered predictions

| Prediction | Outcome |
|---|---|
| Magnitude Jaccard < 0.1 | ✓ (0.000) |
| Concentration Jaccard ∈ [0.1, 0.3] | ✗ overestimated (0.008) |
| Instability Jaccard ∈ [0.2, 0.5] | ✗ overestimated (0.003) |
| Baseline-dominance Jaccard < 0.1 | ✓ (0.006) |
| No SHAP-silence reproduces 0 → nonzero shift | ✓ (no criterion shows U-shape) |

I overestimated SHAP's per-case recovery capacity on instability and concentration by an order of magnitude. The structural argument was correct in direction but I gave SHAP too much credit for recovering some of the population through different mechanism. The actual gap is wider than I predicted. This is a calibration finding to carry into the next pre-registration.

## 8. Followups (not committed)

- **Absolute-threshold re-run.** Re-run magnitude and concentration with cutoffs frozen at V₁ values. If absolute-threshold rates also stay flat or move opposite to Rashomon's U-shape, that closes the SHAP arm of the four-criteria battery.
- **Per-case adverse-action post-hoc test.** Run SHAP's *most-confident* attributions through the realized-outcome validation pipeline. Pre-register that Rashomon should *lose* this comparison; admitting that loss in the regulator-facing document strengthens credibility on the population-level argument.
- **Fannie Mae generalization.** With FM loader unblocked (2018Q1 collector remap landed today), run the same comparison on FM 2007Q1–2009Q4. Cross-asset-class + cross-regime test of whether the per-case-non-overlap and U-shape-non-recovery results survive.
- **Rashomon-from-reasoning-traces variant.** For the next pre-registration, the within-set adversarial sampling structure may produce a sharper "silence" signal that's even more SHAP-invisible. Worth checking whether the methodology in the Rashomon-from-reasoning-traces working notes (memory: `project_rashomon_methodology.md`) extends the per-case gap.
