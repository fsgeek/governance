# Target B null Cat 2 — Findings Note from the 2026-05-11 LC 2015Q4 dual-set run

**Date:** 2026-05-11.
**Status:** Findings note (canonical for the LC 2015Q4 substrate). Plan Task 11 deliverable, re-framed: the plan anticipated a worked Cat 2 case writeup; the run produced zero Cat 2 cases, so the note is about what the run *did* show.
**Authority:** Canonical for the run identified below. Not a generalization to other substrates.
**Depends on:**
- `wedge/orchestration.py::run_dual_set_target_c` (the orchestration that produced the artifacts).
- `docs/superpowers/plans/2026-05-11-prototype-extension.md` Task 11 (the deliverable being satisfied, with re-framing noted).
- `docs/superpowers/specs/2026-05-10-mechanism-specification.md` §§3.2, 3.3, 5, 6.2, 7.2 (the mechanism this run instantiates).
- `runs/2026-05-11T20-25-56Z-target-c.jsonl` (per-case classifications).
- `runs/2026-05-11T20-25-56Z-target-c-manifest.json` (construction manifest).
- Prior-ghola warning (handoff): "weak signal on LC 2015Q4 (admissible_best AUC=0.6257); the dual-set's Cat 2 yield is empirically uncertain."
**Invalidated by:** A future run on a different substrate that *does* produce Cat 2 cases will not invalidate this note; it will sit alongside as evidence of substrate-dependence.
**Last reconciled with code:** 2026-05-11.

---

## 1. What was attempted

Per plan §11: select the highest-likelihood Cat 2 case from a V_2 dual-set run, write a structured findings note explaining (a) why the original ensemble was wrong, (b) which revised-set new-entrant model recovered the case, (c) the structural-distinguishing feature, and (d) what the case demonstrates about the mechanism.

## 2. What ran

`python -m wedge.orchestration --csv data/accepted_2007_to_2018Q4.csv --target-vintage 2015Q4 --surprise-vintages 2016Q1 2016Q2 2016Q3 2016Q4 --policy policy/thin_demo_hmda.yaml --output-dir runs`

- target vintage: LC 2015Q4 36-month terminal, 88,669 rows.
- surprise training cohort: LC 2016Q1–Q4 36-month terminal, 232,353 rows.
- out-of-sample classified: 26,601 cases.
- policy: `policy/thin_demo_hmda.yaml` (`thin_demo_hmda_mortgage` v0.1).
- sweep config: max_depths (4, 6, 8, 10, 12) × min_samples_leafs (25, 50, 100, 200, 400) × 5 feature subsets (full + each-optional-dropped).
- ε_T = ε_F = 0.05, w_T = w_F = 1.5, n_members = 5.

## 3. Aggregate results

| Quantity | Value |
|---|---|
| total sweep results | 75 |
| policy-admissible | 50 |
| policy-excluded | 25 |
| \|R_T(ε_T)\| | 40 |
| \|R_F(ε_F)\| | 40 |
| \|R_T'(ε_T)\| (surprise-weighted) | 40 |
| \|R_F'(ε_F)\| (surprise-weighted) | **1** |
| surprise weight mean / max | 0.2805 / 0.9691 |
| out-of-sample not_failure (original verdict matched realized) | 22,660 (85.2%) |
| out-of-sample Cat 1 | 3,941 (14.8%) |
| out-of-sample Cat 2 | **0** |
| out-of-sample ambiguous | 0 |
| out-of-sample cases with I_pred > 0.2 | 0 |

Every Cat 1 case has `new_entrant_count = 1` and `exit_count = 0`. The single new entrant is the same model across all 3,941 cases: the unique surviving member of R_F'(ε_F) under surprise-weighted L_F'.

## 4. Why no Cat 2 emerged

Spec §6.2's three-condition Cat 2 criterion: (1) original ensemble's verdict ≠ realized outcome; (2) revised ensemble's verdict = realized outcome; (3) new-entrant models share an expressible structural-distinguishing feature. Condition (1) holds for 3,941 cases. Condition (2) fails for all of them — the revised ensemble's mean verdict still disagrees with realized outcome at the 0.5 threshold. Condition (3) never gets evaluated.

Two structural reasons this happened, both visible in the run:

**(a) Original R_T and R_F predict the same case-level verdicts.** I_pred(x) = |E[T | R_T] − E[T | R_F]| is below the 0.2 reporting threshold for *every one* of 26,601 cases. Mean P(grant | x) under R_T and under R_F agree closely on every case in the run. The two ε-bands are different *sets* of models (the per-model loss values for L_T and L_F differ, satisfying the algorithmic precondition for R_T ≠ R_F), but their ensemble verdicts are nearly identical — the dispersion of grant-emphasis-loss-optimal and deny-emphasis-loss-optimal models around the AUC-optimal model is small enough on this substrate that asymmetric cost weighting doesn't move the predicted probability surface.

**(b) Surprise weighting collapses R_F' but the surviving model still predicts the failures wrong.** R_F' shrinks from 40 admissible models to 1. The one survivor is the model that minimizes the surprise-weighted deny-emphasis loss L_F'. Its predictions on the Cat 1 cases agree with the original ensemble's verdict at the 0.5 threshold — so even with this concentrated new entrant added to the mean, `revised_pred` and `original_pred` are on the same side of the decision boundary. Example case (anonymized texture):

| Feature | Value |
|---|---|
| `fico_range_low` | 765 |
| `dti` | 16.43 |
| `annual_inc` | 90,000 |
| `emp_length` | 10 |
| realized_outcome | 0 (charged off) |
| original_pred (mean T over R_T ∪ R_F) | 0.9651 |
| revised_pred (mean T over R_T' ∪ R_F') | 0.9709 |
| I_pred | 0.0 |

