# Frame-evocation vs subset-membership as adequacy discriminator — RESULT note (#13)

**Date:** 2026-05-15. **Status:** RESULT. **Pre-reg:** `docs/superpowers/specs/2026-05-15-frame-evocation-preregistration-note.md` (commit `991a2d9`, OTS `f469fcf`). **Output:** `runs/frame_evocation_2026-05-15.json`. **Script:** `scripts/frame_evocation_test.py`.

---

## P-scorecard

| Pred. | Prior | Verdict | Headline |
|---|---|---|---|
| P1 (M3_max > M2_mean by ≥ 0.10 AUC, p < 0.05) | 0.55 | **directional HIT, threshold MISS** | obs_diff = +0.075 (sign correct), below 0.10 bar; p = 0.69. M3 ≈ M2 statistically. |
| P2 (M3_max > M1 by ≥ 0.05 AUC, p < 0.05) | 0.40 | **MISS** | obs_diff = +0.008, p = 0.98. Frame-coherence and R²-proximity essentially tied. |
| P3 (silence cells off regulated-three, both variants) | 0.30 | **MISS** | Variant B uniformly fico-peaked across all 3 silence cells; only 2/3 cells have variant A off-three. |

P-scorecard reading: **3 MISSes, 1 directional**. The dumb-thought-as-strict-outperformer is falsified. Frame-coherence works *as a discriminator* (AUC = 0.967) but does not beat the pre-reg's two named comparators by the pre-registered margins.

## Headline AUCs (primary binary: non-trivial = silence ∪ reorg-agreement, n=5, vs trivial = no-reorg, n=24)

| Discriminator | AUC |
|---|---|
| M1 (R²-proximity, current pipeline) | 0.958 |
| M2_mean (subset-membership, primary) | 0.892 |
| M2_min (sensitivity) | 0.500 |
| M2_n_zero (sensitivity) | 0.950 |
| **M3_max (frame-coherence, primary)** | **0.967** |
| M3_top2 (sensitivity) | 0.967 |
| M3_entropy (sensitivity) | 0.675 |
| M3_max_ext (extension-only, bonus arm) | 0.558 |

**Structural observation: AUC ceiling.** Five of eight discriminators (M1, M2_mean, M2_n_zero, M3_max, M3_top2) cluster at AUC ∈ [0.89, 0.97]. At n=29 with 5 non-trivial cells, the corpus has insufficient resolution to separate them; permutation tests on AUC differences yield p-values that are uniformly large (P1 p=0.69, P2 p=0.98) for the headline pairs. This is the "directional HIT, threshold MISS" failure mode the pre-reg's §3.5 anticipated: even an honest effect-size HIT can fail the p<0.05 leg at this n.

The clear outlier on the *low* side is M2_min (subset-membership-via-worst-feature; AUC = 0.500, no signal); the clear outliers on the *high* side are M3_max and M3_top2 (0.967). The "current pipeline beats one operationalization of frame-coherence but not the other" reading does not hold up — all the live operationalizations co-occupy the same band.

## Pre-reg corrections (at result time)

Two corrections that do NOT change the pre-registered predictions or thresholds; they reflect data-structure realities discovered when implementing the script. Per the template scoring conventions, these go in this subsection of the result note; the OTS-stamped pre-reg is NOT retroactively edited.

1. **`mandatory_feature_usage_share` is a per-feature dict, not a scalar.** The pre-reg §2b wrote `M2(variant) = -mandatory_feature_usage_share` as if the field were a number. Inspection revealed it is a `{feature: share}` map across all named features. The result run aggregated three ways and reported all as sensitivity arms; the *primary* M2 reported above uses **mean over named features** (`M2_mean`), which is the cleanest read of "subset-membership as enforcement" at the cell level. `M2_min` and `M2_n_zero` are reported as sensitivity. P1's primary verdict is on M2_mean. (Reading P1 against the other M2 arms gives different pictures: vs M2_min frame-coherence beats by +0.467 AUC, p=0.0005 — but M2_min is the least-defensible operationalization, since it amplifies a single underrepresented feature into a "ceiling unreliable" reading.)

