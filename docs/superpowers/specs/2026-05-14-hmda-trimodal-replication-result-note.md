# HMDA-RI 2022 trimodal-phase replication — result note

**Date:** 2026-05-14. **Status:** RESULT. **Substrate:** `data/hmda/processed/hmda_2022_RI.parquet` (41,774 rows × 99 cols; 25,014 scoped; 4,382 denied / 20,632 approved). **Pre-registration:** `2026-05-14-hmda-trimodal-replication-preregistration-note.md` (commit `97fcd6f`, OTS `32ed3be`). **Result-side script:** `scripts/hmda_trimodal_replication.py`. **Result JSON:** `runs/hmda_trimodal_replication_2026-05-14.json`. **Connects:** [[project_saturation_phase_characterization]], [[project_silence_manufacture_result]], [[project_pragmatics_linguistics_lens]], [[project_hmda_trimodal_prereg]], [[project_shap_killer_strategic_seed]].

---

## Headline

The trimodal phase structure of [[project_saturation_phase_characterization]] does **not** replicate on HMDA-RI 2022. The four-part P-scorecard fires **0 of 5 HITs, 3 N/A** (P2/P4/P5 conditional on P1, and P1 misses): the geographic saturation distribution on HMDA is *diffuse*, not trimodal-with-gaps, and no cell satisfies the manufactured-silence criteria on any carrier. Two structural reasons drive the falsification — (i) a `lp1_dec1` outlier cell at geographic saturation 0.80, squarely inside the FM gap-zone (0.65, 0.95), and (ii) an adequacy-threshold collision: HMDA's harder-to-explain disagreement keeps most cells "both inadequate", structurally preventing verdict divergence ≥ 0.30. The carrier-family asymmetry (P3) is directionally preserved — geographic partial ρ on verdict-divergence is **+0.42** (FM had +0.42) — but the institutional partial ρ is **+0.23** on HMDA (FM was −0.07), so the clean "geographic-only" reading does *not* survive the substrate change.

## P-scorecard

| Pred. | Prior | Verdict | Headline |
|---|---|---|---|
| P1 trimodal replication on at least one prohibited carrier | 0.40 | **MISS (all 8 carriers)** | no carrier shows the (a)+(b)+(c)+(d) joint structure |
| P2 trimodal carrier is geographic-context, not direct | 0.65 | N/A | conditional on P1 firing |
| P3 carrier-family asymmetry geographic vs institutional (lei) | 0.55 | **MISS (partial)** | geographic partial ρ=+0.42 ≥ 0.25 ✓; institutional partial ρ=+0.23 > 0.10 ✗ |
| P4 variant-B non-empty on phase-2 cells | 0.85 | N/A | no phase-2 cells |
| P5 phase-2 cells show elevated disparate impact | 0.45 | N/A | no phase-2 cells |

Three of five predictions are **strict MISS** in the sense that the binary HIT/MISS criterion fires negative; two are N/A because they were conditional on P1.

---

## Pre-reg corrections (typos / leaks caught during result-side execution)

Three corrections were applied at the result-side pipeline. Predictions, priors, and scoring thresholds are unchanged. The corrections are documented for auditability against the pre-reg stamp.

1. **Scope-filter code typo.** Pre-reg §2b stipulates `business_or_commercial_purpose == 0` (residential). HMDA's encoding is `1 = yes`, `2 = no`; the data contain no code `0` (only values `{2, 1, 1111}`). Honoring the intent ("residential, not commercial"), the result-side filter uses `== 2`.

2. **Model-class language.** Pre-reg §2e says "gradient-boosted trees max depth 4 (matches FM convention)". Actual FM #11/#12 convention is *depth-≤3 CART* with `max_subset_size=7` (lossless: depth-3 binary trees branch on at most 7 distinct features). Honoring "matches FM convention", the result uses `depths=(1,2,3)`, `leaf_mins=(25,50,100)`. `max_subset_size` was reduced from lossless 7 to **3** as a deliberate compute restriction (HMDA's wider candidate vocabulary makes C(22,7)=170 k subsets-per-cell intractable; on the 29 analyzable cells the de-duplicated bands are 2–25 used-feature-sets, suggesting most discoverable members lie in subsets of size ≤3 — see §3.6 for a sensitivity note).

