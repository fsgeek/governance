# Mechanism Specification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce a single canonical mechanism specification consolidating the architectural decisions distributed across 2026-05-07 through 2026-05-09 specs and memos, locking the dual-R_T/R_F policy-constrained construction that emerged from the 2026-05-10 conversation, formalizing Category 1 vs Category 2 retrospective failure detection, and serving as the citable source for prototype extension and regulator-document translation.

**Architecture:** Single markdown spec at `docs/superpowers/specs/2026-05-10-mechanism-specification.md`, organized in numbered sections. Each section is one task with an explicit acceptance criterion. The spec *consolidates and references* existing memos rather than restating their content — those memos remain authoritative for their topics. New material introduced here: (a) dual-set R_T(ε_T) / R_F(ε_F) construction as the architectural integration of the four-species I framing with the T/F mechanics work, (b) Category 1 vs Category 2 retrospective failure formalization, (c) policy representation expectations linking the codification layer to set construction, (d) prototype validation targets that bound the May 23 deliverable. Frequent per-section commits. The OTS post-commit hook stamps each commit automatically.

**Tech Stack:** Markdown, git, OpenTimestamps (existing post-commit hook). No code produced by this plan; the spec is a written artifact. Implementing the spec is a downstream plan.

**Spec lineage** (cite these by path inside the spec — do not restate their content):
- `docs/superpowers/specs/2026-05-07-rashomon-prototype-wedge-design.md` — V₁ measurement methodology and wedge design
- `docs/superpowers/specs/2026-05-08-indeterminacy-operationalization-memo.md` — four-species I vector
- `docs/superpowers/specs/2026-05-09-tf-mechanics-and-case-level-empty-support.md` — F = 1 − T mechanical correction
- `docs/superpowers/specs/2026-05-09-tf-asymmetry-exploration-note.md` — empty-support inversion at pair level
- `docs/superpowers/specs/2026-05-09-cliff-and-constraint-saturation-synthesis.md` — set-level cliff signal, three-signal decomposition
- `docs/superpowers/specs/2026-05-09-methodology-decomposition-retrospective.md` — (A)–(E) slice map and status
- `docs/superpowers/specs/2026-05-09-shap-vs-rashomon-result-note.md` — SHAP non-inferiority falsification
- `docs/superpowers/specs/2026-05-08-adversarial-robustness-and-examinability-memo.md` — retrospective-trajectory as load-bearing

**Scope note.** This plan produces the *specification*, not prototype extension. The wedge prototype (`wedge/`) currently implements V₁ measurement with degenerate T+F=1. Spec-driven extension to (a) dual-set construction and (b) Category 1/2 detection is a follow-on plan that depends on this spec being stable. The spec is also the citable source for the regulator-facing document and Paper 2 architecture sections; both are downstream consumers, not contents of this plan.

**Open decisions register** — locked as "open" intentionally. The plan does not require resolution of these before the spec is written; the spec writing may resolve some, and the spec must name the rest as deferred with rationale:
1. Policy representation format (structured rules, constraint expressions, hybrid)
2. Set construction algorithm (sample-and-filter, constrained optimization, multi-start)
3. Asymmetric ε between R_T and R_F (same threshold both sides, or different and how chosen)
4. I as operationalized disagreement between R_T and R_F (per-instance metric, population-level, set-symmetric-difference on predictions)
5. Retrospective trajectory species operational definition (statistical test, threshold, baseline)
6. Category 1 vs Category 2 formal criterion (conceptual distinction is clear; spec-level criterion is not)
7. Scope boundaries — what the spec *excludes* for the May 23 deliverable
8. Prototype empirical demonstration targets — what evidence the prototype must produce to validate the spec

**Revision provisions.** This spec is V1. The plan anticipates revision as prototype findings surface gaps and regulator-doc translation reveals operational fuzziness. Revisions land as dated changelog entries appended to the spec file; the spec is not forked into V2 unless the consolidation argument itself requires restructuring.

---

## File Structure

```
docs/superpowers/specs/
└── 2026-05-10-mechanism-specification.md    # The artifact
```

