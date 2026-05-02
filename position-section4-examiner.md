# Section 4: Diagnostic Techniques (EXAMINER-PRIMARY VERSION)

*Status: first-pass draft. Examiner as primary diagnostic agent. To be pressure-tested against architect-primary version. Will be reworked.*

*Citations needed: examiner manual references where available, recent OCC / FDIC examiner guidance on AI systems, FFIEC IT Examination Handbook references on model risk, possibly Carse and Foster on regulatory examination practice.*

---

The empty-chair frame produces interpretive structure (Section 2) and a structural taxonomy of AI applications by verification-regime availability (Section 3). This section operationalizes the frame as a set of diagnostic techniques an examiner can apply to an AI system in a community bank, producing assessment leverage the FS AI RMF's checklist surface does not provide. The techniques developed here turn the frame from analytical to operational; an examiner who learns these techniques can do work the framework's text does not enable.

We frame diagnosis from the examiner's perspective rather than the architect's. The architect's perspective on these techniques is genuine and substantial, and we name it where relevant; but the paper's audience is the regulatory community, the FS AI RMF's purpose is to give examiners a substrate for assessment, and the empty chair the techniques most directly serve is the one the examiner is most often called to represent — the customer affected by the AI's decisions, who is not in the examination room when the institution's claims about its AI systems are evaluated.

## Three diagnostic techniques

The techniques are not exhaustive. We claim three because they emerge cleanly from the frame's structural commitments and are directly applicable to FS AI RMF examination practice. Other techniques are possible and likely; these three are the ones the frame produces first.

### Technique 1: Empty-chair enumeration as the examination's first move

Before assessing whether a control is adequately implemented, the examiner asks: *which empty chairs does this control protect, and which does it leave unaddressed?* The question precedes any compliance evaluation. A control whose empty-chair attribution is ambiguous cannot be assessed for adequacy until the attribution is made explicit.

Section 2 demonstrated this technique applied to BSA/AML transaction monitoring. The same move applies generally. The examiner reading any control objective from the FS AI RMF asks first: *whose interest is this control structurally protecting?* The answer is rarely on the page; it has to be inferred from the control's text, the regulation's underlying intent, and the institution's implementation choices. Making the inference explicit is the technique's primary work.

The technique produces three outputs:

First, an enumeration of empty chairs the control affects. This is the analytical move from Section 2, applied at examination time.

Second, a mapping from empty chairs to implementation choices that affect their representation. The control's text underspecifies; the institution's implementation makes specific choices; those choices determine which chairs are represented and which are not. The mapping makes the institution's implicit choices visible.

Third, a question: *for each empty chair the control was meant to protect, what evidence does the institution have that the implementation represents this chair?* The question shifts the examination's epistemic burden in a specific way. Without the technique, the examiner asks whether the control's text is satisfied (a question the institution is well-prepared to answer). With the technique, the examiner asks whether the empty chairs the control was meant to protect are actually represented (a question the institution may not have prepared for, because the regulation does not explicitly require this kind of preparation).

The technique's regulatory effect, if widely adopted, is to shift institutional behavior from compliance-text satisfaction to substantive empty-chair representation. Institutions that anticipate the question prepare evidence the question requires. Institutions that do not anticipate the question discover during examination that the evidence they have is not the evidence the question requires.

### Technique 2: Pages missing from the ledger

When an institution's attestation regime is well-formed — tamper-evident, contemporaneous, comprehensive — the institution's reasoning becomes inspectable. But attestation regimes are rarely complete. Some decisions are attested; others are not. Some categories of decision have rich evidence; others have thin or no evidence. The examiner's diagnostic move is to read the *gaps* in the attestation as substantive information about the institution's posture.

We call this technique *pages missing from the ledger*. The metaphor is deliberate: an accounting ledger with missing pages is more diagnostic than a forged ledger. A forged ledger requires interpretation of fabricated evidence; a ledger with missing pages requires interpretation of evidence the institution chose not to produce. Choosing not to produce evidence is itself an institutional act, and the act is interpretable.

The technique works as follows. The examiner asks the institution to demonstrate empty-chair representation across the institution's AI deployments. The institution produces evidence for some deployments and not others, or rich evidence for some categories of decision and thin evidence for others. The pattern of presence and absence is the diagnostic.

Some absences are structurally explicable. The institution has not deployed AI in some areas, so no attestation exists. The institution has limited resources and has prioritized attestation in higher-risk areas. These absences are operational and do not constitute negative evidence about the institution's posture.

Other absences are not structurally explicable. The institution has deployed AI in an area but has chosen not to attest the decisions. The institution has rich attestation for low-risk decisions and thin attestation for high-risk decisions. The institution can produce evidence for decisions favorable to itself but not for decisions favorable to challenged customers. These absences are diagnostic. They reveal that the institution understood the value of attestation in some contexts and chose not to extend it to others. The choice is informative about the institution's actual posture toward empty-chair representation, regardless of what its compliance documentation claims.

The technique inverts the usual examination dynamic. Examiners typically ask institutions to demonstrate compliance, and institutions produce evidence to support the demonstration. Pages-missing inverts this: examiners ask institutions to demonstrate where attestation does and does not exist, and the institution's pattern of evidence production becomes the substantive examination subject. An institution cannot game pages-missing by producing more evidence; producing more evidence in some areas and not others is precisely the pattern the technique reads.

