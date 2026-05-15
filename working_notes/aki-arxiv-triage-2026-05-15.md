# Aki's arXiv triage — 2026-05-15

Four papers, all sitting at the **ontology + retrieval/extraction** intersection. Three are RAG-with-ontology variants (2412.15235, 2508.09893, 2509.04696); one is a schema-design / property-routing paper on Wikidata (2604.02618). None of them is on policy-constrained Rashomon sets, model multiplicity, or regulatory observability of underwriting — Aki appears to be pointing at the *infrastructure layer* (how the codified-policy artifact gets built / queried), not the falsification-test layer. The closest match to the project's live seeds is 2508.09893 (regulatory-QA with traceability, a partial cousin of the "receipt" requirement); the strongest *ontology-design-philosophy* contact is 2604.02618 (schema-as-first-class-design-target, intrinsic-relational routing). 2509.04696 reads as an industrial extraction pipeline with limited conceptual contact. 2412.15235 (OG-RAG) is a useful baseline if codification-layer retrieval ever becomes a build target, otherwise orthogonal.

---

## 1. 2508.09893 — RAGulating Compliance: A Multi-Agent Knowledge Graph for Regulatory QA

- **Authors:** Bhavik Agarwal, Hemant Sunil Jomraj, Simone Kaplunov, Jack Krolick, Viktoria Rojkova
- **Year:** 2025 (submitted Aug 13)
- **Core claim:** Regulatory-document QA is improved by extracting subject-predicate-object triplets from regulations, embedding them alongside source text and metadata, and routing QA through an agent pipeline that retrieves at the triplet level. The framing emphasizes factual correctness and traceability for audit use.
- **Method:** Three-stage pipeline — (i) agentic triplet extraction with cleaning/dedup, (ii) unified vector store over triplets + source text + metadata, (iii) orchestrated retrieval-augmented QA with subgraph visualization. "Ontology-free" per the summary (extraction does not commit to a prior schema).
- **Connection to project seeds:** Partial contact with the **pragmatics / receipt** seed: traceability through a triplet-to-source link is a *thin* version of "collapse-with-a-receipt" — a regulator-facing QA answer is justified by a specific triplet and its source span. The contact is weak: the receipt here is provenance (which sentence backed the answer), not the three faces of collapse (data / vocabulary / hypothesis). The paper does not address constraint-typing (relationship / obligation-strength / granularity) or indexicality. Honest read: same neighborhood, different problem — they're building an answerer over regulations; the project is building a falsifier over decisions.
- **Worth a full read?** **Maybe.** Useful as prior art if/when the codification artifact needs a regulator-QA front end; not load-bearing for the current Rashomon / silence-manufacture line.

---

## 2. 2412.15235 — OG-RAG: Ontology-Grounded Retrieval-Augmented Generation for Large Language Models

- **Authors:** Kartik Sharma, Peeyush Kumar, Yunqing Li
- **Year:** 2024 (submitted Dec 12)
- **Core claim:** Grounding RAG retrieval in a domain ontology — by building a hypergraph over documents whose hyperedges are anchored to ontology concepts — improves fact recall (+55%) and response correctness (+40%) on fact-intensive domains (healthcare, legal, agricultural, journalism).
- **Method:** Hypergraph document representation with ontology-anchored knowledge clusters; an optimization step retrieves a minimal hyperedge set as LLM context. Evaluated across four LLMs.
- **Connection to project seeds:** **No direct connection.** The ontology here is an *input* (assumed given for the domain) used to organize retrieval; the project's ontology-design-philosophy seed is about how to *construct* a constraint-typing ontology that represents its own incompleteness and carries indexicality slots. OG-RAG is silent on constraint-types ≡ obligation-graph, on empty-chair / relational balance, and on rung-4 cross-jurisdiction. It might become relevant *downstream* if a codified-policy ontology is in place and one wants to retrieve over policy documents using it, but that's a build-time consumer, not a conceptual contributor.
- **Worth a full read?** **No** (skim only). Decent RAG engineering, but it answers a different question than the project asks. Keep on a "if we ever build a retrieval layer over codified policy" shelf.

---

## 3. 2509.04696 — ODKE+: Ontology-Guided Open-Domain Knowledge Extraction with LLMs