2. **`univariate_spearman_d[feature]` is a dict with `spearman_rho` inside, not a scalar ρ.** Each cell's `univariate_spearman_d` is `{feature: {spearman_rho, spearman_p, mean_d_top_decile, mean_d_bottom_decile, tail_over_mid}}`. The script extracts `spearman_rho` and applies max-over-|ρ| as the pre-reg specified.

3. **Named-feature filter applied as specified.** `univariate_spearman_d` contains both named AND extension features (e.g., `property_state`, `original_upb`, `seller_name`, `servicer_name`). The pre-reg explicitly scoped M3 to named features only; the script does this. An extension-only bonus arm (`M3_max_ext`) reported alongside — used in P3's bonus reading below — was not pre-registered as a discriminator and is reported as a mechanistic observation, not a P-prediction.

These corrections do not advantage any prediction: M2_mean is a strictly more conservative aggregation than M2_min (lower AUC than M2_min would have been on a hypothetical reading); M3's named-feature scope was specified in the pre-reg.

## Unanticipated mechanistic finding (positive observation, not a P-prediction)

The P3 bonus arm — `max_rho_feature_all` across the full `univariate_spearman_d` including extension features — surfaced a structurally clean asymmetry in the three silence cells:

| Silence cell | Variant A max-|ρ| feature (all-features) | Variant B max-|ρ| feature (all-features) |
|---|---|---|
| 2016Q1 rb00 | **property_state** | fico_range_low |
| 2016Q1 rb05 | first_time_homebuyer | fico_range_low |
| 2016Q1 rb09 | dti | fico_range_low |

The asymmetry is not subtle. **In every silence cell, variant A's d-signal peaks on a non-fico feature; variant B's d-signal uniformly falls back to fico_range_low.** Variant B's structural constraint is that it cannot use `property_state` (geography prohibited), and the band's residual disagreement structure collapses onto FICO when the carrier is removed.

For rb00 this is the silence-manufacture mechanism rendered at the d-signal level: variant A's d-signal peaks *on the prohibited carrier itself*, exactly what the silence-manufacture story (from `[[project_silence_manufacture_result]]`) said was happening at the uf-set level. The d-signal is the carrier's footprint, made visible.

For rb05 and rb09 the carrier is different (first_time_homebuyer and dti respectively) — variant A peaks on a *named* feature, not on an extension feature — but the variant-B-falls-back-to-fico asymmetry is preserved. This is potentially a sharper finding than rb00 alone: silence-manufacture does not require the carrier to be an *extension* feature; it can occur when variant A's d-signal peaks on a named feature that variant B's band-construction routes away from.

This is a **post-hoc observation**, not a tested prediction. It motivates a followup pre-reg: across the full FM #12 corpus, does the all-features-d-signal-peak asymmetry between variants reliably discriminate silence cells from no-reorg cells? Cf. §7 followups.

## P3 detail

The pre-reg's P3 was: "the named feature carrying max |ρ(d, ·)| in *both* variants is *outside* {fico_range_low, dti, ltv}."

Per-cell named-only result:
- 2016Q1 rb00: A = num_borrowers (off-three), B = fico_range_low (in-three) → P3 does not fire.
- 2016Q1 rb05: A = first_time_homebuyer (off-three), B = fico_range_low (in-three) → P3 does not fire.
- 2016Q1 rb09: A = dti (in-three), B = fico_range_low (in-three) → P3 does not fire.

**MISS, but informatively so.** A relaxed reading — "variant A alone is off-regulated-three" — fires for 2 of 3 silence cells (rb00, rb05), which is suggestive but n=3 doesn't sustain inference. The pre-reg's symmetric-across-variants formulation is structurally unable to fire on this corpus because variant B is always fico-pinned.

## What the predictions falsify, and what survives

**Falsified:**
- *Frame-coherence strictly outperforms subset-membership as a discriminator at the pre-registered margin.* This is the load-bearing claim of P1. It does not survive.
- *Frame-coherence strictly outperforms R²-proximity.* This is P2. Decisively does not survive.
- *Silence cells concentrate d-signal off the regulated-three symmetrically across variants.* This is P3. Falsified in its symmetric form.

