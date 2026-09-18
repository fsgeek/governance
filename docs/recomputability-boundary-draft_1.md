---
**PROVENANCE — read before building on this.**

Inbound feedback, not this project's own draft. Produced 2026-09-08 by a Claude
instance working from the SSRN preprint of *Architectures of Absence* plus an
unrelated fairy tale, WITHOUT access to this repository. Committed unmodified
below; do not treat its characterizations of the foundation paper as verified.

**Verified 2026-09-18 against the actual sources:**

- **§4's framing is wrong about our text.** It claims the foundation paper
  "understates the result" by treating the binding as one irrecoverable object
  among seven. It does not. `section6.tex` (~L181) already says "one narrow
  record carries most of the weight" and "the smallest change that would convert
  several currently unreachable objects into reachable ones"; `section7.tex`
  (~L34) already frames it as an inversion of "a common assumption about what
  can be recovered later." The leverage argument is ours already. The draft
  mistook first contact with the argument for an extension of it — the
  first-contact-frame failure this project logs repeatedly.
- **Genuinely new here, and worth keeping (~40%):** (1) recomputability as a
  property *conditional on* a preserved binding rather than intrinsic to an
  object — a real sharpening; (2) **the retention corollary (§6)** — "a pointer
  to a deleted object is not a record," and vendor version-retention recast as a
  *procurement term* rather than a transparency demand. This is not in the
  paper at all and is the strongest contribution in the draft; (3) the
  generation seed as part of the binding; (4) §9's explicit defeaters.
- **§9's first defeater is already partly triggered by published work.**
  Hwang, Lee, Rosenblatt, Stoyanovich & Whang, "Explanation Multiplicity in
  SHAP" (arXiv:2601.12654, Jan 2026) hold the trained model FIXED and re-run
  SHAP varying only explainer stochasticity and background resampling.
  Explainer-induced multiplicity dominates on large data, and — load-bearing —
  L2 distance makes attributions look stable while rank-based metrics show
  disagreement approaching a randomized baseline. If that holds, Class A is NOT
  rescued by a binding alone and this draft's central partition needs
  weakening, not strengthening. Any successor work must pre-register a
  RANK-BASED tolerance; an L2 criterion yields a falsely reassuring result.

Still open in the draft's own terms: the HMDA record-generation-vs-surrender
characterization is stated from general knowledge and needs a citation to the
statute and Regulation C.

---

# The Recomputability Boundary

### Why one decision-time record determines what AI governance can verify later

**Working draft — v0.1**
Derived from *Architectures of Absence: AI Governance under the FS AI RMF* (Mason 2026), §3.1 and §7.4.

---

## 1. The claim

AI governance debate is largely a debate about explanation: which method, how faithful, understandable to whom. That framing assumes the evidence will be there when someone comes to look. For most of the objects governance cares about, it will not be — and which ones survive is not a matter of policy preference but of what can and cannot be reconstructed after the fact.

This paper makes one argument in three steps.

1. The evidentiary objects an AI governance regime relies on divide by *recoverability*, not by quality or faithfulness.
2. That division is not intrinsic to the objects. Three of them are recoverable only on the condition that a single small record — the binding between a decision and the system state that produced it — was preserved at decision time. Without it, they are not merely unverified; they have no referent.
3. Therefore the minimum sufficient governance record is small, specific, and cheap, and the case for requiring its creation rests on an existing precedent for mandating record *generation* rather than record surrender.

The claim is narrow on purpose. It does not say that preserving this record makes an AI system fair, compliant, or well-governed. It says that without it, several propositions institutions routinely assert become permanently untestable, and that this consequence is a design choice currently being made by default.

## 2. The objects at issue

The foundation paper identifies seven evidentiary objects that recur in AI-supported decisions in regulated settings:

1. **Decision-time inputs and context** — what was actually presented to the system and to any human at the moment of decision.
2. **Functional feature dependence** — attribution under a declared value function and background construction (SHAP and relatives).
3. **Local behavioural approximation** — a surrogate fitted around an instance (LIME and relatives).
4. **Internal computational states** — attention maps, activations, and similar exposures.
5. **Generated rationales** — natural-language accounts produced by the system.
6. **Human deliberative record** — what a reviewer was shown, consulted, recorded, and decided.
7. **Institutional authorization** — signatures, approvals, and the recorded fact that an authorized actor committed.

These are not interchangeable, and an artifact exposing one does not establish a proposition about another. That is the foundation paper's structural line. What follows asks a different question about the same list: which of these can be produced later, if nobody produced them at the time?

## 3. What "recomputable" requires

An object is recomputable if it can be regenerated after the fact such that the regenerated object is the same evidence as the original would have been. That requires three things simultaneously:

