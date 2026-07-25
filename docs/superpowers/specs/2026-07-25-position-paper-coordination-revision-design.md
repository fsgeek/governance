# Position Paper Coordination Revision Design

**Date:** July 25, 2026  
**Status:** Approved design  
**Document:** *Architectures of Absence: AI Governance under the FS AI RMF*

## Objective

Revise the paper as a coordination-oriented position paper that gives banks,
regulators, and vendors a common ontology for discussing AI-governance evidence
without erasing their different authority, incentives, capabilities, or access.
Empty-chair representation keeps affected parties present in that institutional
conversation even when they are not among its implementers.

The revision will preserve the paper's conceptual identity while correcting
three overextensions identified by review: treating an interpretive framework
as a validated method, treating design hypotheses as current examination
requirements, and implying that community banks can directly implement changes
controlled by vendors or regulators.

## Position-Paper Function

The paper is a boundary object, not an examination manual, implementation
specification, or empirical validation study. Its contribution is a translation
ontology through which the three institutional participants can locate and
contest the same evidentiary relationship.

The shared entities are:

- **actor:** the party making, reviewing, enabling, or contesting a claim;
- **affected interest:** the interest borne by an absent or weakly represented
  party;
- **control objective:** the legal, supervisory, contractual, or voluntary
  outcome at issue;
- **evidentiary object:** the thing a proposition actually requires evidence
  about;
- **artifact:** the record, explanation, metric, approval, or attestation made
  available;
- **inference:** the conclusion an actor asks another actor to draw from the
  artifact;
- **binding:** the declared and inspectable relation between artifact and
  inference;
- **authority:** what an actor may request, compel, decide, or enforce;
- **capability:** what a system or organization can preserve, expose, test, or
  export;
- **obligation:** what law, guidance, contract, or policy currently requires;
- **contest:** the procedure and evidence by which a claim or memory can be
  challenged and revised.

The core relation is:

```text
affected interest
  -> control objective
  -> required evidentiary object
  -> available artifact
  -> claimed inference and binding
  -> actor with authority or capability to close, disclose, or contest the gap
```

This is a translation ontology rather than a universal worldview. Participants
may disagree about interests, sufficiency, or remedy while still identifying the
specific relation in dispute.

## Participants and Theory of Effect

### Community banks

Banks identify which claims they must support, determine which evidence they
possess, document evidence they cannot obtain, design feasible compensating
controls, and translate unresolved gaps into procurement and contractual
requirements. The paper will not imply that a community bank can unilaterally
re-architect a core platform or vendor model.

### Examiners and regulators

Examiners use the ontology to identify unsupported inferences and request
specific evidence within existing authority. A conceptual diagnostic does not
itself establish a violation or support a finding. Where current authority ends,
the paper will label the result as a policy, guidance, coordination, or future-
design question. Regulators can aggregate recurring evidence gaps that no single
community bank can remedy and convert them into guidance, standards, or
coordinated expectations.

### Vendors and system architects

Vendors and architects implement capabilities that banks cannot create at the
edge: provenance, exportability, decision-time capture, declared evidence
bindings, uncertainty representation, and monitoring. Product labels or
dashboards are not sufficient; the relevant acceptance criteria concern the
evidence a capability preserves and the conclusions it can support.

### Affected parties

Customers, future officers, examiners, counterparties, and other empty chairs
are not reduced to a fourth implementation constituency. Their interests supply
the normative reason for the ontology and the standard against which the three
institutional participants' coordination is evaluated. The paper will not
present unequal actors as possessing symmetric power or information.

## Epistemic Status and Claim Hierarchy

The manuscript will use the following hierarchy consistently:

1. **Empty-chair representation** is a normative and interpretive framework.
2. **Structural and produced absence** are sensitizing distinctions that
   generate testable questions; they are not self-proving classifications.
3. **Silence-manufacture** names an artifact-level diagnostic sequence, not the
   discovery of information asymmetry, organizational decoupling, or audit
   substitution.
4. **The three diagnostics** orient inquiry and can be instantiated as evidence-
   request sequences; they are not findings or universally authorized
   examination procedures.
5. **The architectural capabilities** are provisional design hypotheses
   generated by the worked applications; they are not necessary, sufficient, or
   currently mandated for every deployment.

The manuscript will replace claims that the worked examples “demonstrate” the
framework's practical effectiveness with “worked applications” or “illustrative
analyses.” It may claim that the examples expose distinctions, generate
questions, or produce hypotheses.

## Adjacent-Theory Positioning

The revision will add a compact comparison, not a general literature review:

- stakeholder theory and value-sensitive design identify affected interests and
  values;
- principal-agent theory and information asymmetry explain divergent incentives
  and unequal access;
- decoupling, audit-society, and audit-culture accounts explain divergence
  between formal artifacts and operational substance;
- the paper contributes a regulator-facing artifact-to-inference sequence tied
  to FS AI RMF controls, actor authority, and evidence capability.

Novelty will be claimed for the synthesis, ontology, diagnostic sequence, and
financial-regulatory application—not for the existence of absent interests,
asymmetric information, or ceremonial artifacts.

The Goodhart “dual” language will be replaced with “complementary pattern” or an
equally non-formal description.

## Testable Produced Absence

Observed silence does not establish produced absence. Produced absence will be
defined as a hypothesis that a design, cost, rule, interface, or institutional
practice materially changes whether an affected party or contradictory record
becomes observable.

