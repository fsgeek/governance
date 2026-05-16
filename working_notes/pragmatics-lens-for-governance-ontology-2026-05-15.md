# A pragmatics lens for governance ontologies

**Prepared:** 2026-05-15. For: Aki (banking-ontology collaborator). Draft; Tony to revise.

**One-line frame.** Standard ontology engineering is semantics-centric. For governance domains, the layer that does the actual work — context-of-use, scope-of-validity, who-asks-and-why — is pragmatic. This document offers that as a *lens* (a way to look at the field), not a *thesis* (a position to argue for). Try the lens. If it makes hidden structure visible, keep it. If it doesn't, discard.

---

## 1. The lens

Pragmatics in linguistics is the layer semantics can't capture: meaning-in-context. The same sentence carries different commitments depending on speaker, audience, regime, and stipulated background. Speech-act class (commissive vs. constative vs. declarative), indexicality (the same term refers differently in different contexts of utterance), frame semantics (a word evokes a structured background of expected relations) — these are the layer's standard machinery.

Standard ontology engineering treats meaning the way Frege treated it: term *T* denotes thing *X*; downstream tooling reasons over the denotation. Foundational ontologies (BFO, DOLCE, UFO), W3C standards (OWL, SHACL, PROV-O), and the working methodologies (METHONTOLOGY, NeOn, Grüninger-Fox CQ-driven, ODP-composition) all assume the term/concept/role is the primitive — and that context, governance, evolution, and disagreement are *documentation around* that primitive.

The lens: **ask what an ontology's pragmatic layer is, and whether it's typed or smuggled in.** Three sub-questions:

1. **Indexicality.** What contexts does the definition tacitly assume? Substrate (which population, which jurisdiction, which product line)? Variant (which policy version, which operational regime)? Temporal-deployment (effective dates, supersession, sunset)? Does the artifact carry these as first-class structure, or as annotations that humans must read?

2. **Speech-act class.** When a constraint reads "MUST," is that commissive (the institution commits), directive (the regulator demands), constative (the world is asserted to be this way), or declarative (the act of writing it makes it so)? Most ontologies type a constraint by *what it constrains*, not by *what kind of commitment it is*.

3. **Frame evocation.** What background relations does a term *invoke* without naming? In banking: when a policy says "DTI is mandatory," the operative claim is that the policy's interpretive frame foregrounds DTI — not that every model in the band must literally split on it. The standard reading (must-split) is an enforcement reading. The pragmatic reading (must-invoke-the-frame) is a different primitive.

The lens has empirical contact in the project's recent work. The silence-manufacture finding (FM #12) demonstrated that the same band corpus produces *different* adequacy verdicts under variant-A and variant-B — i.e., the verdict is variant-indexed (pragmatic), not just data-dependent (semantic). The HMDA-RI 2022 trimodal-replication failure (P-scorecard MISS) showed that what worked on FM substrate didn't transfer to HMDA — substrate-indexicality, again pragmatic. The pattern itself — pre-registered uniformity-bet → falsification → tightened-to-indexed-claim — is the project's empirical case for naming the layer.

The remainder of this document applies the lens to (a) existing construction methods and tooling, (b) the banking ontology landscape Aki is most likely operating in, and (c) the project's own results — to see what the lens makes visible in each.

---

## 2. The lens applied to existing construction methods

The standard taxonomy has five families (top-down formal, bottom-up data-driven, LLM-assisted, pattern-based, hybrid/CQ-driven). All five are semantics-centric at the core. None types pragmatic context as a construction primitive. The relevant question is: *how* does each smuggle pragmatics in unlabeled?

**Top-down formal (BFO/DOLCE/UFO + OWL + METHONTOLOGY/NeOn).** Definitions are stated as if context-free; in practice, the choice of upper ontology, the OWL profile (DL vs. EL vs. RL), and the inheritance from BFO realist commitments are all pragmatic choices that downstream consumers cannot see. There is no canonical pattern for "this axiom held 2018-Q3 through 2022-Q1" or "this region is deliberately unspecified pending regulatory clarification" — both are pragmatic primitives that get relegated to annotations.