- **Authors:** Samira Khorshidi, Azadeh Nikfarjam, Suprita Shankar, Yisi Sang, Yash Govind, Hyun Jang, Ali Kasgari, Alexis McClimans, Mohamed Soliman, Vishnu Konda, Ahmed Fakhry, Xiaoguang Qi
- **Year:** 2025 (submitted Sep 4)
- **Core claim:** A production-grade system extracts and ingests open-domain facts from the web at high precision (98.8%), processing 9M Wikipedia pages and adding 19M high-confidence facts across 195 predicates, with up to 48% overlap with third-party KGs.
- **Method:** Five-component pipeline — Extraction Initiator (find missing facts), Evidence Retriever (gather sources), hybrid Knowledge Extractors (pattern rules + LLM ontology-prompting), Grounder (validate), Corroborator (rank). Ontology is used as a prompting prior for the LLM extractor.
- **Connection to project seeds:** **Essentially none.** This is industrial KG-population infrastructure for general-knowledge Wikidata-style facts. The "ontology-guided" framing is a prompting tactic, not a design philosophy. No contact with constraint-typing, premature-collapse, or pragmatics/indexicality. If the project ever needed to populate a banking-knowledge KG from filings/regulations at scale, this would be a reference point for *pipeline architecture*, but it doesn't speak to anything currently load-bearing.
- **Worth a full read?** **No.** Note the precision/recall numbers (98.8% precision, 48% overlap) as a benchmark if extraction ever shows up on the roadmap; otherwise skip.

---

## 4. 2604.02618 — OntoKG: Ontology-Oriented Knowledge Graph Construction with Intrinsic-Relational Routing

- **Authors:** Yitao Li, Zhanlin Liu, Anuranjan Pandey, Muni Srikanth
- **Year:** 2026 (submitted Apr 3)
- **Core claim:** Schema design for large KGs should be a first-class artifact for *ontology analysis and downstream use*, not a byproduct of construction. "Intrinsic-relational routing" classifies properties and routes each to an appropriate schema module; the result on the Jan 2026 Wikidata dump is a 34.0M-node / 61.2M-edge property graph across 38 relationship types with 93.3% category coverage and 98.0% module-assignment among classified entities. Five validation applications including ontology analysis, entity disambiguation, and LLM-guided extraction.
- **Method:** Property-graph schema with declarative modules; intrinsic-relational routing as the classification mechanism; portable across storage backends. The abstract is light on what "intrinsic-relational" technically means — whether it's structural (graph-topological) or semantic (predicate-meaning-based) is **unclear from the abstract alone**.
- **Connection to project seeds:** **Strongest contact of the four, with the ontology-design-philosophy seed.** Two specific points:
  - "Schema as first-class design target, not construction byproduct" rhymes with the project thesis that the *codification artifact* (not the model output) is the durable infrastructure. Whether they share the **B≡C / constraint-types-as-obligation-graph** intuition cannot be told from the abstract.
  - Routing properties to modules is a *typing* move — possibly adjacent to the (relationship, obligation-strength, granularity) typing the project wants. But: their typing is over property-relations in Wikidata, not over governance constraints, and the abstract does not mention obligation-strength, deontic typing, or self-incompleteness. So the contact is *structural-analogy*, not *concept-sharing* — easy to over-read.
  - **No** visible contact with premature-collapse-with-a-receipt, indexicality slots, or rung-4 cross-jurisdiction. The 38-relationship-types number is suggestive (do they treat the type system as closed or extensible?) but the abstract doesn't say.
- **Worth a full read?** **Yes** — but with a sharp question in hand: "does 'intrinsic-relational routing' do typing work that maps onto deontic / obligation-strength typing, or is it a structural-only construct?" If the former, this is a serious reference; if the latter, it's a sibling-with-different-goals.

---

## Cross-paper read

Aki has handed over four papers that all live one rung *below* the project's conceptual layer — they're about how to *build* and *query* ontology-backed knowledge artifacts, not about whether a particular constraint vocabulary is adequate to a particular decision (the silence-manufacture / variant-indexicality question). If the project's "codification-as-infrastructure" long arc becomes a build target rather than a research target, this set is roughly the right reading list to start from, with 2604.02618 (OntoKG) as the most-interesting and 2508.09893 (RAGulating Compliance) as the most-domain-adjacent. None of them obviously falsifies, sharpens, or competes with the Rashomon-side of the project. Recommend a full read of 2604.02618 with the specific routing-mechanics question above; skim 2508.09893 for the traceability design; shelve the other two.
