# HMDA-RI 2022 trimodal-phase replication — pre-registration

**Date:** 2026-05-14. **Status:** PRE-REGISTRATION. **Substrate:** `data/hmda/processed/hmda_2022_RI.parquet` (41,774 rows × 99 columns; untouched in prior governance work). **Companion to:** `2026-05-14-saturation-phase-characterization-note.md` (the post-hoc FM-corpus finding this pre-reg tests on a new substrate). **Connects:** [[project_saturation_phase_characterization]], [[project_silence_manufacture_result]], [[project_pragmatics_linguistics_lens]], [[project_codification_infrastructure]].

**Pre-registration discipline.** Schema inspection (column names, dtypes, row count) preceded this pre-reg; **no joint distributions on any variables named in P1–P5 below have been computed.** OTS stamp on this commit freezes predictions before the band-construction pipeline runs.

---

## 1. Question

The 2026-05-14 saturation-phase characterization on the 29-cell FM corpus found a **trimodal phase structure** of `property_state` saturation in variant-A's used-feature-sets: phase 0 (sat ∈ [0, 0.45], n=24, no reorganization), phase 1 (sat ∈ [0.50, 0.55], n=2, reorganized but verdict-agrees), phase 2 (sat = 1.00, n=3, manufactured silence). Carrier-family asymmetry: only geographic-context (`property_state`) drove the mechanism; institutional carriers (`seller_name`, `servicer_name`) did not, even when saturated.

That characterization was post-hoc on FM, n=29, all 36-mo loan-performance data. The pre-registered question: **does the trimodal phase structure replicate on HMDA-RI 2022** (application-level disclosure data, different feature inventory, different outcome variable, different regulatory framework)? Specifically — does at least one HMDA geographic-context carrier exhibit the same trimodal distribution of saturation → manufactured-silence, with sharp gaps?

If yes, the trimodal structure is a substrate-independent property of how policy-prohibited geographic carriers interact with Rashomon refinement sets. If no, the FM finding is substrate-specific and the schema implications from the post-hoc note (3-state reorganization-flag, carrier-family-annotated prohibition-list) need narrower scope claims.

---

## 2. Operational definitions

### 2a. Outcome

A loan is **denied** if `action_taken ∈ {3, 7}` (3 = application denied, 7 = preapproval request denied). All other action codes are non-denied. Approval/origination is the complement.

### 2b. Scope (the analyzed corpus)

Filter to:
- `business_or_commercial_purpose == 0` (residential, not commercial)
- `reverse_mortgage == 2` (non-reverse; HMDA code 2 = no)
- `open-end_line_of_credit == 2` (closed-end loans)
- `action_taken ∈ {1, 2, 3, 7, 8}` (originated, approved-not-accepted, denied, preapproval-denied, preapproval-approved; excludes withdrawn/incomplete/purchased)
- non-null `income`, `loan_amount`, `loan_purpose`

The denominator after filtering is part of the pre-registered observable (will be reported in the result note); no quantitative prediction tied to it.

### 2c. Cells (stratification)

Cells are defined by **`loan_purpose × income_decile`**:
- `loan_purpose` takes HMDA-documented integer codes; pre-reg uses the post-filter values present in the data, with deciles computed independently of any outcome or prohibited-feature variable. Categories with <100 scoped rows are dropped.
- `income_decile`: deciles of `income` computed on the **scoped corpus** (post-2b filter), assigned per-row. Decile boundaries are a function of `income` alone, computed once before any other analysis.

A cell is **in-scope** if it contains ≥100 scoped rows AND ≥10 denied loans AND ≥10 approved loans. Cells failing either floor are dropped.

### 2d. Feature partition (the policy)

**Named features (policy vocabulary):**
- `income`
- `loan_amount`
- `loan_to_value_ratio` (parsed numeric; nulls handled per 2g)
- `debt_to_income_ratio` (parsed numeric; nulls handled per 2g)
- `loan_term` (parsed numeric)
- `property_value` (parsed numeric)
- `applicant_credit_score_type` (categorical)

