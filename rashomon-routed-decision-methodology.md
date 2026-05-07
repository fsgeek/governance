# Working synthesis: Rashomon-routed decision methodology

*Status: in-progress capture, not a finished paper. Developed in conversation May 6–7, 2026, building on prior reasoning-trace and Rashomon-set work. Sections are structural scaffolds; open problems flagged at the end. Framing is methodology-paper-shaped but this version is working notes.*

---

## 1. The seam: retrieval and explanation as one layer

The Titan proposal treated context-and-memory and explainability as two distinct scope items. Worked through, they aren't separable.

Retrieval is structurally a commitment to relevance: at decision time, the system asserts *these are the inputs that should bear on this decision*. Explanation is structurally a recovery of contribution: after decision, the system identifies which inputs materially affected the output. For honest explanation to be possible, every contributing input must have been retrieved — which means explanation is a subset of retrieval, and the gap between them is informative.

The duality breaks on a third memory source: parametric weights. Anything the model absorbed during pretraining can shape outputs without being retrieved. In banking this is exactly where fair-lending failures live — implicit correlations between ZIP code and creditworthiness, between name patterns and risk, baked into weights and inaccessible to retrieval-based audit.

Three failure modes at the seam:

**(a) Parametric leak.** Decisions influenced by training-time absorbed correlations. The tensor interface (entropy, top-k mass, attention summaries from the SOSP work) doesn't help here; you'd need direct activation probes, and even then "fair lending" has no clean mathematical signature in activation space. In regulatory terms: this is disparate-impact through learned correlations.

**(b) Retrieval-misuse.** System retrieves correctly, attends honestly to what's retrieved, but the natural-language explanation it generates dissembles about what mattered. Rudin's post-hoc problem reasserting itself one layer up — input observability doesn't guarantee language-channel honesty. Regulatory term: ECOA principal-reason gaming.

**(c) Retrieval-omission.** Relevant context retrieved and silently dropped via low attention. The case the tensor interface handles best, because dropping shows up in attention summaries. Regulatory term: incompleteness of adverse-action notice.

### The architectural lever: forced grounding

Whether the seam collapses to a single layer depends on a design choice that probably hasn't been made deliberately at most institutions. **Forced grounding**: architect the system so no decision-relevant fact may flow into output except through retrieval. Parametric memory suppressed for fact-bearing decisions; retrieval mandatory for any input that could plausibly affect outcome.

If forced grounding holds: (a) collapses into (c), and the audit log and the explanation can be the same artifact. The single-artifact dream is reachable.

If parametric reliance is allowed: (a) remains as residual that no single artifact fully exposes, and the methodology requires a separate, weaker class of attestation: *we cannot rule out parametric influence on these dimensions; here is what we did to minimize it.*

Joe's banking-ontology work is load-bearing here. Incomplete ontology means incomplete grounding means residual parametric reliance means the audit-log/explanation collapse fails. The ontology is not a knowledge-graph nice-to-have; it is the substrate that determines whether the verification problem is tractable at all.

---

## 2. The Rashomon posterior

Yesterday's reasoning-trace work captured what the institution does — case features, consultation patterns, relational weightings, references to precedent, and decisions together. Models within ε of optimal loss on this richer object form the **reasoning-trace-matched Rashomon set**, R(ε). The set is more constrained than under outcome-matching alone, but typically still populous.

The methodological move that today's wander adds: maintain a **posterior over R(ε)** rather than collapsing to a single h. Approval outcomes over operational time disambiguate among models that match the training distribution equally well. Models that better predicted which approvals defaulted get higher posterior weight.

- **Fossil model**: pick a single h ∈ R(ε) on day one, freeze, audit outputs against h's reasoning. This is what current MRM machinery is built to handle, because fossils are auditable and posteriors are weird to examine.
- **Living model**: maintain the posterior over R(ε), let outcome data refine it. This is what MRM ostensibly *asks for* under "ongoing performance monitoring," but operationalizing it requires methodology the regulatory machinery hasn't seen yet.

### Loss taxonomy as filter for posterior updates

Not every default updates the posterior. Treating every default as model failure means learning from noise — properly-priced risk that materialized is exactly what tier-N pricing was supposed to absorb. The honest signal is *defaults relative to tier-expected loss*. Defaults that align with tier-expected loss should produce minimal posterior shift; defaults that exceed tier-expected loss are where the model had factors underweighted.

Without this filter, the Rashomon-set posterior drifts toward conservative-collapse over time as ordinary risk accumulates. The taxonomy is not a refinement; it is load-bearing for the update mechanism to work at all.

