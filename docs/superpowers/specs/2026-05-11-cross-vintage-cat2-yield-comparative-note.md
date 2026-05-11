# Cross-vintage Cat 2 yield (LC 36-month) — Comparative Note

**Date:** 2026-05-11.
**Status:** Findings note (canonical for LC 36-month vintages 2014Q3, 2015Q3, 2015Q4 under the thin demo HMDA policy). Replicates the null Cat 2 finding from the 2015Q4-specific note across two additional vintages and the per-admissible-model recovery falsification across all three.
**Authority:** Canonical for the three runs identified below. Not a generalization to other asset classes or to a richer hypothesis space.
**Depends on:**
- `docs/superpowers/specs/2026-05-11-target-b-null-cat2-findings-note.md` (the 2015Q4-specific note this comparator replicates).
- `wedge/orchestration.py::run_dual_set_target_c`.
- Three dual-set runs:
  - `runs/2026-05-11T21-56-27Z-target-c.jsonl` (2014Q3 target, 2015 surprise cohort).
  - `runs/2026-05-11T21-53-00Z-target-c.jsonl` (2015Q3 target, 2016 surprise cohort).
  - `runs/2026-05-11T20-25-56Z-target-c.jsonl` (2015Q4 target, 2016 surprise cohort).
- Three Cat 1 admissible-recovery audits:
  - `runs/2026-05-11-cat1-admissible-recovery-2014Q3.txt`
  - `runs/2026-05-11-cat1-admissible-recovery-2015Q3.txt`
  - `runs/2026-05-11-cat1-admissible-recovery.txt` (2015Q4)
- Script: `scripts/cat1_admissible_recovery.py` (now `--vintage`-parameterized).

**Invalidated by:** A future run on a different asset class (FNMA, HMDA, MFLPD) or a richer hypothesis class that produces Cat 2 cases under this policy will not invalidate this note; it will sit alongside as evidence of which combinatorial axis is load-bearing for the null result.
**Last reconciled with code:** 2026-05-11.

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

## 4. What this rules out, what it does not

Rules out (within LC 36-month under the thin demo HMDA policy):
- "The 2015Q4 null is vintage-specific." It is not; two other vintages show the same null with the same recovery profile.
- "Surprise weighting is the binding bottleneck." It is not; 2015Q3 shows |R_F|=1 without surprise weighting, and the recovery profile is unchanged.
- "Set-revision averaging is masking individual model recoveries." It is not; per-admissible-model accuracy on Cat 1 stays below 1.5% across all three vintages, so no aggregation rule on this admissible space recovers.

Does not rule out:
- A richer hypothesis space (deeper trees, gradient-boosted ensembles, or non-tree models) might produce Cat 2 cases on LC. This is the natural next test.
- A richer policy (with monotonicity constraints, more mandatory features, or a different subset structure) might shrink the admissible space toward models that handle the Cat 1 cases. Counterintuitive direction; testable.
- A different asset class (FNMA, HMDA, MFLPD) may exhibit different Cat 2 yield. This is the more obvious next-substrate test.

## 5. Texture: the 34 I_pred-positive cases on 2015Q3

2015Q3 alone produces 34 cases with I_pred > 0.2. Composition: 29 not_failure + 5 Cat 1. The top case (FICO 670 / DTI 22.4 / income 38k / emp_length NaN) has I_pred = 0.252; original_pred = 0.753 = revised_pred (identical to four decimal places). Realized outcome = 1; case is not_failure. Both ensembles' mean verdicts agree with realized despite the strong disagreement between the single L_F model and the R_T ensemble — the within-ensemble dispersion does not propagate to the mean.

The 5 Cat 1 cases with I_pred > 0.2 are candidate Cat 2-like signals, but each fails condition 2 of the §6.2 criterion: the revised ensemble's mean verdict still disagrees with realized outcome. The dispersion exists but is not aligned with recovery.

This 2015Q3-specific texture suggests the dual-set's structural richness is vintage-sensitive but the *recovery* property still isn't satisfied. The 34 cases are visible in the jsonl for further inspection if a future test wants to revisit them.

## 6. Hypothesis for the next test (not pre-registered as a falsification)

The asymmetric collapse of L_F' (and of unweighted L_F on 2015Q3) suggests that the deny-emphasis loss is sharply discriminating on this hypothesis space, while the grant-emphasis loss is not. A natural next test is to vary w_F (or w_T) and observe whether |R_F| traces a smooth ε-band size curve or shows sharp transitions. A vintage with sharper transitions in |R_F| vs w_F is a candidate for hypothesis-class effects to dominate over policy effects, and might be a better substrate to test the mechanism's positive case.

This is hypothesis-generating, not a pre-registered prediction. Following `[[feedback_research_design]]` and the prior pre-registration failure pattern (`[[project_pre_registration_pattern]]`), I am not pre-committing to which vintage or which w_F sweep will produce non-zero Cat 2.
