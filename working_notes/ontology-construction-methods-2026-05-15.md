# A Map of Ontology-Construction Methods, with Governance-Domain Failure Modes

Prepared 2026-05-15 as a "map of the space" to share with Aki before our Monday discussion. Goal is positioning, not ranking: where existing methods land, where they reliably break under evolving / contested / auditable conditions, and where a governance-specific construction method could fill gaps all five families share.

Scope: survey, not literature review. Citations point to canonical or representative work; coverage is uneven where families differ in maturity. Uncertain claims marked.

---

## 1. Top-down formal ontology engineering

**Description.** Start from logical commitments — a foundational ontology, a description-logic formalism (OWL 2 DL), a reasoner. Domain modeling slots into upper-level scaffolding; methodologies prescribe lifecycle stages (specification, conceptualization, formalization, implementation, maintenance).

**Representative anchors.** OWL 2 DL; Protégé; HermiT / Pellet / ELK; SPARQL. Foundational ontologies: BFO (realist; IOF-selected; ISO/IEC 21838-2), DOLCE (descriptive; 21838-3 CD), SUMO, UFO (used in OntoUML / enterprise modeling). Methodologies: METHONTOLOGY (Fernández-López, Gómez-Pérez & Juristo 1997), NeOn (Suárez-Figueroa et al. 2012 — scenario-based, supports ontology *networks*), On-To-Knowledge. Community discipline: OBO Foundry (biomedical) — open, common syntax, unambiguous relations, versioned, bounded scope.

**Strengths.** Logical guarantees you can actually run a reasoner over. Strong interoperability when communities converge on a common upper level (OBO is the existence proof). Methodologies produce defensible process artifacts.

