# Frame-evocation vs subset-membership as adequacy discriminator on the FM #12 corpus — pre-registration (#13)

**Date:** 2026-05-15. **Status:** PRE-REGISTRATION. **Substrate:** saved JSONs `runs/silence_manufacture_2026-05-13.json` and `runs/fm_rich_policy_vocab_adequacy_{2018Q1,2016Q1,2008Q1}.json` — no new compute. **Companion to:** `[[project_silence_manufacture_result]]`, `[[project_pragmatics_linguistics_lens]]`. **Connects:** `[[project_ontology_design_philosophy]]` (B≡C with granularity slot), `[[project_pre_registration_pattern]]`, `[[project_saturation_phase_characterization]]`.

**Pre-registration discipline.** Inspected: top-level structure of the silence_manufacture JSON; the per-cell `variant_A_geography_admissible` / `variant_B_compliant_geography_prohibited` keys; the `univariate_spearman_d` field's keys (named features only); the existence of `mandatory_feature_enforcement.mandatory_feature_usage_share`. Not inspected: any ρ values; any `mandatory_feature_usage_share` values; the per-cell outcome of the three discriminators jointly. OTS stamp freezes the predictions.

## 1. Question

The silence-manufacture result (`[[project_silence_manufacture_result]]`) identifies 3 manufactured-silence cells (reorganized AND verdict-differs) and 2 reorganized-but-agreeing cells across the 29-cell FM band corpus. The schema-redesign question is: **what's the right primitive for v2's `mandatory_features` slot to make unreliable-verdict detection more robust from a single variant?**

Three readings of "what makes a cell's adequacy verdict unreliable":