Single file. If it exceeds ~500 lines per the project's file-size rule, split reactively into `docs/superpowers/specs/mechanism-specification/` with section files and an index. Do not pre-split.

The plan itself lives at `docs/superpowers/plans/2026-05-10-mechanism-specification.md` (this file).

---

## Task 1: Scaffold the spec — Section 0 (TOC) and Section 1 (scope, status, lineage)

**Files:**
- Create: `docs/superpowers/specs/2026-05-10-mechanism-specification.md`

- [ ] **Step 1: State acceptance criterion**

Section 1 is done when a reader unfamiliar with prior memos can determine (a) what this document specifies, (b) what it does not specify, (c) which prior memos it depends on and what each contributes, (d) the document's relationship to the wedge prototype and to the downstream regulator-doc / Paper 2. Length target: 1-2 pages. Section 0 is a TOC listing all planned sections, including those not yet written, so a reader sees the shape.

- [ ] **Step 2: Draft Section 0 (TOC) and Section 1 (scope/status/lineage)**

File begins:

```markdown
# Mechanism Specification — Policy-Constrained Dual-Set Rashomon Construction

**Date:** 2026-05-10
**Status:** V1 draft, intended as the canonical source for the May 23 Olorin deliverable and as the architectural spine of Paper 2.
**Authoritative for:** the dual-set R_T(ε_T) / R_F(ε_F) construction; Category 1 vs Category 2 retrospective failure detection; prototype validation criteria for the May 23 deliverable.
**Defers to prior memos for:** four-species I-vector content (see indeterminacy memo); cliff signal mechanics (see cliff synthesis); T/F mechanical relationship within a single model (see tf-mechanics).

## 0. Table of contents
1. Scope, status, lineage
2. Policy representation
3. Set construction (dual R_T / R_F)
4. Indeterminacy I as inter-set disagreement
5. Retrospective trajectory species — operational definition
6. Category 1 vs Category 2 detection criteria
7. Prototype validation targets for May 23
8. Open decisions register
9. Cross-reference index

## 1. Scope, status, lineage
...
```

Section 1 prose covers: what's in, what's out, which prior memos are inherited as-is and which are extended by this spec. Explicit naming of the two new contributions (dual-set construction, Cat 1/Cat 2 formalization) and what existing material they integrate. One paragraph on the spec's relationship to the wedge prototype: "the wedge currently implements [X]; this spec specifies the extension to [Y]; the wedge implementation of the spec is a follow-on plan."

- [ ] **Step 3: Self-review**

Read Section 1 cold. Check each of the four acceptance criteria. If any fail, revise.

- [ ] **Step 4: Commit**

```bash
git add docs/superpowers/specs/2026-05-10-mechanism-specification.md
git commit -m "spec: scaffold mechanism specification (scope, status, lineage)"
```

---

## Task 2: Section 2 — Policy representation

**Files:**
- Modify: `docs/superpowers/specs/2026-05-10-mechanism-specification.md` (append Section 2)

- [ ] **Step 1: State acceptance criterion**

Section 2 is done when (a) the reader understands what "documented bank policy" means as input to set construction, (b) the form of policy expression is specified at least at a contract level (input shape, even if internal representation is deferred), (c) the connection to the existing `policy/` directory work (encoder.py, synthetic.py, thin_demo_hmda.yaml) is named, (d) the section explicitly states what the spec does *not* require of policy representation (e.g., natural-language parsing is not in scope for V1).

- [ ] **Step 2: Read existing policy work**

Read `policy/README.md`, `policy/encoder.py`, `policy/thin_demo_hmda.yaml` to understand what the project has already committed to as policy representation. The spec must be consistent with this or explicitly note where it extends it.

- [ ] **Step 3: Draft Section 2**

Cover: the contract — what does set construction expect from policy? Output of policy encoding is the constraint graph that bounds the hypothesis space. Reference existing encoder.py output shape. Note open decision #1 (structured-rules vs hybrid) — the spec commits to whichever the existing encoder produces and flags the open question of whether richer policy forms (natural-language policy documents, structured-rule + commentary hybrid) require encoder extension. Distinguish hard constraints (model must satisfy) from soft preferences (penalize but allow).

