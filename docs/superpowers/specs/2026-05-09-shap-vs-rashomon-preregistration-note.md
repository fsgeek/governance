# SHAP vs. Rashomon — Non-Inferiority Pre-Registration

**Date:** 2026-05-09.
**Status:** Pre-registration. **No experimental code has been written yet at the time of this note.** Predictions are recorded *before* the experiment runs so the result is load-bearing rather than reportable.
**Origin:** Strategic question raised in conversation: is SHAP/LIME non-inferior to policy-constrained Rashomon? Per-case post-hoc validation is a structural advantage for SHAP. Population-level outlier identification (T-silent-all) is where Rashomon currently shows a finding. The honest test is whether SHAP, with a fairly chosen silence definition, can recover the same population.

---

## 1. Question

On the same V₂ LendingClub cases that produced the T-silent-all finding (175 cases, charge-off rate 0.292 vs base rate 0.147), can SHAP/LIME on a single calibrated model recover the same population by some pre-specified rule?

If yes → Rashomon's set-level apparatus is non-inferiority-failed against SHAP for outlier identification, and the framework's commercial / regulatory positioning has to lean on different load-bearing arguments (plurality awareness, aggregate-risk surveillance under SR 26-2 §III) rather than on outlier-population identification.

If no → Rashomon catches something SHAP cannot, and the regulator-facing argument earns its complexity.

## 2. Setup

- **Data:** existing V₁ (2014Q3), V₂_alt (2015Q3), V₂ (2015Q4) LendingClub jsonl runs from the empty-support clustering analysis. Same Rashomon set members (M=5), same case definitions, same charge-off labels.
- **Single-model arm:** train one xgboost on the V₂ training distribution, calibrated, picked by lowest validation error. This is the "deployed model" SHAP attributes against. Independent of the Rashomon set construction so the comparison is not rigged.
- **Attribution method:** TreeSHAP (apples-to-apples with tree-based Rashomon members; standard practitioner choice).

## 3. SHAP-silence criteria (pre-registered, all reported)

There is no canonical definition of "SHAP failed to articulate," so the test enumerates candidates and reports all. Cherry-picking the worst-performing criterion to claim Rashomon advantage is excluded by pre-registration.

1. **Magnitude.** Sum of absolute SHAP values over all features below a threshold (model uses no feature strongly). Threshold: bottom decile.
2. **Concentration.** Top-1 SHAP / total below threshold (no dominant reason). Threshold: bottom decile.
3. **Sign-instability.** Top-k feature SHAP signs flip on nearest-neighbor perturbations (k=3, neighbors=10 in feature space). Threshold: ≥1 sign flip in top-3 across majority of neighbors.
4. **Baseline-dominance.** Predicted probability after zeroing top-3 SHAP-magnitude features remains within ε of base rate (model essentially predicts base rate). Threshold: ε = 0.05.

For each criterion compute T-side and F-side variants matching the empty-support clustering note's structure.

## 4. Pre-registered predictions

> **Per-case overlap with T-silent-all (V₂):**
> - **Instability criterion**: Jaccard overlap in [0.2, 0.5]. Partial recovery via SHAP's known instability on small / contested cases.
> - **Magnitude criterion**: Jaccard overlap < 0.1. T-silent-all cases are the *contested* ones with within-set disagreement, not the *unimportant* ones — magnitude doesn't track contestedness.
> - **Concentration criterion**: Jaccard overlap in [0.1, 0.3]. Some signal but weak.
> - **Baseline-dominance criterion**: Jaccard overlap < 0.1. T-silent-all has elevated charge-offs, not base-rate predictions.

> **Regime-shift signature (V₁: 0 cases → V₂: nonzero):**
> - **No SHAP-silence criterion reproduces the 0 → nonzero shift at comparable scale.** SHAP-silence rates will be approximately constant across V₁ / V₂_alt / V₂ (within ±50% relative variation). The regime-shift signature is a property of the policy-constrained set's structure under regime change, and is invisible to single-model attribution because SHAP cannot see the set.

## 5. Falsification criterion

> **Rashomon's set-level apparatus is non-inferiority-failed against SHAP for outlier identification IF any single SHAP-silence criterion produces BOTH:**
> - per-case Jaccard overlap with T-silent-all > 0.5 on V₂, AND
> - regime-shift signature (V₁ rate ≈ 0, V₂ rate nonzero, ratio > 5×) at population scale comparable to T-silent-all.
>
> **AND the SHAP-flagged population has charge-off rate ≥ T-silent-all's (≥ 0.292) at p < 0.05.**

If only the per-case overlap condition is satisfied but not the regime-shift, the conclusion is partial: SHAP recovers per-case attribution failures but not regime-shift detection — Rashomon retains its aggregate-risk-surveillance argument under SR 26-2 §III but loses its per-case outlier-identification argument.

## 6. Why this is the right test now

The T-silent-all finding currently reads as "Rashomon flagged a meaningful population." It does not read as "SHAP would have missed it." Under SR 26-2's conceptual-soundness language (interpretability *or* benchmarking-to-alternatives), both apparatuses are named tools. The regulator-facing argument needs the head-to-head, not just one arm.

Per-case adverse-action (ECOA / Reg B) is SHAP's structural domain — that's not what this test is about. This test is about population-level outlier identification under SR 26-2 §III aggregate-model-risk language, which is the territory where Rashomon's plurality-awareness should produce signal SHAP cannot.

## 7. Followups (not part of this pre-registration)

- **LIME arm.** TreeSHAP first because it's apples-to-apples with the model class. LIME is a model-agnostic alternative with different failure modes (locally linear surrogate); a separate pre-registration would add a LIME variant of each silence criterion.
- **Fannie Mae generalization.** Once the head-to-head is settled on LendingClub, run the same comparison on FM 2007Q1–2009Q4 vintages (the regime-tightening generalization arm from the empty-support clustering note §7).
- **Per-case post-hoc validation arm.** SHAP's structural advantage is post-hoc per-case validation against realized outcomes. A separate test would score SHAP's *most-confident* attributions against outcome — that's where Rashomon should *lose*, and admitting that loss in the regulator-facing document strengthens the credibility of the population-level argument.
