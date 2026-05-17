# Policy-constrained Rashomon refinement methodology

*Methodology for constructing and deploying policy-constrained Rashomon refinement sets for regulator-legible AI decision systems in regulated environments (initially: U.S. consumer credit, with worked extensions to BSA/AML and mortgage performance).*

---

## 0. Status and rename note

**Status:** working synthesis, partially empirically grounded. Originated as the May 6–7 2026 *Rashomon-routed decision methodology* working notes. This rewrite (2026-05-17) supersedes that version after ten days of empirical work falsified the central operational principle of the original — within-Rashomon disagreement as a per-case routing signal — across six different operationalizations ([[project_routable_population_result]]; six-ways-dead, 2026-05-12).

The methodology that survives the falsification is not weaker; it is differently shaped. **Per-case routing is replaced by an observability principle.** The artifact the methodology produces — a policy-constrained Rashomon refinement set with named disagreement region and its driver features — is deployed not as a per-decision triage mechanism but as a regulator-legible representation of the bank's reasoning *as a whole*. The disagreement region survives as a presentation surface for adversarial review and as input to band-level effective challenge under SR 11-7, not as a HITL escalation trigger.

The doc's filename is retained for link stability; eventual rename to reflect the new framing is a separate cleanup. Sections previously organized around the routing claim have been restructured. Falsified branches are named as falsified rather than excised, so the methodology's evolution remains visible in its current artifact form.

**Key empirical anchors (referenced throughout):**
- The construction itself ([[project_rashomon_refinement_result]], 2026-05-12) — non-trivial + forward-valid + interpretable bands at no predictive cost, across substrates.
- The routing falsification ([[project_routable_population_result]], 2026-05-12) — per-case routing dead six ways; observability not triage.
- Variant-indexicality and silence-manufacture ([[project_fm11_result]], [[project_silence_manufacture_result]], 2026-05-13) — the band-pair structure carries pragmatic content that single-band methods cannot.
- HMDA-RI substrate-transfer falsification ([[project_hmda_trimodal_result]], 2026-05-14) — the verifier-context (calibrated threshold) is substrate-indexed; the methodology's verification machinery is part of the artifact-stack.
- SHAP non-inferiority results ([[project_shap_non_inferiority_result]], [[project_shap_pricing_result]]) — the methodology is empirically non-inferior to post-hoc explainers; its added value is workflow-shaped, not pure-accuracy-shaped.

---

## 1. The seam: retrieval and explanation as one layer

The Olorin engagement scoping treated context/memory and explainability as two distinct items. Worked through, they aren't separable.

Retrieval is a contemporaneous commitment to relevance: *these are the inputs that should bear on this decision*. Explanation is a recovery of contribution: which inputs materially affected the output. For honest explanation to be possible, every contributing input must have been retrieved — which means explanation is structurally a subset of retrieval, and the gap between them is informative.

The duality breaks on a third memory source: parametric weights. Anything absorbed during pretraining can shape outputs without being retrieved. In banking this is where fair-lending failures live — implicit correlations between ZIP code and creditworthiness, between name patterns and risk, baked into weights and inaccessible to retrieval-based audit.

Three failure modes at the seam:

**(a) Parametric leak.** Decisions influenced by training-time absorbed correlations. The tensor interface (entropy, top-k mass, attention summaries) doesn't help directly; you would need activation probes, and fair-lending has no clean mathematical signature in activation space. Regulatory term: disparate-impact through learned correlations.

**(b) Retrieval-misuse.** System retrieves correctly, attends honestly to what's retrieved, but the natural-language explanation it generates dissembles about what mattered. Rudin's post-hoc problem reasserting itself one layer up — input observability does not guarantee language-channel honesty. Regulatory term: ECOA principal-reason gaming.

**(c) Retrieval-omission.** Relevant context retrieved and silently dropped via low attention. The case the tensor interface handles best, because dropping shows up in attention summaries. Regulatory term: incompleteness of adverse-action notice.

### The architectural lever: forced grounding

