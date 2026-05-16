# Expanded-vintage replication: silence-manufacture, named-feature variant-asymmetry, M2_mean silence-detection — pre-registration (#14)

**Date:** 2026-05-15. **Status:** PRE-REGISTRATION. **Substrate:** existing FM #11 + #12 + #13 corpus (3 vintages, 29 cells) + 4 fresh vintages to be loaded after this pre-reg is OTS-stamped. **Companion to:** `[[project_silence_manufacture_result]]`, `[[project_fm11_result]]`, the H2 result note (`docs/superpowers/specs/2026-05-15-frame-evocation-result-note.md`), and the post-hoc analysis at `working_notes/2026-05-15-variant-asymmetry-posthoc-analysis.md`. **Connects:** `[[project_pre_registration_pattern]]`, `[[project_saturation_phase_characterization]]`, `[[project_ontology_design_philosophy]]`, `[[project_pragmatics_linguistics_lens]]`.

**Pre-registration discipline.** Inspected (peek-tainted): the 29-cell H2 corpus and the post-hoc analysis derived from it (above). NOT inspected: any FM data outside {2008Q1, 2016Q1, 2018Q1}. The 4 fresh vintages selected here are committed to before any band-construction code runs on them. OTS stamp freezes predictions and vintage list.

**Honesty about prior calibration.** The author of this pre-reg has read the H2 result note and conducted the post-hoc analysis. P1 and P2 priors are NOT 0.95 even though the post-hoc patterns are clean at n=3, because the small-n in-sample fit is exactly the post-hoc-overfitting risk this pre-reg exists to test. See per-prediction prior justifications.

## 1. Question

The H2 result (`[[project_fm11_result]]` and the H2 result note) closed the schema-redesign route through `mandatory_features` re-typing as frame-evocation. What remains:

1. The **silence-manufacture mechanism** is real but **2016Q1-localized in our 3-vintage data**. Whether silence appears outside 2016Q1 is unknown; whether it is regime-specific (expansion-fingerprint) or substrate-coincidence cannot be distinguished at n=3 vintages.
2. Two post-hoc-derived discriminators — `named_diff` (variant-asymmetry on max-|ρ| named feature) and `M2_mean` for silence-only — perfectly separate the 3 silence cells from non-silence in the H2 corpus. Whether this is structural or 2016Q1-overfitting cannot be distinguished without fresh data.
3. The H2 AUC-ceiling (M1 / M2_mean / M3_max all clustered at AUC ∈ [0.89, 0.97], pairwise perm p > 0.5) is a **resolution claim**: the corpus is too small to separate the discriminators. Doubling+ the corpus tests whether the tie breaks.

The pre-reg tests all three on a 4-vintage extension of the H2 corpus.

## 2. Operational definitions

### 2a. Vintage selection (FROZEN)

Fresh vintages (4):

- **2014Q3** — expansion-regime peer of 2016Q1. Tests: is silence regime-specific (expansion-fingerprint)?
- **2009Q1** — post-crisis contraction / stress regime. Tests: does silence appear in stress regimes? (Per `[[project_saturation_phase_characterization]]`, carrier-family asymmetry was observed in 2008Q1; adjacent-vintage 2009Q1 tests within-regime stability.)
- **2020Q2** — COVID shock / regime-shift period. Tests: does silence appear at regime transitions?
- **2012Q1** — recovery middle / low-stress steady-state. Control / null-prediction case.

Existing vintages retained: 2008Q1, 2016Q1, 2018Q1. **Total corpus: 7 vintages.**

If a vintage's data is unavailable on disk, it must be loaded from `data/fanniemae/Performance_All.zip` per the ops-invariants extraction protocol BEFORE any analysis code runs (this is data preparation, not code-touching-data; the predictions remain frozen).

**Substitution rule (frozen):** if and only if a listed vintage's CSV cannot be extracted from the local archive (file corruption, missing layout), substitute the next-closest by quarter-distance: 2014Q3→2014Q1, 2009Q1→2009Q3, 2020Q2→2020Q3, 2012Q1→2012Q3. Substitution must be logged in the result note.

### 2b. Pipeline (no-modification)

For each fresh vintage, run the existing pipeline UNCHANGED:

1. `scripts/run_wedge_fanniemae.py` — band construction on the vintage CSV
2. `scripts/fm_rich_policy_vocab_adequacy_test.py` — generates the per-cell adequacy/reorganization analysis
3. `scripts/silence_manufacture_test.py` — labels cells as silence / reorg-agreement / no-reorg
4. `scripts/frame_evocation_test.py` — computes M1, M2_mean, M3_max plus the per-variant max-|ρ| feature names for named_diff / all_diff