**Bottom-up data-driven (FCA, schema mining, IE-from-text).** Extraction collapses disagreement: where two policy authors used different terms for the same concept, or the same term for different concepts, the extractor silently picks one. This is the silence-manufacture pattern at the construction layer — the pragmatic disagreement gets buried by design.

**LLM-assisted (OG-RAG, OntoKG, FrODO, the legal-norms Graph-RAG line).** Pretraining cutoff is a hidden temporal index. Next-token likelihood flattens contested terminology toward dominant usage. Hallucinated classes are indistinguishable from grounded ones in OWL output. The Microsoft OG-RAG line (EMNLP 2025; arXiv 2412.15235) and the legal-norms Graph-RAG paper (arXiv 2505.00039 — explicit Temporal Version entities) are the closest the literature comes to typing temporal pragmatics; both are domain-specific KG schemas, not general construction discipline.

**Pattern-based (ODPs + eXtreme Design + SAMOD).** Patterns embed pragmatic commitments (realist vs. descriptive, mereological choices, role-vs-quality distinctions) that the catalog presents as solution units. Pattern *selection* presupposes a shared problem vocabulary; in contested domains the dispute migrates from "which pattern" to "what's the right question" — useful migration, but the methodology gives no resolution beyond "more workshops."

**Hybrid / CQ-driven (Grüninger-Fox, TOVE, NeOn).** Competency questions are auditable artifacts and the closest thing in the literature to typed pragmatic intent — they record what the ontology was *supposed to do*. But CQ test benches cover only the *known* questions; no built-in slot for "questions the regulator hasn't asked yet." CQ retirement when regulation changes is unsystematized. The pragmatic layer is *present* (in the CQ artifacts) but isn't bound to the axioms it justifies.

**Cross-cutting finding from this lens.** All five families face the same four-fold gap, viewed from four angles: incompleteness representation, temporal/regulatory versioning as semantic (not metadata), contested-term representation, construction-time provenance bound to axioms. These are not four separate problems; they are one problem — *the pragmatic layer isn't typed* — viewed through four operational windows. The cleanest position-paper articulation in the literature is Meyman's *Versioned Meaning* (SSRN 5918182), which remains a position paper rather than a tooled methodology.

---

## 3. The lens applied to analytic tooling

The eight standard analytic legs (consistency, coverage, alignment, term-equivalence, granularity, completeness, evolution, provenance) divide cleanly under the lens: the legs that operate on a *given reference* are semantics-tooled and mature; the legs that need to operate on *what isn't said* are pragmatically-needed and thin.

**Mature, semantics-tooled (well-developed):**
- Consistency checking: DL reasoners (HermiT, Pellet/Openllet, ELK, Konclude) — given OWL, decide satisfiability.
- Alignment: AML, LogMap, BERTMap, the OAEI-LLM line — given two ontologies, produce a mapping. The 2025 OAEI Bio-ML showed no single winner across tasks (BioGITOM, BERTMap, LogMap-LLM each led on one).
- Structural metrics: OntoMetrics (32 metrics across 7 categories), OOPS! (41 pitfalls), OQuaRE.
- Provenance schemas: PROV-O, PAV, PROV-O extensions for scientific workflows.

**Thin, pragmatically-needed (under-developed):**
- *Completeness diagnostics.* Every tool measures coverage against a *given* reference (corpus, CQ list, closure axiom, sibling ontology). None confronts the unknown-unknown — dimensions the modellers were not equipped to see. For regulatory contexts, where the harms-of-omission story is load-bearing, this is the gap. The position is *uncertain* (the closure-relevant literature is fragmented across DL, KG-completion, and information-systems-ontology communities), but no tool we found contradicts the characterization.
- *Semantic-drift detection on ad-hoc artifacts.* SemaDrift and OnDeT require OWL versions. Most banking ontologies live in spreadsheets and policy documents. No off-the-shelf tool watches a corpus of policy PDFs and flags concept drift; the closest are general-purpose embedding-drift detectors borrowed from ML monitoring.
- *Provenance of modelling decisions.* PROV-O captures *who recorded what when*. It does not capture *which alternatives were considered and rejected, and why* — the pragmatic-annotation layer.