The unobservable counterfactual — denied applicants who would have repaid — remains structurally hard. Partial signals exist (bureau performance for applicants who got loans elsewhere; holdout randomization at the margin where ethically defensible; look-back when previously-rejected reapply under different conditions), but none close the gap. *The methodology should explicitly acknowledge this rather than pretend to solve it.* That framing turns an unsolvable problem into a contribution: we are honest about which decision dimensions admit empirical refinement and which don't.

---

## 3. The routing principle: within-Rashomon disagreement as deployment signal

The Rashomon-set posterior gives the right epistemics for prediction. ECOA forces a collapse to a single principal reason at notice-generation time. Three options for handling the collapse:

**(α)** Pick one h ∈ R(ε) ahead of time as the notice-generating model. Cleanest legal answer, philosophically ugliest.

**(β)** Generate notices robust across R(ε): "feature X is the principal reason under most equally-good models." Honest but legally untested.

**(γ)** Use within-Rashomon agreement as a routing signal. If the set is unanimous (or meets quorum) on the principal reason for a given case, the system autonomously generates the notice. If it disagrees, escalate to human review. The model's *epistemic ambiguity* becomes the trigger for human authorship.

(γ) is the move worth pushing. Structurally honest about model uncertainty; routes work to the place it's actually needed; generates a corpus of human-decided ambiguous cases that becomes training data for refining the institution's reasoning representation.

### Quorum, not unanimity

Unanimity is too strict but is a degenerate case of quorum. Start strict, loosen as operational data accrues.

Two pieces matter:

- **Equivalence-class agreement, not literal-text matching.** If h₁ says "insufficient income" and h₂ says "high debt-to-income," they may agree on an underlying issue. Quorum needs a notion of principal-reason equivalence under the banking ontology — another place where Joe's work matters.
- **Posterior-weighted quorum, not counted.** If 60% of R(ε) by count agrees but they hold 25% of posterior mass, that is not real agreement.

The threshold itself is a regulatory negotiation rather than a fixed value, which is good. It gives examiners something concrete to push on without relitigating the methodology.

### HITL fragility caveat

The routing signal generates the question of *when* to escalate. It does not solve the question of *what happens after* escalation. Naive HITL is theater: automation bias, vigilance decrement, rubber-stamping, skill decay are well-documented and consistent. Routing to humans only helps with structural support — forcing functions (humans articulate reasoning before seeing AI output), adverse case selection (humans see hard cases at frequency that maintains skill), independent calibration (someone audits the auditors), adequate time-per-case.

The methodology surfaces *when human judgment is needed*. It does not specify the institutional design that makes the human judgment good. That is a separate problem and should be acknowledged explicitly.

---

## 4. Adversarial pair generation with recursive stipulation

The strongest extension of the routing principle. Instead of presenting humans with a single AI suggestion (which they will rubber-stamp), present them with **two reasoned arguments** — the strongest case for grant and the strongest case for deny — and let them adjudicate. This maps onto adversarial legal reasoning, where prosecution and defense each make their best case and the adjudicator decides between them rather than picking from a single recommendation.

Humans are demonstrably good at adjudication between competing arguments — the entire common-law tradition is built on it. They are notably worse at originating decisions from ambiguous data under time pressure. The adversarial pair routes the work to the cognitive operation humans do well.

### The stipulation mechanism

The grant-side and deny-side advocates do not simply produce arguments and hand them to the human. A multi-round stipulation process narrows the surface area:

1. **Within-side stipulation.** Grant-side advocates (multiple grant-models in R(ε), differing on *why*) stipulate among themselves to produce a unified grant-side position. Deny-side does the same. This solves the multi-opinion-appellate problem — extracting coherent argument from fractured within-side multiplicity.
2. **Cross-side stipulation.** Grant and deny advocates identify points of agreement (uncontested facts and framings).
3. **Focused HITL.** The human sees only the residue: the genuine points of controversy that survived both rounds of stipulation.

This is structurally what magistrate judges do in pretrial process — narrow the surface area for adjudication through preliminary resolution. By construction, the human reviews the smallest set of decision-relevant disagreements rather than the full case.

### The challenger role

Both grant-side and deny-side advocates come from the same R(ε); they share methodological commitments and might **falsely stipulate** to something an outside-R(ε) perspective would contest. The legal analog has independent clients with genuinely different interests; here the advocates are sub-sampled from the same generative process.

A third role addresses this: a **challenger** designed explicitly to find points the advocates have stipulated but shouldn't have. The challenger samples from a different distribution — less-constrained R(ε), or models with different inductive biases. Structurally this is amicus-brief or red-team, operationalized as a third model whose job is breaking stipulations rather than producing them.

