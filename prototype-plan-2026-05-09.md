# Prototype Plan

Living document. Current lean at top; revision log below. Plans change — the log is how we keep them from being silently rewritten.

---

## Purpose (Rev 3, 2026-05-09)

This prototype exists to give **Olorin** an alternative to SHAP/LIME as their regulatory observability layer. Mode collapse toward SHAP/LIME is the default path because those tools have regulator legibility and mature tooling. If we don't demonstrate a viable alternative on a real timeline, Olorin defaults to SHAP/LIME because they have a problem they need to solve.

The prototype's value is measured **against the SHAP/LIME counterfactual on regulator-legible dimensions**, not against an academic baseline. The falsification target is comparative, not existential.

**Target window:** A–E built by ~2026-05-23.

## Three-deliverable structure (Rev 3, 2026-05-09)

The work produces three distinct artifacts, not one:

1. **Olorin briefing document** — landscape, options, pros/cons, final recommendation. Olorin-shaped voice. Uses the prototype as evidence. Due in the engagement window.
2. **Regulator-facing document** — aligned with the Olorin recommendation but framed as policy-and-practice positioning, not vendor advice. Audience: regulators (OCC, FRB, CFPB, BIS-FSI) and bank governance professionals. Follows the briefing.
3. **Research paper(s)** — truth claims about Rashomon set construction, the V₁→V₂ predictive-test record, the policy-constrained Rashomon methodology, the adversarial-pair stipulation move, reasoning-trace extensions. Engages Zuin (2023), UNIVERSE (Donnelly et al. 2026), Rudin et al. "Amazing Things" (ICML 2024) directly.

Each requires different framing, voice, and evidence. Conflating them was making the position paper feel overloaded.

## Methodology centerpiece (Rev 3, 2026-05-09)

**Policy-constrained Rashomon construction.** The Rashomon set R(ε) is built from a documented bank policy graph rather than from a generic interpretable model class. Every model in R(ε) is, by construction, a refinement of documented bank policy. Within-set disagreement is disagreement *about how to apply that policy*.

This resolves multiple problems at once:

- **Novelty (vs Zuin 2023).** Zuin published the disagreement-routing core idea on a generic model class. The policy-constrained construction is a categorically different intellectual move; the disagreement now means something specific about policy interpretation.
- **Bank deployability.** Banks deploy what codifies their existing practice, not what displaces it.
- **Regulator alignment.** Regulators expect models to match documented policy. Policy-constrained construction makes this automatic.
- **Olorin's competitive moat.** Mode-collapse-as-moat: competitors converging on SHAP/LIME aren't even in the same product category.

The architecture splits into Tier 1 (policy-constrained Rashomon set, reason-of-record) and Tier 2 (LLM advocates feeding adversarial-pair stipulation, exploration of residue, never the decision function). Reasoning-trace constraints further narrow R(ε) when LLM rollouts are available.

## Long-term arc (Rev 3, 2026-05-09)

The policy-codification system is the durable infrastructure; Rashomon-routing is one capability on top. Independent value propositions, all separable from AI/ML:

- Retrospective policy-change analysis ("if we tightened DTI from 43 to 40, how many of last year's approvals would have flipped?")
- M&A due diligence and merger planning (formalize policy graphs; characterize merge operations)
- Regulator audit substrate (verifying policy adherence becomes "is this decision a refinement of the graph?")
- FCRA / consumer adverse-action utility (failed-policy-node notation supports clearer notices and recourse)

Four buyer categories, not one. The Olorin briefing leads with the SHAP/LIME alternative as the immediate recommendation and closes pointing at the larger infrastructure play.

## Current lean (Rev 3, 2026-05-09)

**Build A + C + D + E in two weeks, with constrained B.** SHAP/LIME head-to-head threaded through all of it. Policy-constrained construction is the centerpiece, not an addition.

- **A — Routing signal.** Policy-constrained Rashomon ensemble (interpretable models, monotonicity-respecting, mandatory/prohibited features enforced) on synthetic + HMDA + LendingClub + Fannie Mae. Within-set disagreement surfaces hard cases.
- **C — Observability surface.** Disagreement scalar + UNIVERSE-style interval VI as runtime signals. The artifact a regulator sees. Load-bearing equal to A.
- **D — Adversarial-pair stipulation.** LLM grant/deny advocates over residual cases (Tier 2); residue extraction; thin HITL surface. Answers "what does a human do with this signal?"
- **E — End-to-end loop.** Wiring + Olorin briefing draft. Answers "show me it works."
- **B (constrained) — Reasoning-trace constraint.** LLM advocates' reasoning traces narrow R(ε) beyond verdict-matching. Full B (comprehensive R(ε) treatment) defers to follow-up.

### Sharpenings still in force