**One speculative leg the lens would add: task-grounded equivalence.** Standard term-equivalence (§4 of analytic tools) asks "do labels/contexts/embeddings agree?" The pragmatic reformulation: train a Rashomon set of predictive models for a downstream task using term T1 vs. T2 as inputs; call them *task-equivalent* if the ε-band of near-equivalent models is invariant under substitution. This is functional equivalence ("equivalent for the decision at hand") rather than referential equivalence. It would sit between alignment and label-equivalence as a third leg. The failure mode is obvious: it would call distinct concepts equivalent whenever the downstream task doesn't distinguish them — which for some governance settings is the *desired* answer, and for others is exactly the wrong one. The lens does not commit you to this construction; it just makes the alternative visible.

---

## 4. The lens applied to the banking ontology landscape

The landscape has one big ontology (FIBO), a handful of legal-side ontologies (LKIF, LegalRuleML, Akoma Ntoso, ELI/ECLI), a set of data-dictionary-adjacent standards that *function* as ontologies inside banks (ISO 20022, BIAN, ACTUS, MISMO, FFIEC Call Report XBRL, HMDA LAR), recent academic LLM-assisted work, and the typical ad-hoc bank artifact.

**FIBO under the lens.** FIBO is an entity-and-instrument ontology with strong coverage of *what financial things are* and competent coverage of *who the parties are*. It does not natively model: policy as a first-class object (the bank's deployed decision rule, with version, effective dates, exception ladder); decision-routing and observability (which model evaluated this application, which policy gate, what tier, who has standing to ask why); indexicality / pragmatics (constraints want explicit context-of-utterance slots — substrate, variant, granularity); or the ontology's own incompleteness. FIBO's LOAN module reaches the contract; it does not reach the credit-policy DAG. The community is aware of the policy/decision gap; SR 26-2 may push consumers toward filling it, but no shipping standard does.

**Legal-side ontologies.** LegalRuleML's defeasibility operators are the closest thing in the standards landscape to a typed pragmatic primitive — a rule can be overridden by other rules, syntactically acknowledging non-finality. LKIF's meta-legal layer can talk about the legal sources (a step toward provenance). Neither addresses *decision-procedure-as-deployed-by-a-supervised-entity*; both model law-as-authored, not law-as-applied.

**FRO (Financial Regulation Ontology) is worth a direct read.** Single-maintainer (Jurgen Ziemer / Jayzed Data Models); imports both FIBO (entities) and LKIF (legal expressions); loads CFR Title 12 (Banking) and Title 17 (Investment Adviser Act) plus USC Titles 12 and 15. The worked example is whether an investment fund must register with the SEC. License unclear on the public page. **This is the closest published artifact to a policy-codification ontology — comparable, not competing infrastructure.** The audit question to bring to a reading is: does FRO's hierarchy support representing *what the regulator has not yet specified*, vs. only what it has? If yes, the project should cite it; if no, that's the gap.

**The data-dictionary standards.** ISO 20022, BIAN (v12.0 late 2024), ACTUS, MISMO (v3.6.2 CR Oct 2025), FFIEC Call Report XBRL, HMDA LAR — these are *not ontologies* in the formal sense, but they are what banks actually run on. None types pragmatic context as first-class. MISMO is the operative data dictionary for the project's HMDA work (not FIBO LOAN); recognising that is itself a pragmatic observation.

**The typical ad-hoc bank artifact** (inferred from vendor pitches, MISMO implementation guides, consulting whitepapers): Excel-based business glossary; DMN-style or Excel decision tables for underwriting rules and exceptions; partially-implemented data dictionary for the data warehouse; code-as-policy in underwriting Java/Python/COBOL or Rego policies or SQL stored procedures (*this is where the actual decision lives*); vendor-supplied KYC/AML/sanctions taxonomies. Five capabilities consistently absent: round-trip from policy text to deployed rule, explicit representation of exception paths, counterfactual auditability, cross-jurisdictional indexicality, representation of the policy's own incompleteness. *Every absence is a pragmatic-layer absence.* The artifact is pragmatically-loaded by necessity but pragmatically-untyped by convention.

**Recent academic work the lens highlights.**
- *Black & Dimitrov* (AIES 2022, arXiv 2210.02516), "Equalizing Credit Opportunity in Algorithms: Aligning Algorithmic Fairness Research with U.S. Fair Lending Regulation." The cleanest articulation that the fairness-ML literature is largely disconnected from how Reg B disparate-impact analysis actually runs. **Worth a careful read for Paper 1 framing — same diagnosis (the layer that does the work isn't where the field is looking), different mechanism (here: protected-class proxies; in the project: pragmatic context).**
- *SR 26-2* (Fed, April 2026), superseding SR 11-7. The new guidance expects the **model inventory to be a knowledge graph**, not a spreadsheet; introduces materiality calibration. **The regulator just named the open window the project lands in.** No live infrastructure yet exists to receive a refinement-band artifact in this shape.
- *EU AI Act* (Regulation 2024/1689) requires "meaningful information about the logic involved" for high-risk AI, including credit scoring. The European parallel.

---

## 5. The lens applied to the project's own work

The project has been generating empirical contact with the pragmatic layer without consistently naming it. The lens makes this visible.

**Silence-manufacture (FM #12, OTS-stamped 2026-05-13).** Across the 29-cell FM band corpus, three cells (all 2016Q1) showed *manufactured silence*: variant-A and variant-B build structurally different ε-good bands, each producing an internally-correct vocab-adequacy verdict that *disagrees* with the other. A deployment running only one variant would ratify whichever conclusion the variant supports. This is a pragmatic claim with a receipt — the adequacy verdict is *variant-indexed*, the same artifact yields different conclusions under different contexts of utterance.

**HMDA trimodal-replication MISS (OTS-stamped 2026-05-14).** P-scorecard 0/5 HITs (with 3 N/A). The pre-registered prediction that FM-substrate trimodal saturation phases would generalize to HMDA-RI 2022 fell to two structural reasons: HMDA reorganization decouples from carrier saturation; and the FM-calibrated R²≥0.30 adequacy threshold transferred as a floor on HMDA, structurally suppressing verdict_differs. *The trimodal claim tightens to "FM-substrate-validated," not universal.* This is substrate-indexicality — the same machinery doesn't carry across substrates without explicit substrate-context typing.

**The pre-registration failure pattern itself.** Across the project's recent pre-regs, the dominant failure mode is *uniformity-bet → falsification → tightening-to-indexed-claim*. The pattern is consistent enough that the project memory now flags it as a structural observation: pre-registered predictions assume uniformity; reality is indexed; the failure pattern itself motivates indexicality as a load-bearing typing axis. **The pre-reg failure record is, under this lens, the project's empirical case for naming the layer.**

**H2 — frame-evocation falsification (OTS-stamped today, 2026-05-15).** Three discriminators tested on the FM #12 corpus: R²-proximity (current pipeline proxy), subset-membership (current schema primitive `mandatory_features` as enforcement), frame-coherence (the d-signal's max univariate |ρ| on named features). Predictions: P1 (load-bearing) — frame-coherence outperforms subset-membership by ≥0.10 AUC, prior 0.55. P2 (independent stronger claim) — frame-coherence outperforms R²-proximity by ≥0.05 AUC, prior 0.40. P3 (exploratory, not load-bearing) — silence cells concentrate d on off-regulated-three features, prior 0.30. The pre-reg is the operationalization of *mandatory_features as frame-evocation, not enforcement* — the schema slot's pragmatic re-typing. Result by Sunday; either way it's data on the lens.

**Rashomon-for-term-equivalence (seed; not yet executed).** Take two candidate ontology terms T1, T2. Build four R(ε) bands with features T1-only / T2-only / T1∪T2 / T1∩T2. If all four bands land within ε on a held-out task, the terms are *routing-equivalent for that task*. The Rashomon band *is* the operationalized context-of-utterance — the task, the loss, the data distribution, the modeling tolerance. The novel piece: no commitment to general semantic equivalence, only to *equivalence-for-a-decision*. This is pragmatic-by-construction; it fits as a third leg between alignment and label-equivalence in the analytic toolbox (§3 above).

---

## 6. What this looks like as a tool a banking-ontology collaborator could try

The lens is most useful if it changes what someone *does*, not just what they think. Three concrete suggestions:

**(a) Apply the lens to one existing artifact you maintain.** Pick a bank glossary, decision table, or data-dictionary mapping. For each entry, ask: *what substrate does this apply to? what variant of the policy? what temporal/deployment window?* Mark the entries where the answer is "everywhere / always / unspecified." The marked entries are where pragmatic context is smuggled.

**(b) Read FRO with one specific question.** Pull `finregont.com`'s OWL files. Audit whether FRO's hierarchy supports representing *what the regulator has not yet specified* — provisional rules, deliberately-unspecified regions, contested interpretations — vs. only what it has. If yes, FRO is a natural collaborator-substrate. If no, the gap is where the project's contribution lives.

**(c) Treat SR 26-2 as the design brief.** The Fed's expectation that model inventory be a queryable knowledge graph is the closest the regulator has come to specifying the consumer shape of a governance-ontology artifact. The question to bring is: *what pragmatic slots does that knowledge graph need so that an examiner can ask "is this constraint enforced here, for these products, under this regulation?" and get an honest answer?*

The honest scope claim is that policy-constrained Rashomon is **infrastructure that sits between codified policy and supervisory observability**, and it presupposes both endpoints. Neither endpoint is solved in the current landscape. The lens reframes that: the missing endpoints aren't infrastructure gaps in the usual sense; they're pragmatic-layer typings nobody has built because the field's center of gravity is elsewhere.

---

## Map of the space — back matter

The taxonomies the three companion notes develop, summarized for quick reference. Full treatment in `working_notes/ontology-construction-methods-2026-05-15.md`, `working_notes/ontology-analytic-tools-2026-05-15.md`, `working_notes/banking-ontology-landscape-2026-05-15.md`.

**Construction methods.** Five families: top-down formal (BFO/DOLCE/UFO + OWL + METHONTOLOGY/NeOn); bottom-up data-driven (FCA, schema mining, IE-from-text, LegalRuleML pipelines); LLM-assisted (OG-RAG, OntoKG, FrODO, legal-norms Graph-RAG); pattern-based (ODP catalogs + eXtreme Design + SAMOD); hybrid/CQ-driven (Grüninger-Fox, TOVE, NeOn).

**Analytic tools.** Eight legs: consistency checking (DL reasoners, SHACL/ShEx); coverage measurement (CQ-based, corpus-based); alignment/matching (AML, LogMap, BERTMap, OAEI-LLM line); term-equivalence (lexical, taxonomic, distributional/contextual); granularity (OntoMetrics, OOPS!, OQuaRE); completeness diagnostics (PCWA, closure assertions — *thinnest leg*); evolution tracking (OWLDiff, SemaDrift, OnDeT); provenance & traceability (PROV-O, PAV, justification chains).

**Banking landscape.** FIBO (EDMC, MIT, ~2446 classes, OWL 2 DL aspiration / OWL 2 RL practice). Legal-side: LKIF, LegalRuleML, Akoma Ntoso, ELI/ECLI. FRO as the closest policy-codification prior art (single maintainer). Data-dictionary-adjacent: ISO 20022, BIAN v12.0, ACTUS, MISMO v3.6.2, FFIEC Call Report XBRL, HMDA LAR. Recent: Black & Dimitrov (Reg B / fairness-ML gap), SR 26-2 (Fed's KG expectation), EU AI Act.

---

## Anchors and uncertain claims

- The lens itself is the project's framing, planted by Tony 2026-05-15 ("Using pragmatics for ontology construction actually makes sense"). The empirical grounding is in `[[project_silence_manufacture_result]]` and `[[project_hmda_trimodal_result]]`.
- The "completeness as self-representation is genuinely thin" claim is marked *uncertain* in the companion analytic-tools note: literature is fragmented; we have not exhaustively searched.
- FIBO adoption claims sourced from EDMC and Dataversity treated as *floor not ceiling* — no specific bank's production-runtime use of FIBO as live decision substrate has been verified.
- FRO's license is *not stated* on its public page; treat as "open-source-ish, single-maintainer."
- The Rashomon-for-term-equivalence seed is *not yet executed*; included as an illustration of where the lens points, not as a claim of result.
- The SR 26-2 regulatory window framing is the most concrete operational hook for the project, and the most fragile if the supervisory language shifts — read the actual SR 26-2 letter (`references/SR2602a1.pdf`) before relying on it.