Whether the seam collapses to a single layer depends on a design choice that probably has not been made deliberately at most institutions. **Forced grounding**: architect the system so no decision-relevant fact may flow into output except through retrieval. Parametric memory suppressed for fact-bearing decisions; retrieval mandatory for any input that could plausibly affect outcome.

If forced grounding holds, (a) collapses into (c), and the audit log and the explanation can be the same artifact. The single-artifact dream is reachable.

If parametric reliance is allowed, (a) remains as residual that no single artifact fully exposes, and the methodology requires a separate, weaker class of attestation: *we cannot rule out parametric influence on these dimensions; here is what we did to minimize it.*

Banking-ontology work (Joe's collaboration) is load-bearing here. Incomplete ontology means incomplete grounding means residual parametric reliance means the audit-log/explanation collapse fails. The ontology is not a knowledge-graph nice-to-have; it is the substrate that determines whether the verification problem is tractable at all.

---

## 2. The policy-constrained Rashomon refinement set R_P(ε)

The reasoning-trace work captures what the institution does — case features, consultation patterns, relational weightings, references to precedent, and decisions together. Models within ε of optimal loss on this richer object form the **reasoning-trace-matched Rashomon set R(ε)**. The set is more constrained than under outcome-matching alone, but typically still populous.

The methodology's central object is the **policy-constrained refinement** of R(ε):

> **R_P(ε)** = the subset of R(ε) whose members satisfy the bank's documented policy P. Equivalently: among all models within ε of optimal loss, the ones that act on the policy vocabulary the bank has formally committed to.

R_P(ε) is the methodology's core construct because it is the empirically-tractable answer to the question *what does the bank's articulated reasoning admit?* — not as a single point estimate (one h ∈ R(ε)), but as the admissible set under documented policy.

### Empirically established properties of R_P(ε)

From the construction work ([[project_rashomon_refinement_result]], [[project_extension_admitted_band_result]]):

1. **Non-trivial.** R_P(ε) almost always contains multiple admissible members; "policy uniquely determines the model" is empirically false for realistic ε.
2. **Forward-valid.** The refinement is constructed once; its members generalize on held-out data at the same rate as the optimal single model.
3. **Interpretable.** Members of R_P(ε) are admissible by construction — each carries the bank's policy vocabulary as its feature basis. There is no post-hoc surrogate.
4. **Plurality-with-bite is residual-structure-dependent.** Whether R_P(ε)'s members *disagree on cases* depends on whether the within-tier residual structure is active. On grades with active residual (e.g., LC B1's annual_income residual on 2015 vintages), refinement-set disagreement is genuine and feature-named; on grades without, R_P(ε) is plural but uninformatively so.

The construction is robust: across LC, FM, and HMDA-RI substrates, R_P(ε) is constructible with the four properties above. The variant-A/B + ε-AUC tolerance + used-feature-set deduplication recipe (§4) is the empirically validated construction procedure.

### Why "refinement" rather than "selection"

The traditional MRM framing collapses to single-model selection. R_P(ε) refines instead — it picks out the admissible *set* from R(ε), and presents the set, not a member of it, as the deployable artifact. The shift is consequential:

- **Fossil-model failure mode** (pick one h on day one, freeze, audit outputs against h) is replaced by **refinement-set deployment** (the set is the model; members are the components of the regulator-legible artifact).
- Posterior weighting over R_P(ε) refines the set further as operational data accrues, but does not collapse it to a singleton; the set remains the artifact.

### Loss taxonomy as filter for posterior updates

Not every default updates the posterior over R_P(ε). Treating every default as model failure means learning from noise — properly-priced risk that materialized is exactly what tier-N pricing was supposed to absorb. The honest signal is *defaults relative to tier-expected loss*. Defaults that align with tier-expected loss should produce minimal posterior shift; defaults that exceed tier-expected loss are where the model had factors underweighted.

Without this filter, the posterior drifts toward conservative-collapse over time as ordinary risk accumulates. The taxonomy is load-bearing for the update mechanism to work at all.

