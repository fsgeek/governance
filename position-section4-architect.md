# Section 4: Diagnostic Techniques (ARCHITECT-PRIMARY VERSION)

*Status: first-pass draft. Architect as primary diagnostic agent, with examination-time application falling out as consequence. To be pressure-tested against examiner-primary version. Will be reworked.*

*Citations needed: design methodology references where available, software architecture literature on design-time vs. run-time invariants, possibly Brooks on conceptual integrity, possibly Wing on computational thinking applied to system design.*

---

The empty-chair frame produces interpretive structure (Section 2) and a structural taxonomy of AI applications by verification-regime availability (Section 3). This section operationalizes the frame as a set of diagnostic techniques applied during architecture design — questions an architect asks while building an AI governance system, the answers to which determine whether the resulting system actually represents the empty chairs it claims to. The same techniques apply during regulatory examination of an existing system, but their primary work is at design time, where they shape what gets built rather than evaluating what already exists.

We frame diagnosis from the architect's perspective because the techniques are most powerful when they constrain construction rather than evaluate existing artifacts. An architect who applies these techniques builds systems that are diagnosable; an examiner who applies them to an undiagnosable system can only document that diagnosis is unavailable. The architectural moment is where empty-chair representation is structurally determined, and the diagnostic techniques are most valuable as design-time discipline. The examination-time application of these same techniques falls out as a consequence: a system built with these questions in mind is one an examiner can read for empty-chair representation; a system built without them is one whose representation claims cannot be assessed regardless of how skilled the examiner is.

## Three diagnostic techniques

The techniques are not exhaustive. We claim three because they emerge cleanly from the frame's structural commitments and produce design constraints directly applicable to AI governance system construction. Other techniques are possible and likely; these three are the ones the frame produces first.

### Technique 1: Empty-chair enumeration as design pre-condition

Before specifying any architectural primitive, the architect asks: *which empty chairs is this system supposed to represent, and what does representation require for each?* The question precedes any technical decision. An architecture whose empty-chair attribution is left implicit will produce primitives that serve some chairs and fail to serve others, and the failure will not be visible in the architecture's documentation because the documentation will describe what the system does, not what it leaves out.

Section 2 demonstrated this technique applied analytically to BSA/AML transaction monitoring. The same move applies to design. The architect designing an AI governance system for a community bank's lending operation asks first: *whose interest is this system structurally protecting?* The answer is rarely on the page initially; it has to be derived from the regulatory regime, the institution's risk profile, and the categories of decision the system will affect. Making the derivation explicit at design time is the technique's primary work.

The technique produces three outputs at design time:

First, an enumeration of empty chairs the system affects. This is the analytical move from Section 2, applied at the moment of architectural commitment.

Second, a mapping from empty chairs to architectural requirements that representation imposes. Different empty chairs require different architectural support. The future compliance officer needs durable, queryable institutional knowledge. The denied applicant needs verifiable reasoning. The marginalized customer needs disparate-impact monitoring with population decomposition. The institution's future self needs tamper-evident temporal capture. Each chair generates a set of requirements; the requirements may conflict, and the conflicts are themselves design information.

Third, a constraint on architectural choices: any primitive that fails to satisfy at least one chair's requirement and creates costs without serving any chair is architectural overhead. Any primitive that satisfies one chair's requirement at the cost of failing another's is a design tradeoff that requires explicit attention. The architecture is not a set of capabilities; it is a set of empty-chair representations, with capabilities chosen as the means.

The technique's design effect is to shift architecture decisions from feature-driven to representation-driven. Architectures designed without the technique tend to accumulate capabilities — explainability features, audit trails, monitoring dashboards — without explicit attribution to which empty chairs the capabilities serve. Architectures designed with the technique start from the chairs and select capabilities as the means of representing them. The selection criterion makes capability decisions tractable; without the criterion, capability decisions reduce to keeping up with vendor offerings.

### Technique 2: Designing for pages missing from the ledger

A well-designed attestation regime makes the institution's reasoning inspectable. But attestation cannot be uniformly comprehensive; cost and operational reality require choices about what to attest and what to leave un-attested. The architect's diagnostic move at design time is to make these choices explicitly and to design the attestation regime such that *what is left out is itself informative*.

We call this technique *designing for pages missing from the ledger*. The metaphor is deliberate: an accounting ledger with missing pages is more diagnostic than a forged ledger if the pattern of missing pages is itself interpretable. A ledger where missing pages are random reveals nothing about the institution's posture; a ledger where missing pages cluster around decisions favorable to the institution and unfavorable to challenged customers reveals the institution's posture clearly.

The technique works as follows. The architect determines, for each category of decision the system handles, what attestation will and will not be produced. The determination is documented. The institution's choice not to attest a category is itself attested, with the rationale captured. An examiner reading the system's attestation later can read both the present attestation (what was captured) and the meta-attestation (what was deliberately not captured, and why). The pattern of present and absent attestation is interpretable because the absences are themselves documented choices rather than oversights.

This is a design discipline, not a construction discipline. Most attestation systems are built bottom-up: a capability is implemented, attestation for that capability is added, and the absence of attestation in other areas is ambient. Designing for pages-missing inverts this: the architect specifies in advance the full domain of decisions, marks which will and will not be attested, and ensures the system's structure makes the absence visible rather than ambient.

