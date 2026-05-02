# Section 3 Pressure Test: Lending vs. Underwriting

*Status: comparison artifact. The two drafts (position-section3-lending.md and position-section3-underwriting.md) attack the same task from different examples. This document examines what each does that the other doesn't, where each is weaker, and what the comparison reveals about the frame.*

## What each version is trying to do

Both versions earn positions 2 and 3 from the conclusion: post-hoc explanation as structurally inadequate verification regime in adversarial contexts; human oversight of explanations as not a verification regime. Both make the taxonomic move dividing AI applications into verification-available and verification-unavailable categories. Both maintain the structural-not-gradational character of the line.

The difference is in *which dimension of the dishonest middle* each example illuminates most sharply.

Lending illuminates the dishonest middle as **inadequate verification of an artifact that exists**. Adverse action notices are the artifact; the regulatory regime requires them; they are produced; the dishonest middle is in the gap between what the artifact claims and what the artifact is.

Underwriting illuminates the dishonest middle as **architectural production of empty-chair silence**. There is no artifact; the regulatory regime does not require one; the customer's silence after accepting the offered rate is read as endorsement of the rate.

These are different failure modes of representation. Lending's failure is *misrepresentation* — the artifact misrepresents the reasoning. Underwriting's failure is *non-representation* — there is no artifact, and the absence of complaint is read as non-need for one.

## Where each is stronger

**Lending is stronger at:**

- Earning position 3 (human oversight as verification gap) directly. Adverse action notices have human signatures attached; the gap between signature and verification is the canonical case the categorical addresses. The reader who has a vague intuition about the inadequacy of "human in the loop" gets the intuition sharpened at the regulatory location designed for precisely this concern.

- Connecting to existing regulatory discourse. ECOA / Reg B / FCRA have decades of jurisprudence; the CFPB has issued recent guidance specifically on adverse action notices and AI; the regulatory community has standing concerns about AI-generated notices. The example lands in a conversation already happening, and the frame contributes to that conversation.

- Demonstrating the categorical at its most defensible point. If the reader rejects the categorical applied to lending, the categorical falls. So earning it at the strongest point matters.

**Underwriting is stronger at:**

- Earning the produced-absence frame from Section 2 with a sharper case. The marginalized-customer treatment in Section 2 had produced-absence as a secondary dimension; the underwriting example puts produced absence at the center. The frame's structural-vs-produced distinction gets developed where the produced dimension dominates.

- Demonstrating the frame's reach into regulatory spaces the regulation has not yet designed for. Lending shows the frame applied to a problem the regulation already names; underwriting shows the frame applied to a problem the regulation has not yet recognized. The latter is the more ambitious claim — that the frame produces interpretive leverage on absent-party representation in spaces where the empty chair is not yet a regulatory subject.

- Sharpening the produced-silence diagnostic. The aggregate-validation rejoinder ("statistical validation against outcomes verifies the model") gets dismantled most cleanly in the pricing context, where the gap between aggregate and individual representation is most visible.

- Surprise. Lending is the obvious example. Pricing is less expected. The Section 2 reasoning for choosing BSA/AML over lending applies to Section 3 too: surprise shifts attention from pattern-matching, which matters for human reviewers and probably more for LLM reviewers.

## Where each is weaker

**Lending weakness:** The example is canonical, which means readers come to it with prior commitments. Readers who already believe AI adverse action notices are problematic get confirmation; readers who don't believe it get the case argued at terrain where they have entrenched positions. The frame may not get tested so much as deployed against existing positions.

**Lending weakness:** The categorical is most directly demonstrated, but the produced-absence dimension developed in Section 2 is muted. The lending version mentions produced absence in a single paragraph about the appeal-cost dynamic; the structural/produced distinction does not get extended in lending the way it does in underwriting.

**Underwriting weakness:** The categoricals are demonstrated less directly. There is no signed artifact equivalent to the adverse action notice, so position 3 (human oversight as verification gap) is demonstrated by argument rather than by direct case. The reader has to follow the argument that the underwriter's signature on the file is structurally equivalent to the loan officer's signature on the adverse action notice; the demonstration is a step longer than in lending.