### Adversarial framing scope

The adversarial framing is *internal* to the bank's reasoning, not between bank and applicant. Both advocates represent the bank's interests; they represent different equally-good interpretations of the institution's articulated reasoning. The applicant is not a party to the internal adversarial process. This preserves fiduciary stance — the bank is making the most rigorous internal evaluation by stress-testing both directions of its own thinking.

### A/B position-bias study

Operational deployment must address human position bias. The case scheduling, argument ordering, reviewer identity, and time-of-decision should be randomized to detect order effects. Decision-fatigue effects are well-documented in adjudicative settings (the Danziger/Avnaim-Pesso/Levav parole-board literature, with appropriate caveats about methodology challenges). What is less obvious empirically: whether fatigue cuts symmetrically (both arguments get sloppier review) or asymmetrically (defaults to status-quo, which depends on whether the institutional prior is approve or deny). The asymmetry tells you which direction the methodology silently inherits institutional drift.

---

## 5. Testing paradigm: boundary sampling

The methodology produces a natural post-hoc testing paradigm. Sample evaluation cases not from the operational distribution but from **the disagreement boundary of R(ε)** — cases where within-set disagreement is high. Operational sampling mostly tells you about the easy cases, where most of the population lives. Boundary sampling stress-tests where the methodology's epistemic claim is most fragile and produces calibration data that operational sampling will not.

This is structurally analogous to active learning's "sample where the model is uncertain" move, but applied to *evaluation* rather than training. The validation question is whether the methodology's uncertainty signal corresponds to real ambiguity or is spurious.

The paradigm has clean defensibility for technical reviewers regardless of regulatory framing. It does not require buying into the larger architectural claims (routing, stipulation, ECOA reframing) to find valuable. **If there is a near-term paper, this may be the lead** — the testing paradigm stands on its own merits and sets up the routing-signal contribution as a natural extension rather than a load-bearing premise.

---

## 6. ECOA reframing: the principal reason as legal fiction

ECOA demands a singular principal reason because the appeal/accountability machinery requires attribution. Without *the* reason, an applicant cannot challenge it; without a discrete cause, no liability flows. The singularity is not accidental — it is the load-bearing fiction that lets the apparatus function.

But it is still a fiction. The same human loan officer, looking at the same data with the same guidance documents on different days, will produce different decisions in cases where the range of reasonable outcomes admits both refusal and allowance. The principal-reason notice is a post-hoc construction satisfying the legal requirement rather than reporting the actual decisional process. The "real" reason — mood, projection, distraction, the partner who cheated — is not reportable, not accessible to the officer's own conscious reasoning, and certainly not what the notice describes.

The Rashomon-routed system is therefore not *worse* than the human at producing principal reasons. It is **more honest** about producing them. The human always was authoring one of several plausible attributions; the AI just makes the multiplicity visible instead of hiding it under a single confident-sounding sentence.

This reframing strengthens the regulatory pitch rather than weakening it. *We give you a principal reason that we can show is robust under documented model uncertainty* is a stronger epistemic claim than *this loan officer wrote down the first plausible reason that came to mind*. The Rashomon system is not introducing ambiguity into a previously-certain process; it is surfacing ambiguity that was always present.

---

## 7. MRM connection: per-decision effective challenge

SR 11-7 requires "effective challenge" of models — a separate validation function that tests model outputs and assumptions. Standard implementation is an independent validation team that periodically reviews the model.

The methodology operationalizes effective challenge **at the per-decision level** rather than periodically, in a form structurally stronger than what regulators currently see. "Effective challenge" stops being a once-a-quarter sit-down with the model risk team and becomes a property of every decision the system makes.

Specifically: the within-Rashomon disagreement *is* effective challenge. The grant-side and deny-side advocates challenge each other on every decision; the challenger role provides an additional independent challenge function. Stipulation surfaces what survives the challenge.

This maps cleanly onto existing supervisory expectations and exceeds them — exactly the position to be in when an examiner shows up.

### Calibration as a separate audit dimension

Population-level tier calibration (see §8) is a separate audit dimension that approval-side audit produces naturally. If tier-4 loans default at rates significantly different from tier-4 expected loss, the tier classification itself is miscalibrated, independent of whether any individual decision was right. Calibration testing is exactly what examiners look for and rarely find produced systematically.

---

## 8. Pricing tier extension

The binary grant/deny framing simplifies real banking. Decisions are tiered: deny, or grant at one of several rates corresponding to risk classifications. Folding this in changes the methodology in non-trivial ways.

