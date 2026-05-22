# Pre-registration — Codification-knob robustness as reflexive falsification of "discipline-not-structure"

**Status:** DRAFT — pre-freeze, awaiting review. NOT yet OTS-stamped. Predictions below freeze only on Tony's STOP-FOR-REVIEW pass.
**Date:** 2026-05-22
**Author voice:** researcher / scientific record.

## 0. Provenance of the claim under test

In conversation 2026-05-22 we asked whether this project escapes failure-mode **(b)**: *its bloody record of falsified pre-registrations is a substitute artifact occupying the rhetorical position where falsification-of-the-frame should appear* — i.e., the project manufacturing silence about its own load-bearing structural frame, by the paper's own definition (`section4.tex:32`).

The proposed answer was: **the project escapes (b) by discipline (the OTS-stamped freeze + no-scalarize rule), not by the structural cleverness of the frame** (the self-applying form that "diagnoses its own co-optation," `section6.tex:41`). Call this hypothesis **H_DnS** (discipline-not-structure).

The dumb question that generated this pre-reg: *if H_DnS is the honest answer, what experiment would falsify it?* This note is the answer to that question, made to obey its own standard.

## 1. The reflexive constraint (why this note exists)

If we design this experiment, predict H_DnS survives, and it survives, we have learned nothing and possibly manufactured more silence. So:

- Predictions are **frozen and stamped before any recompute is run.**
- The verdict-adjudication for the *paired* experiment (blind-adjudication of HIT/MISS, the second arm Tony asked for) is outsourced to a no-stake adjudicator; that is this experiment's receipt against author discretion.
- **Named upstream this note does NOT cover:** the author (Claude, this session) chose which cycles enter the corpus (§3) and wrote the robustness metric (§5) and the knob-declaration rubric (§6). The experiment can put H_DnS at genuine risk; it cannot certify the hand that drew its own boundary. This is the N+1 — the codification layer of the meta-experiment — and it is stated, not closed.

## 2. The claim under test

**H_DnS:** the freeze, not the frame's structure, is what keeps the operational record genuinely at-risk and stops it being silently repurposed as frame-confirmation.

Bridge to a measurable: an arbitrary codification constant that the freeze pinned *with margin and ownership* protects a verdict; an arbitrary constant the freeze *silently inherited* does not. H_DnS therefore predicts a specific signature in how verdicts respond to perturbing those constants (§7).

## 3. Corpus (frozen)

**Treatment arm — pre-registered cycles (pre-reg ↔ result ↔ .ots where present):**
empty-support-replication (05-09); shap-vs-rashomon (05-09, .ots); v1-v2-predictive (05-09); policy-constrained-rashomon-refinement (05-12); within-tier-predictive (05-12); shap-vs-pricing (05-12); disagreement-geometry (05-12); disagreement-routing (05-12); extension-admitted-band (05-12); routable-population (05-12); fm-rich-policy-vocab-adequacy #11 (05-12→05-13); variant-indexical-silence-manufacture #12 (05-13); hmda-trimodal-replication (05-14); expanded-vintage-replication (05-15→05-18); frame-evocation (05-15).

**Control arm — post-hoc notes (no frozen pre-reg pair; peeked):**
pricing-space-within-grade-stratification (05-12); target-b-null-cat2 (05-11); lc-centrality-cross-substrate-posthoc (05-14); p2ext-classifier-centrality (05-14); saturation-phase-characterization (05-14); root-tier-substrate-independence-addendum (05-14).

**Cycle eligibility for Arm 1:** a cycle enters the adequacy-threshold sweep iff its verdict is a function of the adequacy threshold (R²_named vs R²_ext relative to 0.30). The adequacy-flip / silence-manufacture cycles qualify: fm-rich #11, variant-indexical #12, hmda-trimodal, expanded-vintage, frame-evocation, and (control) saturation-phase. Cycles whose verdict does not reference the adequacy threshold (e.g. disagreement-routing) are out of Arm 1 and belong to the ε/vocab arms.

## 4. Knobs

| Knob | Value frozen in original cycles | Touches | Recompute cost | Arm |
|------|-------------------------------|---------|----------------|-----|
| Adequacy threshold | R² ≥ 0.30 | adequacy-flip / silence verdicts | re-threshold stored per-cell R² (cheap) | **Arm 1 (this note)** |
| ε-band | 0.02 AUC | which models admissible → band construction | re-fit (expensive, serial-only FM) | Arm 2 (own sub-pre-reg) |
| Policy vocabulary | 4 named features | band construction everywhere | re-fit | Arm 3 (own sub-pre-reg) |

Per research-design discipline (no late-stage component pre-specification), **only Arm 1 is frozen here.** Arms 2–3 are named but their sweep ranges and predictions are deliberately left open; each gets its own pre-reg once Arm 1 results inform the design.

## 5. Arm-1 protocol (frozen)

