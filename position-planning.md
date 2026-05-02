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

## Outline

**Section 1.** Opening movement. Frame, definitions, two categoricals. *Drafted.*

**Section 2.** The frame as method. BSA/AML worked example, six-chair enumeration, three controls walked through. Earns position 1. *Drafted (unrevised); revision integrating produced-silence distinction in progress.*

**Section 3.** Verification regimes as taxonomic move. AI uses categorized by verification-regime availability rather than risk-tier. Earns positions 2 and 3. *Drafted: lending primary with underwriting turn near the end. Both standalone alternatives also preserved (position-section3-lending.md, position-section3-underwriting.md, position-section3-comparison.md) in case the integrated version needs disassembly.*

**Section 4.** Diagnostic techniques. *Pages missing from the ledger.* Empty-chair enumeration, pages-missing, produced-silence question pair as the three techniques. Architect-primary register, with examination-time application as turn near the end. Examiner-primary alternatives preserved as Paper 3 material. Frame becomes operational here. *Three-version drafting: position-section4-architect.md (selected), position-section4-examiner.md (Paper 3 material), position-section4-comparison.md, plus position-conclusion-examiner-test.md (rigor test that determined architectural register; also Paper 3 material). Integrated version pending.*

**Section 5.** Architectural primitive categories. Property-level only, not implementation specs. Quarry section — material accumulates, then most of it moves to Paper 2 (architecture document). Sections 4 and 5 may merge during drafting if the diagnostic and the primitive collapse cleanly.

**Section 6.** Honest uncertainties. Coordination problem at examination time. Conflict between empty chairs and prioritization. Diagnosis-vs-prescription tension. Vocabulary co-optation risk.

**Section 7.** Implications and follow-on work. *Conclusion drafted.*

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

## Citation status

Confirmed real and properly representable:
- arxiv 2602.01368 (Evite, Svetlova, Bucur — Trade-offs in Financial AI: trilemma. Use actual three poles: accuracy, compliance, ease of understanding.)
- CIGI Paper 296 (Witzel, Gonnet, Snider — challenge post-hoc explanations)
- Sullcrom April 2026 model risk guidance memo (April 17, 2026 revised guidance, $30B threshold, GenAI exclusion, promised RFI)
- Bordt et al. arxiv 2201.10295 (post-hoc explanations fail in adversarial contexts) — found via verification pass, central to position 2
- Nick Oh arxiv 2412.17883 (defense of post-hoc) — counterposition for honest engagement

Needs citation but not yet sourced (per Tony's documentation observation):
- "Models trained on historical SAR data inherit historical flagging biases" — empirical claim, needs FinCEN advisory or equivalent
- "Reviewer self-reports are systematically poor at this binding under time pressure and case volume" — Nisbett & Wilson 1977 plus operational decision-making literature
- Disparate-impact in BSA/AML monitoring — strongest evidence available
- Cross-institution displacement effects in money laundering — FinCEN-funded research likely exists
- Treasury/CRI commentary anchor for "systems blueprint" framing
- FS AI RMF release date and content for opening paragraph anchor

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

The current Paper 1 conclusion gestures at "follow-on work for implementation specification" in the singular. With Paper 3 now distinguished, the gesture should reflect both downstream papers. Not a Paper 1 revision needed now; track for revision pass after body sections drafted.

## Operational notes

- Multi-pass approach: this is one of multiple sessions. Important things will reappear if missed.
- Per-section files rather than one growing document. Current files: position-opening.md, position-conclusion.md, position-section2.md, position-section2-unrevised.md, position-section3.md, position-section3-lending.md, position-section3-underwriting.md, position-section3-comparison.md, position-section4-architect.md, position-section4-examiner.md (Paper 3 material), position-section4-comparison.md, position-conclusion-examiner-test.md (Paper 3 material), position-planning.md.
- For sections where the frame's value may be non-uniform across worked examples, comparative drafting (two versions plus comparison artifact) is the default rather than the exception. The comparison artifact's value is in preserving genuine non-uniformity rather than collapsing it to a recommendation. Sections 4 and 5 likely benefit from this approach.
- After body sections drafted, full citation pass.
- After draft complete, Tony moves to new project, converts to LaTeX format.
- Rikuy review before publication.