Evidence can include:

- comparison across channels, institutions, populations, or time;
- challenge-rate response to reduced friction or changed notice design;
- user research or complaint evidence;
- examiner-selected samples;
- a feasible counterfactual design with materially different observability;
- provenance showing that an expected record was suppressed, excluded, or
  overwritten.

Where such evidence is unavailable, the paper may identify a produced-absence
question but may not assert the classification as fact. The institution or
architecture does not anthropomorphically “infer”; identified people, processes,
policies, or reports interpret absence or use it in a decision.

## Operational Diagnostics

Each diagnostic will have two layers.

### Orienting layer

The memorable question changes what an architect, banker, or examiner notices.
It remains explicitly conceptual.

### Evidence-request layer

An instantiation names:

1. the governing objective or authority;
2. the institutional proposition under review;
3. the evidentiary object the proposition requires;
4. the artifact offered;
5. method, configuration, provenance, validation, reviewer-access, and scope
   records needed to evaluate the binding;
6. observations that would support or defeat the inference;
7. the responsible actor and available remedy;
8. whether the result can support a current finding or only a policy/design
   recommendation.

The paper will give at least one compact evidence-request instantiation tied to
an exact FS AI RMF control already analyzed in the worked applications. It will
not prescribe examination thresholds or claim legal authority it has not
established.

## Declared Attestation Scope

“Pages missing from the ledger” will remain as a memorable metaphor, but its
denominator will be explicit. The operational concept is declared attestation
scope. A defensible scope record includes:

- the decision universe and category definitions;
- inclusion and exclusion rules;
- the rationale and authority for those boundaries;
- boundary and version history;
- counts or coverage measures tied to the operational population;
- risk-weighted coverage where raw volume would mislead;
- reconciliation against system inventories and deployed workflows;
- institution-selected and examiner-selected samples.

Absence outside an undefined universe is not a missing page. A discrepancy
within, or a strategically constructed boundary around, a declared universe is
an examinable evidentiary fact. It does not by itself prove motive or violation.

## Provisional Evidentiary Capabilities

The architectural section will describe capabilities rather than universal
requirements.

### Temporal and revision-aware capture

Preserve decision-time inputs, context, actions, and provisional reasons while
allowing later reflective reasoning. Later interpretation must be separately
dated and bound; it may supplement or revise understanding but may not overwrite
or impersonate the decision-time record. Attestation establishes commitment,
sequence, and detectable alteration—not truth or completeness.

### Evidence binding and exportability

Preserve traversable declared relations among decisions, evidence, artifacts,
methods, and authorizations in a form the bank can export and an authorized
reviewer can inspect. Binding establishes association and provenance, not causal
influence or evidentiary sufficiency.

### Non-collapsing uncertainty representation

Preserve material distinctions among supporting evidence, counterevidence,
conflict, model uncertainty, missing information, and policy ambiguity. Support,
counter-support, and insufficiency remain one illustrative schema. The paper
will not call the dimensions orthogonal or require one formalism. A single
probability may be useful but does not by itself identify why uncertainty has a
particular value.

### Technical-change monitoring

Distinguish data, concept, and performance change where those distinctions lead
to different technical investigations. Detection directs inquiry and does not
establish cause.

### Institutional-conformance monitoring

Treat divergence between documented policy and operational practice as a
parallel organizational capability rather than a fourth statistical drift
type. It relies on attestation, workflow evidence, sampling, and audit rather
than being implied to share a detector with model drift.

The design therefore permits five capabilities where the previous manuscript
forced them into four. Count preservation is not a requirement.

## Scope and Compression

The revision will remain bounded:

- no empirical deployment study;
- no complete coding of all 230 controls;
- no implementation specification;
- no examination thresholds or new legal claims;
- no comprehensive survey of adjacent theory;
- no diversion into the Rashomon-model research program.

Target compression is 600–1,000 net words after necessary additions. Sections 2
and 4 are the primary sources of removable meta-commentary and repetition. The
prior-art comparison must remain. Compression must not erase actor authority,
claim status, or counterevidence.

## Review-Artifact Handling

The 2026-07-24 review findings are evidence, not commands. Findings caused by
the LaTeX extraction layer—raw citation keys, `[ref]`, title backslashes, and
author-block formatting—will not trigger manuscript edits when the rendered PDF
is correct. Genuine findings will be resolved against source and rendered PDF.

Future review should distinguish three representations:

- rendered PDF for visible copy and layout;
- normalized PDF text for prose, narrative, and conceptual review;
- LaTeX source for citations, labels, bibliography, and archival checks.

## Verification Gates

The revision is complete only when:

1. every institutional action is assigned to an actor with the authority or
   capability to perform it;
2. policy recommendations cannot be mistaken for current examination findings;
3. produced absence is framed as a testable hypothesis with defeating evidence;
4. adjacent theories are acknowledged and the paper's narrower contribution is
   explicit;
5. each diagnostic includes an orienting question and an evidence-request
   instantiation;
6. attestation scope has a declared denominator and adversarial coverage checks;
7. the five provisional capabilities state what they establish and do not
   establish;
8. decision-time and reflective records remain distinct;
9. the manuscript is shorter on net and retains a coherent regulator-readable
   narrative;
10. citation, reference, clean-build, minimal-package, rendered-PDF, and full
    repository-test gates pass.

