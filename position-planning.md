# Position Paper: Planning Document

*Status: working notes capturing structural decisions made during drafting conversation. Updated as decisions are made. This file should travel with the paper drafts so the structural reasoning isn't lost when this conversation context is gone.*

## Working title

To be decided. Working candidates: *Empty-Chair Representation: A Framework for AI Governance in Community Banking*. *Architectures of Absence: AI Governance under the FS AI RMF*. The first is descriptive; the second is more pointed. Neither final.

## Audience and register

Researcher-to-regulator. Position paper, not architecture document, not academic paper, not vendor proposal. Tony Mason (wamason.com LLC) as author. Published as tech report initially, with arXiv cross-listing under cs.CY. Multi-venue strategy possible after initial publication: ABA channels, OCC bulletin commentary, FS AI RMF RFI when announced.

Target length: 20-30 pages tech-report format.

## Three earned positions (committed in conclusion, body must earn)

**Position 1.** AI governance frameworks in regulated decision contexts are coherent only insofar as they make absent parties audible to the parties present at the moment of decision. Controls that induce observable, auditable constraints represent absent parties; controls that assert representation without inducing constraint are decoration. The distinction is between governance and governance theater.

**Position 2.** Post-hoc explanation is structurally inadequate as a verification regime in adversarial contexts. Bank examination is structurally adversarial. Architectures relying on explanation-of-output build Potemkin accountability.

**Position 3.** Human oversight of AI-generated decisions, in current vendor form, does not address the verification gap. Reviewing an explanation is not verifying reasoning. Org-chart accountability without architectural verification is the dishonest middle.

**Underlying structural pattern (silence-manufacture).** All three positions are instances of one structural failure mode: an architecture suppresses access to ground truth in some domain, then produces a substitute artifact (a metric, a document, a signature, an explanation) that occupies the rhetorical position where evidence of ground truth should appear. The artifact is read as evidence; the suppression is read as endorsement; the architecture's continued operation depends on both readings remaining unchallenged. Naming this pattern explicitly is what makes the three positions cohere into a structural argument rather than a list of related concerns. See "Silence-manufacture as underlying structural pattern" below.

## Outline

**Section 1.** Opening movement. Frame, definitions, two categoricals. *Drafted; needs light foreshadowing of silence-manufacture pattern using silence-breaking language without yet naming the pattern as load-bearing.*

**Section 2.** The frame as method. BSA/AML worked example, six-chair enumeration, three controls walked through. Earns position 1. *Drafted (unrevised); revision integrating produced-silence distinction in progress. Pending extension: extend BSA/AML worked example to follow the SAR → high-risk designation → account closure → ChexSystems escalation, where produced silence operates at maximum strength by regulatory design (tipping-off prohibition under 31 USC §5318(g)(2) is legally-mandated silence-production). De-banking material — FDIC 2023 (4.2% unbanked / 14.2% underbanked, 5x Black/white disparity), Cato PA 1009 (8,361 complaints / 35 mentioning political/religious; majority structurally governmental) — anchors the example empirically.*

**Section 3.** Verification regimes as taxonomic move. AI uses categorized by verification-regime availability rather than risk-tier. Earns positions 2 and 3. *Drafted: lending primary with underwriting turn near the end. Both standalone alternatives also preserved (position-section3-lending.md, position-section3-underwriting.md, position-section3-comparison.md) in case the integrated version needs disassembly.*

**Section 4.** Diagnostic techniques. *Pages missing from the ledger.* Empty-chair enumeration, pages-missing, produced-silence question pair as the three techniques. Architect-primary register, with examination-time application as turn near the end. Examiner-primary alternatives preserved as Paper 3 material. Frame becomes operational here. *Three-version drafting: position-section4-architect.md (selected), position-section4-examiner.md (Paper 3 material), position-section4-comparison.md, plus position-conclusion-examiner-test.md (rigor test that determined architectural register; also Paper 3 material). Integrated version pending. **Pending integration must promote silence-manufacture to organizing concept of the section** — this is where the unification gets concentrated development per placement decision (not distributed across sections). The three diagnostic techniques are silence-breaking instruments against silence-manufactured artifacts; naming the pattern here is what makes Sections 5–7's recommendations cohere rather than read as a list. See "Silence-manufacture" section below for full development.*

