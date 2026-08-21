# Regulator-mediated blinded construction of policy-constrained Rashomon models

**Status:** exploratory  
**Authority:** supporting  
**Depends on:** `working_notes/2026-06-03-provenance-is-the-5th-confound.md`; `working_notes/2026-06-09-pick-one-hides-the-choice.md`; `section6.tex`  
**Invalidated by:** none yet  
**Last reconciled with code:** not applicable; this note describes a proposed protocol, not current implementation

**Date:** 2026-08-20

## Purpose and status

This note captures a possible institutional execution of the governance frame in
*Architectures of Absence*. It also identifies a candidate computer-science
research program around explainable Rashomon models. The mechanism is not a
recommendation that regulators adopt a safe harbor, not a claim that a regulator
currently has authority to create one, and not a requirement that institutions
use a particular modeling paradigm.

The motivating question is narrower: if an institution wants a regulator or
auditor to place greater evidentiary weight on a model-development record, what
protocol could reduce opportunities for the institution and model constructor
to coordinate on a preferred result while preserving accountability for both?

The proposed answer combines four ideas:

1. the institution commits its policy, ontology, and model-selection procedure
   before construction;
2. an authorized reviewer accepts, rejects, or returns that package for
   clarification;
3. the reviewer assigns a qualified model constructor through a double-blind,
   mediated process; and
4. the constructor returns an attested representation of the admissible
   Rashomon set rather than silently choosing a single model.

A regulator could attach a rebuttable procedural or evidentiary presumption to
successful use of this pathway. That incentive is an optional governance
profile around the technical protocol, not a property required by the protocol
itself.

## The distinction doing the work

Here, *blind* does not merely mean that the constructor is denied protected
attributes or the institution's preferred outcome. It describes the assignment
relationship:

- the institution is not told which qualified provider will construct the
  artifact, at least before construction and ideally afterward;
- the provider receives a pseudonymous case package and is not told which
  institution supplied it; and
- the regulator or authorized reviewer selects the provider and mediates all
  questions and delivery.

The reviewer retains the identity mapping. The institution and constructor are
therefore independently accountable to the reviewer without acquiring a direct
relationship through which they can negotiate an implementation. Randomization
does not need to be uniform. A defensible assignment procedure can sample among
providers satisfying competence, capacity, independence, conflict, and
concentration constraints while producing an auditable selection record.
Compensation and recusals would also need to pass through the clearinghouse: the
institution may fund an assessment, but should not negotiate a provider's price
or terms after assignment.

Continued confidentiality matters. Automatically revealing identities after
delivery can create a repeated-game channel through employment, consulting,
referrals, or future contracts. The conservative protocol ends the constructor's
role at delivery of a portable artifact and does not require later disclosure.
This note identifies but does not attempt to eliminate covert communication,
collusion outside the protocol, or reidentification from institutional details.

## Roles

The roles are functional; one legal entity may hold more than one only where the
threat model permits it.

| Role | Principal responsibility | Must not control |
|---|---|---|
| Institution | State the policy objective, ontology, admissible inputs, loss, and selection procedure; provide complete and accurate source material | Constructor assignment or undisclosed post-result selection |
| Authorized reviewer / clearinghouse | Review the committed package, manage clarification, qualify and assign constructors, retain identity mappings, and decide what procedural consequence follows | The constructor's technical execution except through the accepted specification |
| Blinded constructor | Execute the committed candidate-generation procedure and return the candidate representation, manifest, and construction evidence | Institutional policy, the final selection criterion, or deployment |
| Independent evaluator | Compute the pre-specified model- and set-level measurements, using protected or outcome data withheld from the constructor where appropriate | Retrospective alteration of the evaluation or selection criteria |
| Selector | Apply the committed selection functional and tie-breaking rule | Unrecorded discretion among candidates |
| Institution or separate integrator | Deploy the selected portable artifact and demonstrate identity or permitted equivalence | Undisclosed retraining or material transformation |

Questions from the constructor travel through the clearinghouse. A material
ambiguity returns to the institution and reviewer for a committed clarification;
it is not resolved through private compromise between institution and
constructor. The clarification, its timing, and any resulting change in scope
become part of the record.

## The committed package

Pre-registering only the final choice rule leaves the constructor able to steer
the result by controlling which candidates appear. The pre-construction package
therefore needs to describe the relevant choice-producing procedure, not merely
the written policy. At minimum it contains:

- the institutional policy and its version;
- the ontology that gives operational meaning to policy terms, including
  definitions, relationships, exclusions, and exception routes;