**Survives (and is sharpened):**
- *Frame-coherence works as a discriminator* (AUC = 0.967 on the primary binary). The dumb-thought isn't wrong about frame-coherence carrying signal; it's wrong about frame-coherence being a strictly better operationalization than the existing subset-membership and R²-proximity primitives at this n.
- *The pragmatics-as-construction layer claim* — independently established by `[[project_silence_manufacture_result]]` and not load-bearing on this pre-reg's outcome. The frame is empirically grounded by silence-manufacture itself, regardless of whether `mandatory_features` is the right slot to re-type.
- *The silence-manufacture mechanism, made visible at the d-signal level.* The variant-A-leans-on-carrier / variant-B-falls-back-to-fico asymmetry across all three silence cells is post-hoc but structurally clean.

## Implications for the v2 schema redesign

Per the pre-reg's P1 MISS interpretation (§3.1 MISS line: "the dumb-thought dies; `mandatory_features` as enforcement is the right primitive; this is a `[[project_pre_registration_pattern]]` uniformity-bet data point"), the schema-redesign focus shifts off `mandatory_features` as the locus of re-typing.

What remains alive:
- **Granularity slot** (`[[project_ontology_design_philosophy]]` today's seed). The B≡C-plus-granularity proposal is independent of frame-evocation and not falsified here.
- **Substrate / temporal indexicality slots**. The HMDA-trimodal failure (`[[project_hmda_trimodal_result]]`) and silence-manufacture (`[[project_silence_manufacture_result]]`) already give empirical motivation; this result adds neither evidence for nor against.
- **Carrier-family annotation** (`[[project_saturation_phase_characterization]]`). The post-hoc observation in §3 above — that variant A's d-signal peaks on the carrier feature in rb00, and on different non-fico features in rb05/rb09 — suggests carrier-family annotation may be more empirically grounded than first appeared. The mechanism is band-level d-signal pinning, not subset-level enforcement failure.

**The structural lesson is the `[[project_pre_registration_pattern]]` lesson, in its now-familiar shape.** Uniformity bet ("one operationalization of mandatory_features strictly outperforms the others") → falsified → the indexed claim survives ("all near-equivalent discriminators cluster at the AUC ceiling for n=29; the question is what *each* of them is operationalizing, not which wins").

## Scope-of-claim tightening

What this result lets us claim, narrowly:
- On the existing FM #12 corpus (n=29 with 5 non-trivial cells), frame-coherence (M3_max), R²-proximity (M1), and subset-membership-mean (M2_mean) and subset-membership-by-zero-count (M2_n_zero) are statistically indistinguishable as single-variant unreliability discriminators.
- Frame-coherence does NOT strictly improve on the existing pipeline's R²-proximity proxy.
- A v2 schema retyping of `mandatory_features` from enforcement to frame-evocation is NOT empirically motivated by this test.

What this result does NOT let us claim:
- Frame-coherence is the *wrong* concept (the AUC is 0.967, not low).
- The pragmatics-as-construction-layer framing is wrong (silence-manufacture grounds it independently).
- Subset-membership is the right primitive (the test only shows it's not worse than frame-coherence at this n; on a larger corpus with more granular labels, the picture could change).
- The v2 schema doesn't need re-typing (other axes — granularity, indexicality, carrier-family — remain open and motivated).

**Corpus-coverage limitation (explicit).** The FM #12 corpus is 3 of 104 available FM vintages (2018Q1, 2016Q1, 2008Q1). The "all near-equivalent discriminators cluster at AUC ceiling" finding is a statement about this corpus's *resolution*, not about the discriminators' equivalence in general — on a larger corpus they could separate cleanly, or fail to separate but for substantively different reasons (e.g., discriminator-dependent sub-populations). Silence-manufacture is localized to 2016Q1 *in our data*, but our data has never looked at the other ~100 quarters. The expansion-regime-fingerprint claim (per `[[project_silence_manufacture_result]]`) is inference from a 3-vintage sample and is conditional on this slice. The variant-A-on-carrier / variant-B-on-fico asymmetry is derived from 3 silence cells; whether it holds on additional silence cells (if they exist in non-2016 vintages) is untested. **The pre-reg's scope was crystal-clear about the 29-cell corpus and is honestly held. Generalization requires a fresh pre-reg on a larger corpus — queued as the top item in §7.**

## Provenance

- Pre-reg: HEAD `991a2d9`, OTS-stamped at `f469fcf`. Predictions frozen before any code touched data; the data-structure surprises documented in §2 (Pre-reg corrections) reflect script-implementation issues, not retroactive prediction-editing.
- Run: `scripts/frame_evocation_test.py` (unit tests pass; permutation tests with n=10,000, seed=20260515 reproducible).
- Output: `runs/frame_evocation_2026-05-15.json` (per-cell scores + aggregate AUCs + permutation results + P3 detail).
- Result note commit: [TBD]. OTS: [TBD].

## Followups (both branches terminal, per pre-reg §7)

**P1 MISS branch fires.** Per pre-reg §7: schema-redesign focus shifts to granularity / indexicality / carrier-family slots. Concretely, in priority order:

1. **Expanded-vintage FM replication (top priority).** The 3-vintage corpus is 3 of 104 available FM quarters. Re-run the H2 discriminator triad on an expanded slice — 5-15 additional vintages spanning regimes (e.g. 2010Q1, 2012Q1, 2014Q3, 2020Q2, 2022Q1) — to address: (a) whether silence-manufacture appears outside 2016Q1 at all; (b) whether the M1/M2/M3 AUC-tie at n=29 breaks on a larger corpus; (c) whether the variant-A-on-carrier asymmetry generalizes or is 2016Q1-specific; (d) whether new silence-cell carrier-families surface. Cost ~12 min FM-load + analysis per added vintage; ~1 hour for +5 vintages, ~3 hours for +15, ~21 hours for all 104. Fresh pre-reg required — predictions need to be re-elicited without conditioning on today's result. This addresses Tony's 2026-05-15 dumb question about pattern-coverage directly.
2. **Carrier-family-aware M3.** The post-hoc finding that variant A's d-signal peaks on different carrier-families across silence cells (property_state, first_time_homebuyer, dti) suggests a per-carrier-family discriminator. Pre-reg-able as a separate test on the existing OR expanded corpus.
3. **Variant-asymmetry-of-d-signal-peak as discriminator.** "Does variant A's max-|ρ| feature differ from variant B's max-|ρ| feature?" is a candidate alternative discriminator. Cheap to test on existing data; not pre-registered here. Strong candidate to bundle into the expanded-vintage pre-reg.
4. **HMDA cross-substrate.** Multi-vintage HMDA replication tests whether the discriminator vocabulary itself transfers. The HMDA-trimodal MISS (`[[project_hmda_trimodal_result]]`) flagged adequacy-threshold transfer as a structural issue; this would be its sibling.

**Branch not taken:** P1 HIT would have routed to "frame-evocation as v2 `mandatory_features` typing"; that route is closed.

## What this result contributes to the Sunday lens-doc

The result is a data point in `working_notes/pragmatics-lens-for-governance-ontology-2026-05-15.md` §5 (Lens applied to the project's own work):
- Adds to the `[[project_pre_registration_pattern]]` uniformity-bet failure record (one more case where the pre-reg's uniformity assumption falls; the indexed claim survives).
- Adds a positive mechanistic observation (variant-A-leans-on-carrier asymmetry at the d-signal level) that strengthens silence-manufacture's mechanism story.
- Removes the "mandatory_features as frame-evocation" claim from §5's open agenda; v2 schema-redesign routes elsewhere.

The lens doc's thesis is not load-bearing on this result. The thesis (pragmatics-as-construction-layer for governance ontologies) was empirically grounded by `[[project_silence_manufacture_result]]` before this test and remains grounded after. What this test was load-bearing on was *one specific schema-redesign route*; that route is closed; the broader lens is unchanged.

---

**Result author:** Claude Opus 4.7 (ghola), governance lineage. **Date:** 2026-05-15. **OTS:** auto-applied by post-commit hook.