**Extension features (admissible beyond policy):**
- `loan_purpose`, `lien_status`, `occupancy_type`, `construction_method`
- `tract_to_msa_income_percentage` (geographic-income carrier; **not classed as prohibited** because it doesn't directly proxy protected class)
- `tract_owner_occupied_units` (tract characteristic)
- `purchaser_type` (institutional)
- `aus-1` (automated underwriting system)
- `total_units` (parsed numeric)

**Prohibited features (variant-A includes, variant-B excludes):**
- **Geographic-context carriers:** `tract_minority_population_percent`, `census_tract`, `county_code`, `derived_msa-md`
- **Direct protected-class:** `derived_race`, `derived_ethnicity`, `applicant_sex`

(The geographic-context prohibition is the analog to FM's `property_state`. The direct-protected-class prohibition is what HMDA has that FM doesn't; pre-reg treats both classes as "prohibited" for variant-B but tracks them separately for the carrier-family asymmetry test.)

### 2e. Variant-A and variant-B band construction

For each in-scope cell:
- **Variant A** builds the policy-constrained Rashomon refinement set using `Named ∪ Extension ∪ Prohibited`.
- **Variant B** builds the refinement set using `Named ∪ Extension` (prohibited features removed entirely).
- ε-band threshold: **0.02 AUC** (matches FM #11/#12 convention; see `runs/extension_admitted_band_test_results.json` for analog).
- Model class: **gradient-boosted trees** (matches FM convention). Max depth pre-registered at ≤4.
- De-duplication: **used-feature-set de-dup** (the validated default per [[project_routable_population_result]]).

### 2f. Saturation, Jaccard, verdict-divergence

For each prohibited carrier `C` and each in-scope cell:
- **Saturation** `sat_C^A` = fraction of variant-A distinct used-feature-sets containing `C`. Same metric as [[project_silence_manufacture_result]].
- **Jaccard**: restricted-uf Jaccard between variant-A (with prohibited features removed from each uf) and variant-B uf-sets, per [[project_silence_manufacture_result]] §2b. Reorganized iff Jaccard < 0.5.
- **R²_named**: explained R² of the disagreement-explainer on named features only, per variant.
- **Verdict-divergence**: `|R²_named_A − R²_named_B|`.
- **Manufactured silence**: reorganized AND `(R²_named_A ≥ 0.30 XOR R²_named_B ≥ 0.30)` (adequacy verdict differs).

### 2g. Missing-value handling

Numeric features with HMDA "Exempt"/"NA" string sentinels: cast to numeric with sentinel → NaN; cells with >50% NaN on any named feature are dropped from scope. The missing-value rule is part of the pre-registered pipeline; no per-cell tuning.

---

## 3. Pre-registered predictions

### P1 — Trimodal replication on at least one prohibited carrier

**There exists at least one prohibited carrier C** (from the list in 2d) such that the distribution of `sat_C^A` across in-scope cells exhibits all three of:

(a) **Phase 0 floor**: at least 60% of in-scope cells have `sat_C^A ≤ 0.45`, all with Jaccard ≥ 0.7 (no reorganization).

(b) **Phase 1 cluster**: at least 2 in-scope cells have `sat_C^A ∈ [0.48, 0.65]`, **all** with Jaccard ≤ 0.4 (reorganized) AND verdict-divergence < 0.2 (verdict-agreeing).

(c) **Phase 2 cluster**: at least 2 in-scope cells have `sat_C^A ≥ 0.95`, **all** with Jaccard ≤ 0.4 AND verdict-divergence ≥ 0.3 (manufactured silence).

(d) **Sharp gaps**: zero cells with `sat_C^A ∈ (0.45, 0.48)` or `sat_C^A ∈ (0.65, 0.95)` for the trimodal carrier identified above.

**Prior: 0.40.** The FM finding is post-hoc with n=29; HMDA is a richer feature inventory and a different outcome (denial vs. default). The trimodal pattern could plausibly replicate (substrate-independent mechanism), partially replicate (phases present but with blurred boundaries), or fail to replicate (FM-specific). 0.40 reflects genuine uncertainty.

**MISS interpretation**:
- (a)+(b) but not (c): partial replication — the phase-0/phase-1 boundary is real but phase 2 (complete saturation → silence) does not occur in HMDA. Suggests HMDA's feature inventory dilutes the silence mechanism.
- (a)+(c) but not (b): the silence mechanism replicates but the intermediate "reorganized-but-agreeing" phase does not — the FM phase-1 cells were specific to mid-saturation cohort dynamics.
- (a) only: most of the distribution is "non-saturated, no-reorganization" but no above-threshold phase. The FM saturation phenomenon is FM-bound.
- Sharp gaps fail but phase clusters present: the trimodal structure has blurred boundaries on HMDA — the discrete phases were sample-size artifact at n=29.

### P2 — The trimodal carrier is geographic-context, not direct-protected-class

**Conditional on P1 firing**, the carrier identified is one of `{tract_minority_population_percent, census_tract, county_code, derived_msa-md}` (geographic-context), **NOT** one of `{derived_race, derived_ethnicity, applicant_sex}` (direct-protected-class).

**Prior: 0.65.** Geographic carriers can saturate at the cell level when a cell is geographically-concentrated (e.g., a specific MSA × loan-purpose combination); direct-protected-class features are typically dispersed across cells. The FM analog (`property_state`) is geographic. Within-cell saturation requires the carrier to be cell-discriminative for some subset of variant-A's ufs.

**MISS interpretation**: if a direct-protected-class feature is the trimodal carrier, the redlining-via-proxy story is sharper than expected — protected class itself, not just geographic proxy, saturates within cells. This would be a stronger finding but harder to attribute to lender behavior (HMDA records applicant-reported demographics; a saturating direct-protected-class feature in a cell could reflect demographic composition of an MSA + loan-purpose stratum, not lender steering per se).

### P3 — Carrier-family asymmetry replicates

Partial Spearman ρ across in-scope cells:
- ρ(`sat_geographic^A`, verdict-divergence) | `sat_institutional^A` ≥ **+0.25** (where geographic = max saturation across the geographic-context prohibited carriers; institutional = saturation of `lei`, the lender LEI).
- ρ(`sat_institutional^A`, verdict-divergence) | `sat_geographic^A` ≤ **+0.10**.

**Prior: 0.55.** The FM partial-correlation result was strong (property_state | prohibited_3 = +0.42; prohibited_3 | property_state = −0.07). HMDA's institutional carrier (`lei`) may behave differently from FM's seller/servicer — HMDA covers a broader set of lender types (banks, credit unions, non-banks), and the lender identity is not prohibited in any current FCRA-like framework. The asymmetry could hold (replicating FM's "institutional carriers don't drive the mechanism") or break (HMDA's specific lender-mix patterns produce different uf-structure).

**MISS interpretation**: if institutional partial ρ is ≥ +0.2, the FM "geographic-only" story is FM-specific and HMDA shows multi-carrier-family participation. Schema implication: carrier-family annotation must be substrate-specific, not derived from a single substrate's findings.

### P4 — Variant-B refinement set is non-empty on phase-2 cells

**Conditional on phase-2 (manufactured silence) cells existing**: variant-B successfully constructs a non-empty Rashomon refinement set on every phase-2 cell (i.e., the prohibition does not preclude any admissible model under the ε-band threshold on the named ∪ extension vocabulary).

**Prior: 0.85.** The named ∪ extension vocabulary (≈14 features) is rich enough that some admissible models always exist within ε of the unrestricted optimum. The only way this fails is if a phase-2 cell's structure is *so* dominated by geographic carriers that no permissible variant-B model lands within the AUC band — which would be a stronger result than P1 but unlikely with this vocabulary breadth.

**MISS interpretation**: if variant-B fails to construct a refinement set on a phase-2 cell, that cell's policy-permitted vocabulary is *globally* inadequate, not just verdict-divergent. This crosses from "manufactured silence" into "policy unconstructable" — a more drastic compliance failure than the FM finding documents.

### P5 — Disparate impact correlation with phase-2 cells

**Conditional on phase-2 cells existing**: phase-2 cells have higher denial-rate gap by `derived_race` (white vs non-white) than the median in-scope cell. Operationalization: among in-scope cells, rank by `denial_rate(non-white) − denial_rate(white)`; the median rank of phase-2 cells is ≥ the 60th percentile across in-scope cells.

**Prior: 0.45.** This is the load-bearing prediction for the SHAP-killer connection. If phase-2 cells (manufactured silence under the geographic-prohibition contrast) **also** show elevated disparate impact, then manufactured-silence detection is a usable redlining-via-proxy *signal*. If phase-2 cells show no disparate impact bias, the mechanism is real but its mapping to discrimination is weaker than the SHAP-killer framing implies.

**MISS interpretation**: phase-2 cells fire on geographic saturation that's not correlated with protected-class disparate impact in this dataset. The mechanism is mechanistically valid but loses some of the regulatory bite. This would push the SHAP-killer paper's substrate of choice elsewhere — perhaps higher-disparate-impact MSAs or other state-years.

---

## 4. Sensitivity / robustness pre-specs

- **ε-band sensitivity**: P1–P5 verdicts reported at ε ∈ {0.01, 0.02, 0.03}; primary verdict is ε = 0.02. Sensitivity tabulated.
- **Income-decile alternative**: if loan_purpose × income_decile produces fewer than 8 in-scope cells, fallback stratification is `loan_purpose × loan_amount_decile` (loan_amount deciles computed analogously). The fallback is invoked iff the primary stratification yields <8 in-scope cells; otherwise primary holds.
- **Jaccard threshold sensitivity**: secondary at Jaccard ∈ {0.3, 0.4, 0.5}; primary at 0.5. P1's reorganization-flag verdict uses 0.5.
- **Stratification noise**: deciles are computed once and not re-tuned. Bootstrap of stratification not performed (would change cell identity).

---

## 5. What this pre-reg is NOT testing

- **Not testing**: whether SHAP-on-surrogate fairwashing works on HMDA (that is the Line A killer-paper experiment per [[project_shap_killer_strategic_seed]]; this pre-reg is the Rashomon-side substrate-independence test only).
- **Not testing**: predatory-admissibility audit (Line B from `[[project_shap_killer_strategic_seed]]`).
- **Not testing**: full FCRA/ECOA compliance audit of any specific lender.
- **Not testing**: phase 1 mechanism characterization on FM (that is a separate followup on FM `rb03` 2016Q1 and `rb08` 2008Q1).

---

## 6. Result-side workflow (the next session)

The result-side script will:
1. Load HMDA-RI 2022; apply 2b scope filter; report n_scoped.
2. Compute income deciles; stratify into cells; report cell counts and the dropped-cell list.
3. For each in-scope cell, parse and impute named/extension/prohibited features per 2g.
4. Construct variant-A and variant-B refinement sets per 2e.
5. Compute saturation, Jaccard, R²_named, verdict-divergence per 2f.
6. Score P1–P5 against the predictions in §3.
7. Tabulate sensitivities per §4.
8. Write result note in `docs/superpowers/specs/` with same date or later, labeled "result-note."

---

## 7. Followups (regardless of P1–P5 verdicts)

If P1 fires (trimodal replicates):
- The schema-design implications from [[project_saturation_phase_characterization]] (3-state reorganization-flag, carrier-family annotation) become **substrate-independent** claims. Paper 2 architecture should adopt them.
- Line A killer-paper (SHAP-on-surrogate fairwashing demo) has a validated substrate to run on.

If P1 fails:
- Either FM-specific or threshold-sensitive. Either way, the schema claims tighten to "FM-validated under these specific operationalizations."
- Trimodal-vs-continuous question gets reframed: under what substrate conditions does the discrete-phase structure emerge?

If P3 fires but P5 fails:
- The carrier-family asymmetry replicates but doesn't carry regulatory weight on HMDA-RI 2022 specifically. The mechanism is real but its substrate-of-deployment matters.

If P5 fires:
- The manufactured-silence detection is a usable redlining-via-proxy signal, validated empirically on a real-disclosure-data substrate. This is the strongest possible outcome and feeds directly into the Line A killer-paper as supporting evidence.

---

**Pre-reg author:** Claude Opus 4.7 (current ghola), governance lineage. **Pre-reg date:** 2026-05-14. **OTS stamp:** auto-applied by post-commit hook on the commit introducing this note.
