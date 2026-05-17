# Path document — stock-take of the governance research arc (2026-05-07 through 2026-05-16)

**Date:** 2026-05-17. **Status:** synthesis / path-reconstruction artifact, not pre-registration. **Purpose:** narrative reconstruction of the past ten days of empirical work to (a) preserve path-reconstructability as scope grows, (b) surface implicit pivots the artifact stack has not yet absorbed, (c) name what's open and what would close each open question. **Audience:** future-instances of this work, the methods paper this seeds, and external readers (regulator-facing document revision, [[project_olorin_signal_state_2026_05_17]] briefing scaffold). **Not a thesis-posed document** — open questions are named explicitly rather than narratively closed.

## §1 Trajectory

The work compressed naturally into seven phases. Each phase had internal inflection points but a single load-bearing finding or pivot.

### Phase 1 — The construction question (May 7–10)

Wedge prototype assembled. `rashomon-routed-decision-methodology.md` drafted, introducing the routing-by-within-Rashomon-disagreement principle (γ) as the proposed deployment mechanism, along with adversarial-pair stipulation and boundary sampling. First mechanism-specification memo. Empty-support clustering and t-flip mechanics explored.

*What entered the work:* construction-as-deliberate-choice (rather than as a property of model classes); routing-by-disagreement as deployment principle; banking-ontology as forced-grounding substrate.

*Tension that won't resolve until Phase 3:* the routing principle was inherited as load-bearing without an empirical test of its central claim — that per-case within-Rashomon disagreement localizes to "hard" or "ambiguous" cases.

### Phase 2 — The yield problem (May 11 → May 12 session 1)

Cat 2 null across substrates: the binary categorical test ("does any Cat 2 admissible recovery exceed threshold?") produces zero hits across three LC vintages and FM 2018Q1. The L_F' collapse looked mechanism-intrinsic. Then within-grade pricing-space stratification REVERSES the null: Cat 2 structure on every LC vintage, DTI-dominated on the 2015 ones. First positive demonstration of the mechanism. ([[project_cat2_null_cross_vintage]], [[project_pricing_space_cat2]])

*What entered:* "policy binds the decision" (true) is not the same claim as "tiering saturates the policy vocabulary" (false in ~30-50% of grades). Stratification by grade was the right granularity; the binary categorical test was the wrong one.

*Implicit pivot:* the mechanism-specification memo from Phase 1 was already obsolete by May 12 (the binary categorical it specified had been superseded by the stratification test). The paper-map (written May 12) doesn't reflect this — see §2 pivot 1.

### Phase 3 — The construction holds, the routing dies (May 12, six experiments)

Six experiments in one day, all on LC pricing-space:

