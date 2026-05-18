# Expanded-vintage replication (#14) — result note (PARTIAL)

**Date:** 2026-05-18. **Status:** PARTIAL RESULT (2 of 4 fresh vintages completed; 2 failed). **Pre-registration:** `docs/superpowers/specs/2026-05-15-expanded-vintage-replication-preregistration-note.md` (commit `97fcd6f` per session anchor; OTS `f091480` per path-doc §3 Q5). **Substrate:** FM #11 + #12 + #13 existing corpus (3 vintages: 2008Q1, 2016Q1, 2018Q1) + 4 fresh vintages requested (2009Q1, 2014Q3, 2020Q2, 2012Q1). **Connects:** [[project_saturation_phase_characterization]], [[project_silence_manufacture_result]], [[project_hmda_trimodal_result]], [[project_pragmatics_linguistics_lens]], [[project_pre_registration_pattern]].

---

## Headline

P3 (silence outside 2016Q1) HITs decisively on the partial fresh corpus: **8 new silence cells** across 2009Q1 (2) and 2014Q3 (6) — far beyond the pre-reg's "at least one" threshold, with prior 0.45. The silence-manufacture phenomenon is FM-substrate-general within the existing test apparatus, not 2016Q1-specific. **But three load-bearing methodological findings emerge alongside the P3 verdict, two of which falsify earlier claims:**

1. **The trimodal saturation phase characterization is empirically falsified on the expanded corpus.** Silence cells now appear at property_state saturation values {0.00, 0.20, 0.40, 0.42, 0.50, 0.56, 1.00, 1.00} — distributed, not bimodal-at-{0, 1}. The "phase 2 = 1.00 = manufactured silence; phase 0–1 = no silence" structure of [[project_saturation_phase_characterization]] is a 3-vintage 29-cell artifact and does not survive at n=83 cells.

2. **The original silence-manufacture test was stratum-scoped without declaration.** `scripts/silence_manufacture_test.py` line 315 reads `cells = d['strata']['S_rate']['cells']` — only the rate-bucket stratum, not the loan-level-pricing-adjustment (LLPA) stratum. 7 of the 8 new silence cells live in the LLPA stratum the original test never saw. The "bounded to 3 cells" finding had a hidden scope qualifier.

3. **A Mechanism-A / Mechanism-B distinction the prior work did not see.** The silence label fires on two structurally distinct patterns: (A) variant A genuinely engages prohibited features (p_sat or p3_sat > 0) and named-R² collapses when they are restricted in variant B (canonical silence-manufacture); (B) variant A engages no prohibited features at all (p3_sat = 0) but the band is still less named-coherent than B's. 10 of 11 expanded-corpus silence cells are Mechanism-A (9 geographic-carrier, 1 institutional-only); 1 (2014Q3/S_rate/rb03) is Mechanism-B.

P1, P2, and P4 are not yet tested — `scripts/frame_evocation_test.py` has not been re-run on the expanded corpus.

## Partial completion

The pre-reg specified 4 fresh vintages. Status from `runs/expanded-vintage-logs/`:

| Vintage | Final status | Notes |
|---|---|---|
| 2014Q3 | exited 0 at 2026-05-16T21:09:42Z | completed normally after one restart (PID 353419) |
| 2009Q1 | exited 0 at 2026-05-18T00:48:48Z | completed normally; ~47-hour wall time (engineering bottleneck per path-doc Q5) |
| 2020Q2 | exited 1 at 2026-05-18T00:55:04Z | failed twice; cause not investigated in this note |
| 2012Q1 | exited 137 at 2026-05-18T01:12:24Z | OOM-killed |

The 2 completed fresh vintages bracket two distinct regimes: 2009Q1 (post-crisis stress), 2014Q3 (expansion). The "expansion-regime fingerprint" reading of silence from [[project_silence_manufacture_result]] is testable on this partial corpus and is **falsified** (silence appears in stress regime 2009Q1; see below).

## P-scorecard (partial)

| Pred. | Prior | Verdict | Headline |
|---|---|---|---|
| P1 named_diff structural pattern on fresh cells | 0.30 | **NOT YET TESTED** | requires `frame_evocation_test.py` re-run on expanded corpus |
| P2 M2_mean silence-only AUC ≥ 0.95 on full corpus | 0.40 | NOT YET TESTED | same dependency |
| P3 silence cell outside 2016Q1 in fresh data | 0.45 | **HIT (8 cells in 2 fresh vintages)** | 2 in 2009Q1, 6 in 2014Q3 |
| P4 AUC ceiling breaks on M3_max vs M1 | 0.30 | NOT YET TESTED | same dependency |
| P5 diagnostic: anti-uniformity | n/a | **HIT (multi-axis)** | failures of uniformity surfaced on stratum (P3 vintage non-uniformity is unsurprising; carrier-set non-uniformity is the new one — see §3) |