**Section 5.** Architectural primitive categories. Property-level only, not implementation specs. Quarry section — material accumulates, then most of it moves to Paper 2 (architecture document). Sections 4 and 5 may merge during drafting if the diagnostic and the primitive collapse cleanly. *Pending light revision: opening framing should explicitly name the four primitives as silence-breaking instruments rather than metric-improvement instruments. The content already does this; the framing should make it explicit so readers don't read the primitives through a Goodhart lens.*

**Section 6.** Honest uncertainties. Coordination problem at examination time. Conflict between empty chairs and prioritization. Diagnosis-vs-prescription tension. Vocabulary co-optation risk. *Pending addition: brittleness acknowledgment for the silence-manufacture unification (a reader who rejects the unifying pattern rejects the paper's structural claim at one shot; this is a deliberate trade-off — a unified position paper is less brittle in practice than a list of related claims, but the unification deserves explicit marking). Also pending: the regulatory-reform-failure prediction the frame makes — Goodhart-shaped fixes (better metrics, harder-to-game targets) are inadequate against silence-manufacture because the problem isn't a corrupted metric but a manufactured substitute under suppression. Reform that lives at the metric layer leaves the silence-production architecture intact, which manufactures new substitutes that pass new metrics. The persistence of compliance theater across reform cycles is evidence of this prediction operating.*

**Section 7.** Implications and follow-on work. *Conclusion drafted; pending revision to add silence-manufacture callback and partitioned-literatures closing move. The de-banking discourse — Cato 2026 reading the phenomenon as governmental debanking, unbankedamerica.org reading it as access barriers, both reading the same FDIC numbers, neither reconstructing the other's view because the architecture continues producing the silence — is the canonical real-time example of the prediction the frame makes about analytical literatures partitioning around silence-producing architectures.*

## Worked example choices and the unusual/canonical alternation

Sections in this paper alternate between unusual and canonical worked examples. The principle is load management: unusual examples buy intellectual leverage and shift attention from pattern-matching, but a paper that *always* takes the unusual path risks dismissal as contrarian. Mixing the two preserves the unusual choices' value where they matter most while filling in canonical choices to maintain reader trust. The unusual/canonical pattern is itself a structural choice in the paper's overall posture.

**Section 2: BSA/AML transaction monitoring (unusual).** Chosen because (a) lending is the obvious choice and confirms what readers already believe rather than testing the frame, (b) BSA/AML has plural conflicting empty chairs which forces the frame to do real work, (c) less expected so shifts attention from pattern-matching (especially for LLM reviewers).

**Section 3: Lending primary, with pricing turn (canonical).** Chosen because Section 2 already took the unusual path; Section 3 earns positions 2 and 3 at maximum defensibility by demonstrating the categoricals at the canonical regulatory location (adverse action notices under ECOA / Reg B). The pricing turn at the end demonstrates that the frame extends to less-developed regulatory spaces and that produced absence is the dominant failure mode there. The hybrid approach uses the canonical example to earn the categoricals and the unusual example to extend the frame's reach.

The pressure-test artifact (position-section3-comparison.md) preserves the structural reasoning behind the choice. Both standalone alternatives are also preserved in case the integration needs disassembly.

## Six empty chairs in BSA/AML monitoring

1. Next victim of fraud (structural absence — they don't yet exist)
2. False-positive customer (mixed: present in record, absent from decision context; produced silence in non-appeal)
3. Marginalized customer (mixed: structural in training distribution gap, produced in appeal-cost dynamic)
4. Institution's future self (structural absence — doesn't yet exist)
5. Financial system (structural absence — no embodied agent)
6. Criminal (structural absence by intentional design)

## Structural / produced absence distinction (per Tony's appeals observation)

*Some chairs are empty because the architecture has not yet given them a seat; others are empty because the architecture has produced their silence.*

Diagnostic moves differ:
- For structural absence: *how does the architecture make this party audible?*
- For produced absence: *what is the architecture doing that creates this silence, and what is it inferring from the silence it created?*

The second question applied to compliance theater: *the absence of regulatory enforcement against compliance theater is partly because compliance theater succeeds at producing silence, not because compliance theater is adequate.*

This is a frame-level addition. Section 1 needs a sentence acknowledging it; Section 2's enumeration needs to flag which chairs are which type; Section 4 needs to develop the diagnostic-on-produced-silence move.

## Silence-manufacture as underlying structural pattern

The three earned positions are instances of one structural failure mode. Naming the pattern is the paper's load-bearing structural claim, sitting beneath the empty-chair frame as the explanation for why empty chairs persist and why post-hoc explanation, human-on-explanation, and compliance theater all fail in the same way.

### Definition

**Silence-manufacture**: an architecture suppresses access to ground truth in some domain, then produces a substitute artifact (a metric, a document, a signature, an explanation) that occupies the rhetorical position where evidence of ground truth should appear. The artifact is read as evidence; the suppression is read as endorsement; the architecture's continued operation depends on both readings remaining unchallenged.

Silence is the *enabling condition*; substitution is the *active mechanism*. The artifact is real (a Shapley value, an audit document, a signed adverse-action notice), but it does not bind to what it claims to bind to. The binding is architecturally suppressed. The artifact's apparent epistemic content — *this represents the underlying reasoning / decision-making / oversight* — is sustained by the architecture's suppression of what would falsify the claim.

### Relationship to Goodhart's law

Silence-manufacture is the *dual* of Goodhart's law, not strictly its inverse. (Earlier drafting framed it as inverse-Goodhart; "dual" is more precise — Goodhart describes optimization corrupting metrics, silence-manufacture describes suppression manufacturing them. They are related through structural symmetry rather than through direction-reversal.)

- **Goodhart's law**: optimization pressure on a metric corrupts the metric. Pressure lands on the visible; the visible breaks.
- **Silence-manufacture**: suppression pressure on disconfirming evidence sustains the metric's apparent validity. Pressure lands on the invisible; the visible appears intact because what would falsify it has been architecturally suppressed.

The Goodhart relationship is rhetorically useful as a *pointer* — it gives readers a known landmark to anchor the unfamiliar claim — but should not carry the load-bearing name. The frame's name is silence-manufacture; the Goodhart connection is described as the dual.

Tightest parallel formulation: *Goodhart: when a measure becomes a target, it ceases to be a good measure. Silence-manufacture: when silence becomes a measure, it ceases to be evidence of the absence it appears to indicate.* "No complaints," "no SARs from this customer," "no incidents reported," "no harassment claims filed" — silence used as a metric is reliable only when there is no architectural pressure on producing the silence. When the architecture suppresses what would falsify the metric, silence is a manufactured artifact, not evidence.

### Mapping to the three categoricals

Each of the three earned positions is a silence-manufacture instance:

- **Position 2 (post-hoc explanation fails adversarially).** The model's actual reasoning is architecturally inaccessible to the explanation channel. The explanation (Shapley value, LIME approximation, attention-attribution heatmap) is generated by the same loop that produced the decision. The explanation occupies the rhetorical position the reasoning should occupy. The artifact is real; the binding to actual reasoning is architecturally suppressed. The empirical signature in ML is chain-of-thought unfaithfulness (Lanham et al. 2023, Turpin et al. 2023): CoT can be perturbed without changing the answer, changed without perturbing the answer, indicating the explanation is not bound to the underlying computation.

- **Position 3 (human-on-explanation is the dishonest middle).** The reviewer can only see what the architecture has chosen to expose; the underlying reasoning is suppressed from their view. The signature attests to review of the explanation, not verification of the reasoning. The signature occupies the rhetorical position of accountability. The empirical signature in ML is sycophancy and RLHF reward hacking — models optimize for signals visible to human evaluators, and human approval becomes a metric for what the model has produced rather than for the model's quality.

- **Position 1 (governance vs. governance theater).** Compliance theater is the population-level instance: institutions produce documentation that satisfies a framework; the contemporaneous decision-making is architecturally suppressed; the documentation is read as evidence of the suppressed decision-making. The empirical signature is benchmark gaming, eval-set contamination, and the Goodhart-on-safety-evals literature: metrics survive while the underlying construct degrades, and the architecture reads metric-stability as evidence of construct-stability.

The mapping makes the three categoricals into instances of one structural claim with empirical confirmation from a completely different research community (ML alignment / interpretability). This is unusual cross-domain confirmation that strengthens the structural argument substantially — the position paper's claim is not "regulatory practice should change" but "self-measuring architectures cannot verify themselves; here are observable failure modes confirming the claim from both regulatory experience and ML research; both research communities have been describing piecemeal what the empty-chair frame unifies."

### What silence-manufacture predicts

The frame makes specific predictions that distinguish it from Goodhart-shaped critique:

1. **Goodhart-shaped reform fails predictably.** Policy responses that target the visible metric ("improve the controls," "tighten the definitions," "raise the thresholds") leave silence-manufacture intact. The silence-production architecture manufactures new substitutes that pass the new metrics. Reform succeeds at improving documentation; documentation continues to substitute for ground truth; nothing structural changes. The persistence of compliance theater across reform cycles is the prediction operating. The fix has to live at the silence layer (transparency, contemporaneous capture, evidence binding) not the metric layer.

2. **Analytical literatures partition around silence-producing architectures.** When an architecture produces silence about its causal mechanism, observers positioned differently relative to the architecture see different absent parties, reconstruct different stories, and the stories do not converge with more research because the architecture continues producing the silence. Each partition is *internally coherent*; reconstruction requires breaking the silence, not adding observers. Persistent partitioned literatures whose disagreements don't converge with substantial research investment are the signature of operating silence-producing architectures.

3. **Silence-producing architectures distort political discourse in characteristic ways.** When the architecture suppresses the actual cause of harm, narratives that fill the suppression-shaped gap will be wrong in specific ways, and the wrongness will have political consequences the architecture cannot correct. The de-banking discourse is the canonical real-time example — political-debanking framing fills a silence the BSA/AML regime legally produced; the framing is empirically wrong (Cato 2026: 35 of 8,361 complaints mention political/religious motivations) but predictably-wrong-in-the-shape-the-silence-makes-available.

### Placement decisions

- **Concentrated development in Section 4**, not distributed across sections. Distributed presentation risks the unification becoming so soft that readers don't catch it at any single moment. One clear statement in Section 4 lets readers anchor; foreshadowing in Section 1 and callback in Section 6/7 ensure the anchor doesn't feel sudden when it arrives.
- **Section 1 foreshadows** with silence-breaking language ("audible," "made visible") without yet naming silence-manufacture as the load-bearing pattern.
- **Section 4 names and develops** silence-manufacture as the organizing concept for the three diagnostic techniques. The techniques are silence-breaking instruments; their value is in what they make audible that the architecture had suppressed.
- **Section 6 acknowledges brittleness** of the unification (rejecting silence-manufacture rejects the paper's structural claim in one shot — deliberate trade-off, but worth marking) and develops the regulatory-reform-failure prediction.
- **Section 7 callback and partitioned-literatures closing move.** The de-banking discourse as canonical example of the prediction observed in real time.

### Justification trade-off (analytical vs. rhetorical)

The frame's structural correctness is the analytical justification for inclusion. The rhetorical effect — preventing readers from reading the recommendations as weak Goodhart-fixes when they are silence-breaking primitives — is a downstream benefit, not part of the justification. Both motivations point in the same direction without being identical; the structural correctness is what justifies the inclusion, the rhetorical benefit is observed afterward.

### Outstanding questions

- Does "silence-manufacture" survive Section 6's vocabulary co-optation analysis? Any term load-bearing enough to organize the paper's structural claim is also load-bearing enough to be co-opted by the institutions whose practices the term critiques. Worth thinking through whether silence-manufacture is more or less co-optation-resistant than alternatives.
- Should the dual-of-Goodhart relationship be developed more prominently, or kept as a pointer? Risk of developing too prominently: the paper becomes about Goodhart's law extended, when its actual contribution is the empty-chair frame with silence-manufacture as the structural pattern. Risk of keeping minimal: readers without the Goodhart anchor have a harder time locating the claim.
- Does silence-manufacture want a dedicated subsection in Section 4, or should it appear as the section's organizing concept throughout? The latter is more integrated; the former is easier for readers to find and cite.

## De-banking material as empirical anchor

Material acquired during drafting that anchors Section 2's BSA/AML worked example empirically:

**FDIC 2023 National Survey of Unbanked and Underbanked Households** (cited via FDIC press release, October 2024).
- 4.2% of US households unbanked (5.6 million households)
- 14.2% underbanked (19.0 million households)
- Black households: 10.6% unbanked; Hispanic: 9.5%; American Indian/Alaska Native: 12.2%; White: 1.9%
- Lower-income, less-educated, disabled, single-parent households disproportionately unbanked
- Methodology stable across years; demographic disparities persistent
- Provides population-scale anchor for "this isn't a niche phenomenon"

**Cato Institute Policy Analysis 1009** (Anthony, January 8, 2026) — *Understanding Debanking* (file: references/PA 1009.pdf).
- Reuters review of 8,361 account closure complaints; only 35 mentioned politics, religion, conservative, or Christian (≤0.5%)
- Selection bias should *inflate* political-debanking attribution (customers who don't know the cause attribute to locally-available narrative); 35/8361 is therefore stronger evidence than naive complaint-data interpretation suggests
- High-profile cases (Trump Org post-Jan 6, Knowles, Indigenous Advance Ministries, NCRF) collapse on examination into governmental debanking driven by AML/KYC compliance pressure
- Mechanism: structuring SAR → "high-risk" examiner designation → account closure → 31 USC §5318(g)(2) tipping-off prohibition prevents disclosure → ChexSystems entry propagates exclusion across federation
- Cato's lead policy recommendation: repeal 31 USC §5318(g)(2), 12 USC §3420(b), 18 USC §1510 — let banks tell customers why accounts were closed. This is structurally identical to the empty-chair "make the absent party audible" move.
- Use Cato for empirics, not for broader policy conclusion (BSA repeal). The empirical analysis is independent of the libertarian policy prescription; the paper can cite the empirics without adopting the conclusion.

**Atlas of Financial Inclusion** (unbankedamerica.org).
- Visualization-oriented site; uses FDIC arithmetic to derive "62 million Americans unbanked or underbanked"
- Frames the issue as access barriers (fees, ID requirements, mistrust) rather than BSA/AML pressure
- Disagrees with Cato about *cause* of the same phenomenon, while using the same FDIC data
- Disagreement is itself informative: each analysis sees the absent party it is positioned to see; neither reconstructs the other's view; reconstruction requires breaking the silence the BSA/AML regime legally produces. This is the partitioned-literatures pattern in real time.

**OCC December 2025 preliminary supervisory review.** Existence confirmed via Reuters reporting (December 10, 2025) and references on OCC website; document temporarily inaccessible (site maintenance). Cato (January 2026) does not cite — likely publication-cycle timing. Worth chasing when accessible. Citation placeholder until verified: *[OCC December 2025 preliminary review on bank derisking, citation pending verification]*.

### How the de-banking material lands in the paper

- **Section 2's worked example escalates.** Currently stops at transaction monitoring (flags, false-positive rates). Extension follows the SAR → high-risk → closure → ChexSystems pipeline, which is where produced silence operates at maximum strength by regulatory design.
- **Section 7 closing move.** The Cato/unbankedamerica.org partition, viewed against shared FDIC data, is the canonical real-time example of partitioned-literatures-around-silence-producing-architectures.
- **Population scale.** FDIC numbers move the paper from "structural argument with regulatory analogy" to "structural argument with population-scale empirical confirmation." 4.2% unbanked + 14.2% underbanked + 5x demographic disparity is enough to anchor the urgency without polemic.
- **The "produced silence has political consequences" observation.** The political-debanking discourse is itself a silence-manufacture artifact: legal silence created the unfillable causal gap; public discourse filled the gap with locally-available narrative; the narrative is empirically wrong but predictably-wrong-in-the-silence's-shape. This is a meta-instance the paper can cite as evidence the frame makes contentful predictions about discourse, not just architecture.

## Citation status

Confirmed real and properly representable:
- arxiv 2602.01368 (Evite, Svetlova, Bucur — Trade-offs in Financial AI: trilemma. Use actual three poles: accuracy, compliance, ease of understanding.)
- CIGI Paper 296 (Witzel, Gonnet, Snider — challenge post-hoc explanations)
- Sullcrom April 2026 model risk guidance memo (April 17, 2026 revised guidance, $30B threshold, GenAI exclusion, promised RFI)
- Bordt et al. arxiv 2201.10295 (post-hoc explanations fail in adversarial contexts) — found via verification pass, central to position 2
- Nick Oh arxiv 2412.17883 (defense of post-hoc) — counterposition for honest engagement
- FDIC 2024 press release on 2023 National Survey of Unbanked and Underbanked Households (4.2% / 14.2% / demographic disparities) — Section 2 empirical anchor
- Cato Institute PA 1009 (Anthony, January 2026, *Understanding Debanking*; file at references/PA 1009.pdf) — Section 2 empirical anchor and Section 7 partitioned-literatures example. Cite for empirics, not policy conclusion.
- unbankedamerica.org *Atlas of Financial Inclusion* — visualization-oriented secondary source; useful as the partition-counterpart to Cato in Section 7's partitioned-literatures move
- 31 USC §5318(g)(2) — tipping-off prohibition; legally-mandated silence-production; central to BSA/AML escalation example

Needs citation but not yet sourced (per Tony's documentation observation):
- "Models trained on historical SAR data inherit historical flagging biases" — empirical claim, needs FinCEN advisory or equivalent
- "Reviewer self-reports are systematically poor at this binding under time pressure and case volume" — Nisbett & Wilson 1977 plus operational decision-making literature
- Disparate-impact in BSA/AML monitoring — strongest evidence available
- Cross-institution displacement effects in money laundering — FinCEN-funded research likely exists
- Treasury/CRI commentary anchor for "systems blueprint" framing
- FS AI RMF release date and content for opening paragraph anchor
- OCC December 2025 preliminary supervisory review on bank derisking — existence confirmed via Reuters December 10, 2025 reporting and OCC website references; document temporarily inaccessible during drafting (site maintenance). Verify and cite directly when accessible.
- ChexSystems / Early Warning Services federation effects — for Section 2 escalation, the cross-bank exclusion mechanism. Likely needs CFPB or industry-association source.
- Lanham et al. 2023 / Turpin et al. 2023 — for Section 4 silence-manufacture mapping to chain-of-thought unfaithfulness. Already in Section 1 citation list; promote to Section 4 as empirical confirmation of the structural claim.
- Sycophancy / RLHF reward hacking literature (Sharma et al., Perez et al.) — for Section 4 silence-manufacture mapping to human-on-explanation. Cross-domain confirmation from ML alignment.
- Goodhart 1975 / Strathern 1997 — for Section 4 silence-manufacture/Goodhart dual relationship.

Citation deployment principle: every empirical claim either gets cited or rewritten as "the frame implies that..." or "we argue that, structurally..." Marking unsupported claims now; sourcing pass after body is structurally settled.

## Review process

*No paper we create and publish will skip the part about being reviewed by rikuy.*

Rikuy review is the gatekeeper before publication. My role is first-pass triage and drafting; rikuy is final verification.

## Voice and authorship

Tony Mason (wamason.com LLC) as author. Conversational drafting assistance from Claude (Anthropic) acknowledged or not as Tony decides — neither required nor preferable as a default. Tony's voice is present through frame, categoricals, structural decisions, and review of all generated text. The wander that produced the frame is in the conversation history dossiers and is the substantive intellectual contribution.

## Follow-on papers downstream of this one

This paper is Paper 1 in what now appears to be a three-paper structure rather than a two-paper structure:

**Paper 1 (this one).** Position paper. Empty-chair representation as organizing principle for AI governance under the FS AI RMF. Frame, categoricals, diagnostic techniques at property level, primitive categories at property level. Researcher-to-regulator register, architectural commitments load-bearing.

**Paper 2.** Architecture specification. Primitive categories from Paper 1's Section 5 specified at implementation-ready level. Tamper-evident temporal capture, evidence binding, three-dimensional confidence characterization, structural drift typology, diagnostic instrumentation. Builder audience. The strawman material that informs Section 5 is Paper 2's primary input.

**Paper 3.** Examination methodology. Empty-chair frame applied as examination-time methodology. Diagnostic techniques as examiner's repertoire. Examiner-primary register throughout. Regulator audience, examination-practice register. Inputs include position-section4-examiner.md (the architect-primary draft's examiner counterpart) and position-conclusion-examiner-test.md (the rigor test that determined Paper 1 should be architectural rather than examiner register).

**Paper 4 (newly distinguished, possibly).** *Partitioned Literatures*: methodological paper on how silence-producing architectures partition their analytical literatures, with persistent non-convergent disagreement as the partition's signature. Generalizes silence-manufacture beyond banking to AI eval-vs-deployment, NDA'd workplace harassment, pharma efficacy reporting, algorithmic content moderation, intelligence-community oversight. Audience: social scientists and methodologists of empirical inquiry. The methodological contribution: a diagnostic for distinguishing values disputes from structurally-induced literature partitions. Banking/de-banking would be the first worked example. This paper emerged from the wander during Paper 1 drafting and is currently a candidate, not a commitment. The de-banking discourse (Cato vs. unbankedamerica.org viewing the same FDIC numbers and reconstructing different causal accounts) is the canonical real-time example that would anchor it. The fundamental claim: *persistent partitioned literatures whose disagreements don't converge with substantial research investment are evidence of operating silence-producing architectures, and resolution requires architectural change rather than additional empirical work within partitions.* Decide whether to commit after Paper 1 publication.

The current Paper 1 conclusion gestures at "follow-on work for implementation specification" in the singular. With Papers 3 and 4 now distinguished, the gesture should reflect downstream work as plural. Not a Paper 1 revision needed now; track for revision pass after body sections drafted.

## Operational notes

- Multi-pass approach: this is one of multiple sessions. Important things will reappear if missed.
- Per-section files rather than one growing document. Current files: position-opening.md, position-conclusion.md, position-section2.md, position-section2-unrevised.md, position-section3.md, position-section3-lending.md, position-section3-underwriting.md, position-section3-comparison.md, position-section4-architect.md, position-section4-examiner.md (Paper 3 material), position-section4-comparison.md, position-conclusion-examiner-test.md (Paper 3 material), position-planning.md.
- For sections where the frame's value may be non-uniform across worked examples, comparative drafting (two versions plus comparison artifact) is the default rather than the exception. The comparison artifact's value is in preserving genuine non-uniformity rather than collapsing it to a recommendation. Sections 4 and 5 likely benefit from this approach.
- References folder (references/) holds source documents: PA 1009.pdf (Cato 2026). Add OCC December 2025 review when accessible.
- After body sections drafted, full citation pass.
- After draft complete, Tony moves to new project, converts to LaTeX format.
- Rikuy review before publication.

## Pending revisions queue (in order of priority)

These are tracked here so a subsequent drafting session can pick them up without losing the structural decisions:

1. **Section 1**: light foreshadowing of silence-manufacture using silence-breaking language; do not name the pattern as load-bearing here. *Partial — opening foreshadowing addition staged.*
2. **Section 4 integration**: promote silence-manufacture to organizing concept of the section. The three diagnostic techniques are silence-breaking instruments against silence-manufactured artifacts. Develop the dual-of-Goodhart relationship as a pointer (not load-bearing). Map the three categoricals onto silence-manufacture instances with empirical confirmation from ML alignment (chain-of-thought unfaithfulness, sycophancy, benchmark gaming). *Pending; integrated version of Section 4 not yet drafted.*
3. **Section 7 conclusion revision**: callback to silence-manufacture; closing move on partitioned-literatures using the de-banking discourse as canonical real-time example; closing line about architecting deliberately. *Partial — conclusion partitioned-literatures addition staged.*
4. **Section 2 BSA/AML walk-through extension**: extend the worked example to follow the SAR → high-risk → closure → ChexSystems escalation; integrate FDIC and Cato empirical anchors; flag which controls are silence-manufacture cases. *Pending.*
5. **Section 5 framing tweak**: opening sentences should explicitly name the four primitives as silence-breaking instruments rather than metric-improvement instruments. The content already does this; the framing should make it explicit. *Pending.*
6. **Section 6 additions**: brittleness acknowledgment (rejecting silence-manufacture rejects the paper's structural claim in one shot — deliberate trade-off); regulatory-reform-failure prediction (Goodhart-shaped fixes leave silence-production architecture intact). *Pending.*
7. **Vocabulary co-optation analysis** (Section 6): does "silence-manufacture" survive co-optation pressure? Worth thinking through whether silence-manufacture is more or less co-optation-resistant than alternatives. *Pending.*

## Methodological observation (not necessarily for the paper)

The frame's two major structural moves — the structural-versus-produced-absence distinction, and silence-manufacture as the underlying pattern unifying the three categoricals — both emerged from observations *outside* the drafted material rather than from inside it. Both came from Tony's wander rather than from internal coherence-checking on the existing drafts. The drafting tightens what's already there; the wander finds the structure that was implicit. This is the productive mode the paper has relied on. If a methodology note ever gets written about LLM-assisted position-paper drafting, this pattern is the canonical observation: the assistant maintains coherence within the drafted material; the human's observations from outside the drafted material reveal structural features the assistant cannot see from inside, because the structure is in the relationship between the drafts rather than in any individual draft. Rikuy adversarial review is a structural complement to this — it provides the *external* pressure-test that catches drift the internal coherence-check misses.

This is also a small private instance of the paper's argument: the drafted material is a self-measuring architecture; the wander is the exterior observer. Without the exterior observer, the drafts cohere internally without the structural pattern they implicitly rely on becoming visible.