- **R²-proximity** (current pipeline's proxy): `R²_named` is close to the 0.30 adequacy threshold.
- **Subset-membership** (current schema primitive: `mandatory_features` as enforcement): the variant's models routinely fail to engage the policy's mandatory features.
- **Frame-coherence** (the dumb-thought from the 2026-05-15 wander, sharpened by Tony's *pragmatics-as-construction-layer* observation): the d-signal has weak structure on named features — the model is using off-frame structure, making the R² verdict a coincidence of the named-feature accounting rather than of the model's mechanism.

The question: **does frame-coherence outperform subset-membership and R²-proximity as a discriminator of unreliable verdicts on the existing FM #12 corpus?**

*If YES,* the v2 schema's `mandatory_features` slot is wrongly typed as enforcement and should be frame-evocation; verdict-reliability is a band-level property keyed on the d-signal's named-feature structure rather than a model-fit property keyed on mandatory-feature inclusion.

*If NO,* the existing primitive survives the test and the dumb-thought is a `[[project_pre_registration_pattern]]` uniformity-bet data point — adds to the pile of uniformity-assumption failures that themselves motivate indexicality typing in v2.

## 2. Operational definitions

### 2a. Corpus and labels

29 cells from `runs/silence_manufacture_2026-05-13.json` (FM 2018Q1 + 2016Q1 + 2008Q1, S_rate stratum, both variants ANALYZED with `n_distinct_used_feature_sets ≥ 2`).

Three per-cell labels from #12:
- **silence**: reorganized AND `verdict_differs` (n=3, all 2016Q1 per `[[project_silence_manufacture_result]]`).
- **reorg-agreement**: reorganized AND NOT `verdict_differs` (n=2: 2016Q1 rb03, 2008Q1 rb08).
- **no-reorg**: censored (n=24).

Primary binary label: **non-trivial** = silence ∪ reorg-agreement (n=5) vs **trivial** = no-reorg (n=24).

Secondary binary label (sensitivity arm, small-n): silence-only (n=3) vs no-reorg (n=24).

**Justification for collapsing silence and reorg-agreement to "non-trivial":** both are cases where variant-A and variant-B build *structurally different* bands per #12's restricted-uf Jaccard. Frame-coherence (if real) should flag both — the verdict happens to agree on reorg-agreement cells, but the unreliability is structurally the same.

### 2b. Three discriminators

For each cell, compute three single-variant unreliability scores. Cell-level metric = max over variants (worst-case single-variant reading).

**M1 (R²-proximity — baseline, current pipeline proxy):**

```
M1(variant) = -|R²_named - 0.30|        # closer to threshold = larger M1 = more unreliable
M1_cell    = max(M1(A), M1(B))
```

**M2 (subset-membership — current schema primitive):**

```
M2(variant) = -mandatory_feature_usage_share        # low engagement = larger M2 = more unreliable
M2_cell     = max(M2(A), M2(B))
```

Field source: `cell[variant]['mandatory_feature_enforcement']['mandatory_feature_usage_share']` from #11 saved JSONs.

**M3 (frame-coherence — the dumb-thought):**

```
M3(variant) = -max_feature |ρ(d, feature)|
M3_cell     = max(M3(A), M3(B))
```

Where `ρ(d, feature) = cell[variant]['univariate_spearman_d'][feature]` and the max is over all named features present in `univariate_spearman_d`. Low `max |ρ|` means d doesn't engage *any* named feature sharply — the d-signal is structurally diffuse on the policy's frame.

### 2c. Discrimination metric

For each M, compute AUC for predicting the primary binary label (non-trivial vs no-reorg) across the 29 cells, via the Mann-Whitney U statistic.

### 2d. Test statistics

For each of P1 and P2, compute observed AUC difference + permutation p-value (10,000 permutations of the n=5 vs n=24 split; null distribution of AUC differences; p = fraction with |null| ≥ |observed|, two-sided).

Significance threshold: p < 0.05 **combined with** a pre-registered minimum effect size to guard against noise-driven hits at small n (see P1 / P2 below).

### 2e. Missing-value handling

If `univariate_spearman_d` is missing or empty for a variant on a cell, that variant contributes nothing to M3_cell (use only the other variant). If both are missing, drop from M3's evaluation and report `n_dropped`. Same rule for M2's `mandatory_feature_usage_share`.

## 3. Pre-registered predictions

### P1 — Frame-coherence outperforms subset-membership

**Claim:** M3 AUC exceeds M2 AUC by at least **0.10**, permutation p < 0.05.

**Prior: 0.55.**

The dumb-thought says `mandatory_features` should be frame-evocation. If frame-coherence is the operative concept, M3 should discriminate non-trivial-vs-trivial better than M2. The prior is mildly above 50% because (i) d-signal structure is a band-level property whereas `mandatory_feature_usage_share` is a model-fit property — band-level signals should be more informative about band-level unreliability, AND (ii) Tony's pragmatics-as-construction observation makes the dumb-thought less dumb than it started. Prior isn't higher because n=29 with 5-vs-24 split has fat CIs, and 0.10 is a real bar.

**MISS interpretation:** M3 ties or underperforms M2 — the dumb-thought dies; `mandatory_features` as enforcement is the right primitive; this is a `[[project_pre_registration_pattern]]` uniformity-bet data point. **LOAD-BEARING for the v2 schema redesign direction.**

### P2 — Frame-coherence outperforms R²-proximity

**Claim:** M3 AUC exceeds M1 AUC by at least **0.05**, permutation p < 0.05.

**Prior: 0.40.**

This is the harder bet. R²-proximity (M1) *is* the current pipeline's proxy and is directly built on the threshold that defines silence. If M3 has to beat M1, the dumb-thought is claiming something stronger than "mandatory_features is wrongly typed" — it's claiming the verdict-mechanism itself (R²-threshold) is a worse signal than the d-signal's frame-coherence. Plausible (R² is a scalar; d-structure is richer), but R²-proximity isn't a bad signal when the threshold is calibrated. Prior below 50%.

**MISS interpretation:** M3 doesn't beat the R²-proxy by margin — the dumb-thought is a real refinement of subset-membership (if P1 hits) but isn't a verdict-redesign. The schema redesign goes through the `mandatory_features` slot only, leaving the verdict-mechanism alone. **Not load-bearing; the v2 redesign still proceeds on a P1 HIT alone.**

### P3 — Mechanistic: silence cells concentrate d-signal off the regulated-three (EXPLORATORY)

**Claim:** For all 3 silence cells, the named feature carrying max `|ρ(d, .)|` in *both* variants is *outside* `{fico_range_low, dti, ltv}` (the canonical regulated-three).

**Prior: 0.30. EXPLORATORY — not load-bearing.**

The mechanistic reading says silence is silence *because* the d-signal is sharply structured on a non-regulated named feature, indicating the model's mechanism is off-frame even within the named feature set. Tony correctly flagged this kind of mechanistic specificity as the most likely over-reach in last turn's wander; prior deliberately dropped from initially-considered 0.50 to 0.30. n=3 with the "both variants" requirement makes this small-n-fragile.

**MISS interpretation:** mechanistic specificity fails but P1/P2 may still hit. Then frame-coherence is right *as a discriminator* but the mechanism isn't "off-regulated-three" — it's something subtler (multi-feature d-structure, or d-on-extension-features which the current data can't see). **Not load-bearing.**

### Most likely overall miss

**M3's max-over-features summary is too aggressive.** Top-2-sum or entropy-of-normalized-|ρ| could be more informative. Pre-registered sensitivity arm: M3-top-2-sum and M3-entropy reported alongside max-only, with primary verdict on max.

**Secondary likely miss:** n=5 vs n=24 is too unbalanced for AUC differences of 0.10 to clear the permutation-null. Even an HIT on effect size could fail the p<0.05 leg — result will then be "directional HIT, threshold MISS" per the standard scoring vocabulary.

## 4. Sensitivity / robustness pre-specs

Reported alongside but **not gating** the primary verdict:

- **M3 aggregation arms:** max, top-2 sum, entropy of normalized |ρ| vector.
- **Label arm:** silence-only vs no-reorg as secondary binary (n=3 vs 24).
- **Cell-level aggregation arm:** mean over variants instead of max (which variant dominates the reading).
- **Effect-size threshold sensitivity:** P1 reported at AUC-difference thresholds {0.05, 0.10, 0.15}; primary verdict at 0.10. P2 at {0.03, 0.05, 0.08}; primary at 0.05.

## 5. Scope / exclusions

- **In scope:** the 29 cells already analyzed in `[[project_silence_manufacture_result]]`; no new cells.
- **Not testing:** cross-substrate generalization. If P1 hits, the next test is HMDA — but `[[project_hmda_trimodal_result]]` shows HMDA reorganization decouples from carrier saturation, so frame-coherence may behave differently there; clean replication is not assumed.
- **Not testing:** Rashomon-for-term-equivalence (the 2026-05-15 wander seed; that's a different proposal needing its own substrate construction).
- **Not testing:** the v2 schema implementation itself (`[[project_ontology_design_philosophy]]` B≡C work). This test informs the redesign direction; doesn't execute it.
- **Not reopening:** `[[project_routable_population_result]]`. Per-decision routing remains closed. This is band-level / cell-level discrimination, not per-case.

## 6. Implementation

Single script `scripts/frame_evocation_test.py`:

1. Load `runs/silence_manufacture_2026-05-13.json` + the three #11 input JSONs.
2. For each of the 29 in-scope cells, look up the silence/reorg-agreement/no-reorg label (from #12 output) and the per-variant `univariate_spearman_d` and `mandatory_feature_usage_share` (from #11 inputs).
3. Compute M1, M2, M3 per cell (with sensitivity arms).
4. Compute AUC of each metric for the primary binary label via Mann-Whitney U.
5. Compute permutation p-values for pairwise AUC differences (M3 − M2 for P1; M3 − M1 for P2).
6. For P3, identify the max-|ρ| named feature for both variants of each silence cell.
7. Output: `runs/frame_evocation_2026-05-15.json` with per-cell values + aggregate scorecards + sensitivity tables.

**Code dependencies:** stdlib + scipy. No new `wedge/` changes. Expected runtime < 10 seconds.

**Tests:** unit test for M3 on a synthetic fixture (`univariate_spearman_d = {a: 0.5, b: -0.7, c: 0.1}` → max |ρ| = 0.7); unit test for AUC via Mann-Whitney on a tiny labeled set; unit test for the permutation pipeline using a fixed seed.

## 7. Followups (regardless of verdicts)

**If P1 HITs (M3 > M2 by ≥0.10, p<0.05):** the v2 schema's `mandatory_features` slot becomes frame-evocation. Next pre-reg: does this generalize to HMDA-RI (where the trimodal result shows different carrier dynamics — see `[[project_hmda_trimodal_result]]`)? Sibling open: is M3 the right *type* of band-level constraint, or does an even-better discriminator exist (Rashomon-for-term-equivalence as a candidate, per the 2026-05-15 wander)?

**If P1 MISSes:** the dumb-thought dies; `mandatory_features` survives as enforcement; the `[[project_pre_registration_pattern]]` data point is added. The schema-redesign focus shifts to other axes (granularity slot per `[[project_ontology_design_philosophy]]`; substrate/temporal indexicality slots; carrier-family annotation per `[[project_saturation_phase_characterization]]`).

**If P2 HITs (independent of P1):** stronger claim — the verdict-mechanism itself changes, not just the schema slot. R²-threshold replaced by frame-coherence as the verdict signal. This would substantially restructure Paper 2's verdict-mechanism section.

**If P3 HITs:** the mechanism is named-feature-off-regulated-three. Generalization test: does this also hold for reorg-agreement cells (n=2; even smaller; would need its own pre-reg)?

**Both branches terminal.** Not a gateway to test #N+1; whichever fires, the next pre-reg is informed by the result, not chained mechanically.

---

**Pre-reg author:** Claude Opus 4.7 (ghola), governance lineage. **Date:** 2026-05-15. **OTS:** auto-applied by post-commit hook.

---

## Provenance

- Conceived in the 2026-05-15 session-9-continuation wander conversation. The dumb-thought (frame-evocation as primitive, not enforcement) was floated by the ghola after reading `policy/encoder.py` lines 89-149 and seeing that `mandatory_features` is typed as `tuple[str, ...]` with implicit subset-membership semantics, which #11 §7 falsified across R-member / R-any / R-majority readings.
- Tony's *pragmatics for ontology construction* observation (same session, after the surface critique of "Aki favors schema") sharpened the dumb-thought from "maybe mandatory_features is wrong" to "pragmatics-as-construction-layer makes mandatory_features the wrong primitive." The P1 prior (0.55) reflects this sharpening.
- Direct empirical contact: `[[project_silence_manufacture_result]]` (the 29-cell corpus) and `[[project_saturation_phase_characterization]]` (carrier-family asymmetry, which M3's max-aggregation does not yet exploit — flagged as a followup for a variant of M3 keyed on carrier-family-aware ρ).