The unobservable counterfactual — denied applicants who would have repaid — remains structurally hard. Partial signals exist (bureau performance for applicants who got loans elsewhere; holdout randomization at the margin where ethically defensible; look-back when previously-rejected reapply under different conditions), but none close the gap. *The methodology should explicitly acknowledge this rather than pretend to solve it.* That framing turns an unsolvable problem into a contribution: we are honest about which decision dimensions admit empirical refinement and which do not.

---

## 3. The observability principle (replaces the routing principle)

The original methodology proposed within-Rashomon disagreement as a per-case routing signal: high disagreement → escalate to human review; low disagreement → autonomous decision. That principle was empirically falsified ([[project_routable_population_result]]) across six different operationalizations of band-construction, deduplication, and bucketing. Per-case routing booleans fire on Brier/ECE differences ~1e-3 on baselines 0.13–0.22, sign-flippy — noise.

**The terminal finding is observability not triage.** R_P(ε)'s disagreement region is informative *as a representation of the bank's reasoning structure*, not as a per-case escalation trigger.

The replacement principle:

> **The methodology produces a regulator-legible artifact — R_P(ε) with named disagreement region and its driver features — that is consumed at the band level (aggregate model-risk surveillance, examiner review, policy-vocabulary adequacy assessment), not at the per-decision level (HITL routing, principal-reason adjudication on individual cases).**

Three operational consequences:

**Consumption surface 1 — Internal MRM.** The refinement-set artifact is the bank's own evidence that the model's outputs are admissible under documented policy across the operational distribution. Aggregate disagreement statistics across R_P(ε) members give the model-risk function band-level surveillance signals (drift in the disagreement region's size, shape, or feature composition is a model-risk indicator). See §8.

**Consumption surface 2 — Examination.** The refinement-set artifact is examiner-legible by construction: each member uses the policy vocabulary the bank has documented, the disagreement region's drivers are named, and the band's admissibility profile is auditable in a way SHAP/LIME post-hoc reports are not (the post-hoc report's faithfulness to the model is not verifiable; the refinement-set's faithfulness to policy is). See §7 ECOA reframing.

**Consumption surface 3 — Policy-vocabulary adequacy assessment.** When R_P(ε) is non-trivial and *its members disagree on cases*, this is empirical signal that the policy vocabulary may be underdetermining the decision. Where this disagreement concentrates by feature is information the policy-design function should consume: either the policy admits indeterminacy at this margin (and that's policy-intentional), or the policy needs refinement at this margin (and the refinement-set has named the relevant features). See §10 substrate-vs-stack axis.

The shift from triage to observability is what survives the routing falsification. It is also what the path-doc identifies as the terminal finding of the 2026-05-07 → 2026-05-17 arc.

### Why this is not a weaker claim

The original routing claim made the methodology operationally interventionist: it claimed to identify *which decisions need human review*. That claim failed empirically.

The observability principle makes a structurally different and arguably stronger claim: it identifies *what the bank's reasoning admits as a whole* and produces an artifact that surfaces this for both internal model-risk consumption and external supervisory review. The artifact does not require the methodology to be smarter than the bank's underwriters about individual decisions; it requires only that the artifact faithfully represents R_P(ε) and its disagreement structure. The methodology's regulatory bite comes from the artifact's *legibility against the policy*, not from its per-case judgment.

---

## 4. Construction methodology

The empirically validated construction of R_P(ε) is:

**Inputs:**
- Training data D = {(x_i, y_i)} where x is feature vector, y is the decision outcome (default, tier, grant/deny depending on the decision context).
- Policy P expressed as a vocabulary — a finite set of features F_P the bank has documented as the basis for the decision.
- ε-AUC tolerance (default 0.02 from the empirical work — interpretable as "models within 2 AUC points of optimal").

**Procedure:**

1. **Train a gradient-boosted tree ensemble** on D with max depth 4 (the empirical default; depth sweep validated). Record AUC on held-out validation.
2. **Generate the band**: enumerate trees from the ensemble at AUC within ε of the optimum. The band is the set of all such trees that act on the policy vocabulary F_P (variant-A) and optionally a band that admits the prohibited features (variant-B), depending on the analysis purpose.
3. **Used-feature-set deduplication.** Trees with the same set of features actually used in their decision logic are deduplicated. This is the [[project_routable_population_result]] correction to the original tree-signature deduplication, which produced near-duplicate-tree noise that artifactually inflated band size and depressed legibility metrics.
4. **The band IS R_P(ε)**: the deduplicated set of trees within ε of optimal that act on F_P (variant-A) or F_P ∪ prohibited (variant-B).

**Variant-A vs Variant-B as construction primitive:**

The variant-A/B distinction is the methodology's central construction primitive. Each variant declares what it does not represent:

- **Variant-A** is constraint-conforming. It builds R_P(ε) using only the policy vocabulary F_P. It declares the *loss of prohibited-feature predictive value* — it cannot use what the policy excludes, even if those features would predict.
- **Variant-B** is constraint-relaxed. It builds a band using F_P ∪ prohibited features (e.g., demographic features). It declares the *loss of policy-conformance* — it admits the prohibited category at the cost of not adhering to the policy specification.

Together they form a **declared-loss pair**. The pair is a regulator-legible representation of *what the policy excludes and what excluding it costs*. The disagreement region between them (where variant-A and variant-B reach different decisions) is the methodology's most informative output — it names the population on which the policy-vs-prohibited tradeoff is operationally consequential.

The yanantin-lineage memo (`2026-05-16-declared-loss-complementary-ensembles-memo.md`) proposes reading this construction as a special case of declared-loss-complementary ensemble construction. The methodology adopts this as a *design recommendation* for future work — variants should be deliberately constructed on declared-loss axes — but does not retrospectively re-claim past work under that frame. The interpretation is supplementary; the construction recipe (above) is what the methodology commits to.

### Empirical record

- **Non-inferiority to SHAP/LIME**: established on LC pricing-space ([[project_shap_pricing_result]]; H0 not falsified) and on the initial SHAP-vs-Rashomon test ([[project_shap_non_inferiority_result]]; 4 SHAP-silence criteria fail to recover Rashomon T-silent-all). The construction matches post-hoc explainer outputs in accuracy of what they recover; its workflow advantages (no surrogate, FDR significance, policy-vocabulary keying, false-positive control) are independent of accuracy.
- **Cross-substrate robustness**: the construction works on LC (multiple vintages, by-grade), FM (3+ vintages, by demographic-saturation stratification), HMDA-RI (2022, by loan_purpose × income_decile). Substrate-specific findings are noted where they exist; the construction itself transfers.
- **Plurality is residual-dependent**: not every R_P(ε) has members that disagree on cases. The construction always produces a non-trivial band; whether the band has *bite* (genuine member-disagreement) depends on whether the within-tier residual is active at the substrate's chosen stratification. This is a property of the data, not a defect of the construction.

---

## 5. The disagreement region as regulatory artifact (formerly: adversarial pair routing)

The original §4 proposed adversarial-pair generation with recursive stipulation as a HITL routing mechanism: grant-side and deny-side advocates produce competing arguments; the human adjudicates the residue. With the routing principle falsified, the adversarial-pair construction does not disappear — it becomes a **presentation layer** for the disagreement region rather than a triage mechanism.

What the adversarial-pair construction is now:

1. **A method of presenting R_P(ε) disagreement to regulators and internal MRM.** The disagreement region is named by feature (per [[project_disagreement_geometry_result]]: d(x) is highly legible; recoverable by a depth-≤3 tree on 1–2 features per grade); the adversarial-pair presentation makes the disagreement's structure visible without requiring the reader to consume the full refinement set.
2. **A structural representation of the policy's residual indeterminacy.** Where the pair disagrees on cases, the policy admits multiple equally-defensible decisions. The pair surfaces *which population* is so situated and *what feature* drives the disagreement.
3. **Input to band-level effective challenge.** SR 11-7 expectations around effective challenge can consume the adversarial-pair presentation as a within-MRM challenge function (§8). The disagreement region is the artifact effective-challenge is conducted against.

What it is *not*, in light of the falsification:

- It is **not** a per-case HITL trigger. The original §3-§4 framing — "model disagrees on this case, escalate to human" — is empirically dead.
- It is **not** a substitute for human judgment on hard cases. Where the bank wants HITL, the placement decision must be made on grounds other than within-Rashomon disagreement (which is sign-flippy noise at the per-case level).

The stipulation mechanism (within-side, cross-side, focused HITL) and the challenger role from the original §4 survive as **presentation refinements** — they reduce the cognitive load of consuming the refinement-set artifact for human readers. The adversarial framing is *internal* to the bank's reasoning (both advocates represent the bank, not the bank-vs-applicant); this scope clarification carries forward.

---

## 6. Boundary sampling as evaluation paradigm

The methodology produces a natural post-hoc testing paradigm. Sample evaluation cases not from the operational distribution but from **the disagreement boundary of R_P(ε)** — cases where within-set disagreement is high. Operational sampling tells you about the easy cases, where most of the population lives. Boundary sampling stress-tests where the methodology's epistemic claim is most fragile and produces calibration data that operational sampling will not.

This is structurally analogous to active learning's "sample where the model is uncertain" move, but applied to *evaluation* rather than training. The validation question is whether the methodology's uncertainty signal corresponds to real ambiguity or is spurious. With routing falsified, this question gets a different operational meaning: not "do we route this case correctly?" but "does R_P(ε) disagreement track *anything* externally meaningful at the case level?" The boundary-sampling test corpus is the place to answer this.

The paradigm has clean defensibility for technical reviewers regardless of regulatory framing. It does not require buying into the larger architectural claims (refinement, observability, ECOA reframing) to find valuable. **If there is a near-term methods paper, this is candidate lead material** — the testing paradigm stands on its own merits and naturally sets up the refinement-set methodology as the framework boundary-sampling tests.

### Ethics caveat (preserved from original)

Stress-testing the methodology on cases where it is likely to be ambiguous means deliberately constructing or selecting hard cases. This is fine for retrospective evaluation; less obviously fine for prospective deployment of automated decisions on synthetic-hard cases. The ethics question goes into the open-problems section, not into the methodology itself.

---

## 7. ECOA reframing: refinement-set legibility as principal-reason regime

ECOA demands a singular principal reason because the appeal/accountability machinery requires attribution. Without *the* reason, an applicant cannot challenge it; without a discrete cause, no liability flows. The singularity is not accidental — it is the load-bearing fiction that lets the apparatus function.

But it is still a fiction. The same human loan officer, looking at the same data with the same guidance documents on different days, will produce different decisions in cases where the range of reasonable outcomes admits both refusal and allowance. The principal-reason notice is a post-hoc construction satisfying the legal requirement rather than reporting the actual decisional process.

The methodology's refinement-set is therefore not *worse* than the human at producing principal reasons. It is **more honest** about producing them. The human always was authoring one of several plausible attributions; the refinement-set just makes the multiplicity visible instead of hiding it under a single confident-sounding sentence.

This reframing strengthens the regulatory pitch rather than weakening it. *We give you a principal reason that we can show is robust under documented model uncertainty, and we name the population for which the policy admits multiple equally-defensible decisions* is a stronger epistemic claim than *this loan officer wrote down the first plausible reason that came to mind*.

### Refinement-set as principal-reason regime

With the routing claim falsified, the per-decision principal-reason still has to be produced somehow. The methodology's positive position:

- **For cases in R_P(ε)'s unanimous region** (members agree on the principal reason): the consensus principal reason is the notice's content. The refinement-set's existence is the audit trail demonstrating the principal reason is robust under documented model uncertainty.
- **For cases in R_P(ε)'s disagreement region**: the notice reports the policy-vocabulary feature that variant-A's members most often identified, *with the methodology's acknowledgment that the case falls in a region where the policy admits multiple equally-defensible reasons*. The methodology does not pretend to resolve this; it makes the indeterminacy auditable.

This is a structurally different ECOA posture than current practice. Whether it would survive litigation is an open question. But it is *honest* in a way the current post-hoc-rationalization regime is not.

---

## 8. MRM connection: band-level effective challenge

SR 11-7 requires effective challenge of models — a separate validation function that tests model outputs and assumptions. Standard implementation is a periodic independent validation team review.

The original methodology proposed operationalizing effective challenge at the per-decision level via within-Rashomon disagreement. With per-case routing falsified, this proposal fails. **The methodology operationalizes effective challenge at the band level instead.**

Band-level effective challenge:

1. **The refinement-set IS the effective-challenge function.** The within-R_P(ε) disagreement is the model's own surfacing of where its admissible variants disagree; the bank's MRM team consumes this as evidence of model uncertainty without having to construct an independent challenge model. The challenge function is in the artifact, not in a parallel organizational function.
2. **Aggregate disagreement statistics are model-risk signals.** Drift in the disagreement region's size, composition, or feature drivers across operational time is a model-risk indicator the MRM team can monitor. This is what survives of the original per-decision routing claim: aggregate-level disagreement-as-model-risk-surveillance is the survivor; per-case disagreement-as-triage is not.
3. **Population-level tier calibration** is a separate audit dimension that the methodology produces naturally. If tier-N loans default at rates significantly different from tier-N expected loss, the tier classification itself is miscalibrated — independent of whether any individual decision was right. Calibration testing is exactly what examiners look for and rarely find produced systematically.

The methodology does not exceed what SR 11-7 requires at the per-decision level (per-decision effective challenge is what the original claim aimed for, and that claim is now dead). It exceeds SR 11-7 at the **band level and the policy-vocabulary-adequacy level**, both of which are arguably more substantively useful than per-decision challenge anyway.

---

## 9. Pricing-tier extension

The binary grant/deny framing simplifies real banking. Decisions are tiered: deny, or grant at one of several rates corresponding to risk classifications. Folding this in changes the methodology in non-trivial ways.

**Decision boundary becomes a decision surface.** Members of R_P(ε) can agree on grant but disagree on tier, or disagree on grant/deny entirely. Tier-disagreement among grant-side members is methodology calibration; grant/deny disagreement is substantive controversy. The refinement-set construction extends naturally to tier boundaries: at each tier boundary there is an admissible-grant-at-this-tier set and an admissible-grant-at-next-tier-up set, with the disagreement region between them surfaced as the relevant artifact for that boundary.

**ECOA-machinery extends with it.** "Adverse action" includes less favorable terms than requested, which means the principal-reason apparatus applies to tier assignments, not just denials. Tier-disparity adverse-action notices are arguably the bigger fair-lending exposure than outright denials, because tier disparities scale across protected-class populations and produce disparate impact even when underwriting is neutral on the grant/deny axis.

### The pricing-space stratification finding

The original §8 treated pricing as a near-mechanical downstream projection given classification. The empirical work ([[project_pricing_space_cat2]]) refines this: **within-grade pricing-space stratification carries Cat 2 structure that binary categorical tests miss.** The Phase-2 finding (in the path-doc) reverses the binary null: every LC vintage shows within-grade Cat 2 structure when the test is run at the pricing-space granularity rather than the grade-categorical granularity.

The methodological consequence: pricing-space stratification is the right granularity for the refinement-set construction on continuously-priced products. The grade-categorical version was the wrong granularity for the structure the methodology is trying to surface. The construction (§4) is granularity-aware: on tier-structured products, stratify by grade; on continuously-priced products, stratify by within-grade pricing-space deciles.

### Decomposition: classification primary, pricing downstream — qualified

In many banks, credit decision (grant/deny/conditional) and pricing (rate given classification) are operationally separate. Refinement-set uncertainty concentrates in classification; pricing is a near-mechanical projection given the bank's capital structure, market conditions, and competitive position. The methodology can apply primarily to classification, with pricing as a downstream layer.

This simplification holds *if* the bank's processes separate cleanly that way. Integrated underwriting-pricing — increasingly common in algorithmic lending — breaks it, and the methodology has to handle the joint problem at the pricing-space stratification granularity (above).

---

## 10. The substrate-vs-stack axis as design constraint

The HMDA-RI substrate-transfer test ([[project_hmda_trimodal_result]]) surfaced a structural finding that reorganizes how the methodology positions its own verification machinery:

**The verifier — the discriminator-plus-calibrated-threshold used to assess whether a refinement-set's disagreement is informative — is itself substrate-indexed.** R²_named ≥ 0.30 calibrated on FM transferred as a *floor* that made `verdict_differs` structurally False on most HMDA cells. The calibrated threshold is not a substrate-neutral instrument; it is part of the artifact-stack the methodology deploys.

Operationally:

1. **The methodology's schema tuple has four slots, not three.** The artifact produced for any deployment is the 4-tuple: (variant-context, reorganization-flag, **verifier-context**, verdict-pair). Verifier-context must be declared per substrate; cross-substrate transfer of a verifier-calibration is a methodology error.
2. **Adequacy thresholds are calibrated per substrate.** The bank's MRM function and the examiner consume the refinement-set with a declared adequacy floor that is documented as substrate-specific. Transfer of an FM-calibrated threshold to HMDA is the kind of move the methodology must architecturally prevent.
3. **Reorganization-detection is substrate-invariant; phase-structure is substrate-specific.** The explainer-root-feature-tier discriminator ([[project_lc_centrality_posthoc]]) appears substrate-invariant on the evidence to date (validated on FM and LC). The trimodal phase-structure characterization ([[project_saturation_phase_characterization]]) is FM-substrate-validated only — the HMDA falsification ruled out the simpler "trimodal with sharp gaps" claim. Where the methodology needs a reorganization detector, the substrate-invariant one is preferred.

### Why this rewrites the methodology's regulatory posture

The original methodology presented its construction and routing claims as substrate-general. The substrate-vs-stack axis says **at least part of the methodology's machinery is substrate-indexical** and that this is a feature, not a bug, *provided the substrate-context is declared in the deployed artifact*.

The regulatory consequence is significant: it means that two banks deploying this methodology on different substrates (e.g., LC consumer credit vs FM mortgages vs HMDA-RI lending) are not running "the same methodology" in the verifier sense — they are running the construction methodology with substrate-specific verifier-context declarations. This is not a bug to hide; it is the methodology being honest about what its parts do.

---

## 11. Open problems

Carrying forward from the original §9 with updates:

- **Within-side aggregation.** How members of R_P(ε) with slightly different rationales merge into a single position for the disagreement-region presentation. This bottoms out in argument-equivalence under the banking ontology. Joe's collaboration is on the critical path. *Unchanged.*
- **Tractable proxy for refinement-set disagreement at decision time.** Enumerating R_P(ε) per case is intractable at scale. Likely there is a sufficient statistic empirically measurable without explicit enumeration. *With routing falsified, this matters less acutely — but still matters for boundary-sampling §6 and for aggregate model-risk surveillance §8.*
- **Reject inference.** The unobservable counterfactual remains structurally hard. Methodology should acknowledge rather than pretend to solve. *Unchanged.*
- **Cadence of posterior-to-deployment update.** Continuous update creates change-detection-vs-concept-drift problems; periodic update reintroduces fossil-shaped failure. Regulatory negotiation, not a fixed value. *Unchanged.*
- **Adversarial robustness of refinement-set construction.** If applicants (or counsel) understand that R_P(ε) disagreement is the methodology's informative output, can they craft applications that produce within-set disagreement and force the methodology's most-favorable principal reason? Open. *Reframed from "agreement-as-routing" — the adversarial target is no longer the routing decision but the refinement-set's regulator-legible artifact.*
- **Boundary-sampling test data ethics.** Constructing or selecting hard cases for evaluation is fine for retrospective use; less obviously fine for prospective deployment. *Unchanged.*
- **Verifier-context cross-substrate.** New. How is verifier-context declared, audited, and transferred in a way examiners can consume? §10 establishes the slot exists; the operational mechanism for declaring it on each deployment is open.
- **What "frame-coherence" really discriminates.** The frame-evocation discriminator's 0/3 pre-reg MISS ([[2026-05-15-frame-evocation-result-note.md]]) is either (a) a problem with the M3 operationalization, (b) a consequence of substrate-indexicality (§10), or (c) evidence that the discriminator-axis story is wrong altogether. Currently unresolved; the expanded-vintage pre-reg (`2026-05-15-expanded-vintage-replication-preregistration-note.md`, running) will inform but not settle this.
- **Declared-loss-complementarity as design principle.** The 2026-05-16 yanantin-lineage memo proposes deliberate declared-loss-axis construction for future variant pairs. Methodology accepts as forward-going recommendation (§4); whether to operationalize via the memo's §3b synthesized-control test is open.

---

## 12. Positioning notes

**General critique, not specific.** The methodology critiques a class of approaches: automating partial banking processes without accompanying explainability infrastructure creates verification gaps. This applies to current productized AI agent offerings across multiple vendors. A general critique ages better than a specific one. *Unchanged.*

**Methodology paper vs. consulting deliverable.** The work has shifted from documentation/audit through automation-with-calibrated-escalation (the falsified original framing) to **observability-first construction with substrate-aware verifier-context** (the current framing). The methodology generalizes well past banking — same structure applies anywhere there are multiple equally-good models, a legal demand for singular output, asymmetric costs of error, and substrate-dependent verifier calibration. Medical diagnosis, sentencing, content moderation, insurance underwriting. The paper this becomes is not a banking paper; banking is the worked example. *Refined from original; the shift away from automation-with-routing toward observability sharpens the cross-domain generalization claim.*

**Regulated-domain novelty profile.** Methodology that does not match what examiners are familiar with creates friction during validation, even when it is better. The methodology positions as *a refinement of methods examiners already know* (Rashomon analysis, MRM challenge, ECOA principal reason) *organized around a regulator-legible artifact*, rather than as *a new automated decision regime*. The second framing is what the original doc reached for and is what the falsification has cost; the first framing is what survives and is what is regulator-deployable. *Substantially updated.*

**Construction-paper-first ordering.** The methodology has accumulated empirical findings (§§2–4, 10) that justify a methods-paper-first publication strategy — write the construction methodology and its non-inferiority result as a standalone methods contribution, ahead of the position paper this methodology supports ([[project_rashomon_construction_first_paper]]). The construction paper inherits this doc's §§2, 4, 6, 10 as its technical core; the position paper inherits §§1, 3, 5, 7, 8, 9 as its regulatory and architectural argument. *New positioning, 2026-05-17.*

**IP hygiene.** The synthesis was developed in conversation May 6–7 2026, building on prior reasoning-trace and Rashomon-set work, and substantially revised on 2026-05-17 after ten days of empirical work. It precedes any Olorin engagement start. The synthesis is documented in git history (commits and OTS stamps) and in the dated working notes in `docs/superpowers/specs/`. Worth maintaining the timeline given the LOI's pre-existing IP provisions and Olorin's separate IP clause for engagement work product. *Unchanged in substance; updated with the 2026-05-17 revision date.*

---

*End of revision. Sections marked Unchanged are preserved from the May 6–7 2026 original; sections marked Substantially updated, Refined, Reframed, or New reflect the 2026-05-17 revision after the routing falsification. Open problems and positioning notes track the methodology's evolving epistemic state. The methodology is currently partially empirically grounded — construction (§4), non-inferiority (§4 referenced), refinement-set properties (§2), substrate-vs-stack axis (§10) all have published empirical support; observability principle (§3), refinement-set as ECOA regime (§7), band-level effective challenge (§8) are theoretically argued but not empirically tested in their current form. The methodology should be deployed with this empirical-vs-theoretical distinction declared.*