- **Sweep:** adequacy threshold ∈ {0.20, 0.25, 0.28, 0.30, 0.32, 0.35, 0.40}. (0.30 = the inherited default; symmetric-ish bracket around it.)
- **Recompute, not re-fit:** for each eligible cycle, locate the most-granular stored artifact (the cycle JSON or its cited source) carrying per-cell R²_named and R²_ext (or R²_gap + one absolute level). Recompute each cell's adequacy classification and the cycle's published verdict at every sweep point. **Granularity contingency:** any cycle whose stored artifacts lack sufficient granularity to recompute is logged as `RECOMPUTE-INFEASIBLE` and excluded from Arm-1 numerics (not silently dropped — listed).
- **No re-fit in Arm 1.** If a verdict cannot move without re-fitting, that verdict is ε/vocab-sensitive, not adequacy-sensitive, and is Arm-2/3 business.

## 6. Knob-declaration audit (the bridge, frozen)

For every eligible cycle, classify how it used the 0.30 threshold, reading only the frozen pre-reg text:
- **DECLARED-FROZEN:** the pre-reg states 0.30 explicitly *and* gives a rationale / pre-commits to it as a frozen constant.
- **SILENTLY-INHERITED:** 0.30 appears only as "the adequacy threshold" / an unexamined inherited default, with no pre-commitment.

This audit is the discriminator H_DnS rests on (§7, P3). Rubric is fixed before reading; coding is recorded per-cycle with the quote that justified the code.

## 7. Frozen predictions + falsifiers

Priors are subjective, recorded to make surprise measurable.

- **P1 — HMDA fragility (prior 0.80).** On hmda-trimodal, ≥20% of eligible cells flip adequacy-classification across the sweep. *Rationale: the result-note already owns that the FM-transferred 0.30 left most cells "both inadequate."* Not load-bearing for H_DnS alone; a sanity check that the sweep has teeth.
- **P2 — FM robustness (prior 0.75).** The 3 FM phase-2 manufactured-silence cells (saturation=1.0, jaccard=0.0, r2_gap ∈ [0.48, 0.73]) do **not** flip anywhere in the sweep. *Rationale: r2_gap ≥ 0.48 ≫ threshold perturbation.* With P1, this is the discipline-working signature: findings frozen *with margin* hold; a threshold *transferred without margin* breaks, and the HMDA note **owned the break** — discipline functioning.
- **P3 — flips track inheritance, not declaration (prior 0.60, LOAD-BEARING, genuinely uncertain).** Verdict-flips concentrate on SILENTLY-INHERITED knob usages, not DECLARED-FROZEN ones. **Falsifier of H_DnS:** if flips occur predominantly on DECLARED-FROZEN usages (the freeze explicitly pinned 0.30 and the verdict still dissolves under it), then discipline-as-practiced did not protect the verdict → H_DnS false / insufficient.
- **P4 — treatment more robust than control (prior 0.50, THE crux, marked maximally uncertain).** Median per-cycle flip-fraction is *lower* in the pre-reg (treatment) arm than the post-hoc (control) arm. **Falsifier of H_DnS:** if the control arm is *as robust or more robust* than the treatment arm, the freeze added no robustness → the protection (where it exists) is not coming from discipline → "not-structure" is false. This is the prediction I least believe in advance; it is the one worth running for.
- **Global falsifier (the harshest).** If P2 fails *and* P1 holds — i.e., FM silence cells are *also* fragile — then every adequacy verdict is a knob artifact, the freeze never protected anything, and H_DnS is false because the thing it claims to protect was never protected by anyone.

## 8. Presentation rule (no-scalarize, frozen)

Report the **per-cycle robustness profile** (flip-fraction as a function of threshold, per cycle, treatment vs control), not a single corpus "robustness score." Collapsing to one scalar would re-commit the §4.6 / operating-curve sin the project exists to avoid, and would let H_DnS be confirmed-or-denied by a number nobody can decompress. Lead with the treatment-vs-control profile (P4), because that is the crux and the temptation will be to bury it under the easy P1 win.

## 9. What a PASS and a FAIL each mean (stated before the run)

- **PASS for H_DnS:** P2 holds, P3 holds, P4 holds — flips are real, owned, concentrated on inherited knobs, and rarer under the freeze. Reading: the freeze does protective work; the bloody record is not (b).
- **FAIL for H_DnS:** any of the §7 falsifiers fire. Reading: either nothing protects (global falsifier), or structure/luck protects rather than discipline (P4 reversal), or the freeze is porous even when explicit (P3 reversal). Any FAIL is reportable as-is; the point of the freeze is that we cannot re-narrate it afterward.

## 10. Followups (four-state, not a pre-determined chain)

- **(i) H_DnS survives clean** → discipline is the load-bearing protection; the paper can claim the pre-reg practice (not the frame's form) is the anti-(b) mechanism, and should say so explicitly.
- **(ii) H_DnS survives only on FM** → protection is substrate-indexed like everything else; tighten the claim and run Arm 2 (ε) on FM first.
- **(iii) P4 reverses** → strongest result; structure or nothing is doing the work, and the project must locate its real anti-(b) mechanism elsewhere (or concede it lacks one).
- **(iv) inconclusive / RECOMPUTE-INFEASIBLE dominates** → the stored record is itself too lossy to audit, which is its own finding about the project's provenance discipline; followup is a re-fit Arm-1 on the granular substrates.