1. **SHAP/LIME comparison must be fair** — competent-quant-deployed version, not a strawman. Specific recommendations from the SHAP/LIME critique lit map: TreeSHAP not KernelSHAP for tree ensembles; grouped correlated credit features; interventional baselines from approved-applicant distribution; stable LIME (fixed seed, N≥5000, tuned σ, attribution-variance reported). Where SHAP/LIME will struggle even when defended: Slack adversarial scaffolding attack and cross-model Rashomon disagreement. *Non-negotiable on fairness.*
2. **Calibration baseline.** Within-Rashomon disagreement vs vanilla bagging variance — Rashomon framing has to earn its keep.
3. **Name the ambiguity proxy.** Pick one and own it. Don't slip between them.
4. **Datasets.** All four in parallel — synthetic (controlled experiments, ground truth), HMDA (regulator perspective, fair-lending dimension), Fannie Mae (mortgage with FICO, closest to thin demo policy graph), LendingClub (existing temporal substrate, V₁/V₂ test).
5. **Pre-registration discipline.** The pattern across pre-registrations so far is uniformity-assumption-failure (bin-4: assumed flat; V₁→V₂: assumed T/F symmetry). Future pre-registrations should explicitly model heterogeneity and predict per-region or per-side.

### Two-week shape

- **Days 1–2 (done).** Thin demo policy graph (`policy/thin_demo_hmda.yaml`); constraint encoder (`policy/encoder.py`) with 15 tests; synthetic generator (`policy/synthetic.py`) with standard + shifted mechanism support; HMDA loader + 22,481 RI 2022 cases; Fannie Mae loader (awaits manual download); V₁→V₂ predictive test executed and findings note committed; T/F asymmetry exploration note committed.
- **Days 3–5.** Policy-aware Rashomon constructor — extends the wedge's R(ε) construction to filter on `PolicyConstraints` (monotonic_cst, mandatory/prohibited subsets). Validate on synthetic data first (ground truth available), then run on HMDA + LendingClub. Bagging-variance baseline computed on the same data. Pre-register a heterogeneity-aware prediction on synthetic data before running.
- **Days 6–8.** SHAP/LIME defended-baseline implementation. TreeSHAP for tree ensembles; grouped correlated features; interventional baselines; stable LIME with attribution-variance reporting. Head-to-head on synthetic (ground truth), HMDA, LendingClub. Pre-register the comparison criteria before running.
- **Days 9–10.** D — adversarial-pair stipulation. LLM grant/deny advocates over high-disagreement cases; residue extraction; thin HITL surface. Tier 2 architecture, never the decision function.
- **Days 11–12.** Constrained B — advocates' reasoning traces feed Rashomon constraint; show whether trace-matching narrows R(ε) beyond verdict-matching.
- **Days 13–14.** E (end-to-end loop) + Olorin briefing draft. OTS stamp the result.

### What slips first if reality pushes back

Full B. The constrained demonstration (traces *can* constrain) stays; the comprehensive R(ε) treatment moves to follow-up. Everything else is non-negotiable for the pitch to land.

### What changed materially in Rev 3 (vs Rev 2)

- Three-deliverable structure replaces single-paper framing.
- Policy-constrained Rashomon promoted to methodology centerpiece (resolves Zuin novelty issue).
- Codification-as-infrastructure long-term arc captured.
- Datasets shifted from "HMDA only" to "all four in parallel" (each tells different things).
- SHAP/LIME defended-baseline specifics added from lit map (TreeSHAP, grouped features, interventional baselines, stable LIME).
- Pre-registration discipline updated with the uniformity-failure meta-pattern.
- V₁→V₂ findings note now part of the project record; P5 missed on T side; T/F asymmetry exploration committed.
- Day 1–2 work marked as completed (encoder, synthetic generator, HMDA loader, Fannie Mae loader scaffolding, predictive test execution, T/F exploration).

---

## Revision log

### Rev 3 — 2026-05-09 (end of day)

End-of-day reframing after a full session of methodology work. Key shifts from Rev 2:

- **Three-deliverable structure** named explicitly (Olorin briefing / regulator document / research papers). Each different audience and voice.
- **Policy-constrained Rashomon** promoted to methodology centerpiece. Zuin (2023) publishes the disagreement-routing core; what remains novel is the policy-derived constraint on the model class, the adversarial-pair stipulation on residue, and the reasoning-trace extension.
- **Codification-as-infrastructure** named as the long-term arc. The policy-codification system is the durable infrastructure; Rashomon-routing is one capability on top. Independent buyers: banks (deployment + retrospective + M&A), regulators (audit), customers/their counsel (FCRA/adverse-action), Olorin (consulting wedge).
- **All four datasets in parallel** (synthetic / HMDA / Fannie Mae / LendingClub) — each tells different things.
- **SHAP/LIME defended-baseline specifics** added from lit map (TreeSHAP, grouped features, interventional baselines, stable LIME, attribution-variance reported).
- **Pre-registration uniformity-failure meta-pattern** captured — bin-4 and V₁→V₂ both failed because they assumed homogeneity. Future pre-registrations explicitly model heterogeneity.