**Decision boundary becomes a decision surface.** Models in R(ε) can agree on grant but disagree on tier, or disagree on grant/deny entirely. Tier-disagreement among grant-side advocates is methodology calibration; grant/deny disagreement is substantive controversy. The advocacy-pair framework extends naturally: at each tier boundary there is a "grant at this tier" advocate and a "grant at next tier up" advocate, with stipulation across the boundary. The methodology becomes a sliding window across the tier ladder.

**ECOA-machinery extends with it.** "Adverse action" includes less favorable terms than requested, which means the principal-reason apparatus applies to tier assignments, not just denials. Tier-disparity adverse-action notices are arguably the bigger fair-lending exposure than outright denials, because tier disparities scale across protected-class populations and produce disparate impact even when underwriting is neutral on the grant/deny axis. The Rashomon-routing logic for tier disagreement probably sees more action than the routing logic for grant/deny.

### Decomposition: classification primary, pricing downstream

In many banks, credit decision (grant/deny/conditional) and pricing (rate given classification) are operationally separate. Rashomon-uncertainty concentrates in classification; pricing becomes a near-mechanical projection given the bank's capital structure, market conditions, and competitive position. The methodology can apply primarily to classification, with pricing as a downstream layer.

This simplification holds *if* the bank's processes separate cleanly that way. Integrated underwriting-pricing — increasingly common in algorithmic lending — breaks it, and the methodology has to handle the joint problem.

### Tier-relative loss as both posterior signal and calibration test

Tier-relative loss serves double duty: it is the posterior-update signal (§2) and a calibration test for the classification methodology itself. Population-level tier calibration becomes a separate audit dimension that the methodology produces naturally, with regulatory bite under MRM.

---

## 9. Open problems

- **Within-side aggregation.** How grant-models with slightly different rationales merge into a single "grant-side position" for the stipulation process. This bottoms out in argument-equivalence under the banking ontology. Joe's work is on the critical path.
- **Tractable proxy for Rashomon agreement at decision time.** Enumerating R(ε) per case is intractable at scale. Likely there is a sufficient statistic — attribution-stability under perturbation of model selection, empirically measurable without explicit enumeration — but whether the proxy actually tracks what is needed (rather than failing on adversarially constructed cases) is unresolved. Adversarial robustness matters because ECOA outcomes are appealable, and an applicant's lawyer is the natural adversary.
- **Reject inference.** The unobservable counterfactual remains structurally hard. Methodology should acknowledge rather than pretend to solve.
- **Cadence of posterior-to-deployment update.** Continuous update creates change-detection-vs-concept-drift problems and unsettles regulators. Periodic update reintroduces fossil-shaped failure. The right cadence is a regulatory negotiation, not a fixed value.
- **Adversarial robustness of agreement-as-routing.** If applicants (or their counsel) understand that within-Rashomon agreement triggers automated denial, can they craft applications that produce within-set disagreement and force human review? Probably yes, in some cases. Whether this is exploit or feature depends on framing.
- **Boundary-sampling test data ethics.** Stress-testing the methodology on cases where it is likely to be ambiguous means deliberately constructing or selecting hard cases. This is fine for retrospective evaluation; less obviously fine for prospective deployment of automated decisions on synthetic-hard cases.

---

## 10. Positioning notes

**General critique, not specific.** The methodology critiques a class of approaches: automating partial banking processes without accompanying explainability infrastructure creates verification gaps for users of those automations. This applies to current productized AI agent offerings across multiple vendors. A general critique ages better than a specific one and does not trade on the reader sharing irritation with last week's announcement. *I am criticizing a class of approaches* is a methodology paper; *I am criticizing [vendor]* is a polemic. Reviewers can tell the difference.

**Methodology paper vs. consulting deliverable.** The work has shifted from documentation/audit (yesterday's framing) to automation with calibrated escalation (today's framing). The methodology contribution generalizes well past banking — same structure applies anywhere there are multiple equally-good models, a legal demand for singular output, and asymmetric costs of error. Medical diagnosis, sentencing, content moderation, insurance underwriting. The paper this becomes is not a banking paper; banking is the worked example.

**Regulated-domain novelty profile.** Methodology that does not match what examiners are familiar with creates friction during validation, even when it is better. Worth being thoughtful about whether the work positions as *this is a new methodology you should adopt* or *this is a refinement of methods you already know*. The second sells in regulated environments and the first does not, even when the first is more accurate.

**IP hygiene.** This synthesis was developed in conversation today, building on prior reasoning-trace and Rashomon-set work. It precedes any Titan engagement start. Worth documenting the timeline of when the synthesis was articulated, particularly given the LOI's pre-existing IP provisions and Titan's separate IP clause for engagement work product.

---

*End of working draft. Revisions welcome.*