- **The operative system state.** The specific model version and configuration that ran, not a successor, not a retrained checkpoint, not "the production model."
- **The operative inputs.** The exact input as presented, including any preprocessing, feature construction, and enrichment applied at the time.
- **The method construction.** For attribution methods, the value function, background or reference distribution, sampling parameters, and software version.

Miss any one and the regenerated object is evidence about a different system, a different case, or a different method. It may still be informative. It is not the same evidence, and it cannot support a claim about what happened.

The three requirements share a dependency: all of them are facts about the *state at decision time*, and none can be inferred from the decision's outcome. A record of "denied, 2026-03-14" does not identify which model version denied it.

## 4. The partition, corrected

The foundation paper observes that feature attributions, local approximations, and internal-state observations are in principle recomputable later, while the binding is not. That is right, and it understates the result. The correct statement is stronger:

> Recomputability is not a property of an evidentiary object. It is a property conditional on a preserved binding. Nothing in the list is recomputable without one.

This yields a partition with three classes rather than two.

**Class A — recoverable, conditional on the binding.** Functional feature dependence, local behavioural approximation, internal computational states. Each of these is a deterministic (or seeded) function of model, configuration, input, and method construction. Given all four, each can be regenerated at any later date, at a cost measured in compute rather than in institutional memory. Given fewer than all four, none can. These objects are not durable; they are *reconstructible*, and their reconstructibility is entirely parasitic on a record that is itself Class B.

**Class B — irrecoverable in principle.** Three items sit here.

- *The binding itself*: which model version, under which configuration, under which policy in force, produced this decision on this file. This is a contingent historical fact. It leaves no trace in the outcome and cannot be derived from the decision or from the system state.

  One qualification matters and should not be buried. A binding that was never recorded may sometimes be *reconstructed circumstantially* — from deployment logs, change-management records, release timestamps, or configuration histories that were kept for unrelated reasons. This is the ordinary situation in which custody is established by inference rather than by record. It is a real pathway and it is worth naming, but it differs from the recorded case in three ways that matter for evidence: it is available only when such collateral records happen to exist and happen to be retained; its confidence must itself be established rather than assumed; and it degrades as the collateral records are themselves rotated, compacted, or aged out. A circumstantially reconstructed binding is therefore not a substitute for a recorded one. It is what an institution is left arguing about when it did not make one.
- *Decision-time inputs and context*: what was actually presented. Data changes. Records are updated, corrected, enriched, and overwritten. A field read at decision time may hold a different value a week later, and the current value is evidence about the present, not the past.
- *The human deliberative record*: what the reviewer was shown, what they consulted, what they changed. A reviewer's later account is a new object — a generated rationale by a human author — and the foundation paper's structural line applies to it with equal force.

**Class C — contemporaneous but conventionally preserved.** Institutional authorization. Signatures and approval logs are also irrecoverable in principle, but institutions already retain them as a matter of course, for reasons that predate AI. They are Class B objects that the existing record-keeping regime happens to catch.

Generated rationales sit awkwardly and deserve a note. Where generation is stochastic, the specific rationale emitted is not recomputable even with a perfect binding; only the distribution is. Where generation is seeded and the seed is recorded, the rationale becomes Class A. The seed is part of the binding.

## 5. The leverage argument

The corrected partition changes what the binding is for.

Read as one irrecoverable object among seven, the binding is one item on a preservation list, competing with six others for storage, engineering attention, and vendor cooperation.

Read correctly, it is the enabling condition for three others. Preserving it converts Class A from lost to recoverable at any future date. That is a leverage ratio, and it is the argument that makes a narrow mandate plausible: one record of a few identifiers rescues three evidentiary objects that would otherwise be unreachable, and it does so without requiring institutions to store explanations for decisions nobody will ever examine.

The remaining Class B items — decision-time context and the reviewer record — get no leverage from the binding and require separate preservation. That is a real limit on the proposal, and it should be stated rather than elided: **the minimum sufficient record has two components, not one.** The binding rescues the machine-side objects. It does nothing for what a human was shown.

## 6. The retention corollary

A binding is a pointer. A pointer to a deleted object is not a record.

If a bank preserves "model v4.2.1, config hash abc123, policy P-17" and the vendor has since retired v4.2.1 and retains no artifact of it, the binding documents that a determinate system produced the decision while leaving that system permanently unavailable. The bank's record is honest and useless. Class A has not been rescued; it has been annotated.

This produces the actual demand on vendors, and it is narrower than the demands usually made of them. It is not a demand for source code, training data, or method transparency. It is a demand for **version retention and retrievability for the applicable record-retention period**: that a model version identified in a customer's decision record remain instantiable, or at minimum that its parameters and configuration remain archived and available under contract, for as long as the decision it produced remains subject to examination or challenge.