The technique produces a design output: a manifest of attested and un-attested decision categories, with rationale, that travels with the system as part of its architectural documentation. An examiner reading the manifest can ask whether the un-attested categories are operationally explicable (resource constraints, low-risk decisions deprioritized) or whether they cluster in ways that reveal a posture (decisions favorable to the institution attested, decisions unfavorable to challenged customers not). The architect who has produced the manifest knows in advance which questions the manifest will answer and which it will not, and can adjust the attestation scope accordingly.

The architect's question to themselves at this stage: *what does my pattern of attestation reveal about my posture toward empty-chair representation, and is that what I intend it to reveal?*

### Technique 3: The produced-silence question pair as design constraint

Section 2 introduced the distinction between structural and produced absence. The diagnostic technique on produced absence, applied at design time, is a question pair the architect asks of every interface, every documentation regime, every customer-facing artifact:

*What is this design doing that creates silence?*

*What is this design inferring from the silence it creates?*

A design that asks reviewers to write justification after deciding creates silence around the reviewer's contemporaneous reasoning, then infers from the absence of contradicting evidence in the post-hoc justification that the documentation is faithful. The architect applying the question pair at design time recognizes the silence-production and chooses differently — capturing decision context as the reviewer engages with it rather than asking for narrative reconstruction.

A design that produces adverse action notices in regulatory boilerplate creates silence around the customer's effective interrogation of the notice, then infers from the absence of customer challenges that the notice is adequate. The architect applying the question pair at design time recognizes the boilerplate's interrogation-resistance and chooses differently — producing notices the customer can effectively interrogate, even if doing so requires architectural work the regulation does not currently require.

A design that prices loans without communicating substantive justification to the customer creates silence around the customer's standing to negotiate, then infers from acceptance rates that pricing is fair. The architect applying the question pair at design time recognizes the absence of customer-side justification mechanisms as a design choice with consequences, and weighs whether the consequences are acceptable given the empty chair the design leaves unrepresented.

The question pair, applied at design time, has the same structure as at examination time but different effect. At examination time, it diagnoses what the architecture has already done. At design time, it constrains what the architecture will do. The architect who anticipates the diagnostic question pair builds a system that can answer it; the architect who does not builds a system that the question pair will diagnose negatively.

This technique is the most contestable of the three because it requires the architect to design for absences they are choosing to allow. An architect may legitimately respond that some silences are structural rather than produced, that customers who don't challenge are satisfied, that reviewers who don't surface contemporaneous reasoning don't have any to surface. The architect may be correct in some cases. The technique's value is in making the question explicit at design time so the architect's choice is conscious rather than ambient.

The architect's question to themselves at this stage: *for every silence my system produces, am I confident the silence reflects the absence of objection rather than the suppression of objection by the system itself?*

## The techniques as compounding design constraints

The three techniques compound at design time. Empty-chair enumeration determines what the system is supposed to represent. Designing-for-pages-missing determines how the system makes its representation choices visible. Produced-silence-as-design-constraint determines how the system avoids architectural patterns that suppress the empty chair while inferring endorsement from the suppression.

In combination, the techniques produce a design discipline that is structurally different from feature-driven architecture. The system's capabilities are chosen as means of empty-chair representation; the system's attestation regime is designed for pattern-readability; the system's interfaces are scrutinized for silence-production at the moment of design rather than at the moment of examination. The architecture that results is one that an examiner can read; the architecture without these techniques is one that an examiner cannot read regardless of skill.

This is the operational claim of the section: the empty-chair frame, when developed into design-time diagnostic techniques, produces architectural discipline that makes the resulting systems substantively examinable. The frame is not an examination methodology that compensates for inadequate architecture; it is an architectural discipline that produces examinable systems.

## Examination as consequence

The same three techniques, applied by an examiner to an existing system, produce assessment leverage the FS AI RMF's checklist does not provide. The examiner asks: *which empty chairs does this system claim to represent? What does its attestation pattern reveal about its actual representation? What silences does its architecture produce, and what does the architecture infer from those silences?* These are the same questions the architect asked at design time, redirected from "what should I build" to "what was built."

The asymmetry between design-time and examination-time application is important. A system designed with the techniques in mind answers all three questions; an examiner reading such a system can assess whether the answers are substantive or theatrical. A system designed without the techniques in mind may be unable to answer the questions at all; an examiner reading such a system can only document the unavailability of substantive assessment.

The implication: the techniques' regulatory effect depends on adoption at the architectural level, not just at the examination level. An examiner who applies the techniques to a system designed without them produces findings of inadequacy, but the inadequacy is structural — it cannot be remediated by additional examination, only by re-architecture. The frame's claim is that AI governance systems for community banking should be architected to be diagnosable, and the diagnostic techniques developed here should shape the architecture rather than only its evaluation.

## Implications for architectural primitive selection

Section 5 develops the categories of architectural primitive that empty-chair representation requires. The diagnostic techniques developed here constrain that development: a primitive is valuable in proportion to its support of design-time diagnostic discipline. Tamper-evident temporal capture is valuable because designing-for-pages-missing requires the ability to attest both presence and absence of records. Three-dimensional confidence characterization is valuable because empty-chair enumeration requires distinguishing decisions where the architect provided genuine evidentiary support from decisions where the architect produced narrative without substantive grounding. The primitive categories are not generic technical capabilities; they are capabilities selected because the design-time techniques require them.

This is the section's transition into Section 5. The techniques operationalize the frame at design time; the primitives operationalize the techniques. Each layer of the architecture is justified by what the layer above it requires of it.