- admissible and prohibited inputs and transformations;
- the hypothesis class;
- the training population and declared scope;
- the loss or performance objective;
- the Rashomon tolerance and the reference against which it is measured;
- policy-conformance constraints;
- the candidate enumeration, search, or sampling procedure;
- required coverage and diversity diagnostics;
- evaluation measures and access rules, including any separation of protected
  attributes from construction data;
- the selection functional and deterministic or randomized tie-breaking rule;
- permitted deployment transformations; and
- conditions requiring clarification, renewed review, or a new construction
  cycle.

The selection specification is part of policy for purposes of commitment and
change control. This does not mean that the protocol dictates which model an
institution must use. It means that the institution states in advance how a
model will become selectable and exposes that procedure to review before the
candidate outcomes are known.

## The technical object

Let the reviewed package define an ontology \(O\), policy constraints \(P\),
hypothesis class \(H\), loss \(L\), and tolerance \(\epsilon\). The ideal
policy-constrained Rashomon set is

\[
R_{P,O,\epsilon} = \{f \in H : L(f) \leq L^* + \epsilon
\;\text{and}\; f \models (P,O)\}.
\]

Here \(L^*\) is a reference loss fixed by the committed package. The package
must state whether it is the best loss over \(H\), the best loss over the
policy-conforming subset, or another independently reproducible benchmark;
those definitions can admit materially different sets.

In realistic hypothesis classes, exhaustive enumeration will usually be
impossible. The constructor therefore returns an attested representation
\(\widehat{R}\), which may be a finite candidate set, a structured
parameterization, or a reproducibly sampled subset. The claim is not that
\(\widehat{R}=R\) unless completeness can actually be established. The output
must instead identify:

- the committed search procedure and its execution record;
- inclusion and exclusion criteria;
- duplicate handling;
- convergence, coverage, and diversity diagnostics appropriate to the class;
- every material deviation or failure; and
- a manifest binding each candidate to the package, source data, code,
  environment, and evaluation record.

The independent evaluator attaches two different kinds of explanation:

1. **Model-level explanation:** what the selected model did, within the warrant
   of the chosen explanatory method.
2. **Set-level explanation:** which conclusions are stable across equally
   adequate policy-conforming candidates, where candidates disagree, how much
   individual or population outcomes depend on selection, and which discretion
   remains after applying the policy.

The second is the distinctive governance object. Existing repository results
show why it matters: tied or near-tied policy-admissible models can rank
individual borrowers very differently. Selecting one without preserving the
alternatives converts consequential discretion into an apparently technical
inevitability (`working_notes/2026-06-09-pick-one-hides-the-choice.md`).

## Protocol sketch

1. **Commit.** The institution signs and timestamps the policy, ontology,
   construction specification, and selection specification.
2. **Review.** The authorized reviewer tests eligibility, clarity, legal and
   policy constraints, evidentiary sufficiency, and identified ambiguities. It
   accepts the package, objects, or returns questions.
3. **Package.** The clearinghouse minimizes direct identifiers without removing
   facts materially required for valid construction. It assigns a case
   identifier and records the package hash.
4. **Assign.** An auditable eligibility-constrained random process selects a
   qualified constructor. The institution receives no advance provider identity;
   the constructor receives no institution identity.
5. **Clarify through the intermediary.** Questions and answers are relayed and
   committed. A substantive change returns to review rather than becoming an
   informal implementation choice.
6. **Construct.** The provider executes the committed procedure and returns
   \(\widehat{R}\), its manifest, coverage evidence, and signed attestations.
7. **Evaluate.** An independent evaluator computes the pre-specified
   measurements and set-level disagreement quantities. Separation can allow the
   evaluator to use protected attributes that the constructor did not receive.
8. **Select.** The committed rule is applied to the evaluated candidate
   representation. Any undefined case, failed condition, or discretionary
   override is visible and handled through a declared exception path.
9. **Deliver.** The clearinghouse releases a portable selected artifact and its
   evidence package without necessarily disclosing the constructor.
10. **Deploy and bind.** The institution or a separate integrator deploys the
    artifact. Hashes, reproducible builds, or behavioral-equivalence tests bind
    the deployed implementation to the reviewed artifact. Retraining or a
    material transformation begins a new cycle unless expressly permitted.

## What the protocol can and cannot warrant

The defensible claim is procedural:

> Within the declared threat model, the record can show that a committed policy,
> ontology, candidate-generation procedure, and selection rule preceded model
> construction; that an independently assigned provider executed the declared
> procedure; that the reported alternatives and evaluation bind to that
> execution; and that the selected portable artifact followed the committed
> rule.

The protocol can make adaptive and retrospective fairwashing more difficult or
visible. In particular, it reduces bilateral institution--constructor
coordination, post-result changes to the institutional story, silent selection
from contradictory alternatives, and substitution of a different artifact at
delivery.