3. **Feature-partition leak (the one that mattered).** Pre-reg §2d listed `purchaser_type` as an extension feature. HMDA encodes `purchaser_type == 0` as "not applicable (loan denied or not sold)"; **100 % of denied loans in the corpus carry code 0**, while approved loans spread across codes 0–72. A probe before the full run confirmed `purchaser_type` saturating every variant-A and variant-B used-feature-set — it acts as the label re-encoded. Honoring "application-time features only" (the rationale stated for excluding `interest_rate`, `rate_spread`, etc.), `purchaser_type` is **dropped** from the extension list.

A fourth observation, retained but documented: `derived_msa-md` is degenerate on the RI single-state slice (99.2 % of scoped rows are Providence-Warwick MSA `39300`). It carries no within-cell signal and was dropped from the prohibited-geographic candidate set. This is a substrate-of-choice consequence, not a pre-reg error; the RI slice was selected for tractable file size.

---

## 1. Corpus & cells

- **Raw:** 41,774 × 99. **Scoped:** 25,014 (4,382 denied, 20,632 approved). **Denial rate:** 17.5 %.
- **Action codes present:** `{1, 3}` only (the FFIEC download was pre-filtered to `actions_taken=1,3`). Pre-reg's wider `{1,2,3,7,8}` set intersects to `{1,3}`.
- **Stratification:** `loan_purpose × income_decile`. **In-scope cells:** 43 (≥100 scoped, ≥10 denied, ≥10 approved). **Analyzed (band-plural):** 29. **Skipped:** 14 (mainly `lp2`/`lp4` cells of n=85-160, where `leaf_min=(25,50,100)` constraints prevent ≥2 distinct-uf band members; plus two `lp31`/`lp32` cells where the band was singular). The primary stratification yielded > 8 in-scope cells, so the loan_amount fallback was not invoked.
- **Geographic bucketing:** `census_tract` (244 unique) → top-7 + `__other__`; `lei` (335 unique) → top-7 + `__other__`.

## 2. Band-construction parameters

| Parameter | Value |
|---|---|
| ε (AUC) | 0.02 (primary) |
| ε arm | {0.01, 0.02, 0.03} (recorded in JSON; primary verdict at 0.02) |
| Jaccard primary | 0.5 |
| Jaccard arm | {0.3, 0.4, 0.5} |
| Depths | (1, 2, 3) |
| Leaf-mins | (25, 50, 100) |
| `max_subset_size` (primary) | 3 |
| Monotonicity | empty (no HMDA-policy YAML; pre-reg did not require) |
| De-dup | used-feature-set (highest-holdout-AUC representative) |
| Adequacy threshold (R²_named) | 0.30 |
| Disagreement explainer | depth-3 regression CART, leaf-min 50, 5-fold CV |

## 3. Per-prediction verdicts

### 3.1 P1 — Trimodal replication (MISS on every carrier)

For each prohibited carrier `C`, P1 requires (a) ≥60 % of in-scope cells with `sat_C ≤ 0.45` and all Jaccard ≥ 0.7, (b) ≥2 cells in `[0.48, 0.65]` reorganized + verdict-agreeing, (c) ≥2 cells with `sat_C ≥ 0.95` reorganized + verdict-divergent (manufactured silence), and (d) zero cells in `(0.45, 0.48)` or `(0.65, 0.95)`.

| Carrier | n | Phase-0 in range | Phase-1 in range | Phase-2 in range | (a) | (b) | (c) | (d) | P1 |
|---|---|---|---|---|---|---|---|---|---|
| `tract_minority_population_percent` | 29 | 27 | 1 | 0 | ✗ | ✗ | ✗ | ✗ | MISS |
| `census_tract` | 29 | 29 | 0 | 0 | ✗ | ✗ | ✗ | ✓ | MISS |
| `county_code` | 29 | 29 | 0 | 0 | ✗ | ✗ | ✗ | ✓ | MISS |
| `derived_race` | 29 | 27 | 1 | 1 | ✗ | ✗ | ✗ | ✓ | MISS |
| `derived_ethnicity` | 29 | 28 | 1 | 0 | ✗ | ✗ | ✗ | ✓ | MISS |
| `applicant_sex` | 29 | 29 | 0 | 0 | ✗ | ✗ | ✗ | ✓ | MISS |
| `__family_geographic` | 29 | 27 | 1 | 0 | ✗ | ✗ | ✗ | **✗** | MISS |
| `__family_direct` | 29 | 24 | 2 | 1 | ✗ | ✗ | ✗ | ✗ | MISS |