The technique's effectiveness depends on the examiner having the analytical framework to read absence as information. Without the empty-chair frame, an absence of attestation reads as a documentation gap to be filled. With the frame, the same absence reads as institutional choice. The frame is the precondition for the technique.

### Technique 3: The produced-silence question pair

Section 2 introduced the distinction between structural and produced absence: parties absent because the situation places them outside the decision context, versus parties absent because the architecture suppresses their voice and reads the suppression as endorsement. The diagnostic technique on produced absence is a question pair the examiner asks of the institution and of the architecture:

*What is the architecture doing that creates this silence?*

*What is the architecture inferring from the silence it created?*

Applied to adverse action notices (Section 3 lending example): the architecture is producing notices in regulatory boilerplate that the customer cannot effectively interrogate. The architecture is then inferring from the absence of customer challenges that the notices are adequate. The institution's stable record of un-challenged adverse action notices is partly produced by the boilerplate's interrogation-resistance, not by the notices being faithful. The question pair makes the production-and-inference structure visible.

Applied to risk-based pricing (Section 3 turn): the architecture is producing rates without substantive justification, structuring the transaction such that the customer cannot effectively negotiate. The architecture is then inferring from acceptance rates that pricing is fair. The institution's pricing data shows accepted offers and declined offers; it does not show customers who would have asked for justification if justification were available, because that population is not measured.

Applied to documentation regimes for human review (Section 2 third control): the architecture is asking reviewers to write justification after deciding, producing narrative that the institution treats as the audit trail. The architecture is then inferring from the absence of contradicting evidence in the narrative that the documentation is faithful. The reviewer's actual contemporaneous reasoning is suppressed; its silence is read as endorsement.

The pattern across applications: the architecture produces a population of silent affected parties (customers who don't challenge, customers who accept rates, reviewers who don't surface their actual reasoning), and the institution interprets the silence as evidence the architecture is correct. The question pair surfaces the production mechanism and the inferential leap.

This technique is structurally different from the first two. Empty-chair enumeration and pages-missing operate on observable artifacts — controls, attestation records, documentation. Produced-silence operates on what the architecture is *not* producing — the challenges that didn't happen, the negotiations that didn't occur, the contemporaneous reasoning that wasn't captured. The technique's diagnostic move is to make the absence visible as architectural product rather than treating it as the natural state of affairs.

The technique is also the most contestable of the three. An institution may respond that customers who don't challenge accept their decisions, that customers who don't negotiate are satisfied with their rates, that reviewers who don't surface contemporaneous reasoning don't have any to surface. The defense against this response is empirical work the position paper does not undertake. The technique points to where the work needs to be done; it does not do the work itself.

## The techniques in combination

The three techniques compound. An examiner using only empty-chair enumeration produces a list of unaddressed chairs but cannot read the institution's posture toward them. Adding pages-missing produces information about which chairs the institution chose not to attest for, distinguishing operational gaps from posture gaps. Adding produced-silence surfaces the architectures that suppress challenge and read the suppression as evidence of correctness.

In combination, the techniques produce an examination posture that is structurally different from checklist-aligned compliance review. The institution's compliance documentation is one input among several; the institution's pattern of attestation is a second; the institution's architectural choices about what to capture and what to leave to silence are a third. The examiner who uses all three techniques is reading the institution's actual posture toward empty-chair representation, not the institution's documentation about its posture.

This is the operational claim of the section: the empty-chair frame, when developed into diagnostic techniques, gives examiners assessment leverage the FS AI RMF's checklist does not provide. The frame is not a more sympathetic vocabulary for compliance review; it is a different examination methodology, and it produces different findings.

## What the techniques do not do

The techniques do not provide bright-line rules for examination findings. They produce diagnostic leverage; the examiner's substantive judgment about whether the diagnostic findings constitute supervisory concerns remains the examiner's. The techniques sharpen what the examiner sees; they do not make the seeing automatic.

The techniques do not eliminate institutional capacity to evade them. An institution that understands the techniques can architect its systems and documentation to anticipate the questions, which is partly the point — the techniques are meant to shift institutional behavior toward substantive empty-chair representation by making the absence of representation visible. But sophisticated institutions can also produce surface-level compliance with the techniques while preserving the substantive gaps the techniques are meant to surface. The defense against this is examiner expertise developed over time, examination practice that compounds across institutions, and continued evolution of the techniques as institutional responses develop.

The techniques do not address the coordination problem at examination time named in Section 1's verification-regime caveat. The techniques are valuable only if examiners have the time, expertise, and institutional support to apply them. Examination practice is resource-constrained; not every examiner can apply techniques of this depth to every institution. The techniques work best when their existence is widely known across the regulatory community, so that institutions anticipate them and architect for them in advance, rather than relying on examiner application case by case.

## Implications for architectural primitive selection

Section 5 develops the categories of architectural primitive that empty-chair representation requires. The diagnostic techniques developed here constrain that development: a primitive is valuable in proportion to its support of diagnostic techniques the examiner can apply. Tamper-evident temporal capture is valuable because pages-missing and produced-silence both require the ability to read what was attested when. Three-dimensional confidence characterization is valuable because empty-chair enumeration requires distinguishing decisions where the institution had genuine evidence from decisions where the institution had inadequate evidence and produced narrative anyway. The primitive categories are not generic technical capabilities; they are capabilities selected because the diagnostic techniques require them.

This is the section's transition into Section 5. The techniques operationalize the frame; the primitives operationalize the techniques. Each layer of the architecture is justified by what the layer above it requires of it.
