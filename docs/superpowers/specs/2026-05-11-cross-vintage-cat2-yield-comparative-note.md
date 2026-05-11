# Cross-substrate Cat 2 yield — Comparative Note (LC 36-month × 3 vintages + FM 2018Q1)

**Date:** 2026-05-11.
**Status:** Findings note (canonical for LC 36-month vintages 2014Q3, 2015Q3, 2015Q4 under the thin demo HMDA policy AND for Fannie Mae 2018Q1 first-lien mortgage under the thin demo FM policy). The file name retains its original cross-vintage scope; the FM 2018Q1 cross-asset-class section (§4) extends scope to a different substrate.
**Authority:** Canonical for the four runs identified below. Not a generalization to a richer hypothesis space.
**Depends on:**
- `docs/superpowers/specs/2026-05-11-target-b-null-cat2-findings-note.md` (the 2015Q4-specific note this comparator replicates).
- `wedge/orchestration.py::run_dual_set_target_c`.
- Four dual-set runs:
  - `runs/2026-05-11T21-56-27Z-target-c.jsonl` (LC 2014Q3 target, 2015 surprise cohort).
  - `runs/2026-05-11T21-53-00Z-target-c.jsonl` (LC 2015Q3 target, 2016 surprise cohort).
  - `runs/2026-05-11T20-25-56Z-target-c.jsonl` (LC 2015Q4 target, 2016 surprise cohort).
  - `runs/2026-05-11T22-12-32Z-target-c.jsonl` (FM 2018Q1 target, sibling-half surprise cohort).
- Four Cat 1 admissible-recovery audits:
  - `runs/2026-05-11-cat1-admissible-recovery-2014Q3.txt`
  - `runs/2026-05-11-cat1-admissible-recovery-2015Q3.txt`
  - `runs/2026-05-11-cat1-admissible-recovery.txt` (LC 2015Q4)
  - `runs/2026-05-11-cat1-admissible-recovery-FM2018Q1.txt`
