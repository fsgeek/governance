# Mechanism Specification — Policy-Constrained Dual-Set Rashomon Construction

**Date:** 2026-05-10 (drafting started; sections may carry later dates).
**Status:** V1 draft. Intended as the canonical architectural source for the May 23 Olorin deliverable, for Paper 2 (architecture), and for translation into the regulator-facing document. This document is *consolidation plus two extensions*; the consolidation references existing memos rather than restating them, and the two extensions (dual-set construction; Category 1 vs Category 2 formalization) emerged from the 2026-05-10 working conversation and are introduced here for the first time.
**Authoritative for:** the dual-set R_T(ε_T) / R_F(ε_F) policy-constrained construction; the inter-set framing of indeterminacy I; the Category 1 vs Category 2 retrospective failure detection criterion; the prototype validation targets bounding the May 23 deliverable.
**Defers to prior memos for:** the four-species I-vector content (`2026-05-08-indeterminacy-operationalization-memo.md`); the cliff signal mechanics and constraint-saturation reading (`2026-05-09-cliff-and-constraint-saturation-synthesis.md`); the T/F mechanical relationship within a single model (`2026-05-09-tf-mechanics-and-case-level-empty-support.md`); the SHAP non-inferiority falsification result (`2026-05-09-shap-vs-rashomon-result-note.md`); the (A)–(E) slice map and current status (`2026-05-09-methodology-decomposition-retrospective.md`); the adversarial-robustness argument for retrospective-trajectory (`2026-05-08-adversarial-robustness-and-examinability-memo.md`).
**Plan:** `docs/superpowers/plans/2026-05-10-mechanism-specification.md`.

---

## 0. Table of contents

1. Scope, status, lineage *(this section)*
2. Policy representation
3. Set construction — dual R_T(ε_T) and R_F(ε_F)
4. Indeterminacy I as inter-set disagreement
5. Retrospective trajectory species — operational definition
6. Category 1 vs Category 2 detection criteria
7. Prototype validation targets for May 23
8. Open decisions register
9. Cross-reference index

Sections after this one are appended as Tasks 2–10 of the plan are executed. The TOC is presented in full at scaffolding time so readers see the intended shape before later sections exist.

---

## 1. Scope, status, lineage

### 1.1 What this document specifies

This specification consolidates the architectural decisions distributed across the project's 2026-05-07 through 2026-05-10 working memos into a single canonical source, and extends them with two contributions developed in the 2026-05-10 working conversation:

1. **Dual-set construction.** The mechanism specified here builds two policy-constrained Rashomon sets — R_T(ε_T) of grant-supportive ε_T-optimal models and R_F(ε_F) of deny-supportive ε_F-optimal models — rather than a single combined set. Indeterminacy I is then operationalized as disagreement *between* the two sets, not as a residual of T and F within a single set. This resolves the F = 1 − T flatness problem identified in `2026-05-09-tf-mechanics-and-case-level-empty-support.md` §2 and recovers the operationally meaningful distinction between "hard but coherent" and "hard and atypical" that the wedge's current probabilistic implementation collapses (per `2026-05-09-cliff-and-constraint-saturation-synthesis.md` §7).

2. **Category 1 vs Category 2 retrospective failure formalization.** The conceptual distinction between inherent lending risk (Category 1: conditions changed unpredictably; no model would have caught it) and informational under-weighting (Category 2: factors that emerge from retrospective analysis of the entire dataset, not just the decision explanation, that could have reduced bank risk) is formalized with a detection criterion grounded in R(ε) member-by-member analysis on the retrospective trajectory output. The dataset-level vs decision-level cut is the load-bearing line.

Section 2 specifies the policy representation contract that the set construction depends on. Section 3 specifies the dual-set construction. Section 4 specifies I as inter-set disagreement and reframes the four-species I-vector as generators of disagreement within and between the sets. Section 5 sharpens the retrospective-trajectory species' operational definition. Section 6 formalizes Cat 1 / Cat 2 detection. Section 7 names the prototype validation targets for the May 23 deliverable. Section 8 registers the open decisions deferred at V1, and Section 9 indexes the cross-references.

### 1.2 What this document does *not* specify