Stated that way it is a procurement term, not a policy revolution, and it is the kind of thing a trade group or a supervisory expectation could make standard across vendors in a way no single community bank can negotiate alone.

## 7. The minimum sufficient record

Consolidating, the proposal is that a decision record in a regulated AI-supported process should bind, at decision time:

- model identifier and version,
- configuration identifier or hash, including any feature-construction or preprocessing version,
- policy or rule version in force,
- case or file identifier,
- the inputs as presented, or an immutable reference to them,
- generation seed, where outputs are stochastic and later reproduction is claimed,
- timestamp and the authority under which the decision was taken.

And, separately, for decisions involving human review: what the reviewer was presented with, and what they did with it.

The first list is small — identifiers and hashes, on the order of a few hundred bytes per decision. It is smaller by orders of magnitude than storing an explanation artifact per decision, which is the alternative most explanation-centred proposals imply. The second list is more expensive and is where the cost argument actually has to be made; this paper does not resolve it.

## 8. Precedent for mandating generation

The objection to any of this is that examination authority reaches records an institution holds, not records it declined to create. That objection has a known answer.

The Home Mortgage Disclosure Act did not ask institutions to surrender loan data they happened to keep. It required the loan-level record to be *generated* so that oversight would have something to examine. The record-keeping obligation was created because the oversight purpose required an object that would not otherwise exist.

A decision-time binding is a considerably smaller requirement of the same kind: a handful of identifiers, generated at the moment of decision, so that later examination has a referent. Identifying the smallest sufficient rule is not the same as establishing that it should be adopted, and this paper does not claim the latter. It claims that the rule is small, that its absence forecloses several categories of later verification permanently rather than expensively, and that the precedent for requiring generation rather than surrender is established.

## 9. What would defeat this argument

Three observations would materially weaken or break it.

**Nondeterminism at scale.** Class A depends on regeneration producing the same object. If, in practice, attributions computed against a correctly identified model version and configuration diverge materially — through floating-point nondeterminism, hardware differences, unrecorded library versions, or unseeded sampling in the attribution method itself — then Class A is not recoverable and the minimum record must grow to include the artifacts themselves. This is an empirical question with a cheap experiment attached, and it should be run before the policy claim is pressed.

**Binding unavailability at source.** If vendor systems do not expose a stable version and configuration identifier at inference time, the bank cannot record a binding regardless of obligation. The proposal then becomes a vendor-interface requirement before it can be an institutional record requirement, which changes who must move first.

**Substitutability of later reconstruction.** If, for the propositions that actually arise in examination and litigation, a reconstruction against a successor model is treated as adequate — because the question asked is about typical system behaviour rather than about this decision — then the recomputability boundary is real but not consequential, and the effort belongs on population-level validation instead. This is a claim about what examiners and courts actually ask, and it is answerable by looking at what they have asked.

## 10. What this does not establish

It does not establish that a preserved binding makes a decision correct, lawful, or fair. It does not establish that any particular affected party can obtain the record, which is a question of access and standing addressed elsewhere. It does not establish that the cost of the human-review half is proportionate. And it does not establish that regulators should require any of this — only that the requirement, if made, would be small, that its absence is currently forfeiting evidence irreversibly, and that this forfeiture is happening by default rather than by decision.

---

## Notes for revision

- **Verify before circulating**: the HMDA characterization (record generation vs. surrender) is stated from general knowledge and needs a citation to the statute and to Regulation C's LAR requirements.
- **Open**: the nondeterminism claim in §9 is the load-bearing empirical question. A small experiment — recompute attributions against a pinned model/config across environments and measure divergence — would either harden §4 or force it to change. Worth running before submission.
- **Relationship to the foundation paper**: this piece needs the empty-chair frame only as motivation. It is written to stand alone with a single citation back.
- **Length**: currently ~2,000 words. Comment-letter form would want the §7 record spec and §8 precedent foregrounded; journal form would want §4 and §5 foregrounded and §7 as a consequence.
- **Unresolved**: whether Class C (institutional authorization) is worth separating or should collapse into Class B with a note. Kept separate here because the existing-retention fact changes what has to be argued for.
- **Changed in this revision**: §4's Class B entry for the binding previously said "irrecoverable in principle." That was too strong. Circumstantial reconstruction from collateral records is a real pathway, and the honest claim is that it is contingent, of unestablished confidence, and decaying — not that it is impossible. The policy argument is unaffected and arguably improved: the ask is now "make the recorded case available" rather than "avert an impossibility."