Two structural reasons drive the universal MISS:

**(i) The phase-0 floor (a) fails everywhere** because the cells with `sat ≤ 0.45` are not uniformly "phase-0 by Jaccard". Several mid-saturation cells (`lp1_dec1`, `lp1_dec8`, `lp32_dec5`, etc.) are *reorganized* (Jaccard < 0.7) at low or mid geographic saturation, which violates the pre-reg's "all phase-0 cells with Jaccard ≥ 0.7" requirement. Reorganization on HMDA is **not** tied to the prohibited-carrier saturation level. (Compare FM where the 24 phase-0 cells all had Jaccard ≈ 1.0.)

**(ii) The phase-2 cluster (c) fails because no cell satisfies the manufactured-silence joint criteria.** The closest single cell is `lp31_dec3` (refinance, decile 3, n=278): `derived_race` saturation **1.00**, Jaccard **0.00**, but verdict-divergence **0.095** — well below the 0.30 silence threshold. Both variants land at R²_named ≈ 0 (`R²_A = −0.07`, `R²_B = 0.025`); the adequacy verdicts agree (both `inadequate`) even though the band reorganizes completely. This is **FM-phase-1-shaped geometry occurring at FM-phase-2-level saturation**, an interesting hybrid that the pre-reg's discrete-phase taxonomy does not name.

**(iii) The sharp-gaps clause (d) fails on the geographic family** because `lp1_dec1` (home-purchase, decile 1, n=1026) shows `__family_geographic` saturation **0.80** — squarely inside the FM gap-zone (0.65, 0.95). Geographic saturation on HMDA is *diffuse*, not concentrated at the trimodal vertices.

### 3.2 P2 — N/A

P1 didn't fire, so P2 (conditional on P1) has no applicable verdict. As a directional read (no scoring weight), the two carriers that came closest to a phase-2 cell are `derived_race` (one cell, sat=1.0) and `__family_direct` (one cell). Geographic carriers had no cell at sat ≥ 0.95. If we relaxed the silence threshold from vd ≥ 0.30 to vd ≥ 0.05 (a far weaker bar), the directional answer would point to **direct-protected-class**, not geographic — the *opposite* of the pre-reg's 0.65-prior expectation.

### 3.3 P3 — Carrier-family asymmetry: directional HIT, threshold MISS

Across 28 analyzable cells with usable verdict-divergence:

| Statistic | Value | FM benchmark | Pre-reg threshold | Pass |
|---|---|---|---|---|
| ρ(geographic, vd) marginal | **+0.424** | +0.585 | – | – |
| ρ(institutional/lei, vd) marginal | **+0.245** | +0.450 | – | – |
| ρ(geographic, vd) ∣ institutional | **+0.417** | +0.424 | ≥ 0.25 | ✓ |
| ρ(institutional/lei, vd) ∣ geographic | **+0.231** | −0.074 | ≤ 0.10 | **✗** |

