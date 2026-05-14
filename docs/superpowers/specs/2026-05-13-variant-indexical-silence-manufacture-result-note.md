# Variant-indexical silence-manufacture across the FM band corpus — result note (#12)

**Date:** 2026-05-13. **Status:** result. **Substrate:** saved JSONs from #11 (`runs/fm_rich_policy_vocab_adequacy_{2018Q1,2016Q1,2008Q1}.json`), 29 analyzed cells with ≥2 distinct used-feature-sets in both variants. **Pre-registration:** `docs/superpowers/specs/2026-05-13-variant-indexical-silence-manufacture-preregistration-note.md` (committed `9dd642b`, OTS-stamped `3a8959f`). **Companion to:** #11 result note §3b (rb05 falsification + reframe) and §7 sibling pre-reg #1 (descriptive variant-indexicality).

---

## Headline

**The manufactured-silence pattern is a small, bounded, rung-3b-specific class — and the reorganization-via-Jaccard discriminator is structurally sharper than the adequacy-verdict that defines silence-manufacture.**

Of 29 analyzed cells across three FM vintages, **5 are reorganized** (P1 HIT at the 15% floor: 17.2%). Of those 5, **3 are manufactured-silence cells** — all on 2016Q1, all rung-3b: rb00, rb05, rb09. **No 4th case beyond what #11 §3b already discussed surfaced** (P4 MISS: 3 vs ≥4). But **2 new reorganized-but-agreeing cells did surface** (2016Q1 rb03 and 2008Q1 rb08), where variant A and variant B build structurally different ε-good bands and yet *the R²_named-≥-0.30 adequacy verdict happens to agree on both variants* (both adequate, both above 0.30). These two cells show that **the reorganization mechanism is more endemic than the manufactured-silence verdict catches** — the indexicality lens discriminates a structural pattern the adequacy threshold doesn't.

**P5 lands clean and strong** (the load-bearing prediction): among the 24 censored cells, **zero** show verdict divergence. The reorganization/censoring split is the right axis for the protocol-mandate claim. Ratio is undefined (∞, the censored divergence rate is exactly 0). **But this is partly artifact of R² distribution** — most censored cells have R²_named > 0.5 in both variants, so the threshold can't separate them by construction. The clean separation IS robust to threshold choice within plausible ranges, but the claim is "the discriminator distinguishes the cells where variants *could* disagree on verdict," not "the discriminator picks out all and only those cells where they *would* disagree under any threshold."

**Scorecard: 4 HITs, 1 MISS, with structurally-informative MISS interpretation.**

---

## 1. Scorecard

| prediction | prior | result | verdict |
|------------|-------|--------|---------|
| P1 — reorganization rate ≥15% of corpus (≥5 cells) | 0.65 | 5/29 = 17.2% | **HIT** at floor |
| P2 — property_state-saturation classifier ≥80% accurate | 0.7 | 100% (29/29) | **HIT (strong)** — but with co-mechanism caveat (§3a) |
| P3 — verdict divergence on reorganized ≥60% | 0.55 | 3/5 = 60% | **HIT at floor** |
| P4 — manufactured-silence count ≥4 | 0.5 | 3 | **MISS** — informative (§3b) |
| P5 — reorg/censored divergence ratio ≥3 | 0.65 | ∞ (cens=0) | **HIT (strong)** — with R²-distribution caveat (§3c) |

**Sensitivity over J thresholds:** primary verdict at J=0.5 is stable across J ∈ {0.4, 0.5, 0.6, 0.7} (5 reorganized cells, 3 manufactured-silence); at J=0.3 the corpus drops to 3 reorganized (rb00, rb05, rb09 — the empty-uf-short-circuit cases) and P1 verdict flips to MISS. **The HIT on P1 is sustained at J ∈ [0.4, 0.7], fails at J=0.3.** Manufactured-silence count is invariant to J (always 3) — the 3 hits are all empty-uf-short-circuit + verdict-differs, immune to Jaccard threshold tuning.

---

## 2. The two new reorganized cells (the scientifically interesting "what surfaced")

### 2a. 2016Q1 rb03