- **Prototype extension.** The current wedge (`wedge/`) implements V₁ measurement with degenerate T+F=1, three vintages run, four species of I prototyped at the *case* level (per the indeterminacy memo §4 / the conversation-residue capture's §4). Extending the wedge to (a) the dual-set construction, (b) per-model I emission, and (c) Cat 2 detection is a downstream implementation plan that depends on this spec stabilizing. The prototype is the validator of this spec; this spec is not the prototype.

- **The position paper (Paper 1) or the architecture paper (Paper 2).** This spec is the architectural spine that Paper 2 draws on. Paper 1 (in progress; drafts at repo root `paper.tex`, `position-*.md`) writes against the empirical findings — cliff, regime rotation, SHAP non-inferiority — using this spec's vocabulary but does not depend on the spec being complete to make its positional argument. Paper 2 specifically *is* the prose narrative of this spec's architecture and is downstream.

- **The regulator-facing document.** Translation of this spec into examination-procedure language is a downstream artifact for the May 23 Olorin deliverable. Operational fuzziness surfaced during translation is feedback into spec revision; the regulator document is not contained here.

- **The codification representation itself.** Section 2 specifies the *contract* set construction expects from policy — input shape, output shape, invariants — but does not specify how the codification layer extracts policy from source materials. The `policy/` directory (encoder.py, synthetic.py, thin_demo_hmda.yaml) is the working scaffolding for that layer; this spec specifies what set construction needs from it, not how the layer produces it. Codification representation richer than the current encoder's output is on the open-decisions register (OD-1) as deferred.

- **The four-species I content.** The species themselves — local-density, multivariate-coherence, Ioannidis-suspicion, retrospective-trajectory — are specified in `2026-05-08-indeterminacy-operationalization-memo.md` §3–§4. Section 4 of this spec reframes them as *generators of disagreement* under the dual-set construction; it does not redefine them. The indeterminacy memo remains authoritative for species content.

### 1.3 Relationship to existing memos

The lineage memos divide into two groups by how this spec uses them.

**Inherited as-is** (this spec cites; the memo remains authoritative for its content):
- `2026-05-07-rashomon-prototype-wedge-design.md` — wedge design, V₁ measurement methodology, (A)–(E) labels for what's deferred.
- `2026-05-08-indeterminacy-operationalization-memo.md` — four-species I-vector content, computational definitions in CART/LC terms, pre-registered I-behaviors.
- `2026-05-08-adversarial-robustness-and-examinability-memo.md` — the adversarial-robustness property of retrospective-trajectory (cannot be gamed without producing the evidence it is designed to detect). This property underwrites the standard-of-care argument in Section 6 and is not restated; the memo remains authoritative.
- `2026-05-09-tf-mechanics-and-case-level-empty-support.md` — F = 1 − T mechanical relationship within a single model; case-level empty-support finding.
- `2026-05-09-tf-asymmetry-exploration-note.md` — empty-support inversion at pair level (superseded at case level by the cliff synthesis, preserved here as provenance).
- `2026-05-09-shap-vs-rashomon-result-note.md` — SHAP non-inferiority falsification (Jaccard 0.000–0.008, charge-off 0.292 vs base 0.148, U-shaped regime signature). See §7.1 caveat: the instability-anti-correlation observation deserves a sub-finding revision; until that revision lands, this spec cites the result note as the empirical falsification arm and treats the instability observation as a separately-named structural distinction (instability falls 26→15% while Rashomon-silence rises 0.11→0.58%; the two metrics are *anti-correlated* under regime shift in a diagnostically informative way).
- `2026-05-09-cliff-and-constraint-saturation-synthesis.md` — cliff structure as a set-level signal, three-signal decomposition, constraint-saturation mechanism. Section 3's structural-distinctiveness argument is the source of this spec's defense of dual-set construction over single-model attribution methods.
- `2026-05-09-methodology-decomposition-retrospective.md` — (A)–(E) slice map and status; the wedge's current implementation status is inherited from §3 of that memo.
- `2026-05-09-conversation-residue-capture.md` — three captured items (path-dependent harness-load theory, Sonnet inter-rater limitation, I-stability experiment as pending test). The I-stability item is referenced in Section 4 as a pending validation target.

**Extended** (this spec adds to or reframes the memo's content):
- The indeterminacy memo's four-species I-vector is *reframed* in Section 4 as generators of inter-set disagreement under dual-set construction. The species content is unchanged; what changes is the wrapper.
- The cliff synthesis's §3 structural-distinctiveness argument is *generalized* in Section 3 from "R(ε)" (single set) to "R_T(ε_T) and R_F(ε_F)" (dual set). The argument's logical shape is preserved; the construction it defends becomes dual.
- The adversarial-robustness memo's retrospective-trajectory argument is *operationalized* in Section 5 and *applied* in Section 6 to underwrite the Cat 2 detection criterion's credibility.

### 1.4 Relationship to the wedge prototype

The wedge (`wedge/`) is the V₁ measurement instantiation of an earlier, single-set version of the methodology. It has produced the empirical anchors this spec consolidates: cliff structure across three vintages, regime rotation, charge-off elevation on T-silent-all cases, SHAP non-inferiority falsification. Those findings are load-bearing for Paper 1 and for the May 23 deliverable.

This spec extends the methodology in two ways the wedge does not currently implement:
1. **Dual-set construction** (Section 3) — the wedge builds one R(ε); this spec specifies two.
2. **Per-model I emission for the I-stability test** — flagged in the conversation residue capture's §4 as the most informative untested experiment. Required for operationalizing I as inter-set disagreement at the per-instance level (Section 4 OD-4).

The wedge extension that implements this spec is a downstream plan. The May 23 prototype validation targets (Section 7) bound what extension is required for the deliverable and explicitly defer what is not.

### 1.5 Versioning and revision provisions

This is V1. The plan that produced it (`docs/superpowers/plans/2026-05-10-mechanism-specification.md`) anticipates revision as prototype findings surface gaps and regulator-document translation reveals operational fuzziness. Revisions land as dated changelog entries appended to this file. The spec is not forked into V2 unless the consolidation argument itself requires restructuring.

Each section names its own acceptance criterion in the plan; failure to meet a criterion in a later read-through is a bug in the spec, not a feature of revision. Open decisions named in Section 8 are *deferred*, not unspecified — the deferral itself is a specification act, with default and rationale recorded.

---

## 2. Policy representation

### 2.1 The contract

Set construction (Section 3) consumes the *output* of policy encoding, not policy source materials. The contract this spec commits to for V1 is the shape produced by `policy/encoder.py`'s `load_policy()` — a typed `PolicyConstraints` object carrying:

- **`monotonicity_map`**: `feature_name → {-1, +1}` per the sklearn `monotonic_cst` convention. Sign is interpreted relative to `classes_[1]` (the positive class). For binary `{0=deny, 1=grant}` encoding, `+1` means "feature ↑ ⇒ P(grant) does not decrease."
- **`mandatory_features`**: features every admissible model must split on. A model whose factor support omits a mandatory feature is excluded from R(ε).
- **`prohibited_features`**: features no admissible model may split on. A model whose factor support includes a prohibited feature is excluded from R(ε).
- **`applicable_regime`**: a mapping of feature-or-context conditions identifying the cases the policy graph scopes. Out-of-regime cases route to manual review and are not scored by R(ε) (Section 3 specifies how this routing affects set construction).
- **Provenance fields** (`name`, `version`, `status`): not interpreted by set construction; logged for audit trail.

`policy/thin_demo_hmda.yaml` is the canonical demonstration source for what produces this output. The YAML is the audit artifact — the same artifact a regulator reads is the artifact that constrains the model class. That co-identification is the methodology's transparency property at the policy layer, not a deployment detail.

The `PolicyConstraints` API surface set construction depends on:
- `monotonic_cst(features: list[str]) → list[int]` — returns the sklearn-compatible monotonicity array aligned to a supplied feature ordering. Raises `PolicyValidationError` if a constrained feature is absent from the list (silent dropping would unenforce the constraint).
- `is_feature_subset_admissible(subset: tuple[str, ...]) → bool` — the gate the Rashomon hyperparameter sweep uses to skip inadmissible subsets before fitting.

Monotonicity is enforced at fit time via sklearn; mandatory/prohibited are enforced as a pre-fit admissibility gate. These two enforcement modes are not interchangeable — see §2.4.

### 2.2 Decision-space shape: three-way, not binary

Policy decisions are **three-way**: `{grant, human_review, deny}`. The thin demo's decision graph routes cases to `manual_review` whenever a non-pass-non-deny gate is hit (e.g., DTI 43–compensating-factor band, employment tenure < 2 years with potential offset documentation), and these cases are deliberately *not scored* by R(ε). The model class operates on the grant/deny binary; manual-review routing is upstream of the model.

This matters for the dual-set construction (Section 3) because R_T and R_F are sets of *binary* classifiers — they assign T-support or F-support to the grant/deny axis. Manual-review cases are out-of-scope for both R_T and R_F by policy construction, not by model failure. The empty-class cliff signal (per `2026-05-09-cliff-and-constraint-saturation-synthesis.md`) is therefore a property of *scored* cases; cases routed to manual review are categorically absent from both sets and are reported separately in the policy-node trace.

The dual-set inter-set disagreement metric (Section 4) is defined on scored cases only. Manual-review routing is itself a governance signal — *which* cases the policy graph cannot adjudicate — but it is a signal of the policy graph, not of the Rashomon construction. The two signals are reported separately.

### 2.3 The five constraint classes — V1 support status

The `policy/README.md` enumerates five constraint classes; V1 set construction supports the first three plus a partial implementation of the fifth:

| Constraint class | V1 status | Source |
|---|---|---|
| 1. Monotonicity | **Supported.** sklearn `monotonic_cst` at fit time. | `PolicyConstraints.monotonicity_map` |
| 2. Mandatory-feature | **Supported.** Pre-fit admissibility gate. | `PolicyConstraints.mandatory_features` |
| 3. Prohibited-feature | **Supported.** Pre-fit admissibility gate. | `PolicyConstraints.prohibited_features` |
| 4. Predicate (decision-region structure) | **Deferred.** Decision graph nodes parsed for routing only; not used to constrain model decision-region shape. See OD-1. | YAML `nodes:` block |
| 5. Routing (manual_review escape) | **Partial.** Applicable-regime routing supported via `applicable_regime`. Per-node `on_fail: manual_review` routing depends on a decision-graph executor not yet wired into set construction. | YAML `applicable_regime`, `nodes:` `on_fail:` edges |

Classes 4 and 5's deferred portions are on the open-decisions register (OD-1) as "richer codification representation." The May 23 deliverable validates Sections 3–6 against the V1-supported subset; deferred classes are flagged in Section 7 as not-in-scope for the deliverable and not required to validate the dual-set construction's core claim.

### 2.4 Hard vs soft constraints

V1 commits to **hard constraints only**. A model is either in R_T(ε_T) / R_F(ε_F) or it is not; there is no "preferred but allowed" mode. This is consistent with the current encoder (which validates and returns a typed object without weight parameters) and with the audit-artifact framing (a YAML constraint a regulator reads should mean *constraint*, not *preference*).

Soft constraints — penalize-but-allow — are conceptually coherent and would correspond to ε_T / ε_F regions extending into mildly-non-compliant model space with a penalty term in the loss. They are deferred to a future revision and are explicitly out-of-scope for V1. The spec does not preclude them; it simply does not commit to them, because:
1. The audit-artifact framing breaks down under soft constraints (does a regulator read a soft constraint as "the bank's policy" or "the bank's preference"? The ambiguity is governance-fraught.).
2. The dual-set construction's structural-distinctiveness argument (Section 3) is cleanest under hard constraints; under soft constraints the set-level cliff signal smears into a gradient.
3. The current encoder has no soft-constraint syntax. Adding it is non-trivial and out of scope for the May 23 deliverable.

### 2.5 What this spec does *not* require of policy representation

- **Natural-language parsing.** The codification layer that produces `PolicyConstraints` from source materials (policy memos, underwriting manuals, regulatory text) is out of scope. V1 assumes a hand-curated YAML in the schema demonstrated by `thin_demo_hmda.yaml`. NL extraction and richer policy-document ingestion are codification-layer work, downstream of this spec.
- **Cross-policy coherence checks.** A YAML may declare constraints that conflict with regulatory baseline (e.g., a monotonicity direction inconsistent with ECOA); this spec does not require the encoder to detect such conflicts. Future work.
- **Versioning and policy drift tracking.** The `version` field is logged but the spec does not specify how policy revisions interact with previously-built R(ε). A bank that revises policy mid-vintage has a governance question this spec does not answer; flagging it as future work.
- **Multi-policy comparison.** The M&A scenario use case sweeps multiple candidate combined policies. V1 supports one policy per construction; multi-policy sweep is a downstream capability that uses this spec as substrate but is not part of the May 23 deliverable.

### 2.6 Open decision OD-1: codification richness

The V1 contract commits to the current `policy/encoder.py` output shape. Three richer alternatives are deferred and named here so a future revision has a starting frame:

- **Hybrid NL + structured.** A policy document with structured constraint blocks (current YAML) plus natural-language commentary that the codification layer extracts additional constraints from. Default position: defer; richer policy expressivity is a codification-layer problem, not a set-construction problem.
- **Decision-graph predicate enforcement.** Class 4 above — use the YAML's `nodes:` block to constrain not just admissibility but the decision-region structure each model in R(ε) can express. Default position: defer until V1 validation reveals whether this changes the cliff signal or the inter-set disagreement metric materially.
- **Soft constraints.** §2.4. Default position: defer indefinitely unless governance demand surfaces.

Each is an "open" decision in the sense of Section 8's register (OD-1 captures all three sub-decisions). The deferral is itself a specification act: V1 does *not* support them, and the spec records this as an explicit choice with rationale.