The geographic-family partial correlation **replicates FM almost exactly** (HMDA +0.42 vs FM +0.42). But the institutional-family partial correlation is **non-trivially positive** on HMDA (+0.23 vs FM's −0.07), so the *clean* asymmetry of the FM finding breaks. The institutional carrier (`lei`) does carry independent signal on HMDA — visible directly in `lp1_dec4` (lei sat=1.00, J=1.0 no reorg), `lp32_dec5` (lei sat=0.57, J=0.38 reorg, vd=0.22), `lp32_dec6` (lei sat=1.00). The lender-LEI substrate dynamics here (broader institution mix: banks + credit unions + non-banks, in a small market) differ from the seller/servicer dynamics in FM.

**P3 is the load-bearing residual finding.** Geographic does dominate (the partial-ρ asymmetry is +0.42 vs +0.23, still substantial), but the FM-2018Q1+2016Q1+2008Q1 "geographic-only" mechanism is **not** a universal feature of policy-constrained Rashomon refinement. Carrier-family annotation must be substrate-indexed.

### 3.4 P4 / P5 — N/A

No phase-2 cells ⇒ both predictions are inapplicable. The pre-reg's "load-bearing for SHAP-killer Line A" cell-supply doesn't materialize on this substrate. Two implications:

- **For Line A** (retrospective SHAP-killer on HMDA-RI 2022): manufactured-silence-via-prohibition is not visible in this substrate; the Line A argument would need either (i) a different substrate (a multi-state HMDA slice with richer MSA / county variation, or a portfolio with documented vintage-specific policy variants), or (ii) a different mechanism than the FM trimodal one (e.g., variant-pair shopping at the model-class level rather than carrier-saturation).
- **For schema design** (Paper 2 / `[[project_pragmatics_linguistics_lens]]`): the three-state reorganization-flag claim from [[project_saturation_phase_characterization]] does *not* extend to HMDA cleanly. The space wants finer-grained annotation: at minimum, *(sat-level, J-level, vd-level)* as separate axes, not collapsed into a 3-state enum.

### 3.5 Sensitivity arms (recorded in result JSON; not re-run as a second pipeline)

ε-band and Jaccard-threshold sensitivity arms are recorded in `runs/hmda_trimodal_replication_2026-05-14.json` (the `eps_arm`, `j_arm` fields). For the primary ε=0.02 and J-primary=0.5 the verdicts above hold. The phase-2 cluster does not appear at ε=0.01 either; with ε=0.03 the band widens, plausibly producing more reorganized cells but no additional sat≥0.95 cells (the carriers that don't saturate at 0.02 don't suddenly saturate at 0.03). Jaccard sensitivity is irrelevant given zero cells satisfy the joint criteria at any J threshold.

### 3.6 `max_subset_size=3` restriction sensitivity (informal)

The probe at `max_subset_size=4` on `lp31_dec3` (the most-reorganized cell) returned 2 distinct ufs in A and 6 in B — within an order of magnitude of the `max_subset_size=3` result (2 in A, 7 in B). The verdict (J=0.00, vd≈0.07-0.10, both-inadequate) is identical. The restriction lowers the granularity of saturation (4-uf cells have sat values in `{0/4, 1/4, 2/4, 3/4, 4/4}` ⇒ minimum gap 0.25), but does *not* produce the missing trimodal structure. Cells with high uf-counts (`lp1_dec1` at 5/25, `lp1_dec3` at 16/11, `lp1_dec4` at 15/10) have finer granularity yet still show diffuse-not-trimodal saturation.

---

## 4. Discussion

### 4.1 What this falsifies

The substrate-independence claim from [[project_saturation_phase_characterization]] (n=29, three FM vintages, all 36-mo loan-performance data) does **not** survive its first independent test. The trimodal phase structure with sharp gaps was, on the most charitable reading, an FM-corpus-specific pattern. The phase-2 (manufactured silence) cell count drops from 3/29 on FM to 0/29 on HMDA-RI 2022.

This is the **pre-registered failure pattern** ([[project_pre_registration_pattern]]) firing again: a pre-registered prediction that assumed cross-substrate uniformity, when the actual mechanism is substrate-modulated. Tony's "model heterogeneity explicitly next time" guidance applies — a better-shaped Paper 2 schema would have priors at the carrier-and-substrate level, not the carrier level.

### 4.2 What survives

- **The carrier-family-asymmetry** *directionally*. Geographic prohibition does drive more verdict-divergence than institutional, by a factor of ~2 (+0.42 vs +0.23 partial ρ). This holds on both FM and HMDA, with different magnitudes.
- **Reorganization-without-silence** as a distinct phenomenon. FM phase 1 (n=2: sat ≈ 0.5, J ≈ 0.33, vd small) reappears on HMDA, but at *different* sat levels (e.g., `lp31_dec3` at sat=1.00 race, J=0.00, vd=0.10). The phenomenon is real; the trimodal-discreteness was the over-claim.
- **The variant-indexicality finding** ([[project_silence_manufacture_result]]). HMDA reinforces — *strongly* — that "vocab adequacy" is variant-indexed and substrate-indexed. R²_named distributions on HMDA are dramatically lower than on FM (most cells "both inadequate"), so the same R² ≥ 0.30 adequacy threshold produces different scoring physics. The Paper 2 schema needs `(variant-context, substrate-context, adequacy-threshold)` as a tuple, not a singleton.

### 4.3 Two mechanistic candidates for why HMDA differs

1. **Outcome timing.** Denial is an application-time 0/1 decision; default is a 36-month loan-performance outcome. The features that drive denial are the lender's application-screen inputs (LTV, DTI, credit-score-model, AUS); the features that drive default are post-origination borrower behavior (interacting with property/state economics over time). The vocabularies don't have to overlap — and the FM saturation-of-property_state may be picking up *state-level economic-cycle exposure during the loan term*, which has no HMDA-application-time analog.

2. **Geographic-cardinality scale.** FM's `property_state` is 50 levels with substantial within-state variation; HMDA-RI's `property_state` is degenerate (one state) and `census_tract` is bucketed to 7 levels for tractability. Saturation can't reach 1.00 unless the band's depth-3 trees can split on the carrier in every model — which is easy when the carrier has many levels and substantial variance in outcome. With 7 bucketed levels, even strongly-discriminative carriers may not appear in *every* tree.

Either or both mechanisms could explain the substrate gap. Distinguishing them would require running the same pipeline on (a) a multi-state HMDA slice (where geographic cardinality is comparable to FM), and (b) FM with denial-analog outcomes (e.g., the FM Loan Application Register, where it exists) — both substantial followups.

### 4.4 Implication for [[project_shap_killer_strategic_seed]] Line A

The retrospective-SHAP-killer paper proposed HMDA-RI 2022 as a candidate substrate for demonstrating fairwashing via surrogate distillation, with manufactured-silence-via-prohibition as a signal. **That substrate doesn't supply the signal.** Line A needs either a richer HMDA slice (multi-state, multi-vintage), or a different mechanism (variant-pair-shopping at the codification step, rather than at the prediction step). The strategic conditional from the seed note (Olorin-alignment binding; substrate is downstream-choice) means this re-routing has low cost — but the *recipe-form constructive proof* the seed proposed needs a different demonstration vehicle.

---

## 5. Followups

1. **Multi-state HMDA replication.** Re-run on a HMDA slice with ≥10 states + 1 year (e.g., New England states 2022). Tests mechanistic candidate (2): whether geographic-cardinality scaling restores the trimodal structure.
2. **Cross-vintage HMDA.** Re-run on HMDA 2020 / 2021 / 2022 / 2023 RI. Tests whether the diffuse-saturation pattern is vintage-stable or vintage-modulated.
3. **`lp1_dec1` and `lp31_dec3` deep-dive (in-substrate).** Two cells in this corpus show the FM mechanism's *fragments* — `lp1_dec1` has geographic sat 0.80 + J=0.11 (reorganized at near-phase-2 saturation, verdict-agree); `lp31_dec3` has direct-class sat 1.00 + J=0.00 (full saturation + complete reorganization, verdict-agree-by-floor). Characterize what made these two cells "almost-silent" — was it the borrower-mix, the lender-mix, or the cell stratification choice?
4. **Adequacy-threshold sensitivity per substrate.** The R²_named ≥ 0.30 threshold was set by [[project_fm11_result]]. On HMDA most cells fall below it. Re-do the silence-manufacture analysis with the adequacy threshold set at the *substrate-median* R²_named — does that re-introduce phase-2 cells? This is a substrate-pragmatic adjustment, similar to [[project_pragmatics_linguistics_lens]] §3-borrow on indexicality.
5. **Paper 2 schema revision.** The 3-state reorganization-flag claim from [[project_saturation_phase_characterization]] tightens to "FM-substrate-validated 3-state structure; not universally a discrete enum across substrates". Replace with `(sat, J, vd, R²_named-floor)` continuous tuple, annotated by substrate-context.

---

**Result author:** Claude Opus 4.7 (ghola; governance lineage). **Run date:** 2026-05-14. **Wall time:** 1217s (20m17s) on 29 analyzable cells. **HEAD (substantive):** TBD on commit. **HEAD (OTS stamp):** TBD on commit.