A FICO 765 / DTI 16.4 / income 90k / 10+ years employment borrower defaulted. Every admissible model — every depth, every min_leaf, every feature subset that includes the mandatory three (fico, dti, annual_inc) — predicts >0.96 grant. The realized 0 outcome is not recoverable inside this admissible space; the surprise model knows the case is anomalous (large weight in the holdout), but the loss-reweighting it induces selects an admissible model that still predicts grant.

## 5. The asymmetric collapse of L_F' is itself a structural observation

The construction manifest records four set sizes: |R_T| = 40, |R_F| = 40, |R_T'| = 40, |R_F'| = 1. Three of the four are unchanged by surprise weighting; one collapses to a single model. This is not a symmetric scaling under weighted loss — it is a sign that the deny-emphasis loss is much more sensitive to surprise weighting on this substrate than the grant-emphasis loss is. Under uniform weights, 40 models are within ε of the best L_F; under surprise weights, the ε-band shrinks to one. Under either weighting, the grant-emphasis ε-band stays at 40.

Hypothesis (not tested in this run): the LC 2015Q4 admissible-model space has many near-equivalent ways to optimize false-grant cost (since paid loans dominate the dataset, the false-grant loss is averaged over many cases and is robust to reweighting), but few ways to optimize false-deny cost (since charged-off loans are rarer and their re-weighting concentrates the loss). This is testable: a vintage with a more balanced label distribution should show less asymmetry.

## 6. What this run demonstrates about the mechanism

On LC 2015Q4 with the thin demo HMDA policy and the V1 default sweep, the dual-set mechanism's set-revision step under surprise weighting does not recover any out-of-sample failure. This is consistent with one of two diagnoses, both internal to the mechanism's design:

- The admissible space (CART, depth ≤ 12, min_leaf ≥ 25, must include fico_range_low ∧ dti ∧ annual_inc) does not contain a model that predicts the realized failures correctly. If the realized failures of LC 2015Q4 are not separable inside the policy's hypothesis class, no admissible recovery is possible. This is the Cat 1 ground-state of the mechanism: the policy is genuinely binding.
- The set-revision mechanism (surprise-weighted L_T' / L_F') is too coarse to surface a recovering model even when one exists in the admissible space. This is the failure-mode the mechanism is supposed to *exclude* by construction; it is testable by inspecting whether any single admissible model gets the Cat 1 cases right, regardless of which set it falls into.

The second diagnosis is the more interesting falsification target; it can be checked by computing per-admissible-model accuracy on the Cat 1 case subset and asking whether any single admissible model exceeds a meaningful fraction.

## 7. The pending test, executed (2026-05-11)

Cat 1 on this run is structurally narrow: every Cat 1 case has realized_outcome = 0 (charged off) AND original ensemble verdict = 1 (predicted grant). So the falsification test reduces to: "for each admissible model, on what fraction of the 3,941 predicted-grant / actually-defaulted cases does the model predict deny?"

Script: `scripts/cat1_admissible_recovery.py`. Output: `runs/2026-05-11-cat1-admissible-recovery.txt`.

| Quantity | Value |
|---|---|
| admissible models tested | 50 |
| max admissible Cat 1 deny-fraction (== accuracy) | **0.0089** (35 / 3,941) |
| mean admissible Cat 1 accuracy | 0.0008 |
| admissible models with any deny prediction on Cat 1 | **10 / 50** |
| admissible models with zero deny prediction on Cat 1 | 40 / 50 |

The top recovering model (max_depth=12, min_samples_leaf=25, 3-feature subset) catches 35 of 3,941 Cat 1 cases. The other 40 of 50 admissible models predict grant on every single Cat 1 case.

**The "policy genuinely binding" diagnosis stands.** The set-revision mechanism (surprise-weighted L_T' / L_F') was not too coarse to surface a recovering model — there simply isn't a recovering admissible model to surface. The maximum admissible recovery is under 1%; no aggregation rule applied to a 50-model admissible space will produce a Cat 2 verdict from this material.

### 7.1 Texture: recovery tracks overfitting, not predictive quality

A regularity worth flagging: Cat 1 recovery and holdout AUC do *not* covary positively across admissible models.

| Model | max_depth | min_samples_leaf | holdout AUC | Cat 1 deny-fraction |
|---|---|---|---|---|
| best Cat 1 recovery | 12 | 25 | 0.5875 | 0.0089 |
| highest AUC at d=12 | 12 | 400 | 0.6249 | 0.0000 |

The shallowest / largest-leaf admissible models (the most regularized) recover *zero* Cat 1 cases but achieve the best holdout AUC. The deepest / smallest-leaf admissible models (the leakiest) recover the most Cat 1 cases at lower AUC. Cat 1 recovery, on this substrate, is an artifact of overfitting to anomalous training cases — not a signal of better predictive judgment.

This is mechanism-internal good news: the regularized admissible models are not failing to find a real signal that an overfit model would catch; the "recoveries" the deepest models produce are extensions of overfit decision boundaries to similar-looking anomalous cases in the out-of-sample set. The mechanism's regularization is doing what it should.

## 8. Generalization

This run does not generalize. The negative Cat 2 yield is a finding about *this substrate × this policy × this hypothesis space*, not about the mechanism's effectiveness in general. A run on a substrate with stronger admissible-space heterogeneity — a different vintage, a different asset class, or a richer hypothesis class — would test the mechanism differently. The §7 result rules out one specific failure mode (coarse set-revision masking a recovery present in the admissible space) for *this* run only.