- [ ] **Step 4: Self-review**

Acceptance criteria check. Cross-reference with `policy/encoder.py` — does the section accurately describe what the encoder produces? If not, fix.

- [ ] **Step 5: Commit**

```bash
git add docs/superpowers/specs/2026-05-10-mechanism-specification.md
git commit -m "spec: section 2 — policy representation contract"
```

---

## Task 3: Section 3 — Set construction (dual R_T / R_F)

**Files:**
- Modify: `docs/superpowers/specs/2026-05-10-mechanism-specification.md` (append Section 3)

- [ ] **Step 1: State acceptance criterion**

Section 3 is done when (a) the dual-set construction is specified: R_T(ε_T) is the set of grant-supportive models ε_T-optimal under policy constraints; R_F(ε_F) is the analogous set on the deny-supportive side; (b) the asymmetric-ε question (open decision #3) is addressed — either resolved with rationale, or named as deferred with a default specified; (c) the construction algorithm (open decision #2) is specified at the contract level — input, output, invariants — with the choice of implementation algorithm permitted to vary; (d) the section explains why dual-set construction is structurally distinct from a single-set R(ε) — i.e., names the F = 1 − T flatness it resolves, citing tf-mechanics memo; (e) the section names the construction-relativity caveat from the cliff synthesis (§3): the construction is declarable and auditable, which is itself the transparency property.

- [ ] **Step 2: Read tf-mechanics and cliff synthesis sections cited**

Re-read `2026-05-09-tf-mechanics-and-case-level-empty-support.md` and `2026-05-09-cliff-and-constraint-saturation-synthesis.md` §3 to make sure the citations are accurate.

- [ ] **Step 3: Draft Section 3**

Cover, in order: motivation (F = 1 − T flatness problem in V₁ wedge); contract for R_T (model class, loss function, policy constraint, ε_T threshold; output: a set of models); same for R_F; the asymmetric-ε discussion (recommended default: ε_T = ε_F at V1, but the spec names the asymmetric case as architecturally permitted and notes the considerations); construction-relativity (R_T and R_F are defined relative to the declared policy graph, ε, algorithm, and training sample); structural-distinctiveness argument adapted from cliff synthesis §3.

- [ ] **Step 4: Self-review**

Acceptance criteria check. Verify each citation is to the actual content in the cited memo (re-open the memo, check the section number). Verify the section does not contradict the existing wedge spec's treatment of R(ε) — if it extends, name the extension explicitly.

- [ ] **Step 5: Commit**

```bash
git add docs/superpowers/specs/2026-05-10-mechanism-specification.md
git commit -m "spec: section 3 — dual-set R_T/R_F construction"
```

---

## Task 4: Section 4 — Indeterminacy I as inter-set disagreement

**Files:**
- Modify: `docs/superpowers/specs/2026-05-10-mechanism-specification.md` (append Section 4)

- [ ] **Step 1: State acceptance criterion**

Section 4 is done when (a) I is operationalized as disagreement between R_T and R_F (this is the new contribution; the indeterminacy memo specified I as a four-species vector, but the inter-set framing reframes what "I" *is* before the species decomposition); (b) the relationship to the four-species I-vector from the indeterminacy memo is made explicit — the species (local-density, multivariate-coherence, Ioannidis-suspicion, retrospective-trajectory) become *generators of disagreement* within and between the dual sets, not separate I dimensions; (c) the open question of per-instance vs population-level operationalization (open decision #4) is addressed — recommended default specified, alternatives named; (d) the section explains why this framing dissolves the supervisory problem for I (no labels for I needed; disagreement between two well-defined constrained sets is observable).

- [ ] **Step 2: Re-read indeterminacy memo sections 3 and 4**

Confirm the four-species content as written; the spec is *reframing*, not contradicting it.

- [ ] **Step 3: Draft Section 4**

Cover: the inter-set framing (I = disagreement between R_T(ε_T) and R_F(ε_F) on a case's prediction); how the four species enter as generators of disagreement; the per-instance default operationalization (recommended: a per-case scalar based on R_T-vs-R_F prediction divergence, with an attached species-decomposition); the population-level alternative (named, deferred); the supervisory dissolution (you don't need I labels; you need disagreement metrics, which are observable from set output).

- [ ] **Step 4: Self-review**

Acceptance criteria check. Specifically check: does the reframing contradict anything in the indeterminacy memo, or extend it cleanly? If it contradicts, name the contradiction and resolve it (the memo predates the dual-set framing).

- [ ] **Step 5: Commit**

```bash
git add docs/superpowers/specs/2026-05-10-mechanism-specification.md
git commit -m "spec: section 4 — I as inter-set disagreement"
```

---

## Task 5: Section 5 — Retrospective trajectory species, operational definition

**Files:**
- Modify: `docs/superpowers/specs/2026-05-10-mechanism-specification.md` (append Section 5)

- [ ] **Step 1: State acceptance criterion**

Section 5 is done when (a) the retrospective trajectory species is operationally specified, sharpening §4 of the indeterminacy memo (which sketches it but defers spec-level detail); (b) the species' role *within the dual-set framing* is named — it's the mechanism by which post-origination outcomes feed back into either R_T or R_F or both; (c) the LC-evaluation proxy and production version are both specified at the contract level (per indeterminacy memo §4); (d) the statistical test specifics (open decision #5) are at least partially resolved — what's the comparison, what's the test, what's the threshold, what's the null.

- [ ] **Step 2: Re-read indeterminacy memo section 4 (Retrospective-trajectory)**

The memo sketches the surprise-model approach. The spec must specify it at a level the prototype can implement.

- [ ] **Step 3: Draft Section 5**

Cover: motivation (retrospective trajectory is load-bearing per indeterminacy memo §3 and adversarial-robustness memo); surprise model definition (origination_features → outcome_surprise); how surprise propagates into R_T or R_F (a model that systematically under-weighted a signal correlated with later surprise loses membership in R(ε) on the revised loss function; the spec specifies this as the mechanism for set membership shifting under retrospective evidence); the statistical test (recommended default: model accuracy on holdout vs. surprise-corrected accuracy, with significance threshold; alternative tests named).

- [ ] **Step 4: Self-review**

Acceptance criteria check. Specifically: is the operational definition concrete enough that the prototype team could implement it without further clarification? If not, sharpen.

- [ ] **Step 5: Commit**

```bash
git add docs/superpowers/specs/2026-05-10-mechanism-specification.md
git commit -m "spec: section 5 — retrospective trajectory operationalization"
```

---

## Task 6: Section 6 — Category 1 vs Category 2 detection criteria

**Files:**
- Modify: `docs/superpowers/specs/2026-05-10-mechanism-specification.md` (append Section 6)

- [ ] **Step 1: State acceptance criterion**

Section 6 is done when (a) the conceptual distinction is restated cleanly: Cat 1 = inherent lending risk (conditions changed unpredictably; no model would have caught it); Cat 2 = informational under-weighting (some R(ε) members did weight the signal correctly; the chosen model didn't); (b) the formal detection criterion (open decision #6) is specified — recommended default: a case is Cat 2 if, among R(ε) members at decision time, those that correctly predicted the outcome share a structural feature (specific feature-weighting pattern) that the chosen model lacks; otherwise Cat 1; (c) the section names the boundary case explicitly: Cat 1 / Cat 2 is not always retrospectively decidable, and the spec specifies how to handle ambiguous cases (recommended: report both Cat 1 and Cat 2 likelihoods with confidence, do not force a binary); (d) the section explicitly notes the SHAP+ensemble limit: SHAP applied to an ensemble can approximate prediction-side trajectory but cannot detect *governance-relevant* Cat 2 because the set definition isn't policy-derived (citation: shap-vs-rashomon-result-note plus the May 10 conversation residue).

- [ ] **Step 2: Draft Section 6**

Cover: definitions (Cat 1, Cat 2, ambiguous); formal detection criterion using R(ε) member-by-member analysis on the retrospective trajectory output; ambiguous case handling; SHAP comparative limit; what Cat 2 detection *requires* — that R(ε) include members weighting the under-weighted signal (if policy excludes those weightings, Cat 2 detection fails by construction, which is itself a governance-visible property of the policy).

- [ ] **Step 3: Self-review**

Acceptance criteria check. Specifically: does the formal criterion match the conceptual distinction? Are there cases the criterion mis-classifies? Are those mis-classifications named?

- [ ] **Step 4: Commit**

```bash
git add docs/superpowers/specs/2026-05-10-mechanism-specification.md
git commit -m "spec: section 6 — Category 1 vs Category 2 detection"
```

---

## Task 7: Section 7 — Prototype validation targets for May 23

**Files:**
- Modify: `docs/superpowers/specs/2026-05-10-mechanism-specification.md` (append Section 7)

- [ ] **Step 1: State acceptance criterion**

Section 7 is done when (a) the spec names what evidence the prototype must produce to validate this specification by May 23; (b) prior evidence already in hand is acknowledged (SHAP non-inferiority falsification from 2026-05-09 is one validation target already met); (c) new validation targets are listed concretely — at minimum, one demonstration of dual-set construction producing nontrivial R_T ≠ R_F disagreement, and one demonstration of Cat 2 detection on a vintage with sufficient retrospective data; (d) explicit scope boundaries (open decision #7) — what's *out* of the May 23 deliverable so the prototype team can plan against bounded scope.

- [ ] **Step 2: Draft Section 7**

Cover: what's already validated (SHAP non-inferiority); what's new for May 23 (dual-set demonstration, Cat 2 detection on at least one vintage, integration story showing the spec's mechanism applied end-to-end on a real LendingClub vintage with outcomes); explicit out-of-scope items (regulator-doc translation is downstream, Paper 2 is downstream, HMDA cross-validation is post-May-23, multi-policy M&A sweep is post-prototype).

- [ ] **Step 3: Self-review**

Acceptance criteria check. The targets must be (a) achievable in the time remaining, (b) falsifiable, (c) directly validating something the spec claims.

- [ ] **Step 4: Commit**

```bash
git add docs/superpowers/specs/2026-05-10-mechanism-specification.md
git commit -m "spec: section 7 — May 23 prototype validation targets"
```

---

## Task 8: Section 8 — Open decisions register

**Files:**
- Modify: `docs/superpowers/specs/2026-05-10-mechanism-specification.md` (append Section 8)

- [ ] **Step 1: State acceptance criterion**

Section 8 is done when (a) all open decisions from this plan are listed with their current resolution state (resolved, deferred with default, deferred without default); (b) for resolved ones, the section names where in the spec the resolution lives; (c) for deferred ones, the section names the default (if any), the considerations that would drive a different choice, and the conditions under which the decision should be re-opened; (d) the section is structured so that future revisions can append new open decisions without re-numbering existing ones.

- [ ] **Step 2: Draft Section 8**

For each of the 8 open decisions in this plan's preamble, write a paragraph stating: current resolution, location in spec, considerations, re-open conditions. Use stable numeric IDs (OD-1 through OD-8) so future references stay valid.

- [ ] **Step 3: Self-review**

Walk through Sections 2–7 of the spec; for each open decision, check that the resolution stated in Section 8 matches the resolution actually used in the cited section. Inconsistency here is a load-bearing failure.

- [ ] **Step 4: Commit**

```bash
git add docs/superpowers/specs/2026-05-10-mechanism-specification.md
git commit -m "spec: section 8 — open decisions register"
```

---

## Task 9: Section 9 — Cross-reference index

**Files:**
- Modify: `docs/superpowers/specs/2026-05-10-mechanism-specification.md` (append Section 9)

- [ ] **Step 1: State acceptance criterion**

Section 9 is done when (a) every prior memo cited in the spec is listed with what it contributes and which sections of the spec depend on it; (b) reverse direction is also captured — for each section of the spec, the prior memos it relies on are listed; (c) the index is structured so that updating one memo (or adding a new one) doesn't require restructuring the section.

- [ ] **Step 2: Draft Section 9**

Two tables: (a) memo → sections that cite it, (b) section → memos cited. Cover all eight lineage memos from this plan's preamble plus any others surfaced during spec writing.

- [ ] **Step 3: Self-review**

Verify each citation by checking the spec sections actually do cite the named memo. Missing citations or stale ones are caught here.

- [ ] **Step 4: Commit**

```bash
git add docs/superpowers/specs/2026-05-10-mechanism-specification.md
git commit -m "spec: section 9 — cross-reference index"
```

---

## Task 10: Full spec self-review and stabilization commit

**Files:**
- Modify: `docs/superpowers/specs/2026-05-10-mechanism-specification.md` (final review pass)

- [ ] **Step 1: State acceptance criterion**

The spec is V1-stable when (a) every section's acceptance criterion (Tasks 1–9) is met; (b) the spec's claims are internally consistent across sections (no contradiction between Section 3's dual-set construction and Section 6's Cat 2 detection criterion, for instance); (c) terminology used across sections is consistent (R_T, R_F, ε_T, ε_F, I, Cat 1, Cat 2, retrospective trajectory species, surprise model — these terms have one definition each, used consistently throughout); (d) the spec is citable by the wedge extension plan, the regulator-doc translation, and the Paper 2 architecture sections without further clarification; (e) total length is checked against the 500-line file-size rule; if exceeded, splitting plan is added as Task 11.

- [ ] **Step 2: Full read-through with terminology check**

Read the spec start-to-finish. Maintain a glossary of terms as you go. After reading, check that each term has exactly one definition. Variants ("R_T(ε_T)" vs "R_T" vs "the grant-supportive set" — all referring to the same thing — are fine as long as the first introduction binds them.

- [ ] **Step 3: Spec coverage check against this plan**

For each open decision in this plan's preamble, find where in the spec it is addressed. Any unaddressed open decisions are bugs in the spec.

- [ ] **Step 4: Stabilization commit**

```bash
git add docs/superpowers/specs/2026-05-10-mechanism-specification.md
git commit -m "spec: V1 stabilization — full self-review pass"
```

- [ ] **Step 5: Mark the spec as the canonical source**

Add a one-line entry to `docs/superpowers/specs/` if there's an index file (check first), or update the README of that directory if one exists, noting that the 2026-05-10 mechanism specification is the canonical source for the dual-set construction. If no index/README exists, no action needed — the spec stands on its own and is discoverable by date.

```bash
git add -u
git commit -m "spec: mark mechanism specification as canonical" --allow-empty
```

(The `--allow-empty` is for the case where Step 5 has nothing to commit; the commit then documents that the V1 stabilization is the canonical version.)

---

## Self-Review of This Plan

**1. Spec coverage.** Every open decision in the preamble has at least one task addressing it. Every section of the planned spec has a task creating it. The two new contributions named in the architecture preamble (dual-set construction; Cat 1/Cat 2 formalization) have dedicated tasks (3 and 6).

**2. Placeholder scan.** No TBDs, no "implement later," no "similar to Task N." Each task has its own acceptance criterion, its own draft prose direction, and its own self-review instructions.

**3. Type consistency.** Terminology used throughout this plan: R_T, R_F, ε_T, ε_F, I, R(ε), Cat 1, Cat 2, retrospective trajectory species, surprise model. These appear with consistent meaning across tasks.

**4. Scope.** This plan produces the specification. It does not produce prototype extension, regulator-doc translation, or Paper 2 sections. Those are downstream plans that depend on this spec stabilizing.

**5. The path-change provision.** Task 10 stabilizes V1; revisions thereafter land as appended changelog entries, not as a fork. The plan's preamble names "revision provisions" explicitly. Prototype findings or regulator-doc translation friction trigger revision; the spec is the integrator, not a frozen contract.

---

## Execution

This plan is for a written-document artifact, not code. The standard subagent-driven-development / executing-plans execution patterns are over-engineered for prose drafting; the author (this conversation's lead) has the context and should draft inline with self-review at each task boundary. A subagent dispatch would lose the conversation context that grounds the spec.

**Recommended execution:** inline, task-by-task, with explicit user review point at the end of Task 3 (after the dual-set construction is drafted, since that's the load-bearing new contribution and is the most likely place a divergence from user intent would surface).