**Weaknesses for governance.** OWL has no native temporal/versioning semantics — when a regulation amends a definition mid-lifecycle, the right reaction (revise the class? mint a new one? add a temporal qualifier?) is not prescribed, and DL reasoners cannot represent "this axiom held 2018-Q3 through 2022-Q1" (uncertain: I have not seen a widely adopted OWL temporal-versioning pattern that survives a real bank's change cadence). Foundational ontologies are mutually incompatible — BFO's relational-quality treatment violates DOLCE's inherence principle, mereology differs across BFO/DOLCE/UFO — and the choice of upper ontology is invisible to downstream consumers. There is no canonical pattern for "this region is deliberately unspecified pending regulatory clarification." PAV / PROV-O exist for provenance but layer on top; the design rationale itself lives in METHONTOLOGY documentation that is human-readable, not machine-queryable alongside the axioms.

**Cost barrier.** High; trained ontologist + domain experts; foundational-ontology fluency rare; large METHONTOLOGY projects generate documentation overload.

---

## 2. Bottom-up data-driven extraction

**Description.** Induce structure from existing artifacts — relational schemas, text corpora, transaction logs, regulations — rather than positing it. Output is typically a draft concept hierarchy or KG that an ontologist prunes and aligns.

**Representative anchors.** Formal Concept Analysis (Ganter & Wille); Cimiano's *Ontology Learning from Text* (FCA + Relational Concept Analysis over corpus-derived incidence). Schema mining from RDBMS. Open IE / NER + relation extraction (Stanford OpenIE, REBEL, transformer extractors over legal text — CRIKE, Lenci et al. CEUR Vol-321). Legal-text → LegalRuleML / SHACL pipelines. Process mining (van der Aalst) over event logs to recover de facto workflow ontologies.

**Strengths.** Cheap to start; surfaces what an institution *actually does* (transaction logs) versus what it claims to do (policy text). FCA gives a mathematically principled hierarchy without upper-ontology commitment. Useful for discovery and gap-finding.

**Weaknesses for governance.** Output is a corpus snapshot — re-running on a new regulation produces a new lattice, and mapping last quarter's concepts to this quarter's is a separate unsolved alignment problem. Extraction *collapses disagreement*: where two policy authors used different terms for the same concept (or the same term for different concepts), the extractor returns one outcome and silently buries the contestation. This is the failure pattern the parent project's [[project_silence_manufacture_result]] documents on FM data. Bottom-up methods cannot represent "the corpus does not cover this case" — the lattice is, by construction, what the data says exists. Provenance is decent at the source-document level (you can cite the paragraph) and poor at the modeling-decision level (why was this term lifted to a class versus a property?).

**Cost barrier.** Medium to start, high to make production-grade; extractors are noisy and FCA lattices over realistic corpora explode combinatorially.

---

## 3. LLM-assisted construction

**Description.** LLMs as drafters (propose classes/relations from text), as competency-question generators, as evaluators (does the ontology answer these CQs?), or as the retrieval substrate. The 2024-2026 wave moves from "LLM helps draft OWL" to "ontology grounds LLM retrieval."

**Representative anchors.** CQ-driven drafting: Memoryless CQbyCQ and Ontogenia prompting strategies; FrODO (Mongiovì et al., arXiv:2206.02485); RAG-based CQ generation (Antia & Keet, arXiv:2409.08820). End-to-end: fusion-jena's automatic-KG-creation-with-LLM; OntoKG (arXiv:2604.02618, intrinsic-relational routing); LLM-driven enterprise KG construction (arXiv:2602.01276). Ontology-grounded retrieval: OG-RAG (Microsoft, EMNLP 2025; arXiv:2412.15235) — hypergraph of ontology-grounded fact clusters; reports +55% fact recall, +40% correctness vs. baseline RAG. Regulation-specific: Ontology-Driven Graph RAG for Legal Norms (arXiv:2505.00039 — hierarchical, temporal, deterministic); AEC3PO (Accord, 2024, digital building permits).

**Strengths.** Order-of-magnitude faster initial drafting. Lowers the OWL-fluency barrier for domain experts. CQ-generation unblocks a long-standing bottleneck in Grüninger-Fox. OG-RAG-style architectures let an ontology *constrain* a generative system rather than just describe one.

**Weaknesses for governance.** The LLM's pretraining cutoff is a hidden version pin — regulator amends Reg B in Q1, model was trained before that, the ontology drift is silent. LLMs flatten contested terminology by design (next-token likelihood prefers dominant usage); two disagreeing policy authors become one synthesized "consensus" definition — the [[project_premature_collapse_frame]] failure running at construction layer. Hallucinated classes look identical to grounded ones in OWL output, and LLMs do not flag "I don't know what this term means in your jurisdiction." Provenance is the weakest spot: even with RAG, the chain from regulation paragraph → extracted axiom → human accept/reject is rarely captured in machine-checkable form (cf. Meyman, *Versioned Meaning*, SSRN 5918182).

**Cost barrier.** Low to start, high to validate for a regulated domain; validation tooling is essentially a research problem.

---

## 4. Pattern-based (Ontology Design Patterns)

**Description.** Compose pre-vetted templates that solve recurring modeling problems — *Participation*, *Time Interval*, *Role*, *Information Realization*. Distinct from foundational ontologies: ODPs are smaller, parameterizable, often pre-axiomatized.

**Representative anchors.** Catalogs: ontologydesignpatterns.org; Manchester ODP catalog; NeOn ODP repository. Methodologies that depend on patterns: eXtreme Design (Blomqvist et al., CEUR Vol-516 — pair design with CQs as requirements, ODPs as solution units); SAMOD (Peroni 2016 — TDD-inspired three-step iteration). Pattern languages: OPLa annotations for how patterns combine.

**Strengths.** Reuse compresses design time and propagates good axiomatization. Pattern instantiation is *legible* — "this is the Role pattern" beats re-deriving the axioms. SAMOD/XD give agile cadence that survives stakeholder review cycles.

**Weaknesses for governance.** Patterns are static; revising a pattern cascades through every ontology that instantiated it, with no tooling to support the migration. Pattern *selection* presupposes a shared problem vocabulary — if the dispute is "is this fact a Role or a Quality?" the catalog cannot resolve it, it provides both. Catalogs are themselves incomplete and embed metaphysical commitments — realist (BFO-aligned) ontologies report trouble integrating NeOn patterns. A biomedical survey of 8 widely used ontologies recovered only 5 of 69 catalog patterns (PMC3540458), suggesting catalog patterns are often too specific to actually recur. Pattern *use* is auditable ("I applied pattern X v.2"); pattern *non-use* and deviations are not.

**Cost barrier.** Medium; lower than top-down-from-scratch, requires catalog fluency and a senior reviewer.

---

## 5. Hybrid / iterative (CQ-driven, stakeholder-elicited, agile)

**Description.** Drive construction from *use* rather than formalism: elicit competency questions from stakeholders, build the smallest ontology that answers them, iterate. Output is whatever shape passes the CQ test bench — OWL, RDFS, SKOS, mixed.

**Representative anchors.** Grüninger & Fox (1995), *Methodology for the Design and Evaluation of Ontologies*; TOVE project (first CQ formalization). Agile family: XD, SAMOD, OD-101 (Noy & McGuinness — the de facto Protégé tutorial methodology). Stakeholder elicitation: participatory ontology design (Vrandečić et al.); NeOn "non-ontological resource reuse" scenarios.

**Strengths.** CQs are auditable artifacts in their own right — they document what the ontology was *supposed* to do, a partial answer to the auditability problem. Iterative methods accommodate ongoing requirement change better than waterfall. Aligns naturally with how regulators frame examination questions ("can your system answer: which loans flagged for second-review involved a manual override?").

**Weaknesses for governance.** CQs evolve too; there is no canonical method for *retiring* a CQ when regulation changes, and old CQs drift into measuring obsolete requirements. The method assumes CQ consensus before formalization — in contested-vocabulary domains this often fails, with disagreement migrating from "what's the class hierarchy" to "what's the right question" (useful migration, but the methodology offers no resolution beyond "more workshops"). CQ test benches are by definition the *known* questions — no built-in slot for "questions the regulator hasn't asked yet but might." Provenance is better than most — CQs, user stories, iteration logs — but the trail typically lives in wiki / Jira form, not co-located with the axioms.

**Cost barrier.** Medium; lighter ontologist load, heavier stakeholder time. Stakeholder availability is the typical bottleneck in regulated industries.

---

## Cross-cutting analysis

**What does an ad-hoc "smart bank team" actually produce?** Almost certainly some hybrid of (5) and (1) without naming either. The artifact tends to be: a glossary or data dictionary (rarely OWL — more often JSON Schema, a SQL schema with extensive comments, or a Confluence page with linked tables); a small set of derived rules in whatever the policy-engine DSL is (drools, business-rule tables, SQL views, Python); and an informal set of "questions the team should be able to answer" that functions as latent CQs. A senior architect imposes top-down structure; juniors and analysts extend bottom-up from incidents and new product launches. Usually no foundational-ontology commitment, no DL reasoner in the loop, no formal versioning beyond git, and provenance is "ask whoever last touched it." The artifact is locally coherent, globally fragile under regulatory change, and structurally unable to represent its own incompleteness. This is not a criticism — it is the rational equilibrium for a team optimizing for shipping, given the cost barriers in (1)-(4). The relevant question is what we can offer that *composes with* this ad-hoc artifact rather than asks the team to replace it.

**What is consistently missing across all five families?** Four capabilities recur as gaps, and they are the same gap viewed from four angles:

1. *First-class representation of the ontology's own incompleteness.* All five can represent what the ontology contains; none has a canonical machine-queryable construct for "deliberately unspecified," "contested between authors A and B," or "provisional pending clarification." Closest existing: PAV/PROV-O for authorship, owl:deprecated for retired terms, SKOS notes — none reasoner-actionable.
2. *Temporal/regulatory versioning as a first-class semantic, not metadata.* The Graph-RAG-for-legal-norms work (arXiv:2505.00039) gets closest with explicit Temporal Version entities, but this is a domain-specific KG schema, not a general construction discipline. "When did this constraint become binding, when does it cease, what supersedes it" is everywhere relegated to annotations.
3. *Contested-term representation.* No family treats expert disagreement as a structural feature. Disagreement is either resolved before formalization (1, 4, 5), silently collapsed by extraction (2, 3), or shuffled into documentation (all five). The parent project's pragmatics-in-linguistics framing ([[project_pragmatics_linguistics_lens]]) — explicit context-of-utterance slots, variant-indexed verdicts — is one approach the literature has not yet offered.
4. *Construction-time provenance bound to axioms.* Provenance ontologies exist; the discipline of binding every axiom to (regulation paragraph, modeling decision, human approver, supersession edge) does not. Meyman's *Versioned Meaning* (SSRN 5918182) is one of the few explicit treatments and is still a position paper, not a tooled methodology.

A governance-specific construction discipline could position itself as *the methodology that treats incompleteness, time, disagreement, and provenance as construction primitives* rather than as documentation afterthoughts.

---

## Sources

- METHONTOLOGY / NeOn: Suárez-Figueroa et al., *NeOn Methodology for Building Ontology Networks* (UPM 2010); Fernández-López et al. (1997).
- Foundational ontologies: Keet, *Introduction to Ontology Engineering* (LibreTexts ch. 6-7); BFO 2.0 spec; ISO/IEC 21838-2 (BFO), 21838-3 (DOLCE CD).
- OBO Foundry: Smith et al., *Nature Biotechnology* 25:1251 (2007); Jackson et al., *Database* 2021.
- FCA / legal: Cimiano (2006); Lenci et al., CEUR Vol-321 paper 7; CRIKE.
- LLM-assisted: OG-RAG (arXiv:2412.15235, EMNLP 2025); legal-norms Graph RAG (arXiv:2505.00039); FrODO (arXiv:2206.02485); Antia & Keet (arXiv:2409.08820); OntoKG (arXiv:2604.02618).
- ODPs: ontologydesignpatterns.org; Blomqvist et al. eXtreme Design (CEUR Vol-516); biomedical pattern-uptake survey (PMC3540458).
- Grüninger-Fox / TOVE: Grüninger & Fox (1995); *The Role of Competency Questions in Enterprise Engineering*.
- SAMOD: Peroni (2016), essepuntato.it/samod.
- Versioning / provenance: PAV (pav-ontology.github.io); Meyman, *Versioned Meaning*, SSRN 5918182.
- Compliance: AEC3PO (Accord, 2024); Gallina et al., *J. Software: Evolution and Process* 2025.