**P3 HIT is the only stamped verdict landed.** It alone is sufficient to retire the "silence is 2016Q1-specific" framing.

---

## 1. Distribution-of-silence finding (P3 detail and the trimodal falsification)

The expanded corpus (n=83 in-scope cells across 5 vintages, all strata) yields the following property_state saturation distribution by reorganization status:

| Phase band | n no-reorg | n reorg-agreement | n silence |
|---|---|---|---|
| Phase 0 [0, 0.45) | 61 | 4 | **5** |
| Phase 1 [0.45, 0.55] | 1 | 3 | 1 |
| Gap [0.55, 1.00) | 1 | 1 | 1 |
| Phase 2 = 1.00 | 0 | 1 | 4 |

The trimodal-with-gaps structure of [[project_saturation_phase_characterization]] was: phase 0 = no-reorg only; phase 1 = reorg-agreement only; phase 2 = silence only, with empty bands between. **The empty bands are no longer empty on n=83.** Phase 0 contains 5 silence cells (was 0); the "gap" between phase 1 and phase 2 contains 1 silence + 1 reorg-agreement (was empty); phase 2 still contains silence preferentially but also contains 1 reorg-agreement (the "carrier-saturated but doesn't induce reorganization" cell at p_sat=1.00 that the 2026-05-14 characterization noted as institutional).

The full per-cell breakdown for silence cells is:

| Vintage | Cell | p_sat | p3_sat | Jaccard | R²_A | R²_B | Mechanism |
|---|---|---|---|---|---|---|---|
| 2009Q1 | S_llpa/llpa_2x3 | 0.42 | 1.00 | 0.04 | 0.15 | 0.41 | A_geo |
| 2009Q1 | S_llpa/llpa_7x0 | 0.40 | 0.80 | 0.08 | 0.25 | 0.64 | A_geo |
| 2014Q3 | S_rate/rb03 | 0.00 | 0.00 | 0.04 | 0.25 | 0.92 | **B** |
| 2014Q3 | S_llpa/llpa_0x3 | 0.00 | 1.00 | 0.08 | 0.04 | 0.36 | A_inst |
| 2014Q3 | S_llpa/llpa_2x6 | 0.56 | 0.89 | 0.08 | 0.26 | 0.35 | A_geo |
| 2014Q3 | S_llpa/llpa_3x3 | 0.50 | 0.64 | 0.29 | 0.27 | 0.65 | A_geo |
| 2014Q3 | S_llpa/llpa_7x2 | 0.20 | 1.00 | 0.29 | 0.28 | 0.59 | A_geo |
| 2014Q3 | S_llpa/llpa_7x3 | 1.00 | 1.00 | 0.00 | 0.03 | 0.91 | A_geo |
| 2016Q1 | S_rate/rb00 | 1.00 | 1.00 | 0.00 | 0.04 | 0.77 | A_geo |
| 2016Q1 | S_rate/rb05 | 1.00 | 1.00 | 0.00 | 0.21 | 0.69 | A_geo |
| 2016Q1 | S_rate/rb09 | 1.00 | 1.00 | 0.00 | 0.02 | 0.74 | A_geo |

The mechanism classification (defined in §3 below) reveals:

- 9 cells are **A_geo** (variant A actually uses geographic carrier; restricting it tanks named-R²) — the canonical pattern.
- 1 cell is **A_inst** (institutional carriers seller/servicer fully present, no geographic) — the carrier-family expansion.
- 1 cell is **B** (no prohibited-feature engagement in variant A whatsoever; silence label fires by R²-asymmetry alone) — the previously-unsurfaced mechanism.

## 2. Stratum-scope finding (the methodology silenced its own findings by omission)

The original silence-manufacture test (`scripts/silence_manufacture_test.py`, executed 2026-05-13) read only `S_rate` cells:

```python
cells = d["strata"]["S_rate"]["cells"]  # line 315
```

This was a defensible scope choice when written (the rate-bucket stratum was the established analytical surface for 2008Q1/2016Q1/2018Q1, all of which had only S_rate populated). It was not declared as an indexical scope choice, and it did not propagate to a corpus check when the expanded vintages added the much-richer S_llpa stratum (2009Q1: 19 LLPA cells; 2014Q3: 21 LLPA cells; neither vintage in the original 3).

**Of the 8 new silence cells, 7 live in S_llpa and would have been invisible to a re-run of the original test against the expanded corpus.** Only 2014Q3/S_rate/rb03 would have been found by a vintages-only extension.

This is the cleanest instance in the program's record of the recursive-silence reading articulated for HMDA: the methodology silenced findings by an undeclared scope choice, just as bank policy can silence findings by undeclared feature-omission. The cure is the same — declare scope explicitly per artifact.