- Scripts: `scripts/cat1_admissible_recovery.py` (LC; `--vintage`-parameterized), `scripts/cat1_admissible_recovery_fm.py` (FM), `scripts/run_dual_set_fm.py` (FM orchestration entry).
- Policy: `policy/thin_demo_fm.yaml` (companion to thin_demo_hmda.yaml for FM's feature space).

**Invalidated by:** A future run on a different asset class (HMDA full-file, MFLPD, HARP) or a richer hypothesis class that produces Cat 2 cases under this policy will not invalidate this note; it will sit alongside as evidence of which combinatorial axis is load-bearing for the null result.
**Last reconciled with code:** 2026-05-11 (FM section added later same day; see §4).

---

## 1. The replication question

The 2015Q4 null-Cat-2 note diagnosed "policy genuinely binding on this substrate × hypothesis space," with the falsification test (max admissible Cat 1 recovery < 1%) carrying that diagnosis. The question this note answers: does the null Cat 2 result hold across LC 36-month vintages, or is it 2015Q4-specific?

Method: rerun `wedge.orchestration run_dual_set_target_c` on two additional LC vintages with comparable surprise cohorts, then rerun the per-admissible-model Cat 1 recovery test on each.

## 2. Cross-vintage dual-set runs

All three runs share: thin demo HMDA policy, ε_T = ε_F = 0.05, w_T = w_F = 1.5, n_members = 5, seed = 0, sweep grid (depths 4-12, leafs 25-400, 5 feature subsets).

| Quantity | 2014Q3 (V_1) | 2015Q3 (V_2_alt) | 2015Q4 (V_2) |
|---|---|---|---|
| surprise cohort | 2015Q1-Q4 | 2016Q1-Q4 | 2016Q1-Q4 |
| target rows | 40,595 | 73,567 | 88,669 |
| surprise rows | 283,026 | 232,353 | 232,353 |
| out-of-sample cases | 12,179 | 22,071 | 26,601 |
| swept / admissible / excluded | 75 / 50 / 25 | 75 / 50 / 25 | 75 / 50 / 25 |
| \|R_T\| | 45 | 43 | 40 |
| \|R_F\| | 45 | **1** | 40 |
| \|R_T'\| | 45 | 43 | 40 |
| \|R_F'\| | **1** | **1** | **1** |
| not_failure | 10,519 (86.4%) | 18,853 (85.4%) | 22,660 (85.2%) |
| Cat 1 | 1,660 (13.6%) | 3,218 (14.6%) | 3,941 (14.8%) |
| **Cat 2** | **0** | **0** | **0** |
| ambiguous | 0 | 0 | 0 |
| I_pred > 0.2 cases | 0 | 34 | 0 |
| surprise weight mean / max | 0.235 / 0.984 | 0.279 / 0.986 | 0.281 / 0.969 |

Patterns across all three:
- Cat 2 yield is **zero** on every vintage.
- |R_F'| collapses to a single model under surprise-weighted L_F' on every vintage.
- Cat 1 fraction is stable at 13.6%–14.8% across vintages; not_failure fraction is stable at 85.2%–86.4%.
- The admissible-set size (50) is identical across vintages, indicating the policy filter is operating on the same structural axes.

Patterns that vary:
- |R_F| under *unweighted* L_F varies: 45 on 2014Q3, 1 on 2015Q3, 40 on 2015Q4. 2015Q3 alone exhibits L_F-collapse without surprise weighting.
- I_pred > 0.2 cases: 0, 34, 0. Only 2015Q3 produces case-level R_T-vs-R_F disagreement; in the others the two ε-bands' ensemble verdicts agree on every case.

## 3. Cat 1 admissible-recovery — across vintages

Falsification target as in the 2015Q4 note: if any single admissible model recovers a meaningful fraction of Cat 1 cases, the diagnosis would be "set-revision mechanism too coarse," not "policy binding." Cat 1 on every vintage is again structurally narrow (realized=0 / original-verdict=1 on every Cat 1 case), so the test reduces to per-model deny-fraction.

| Vintage | n Cat 1 | max recovery | mean recovery | models with any deny / 50 |
|---|---|---|---|---|
| 2014Q3 | 1,660 | **0.0133** (22 / 1,660) | 0.0013 | 8 / 50 |
| 2015Q3 | 3,218 | **0.0059** (19 / 3,218) | 0.0004 | 7 / 50 |
| 2015Q4 | 3,941 | **0.0089** (35 / 3,941) | 0.0008 | 10 / 50 |

Across all three vintages: max admissible recovery on Cat 1 stays ≤ 1.33%. 80%-86% of admissible models predict grant on *every* Cat 1 case (zero denies). The deepest, leakiest admissible model (d=12, leaf=25) is consistently the top recoverer on every vintage; the most-regularized admissible models (d=12, leaf=400) consistently recover zero.

**The "policy genuinely binding" diagnosis holds across LC 36-month vintages.** No admissible model under this policy and hypothesis space recovers a meaningful fraction of the realized failures, on any of the three vintages. The set-revision mechanism is not the bottleneck; the admissible space is.

## 4. Cross-asset-class: Fannie Mae 2018Q1

The natural next-substrate test is a different asset class. FM 2018Q1 is the only FM cohort available on disk, so the orchestration is run with target / surprise cohorts drawn from a 50/50 stratified split of the same vintage. This degrades the "different-vintage surprise" semantic (the surprise model is trained on a sibling subset of the same vintage rather than a distinct prior vintage) but the dual-set / Cat 2 mechanics still exercise; the surprise-weighting interpretation is weaker on this run, as §4.1 makes explicit.

Policy: `policy/thin_demo_fm.yaml` — the HMDA thin demo adapted to FM's feature space (LTV substitutes for annual_inc; mandatory = fico_range_low, dti, ltv).

Run: `runs/2026-05-11T22-12-32Z-target-c.{jsonl,manifest.json}`. Script: `scripts/run_dual_set_fm.py`.

| Quantity | FM 2018Q1 | LC 2014Q3 | LC 2015Q3 | LC 2015Q4 |
|---|---|---|---|---|
| eligible rows | 401,623 | 40,595 | 73,567 | 88,669 |
| oos cases | 60,192 | 12,179 | 22,071 | 26,601 |
| grant fraction | **0.992** | ~0.87 | ~0.87 | ~0.87 |
| admissible / excluded | 50 / 25 | 50 / 25 | 50 / 25 | 50 / 25 |
| \|R_T\| | 50 | 45 | 43 | 40 |
| \|R_F\| | **50** | 45 | **1** | 40 |
| \|R_T'\| | 50 | 45 | 43 | 40 |
| \|R_F'\| | **50** | **1** | **1** | **1** |
| Cat 1 | 479 (0.80%) | 1,660 (13.6%) | 3,218 (14.6%) | 3,941 (14.8%) |
| **Cat 2** | **0** | **0** | **0** | **0** |
| I_pred > 0.2 | 0 | 0 | 34 | 0 |
| surprise weight mean / max | **0.015** / 1.000 | 0.235 / 0.984 | 0.279 / 0.986 | 0.281 / 0.969 |

### 4.1 Three substantive differences from the LC vintages

**(i) The L_F' collapse is LC-specific.** On FM, every band stays at full size (|R_T| = |R_F| = |R_T'| = |R_F'| = 50). The asymmetric collapse of R_F' observed on every LC vintage does not happen on FM. The structural finding "deny-emphasis loss under surprise weighting is sharply discriminating" was a feature of the LC substrate × this hypothesis space, not a property of the mechanism.

**(ii) Surprise weights collapse on the FM substrate.** Mean surprise weight is 0.015 on FM vs 0.23-0.28 on LC. This is a direct consequence of class imbalance: with 99.2% grant rate, the surprise model's p_grant is near 1 for almost every case, and `realized - p_grant` is near 0 in absolute value. The surprise-weighted L_T' / L_F' are therefore very close to the unweighted L_T / L_F, and the revised set is approximately the original set. So the FM run does not really exercise the surprise-weighting story — it's effectively an original-set-only run.

**(iii) Cat 1 fraction tracks deny rate.** 0.80% Cat 1 on FM, 13.6-14.8% on LC; the deny rates are 0.80% and ~13% respectively. Almost every actually-denied case becomes a Cat 1 case under this policy and hypothesis space, on both substrates. This says the original ensemble's verdict consistently agrees with the dominant class, and the failures are all "predicted dominant, realized minority."

### 4.2 Cat 1 admissible-recovery on FM (falsification)

Following the §3 method on the FM 479-case Cat 1 subset. Cat 1 on FM is again uniform: realized=0 / original-verdict=1 on every case.

Script: `scripts/cat1_admissible_recovery_fm.py`. Output: `runs/2026-05-11-cat1-admissible-recovery-FM2018Q1.txt`.

| Quantity | Value |
|---|---|
| admissible models tested | 50 |
| n Cat 1 cases | 479 |
| max admissible Cat 1 deny-fraction | **0.0000** (0 / 479) |
| mean admissible Cat 1 accuracy | 0.0000 |
| admissible models with any deny prediction on Cat 1 | **0 / 50** |

**Sharper falsification than LC.** Across 50 admissible models × 479 Cat 1 cases = 23,950 model-case predictions, *not one* predicts deny. Every admissible model collapses to "always-grant" on the realized-default cases.

Texture: FM admissible AUCs range 0.71-0.80 (vs LC's 0.59-0.63). The FM models are much better overall predictors than the LC models — they just collapse uniformly to grant on the failure cases, which is consistent with class imbalance (0.80% deny on FM): a model can achieve AUC 0.79 by predicting grant on essentially everything. Whether this reflects "the FM admissible space genuinely cannot recover" or "the FM admissible space is so dominated by the majority class that recovery requires giving up overall AUC" is unresolved by this test — but for the purposes of the §6.2 Cat 2 criterion, the diagnosis is the same: no admissible model recovers.

The d=4 admissible models (the *most* regularized, AUC 0.79) and the d=12 admissible models (the least, AUC 0.71-0.78) both produce zero deny predictions on Cat 1. The LC pattern "deeper trees recover more" does not hold on FM: every depth produces zero recovery.

## 5. What this rules out, what it does not

Rules out (across the four substrates run today: LC 2014Q3, LC 2015Q3, LC 2015Q4, FM 2018Q1):
- "The null is LC-specific." It is not; FM 2018Q1 also produces zero Cat 2.
- "The null is vintage-specific within LC." It is not; three LC vintages all show the null.
- "Surprise weighting is the binding bottleneck." It is not; 2015Q3 shows |R_F|=1 without surprise weighting and the LC recovery profile is unchanged, and the FM run's surprise weights collapse without changing the null.
- "Set-revision averaging is masking individual model recoveries within LC." It is not; per-admissible-model accuracy on Cat 1 stays below 1.5% across all three LC vintages.
- "The L_F' collapse is mechanism-intrinsic." It is not; FM's L_F' stays at full size.

Does not rule out:
- A richer hypothesis space (deeper trees, gradient-boosted ensembles, or non-tree models) might produce Cat 2 cases. Natural next test on either substrate.
- A richer policy (with monotonicity constraints, more mandatory features, or a different subset structure) might shrink the admissible space toward models that handle the Cat 1 cases.
- Another asset class (HMDA full-file, MFLPD, HARP) may exhibit different Cat 2 yield. FM is one extra substrate; not a generalization to all of mortgage finance.
- The FM run's surprise-weighting story is weak (sibling-cohort surprise model); a re-run with a multi-vintage FM surprise cohort, when more FM data is available, would tighten that.

## 6. Texture: the 34 I_pred-positive cases on 2015Q3

2015Q3 alone produces 34 cases with I_pred > 0.2. Composition: 29 not_failure + 5 Cat 1. The top case (FICO 670 / DTI 22.4 / income 38k / emp_length NaN) has I_pred = 0.252; original_pred = 0.753 = revised_pred (identical to four decimal places). Realized outcome = 1; case is not_failure. Both ensembles' mean verdicts agree with realized despite the strong disagreement between the single L_F model and the R_T ensemble — the within-ensemble dispersion does not propagate to the mean.

The 5 Cat 1 cases with I_pred > 0.2 are candidate Cat 2-like signals, but each fails condition 2 of the §6.2 criterion: the revised ensemble's mean verdict still disagrees with realized outcome. The dispersion exists but is not aligned with recovery.

This 2015Q3-specific texture suggests the dual-set's structural richness is vintage-sensitive but the *recovery* property still isn't satisfied. The 34 cases are visible in the jsonl for further inspection if a future test wants to revisit them.

## 7. Hypotheses for next tests (not pre-registered as falsifications)

**(a) w_F / w_T sweep on LC.** The asymmetric collapse of L_F' on LC suggests the deny-emphasis loss is sharply discriminating on the LC × thin-demo-HMDA × CART combination. A natural next test is to vary w_F (or w_T) and observe whether |R_F| traces a smooth ε-band size curve or shows sharp transitions. The FM result removes one diagnosis (the asymmetry is mechanism-intrinsic) and sharpens the question: what specific feature of LC × thin demo × CART produces the L_F collapse?

**(b) Richer hypothesis space.** Across all four substrates, the admissible-set size is 50 (post-policy from 75 swept). A richer hypothesis class (more depths, more min-leaf settings, more feature subsets, or non-CART models) would test whether the null Cat 2 is a property of the CART-with-this-grid space or of the policy × substrate.

**(c) Multi-vintage FM surprise cohort.** The FM run's sibling-cohort surprise model is the weakest part of the design. Acquiring additional FM quarters (2017Q4 or earlier as surprise training; 2018Q1 as target) would tighten the surprise-weighting interpretation. Whether this changes the Cat 2 yield is genuinely unknown — the dominant signal on FM appears to be class imbalance, not surprise.

These are hypothesis-generating, not pre-registered predictions. Following `[[feedback_research_design]]` and the prior pre-registration failure pattern (`[[project_pre_registration_pattern]]`), I am not pre-committing to which next test produces non-zero Cat 2 or to a direction.