- R²A = 0.365, R²B = 0.778 → both *adequate* under the R²_named ≥ 0.30 threshold → verdict agrees
- property_state-saturation_A = 0.50 (exactly half of variant-A's 4 distinct used-feature-sets use property_state)
- J = 0.333 → reorganized at J_thresh = 0.5 (would be censored at J_thresh = 0.3)
- A_restricted: `{dti, loan_term, num_borrowers}`, `{loan_purpose, ltv, num_borrowers}`, `{loan_purpose, num_borrowers}`, `{loan_term, num_borrowers}` — the half *without* property_state
- B_ufs: 8 distinct, including `{dti, FTHB, loan_purpose, ltv, num_borrowers}`, `{dti, loan_purpose, num_borrowers}`, `{dti, loan_purpose, num_borrowers, property_type}`, `{loan_purpose, ltv, num_borrowers}` — variant B's band reorganizes around DTI + loan_purpose + num_borrowers combinations
- rung classification: None (the cell isn't in any gap class under #11's strict criterion)

**Reading:** variant A's band uses property_state on half its ufs and DTI-combinations on the other half; variant B's band can't use property_state and reorganizes more heavily around DTI. Variant B's R²_named is 0.78 (cleanly adequate) because the DTI-reorganized band is more named-explainable. Variant A's R²_named is only 0.365 (just barely adequate at the 0.30 threshold) because half the ufs use property_state, which the named-only explainer can't reach. **At any adequacy threshold above ~0.45, this would become a manufactured-silence cell** (R²A inadequate, R²B adequate). The reorganization caught a cell where verdict-divergence is *near the threshold but not over it*.

### 2b. 2008Q1 rb08

- R²A = 0.450, R²B = 0.730 → both adequate → verdict agrees
- property_state-saturation_A = 0.55
- J = 0.360 → reorganized
- This is the cell flagged in #11 §3c as "marginal eps-unstable" (gap only at ε=0.05, doesn't count for strict verdict)
- A_restricted: `{cltv, fico}`, `{cltv, fico, original_upb}`, `{dti, fico}`, `{dti, fico, ltv}`, `{dti, fico, num_borrowers}` — FICO-rooted on the non-property_state half
- B_ufs: 24 distinct (large band)
- rung: None (under strict ε=0.02 criterion)

**Reading:** in the 2008Q1 8.5%-default-rate band, property_state carries half of variant A's band structure. Variant B reorganizes around FICO + DTI. The cell didn't make the gap-cell verdict-class because variant A's R²_named (0.45) is above 0.30, but the underlying mechanism is structurally similar to rb09's 3a/3b-mixed pattern — just less extreme. **Suggests the rung-3b class is wider than the strict ε-stable verdict isolates.** A regulator-grade artifact applying the variant-indexicality test would flag rb08 as structurally suspect even though the gap-verdict doesn't catch it.

### 2c. What these two cells tell us

The reorganization mechanism — property_state-carrying half the band's structure under variant A — produces *the same structural pattern* as the 3 manufactured-silence cells, but the R²_named values happen to land both above the 0.30 adequacy threshold. The strict gap-verdict misses these cells; the reorganization discriminator catches them.

**Practical implication for the artifact:** report the (reorganization-flag, verdict-pair) *tuple*, not just the verdict. Two cells with the same verdict ("both adequate") but different reorganization-flags should be treated differently — the reorganized cell is structurally vulnerable to silence-manufacture at threshold-adjacent regulatory or operational decisions, while the censored cell is not.

---

## 3. Per-prediction analysis

### 3a. P2 HIT at 100% — methodological caveat

property_state-saturation_A ≥ 0.50 perfectly classifies the 29 cells into reorganized (5) and censored (24). All 5 reorganized cells have saturation ≥ 0.50; all 24 censored cells have saturation < 0.50. **But this is partially co-mechanistic with the discriminator** — when most of variant-A's ufs use a prohibited carrier, restriction to non-prohibited features drops that carrier from those ufs, which mechanically produces low Jaccard with variant-B's ufs (which never use the prohibited carrier). So P2's 100% accuracy is a strong signal that property_state IS the reorganization driver, but it's *not* an independent confirmation that reorganization is structurally meaningful — it's saying "when variant-A's band is dominated by a prohibited feature, the band restructures under variant B," which is close to tautological.

The independence question is answered by P2-extended (the 3-prohibited-feature saturation): including seller_name and servicer_name in the saturation measure DROPS accuracy from 100% to **72.4%**. This is informative: **property_state is the asymmetric reorganization driver**; seller_name and servicer_name when present in variant-A's ufs do *not* reliably predict reorganization. The mechanism is feature-specific, not just "any prohibited feature."

**Why property_state and not seller/servicer:** property_state captures geography-driven within-band default heterogeneity (FM's geographic concentration in distressed regions during 2008, regional housing-price cycles in 2016) that is *structurally not reducible* to underwriting-vocabulary features. Seller_name and servicer_name capture lender-identity effects that *are partially absorbed* by underwriting-vocabulary features (sellers correlate with FICO/LTV/loan_purpose mix). The asymmetry is itself a finding — rung-3b carriers are heterogeneous in their codification-irreducibility, and property_state sits at the deeply-irreducible end of the spectrum.

### 3b. P4 MISS — the manufactured-silence class is bounded

The 3 manufactured-silence cells are exactly {2016Q1 rb00, 2016Q1 rb05, 2016Q1 rb09} — all on the same vintage, all rung-3b under #11's classification. No additional cell surfaced from 2018Q1 (which has no gap cells) or 2008Q1 (which has rb09 as a gap cell, but rb09 2008Q1 is **censored** under the discriminator with J=0.682, and both variants are inadequate so verdict agrees anyway).

**Why 2008Q1 rb09 is censored despite being a rung-3b gap cell:** variant A's band on 2008Q1 rb09 uses `original_upb` extensively (and original_upb is NOT prohibited in variant B). So restriction to non-prohibited features drops only property_state from the ufs, leaving large overlap with variant B's ufs. The reorganization metric correctly identifies this as "variant B sees most of what variant A sees, just minus property_state" — a censored-difference. And both variants are inadequate (R²A=0.08, R²B=0.26), so the verdict agrees in the "inadequate floor" direction.

**Interpretation:** the manufactured-silence class is **vintage-specific** (only 2016Q1 in this corpus) and **carrier-specific** (only cases where property_state monopolizes variant-A's band, AND variant B's band restructures to find a different-but-still-named-feature-explanation). The 2008Q1 rb09 case fails the second condition — variant B finds no named-feature-explanation either, so both verdicts agree on "inadequate." The 3-cell class is the **expansion-regime rung-3b fingerprint**, not a general phenomenon.

**Paper 2 implication:** the protocol mandate "always report both variants" binds *specifically* on expansion-regime rung-3b cells. In crisis-regime, the carriers are correlated enough across variants that no manufactured-silence opportunity exists. The artifact-design recommendation should be more granular than "always": it should be "always *when the band has rung-3b-irreducible structural carriers*."

### 3c. P5 HIT at ∞ — strong but with R² distribution caveat

Censored cells: 24, R²_named distribution: min 0.076 (2008Q1 rb09), median 0.832, max 0.949. R²_named_B: min 0.264, median 0.829, max 0.940. **Most censored cells are in the prime-band range (R²>0.5 in both variants).** At that R² level, both variants are mechanically adequate by construction, so verdict-divergence is structurally impossible.

The exception — 2008Q1 rb09 censored with R²A=0.08, R²B=0.26, both inadequate — is the only censored cell where the verdict *could* legitimately differ if the threshold were placed differently. At threshold 0.30, both inadequate, verdict agrees. At threshold 0.20, R²A inadequate, R²B inadequate (still agrees). At threshold 0.10, R²A inadequate, R²B adequate (would differ). So even on this near-threshold censored cell, the manufactured-silence pattern is sensitive to where the adequacy threshold is placed.

**Sensitivity to adequacy threshold:**
- At threshold 0.30 (pre-reg primary): P5 ratio = ∞, manufactured silence = 3
- At threshold 0.50: would add 2016Q1 rb03 (R²A=0.365 inadequate, R²B=0.778 adequate, REORGANIZED) and 2008Q1 rb08 (R²A=0.45 inadequate, R²B=0.73 adequate, REORGANIZED) to the manufactured-silence count → 5 manufactured silence cells, all reorganized; P5 ratio still ∞ (no censored cell flips); P1 verdict still HIT
- At threshold 0.10: 2008Q1 rb09 would flip (R²A=0.08 inadequate, R²B=0.26 adequate) → manufactured silence count 4, **AND it's a censored cell** — P5 ratio drops to finite (24 censored, 1 verdict-differing → cens rate = 4.2%; reorg rate = 60% → ratio ≈ 14)

**Conclusion:** P5's clean ∞ is at the primary threshold; the discriminator-quality claim is *robust* to threshold within [0.20, ~0.70] but *breaks* at very low thresholds where censored gap-cells start to disagree on verdict for reasons other than reorganization. The pre-registered threshold 0.30 sits in the robust-range middle. Honest framing: **on the FM substrate at any plausible adequacy threshold, censored cells never disagree on verdict in a way driven by anything other than the same low-R² floor; reorganized cells disagree because the bands have genuinely different named-explainability.**

### 3d. P3 HIT at exact threshold — calibrated landing

3 of 5 reorganized cells differ on verdict (60% exactly). The 2 that don't (rb03, rb08) are the §2 cells just discussed — reorganized but verdict-threshold-adjacent in both variants. P3 was deliberately set at 60% rather than 75% because of these likely-adjacent cases; the prediction held at the floor exactly as the prior anticipated. Calibration sweet spot.

---

## 4. Implications

### 4a. For Paper 2 schema-redesign

Reporting *just* the verdict misses a class of structural reorganization (the rb03/rb08 type) where indexicality is real but the threshold doesn't catch it. The artifact-form for the indexicality lens should be a **(reorganization-flag, verdict-pair)** tuple per cell, computed under the explicit two-variant protocol. The "no manufactured silence" claim binds at the verdict level on 29/29 censored cells, but the "no structural reorganization" claim binds at the discriminator level on only 24/29 cells. The schema needs both layers.

Concretely, the `mandatory_features` slot redesign from #11 §5a (band-level admissibility predicate) is necessary but not sufficient. A complete redesign should add:

1. **Variant-context declaration slot** (the explicit context-of-utterance per [[project_pragmatics_linguistics_lens]]): every band-level adequacy claim is indexed by `(candidate_features_admitted, prohibited_features)`.
2. **Reorganization-flag slot**: paired-variant comparison reporting Jaccard or analogous structural-similarity metric, with a configurable threshold and the empty-uf short-circuit.
3. **Verdict slot**: the existing R²_named adequacy verdict, but interpreted *in the context of the reorganization-flag*: "vocab-adequate under variant A, vocab-adequate under variant B, **reorganized**" is a structurally different verdict than "vocab-adequate under variant A, vocab-adequate under variant B, **censored**."

The first interpretation gets reported as "the band admits two valid stories, both explanatory, but resting on different carrier features — examiner should investigate which deployment context is relevant"; the second is "the band's structure is robust to the prohibition — no examination action needed." The current `mandatory_features` slot collapses both into the same vacuous binary.

### 4b. For Paper 1 (silence-manufacture frame)

The result supports a *qualified* version of the silence-manufacture-as-load-bearing claim:

- **Manufactured silence is a real, structural, falsifiable pattern** — not a frame-deformation imposed on neutral data.
- **It is bounded** — exactly 3 cells in a 29-cell substrate, all in one vintage's rung-3b cells. Not endemic, not arbitrary, not everywhere.
- **It has a mechanism** — property_state-saturated bands under one variant, reorganizing to FICO/DTI/etc.-structured bands under the prohibited-features variant.
- **It is preventable** — the protocol mandate "always report both variants" eliminates the failure mode by construction, but the mandate only carries weight where the structural conditions are met.

The Paper-1 line: *manufactured silence is a structural risk specific to certain regulatory-irreducible carriers; the protocol of always reporting indexical context prevents it where it could occur and is no-cost where it could not.* Crisply: **the indexicality protocol is asymmetric — it's load-bearing on the small minority of cells where structure permits, and vacuous on the majority where structure doesn't. The right artifact-design move is to keep the protocol active on all cells (uniform discipline) but interpret its findings asymmetrically.**

### 4c. For [[project_pragmatics_linguistics_lens]]

The pragmatics seed predicted "constraints want explicit context-of-utterance slots." The result confirms this on the `mandatory_features` slot specifically: the existing slot is *unindexed* (a single feature list, applied uniformly) and consequently *vacuous* on this substrate (#11 §5a). A variant-indexed version (declared candidate-feature-context) would do the diagnostic work the unindexed version cannot. **First empirical confirmation of the pragmatics-as-codification-layer hypothesis on a real substrate.**

The seed's three direct borrows from linguistics map cleanly:
- **Indexicality**: candidate-feature-context is the slot. The 2-variant test is the minimum-viable indexical declaration.
- **Speech-act theory**: "vocab-adequate" as a *performative* commitment to a particular variant context — not a *constative* claim about the world simpliciter.
- **Frame semantics**: the (variant-A, variant-B) pairing is a frame-structure for the adequacy diagnostic.

This is one data point, on one substrate, with one slot. The general claim ("codification artifacts need a pragmatic-annotation layer") would need replication on other slots (`monotonicity:`, `applicable_regime:`, the missing `gates:` slot) and other substrates (LC, HMDA). But the directionality is supported.

---

## 5. Limits

- **One substrate (FM SF).** Whether the reorganization pattern survives LC pricing-space or HMDA replication is an open question. Likely cross-substrate-relevant because property_state-equivalent geographic concentration appears across portfolios, but not testable from this analysis.
- **Two variants only.** The variant-indexicality test is degenerate with only two variant options. A richer test would have multiple prohibition profiles (geography-only, lender-only, loan-size-only) — the result would tell us which carriers are independently codification-irreducible. Pre-reg-worthy followup.
- **Member-weighted Jaccard not feasible on saved data.** The pre-reg flagged member-weighted Jaccard as a sensitivity check; the saved JSONs don't include per-uf member counts (only the deduplicated uf list). The unweighted Jaccard reported here is the only feasible analysis. **A re-run of #11 with per-uf member-count tracking would unblock the sensitivity check**; whether that's worth the compute is a judgment call (the unweighted analysis already separates the corpus cleanly).
- **Adequacy threshold sensitivity demonstrated, not pre-registered.** §3c's threshold analysis is post-hoc exploration of the R²_named-≥-0.30 threshold's robustness, not a pre-registered prediction. Reported as caveat, not as result.
- **The corpus is small (29 cells, 5 reorganized, 3 manufactured silence).** Statistical inference would be over-confident; this is exploratory pattern characterization, not significance testing.
- **No new compute — same data, different analysis.** The findings inherit any structural issues in the saved JSONs. The headline (3 manufactured-silence cells, all 2016Q1 rung-3b) replicates rb05's direct discussion in #11 §3b and is internally consistent; that's the soundness check available without rerunning.

---

## 6. Provenance

- Pre-reg (frozen): `9dd642b` (substantive) / `3a8959f` (OTS).
- Analysis script: `scripts/silence_manufacture_test.py` (committed with this result note).
- Saved output: `runs/silence_manufacture_2026-05-13.json`.
- Result + script commit hash: [TBD] / [TBD] (OTS).

**Followups in priority order:**

1. **Multi-variant indexicality test** — extend from 2 variants (geography-prohibited) to 3-4 (geography-only-prohibited, loan-size-only-prohibited, lender-only-prohibited, full-Eligibility-Matrix variant C from #11 §7 #4). Tests which carriers are independently codification-irreducible. Combines with this result's reorganization machinery; same substrate. ~1-day pre-reg.
2. **LC pricing-space replication** — replicate the variant-indexicality test on the LC pricing-space substrate (where #6/#9 already established within-grade structure). Tests cross-substrate generality of the property_state-equivalent pattern. ~2-day pre-reg + run.
3. **Schema redesign sketch as Paper 2 §X** — draft the (variant-context, reorganization-flag, verdict-pair) tuple-slot schema as a Paper 2 architectural section. Not a pre-reg; a writing task.
4. **Member-weighted Jaccard sensitivity** — re-run #11 with per-uf member-count tracking, repeat this analysis with weighted Jaccard. Lower priority unless the unweighted finding's robustness is challenged.
5. **§7 sibling pre-reg #1 (the descriptive cousin)** — descriptive variant-indexicality (rate of band-reorganization across cells, predictors). Largely subsumed by this adversarial test's per-cell tables; reframe as a Paper-2 figure source rather than a standalone pre-reg.

---

## 7. Headline sentence (one-line claim form)

*On FM SF acquisitions, variant-indexical silence-manufacture is a real, falsifiable, structurally-bounded pattern: 3 of 29 analyzed band-corpus cells (10.3%) admit two valid-but-disagreeing vocab-adequacy verdicts under different candidate-feature contexts; all 3 are 2016Q1 rung-3b cells; the discriminator (restricted-uf Jaccard with empty-uf short-circuit) catches a structurally-similar wider class (5/29, including 2 cells where the verdict-threshold happens to keep both variants on the same side); censored cells show zero verdict-divergence by construction. The protocol "always report both variants" is load-bearing on the small minority where structural conditions support manufactured silence, and no-cost on the majority where they do not.*
