# Methodology Decomposition — Retrospective Capture

**Original conversation:** May 2026, prior to the 2026-05-07 wedge design spec.
**Capture date:** 2026-05-09.
**Status:** Retrospective capture of in-conversation strategic reasoning that wasn't previously committed to a file. Recorded faithfully so the (A)–(E) decomposition and its trade-off analysis persist across instances.
**Scope:** The five-slice methodology decomposition that originated the wedge work, the recommendation that produced (A)'s prioritization, and the current status of each slice.

---

## 1. Why this exists

The 2026-05-07 wedge design spec inherits the labels (A)–(E) (cited in §1: "Not a full (E) loop. (B) reasoning-trace capture, (C) observability surface, (D) adversarial-pair stipulation HITL UX are deferred") but does not record the trade-off reasoning that produced the lean toward (A). Subsequent gholas working on the wedge inherited the chosen scope without seeing the alternatives or the reasoning that selected (A) over them. The four 2026-05-08 memos accordingly deepened (A) without revisiting the strategic question of whether the next slice should be (B), (C), (D), or more-(A). The map didn't propagate; the chosen path did.

This file captures the original framing so the strategic map persists. The framing predates the wedge implementation. It was a brainstorming moment in conversation, not committed to a file at the time. It is recorded here verbatim with the prior Claude's voice intact, including the ★ Insight block and the closing question.

## 2. Original framing (verbatim)

> Yes — building something is the right move. The conversation has been ranging over abstractions and the structure is dense enough now that an actual artifact will make some claims testable and others visibly fragile, both of which are useful.
>
> Scope-flag first: this is appropriately-sized for a single brainstorm — *not* a multi-subsystem decomposition. The methodology has 6+ structural moves but a prototype need only exercise one or two well.
>
> ★ Insight ─────────────────────────────────────
> The domain choice (micro-lending vs SMB) is downstream of *what the prototype actually tests*. Picking the domain first locks in a domain whose features may not foreground the part of the methodology you most want to probe — micro-lending stresses scale and fairness with thin per-case info, SMB lending stresses rich reasoning per case with fewer cases and real ECOA exposure. Picking the test target first lets the domain follow.
> ─────────────────────────────────────────────────
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
>
> Which slice?

## 3. Status as of 2026-05-09