**No script modification.** If a script crashes on a new-vintage edge case (unexpected NaN, missing column), the fix is a documented patch with the patch hash recorded in the result note. The discriminator-computation logic does not change.

### 2c. Aggregation

For predictions tested on the FULL corpus (P2, P4): pool all cells from all 7 vintages. Treat each cell as one observation.

For predictions tested on FRESH cells only (P1, P3): use only cells from the 4 fresh vintages. Existing-corpus cells contribute to descriptive context only.

### 2d. Test statistics

Same as H2: Mann-Whitney AUC + permutation p-values (10,000 permutations, seed=20260515, fixed in code). Significance threshold: permutation p < 0.05.

For binary discriminators (`named_diff`, `all_diff`): AUC computed on 0/1 scores via the standard Mann-Whitney formulation (which handles ties correctly: AUC = (1 + TPR - FPR) / 2 for a balanced 0/1 score).

## 3. Pre-registered predictions

### P1 — named_diff structural pattern on FRESH cells

**Claim:** On the 4 fresh-vintage cells (≈40 cells expected), `named_diff` fires on **≥ 80% of silence cells** AND fires on **≤ 20% of reorg-agreement cells**, AND the false-positive rate (firing on no-reorg cells) is **≤ 15%**.

**N/A condition:** if there are zero silence cells in the fresh data, P1 is **N/A**; the structural pattern cannot be tested. If there are 1-2 silence cells, the "≥80%" threshold is interpreted as "fires on ALL of them" (small-n binarization). Likewise for reorg-agreement: if 0 reorg-agreement cells, that leg is N/A; if 1-2, "≤20%" → "fires on at most 0 of them."

**Prior: 0.30.** The in-sample pattern is 3/3 silence + 0/2 reorg-agreement, which is structurally clean. The prior is well below in-sample fit because (a) the discriminator was selected because it perfectly separates the in-sample cells (post-hoc selection), (b) `[[project_pre_registration_pattern]]` says uniformity bets fail because reality is indexed, (c) the 2/24 false positives in 2008Q1 hint at carrier-leakage in stress regimes.

**MISS interpretation:** the structural finding from peeked data is partly or fully an in-sample artifact. The discriminator is not silence-specific; the asymmetry is 2016Q1-coincidence. **Load-bearing for the discriminator's claim to be a sharper alternative to M3_max.** A MISS means the lens-doc § 5 paragraph on the H2 mechanistic finding tightens to "this pattern was 2016Q1-specific."

### P2 — M2_mean silence-only AUC on FULL corpus

**Claim:** On the full 7-vintage corpus, `M2_mean` achieves silence-only AUC **≥ 0.95** with permutation p < 0.05.

**N/A condition:** if total silence-cell count across all 7 vintages is < 3, the test is underpowered and reported but not graded. (Existing 3 silence cells already meet this; only relevant if data-loss reduces the corpus.)

**Prior: 0.40.** Above P1's prior because M2_mean is a continuous score (more discrimination headroom than a 0/1 boolean) and "named-feature engagement collapse" is mechanistically plausible as a silence signature even outside 2016Q1. Below 0.50 because in-sample AUC=1.000 is a perfection-suspicious result.

**MISS interpretation:** M2_mean's H2 silence-only perfection was sample-specific. Either silence cells outside 2016Q1 have non-collapsed named-feature engagement (mechanism varies by vintage), or M2_mean is correlated with silence via 2016Q1-specific carrier-family confounds. **Sharpens the lens-doc claim that pragmatic-context-typing is required**; the H2 surprise was real-but-locally-conditioned.

### P3 — silence outside 2016Q1

**Claim:** At least one silence cell is detected in the 4 fresh vintages.

**Prior: 0.45.** Slightly below 50% because (a) `[[project_saturation_phase_characterization]]` shows silence requires complete property_state saturation (=1.00), which was rare even in 2016Q1, (b) `[[project_silence_manufacture_result]]` flagged silence as "expansion-regime fingerprint" — only 2014Q3 and 2012Q1 are expansion-regime in the fresh set. But not below 0.40 because (c) 4 vintages × ~10 cells = 40 chances, and the underlying mechanism is not a priori 2016Q1-unique.