## 3. Mechanism-A vs Mechanism-B (a new distinction the test conflates)

The silence test labels a cell `manufactured_silence = is_reorganized_primary AND verdict_differs`, where:

- `is_reorganized_primary = (Jaccard(A_restricted, B) < 0.5) OR (empty frozenset ∈ A_restricted)`
- `verdict_differs = (adequacy(R²_A) ≠ adequacy(R²_B))` at threshold 0.30

This signature catches two structurally distinct phenomena. Concrete contrast on the expanded corpus:

**Canonical (Mechanism-A):** 2014Q3/S_llpa/llpa_7x3. Variant A has 12 of 12 used-feature-sets containing property_state (p_sat=1.00, p3_sat=1.00). When variant B prohibits geographic+institutional features, B's bands reorganize entirely onto fico-centric ufs. R²_A=0.03, R²_B=0.91. Restricting the prohibited features collapses named-feature engagement on A. This is what the 2026-05-13 silence-manufacture pre-reg called silence-manufacture.

**Anomalous (Mechanism-B):** 2014Q3/S_rate/rb03. Variant A has 3 used-feature-sets, all using only `{cltv, loan_purpose, num_borrowers, ltv}` — **no prohibited feature engagement whatsoever** (p_sat=0.00, p3_sat=0.00). Variant B has 54 ufs all anchored on fico_range_low. R²_A=0.25, R²_B=0.92. Restricting prohibited features in B *could not have caused* the asymmetry (A doesn't use them). The asymmetry arises from somewhere else — likely an artifact of which extension features each variant's candidate set admitted (A's cand_ext was `{property_state, original_upb, seller_name, servicer_name}`; B's was `{original_upb}`) and how the band-construction algorithm's depth-3 candidate-search converged differently on the two extension menus.

The test as-built cannot distinguish A from B. Both fire the silence label. This matters because:

- The silence-manufacture story for regulator/Tay audiences depends on Mechanism-A's causal narrative (the prohibited feature is doing the work; restricting it manifests reorganization). Mechanism-B has no such narrative.
- The named_diff and M2_mean post-hoc discriminators from the 2026-05-15 pre-reg were calibrated on cells that turn out (in retrospect) to all be Mechanism-A. Whether they generalize to a corpus containing both is the live P1 question.

**Carrier-set expansion within Mechanism-A.** Of the 10 Mechanism-A cells, 9 use property_state (the carrier the 2026-05-14 characterization named). 1 cell (2014Q3/S_llpa/llpa_0x3) uses only institutional carriers — p_sat=0.00, p3_sat=1.00, meaning every uf in A contains seller_name or servicer_name but none contain property_state. The 2026-05-14 characterization said institutional carriers saturate to 0.67 without inducing reorganization; on the expanded corpus, this is no longer absolute. The "property_state is the asymmetric reorganization driver" claim tightens to "geographic is the dominant carrier; institutional can be a sole carrier in expansion-regime LLPA cells."

## 4. Anti-uniformity (P5 diagnostic detail)

[[project_pre_registration_pattern]] predicts: "pre-registered hypotheses with uniformity assumptions consistently fail because reality is indexed." The expanded-vintage pre-reg's P5 was explicitly diagnostic for this. Where uniformity assumptions held vs failed:

- **Held:** "P3 will be ≥1 cell of silence in fresh data" (a non-uniformity claim, not a uniformity claim — held loudly, 8 cells)
- **Failed:** "silence is expansion-regime fingerprint" (assumed regime-uniformity of mechanism; 2009Q1 silence rebuts)
- **Failed:** "silence requires property_state saturation = 1.00" (assumed carrier-uniformity; expansion to 8 distributed-saturation cells rebuts)
- **Failed:** "property_state is the asymmetric reorganization driver" (assumed carrier-identity-uniformity; institutional-only silence cell rebuts)
- **Failed (structurally):** "the silence test catches one phenomenon" (assumed mechanism-uniformity; Mechanism-B presence rebuts)

P5 fires on **three** axes (regime, carrier, mechanism), not the predicted one. This is itself a finding for [[project_pre_registration_pattern]] — the uniformity-failures cluster, suggesting the indexicality is structural at this point in the program rather than incidental.

## 5. What this does to load-bearing prose claims

The findings touch several prose artifacts that need explicit updates. Listed by what they currently assert vs what survives:

- **`[[project_saturation_phase_characterization]]`** (2026-05-14 memory): "Phase 0 [0, 0.45] n=24 no-reorg, phase 1 [0.50, 0.55] n=2 reorg-agreement, phase 2 =1.00 n=3 manufactured-silence; silence requires complete saturation." **Falsified on n=83.** The trimodal structure is FM-3-vintage-29-cell-validated only. The memory should be updated or annotated with this finding before the next conversation.

- **`[[project_silence_manufacture_result]]`** (2026-05-13 memory): "Manufactured silence is real, bounded (3 cells, all 2016Q1 rung-3b — expansion-regime fingerprint)." **Strengthened in scope, falsified in qualifier.** The phenomenon is real and FM-substrate-general (11 cells across 3 vintages); the "bounded to 3 cells / 2016Q1 / expansion-regime" qualifier is gone.

- **`section6.tex` L31** ("asserted but not demonstrated beyond banking"): unchanged — the cross-substrate question is still HMDA-falsified. Within-substrate generalization is now demonstrated.

- **`rashomon-routed-decision-methodology.md` §10**: the substrate-vs-stack axis prose carries. The recursive instance (stratum-omission within FM) is a new empirical attestation that belongs in §10 as a within-substrate analog to the HMDA threshold-transfer finding.

- **[[project_hmda_trimodal_result]]**: HMDA falsification reading is unchanged, but its weight shifts. The HMDA trimodal MISS was previously the strongest evidence that the verifier is substrate-indexed. We now know the verifier is *also* stratum-indexed within FM. The substrate-vs-stack axis is real but its operational granularity is finer than "substrate"; it's "calibration-context-of-verifier" at whatever grain the calibration was done.

- **[[project_pragmatics_linguistics_lens]]**: empirically attested at a third granularity (stratum-within-substrate, in addition to substrate-transfer and variant-context). The lens predicts exactly this pattern; the third instance is corroboration, not extension.

## 6. Followups

Ordered by what would close the largest open question first.

1. **Re-run `frame_evocation_test.py` on the expanded corpus to test P1, P2, P4.** The three stamped predictions sit on the same code path; one execution closes all three. P1 is the live question: does named_diff fire structurally on the new Mechanism-A cells and (critically) on the Mechanism-B cell? If the discriminator catches both, it's an asymmetry-detector not a silence-detector. If it catches only Mechanism-A, it's discriminating something real.

2. **Diagnose 2020Q2 and 2012Q1 failures.** 2020Q2 exited 1 (likely data-loading error), 2012Q1 exited 137 (OOM). Either may load with the placebo+eps-arm reductions already applied in the recovery script. Completing the 4-vintage fresh set strengthens P3 and adds COVID-regime + recovery-regime evidence to the carrier-set question.

3. **Update `[[project_saturation_phase_characterization]]` memory** with the falsification. Optional companion: write a 2026-05-18 saturation-phase-revision note in `docs/superpowers/specs/` superseding the 2026-05-14 characterization.

4. **2014Q3/rb03 deep-dive.** The single Mechanism-B cell deserves either a one-cell case study (what makes A's 3 ufs converge on a worse-named-R² configuration than B's 54?) or a labeled-as-spurious classification with the criterion that distinguishes it from Mechanism-A. Either resolution closes the discriminator-specificity question.

5. **Re-run `silence_manufacture_test.py` on all strata with the explicit scope declaration.** Reproduces the n=83 numbers in this note via the canonical script (current note used in-line analysis off the script's `analyze_cell`).

---

## 7. Scope of claim

**In scope:** FM 30Y conforming corpus, 5 vintages (3 original + 2 fresh completed), all strata as populated. Within-substrate generalization of silence-manufacture.

**NOT in scope:** P1/P2/P4 verdicts (frame_evocation not yet re-run). The named_diff discriminator's generalization status remains the live methodological question.

**NOT in scope:** cross-substrate (HMDA already broke; this run does not retest). MFLPD / LC pricing (separate substrates).

**NOT in scope:** mechanism-discrimination decision for the silence test (the Mechanism-A/B distinction is surfaced here; whether to refine the test to discriminate, or to relabel cells as Mechanism-A-silence vs Mechanism-B-asymmetry, is a methodology decision left to the construction paper).

**Narrow form:** "On 5 FM vintages spanning crisis / expansion / steady-state, the silence-manufacture phenomenon is present in 11 cells across 3 vintages, with distributed property_state saturation (not trimodal), multi-carrier (geographic + institutional), and the silence-test signature catches at least one non-canonical mechanism the prior work did not see."

---

**Result-note author:** Claude Opus 4.7 (governance lineage). **Date:** 2026-05-18. **Method:** in-script analysis using `silence_manufacture_test.analyze_cell` against the 5 per-vintage `fm_rich_policy_vocab_adequacy_*.json` files. No new compute, no model fits. P-verdicts P1/P2/P4 pending re-run of `scripts/frame_evocation_test.py` on the expanded corpus. **Pseudonym layer in use:** Olorin (layer 1) / Tay (layer 2). **References to result-notes use [[wikilink]] form.**