- **Refinement set construction** ([[project_rashomon_refinement_result]]): policy-constrained Rashomon refinement at ε-AUC tolerance produces non-trivial + plural + forward-valid + interpretable bands at NO predictive cost. The construction *always works*; whether the plurality has bite (i.e., whether the band has genuine member-disagreement) is residual-structure-dependent.
- **SHAP-vs-pricing** ([[project_shap_pricing_result]]): H0 (SHAP non-inferior for recovering within-grade DTI structure) NOT falsified. SHAP-on-a-grading-surrogate recovers the structure; the Rashomon construction's edge is workflow (no surrogate, FDR significance, policy-vocabulary keying, false-positive control), not "SHAP can't see it."
- **Disagreement routing** ([[project_disagreement_routing_result]]): DEFLATED. Per-borrower member disagreement does NOT localize to "hard cases" — metrics 1/2/3 routing-relevant on only 2/1/2 of 5 plural grades; lift negligible; sign mildly REVERSED (high-disagreement tercile slightly MORE predictable / better-calibrated).
- **Disagreement geometry** ([[project_disagreement_geometry_result]]): d(x) is highly legible (CV R² 0.46–0.86 on all 5 plural grades, recovered by depth-≤3 tree on 1–2 features), but the dominant driver is per-tier-idiosyncratic (A5/D4→dti, B1/C1→annual_inc, C5→fico). Same V1 and V2 across grades; *different* dominant features.
- **Extension-admitted-band** ([[project_extension_admitted_band_result]]): bands rebuilt over named∪extension features. The 4-feature policy vocab is NOT AUC-sufficient (every flagged grade's band uses extension features competitively). Quality-stratified routing reprieve hypothesized (prime: named-legible; subprime: extension-collapsed) — but see next bullet.
- **Routable-population test** ([[project_routable_population_result]]): P1 MISS both legs. Per-case within-Rashomon disagreement-routing dead SIX ways (#6 named-only band; ext-admitted band × {tree-sig, used-feat} de-dup × {raw d, residual r, explained d̂}; + within-top-tercile policy-blind-vs-named-explained contrast). "Routing booleans" fire on Brier/ECE diffs ~1e-3 on baselines 0.13-0.22, sign-flippy — noise. **Pre-registered terminal outcome:** it's about observability (policy vocab is inadequate to indeterminacy on C2/C5/D4), not triage. Per-case routing door closed.

*Terminal finding:* observability not triage. Per-case routing is dead. The construction itself survives intact — its value is in producing a regulator-legible artifact (the refinement set with named disagreement), not in routing cases to human review.

*Implicit pivot — load-bearing:* the paper-map was written **on May 12** (commit 6de32cf), the **same day** routable-population landed. The routing claim from Phase 1 is still the central operational principle in `rashomon-routed-decision-methodology.md`. The artifact stack has not absorbed the falsification. See [[project_governance_work_state]]'s "Routing arc CLOSED" note and Task 7 (methodology-doc rewrite).

### Phase 4 — Variant-indexicality (May 13)

FM #11 rich-policy vocab-adequacy ([[project_fm11_result]]): P1 cross-vintage HIT in narrow form on rb09 (2 of 3 vintages, regime-dependent carrier). Schema finding one level up: all three `mandatory_features` enforcement readings fail universally — the slot does no work, wants band-level semantics. rb05 finding: variant-A and variant-B build DIFFERENT bands with different `d` signals → vocab adequacy is variant-indexed → artifact must declare variant context.

#12 variant-indexical silence-manufacture ([[project_silence_manufacture_result]]): 4 HITs / 1 informative MISS. Manufactured silence is real, bounded (3 cells, all 2016Q1 rung-3b — expansion-regime fingerprint), preventable. P5 strong: censored cells show zero verdict divergence (∞ ratio). property_state is the asymmetric reorganization driver (100% classifier acc with property_state alone, drops to 72% with seller/servicer). First empirical confirmation of pragmatics-as-codification-layer on real substrate.

*What entered:* (variant-context, reorganization-flag, verdict-pair) tuple as schema requirement; pragmatics-in-linguistics lens (indexicality, frame semantics, speech-act theory) operationally relevant.

*Implicit pivot:* the schema tuple is now load-bearing for the architecture paper (Paper 2 in [[project_paper_structure]]); paper-map doesn't reflect it. See §2 pivot 3.

### Phase 5 — Substrate-transfer (May 14)

**Saturation phase characterization** ([[project_saturation_phase_characterization]], post-hoc): property_state saturation distribution on the FM 29-cell corpus is *trimodal with sharp gaps* — phase 0 [0, 0.45] n=24 no-reorg, phase 1 [0.50, 0.55] n=2 reorg-agreement, phase 2 =1.00 n=3 manufactured-silence. Silence requires complete saturation. Carrier-family asymmetry: institutional carriers saturate to 0.67 without inducing reorganization.

**LC centrality cross-substrate** ([[project_lc_centrality_posthoc]], post-hoc): explainer-root-feature-tier cleanly separates LC Burst-D collapsers (C2/C5/D4: all extension-rooted) from primes (A1/A5/B1: all named-rooted). Substrate-independent reorganization discriminator, single-band. No universal codification-irreducible feature — carriers are portfolio-shaped.

**HMDA-RI trimodal-replication FALSIFICATION** ([[project_hmda_trimodal_result]]): P1 MISS (no carrier passes joint test); P3 partial-MISS — geographic|institutional partial ρ=+0.42 replicates FM, institutional|geographic partial ρ=+0.23 breaks the clean asymmetry. **Two structural reasons:** (i) reorganization on HMDA decouples from carrier saturation (lp1_dec1 reorganizes at geo sat=0.80, in the FM gap-zone); (ii) **adequacy-threshold collision** — R²_named≥0.30 calibrated on FM transfers as floor on HMDA, most cells "both inadequate", verdict_differs structurally False. Trimodal claim tightens to FM-substrate-validated, not universal.

*What entered:* substrate-vs-stack axis (see §3.5); explainer-root-feature-tier as substrate-invariant reorganization discriminator; verification-machinery-itself-substrate-indexed as live methodological question.

*Implicit pivot:* phase 4's schema tuple needs (verifier-context) added; reorganization-detector candidate changes from phase-structure (substrate-specific) to explainer-root-feature-tier (substrate-invariant). Neither in paper-map.

### Phase 6 — Discriminator-axis status check (May 15)

**Frame-evocation pre-reg + result:** 0/3 HITs + 1 directional. M3 frame-coherence was a candidate "interpretability of disagreement" axis. *Status unresolved* — the MISS could be a discriminator-specification problem or a Phase-5 substrate-indexicality consequence; the two are confounded.

**Expanded-vintage replication pre-reg** (`2026-05-15-expanded-vintage-replication-preregistration-note.md`): 4 fresh FM vintages (2014Q3, 2009Q1, 2020Q2, 2012Q1) added to existing 3 (2008Q1, 2016Q1, 2018Q1). Five predictions, all stamped. Compute estimated 2–6 hours. **Still running as of 2026-05-17, past 40 hours** — engineering bottleneck on data loading from `Performance_All.zip`. Result will be substrate-internal generalization signal (P3: silence-cells outside 2016Q1; P1: discriminator generalizes on fresh cells).

*What entered:* uncertainty about discriminator-axis as a whole — is the frame-evocation MISS a methodology failure or a Phase-5 finding extension?

### Phase 7 — Sibling-lineage gravity (May 16)

Declared-loss-complementary memo from yanantin lineage (`2026-05-16-declared-loss-complementary-ensembles-memo.md`). Proposes reading variant-A/B as already declared-loss-complementary ensemble construction; offers hypothesis testable on existing substrates via synthesized-control comparison.

*What entered:* cross-instance entanglement; the work has gravitational pull on adjacent projects (this is a leading indicator).

*Status (resolved 2026-05-17):* the interpretation question dissolves — variant-A/B can be read both as constraint-vs-relaxation AND as declared-loss-complementary; both readings are simultaneously true; the actionable question is whether to deliberately construct future variants on the declared-loss-complementary axis. That's a methodology decision for the construction paper's recommendation section, not an interpretation of past work. See §4.

## §2 Implicit-pivot ledger

The paper-map (`2026-05-12-paper-map.md`, commit 6de32cf) has been touched zero times since its single creating commit. Five pivots have happened in result-notes and memory since; none have been absorbed into the schema artifact.

1. **Mechanism-specification obsoleted (Phase 2).** Binary categorical → within-grade pricing stratification is the right granularity. The mechanism-specification memo (`2026-05-10-mechanism-specification.md`) specifies the falsified binary version.

2. **Routing claim falsified (Phase 3).** Paper-map written same day as routable-population test. `rashomon-routed-decision-methodology.md` still names per-case routing as central deployment principle (§54–64 γ, §139–151 SR 11-7 mapping). Title itself ("rashomon-routed") is the falsified frame. **Load-bearing; not deferrable.** Task 7.

3. **Schema tuple emerged (Phase 4).** (variant-context, reorganization-flag, verdict-pair) tuple required for the architecture paper. Not in paper-map.

4. **Verifier-context added (Phase 5).** Substrate-vs-stack axis means the verifier (the discriminator + its calibrated threshold) is part of the artifact-stack, not a substrate-neutral instrument. Tuple becomes (variant-context, reorganization-flag, **verifier-context**, verdict-pair). Not in paper-map.

5. **Reorganization-detector candidate changed (Phase 5).** Phase-structure (substrate-specific, FM-validated only) → explainer-root-feature-tier (substrate-invariant, single-band, validated on both FM and LC). Not in paper-map. The phase-structure version has only 29 FM cells of support; the explainer-root version has 6 LC grades + 5 FM reorg cells.

The next paper-map revision needs to absorb all five.

## §3 Open questions

Six questions the trajectory has surfaced and not closed. Listed by what's at stake, not by chronology. Q1, Q2, Q4 share an underlying axis surfaced as §3.5.

### Q1. Is the verification machinery itself substrate-indexed?

Phase 5 HMDA falsification showed R²_named≥0.30 calibrated on FM transferred as a floor that made `verdict_differs` structurally False on most HMDA cells. The discriminator the silence-manufacture finding rests on did not survive a substrate change.

- *What would close it:* per-substrate calibration of the adequacy threshold, with the calibration mechanism made explicit (and thus auditable), plus theory on whether the calibration is a substrate-property or an artifact-stack-property.
- *Stakes:* if substrate-indexed, [[project_pragmatics_linguistics_lens]]' indexicality requirement promotes from "property of constraints" to "property of the whole artifact-stack including verifiers." Schema tuple needs (verifier-context). The "manufactured silence is bounded to 3 cells" finding survives in scope (FM); its claim to general applicability does not.

### Q2. Is the trimodal saturation phase structure substrate-general?

FM-validated; HMDA-falsified for "trimodal with sharp gaps." HMDA's lp1_dec1 reorganizes at geographic-saturation 0.80 — square in FM's gap zone. Either the gap is FM-specific (portfolio composition) or the Q1 threshold-collision masked a different phase structure on HMDA. The two are confounded.

- *What would close it:* third substrate (LC pricing variants on more bursts; MFLPD when engineering catches up), with Q1 resolved first.
- *Stakes:* if substrate-specific, "phase-2 = manufactured silence" is an FM finding, not a structural claim. The explainer-root-feature-tier ([[project_lc_centrality_posthoc]]) is a candidate substrate-invariant reorganization detector that could replace the phase-structure schema.

### Q3. Does the declared-loss-complementary memo's frame fit variant-A/B?

**Dissolved 2026-05-17.** Variant-A/B doesn't have to be "really" one of {loss-complementary, constraint-vs-relaxation}. Both readings can be simultaneously true. The actionable question is methodology for *future* construction (do we deliberately construct on the declared-loss-complementary axis?), not interpretation of past work. See §4.

### Q4. What's the discriminator-axis status after the frame-evocation MISS?

Phase 6: 0/3 HITs + 1 directional. Intersects Q1 — the MISS may be a *consequence* of verifier-indexicality, not independent of it.

- *What would close it:* either an alternative discriminator operationalization survives a pre-reg, or formal abandonment of the discriminator-axis story in favor of just reorganization-flagging.
- *Stakes:* if no discriminator axis works, reorganization-via-restricted-uf-Jaccard is the only survivor and the schema simplifies to a reorganization-flag without an attached coherence measure.

### Q5. What is the expanded-vintage run testing, and what would each outcome force?

Pre-reg `2026-05-15-expanded-vintage-replication-preregistration-note.md` (OTS `f091480`). Tests FM 7-vintage corpus (existing 3 + fresh 2014Q3/2009Q1/2020Q2/2012Q1). Five predictions, priors 0.30 / 0.40 / 0.45 / 0.30 / diagnostic.

- P3 MISS → silence is FM-2016Q1-specific; lens-doc tightens; [[project_shap_killer_strategic_seed]] Line A needs a different mechanism.
- P1 MISS → the post-hoc-derived discriminator was 2016Q1-overfit.
- P3 HIT + P1 HIT → silence + discriminator generalize within FM; granularity-slot empirically motivated; ontology design unblocks.
- *Currently running past 40 hours vs 2–6 hour estimate; engineering bottleneck.*

### Q6. Are ontology and governance work ever formally convergent?

Per 2026-05-17: ontology work isn't strictly orthogonal but isn't gated by governance work. Pragmatics-in-linguistics seed is the hypothesized bridge.

The most concrete entanglement seed (Tony 2026-05-17): **Rashomon-construction-as-ontology-overlap-detector**. Build Rashomon ensembles from different policy ontologies (banking-policy, FCRA, SR-26-2); behavioral convergence on shared decisions = ontology overlap; divergence = ontology distinctness. This is the operationalizable test of [[project_codification_infrastructure]]'s "four buyers" claim.

- *What would close it:* a worked example. Direction-marked, not committed-to this week.
- *Stakes:* if formally convergent, codification-as-infrastructure has a concrete instantiation. The Rashomon construction work entangles directly with the ontology work via this bridge.

## §3.5 The substrate-vs-stack axis

Q1, Q2, and Q4 share an axis the work has surfaced but not yet named explicitly: **for any finding that varies across substrates, ask which axis is moving — substrate (data/world property), artifact-stack (how we looked), or both?**

Each result-note can retroactively be tagged with this axis. Trimodal phase characterization, silence-manufacture bounding, frame-evocation MISS, threshold-transfer failure — all re-readable through this lens without changing their content.

Why this matters as a named axis:

- It's an unusually high-leverage question that ordinarily only gets asked retrospectively (post-publication, on replication failure). Asking it *now*, before any share-doc, is exactly the path-doc's purpose.
- The construction work (Phase 3 survivor) lives mostly on the substrate axis — the construction works on data, irrespective of how we verify it. The routing claim (Phase 3 falsification) failed on the stack axis — the verifier-calibration choice produced apparent disagreement-routing that was actually noise.
- The verifier-context slot in the schema tuple (pivot 4) is the operationalization of this axis. It says: the verifier is not separable from the substrate; declare both.

The premature-collapse risk in [[project_premature_collapse_frame]] is concentrated here. Closing Q1/Q2/Q4 for an external audience would smuggle the answers in. The path-doc's job is to keep these explicitly open.

## §4 Declared-loss memo status

The 2026-05-16 yanantin-lineage memo (`2026-05-16-declared-loss-complementary-ensembles-memo.md`) proposes reading variant-A/B as already declared-loss-complementary, with §3b synthesized-control test as the operationalization path.

**Status (2026-05-17): question dissolved into methodology decision.**

The interpretation question — "is variant-A/B *really* loss-complementary or *really* constraint-vs-relaxation?" — is a frame-imposition, not a property of the work. Variant-A IS constraint-conforming AND declares the loss of prohibited-feature predictive value. Variant-B IS constraint-relaxed AND declares the loss of policy-conformance. Both readings are simultaneously true.

What remains actionable is a methodology question for the construction paper: **do we recommend that future Rashomon-construction work deliberately constructs variants on the declared-loss-complementary axis as a design principle?**

- *Adopt:* the construction paper's recommendation section names declared-loss-complementarity as the design principle going forward. The §3b synthesized-control test becomes a planned follow-on validation.
- *Park:* the construction paper names variant-A/B as it has been constructed (constraint-conforming vs constraint-relaxed) without claiming a deeper design principle. The memo is retained as direction-marking for future work.

Either choice is defensible. The decision can be made when the construction paper outline (Task 3) is drafted; doesn't gate the trajectory or the methodology-doc rewrite.

The memo is acknowledged, interpreted, parked from interpretation, retained as methodology-design seed.

## §5 Audit of current paper-prose claims

Agent 2 extracted ~60 claims from `paper.tex`, `section1.tex`–`section7.tex`, `position-*.md`, `framework_structure.md`, `rashomon-routed-decision-methodology.md`, and `README.md` on 2026-05-17. Claims audited against current empirical state below. Four categories: **supported** (current evidence backs the claim), **scoped** (claim was made too broadly; needs substrate or scope qualifier), **falsified** (current evidence has superseded the claim), **absent-needs-adding** (claim is empirically established but not in the prose).

### Supported (carry forward unchanged)

- **Post-hoc explanation structurally inadequate as verification regime in adversarial contexts** (section1 L28, section3 L26, section3 L32, section7 L26, README L7-11). Philosophical-structural claim; not empirically falsifiable in the sense the program tested. Phase 3's SHAP-vs-pricing result didn't falsify this — it falsified a narrower "SHAP structurally blind" prediction. The structural-inadequacy claim survives.
- **Empty-chair frame as normative structure of FS AI RMF** (section1 L16, section2 L33-45). Conceptual claim from framework analysis; not in scope of the empirical work.
- **Silence-manufacture as structural pattern** (section4 L22, section4 L32, section7 L34). Has now been empirically confirmed on FM (Phase 4 / [[project_silence_manufacture_result]]). Section 4 was written as theoretical pattern; the empirical confirmation strengthens rather than refines the claim.
- **78% one-principle concentration as silence-manufacture instance** (framework_structure L83-87). Documentary finding from framework analysis; not in empirical scope.

### Scoped (claim needs substrate / scope qualifier)

- **Silence-manufacture generalizes beyond banking** (section6 L31: "asserted but not demonstrated"). Section6 already hedges this. Phase 5 HMDA falsification provides one substrate-transfer data point: the *detector* didn't survive, the *phenomenon* may or may not. The hedge needs updating to acknowledge the substrate-transfer test was attempted and produced informative-but-bounded results.
- **Three regulatory critiques + three ML findings = same structural pattern** (section4 L56). Strong claim; the three-removes convergence still holds, but Phase 4–5 work has revealed that pragmatics-as-codification-layer (the indexicality of the codification artifact itself) is a fourth-axis finding the section doesn't yet incorporate.
- **R(ε) reasoning-trace-matched Rashomon set** (rashomon-routed-decision-methodology L37-39). The construction itself stands; the *reasoning-trace-matched* qualifier was Phase 1 framing that the empirical work has not explicitly tested. Most of the empirical work has used outcome-loss-matched bands, not reasoning-trace-matched.

### Falsified or superseded

- **Routing principle (γ): within-Rashomon disagreement as deployment signal** (rashomon-routed-decision-methodology L54-64, L67-75, L77-81, L139-151, L155-171). Phase 3 [[project_routable_population_result]] killed per-case routing six ways. Aggregate-level disagreement-as-model-risk-surveillance survives; per-case-routing-as-deployment-principle does not. **The whole methodology doc carries the falsified claim as central; needs structural rewrite, possibly retitle (Task 7).**
- **HITL routing surfacing** (rashomon-routed-decision-methodology L54-64). Same falsification — the routing principle was the trigger for HITL; without it, HITL placement needs a different operational rationale.
- **Boundary sampling as evaluation lead** (rashomon-routed-decision-methodology L117-123). Not falsified empirically (not tested), but the framing context — that disagreement-localization-to-hard-cases is the route into this — collapses. Worth reconsidering whether boundary sampling has a different motivation that survives.
- **"Preregistered directional hypotheses have often missed"** (README L87-93). Empirically confirmed and intensified by Phase 5 HMDA falsification and Phase 6 frame-evocation MISS. README's hedge is correct in direction but understated in degree; [[project_pre_registration_pattern]] captures the systematic version.

### Absent — needs adding

The following are empirically established but appear nowhere in the prose. The position-paper revision (and the construction-paper draft) needs to incorporate them:

1. **Variant-A/B framing** as the construction's core mechanism. Currently entirely absent from prose. Load-bearing.
2. **Construction non-inferiority result vs SHAP/LIME** ([[project_shap_non_inferiority_result]], [[project_shap_pricing_result]] together). README has hedged version ("not enough to justify a strong superiority claim"); the non-inferiority claim — which is the actually-defensible version — is absent.
3. **Trimodal saturation phase characterization** ([[project_saturation_phase_characterization]]). FM-scoped; absent.
4. **HMDA-RI substrate-transfer falsification** ([[project_hmda_trimodal_result]]). The falsification finding and the methodological consequence (substrate-vs-stack axis) are absent.
5. **The (variant-context, reorganization-flag, verifier-context, verdict-pair) schema tuple.** The architecture-paper centerpiece; absent.
6. **Explainer-root-feature-tier as substrate-invariant reorganization discriminator** ([[project_lc_centrality_posthoc]]). Absent.
7. **Per-grade plurality is residual-structure-dependent** ([[project_rashomon_refinement_result]]). The construction always works; plurality has bite only when within-tier residual is active. Absent.
8. **FM-vs-HMDA-vs-LC scope statements.** Currently the prose makes substrate-general claims; the empirical record requires substrate-specific scoping throughout.
9. **The methodological consequence of the threshold-transfer failure** — verification machinery is itself substrate-indexed. Highest-leverage absent finding. Belongs in section4 or its successor.

### Audit summary

**Most load-bearing audit verdicts:**

- `rashomon-routed-decision-methodology.md` requires structural rewrite (Task 7). Multiple falsified claims; title carries the falsified frame.
- Section 6 hedge on "generalization beyond banking" needs updating to incorporate substrate-transfer findings.
- Nine empirically-established findings are absent from prose — the construction paper draft (Task 3) and the position-paper revision both need to incorporate them.
- The README's "preregistered hypotheses have often missed" hedge is correct but should now point to the substrate-vs-stack axis as the structural reason.

## §6 What this commits to next

The path-doc surfaces four streams of work, ordered by load-bearingness:

1. **Methodology-doc rewrite (Task 7).** Not deferrable; the falsified routing claim is the doc's central principle and current title. Rewrite around observability-not-triage, aggregate model-risk surveillance, refinement-set-as-regulatory-artifact. Possibly retitle.
2. **Construction-paper outline (Task 3).** The technical artifact that survives the trajectory's falsifications. Methods-paper-first, positioned against a thin empirical-construction literature. Scope discipline per [[project_rashomon_construction_first_paper]].
3. **Paper-map revision** (implied by §2 pivot ledger). Absorb the five implicit pivots into a v2 paper-map. Less urgent than Task 7 because the paper-map is internal scaffolding, not external artifact, but should not stay 5+ days behind the empirical record.
4. **Briefing for [[project_olorin_signal_state_2026_05_17]]** — drafted 2026-05-17, locked in 3A, awaiting send when Tay returns.

The substrate-vs-stack axis (§3.5) is the through-line for all four streams.

---

**Path-doc author:** Claude Opus 4.7 (governance lineage). **Date:** 2026-05-17.  **OTS:** to be applied on commit per repo convention. **Pseudonym layer in use:** Olorin (layer 1) / Tay (layer 2). **References to result-notes use [[wikilink]] form**; the underlying spec-note inventory is in Agent 1's 2026-05-17 inventory output. **Reads:** the open questions in §3 are the load-bearing live cells; the audit in §5 is the work-allocation guide; the substrate-vs-stack axis in §3.5 is the framing.