It cannot establish that the original policy or ontology was adopted in good
faith. A discriminatory choice can be expressed consistently, committed early,
and executed perfectly. Provenance establishes timing, content, integrity,
conformance, and non-equivocation; it does not identify motive
(`working_notes/2026-06-03-provenance-is-the-5th-confound.md`). Nor does the
protocol by itself:

- establish substantive legal compliance or the absence of disparate impact;
- prove that the pseudonymous package cannot identify the institution;
- eliminate bribery, side agreements, or other collusion outside the protocol;
- prove completeness of a candidate representation when enumeration is
  intractable;
- establish that a deployed system preserves the reviewed behavior without
  separate binding evidence;
- resolve distribution shift, data error, or later policy change; or
- create regulatory authority, affected-party access, participation, or remedy.

These boundaries should appear next to any safe-harbor discussion. Otherwise
the protocol risks becoming the kind of evidentiary substitution the governance
paper criticizes: a clean process artifact asked to support a broader claim
about fairness or intent.

## Optional safe-harbor profile

A jurisdiction or supervisory body could motivate voluntary participation by
attaching a bounded consequence to a conforming record: for example, a
rebuttable evidentiary presumption, a streamlined examination path, or reduced
duplication of specified process review. The ordinary path remains available:
an institution may define and build its own system, but receives no special
presumption and remains subject to ordinary review.

The term *safe harbor* must not imply immunity. Any benefit should specify:

- the exact proposition for which reliance is permitted;
- the artifacts and operational conditions within scope;
- facts, omissions, changes, or deployment deviations that defeat reliance;
- continuing institutional responsibility; and
- the regulator's ability to examine outcomes and substantive obligations.

The useful retirement-plan analogy contains two separate mechanisms. IRS
pre-approved retirement plans provide a reviewed base document and an adoption
agreement containing permitted employer choices; changes outside the permitted
options can remove reliance on the provider's opinion letter. Separately, a
safe-harbor 401(k) receives relief from specified annual nondiscrimination tests
by satisfying defined design and operational conditions. Neither is general
immunity, and using an outside provider does not eliminate the employer's duty
to operate the plan correctly and monitor service providers.

Primary descriptions:

- IRS, [Preapproved retirement plans: adopting employer](https://www.irs.gov/retirement-plans/preapproved-retirement-plans-adopting-employer)
- IRS, [401(k) plan overview](https://www.irs.gov/retirement-plans/plan-sponsor/401k-plan-overview)
- Department of Labor, [Tips for Selecting and Monitoring Service Providers for Your Employee Benefit Plan](https://www.dol.gov/sites/dolgov/files/EBSA/about-ebsa/our-activities/resource-center/fact-sheets/tips-for-selecting-and-monitoring-service-providers.pdf)

## Possible scaling outcome: reviewed baseline packages

If individualized review and construction impose high fixed costs, regulators,
trade groups, or qualified providers might develop reviewed reference policies
and ontologies for common products. A small or medium institution could adopt a
baseline and record its permitted elections in an adoption agreement. Material
semantic changes would require renewed review or move the institution to the
ordinary individually designed path.

This is a possible institutional consequence, not a recommendation or technical
requirement. It could lower drafting cost, reduce semantic fragmentation, make
provider services economically viable, and produce comparable evidence across
institutions. It could also create model monoculture, suppress locally material
interests, harden regulatory mistakes into defaults, invite capture of the
baseline-setting process, and allow ceremonial adoption to substitute for
operational conformance. Versioning, restatement cycles, extension rules, and
continued outcome review would therefore matter as much as initial approval.

## Candidate research contribution

The strongest computer-science claim is not simply that an explainable model can
be found. It is that a system can preserve and attest **policy-constrained model
multiplicity while binding eventual selection to a rule committed before the
alternatives and their effects are known**.

That claim suggests several separable research questions:

1. How should policy and ontology changes compile into constraints over a model
   class, and how can semantically material changes be detected?
2. What evidence can support coverage claims for a finite representation of an
   intractable Rashomon set?
3. Which set-level explanations expose consequential selection discretion
   without overwhelming a reviewer?
4. How resistant is precommitted candidate generation and selection to gaming
   through the hypothesis class, loss, tolerance, ontology, or search procedure?
5. What information must remain visible for valid construction, and what can be
   minimized to preserve practical institutional blindness?
6. What artifact-equivalence tests are sufficient to bind a reviewed portable
   model to deployment without returning the constructor to the institution?

Novelty relative to current multiplicity, fairness, constrained-learning, and
assurance literature remains to be established through a targeted review. The
mechanism is nevertheless concrete enough to formalize and prototype without
making the safe-harbor policy choice part of the technical contribution.