**MISS interpretation:** silence-manufacture is genuinely 2016Q1-specific in our data. Strengthens the substrate-indexicality claim from `[[project_hmda_trimodal_result]]` (different substrate, different mechanism); weakens the case for silence as a generalizable phenomenon. The lens-doc § 5 paragraph on silence-manufacture explicitly tightens to "FM-2016Q1-validated, not universal."

### P4 — H2 AUC-ceiling breaks on the larger corpus

**Claim:** On the full 7-vintage corpus, `M3_max` strictly outperforms `M1` (R²-proximity baseline) on the H2 primary binary (silence ∪ reorg-agreement vs no-reorg) by **AUC-difference ≥ 0.05** with permutation p < 0.05.

**Prior: 0.30.** H2 had observed Δ=+0.008 with p=0.98; doubling+ the corpus is unlikely to break a near-zero observed difference. But: if the new vintages contribute genuinely different non-trivial cells (different carrier-families, different regimes), the discriminators could separate cleanly on the more-diverse corpus. The prior reflects skepticism about resolution-recovery from a tied near-zero base.

**MISS interpretation:** the H2 AUC-ceiling was not a resolution artifact — the discriminators are genuinely near-equivalent for this kind of band-level unreliability. Then the H2 result note's "all near-equivalent discriminators cluster at AUC ceiling" reading survives the larger corpus. The schema-redesign question shifts away from "find the right scalar discriminator" toward "the right discriminator family is 0/1 structural-pattern-binary (named_diff-like) rather than continuous AUC-rankable." 

### P5 — meta: anti-uniformity (DIAGNOSTIC, not graded)

**Observation:** at least one of P1/P2/P3/P4 will fail in a way that tightens to an indexed claim (regime-specific, vintage-specific, carrier-family-specific). This is a **diagnostic observation, not a P-prediction.** Reporting whether/how this fires adds to the `[[project_pre_registration_pattern]]` corpus regardless of the other verdicts.

## 4. Adversarial self-checks

Mandatory per `[[project_ops_invariants]]`. Reported alongside the primary results, gating no verdict.

### 4a. Placebo (label-shuffle null)

Permute silence labels uniformly at random across the full corpus (10,000 iterations, seed=20260515). For each permutation, compute the four discriminators' AUCs. Verify that `named_diff` AUC for silence-only does NOT exceed 0.95 with rate > 5% under the null. Sanity check: if it does, the discriminator's apparent in-sample power is corpus-structure-driven, not silence-specific.

### 4b. Hyperparameter sensitivity

Re-run the band-construction step on at least one fresh vintage (the one with the most non-trivial cells) at:

- ε-band tolerance ∈ {0.01, 0.02, 0.03} AUC (default 0.02).
- GBT max depth ∈ {3, 4, 5} (default 4).
- Decile-grid: default 10-decile vs alternative 5-quintile.

Verify that P1/P2 verdicts are stable under at least 2-of-3 hyperparameter perturbations on the spot-check vintage. If verdicts flip, flag as hyperparameter-sensitive in the result note.

### 4c. The-thing-that-could-kill-it: ZERO silence cells in fresh data