Day 1–2 work also marked as completed in this rev: thin demo policy graph, constraint encoder + 15 tests, synthetic generator with standard/shifted mechanisms, HMDA loader + 22,481 RI 2022 cases, Fannie Mae loader scaffolding (awaits manual download), V₁→V₂ predictive test executed (P5 missed on T side), T/F asymmetry exploration note committed.

### Rev 2 — 2026-05-09 (later)

Tony named the actual purpose: prototype is a counter-proposal to Olorin defaulting to SHAP/LIME for regulatory observability. Two-week target for A–E.

Key reframings:

- **Falsification target shifted from existential to comparative.** Not "does disagreement track ambiguity" but "does Rashomon-routed-decision give Olorin something SHAP/LIME cannot, on dimensions a regulator scores against?" Existence is necessary but insufficient — SHAP/LIME exists too.
- **C is no longer a thin slice.** Observability *is* the use case. The runtime disagreement signal is the artifact the regulator sees. Load-bearing equal to A.
- **D and E moved out of "Phase 3."** Both are part of the pitch surface. A regulator asks "what does a human do with this?" (D); Olorin asks "show me the loop" (E).
- **B constrained, not deferred.** Use LLM advocate reasoning as trace substrate (cheaper than full model-internal traces); demonstrate trace-matching narrows the Rashomon set beyond verdict-matching. Full R(ε) treatment defers to follow-up.
- **SHAP/LIME comparison must be fair.** A competent-quant-deployed version. Beating a strawman dies instantly on regulator legibility — the very axis SHAP/LIME owns.

This rev also resolves the "is this a vanity project" question Tony raised earlier the same day: real audience (Olorin), real counterfactual (SHAP/LIME deployment), real deadline (~2026-05-23) = not vanity. The remaining test is whether the prototype actually gets built on the timeline.

### Rev 1 — 2026-05-09

Reviewed Rev 0 with Tony. Endorsed the A + thin-C lean. Two updates:

- The "B is synthetic, finger on scale" objection is stale given the May 6–7 reasoning-trace work. B is now empirically grounded, but still belongs in Phase 2 because A's leg has to hold first.
- Added three sharpenings: calibration baseline (vs bagging), explicit ambiguity proxy, domain choice (HMDA).

What survived from Rev 0 and is still load-bearing: **C is the move that makes this an artifact you can hand Margo.** The disagreement scalar exposed as an observability signal is the framing she'd recognize as a real systems object.

### Rev 0 — circa 2026-05-06 (recovered from claude code logs)

Original framing of the prototype fork. Captured verbatim because the texture of how the call was made matters for future revisions:

> Yes — building something is the right move. The conversation has been ranging over abstractions and the structure is dense enough now that an actual artifact will make some claims testable and others visibly fragile, both of which are useful.
>
> Scope-flag first: this is appropriately-sized for a single brainstorm — *not* a multi-subsystem decomposition. The methodology has 6+ structural moves but a prototype need only exercise one or two well.
>
> The domain choice (micro-lending vs SMB) is downstream of *what the prototype actually tests*. Picking the domain first locks in a domain whose features may not foreground the part of the methodology you most want to probe — micro-lending stresses scale and fairness with thin per-case info, SMB lending stresses rich reasoning per case with fewer cases and real ECOA exposure. Picking the test target first lets the domain follow.
>
> So before we settle on the domain, the upstream fork. Which slice of the methodology do you most want this prototype to exercise?
>
> **A) Routing signal.** Build a small Rashomon ensemble (handful of differently-tuned interpretable models), run cases through it, surface within-set disagreement, route high-disagreement cases to a "human" tray. Tests: does within-Rashomon disagreement actually distinguish hard cases from easy ones?
>
> **B) Reasoning-trace + R(ε) pipeline.** Capture (synthetic) reasoning traces, search for models that reproduce both verdicts and reasoning paths, validate. Tests: is the reasoning-trace-matched Rashomon set actually more constrained than verdict-only? Is "interpretable in the Rudin sense" achievable from this substrate?
>
> **C) Observability surface.** Expose the disagreement scalar as a runtime signal — SLOs, traces, the "observability of a posterior over models" problem. Tests: what does this look like to operations? What does Margo's infrastructure need to add to handle it?
>
> **D) Adversarial-pair stipulation HITL UX.** Generate grant-side / deny-side advocates, run stipulation, present the residue to a human. Tests: can humans actually adjudicate the residue more reliably than they decide from scratch?
>
> **E) Minimal full loop**, all of the above shallowly — useful for showing end-to-end shape, less useful for testing any single claim rigorously.
>
> My lean: **(A) plus a thin slice of (C)**. (A) is where the methodology's empirical claim lives and is the cheapest piece to *falsify* — if disagreement doesn't track ambiguity, the structure's leaning on a wobbly leg. (C) layered on (A) yields the artifact you'd hand Margo. (B) is more ambitious but depends on inventing reasoning traces, which puts a finger on the scale. (D) and (E) come later, after we know (A) holds up.

This Rev 0 was never captured in the repo at the time. Tony recovered it from claude code logs on 2026-05-09 and offered it back. The fact that it was almost lost is itself the reason this file exists.
