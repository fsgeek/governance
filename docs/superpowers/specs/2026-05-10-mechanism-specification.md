# Mechanism Specification — Policy-Constrained Dual-Set Rashomon Construction

**Date:** 2026-05-10 (drafting started; sections may carry later dates).
**Status:** V1 in draft. Intended as the canonical architectural source for the May 23 Olorin deliverable, for Paper 2 (architecture), and for translation into the regulator-facing document. This document is *consolidation plus two extensions*; the consolidation references existing memos rather than restating them, and the two extensions (dual-set construction; Category 1 vs Category 2 formalization) emerged from the 2026-05-10 working conversation and are introduced here for the first time.
**Section status at time of writing:** Sections 1–3 landed (scope/lineage; policy representation; dual-set construction). Sections 4–9 pending per `docs/superpowers/plans/2026-05-10-mechanism-specification.md`.
**Will be authoritative for (upon V1 stabilization):** the dual-set R_T(ε_T) / R_F(ε_F) policy-constrained construction (§3, landed); the inter-set framing of indeterminacy I (§4, pending); the Category 1 vs Category 2 retrospective failure detection criterion (§6, pending); the prototype validation targets bounding the May 23 deliverable (§7, pending). Until Sections 4–9 land, claims here that depend on them are *intended* commitments, not current ones.
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
2. **Per-model I emission for inter-set disagreement under the dual-set construction.** The wedge already emits per-model I for the local_density species (visible in the existing jsonl schema; this corrects the conversation-residue capture's §4 which understated existing capability). The I-stability prediction that motivated per-model emission was tested against single-R(ε) data on 2026-05-09 and *falsified decisively* — I CV is 7–9× T CV across all three vintages (`2026-05-09-i-stability-falsification-findings-note.md`). What remains untested is per-model I emission for the *other three species* (multivariate-coherence, Ioannidis-suspicion, retrospective-trajectory) and per-model I behavior under the dual-set R_T / R_F construction this spec specifies. The local_density falsification under single-R(ε) does not transfer mechanically to the dual-set case; it does invalidate the original contrarian prediction in its single-R(ε) form, and Section 4 OD-4 names the dual-set per-instance operationalization as the still-open question.

The wedge extension that implements this spec is a downstream plan. The May 23 prototype validation targets (Section 7) bound what extension is required for the deliverable and explicitly defer what is not.

### 1.5 Versioning and revision provisions

This is V1. The plan that produced it (`docs/superpowers/plans/2026-05-10-mechanism-specification.md`) anticipates revision as prototype findings surface gaps and regulator-document translation reveals operational fuzziness. Revisions land as dated changelog entries appended to this file. The spec is not forked into V2 unless the consolidation argument itself requires restructuring.

Each section names its own acceptance criterion in the plan; failure to meet a criterion in a later read-through is a bug in the spec, not a feature of revision. Open decisions named in Section 8 are *deferred*, not unspecified — the deferral itself is a specification act, with default and rationale recorded.

---

## 2. Policy representation

### 2.1 The contract

Set construction (Section 3) consumes the *output* of policy encoding, not policy source materials. The contract this spec commits to for V1 is the shape produced by `policy/encoder.py`'s `load_policy()` — a typed `PolicyConstraints` object carrying:

- **`monotonicity_map`**: `feature_name → {-1, +1}` per the sklearn `monotonic_cst` convention. Sign is interpreted relative to `classes_[1]` (the positive class). The `policy/encoder.py` module docstring assumes positive class = grant; the YAML's `direction` field is stated relative to *grant probability* (`direction: positive` = "feature ↑ never decreases P(grant)"). **Caveat: the wedge's current collectors do not match this convention.** `wedge/collectors/lendingclub.py` emits `label=1 ⇔ charged_off` (charged-off as positive class) and `wedge/collectors/hmda.py` emits `label=1 ⇔ denied` (denial as positive class) — both deliberately encoding the *adverse* outcome as positive, consistent with the wedge's fair-lending-review framing. The encoder explicitly warns the caller about this in its module docstring at `policy/encoder.py:43`. See §2.7 (OD-9) for the sign-flip adapter requirement this creates and the deferral rationale.
- **`mandatory_features`**: features every admissible model's *candidate feature subset* must contain. The encoder API (`is_feature_subset_admissible`) checks subset membership at the pre-fit admissibility gate; it does *not* enforce that the fitted model actually splits on the feature. A feature in the subset can be unused by the fitted tree if no split on it reduces the loss enough to be selected. The V1 contract is therefore "must be available to the model," not "must be split on." A stronger guarantee (post-fit split-use verification) would require an additional check that V1 does not specify; flagged in §2.7 (OD-9) for future-revision consideration.
- **`prohibited_features`**: features no admissible model's candidate subset may contain. Same pre-fit gate; a feature absent from the subset cannot be split on, so prohibition *is* enforced by the pre-fit check (the asymmetry with mandatory is real — prohibition by exclusion is air-tight, mandate by inclusion is not).
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

### 2.7 Open decision OD-9: label-polarity convention and mandatory-feature enforcement gap

Two distinct issues surfaced during V1 spec review that are recorded here rather than silently coerced.

**OD-9a: Label-polarity convention conflict.** `policy/encoder.py` assumes positive class = grant (YAML `direction` is stated relative to grant probability). `wedge/collectors/lendingclub.py` and `wedge/collectors/hmda.py` emit positive class = adverse outcome (charged_off / denied). The encoder's module docstring warns the caller about this; in current code there is no automatic adapter, so a naive composition would apply monotonicity signs inverted from their intended meaning.

Three resolution paths exist; V1 commits to the first and records the alternatives:

1. **(V1 default) Sign-flip adapter at the policy-to-construction boundary.** Set construction takes a `PolicyConstraints` instance plus an explicit `positive_class_is_grant: bool` parameter; when `False` (the current collector convention), `monotonic_cst()` output is negated before being passed to sklearn. Rationale: smallest change; no code edits required to existing collectors or encoder; the adapter point is the place the convention conflict becomes visible at fit time. Implementation debt: every set-construction call site must remember to pass the parameter correctly.
2. **Standardize collectors to grant-as-positive.** Edit `derive_label` in both collectors to emit `label=1 ⇔ grant`. Rationale: removes the conflict permanently; aligns the wedge with the encoder's documented assumption. Cost: invalidates the wedge's existing charge-off / deny-side framing, which is the basis for the cliff signal's interpretation (T-silent-all means "no member articulates grant-supportive evidence"; under the flip it would mean "no member articulates adverse-outcome evidence"). The published findings would need re-interpretation. Recorded as the cleanest long-term path that is not free.
3. **Invert the encoder's sklearn mapping.** Make `direction: positive` in YAML map to sklearn `-1` (consistent with adverse-as-positive in `classes_[1]`). Cost: contradicts the encoder's own module docstring, requires updating every YAML rationale, and the YAML's `direction: positive` becomes counterintuitive (reads as "positive direction toward adverse outcome"). Recorded as available but unattractive.

The V1 default (adapter at the construction boundary) is the lightest move and the easiest to reverse if the bank-side deployment surfaces a preference for one of the alternatives. The choice is explicitly named so future revisions don't silently drift.

**OD-9b: Mandatory-feature enforcement gap.** The current encoder API checks that mandatory features are present in a model's candidate feature subset before fitting; it does not enforce that the fitted model actually splits on them. A feature that's available but unused passes the admissibility gate and ends up in R(ε) without ever appearing in the factor-support trace. For the dual-set construction (Section 3) and inter-set disagreement (Section 4) this is mostly benign — the model is still policy-admissible in the sense the encoder declares, and factor-support attribution will just show the feature is unused — but for a regulator who reads "mandatory feature" as "this feature was considered in the decision," the gap matters.

Two resolution paths:

1. **(V1 default) Weaken the claim.** The spec says "must be available to the model," not "must be split on." Documentation in the regulator-facing document needs to match — mandatory means "the model could have used it," not "the model did use it." This is what the encoder actually enforces; the spec stays honest.
2. **Add a post-fit split-use check.** Set construction inspects each fitted tree's used-feature set; models that fail to split on a mandatory feature are excluded from R(ε) at a second admissibility pass. Cost: requires a new check the encoder does not currently provide; downstream implication is that R(ε) may be empty more often (the second gate is strictly tighter). Recorded as architecturally sound but deferred to V2 pending governance review of whether the strong guarantee is wanted.

The V1 default is the weaker guarantee that matches the current API. The regulator-facing document translation (downstream artifact) must reflect this weaker reading and not over-claim.

Both OD-9a and OD-9b are *implementation debt* — places where the spec is honest about a gap between intent and current code. Future revisions resolve them with a code change plus a spec update; V1 names them so the gap is auditable.

---

## 3. Set construction — dual R_T(ε_T) and R_F(ε_F)

### 3.1 Motivation

The wedge's V₁ implementation constructs a single R(ε) of CART models, each emitting T-support and F-support attribution by walking the decision path per case. T and F within a single model are mechanically related: per `2026-05-09-tf-mechanics-and-case-level-empty-support.md` §2, the per-case F = 1 − T identity holds by construction in the wedge's current emission. This is the *F = 1 − T flatness* problem.

The flatness is operationally lossy in two ways:

1. **Conflicting-evidence cases are not representable.** A borrower with strong grant-supportive history *and* strong deny-supportive recent debt-load deterioration has high evidential support on both sides. Under F = 1 − T, the model emits T ∈ [0, 1] and F = 1 − T mechanically; "high T and high F simultaneously" cannot occur. The model's output collapses the two-axis evidential structure onto one axis. This is operationally distinct from the *thin-evidence* case (low T, low F) — the operational distinction is whether the case is *contested* or *uncertain*, and the wedge cannot tell them apart.

2. **The hard-but-coherent vs hard-and-atypical distinction is collapsed within the cliff.** Per `2026-05-09-cliff-and-constraint-saturation-synthesis.md` §7, the V₂ cliff cohort's low-I half (FICO 660 cluster, charge-off 2× population) is *hard but coherent* — constraint-saturated at the policy boundary, internally similar, baseline I-mean. The high-I half is *hard and atypical* — anomalies on top of FICO floor. Probabilistic semantics with F = 1 − T marks both as equivalently silent on T-side attribution; the operationally pivotal distinction is invisible.

The dual-set construction resolves both losses by operationalizing T and F as outputs of *different models trained under different cost regimes*, not as residuals of a single model.

**Sharpening from 2026-05-11 cross-instance review (queued for V1.1 — see plan OD-11):** The construction as specified operationalizes *cost-asymmetry boundary sensitivity* — cases sitting near both R_T and R_F decision boundaries under their respective cost regimes. This is correlated with but not identical to *intrinsic evidential conflict in x* (features carrying opposing signals). Under policy-constrained hypothesis spaces the two senses tighten: the policy constraint reduces model degrees of freedom, more tightly coupling loss-landscape boundaries to feature-space evidential structure. But the w_T and w_F values are themselves modeling choices, so the constrained-interpretation argument requires §3.6's manifest sensitivity reporting (perturbation across w, ε, H) to be *load-bearing rather than ornamental*. §3.1 (motivation) and §3.6 (sensitivity reporting) are a single argument across two surfaces; V1.1 owes the explicit version of this coupling. Section 4's I-as-inter-set-disagreement inherits the caveat: the boundary-sensitivity reading is direct from the construction; the evidential-conflict reading requires the constrained-hypothesis-space argument and the sensitivity-reporting evidence together.

### 3.2 Contract: R_T(ε_T) — the grant-emphasis set

**Definition.** R_T(ε_T) is the set of binary classifiers h: X → {grant, deny} that satisfy all of:

1. **Policy admissibility.** h's factor support satisfies `PolicyConstraints.is_feature_subset_admissible()` (mandatory present, prohibited absent), and h's fit respects `PolicyConstraints.monotonic_cst()` at the declared feature ordering.
2. **Regime scope.** h is fit on training cases whose applicable-regime check passes; out-of-regime cases are excluded from training and not scored at inference.
3. **Grant-emphasis ε_T optimality.** h is ε_T-optimal on the grant-emphasis loss L_T over the in-regime training sample. L_T weights grant-side errors more heavily than deny-side errors; the canonical default at V1 is L_T(y, ŷ) = w_T · 1[y=grant, ŷ=deny] + 1[y=deny, ŷ=grant], with w_T chosen so the Bayes-optimal classifier under L_T predicts grant on cases where P(grant | x) ≥ τ_T for a τ_T < 0.5.

**Contract surface.** A set-construction implementation produces R_T(ε_T) given:
- a `PolicyConstraints` instance (Section 2);
- a training corpus (in-regime cases with grant/deny labels);
- a hyperparameter space H (model class, tree depth, leaf size, etc.);
- a grant-emphasis weight w_T;
- a tolerance ε_T.

Output: a non-empty set of fitted classifiers, each carrying its hyperparameter signature, its training loss under L_T, and its factor-support trace (the path-walk attribution the wedge already implements).

**Invariants.**
- Every h ∈ R_T(ε_T) is policy-admissible.
- For every h, h's L_T training loss is within ε_T of the best policy-admissible loss achievable in H.
- The set is non-empty iff at least one policy-admissible classifier in H achieves L_T training loss below the best-plus-ε_T threshold. (The empty case is a governance-visible signal that the policy + hypothesis-class combination is too tight; flagged but not silently coerced.)

### 3.3 Contract: R_F(ε_F) — the deny-emphasis set

**Definition.** R_F(ε_F) is the symmetric construction with the loss inverted: L_F weights deny-side errors more heavily. The canonical default at V1 is L_F(y, ŷ) = 1[y=grant, ŷ=deny] + w_F · 1[y=deny, ŷ=grant], with w_F chosen so the Bayes-optimal classifier under L_F predicts deny on cases where P(deny | x) ≥ τ_F for a τ_F < 0.5.

**Contract surface.** Identical to §3.2 with L_F substituted for L_T and ε_F for ε_T.

**Invariants.** Identical to §3.2 with the corresponding substitutions. The empty-R_F case is again a governance-visible signal — flagged, not coerced.

### 3.4 The relationship to single-R(ε) and to T/F within a single model

The single-set wedge R(ε) is approximately the cost-symmetric special case w_T = w_F = 1 (standard binary loss). R_T(ε_T) and R_F(ε_F) under symmetric ε but asymmetric w generalize: they are two policy-constrained Rashomon sets evaluated on *different objectives*. Each set still emits T-support and F-support attribution per the wedge's existing path-walk mechanics; the F = 1 − T identity still holds *within* a given model in either set. What's new is that T (grant-supportive evidence in R_T members) and F (deny-supportive evidence in R_F members) are now produced by *different model populations* and can carry independent information.

Inter-set disagreement (Section 4) is the formal mechanism by which this independence becomes a usable signal. A case where R_T predicts grant with high T-support *and* R_F predicts deny with high F-support is the conflicting-evidence case that single-R(ε) could not represent. A case where both sets agree on prediction (e.g., both predict grant) is *not* conflicting-evidence regardless of within-model T/F values; the two-axis structure is meaningful only when the two sets disagree.

### 3.5 Asymmetric ε — default and rationale (OD-3)

**V1 default: ε_T = ε_F.** Symmetric tolerance is the default both because it minimizes degrees of freedom (one ε to defend rather than two) and because the asymmetric-ε case introduces a governance question (whose decision-set's tolerance is wider?) that should be answered by policy, not by methodology.

**The asymmetric case as regulatory optional.** Regulatory frameworks already encode asymmetric grant/deny risk treatment. The Equal Credit Opportunity Act's adverse-action framework places explicit duties on deny decisions (specific reasons must be furnished; the bank carries the burden of explanation) that do not apply symmetrically to grant decisions. A bank's policy may legitimately declare that its deny-side decision-set tolerance ε_F should be tighter than its grant-side ε_T — i.e., a deny is held to a higher methodological standard than a grant, because the consequences of an unjustified deny carry asymmetric regulatory weight.

When ε_T ≠ ε_F is invoked, the spec requires:
1. The asymmetry is declared in the policy YAML, not invented at construction time.
2. The rationale for asymmetry is recorded in the policy's audit trail (the same YAML the regulator reads).
3. The downstream inter-set disagreement metric (Section 4) accounts for the asymmetry — disagreement weighted by which side carries the tighter tolerance.

V1 implementation supports ε_T = ε_F only; asymmetric ε is named here as architecturally permitted and deferred to a future revision with the explicit rationale that V1 wants to validate the dual-set core claim before adding the asymmetry degree of freedom.

### 3.6 Construction-relativity

R_T(ε_T) and R_F(ε_F) are defined *relative to* the declared construction parameters: the policy graph (Section 2), the hypothesis space H, the training sample, the loss functions L_T and L_F including the cost weights w_T and w_F, and the tolerances ε_T and ε_F. This is the same parameter-relativity any Rashomon-set construction carries (`2026-05-09-cliff-and-constraint-saturation-synthesis.md` §3) and is not a weakness — the construction is *declarable and auditable*, and the declaration is itself the transparency property that distinguishes the methodology from arbitrary-threshold attribution rules.

Two corollaries the spec records explicitly:

- **Reproducibility requires recording the full construction.** A bank's published R_T(ε_T) is only meaningful if it ships with the policy YAML, the hypothesis space declaration, the training sample identification, the loss weights, and the tolerances. Stripping any of these decouples the set from its audit basis. The spec mandates that set construction emit a *construction manifest* alongside the set itself, listing all six parameters with their values.

- **Policy revision invalidates R_T / R_F.** A policy update — even a small constraint change — produces a different `PolicyConstraints` instance and therefore a different R_T(ε_T) and R_F(ε_F). The mechanism does *not* support hot-swapping policy on a pre-built set; revision triggers reconstruction. This is the dynamic-construction property the strategic argument (memory: `project_strategic_argument.md`) treats as a feature, not a bug, because each candidate policy generates its own auditable R_T / R_F under the same machinery.

### 3.7 Structural distinctiveness from per-model attribution methods

Adapted from `2026-05-09-cliff-and-constraint-saturation-synthesis.md` §3 and generalized to dual-set:

> Within a specified construction (policy graph, H, training sample, w_T, w_F, ε_T, ε_F), whole-class attribution-failure on either side is a logical property of R_T(ε_T) or R_F(ε_F) **as sets**, not of any element. Per-model attribution methods (SHAP, LIME, integrated gradients) evaluate elements, not sets. The cliff signal — count of zero supporting factors across all members of R_T or R_F — is therefore structurally inaccessible to per-model methods; only approximable via thresholded aggregation rules over a separately-chosen ensemble, with the threshold introducing arbitrariness the set-level signal does not require.

The dual-set construction adds a second structural distinction beyond the cliff:

> Cases where R_T(ε_T) predicts grant with high T-support and R_F(ε_F) predicts deny with high F-support — *conflicting-evidence cases* — are a property of the *pair of sets*, not of either set individually and not of any single model. A per-model method evaluates one model's attribution and cannot represent the joint structure of two cost-asymmetric set-level objectives disagreeing on the same case. This is type-distinct from "the model's attribution is uncertain" — the uncertain-attribution case is a property of a single model; the conflicting-evidence case is a property of two separately-constructed, separately-validated cost-asymmetric model populations producing incompatible recommendations.

A SHAP-on-ensemble counter (run SHAP on multiple models, look for attribution disagreement) can approximate prediction-side disagreement but cannot produce the *governance-relevant* version: the set definitions are not policy-derived, the cost regimes are not separately declared, and the construction manifest does not exist. The structural advantage of the dual-set construction over SHAP+ensemble is not "we use sets" — it is the policy-constrained set construction plus the cost-asymmetric pair plus the construction manifest. Each is necessary; together they produce an auditable governance artifact that per-model attribution methods cannot natively produce regardless of how many models they are run on.

---

## 4. Indeterminacy I as inter-set disagreement

### 4.1 The reframing

Prior memos specified I as a four-species vector computed *per case* from feature-level signals (`2026-05-08-indeterminacy-operationalization-memo.md` §3): local-density, multivariate-coherence, Ioannidis-suspicion, retrospective-trajectory. Each species is a case-level computation defined relative to the training distribution and (for some species) the model's leaf structure.

The dual-set construction (Section 3) makes a different operational definition of I available: I is *what R_T(ε_T) and R_F(ε_F) disagree about on the case*. The inter-set framing reframes what I is at the load-bearing layer, before the species decomposition:

> **I as inter-set disagreement.** For each case x in the substrate's in-regime scope, I(x) measures the divergence between R_T(ε_T)'s response to x and R_F(ε_F)'s response to x. Higher I(x) means the two cost-asymmetric policy-admissible sets disagree more about x.

This is operationally observable from the sets' outputs alone — no per-species feature computation is required to get a primary I signal. The four species become *diagnostic decomposition* of *why* a case shows high inter-set disagreement; they enrich the signal rather than constitute it.

The reframing does not invalidate the species memo. It places that memo's content one layer down: the species explain the *generators* of inter-set disagreement, where I-as-disagreement is the *measurement*. Section 4.4 below specifies the relationship explicitly.

### 4.2 V1 operational definition (OD-4 default)

V1 commits to a per-case I scalar derived from prediction-side disagreement:

> **I_pred(x) = |E[h_T(x) | h_T ∈ R_T(ε_T)] − E[h_F(x) | h_F ∈ R_F(ε_F)]|**

where each expectation is over the set's members under uniform weighting (or under a declared weighting recorded in the construction manifest). For binary classifiers emitting {grant, deny}, the expectation can be taken on the predicted-probability surface (giving a [0, 1] scalar I_pred per case) or on the hard-label surface (giving a discrete disagreement count). V1 default: predicted-probability difference; alternative discrete-label version named.

**Why this is the V1 default (and what it carries):**
- *Directly observable* from set outputs; no additional feature computation needed.
- *Interpretation is direct under boundary-sensitivity reading*: high I_pred means the case sits where reasonable cost-asymmetric admissible models split decisions.
- *Interpretation under evidential-conflict reading requires §3.1's V1.1 argument*: the constrained-hypothesis-space tightening claim plus §3.6's sensitivity reporting are what license reading I_pred as evidence about *x* rather than about (w_T, w_F) choice. Until V1.1 lands the joint argument, I_pred is best read as boundary-sensitivity-under-cost-variation; the stronger interpretation is queued.

**Attribution-side I.** I_attr(x), defined as some divergence between R_T-aggregated factor-support and R_F-aggregated factor-support on x, is an alternative or supplementary signal. V1 names it as architecturally permitted but does not specify the metric (Jaccard on factor sets, JSD on factor-support distributions, set-cardinality difference each defensible); the choice is deferred to OD-4's V1.1 resolution alongside the per-instance-vs-population question below.

### 4.3 Per-instance vs population-level (OD-4)

I_pred(x) is per-instance. Two derived population-level quantities are useful for governance:

- **Disagreement rate:** the fraction of in-regime cases with I_pred(x) above a threshold. A property of the (policy, substrate, ε, w) combination, not of any case. Reported per construction in the manifest.
- **Disagreement distribution:** the full distribution of I_pred values across cases, summarized by quantiles. Surfaces tail structure the rate cannot show.

V1 default: emit per-instance I_pred per case (matching the wedge's existing per-case schema), plus the two population summaries in the construction manifest (§3.6). Population-only emission is rejected at V1 because it would discard the case-level identification that governance interrogation needs ("which cases are high-I?" is a governance question; the population summary alone cannot answer it).

### 4.4 The four species as generators of disagreement

The indeterminacy memo's four species remain authoritative for *what each species computes*. The reframing here is *what role each plays under the dual-set construction*:

- **Local-density.** A case unusual in its leaf's typical feature distribution is more likely to produce R_T / R_F disagreement, because the two cost-asymmetric sets fit different decision surfaces and atypical-in-leaf cases land where the surfaces diverge. Local-density per case is therefore a *generator* of I_pred. It can be reported as a separate diagnostic axis (a per-case local-density score alongside the per-case I_pred) but is not a separate dimension of I itself.

- **Multivariate-coherence.** A case violating expected feature correlation structure is also a generator: cost-asymmetric models with different feature emphases react differently to coherence-violating cases. Same status — diagnostic, not constitutive.

- **Ioannidis-suspicion.** A case with provenance pathology (round-number clustering, threshold-hugging, Benford violations) is a generator in a weaker sense: the suspicion battery flags data-quality concerns that may propagate into both R_T and R_F training and produce disagreement that isn't about the case's underlying credit risk at all. Reporting Ioannidis-suspicion alongside I_pred is governance-useful precisely because it tells an examiner *what the disagreement is about* (data pathology vs evidential structure).

- **Retrospective-trajectory.** This species is structurally distinct from the other three. The other three are case-level signals computed from features. Retrospective-trajectory is *longitudinal* — it propagates post-origination outcome surprise back into the construction itself, shifting which models qualify for R_T or R_F under revised loss functions. It is a *set-membership signal*, not a per-case feature signal. Section 5 specifies it as an operational mechanism for set revision under retrospective evidence; it is not measured as a per-case I component in V1.

The decomposition matters: an examiner asking "why is case x high-I?" can be answered by species-level decomposition (high local-density, low multivariate-coherence, no Ioannidis flags, retrospective-trajectory-stable) without conflating the answer with the I measurement itself. The four species enrich the signal; I is still the measurement.

### 4.5 Why the supervisory problem dissolves

The indeterminacy memo §1 noted that I-supervision (training a model that emits I) requires labels for I, which are not naturally available. The dual-set framing dissolves this problem at the measurement layer:

- R_T(ε_T) is trained against grant/deny labels under L_T.
- R_F(ε_F) is trained against grant/deny labels under L_F.
- I_pred(x) is *derived* from the two sets' outputs, not learned from a separate I label.

No supervisor produces I labels. The construction is *observable* from set outputs; the per-species diagnostic decomposition is computed from features and (for retrospective-trajectory) from outcome data, neither requiring I-specific supervision.

What the dissolution does *not* solve: the §3.1 caveat (boundary-sensitivity vs evidential-conflict interpretation) and OD-10's substrate-axis question (what I_pred *means* on HMDA-decisions vs LC-outcomes substrates) both bear on how I_pred is *read* by a governance audience. The supervisory problem dissolves at the measurement layer; the interpretation problem remains and is the V1.1 work.

### 4.6 What this section does *not* specify

- The choice of attribution-side I_attr metric (deferred to V1.1; named architecturally permitted in §4.2).
- Per-species computational details for the wedge implementation (those live in the indeterminacy memo §4 and remain authoritative there).
- How I_pred feeds into Category 1 vs Category 2 detection (Section 6's work; §6 reads I_pred as one input alongside retrospective-trajectory output).
- The retrospective-trajectory species's full operational definition (Section 5's work).

---

## 5. Retrospective trajectory species — operational definition

### 5.1 Motivation and load-bearing role

The retrospective-trajectory species is named load-bearing by two prior memos for distinct reasons:

- `2026-05-08-indeterminacy-operationalization-memo.md` §3.4 / §7 — load-bearing for the Olorin deployment story. Banks have post-origination lifecycle data; current credit-scoring stacks treat it as model-retraining input or aggregate drift metric. The retrospective-trajectory species structures it as a *per-case I-channel* that is externally examinable.
- `2026-05-08-adversarial-robustness-and-examinability-memo.md` — load-bearing for the structural defense argument post-publication. Retrospective-trajectory has the property that it *cannot be gamed without producing exactly the evidence it is designed to detect*: a bank that wants to evade the species's signal must produce outcome data that the species would flag. This is the adversarial-robustness property that underwrites Section 6's standard-of-care argument.

Sections 5 below specifies the mechanism for V1; the *property* the memos name (adversarial robustness; per-case lifecycle channel) is inherited from the memos and is not restated here.

### 5.2 The surprise model

Define a *surprise model* S: origination_features → outcome_surprise, trained on completed-observation cases where both origination features and realized outcomes are available.

**outcome_surprise** is a per-case scalar capturing the gap between what origination features predict and what actually happened. V1 canonical default: residual of a calibrated probability model — for a case with origination features x and realized binary outcome y ∈ {paid, defaulted}, surprise(x, y) = y − P̂(default | x) under a baseline model P̂ trained on the same vintage class. Surprise is positive when the case defaulted more than its origination features predicted; negative when it paid better than predicted. The magnitude is the load-bearing quantity for retrospective detection.

**Why a separate model and not direct residuals on R_T / R_F.** Two reasons:
1. R_T and R_F are constrained to policy-admissible models. The surprise model is *not* policy-constrained — its job is to detect signal the policy-constrained models may have missed. Constraining the surprise model to the same hypothesis space defeats the purpose.
2. The surprise model can use features the policy-constrained model class excludes (with the asymmetric caveat that *protected-class proxies* must still be excluded from S; surprise modeling is not a back door for prohibited features). The surprise model's feature set is a separate declaration in the construction manifest.

### 5.3 Two surface configurations

The indeterminacy memo §4 distinguished a production version and an LC-evaluation proxy. The V1 spec preserves both:

**Production version (Olorin deployment).** S is trained on the bank's own historical loans with completed terminal observations. Origination_features are the same as those R_T / R_F use; outcome_surprise is computed against the bank's realized outcomes. Per-case surprise scores feed into V1.1's set-revision mechanism (§5.4) and the regulator-facing trajectory report.

**LC-evaluation proxy.** S is trained on later vintages' completed outcomes (e.g., 2016–2017 cohorts) and applied retrospectively to 2014Q3 / 2015Q3 / 2015Q4 origination features. This tests the *architecture* on the LendingClub corpus without claiming production deployment. The proxy is sufficient for May 23 spec validation but is not equivalent to production behavior — the LC corpus has origination-selection structure and a specific population that real-world bank deployment will differ from.

The construction manifest must declare which configuration produced the surprise scores; substrate-axis caveats from OD-10 apply asymmetrically here. LC-evaluation proxy results are not directly transferable to bank deployment without an explicit transferability argument.

### 5.4 The set-revision mechanism

The retrospective-trajectory species feeds back into R_T / R_F membership through a revised loss function. Mechanism:

1. **Original loss.** R_T(ε_T) and R_F(ε_F) are constructed under L_T and L_F respectively (Section 3).
2. **Surprise-weighted revised loss.** L_T' weights cases by |surprise(x, y)| — cases the surprise model flags get more weight in the loss. L_F' is the symmetric reweighting on the deny side.
3. **Revised set membership.** A model h previously in R_T(ε_T) may exit R_T(ε_T) under L_T' if it systematically misclassified surprise-elevated cases — i.e., the model was ε_T-optimal on L_T but is not ε_T-optimal on L_T'. Conversely, a model previously *outside* R_T(ε_T) may enter under L_T' if it correctly handled surprise-elevated cases that L_T-optimal models missed.

Set revision is the operational form of *the Rashomon set shifting under retrospective evidence* — the framing Tony introduced in the 2026-05-10 conversation about Category 2 failures. A Category 2 failure (informational under-weighting) shows up as a set-membership shift: models that retrospectively turn out to have weighted the under-weighted signal correctly enter R_T'(ε_T) / R_F'(ε_F); models that under-weighted it exit.

Set revision is *not* hot-swap. It is a separate construction with its own construction manifest, citing the original sets, the surprise model, and the revision parameters. The original R_T / R_F remain as historical artifacts; the revised R_T' / R_F' are new sets with their own audit trail.

### 5.5 Statistical test specifics (OD-5)

V1 default test for whether the retrospective trajectory species has produced a meaningful set shift:

**Test:** is there a model h ∈ R_T'(ε_T) \ R_T(ε_T) — i.e., a model that enters R_T under the surprise-weighted loss but was not in R_T under the original loss — that improves population-level holdout accuracy on surprise-elevated cases (|surprise| above a threshold) by a margin exceeding a stated significance threshold?

**Null hypothesis:** the original L_T-optimal models are also approximately L_T'-optimal on surprise-elevated cases; no set membership shift is warranted.

**Threshold:** V1 default is a 5% holdout-accuracy improvement on surprise-elevated cases at p < 0.05 under permutation testing across 1000 shuffles. The threshold is declared in the construction manifest; banks may legitimately choose more conservative thresholds.

**Alternatives named (not V1 default):** Bayesian posterior on set membership change; cross-validation stability across surprise-model variants; resampling tests on surprise-model robustness. Each is more sophisticated; V1 uses the simpler permutation test and flags the alternatives as V1.1 candidates if the simpler test proves under- or over-sensitive in practice.

### 5.6 Adversarial-robustness property (inherited)

The retrospective-trajectory species's adversarial-robustness property — *cannot be gamed without producing the evidence it is designed to detect* — is specified in the adversarial-robustness memo and inherited here as the underwriting for Section 6's standard-of-care argument. The property holds because:

- Gaming the surprise model requires either suppressing outcome data (which is observable by the regulator with auditing authority) or producing fabricated outcome data (which produces internal inconsistencies the surprise model surfaces against the bank's own historical record).
- The species is *retrospective* by construction: it operates on outcomes already realized. A bank cannot pre-decide what its loan book's surprise distribution will look like; the data accumulates.
- The surprise model is *separately constructed* from R_T / R_F: a bank that games R_T / R_F's construction does not thereby game S, because S uses a different feature set (with prohibited features still excluded) and a different (unconstrained) hypothesis space.

This property is the load-bearing piece for Section 6: the standard-of-care argument depends on Cat 2 detection being credibly forward-looking, and forward-looking credibility requires that the detection method survive adversarial knowledge of its own existence. Retrospective-trajectory has that property in a way per-case attribution methods structurally do not.

### 5.7 What this section does *not* specify

- The full mathematical form of the surprise model (V1 default is calibrated probability residual; alternatives like quantile regression, isotonic-calibration residuals, Brier-score decompositions are named in OD-5 but deferred).
- The feature-engineering details for S in production deployment (bank-specific; the deployment plan, not the spec, decides).
- The specific cadence at which S is retrained as new outcomes accumulate (operational concern; the spec specifies *when retraining is permitted* — at policy revision boundaries and at declared periodic intervals — but not the interval itself).
- The interaction between S and policy revision (when policy revises, the substrate for S shifts; this is non-trivial and is partially deferred to OD-10's substrate-axis work in V1.1).

---

## 6. Category 1 vs Category 2 detection criteria

### 6.1 The distinction (Tony's framing, canonical)

The retrospective failure taxonomy distinguishes two categories of post-decision failure that look similar from the loan-officer's chair but are structurally different and call for different governance responses:

- **Category 1 (inherent lending risk).** Factors that could not be foreseen at the time the decision was made. The evidence available at origination was weighted appropriately; circumstances subsequently shifted in ways no information available at decision time could have predicted. Health events, macroeconomic shocks, household-level events outside the data record. Category 1 is *tragic in the classical sense* — not preventable by better reasoning. The bank's defense is stable: "we could not have known."

- **Category 2 (informational under-weighting).** Factors that emerge from retrospective analysis of the entire dataset — not just from the individual decision's explanation — that could have reduced bank risk if appropriately weighted. The signal was in the data at decision time; the chosen model's analytical apparatus failed to capture it. Category 2 is *epistemic, not tragic*. The bank's defense is unstable: the data was there, the methodology that would have caught it was available (or becoming available), and the choice of analytical apparatus that missed it is the bank's choice.

The portfolio-level vs decision-level cut is the load-bearing line. Per-case post-hoc attribution (SHAP, LIME) explains *the decision*; it cannot diagnose *the dataset-level pattern* that distinguishes Cat 2 from Cat 1. That distinction is what Section 5's retrospective-trajectory species makes operational, and it is what Section 6's detection criterion formalizes.

### 6.2 The formal detection criterion (OD-6)

A case x is detected as **Category 2** when, under retrospective-trajectory set revision (§5.4):

1. The original R_T(ε_T) and R_F(ε_F) gave a particular prediction on x (call it the *original verdict*), and the realized outcome differed from the original verdict.
2. The revised R_T'(ε_T) ∪ R_F'(ε_F) — the union of the surprise-weighted revised sets — contains models that would have predicted the realized outcome on x.
3. The structural feature distinguishing R_T'(ε_T) \ R_T(ε_T) (the new entrants under surprise-weighted loss) from R_T(ε_T) \ R_T'(ε_T) (the original models that exited) is *expressible* — there exists a feature weighting, a feature interaction, or a decision-region pattern that characterizes the new-entrant models and was systematically under-represented in the original models.

A case x is detected as **Category 1** when conditions 1 holds but condition 2 or 3 fails — i.e., even under surprise-weighted revision, no admissible model would have predicted the realized outcome, or the new-entrant models are not structurally distinguishable from the originals in any expressible way (the revision is statistical noise, not signal).

A case x is detected as **ambiguous** when condition 2 holds but condition 3 is unclear (revised-set entrants exist but their structural distinguishing feature is unstable across cross-validation folds or under sensitivity to (w_T, w_F, ε) perturbation). Ambiguous cases are reported as both-likelihoods, not forced to a binary.

### 6.3 Boundary cases and reporting discipline

The formal criterion produces three categories — Cat 1, Cat 2, ambiguous — not a binary. The reporting discipline V1 specifies:

- **Per-case classification with confidence.** Each retrospectively-analyzed case carries a tuple (Cat 1 likelihood, Cat 2 likelihood, ambiguous flag, structural-distinguishing-feature description if Cat 2). The likelihoods are derived from the cross-validation stability and the (w, ε) sensitivity reporting (§3.6 mandate).
- **No forced binarization.** Reports may aggregate over Cat 2 likelihood thresholds for population summaries ("X% of post-default cases are likely Cat 2 at threshold 0.5") but the per-case record is always the tuple.
- **Boundary movement is governance-visible, not silent.** When a case transitions from ambiguous to Cat 2 (or back) under V1.1 revisions (refined surprise model, new vintages, etc.), the transition is logged in the construction manifest. The classification is a function of the data available at evaluation time, not a permanent label.

### 6.4 The standard-of-care argument

The Cat 1 / Cat 2 boundary moves with available methodology. A failure that is correctly classified as Cat 1 in 2024 (no analytical apparatus then could have caught it) may be reclassified as Cat 2 in 2026 if a methodology demonstrates routine detection of that failure class. This boundary movement has regulatory implications: a methodology that detects Cat 2 failures is implicitly an argument about where the standard-of-care boundary should sit.

That argument is *only credible* if the detection methodology has the adversarial-robustness property (§5.6). Without it, "the boundary should move because we can detect this" is self-promoting rhetoric — any vendor with a new attribution method could make the same claim. With it, the argument is structural: the methodology survives gaming because gaming it produces the evidence it is designed to detect. The standard-of-care argument and the adversarial-robustness property are inseparable.

Concretely: the regulator-facing translation of this spec should foreground the Cat 1 / Cat 2 distinction *paired with* the adversarial-robustness property, not the boundary-movement claim in isolation. The framing is a *structural observation about how Cat boundaries shift as detection methodologies become available, conditioned on those methodologies being adversarially robust*. The boundary movement is the leverage; the robustness is what licenses the leverage.

### 6.5 What SHAP and per-model attribution methods structurally cannot do

A per-model attribution method (SHAP, LIME, integrated gradients) applied to a deployed model can explain that model's per-case decisions. It cannot:

1. **Detect dataset-level patterns.** Cat 2 is a dataset-level pattern (per Tony's framing). Per-case attribution is by construction per-case; aggregating per-case explanations does not produce dataset-level inference.
2. **Compare against counterfactual model choices.** Cat 2 detection requires asking "what would an equally-good model that weighted X differently have predicted?" The per-model method evaluates the model that was chosen; counterfactual model evaluation is outside its scope.
3. **Carry adversarial robustness.** Per-model attributions can be gamed at training time (regularize attributions to look reasonable; suppress feature importance on sensitive variables). The gaming produces a model that still attributes reasonably on the surface but has not changed its underlying behavior. Retrospective-trajectory cannot be gamed this way because S operates on outcome data after decisions land, not on attributions before.

A SHAP-on-ensemble extension can approximate prediction-side trajectory by computing attribution variance across a manually-constructed ensemble of models — but the ensemble is not policy-derived, the cost regimes are not separately declared, the revision mechanism (§5.4) is absent, and the adversarial-robustness property does not transfer because SHAP-on-ensemble still operates on attribution-side artifacts, not on outcome-data feedback. The structural distinction from §3.7 carries forward to Cat 2: per-model methods cannot natively produce the governance-relevant Cat 2 signal regardless of how many models they are run on.

### 6.6 What this section does *not* specify

- The exact threshold separating ambiguous from Cat 2 (this is a calibration choice; V1 names it as a construction-manifest parameter and a sensitivity-reporting target, not a fixed value).
- The structural-distinguishing-feature description format (V1 names that one is required; the format — feature weight delta, decision-region difference, interaction term, etc. — is operational detail deferred to the implementation plan).
- The regulator-facing translation of Cat 1 / Cat 2 vocabulary into examination-procedure language (downstream artifact, not contents of this spec).
- The interaction with substrate-axis (OD-10): Cat 2 detection on HMDA-decisions substrate is detecting "past underwriters under-weighted X under cost variation"; Cat 2 on LC-outcomes substrate is detecting "models under-weighted X relative to realized outcomes." These are different governance claims and the substrate-axis V1.1 work bears directly on which claim each reported Cat 2 detection is making.

---

## 7. Prototype validation targets for May 23

### 7.1 What is already validated (prior evidence in hand)

The wedge has produced empirical evidence that bears on this spec's V1 claims, prior to the spec being written:

- **SHAP non-inferiority falsification** (`2026-05-09-shap-vs-rashomon-result-note.md`). Pre-registered, OTS-stamped. Four SHAP-silence criteria fail to recover Rashomon T-silent-all on LendingClub V₁/V₂_alt/V₂; per-case Jaccard 0.000–0.008; T-silent-all charge-off 0.292 vs base 0.148 (2× elevation); no SHAP criterion reproduces the U-shaped regime signature. Falsification arm of the cliff/structural-distinctiveness claim landed. *Caveat* (per cross-instance review 2026-05-11): the SHAP-instability vs Rashomon-silence anti-correlation under regime shift is a buried sub-finding deserving an amendment to the result note.
- **Cliff structure across three vintages** (`2026-05-09-cliff-and-constraint-saturation-synthesis.md`). Whole-class attribution-failure as a set-level signal; regime rotation (F-empty in V₁ pre-tightening, T-empty in V₂ post-tightening, regime-symmetric 1.74×/1.75× I-mean ratio); within-cohort hard-but-coherent vs hard-and-atypical decomposition.
- **I-stability prediction falsification** (`2026-05-09-i-stability-falsification-findings-note.md`). Tony's contrarian prediction that I would be more stable than T/F was falsified decisively (I CV 7–9× T CV across three vintages). This falsification operates under the *single-R(ε)* construction; its transfer to dual-set R_T/R_F is not yet tested and is itself a V1.1 validation target.

Combined, these establish the wedge's V₁ measurement infrastructure as substrate for the spec's V1 claims. They do *not* validate the spec's two new contributions (dual-set construction; Cat 1/Cat 2 detection) — those are May 23 targets.

### 7.2 New validation targets for May 23

V1's two new contributions each require at least one empirical demonstration before the May 23 deliverable. The targets are bounded; "validate" here means "produce evidence the contribution is operationally instantiable and produces governance-relevant outputs on at least one substrate," not "validate across all substrates and regimes."

**Target A: Dual-set construction demonstration.**
- Build R_T(ε_T) and R_F(ε_F) on a single LendingClub vintage (V₂ = 2015Q4 recommended for continuity with prior findings) under the V1 default L_T / L_F with w_T = w_F = 1.5 (illustrative, declared in construction manifest).
- Emit per-case I_pred(x) per §4.2.
- Demonstrate that R_T(ε_T) ≠ R_F(ε_F) on a nontrivial fraction of in-regime cases — i.e., the two sets are not degenerate copies of each other.
- Report disagreement-rate distribution alongside the existing single-R(ε) cliff structure for comparison.
- Acceptance: ≥ 1% of in-regime cases show I_pred above an a-priori-declared threshold, with the threshold itself declared in the construction manifest.

**Target B: Cat 2 detection demonstration.**
- Use the same V₂ vintage. Train the surprise model S on a later vintage's completed outcomes (LC-evaluation proxy per §5.3 — recommended source: 2016Q1–2016Q4 originations with completed terminal observations through end of available LC data).
- Apply S to V₂ origination features; identify cases with |surprise| above a stated threshold.
- Construct R_T'(ε_T) and R_F'(ε_F) under the surprise-weighted loss L_T' / L_F' per §5.4.
- Identify at least one case x such that: original R_T/R_F predicted one outcome on x, the realized LC outcome differed, and a model in R_T'(ε_T) \ R_T(ε_T) predicts the realized outcome with an expressible structural-distinguishing feature.
- Acceptance: at least one such case identified with the structural-distinguishing feature articulated in text. *Statistical significance is not required at this scale*; the May 23 target is demonstration of the mechanism, not population-level validation. Population-level validation is post-May-23.

**Target C (combined): integration story.**
- A single end-to-end run on V₂ produces: the construction manifest (per §3.6); the in-regime case dataset with per-case I_pred (per §4.2); the set-revision manifest (per §5.4); and at least one Cat 2 case worked through with its tuple (likelihoods, ambiguous flag, structural-distinguishing feature) per §6.3.
- Acceptance: the run executes end-to-end and produces all four artifacts; the artifacts are auditable in the sense that a third reader can reconstruct the construction parameters from the manifest and re-execute.

### 7.3 Explicit out-of-scope items for May 23

The deliverable's bounded scope. These items are *not* required for May 23 and *are* required for downstream artifacts; staging them as out-of-scope is part of the spec's scope discipline:

- **Regulator-facing document translation.** The Cat 1 / Cat 2 vocabulary, the construction-manifest declarations, and the standard-of-care framing all require translation into examination-procedure language for the regulator-document. That translation is a downstream artifact, not contents of the May 23 prototype.
- **Paper 2 (architecture) prose.** This spec is the architectural source for Paper 2; the paper itself is downstream.
- **HMDA cross-validation.** Per OD-10 (V1.1), HMDA and LC are different substrates with different governance interpretations. Demonstrating Targets A–C on LC is sufficient for May 23; the HMDA companion validation is post-May-23.
- **Fannie Mae generalization.** Pre-registered in `2026-05-09-shap-vs-rashomon-result-note.md` §8 as a followup. Cross-asset-class + cross-regime test of whether the per-case-non-overlap and U-shape-non-recovery results survive. Post-May-23.
- **Multi-policy M&A sweep.** The strategic argument (memory: `project_strategic_argument.md`) names retrospective multi-policy comparison as a load-bearing use case for mid-tier-bank deployment. Operationalizing it requires multi-policy construction support, which is a downstream capability and not part of V1 set construction.
- **V1.1 OD-10..15 resolutions.** Each is a deliberate deferral with rationale; collectively they are post-May-23 work *except* OD-12 (post-fit split-use check) and OD-13 (collector standardization), which are flagged in the plan's Task 11 as required by May 23.
- **Production deployment-grade infrastructure.** The May 23 prototype validates the spec's mechanism; it does not produce production-grade deployment. Performance characteristics, monitoring, on-call runbooks, etc. are out of scope.

### 7.4 What May 23 validation does *not* establish

Honest framing of what the validation targets above can and cannot conclude:

- Targets A–C demonstrate *instantiability* on one substrate (LendingClub) under one policy graph (thin demo). They do *not* establish that the mechanism generalizes across substrates, policies, or regimes. Generalization claims require the post-May-23 work named in §7.3.
- A successful Target B demonstration (≥1 Cat 2 case found) does *not* establish Cat 2 *prevalence* or that Cat 2 detection works at production-relevant rates. Prevalence is a population-level claim that requires more cases and the substrate-axis V1.1 work.
- The construction manifest (§3.6) is *declared* in the run outputs but its *sensitivity reporting* requirement (OD-15) is V1.1 work. May 23 demonstrates the manifest exists with the V1 fields; load-bearing sensitivity reporting is V1.1.
- The adversarial-robustness property (§5.6) is *inherited from the prior memo and reasoned about in §6.4*; it is not empirically demonstrated by May 23. Empirical demonstration of adversarial robustness is a long-horizon validation that no realistic prototype timeline supports; the property's load-bearing role is structural, not empirically established by this spec.

The disciplined framing of the May 23 deliverable is: *the mechanism is instantiated, the artifacts are produced, the construction is auditable, and at least one Cat 2 case is worked end-to-end*. That is sufficient for the Olorin engagement and for Paper 1's empirical anchors; it is insufficient as a complete validation of the V1 spec's claims. The post-May-23 work is named in §7.3 and the V1.1 register so the gap is auditable rather than hidden.