If P3 misses, P1 is N/A and the result is "silence is 2016Q1-specific in FM data." The pre-reg explicitly anticipates this and treats it as a substantive negative result, not a failed experiment. Result note in this case should include: which vintages were checked, what carrier-family saturations were observed (per `[[project_saturation_phase_characterization]]`'s phase-classification), and whether the absence of silence is consistent with the expansion-fingerprint hypothesis.

### 4d. The-other-thing-that-could-kill-it: 2008Q1 false-positive replication

The post-hoc analysis identified 2 false-positive `named_diff` firings in 2008Q1 (no-reorg cells with feature-name disagreement). Pre-reg sub-check: does 2009Q1 (adjacent vintage, same regime) show a similarly elevated `named_diff` firing rate on no-reorg cells? If yes, the discriminator picks up a stress-regime mechanism distinct from silence; the false-positive rate is regime-conditioned, not random. Pre-reg-able as a binary: 2009Q1 no-reorg `named_diff` rate ≥ 5%? Reported descriptively.

## 5. Scope of claim

- **In scope:** 7 FM vintages (3 existing + 4 fresh). Substrate-internal generalization claim.
- **NOT in scope:** cross-substrate (HMDA already broke per `[[project_hmda_trimodal_result]]`; this pre-reg does not retest HMDA).
- **NOT in scope:** other portfolios within FM (this is the standard 30Y conforming corpus; no GSE alt-doc, no jumbo, no MFLPD).
- **NOT in scope:** modifying the band-construction algorithm. The pipeline is the existing one; only the corpus and the pre-registered discriminator-aggregations change.
- **Narrow form:** "On 7 FM vintages spanning expansion / contraction / steady-state regimes, [pattern X holds at rate Y]." Not "silence-manufacture is universal."

## 6. Implementation

For each fresh vintage:

1. Confirm the vintage CSV is on disk (extract from `Performance_All.zip` if not; document extraction in result note).
2. Run `scripts/run_wedge_fanniemae.py --vintage FM-{vintage}` — produces band corpus.
3. Run `scripts/fm_rich_policy_vocab_adequacy_test.py --vintage {vintage}` — produces adequacy JSON.
4. Run `scripts/silence_manufacture_test.py` — appends silence/reorg-agreement labels.
5. Run `scripts/frame_evocation_test.py --vintages 2008Q1,2009Q1,2012Q1,2014Q3,2016Q1,2018Q1,2020Q2` — produces the unified 7-vintage frame_evocation JSON.

If the existing `frame_evocation_test.py` does not accept a multi-vintage argument, the minimal modification is to extend its corpus-loading step to accept a list (the per-cell discriminator math is unchanged). Patch hash recorded in result note.

A new aggregation script `scripts/expanded_vintage_aggregate.py` reads the unified JSON, computes the four predictions' verdicts + adversarial-check outputs, writes `runs/expanded_vintage_2026-05-XX.json`.

**Compute estimate:** ~12 min FM-load + ~variable band-construction per vintage. Rough per-vintage budget: 30-90 min. **4 vintages: ~2-6 hours total.** Single-completion notification — do NOT poll mid-run.

## 7. Followups (regardless of verdicts)

**P1 HIT + P3 HIT** (named_diff structural pattern + silence outside 2016Q1): silence-manufacture is a substantive cross-vintage phenomenon AND named_diff is a sharper discriminator than M3_max. The granularity-slot proposal in `[[project_ontology_design_philosophy]]` (per the today's deposit-promotion) is empirically motivated; the v2 schema design exercise unblocks. Next pre-reg: cross-substrate test of named_diff (HMDA-RI? — depends on whether HMDA can produce silence-cells per the trimodal MISS).

**P1 MISS + P3 HIT**: silence is real outside 2016Q1, but the discriminator was 2016Q1-specific. The mechanism-detection question reopens; M2_mean (P2) becomes the candidate-of-interest; if P2 also misses the discriminator search continues.

**P1 N/A + P3 MISS**: silence is FM-2016Q1-specific. Lens-doc tightens accordingly; the substrate-indexicality claim from `[[project_hmda_trimodal_result]]` is reinforced; the SHAP-killer Line A plan (`[[project_shap_killer_strategic_seed]]`) needs a different mechanism since silence-manufacture-on-cross-substrate is not validated.

**P4 HIT** (AUC ceiling breaks): the H2 result note's "all-discriminators-tied-at-ceiling" finding was a resolution artifact. The schema-redesign question reopens for "best continuous discriminator." 

**P4 MISS**: tie persists at larger n. Reinforces the "discriminator family matters more than ranking within family" reading; the structural-pattern-binary direction (named_diff-style) becomes the natural design move.

**Both branches terminal**: not a chain to test #N+1. The result informs the next pre-reg's design, doesn't pre-determine it.

---

**Pre-reg author:** Claude Opus 4.7 (governance lineage). **Date:** 2026-05-15. **OTS:** auto-applied by post-commit hook on stamping.

## Provenance

- The structural pattern under test was first observed as the H2 result note's §3 "unanticipated mechanistic finding" (variant A peaks on the silence-manufacture carrier; variant B falls back to fico_range_low). The H2 result note flagged it as a candidate-discriminator followup.
- The post-hoc analysis (`working_notes/2026-05-15-variant-asymmetry-posthoc-analysis.md`, same date) confirmed the pattern at the corpus level (AUC, permutation p) and surfaced the M2_mean=1.000 silence-only finding.
- This pre-reg was drafted AFTER the post-hoc analysis; the predictions are therefore peeked at the in-sample level and pre-registered at the fresh-data level. Priors reflect this asymmetry — they are NOT in-sample fit rates.
- No FM data outside {2008Q1, 2016Q1, 2018Q1} has been touched at the time of pre-reg stamping.