**Underwriting weakness:** The regulatory location is less clearly within the FS AI RMF's design space. Adverse action notices are unambiguously a regulatory artifact with AI implications; risk-based pricing has fewer specific regulatory hooks. The argument that the empty chair *should* be represented in pricing depends on accepting the frame as normatively correct, not just on accepting the regulation as written. This is a harder argument and possibly the right one, but it requires more from the reader.

**Underwriting weakness:** Statistical validation as a counter-argument is partly correct in ways the version handles but does not fully resolve. The institution genuinely does have responsibility to the aggregate empty chair (regulators examining fair-lending compliance), and aggregate validation does represent that chair. The version's argument that aggregate validation does not represent the individual empty chair is correct but somewhat philosophical, and a reader who is satisfied with aggregate-level fair-lending compliance may not accept the individual-level claim as urgent.

## What the comparison reveals about the frame

The frame produces interpretive leverage in both cases, but in structurally different ways. Lending shows the frame as a *sharpening tool* applied to existing regulatory categories; underwriting shows the frame as a *generative tool* producing categories the regulation has not yet developed.

This is itself an interesting finding. The frame's value is not uniform across regulatory contexts. In well-developed regulatory spaces (lending, fair credit), the frame sharpens existing concerns and gives examiners diagnostic leverage on problems already named. In less-developed regulatory spaces (pricing, behavioral targeting in financial product offerings), the frame names problems that have not yet been articulated regulatorily, and proposes architectural primitives that would address them.

A position paper that argues for empty-chair representation as the organizing principle of the FS AI RMF should demonstrate both kinds of value. The frame should show that it sharpens existing concerns *and* that it generates new ones. Choosing only one example demonstrates only one kind of value.

## Recommendation

Use both. Not as separate full sections, but with one as primary and the other as a sharper turn at a specific point.

**Primary: lending.** It earns the categoricals at their canonical regulatory location, which is what Section 3 needs to do. The reader who follows the lending argument is in a position to accept the taxonomic move; the reader who rejects it has rejected the section's load-bearing claim.

**Secondary: underwriting, integrated as a turn near the end of the section.** After the lending example earns the categoricals and demonstrates the structural line, a brief turn to underwriting demonstrates that the frame produces leverage in regulatory spaces where the empty chair is not yet a regulatory subject. This earns the produced-absence frame from Section 2 in its sharpest form, demonstrates the frame's reach beyond existing regulation, and surfaces the architectural primitive question (Section 5) where the regulation does not yet require what the frame proposes.

Estimated section length under this structure: the lending material as drafted is ~1700 words; a 600-800 word turn to underwriting at the end would bring the section to ~2400-2500 words. Long but justifiable for a section that earns two of the paper's three positions.

## Alternative I rejected

Two full worked examples, lending and underwriting at equal length. Rejected because Section 3 is already structurally heavy — it argues categoricals and proposes a taxonomy — and two full examples would dilute the section's argumentative thread. The hybrid approach uses lending to earn the categoricals and underwriting to extend the frame's reach without restating the categorical argument from a different example.

## What I'm uncertain about in the comparison

The lending example may be too canonical to test the frame; the underwriting example may be too ambitious to earn the categoricals. The hybrid approach assumes lending earns enough of the categorical that underwriting can extend without re-earning, which may be wrong. If during revision the lending material does not feel like it has earned enough, underwriting may need to do more of the earning, which collapses the structure back toward two full examples.

The produced-absence dimension in lending is currently muted. Whether to develop it more in the lending material (so the structural/produced distinction extends) or to keep produced absence concentrated in the underwriting turn (so the section has a clear movement from misrepresentation to non-representation) is a structural choice that affects the section's overall shape. Currently leaning toward keeping produced absence concentrated in the underwriting turn for clarity, but this is contestable.

The aggregate-vs-individual representation argument in underwriting is philosophically sharp and may not be the right move for a position paper. A position paper benefits from arguments the reader can accept without philosophical commitment; the aggregate-vs-individual argument requires the reader to accept that individual representation has a different weight than aggregate representation, which is not obviously a position the FS AI RMF takes. May need to be softened or supported with regulatory hooks.
