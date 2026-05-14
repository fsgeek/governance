# Variant-indexical silence-manufacture across the FM band corpus — pre-registration (#12)

**Date:** 2026-05-13. **Status:** pre-registration. **Substrate:** saved JSONs from #11 (`runs/fm_rich_policy_vocab_adequacy_{2018Q1,2016Q1,2008Q1}.json`) — no new compute. **Companion to:** `2026-05-13-fm-rich-policy-vocab-adequacy-result-note.md` §3b (the rb05 falsification + reframe) and §7 sibling pre-reg #1 (variant-indexicality). **Pragmatics seed:** [[project_pragmatics_linguistics_lens]] — codification artifacts must declare their context-of-utterance. **Distinction from §7 #1:** §7 #1 is the *descriptive* version (how much band reorganization exists, what predicts it). This pre-reg is the *adversarial* version (how often does single-variant verdict reporting produce a biased adequacy claim, i.e. manufactured silence). The two share substrate and indexicality machinery but ask different questions; this one is sharper on the artifact-design lever.

---

## 1. Question

The rb05 2016Q1 finding (#11 §3b) shows variant-A and variant-B construct **structurally different ε-good bands** on the same cell, each producing an internally-correct vocab-adequacy verdict that *disagrees* with the other (variant-A: R²_named=0.21 → inadequate; variant-B: R²_named=0.69 → adequate). A deployment running only one variant would ratify whichever conclusion the variant supports — a silence-manufacture mechanism that's invisible from inside any single variant.

The question: **is rb05 a unicum, or is variant-driven verdict divergence systematic enough across the band corpus that a single-variant reporting protocol is structurally unreliable?**

---

## 2. Definitions (operational)

### 2a. The two kinds of A↔B difference

- **Censored difference**: variant-B's band is what variant-A's band would look like if you couldn't see the prohibited carriers. Same structural skeleton, variant-B just can't name some of variant-A's features. Verdict differences here are *honest in the prohibition's own terms* — the prohibition does what it says.
- **Reorganized difference**: variant-A and variant-B construct *structurally different* ε-good bands keyed on different non-prohibited features. The cell admits both as ε-good; choice of variant is choice of which valid story to tell. Verdict differences here are *indexical* — both are correct in their context, neither is privileged, and reporting one without the other is silence-manufacture.

### 2b. The discriminator: restricted-uf Jaccard

For each cell where both variants are ANALYZED with `n_distinct_used_feature_sets ≥ 2`:

1. Let **`prohibited_features`** = {features in variant-A's `candidate_extension`} \ {features in variant-B's `candidate_extension`}. On the #11 substrate: `{property_state, seller_name, servicer_name, msa}` (variant B keeps `original_upb`).
2. For each variant-A used-feature-set `uf_A`, compute the **restricted** set `r(uf_A) = uf_A \ prohibited_features`. Note: some `r(uf_A)` may be the empty set `∅` (variant-A uf used *only* prohibited features).
3. `A_restricted` = the multiset `{r(uf_A) : uf_A in A_ufs}`, deduplicated to a set-of-frozensets.
4. `B_set` = the variant-B used-feature-sets, set-of-frozensets.
5. **Jaccard** `J = |A_restricted ∩ B_set| / |A_restricted ∪ B_set|` over the set-of-frozensets.

### 2c. Reorganization classification

A cell is **reorganized** if either:
- (i) `J < J_thresh`, OR
- (ii) `∅ ∈ A_restricted` (at least one variant-A uf used *only* prohibited features — variant-B literally cannot represent that uf's structure).

Otherwise the cell is **censored**.

**Pre-registered J_thresh = 0.5.** Sensitivity analysis at `J_thresh ∈ {0.3, 0.4, 0.5, 0.6, 0.7}` reported alongside; the verdict on each P-prediction is the J_thresh=0.5 value, with sensitivity tabulated.

### 2d. Adequacy verdict (per variant)

A variant is **vocab-adequate** on a cell iff `R²_named ≥ 0.30`. Otherwise **vocab-inadequate**. (Matches #11's gap criterion; `dR²_ext ≥ 0.15` is *not* required here because we are asking about the adequacy-verdict a single-variant artifact would report, not about the gap-recurs verdict for a full P1-style test.)

### 2e. Manufactured-silence cell

A cell is a **manufactured-silence cell** iff it is *reorganized* AND its variant-A and variant-B adequacy verdicts *differ*.

---

## 3. Pre-registered predictions

Corpus: **29 analyzed cells** (3 vintages × 9-10 rate-bands minus a few non-ANALYZED cells; all with ≥2 distinct ufs in both variants — confirmed by direct inspection of the saved JSONs prior to freezing). All J/verdict computations on saved data.

### P1 — Reorganization is non-rare

**Reorganized cell rate ≥ 15% of the 29-cell corpus** (i.e. ≥ 5 reorganized cells) at J_thresh = 0.5.

**Prior: 0.65.** The known reorganized cases from #11 §3b are rb05 2016Q1 (the explicit example), and very likely rb00 2016Q1 + rb09 2016Q1 + rb09 2008Q1 (all property_state-saturated under variant A). That's 4. P1 requires the corpus to surface ≥1 *additional* cell beyond what §3b discusses. The 25 prime/mid-band cells are mostly FICO-rooted and likely *censored* (variant A's FICO-based ufs survive restriction). But "mostly" admits exceptions.

**MISS interpretation:** if reorganization is ≤4 (just the §3b-known cases), it's a rare edge phenomenon — the protocol-mandate framing weakens to "this happens occasionally, document it." HIT interpretation: a non-trivial fraction of the band corpus admits multiple valid stories under different variants.

### P2 — Reorganization is predictable from variant-A property_state-saturation

**Define property_state-saturation rate** on a cell = fraction of variant-A `distinct_used_feature_sets` containing `property_state`. **Cells with saturation ≥ 0.50 are reorganized; cells with saturation < 0.50 are censored.** Predict classification accuracy ≥ 80% across the 29-cell corpus.

**Prior: 0.7.** property_state-saturation is the most direct mechanism by which restriction forces reorganization (when most of variant-A's bands hinge on a prohibited feature, variant-B *must* reorganize). But there may be other reorganization paths (seller/servicer saturation, or original_upb-driven structure that variant-B still admits but reorganizes around). Sensitivity to including `seller_name`-saturation pre-registered.

**MISS interpretation:** if classification is poor, reorganization happens for reasons beyond property_state — design space for the diagnostic is wider than the §3b case suggests.

### P3 — On reorganized cells, verdict divergence is the rule, not the exception

**Among reorganized cells, the variant-A and variant-B adequacy verdicts differ on ≥ 60% of cells.**

**Prior: 0.55.** Reorganization is *structural*; verdict is *predictive-explanatory* (R²_named on the disagreement explainer). They could in principle decouple — a band that restructures but produces similar R²_named values would be a reorganized-but-agreeing cell. The known cases split: rb05 differs (0.21 vs 0.69), rb00 2016Q1 differs (0.04 vs 0.77), rb09 2016Q1 differs (0.02 vs 0.74), **rb09 2008Q1 agrees** (0.08 vs 0.26 — both inadequate). 3 of 4 known cases differ, but rb09 2008Q1 shows the agreement branch is real.

**MISS interpretation:** if reorganization frequently produces *agreeing* verdicts, the indexicality lens isn't carving nature at the joint we hoped — verdict differences track something other than band-reorganization structure.

### P4 — Manufactured-silence cells are not a single-case phenomenon

**The corpus contains ≥ 4 manufactured-silence cells** (reorganized AND verdict-differing).

**Prior: 0.5.** The 3 known cases (rb05, rb00 2016Q1, rb09 2016Q1) put the floor at 3. P4 requires the analysis to surface ≥1 cell not already discussed in #11 §3b — a real test of "is rb05 a unicum or part of a class."

**MISS interpretation:** if exactly 3 (the known cases), the manufactured-silence pattern is the gap-cells' fingerprint, not a broader phenomenon — the protocol-mandate claim is narrower (binds on rung-3b cells, not on the general band corpus).

### P5 — Reorganized cells are over-represented among silence-manufacture cells, vs censored cells

**Verdict-divergence rate among *reorganized* cells is at least 3× the verdict-divergence rate among *censored* cells.**

**Prior: 0.65.** This is the prediction that *tests whether the discriminator (reorganization-via-Jaccard) is the right axis*. If censored cells also show frequent verdict divergence, then the Jaccard discriminator isn't picking up the right structural signal — manufactured silence happens for reasons orthogonal to reorganization. If censored cells reliably *agree* on verdict (because they're "the same band, viewed with/without prohibited features"), then reorganization IS the diagnostic axis and the protocol-mandate claim sharpens.

**This is the load-bearing prediction for the artifact-design lever.** P1-P4 measure phenomena; P5 measures whether reorganization is the right *concept* to base a protocol on.

**MISS interpretation:** the protocol-design recommendation ("always report both variants") is *underdetermined* by reorganization-vs-censoring — the manufactured-silence rate doesn't track the reorganization/censoring split. We'd need a different discriminator.

### Most likely overall miss

**The Jaccard metric is wrong.** Set-of-frozensets Jaccard on used-feature-sets weights each unique uf equally regardless of how many band members use it. A variant-A uf used by 50 of 60 band members and a variant-A uf used by 1 of 60 count equally in the Jaccard numerator. A weighted version (each uf weighted by member fraction) would better track "what does the band actually look like." Sensitivity check: re-run with member-weighted Jaccard pre-registered as an alternative, with the verdict re-tabulated.

**Secondary likely miss:** the property_state-saturation operationalization in P2 may be too narrow — seller/servicer saturation can also drive reorganization (per §3b's rb05 ufs which include `servicer_name`). The sensitivity to {property_state, seller_name, servicer_name}-or-saturation pre-registered.

---

## 4. Scope and exclusions

- **In scope:** 29 cells with ANALYZED verdict and `n_distinct_used_feature_sets ≥ 2` in both variants.
- **Out of scope:** cells where either variant has `n_distinct_used_feature_sets < 2` (no meaningful reorganization question to ask). On #11's substrate, this excludes 1 cell (2016Q1 rb00 in variant A has only 3 distinct ufs but ≥2, so it's in; cells where the band collapses to a single uf would be out but none of the analyzed cells does this).
- **Not tested:** the consensus P(default|x) functional-dependence reading from #11 §5a (band-level admissibility predicate). That's a *different* schema-redesign direction — it asks "does the band's consensus depend on each mandatory feature non-trivially," which I now think doesn't separately advance the science (the depth-3 / leaf_min ≥ 25 mechanism makes it mechanical, per [calibrated critique in the conversation that produced this pre-reg]). This pre-reg replaces that direction.
- **Not extended to other vintages or substrates.** Whatever is found here is FM-specific; LC pricing-space replication is a separate piece of work and would need its own pre-reg.

---

## 5. Implementation

Single script `scripts/silence_manufacture_test.py`:

1. Load the three #11 JSONs.
2. For each cell × variant, extract `distinct_used_feature_sets`, `R²_named`, `n_distinct_used_feature_sets`, `candidate_named`, `candidate_extension`, `plural`, `R²_all`, `dR²_ext`.
3. Compute `prohibited_features` per cell (it should be uniform — `{property_state, seller_name, servicer_name, msa}` — but compute defensively).
4. Compute `A_restricted`, `B_set`, Jaccard at all five J_thresh values.
5. Classify each cell as reorganized (per J_thresh=0.5) or censored.
6. Compute verdict-pair per cell.
7. Aggregate: P1 reorganization rate, P2 classification accuracy, P3 verdict-divergence rate on reorganized, P4 manufactured-silence count, P5 reorganization-vs-censoring divergence ratio.
8. Output: `runs/silence_manufacture_2026-05-13.json` with all per-cell data + aggregate scorecards.

**Code dependencies:** stdlib only (json, pathlib, collections). No new wedge/ changes. No new compute. Expected runtime < 1 second.

**Tests:** add a unit test for the Jaccard discriminator on a synthetic fixture (variant-A ufs = `[{a,p}, {b,p}]`, prohibited = `{p}` → `A_restricted = {{a}, {b}}`; variant-B ufs = `[{a}, {c}]` → `J = 1/3`). Also a test for the `∅ ∈ A_restricted` short-circuit.

---

## 6. After

1. **Commit this pre-reg.** OTS-stamp.
2. **Write the analysis script + tests.** Commit.
3. **Run the script.** Output JSON.
4. **Write the result note** `docs/superpowers/specs/2026-05-13-variant-indexical-silence-manufacture-result-note.md` — P1-P5 scorecard, sensitivity tables on J_thresh and on member-weighted Jaccard, per-cell table, mechanism reading.
5. **OTS-stamp the result.**
6. **Update MEMORY** with the outcome and the artifact-design implications.

**Estimated effort:** ~0.5 day total. Saved-data analysis only.

---

## 7. What this would and would not tell us

**WOULD tell us:**
- Whether rb05 is a unicum or a class.
- Whether reorganization (defined via restricted-uf Jaccard) is the right structural discriminator for manufactured-silence verdicts.
- Whether a protocol mandate of "report both variants" is *necessary* on the FM substrate or *aesthetic* (i.e., would have caught rb05 only because it was already the one we knew about).
- Empirical input for the schema-redesign discussion in Paper 2 — specifically, what an indexical declaration slot should look like and why it's load-bearing.

**WOULD NOT tell us:**
- Whether this generalizes past FM SF. The discriminator might index FM-specific feature structure (property_state-driven heterogeneity is partly an FM phenomenon — LC sub-grade or HMDA might reorganize differently).
- Whether reorganization correlates with rung classification or other characterizations.
- Whether the *consensus-function* admissibility predicate (#11 §5a's "P(default|x) depends non-trivially on each mandatory feature") would do better as a schema redesign — that's a different test (likely mechanical for the depth-3 reasons given above, but the actual demonstration is pending).
- Whether the per-decision routing arc is reopened. **It is not. This test is purely about tier-level observability and the protocol for reporting it.** [[project_routable_population_result]] remains terminal.

---

## 8. Provenance

- Conceived in the 2026-05-13 session-9 conversation (the lineage's calibrated-critique exchange that demoted a less-surprising R-pragmatic proposal and re-shaped to silence-manufacture).
- The rb05 finding that motivated this pre-reg is in `2026-05-13-fm-rich-policy-vocab-adequacy-result-note.md` §3b (committed `e6b8778`, OTS `997da60`).
- The §7 sibling pre-reg #1 in that result note is the descriptive cousin to this adversarial test; this one DOES NOT replace it (the two complement; §7 #1 catalogs reorganization, this one tests verdict-bias).
- Commit (pre-reg, this file): [TBD] / OTS [TBD].