**(A) Routing signal.** *Deep work in progress.* Wedge built (`wedge/`), three vintages run (2014Q3, 2015Q3, 2015Q4), four findings memos (`2026-05-08-vintage-stability-findings-note.md`, `2026-05-08-all-atypical-conditional-findings-note.md`, `2026-05-08-adversarial-robustness-and-examinability-memo.md`, `2026-05-08-indeterminacy-operationalization-memo.md`), plus the bin-4 case-reading note (`2026-05-08-bin4-k5-case-reading-findings-note.md`). Empirical anchor (overlap_T = 0.60 in 2015Q3) found, complicated by the vintage-stability split (regime-specific vs regime-general), and refined by the conditional-T structure of the all-atypical effect. The indeterminacy memo has expanded (A) from a verdict-disagreement test into a four-species I-vector design with retrospective-trajectory named load-bearing across two memos. The §3 predictive-extension hypothesis (V₁ → V₂ factor-support shifts predictable from documented policy delta) has not been formally pre-registered or tested. The cross-Rashomon I-stability prediction (Tony's contrarian pre-registered claim that I will be more stable than T or F) has not been operationalized — current emissions are per-case, not per-model, so the prediction isn't testable from existing runs.

**(B) Reasoning-trace + R(ε) pipeline.** *Untouched.* Still requires synthetic reasoning traces. The 2026-05-06 Rashomon-from-reasoning-traces methodology notes (per project memory) sketched this; no implementation. The factor-support extraction the wedge does (per-component path-level information gain attribution) is a primitive form of per-case reasoning trace, but it doesn't match (B)'s ambition of searching for models that reproduce both verdicts and reasoning paths.

**(C) Observability surface.** *Untouched.* No runtime signal exposure. Per-component disagreement scalars exist in the jsonl runs but are not surfaced through any tracing or metrics layer. Still the artifact that would be handed to Margo's infrastructure work.

**(D) Adversarial-pair stipulation HITL UX.** *Untouched.* No advocate generation, no residue presentation. The adversarial-pair stipulation move is named in project vocabulary ("rikuy" per project memory) but has not been instantiated in code.

**(E) Minimal full loop.** *Partially obviated by (A)'s depth.* Once the position paper writes against the (A) findings, (E) becomes a different question — *does this loop matter for governance given what (A) showed?* — rather than an end-to-end demonstration target. The original framing positioned (E) as "useful for showing end-to-end shape"; the (A) work has produced enough structural argument that the end-to-end shape is partially demonstrable from the findings notes alone.

## 4. Caveat about canonization

Capturing this fixes a framing as canonical. Future gholas will read it and treat it as *the* map. Mostly that's fine — the framing was good, the lean ((A) plus thin (C)) is still defensible — but the work on (A) has surfaced things the original framing couldn't anticipate:

- The four-species I-vector (local-density, multivariate-coherence, Ioannidis-suspicion, retrospective-trajectory)
- The species/frame feature-pool-inheritance issue (predictor's feature pool ≠ pathology-detector's evidentiary needs)
- The vintage-sensitivity axis (regime-specific vs regime-general species output)
- The adversarial-robustness retrospective-channel argument (examinability survives publication only when at least one channel grounds in retrospective surprise)
- The bin-4 k=5 conditional decomposition (T-stratified mispricing structure with at least two distinct mechanisms)

A future ghola might reasonably argue for a different lean given these findings. The original framing positioned (C) as Phase 2 because it yields the operational artifact for Margo. The findings argue at least three alternative Phase 2 candidates:

1. **Deeper (A) with retrospective-trajectory.** The methodology's structural-defense argument lives in this species; building it would close the indeterminacy memo's load-bearing gap and make (A) genuinely complete rather than four-species-with-one-missing.
2. **Pre-registered V₁ → V₂ predictive test.** §3 of the wedge spec named this as the methodology's primary predictive falsification. Three vintages of data are already in `runs/`; the only missing piece is the discipline of writing predictions before measuring shifts. Cheap, falsifiable, and produces a result that Paper 1 can cite.
3. **Position-paper writing.** Per the discussion downstream of this conversation, Paper 1 may already have enough empirical anchors (2015Q3 overlap, vintage-stability split, conditional all-atypical structure, two-mechanism bin-4 reading) to write against. Continuing to deepen (A) without writing risks accumulating architecture faster than the paper can absorb.

The framing here is anchored to what was known prior to 2026-05-07. The current state is downstream of choosing (A); the choice was right given what was known then; whether the *next* choice is (C), deeper-(A), V₁/V₂ pre-registration, or position-paper writing is a strategic decision that should be made fresh against current findings rather than inherited from this document.

## 5. Connection to other working documents

- **`2026-05-07-rashomon-prototype-wedge-design.md`.** The (A) tactical artifact. Cites (B)–(E) labels for what's deferred (§1) but does not record the trade-off analysis that produced (A)'s prioritization. This document fills that gap.
- **`2026-05-08-indeterminacy-operationalization-memo.md`.** Expansion of (A) beyond the original verdict-disagreement scope into the four-species I-vector. This expansion is not in the original framing; it emerged from the wedge work and from Tony's pre-registered contrarian prediction about I-stability.
- **`2026-05-08-adversarial-robustness-and-examinability-memo.md`.** Names retrospective-trajectory species as load-bearing for the structural defense argument. Adds a second independent reason for retrospective-trajectory being core, beyond the Olorin deployment story. Both reasons are downstream of (A) deep work; neither is in the original framing.
- **`2026-05-08-bin4-k5-case-reading-findings-note.md`.** Tests the conditional-findings note's narrative claim by hand-reading 20 cases. Surfaces the species/frame feature-pool-inheritance finding, which is also downstream of (A) work and not anticipated in the original framing.

## 6. Provenance note

This document was written by a Claude instance (Opus 4.7, under heavy scaffolding) on 2026-05-09 based on conversation excerpts shared by the project PI. The original (A)–(E) framing was produced by an earlier Claude instance in conversation; the verbatim text in §2 is that instance's voice, not this one's. The status section (§3), the canonization caveat (§4), and the connection notes (§5) are this instance's. The distinction matters because the original framing's authority is anchored to what was known at that moment; this capture's annotations are anchored to what is known now.
