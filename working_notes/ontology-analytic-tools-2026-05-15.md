# Analytic tooling for existing ontologies — survey
2026-05-15. Audience: Aki (banking-ontology collaborator), Monday packet.
Scope: tools that **analyze** an ontology you already have. Construction tools, editors, and learners are out of scope except where they double as analyzers. Special attention to whether each tool requires a formal OWL/RDF artifact or can operate on ad-hoc structures (spreadsheets, glossaries, controlled-vocabulary documents, typed-graph dumps).

## 1. Consistency checking

**Task.** Given an ontology, decide whether the axioms are satisfiable (no class is forced to be empty by contradiction) and whether asserted individuals violate class definitions. For RDF data graphs, the analogous task is shape conformance: does the data instance match the structural constraints declared for it.

**DL reasoners.** [HermiT](http://www.hermit-reasoner.com/), [Pellet/Openllet](https://github.com/Galigator/openllet), [ELK](https://github.com/liveontologies/elk-reasoner), [Konclude](https://www.derivo.de/en/produkte/konclude). HermiT and Konclude lead in ORE-class benchmarks for consistency and classification; ELK is restricted to the OWL 2 EL profile but is near-linear on big terminologies (SNOMED-scale). Pellet/Openllet uniquely supports SWRL-rule reasoning and explicit justification generation.

**Shape validation.** [SHACL](https://www.w3.org/TR/shacl/) (W3C Recommendation, 2017) and [ShEx](https://shex.io/). SHACL is the standard; both express cardinality, datatype, pattern, and structural constraints on RDF graphs. Tooling: TopBraid SHACL, pySHACL, RDF4J, GraphDB.

**Input requirement.** Strict. DL reasoners need OWL DL syntax (Functional, Manchester, RDF/XML, Turtle/OWL). SHACL/ShEx need RDF and a shapes graph. An ad-hoc spreadsheet ontology does **not** run through these; it must first be lifted to RDF/OWL, which is itself a nontrivial modelling step.

**Cost/expertise.** Moderate-to-high. Running a reasoner is one command; reading its output (especially an unsatisfiability or a SHACL violation report) requires DL/SHACL fluency.

**Failure mode.** Silent over-acceptance under the open-world assumption (see §6). A consistent ontology can still be drastically incomplete or wrong — consistency is a floor, not a ceiling. Reasoners also will not flag *what the ontology fails to say*.

## 2. Coverage measurement

**Task.** Decide whether the ontology covers its intended scope, by two routes: (a) competency questions (CQs) — can the ontology answer the natural-language questions stipulated as in-scope? (b) corpus coverage — what fraction of domain terms drawn from a reference corpus are present?

**CQ-based.** [CQChecker](https://www.researchgate.net/publication/220940073) and successors translate controlled-NL CQs to SPARQL-OWL and check whether the ontology answers them ([Keet & Lawrynowicz 2016, SAC](https://www.sciencedirect.com/science/article/abs/pii/S1570826819300617); [Ren et al. taxonomy 2014](https://ieeexplore.ieee.org/document/6690745); [ROCQS repository, 2024](https://arxiv.org/html/2412.13688v1) — 438 annotated CQs and a 5-type model: Scoping, Validating, Foundational, Relationship, Metaproperty).

**Corpus-based.** [Brewster et al. corpus-fit](https://www.researchgate.net/publication/262292931); [Automated Ontology Evaluation, WebConf 2023](https://dl.acm.org/doi/abs/10.1145/3543873.3587617) (NER + domain-tuned coverage). Term-extraction tools (Text2Onto, ATR systems — see [Tran et al. ATR survey, 2023](https://arxiv.org/pdf/2301.06767)) produce candidate term lists that an existing ontology is then scored against.

**Input requirement.** CQ tools want OWL + SPARQL-OWL. Corpus tools work on **any** lexicalized concept list — names + synonyms in a spreadsheet are enough to compute term-overlap. This is the cheapest way to get an analytic signal off an ad-hoc artifact.

**Cost/expertise.** CQ formalization is the dominant cost (it is itself a modelling task). Corpus coverage is low-cost if a corpus exists.

**Failure mode.** CQs cover what the modellers *thought to ask*; corpus coverage is bounded by the corpus's own representativeness. Neither finds an absent concept whose absence nobody noticed.

## 3. Ontology alignment / matching

**Task.** Given two ontologies, produce a mapping between their entities (classes, properties, individuals). The Ontology Alignment Evaluation Initiative ([OAEI 2024](https://oaei.ontologymatching.org/2024/), [2025](https://oaei.ontologymatching.org/2025/)) is the annual benchmark.

**Classical systems.** [AML](https://github.com/AgreementMakerLight/AML) (AgreementMakerLight — lexical + structural + background-knowledge), [LogMap](https://github.com/ernestojimenezruiz/logmap-matcher) (lexical indexation + logic-based repair, scales to LargeBio), [Anchor-Flood](https://www.researchgate.net/publication/220853078) (anchor-driven local matching). LogMap remains the most-cited baseline; it is one of the few systems that guarantees a *coherent* alignment (no induced unsatisfiability).

**Neural / LLM-based.** [BERTMap](https://github.com/KRR-Oxford/BERTMap) (AAAI 2022) fine-tunes BERT on ontology lexical context. [LLMs4OM, ESWC 2024](https://2024.eswc-conferences.org/wp-content/uploads/2024/05/77770022.pdf); [MILA / prioritized-DFS, 2025](https://arxiv.org/abs/2501.11441); [Agent-OM, Monash 2024–25](http://om.ontologymatching.org/2025/papers/); [LogMap-LLM / LLM-as-oracle, Jimenez-Ruiz 2025](https://ernestojimenezruiz.github.io/assets/pdf/llm-oa-oracles-2025.pdf); [OAEI-LLM hallucination benchmark](https://arxiv.org/abs/2409.14038). 2025 OAEI Bio-ML: BioGITOM, BERTMap, and LogMap-LLM each led on at least one task — no single winner.

**Input requirement.** Classical matchers want OWL. LLM-based matchers degrade gracefully — a labelled concept list with parent/child links is often enough. This makes alignment one of the more ad-hoc-friendly capabilities.

**Cost/expertise.** Moderate. The OAEI MELT platform handles wrapping. LLM-based variants add token cost and require hallucination guarding (see OAEI-LLM benchmark).

**Failure mode.** Polysemy and label collisions; cultural/regulatory framing differences not visible in labels; structural alignments that flip semantics ("loan" as obligation vs. as cash-flow).

## 4. Term-equivalence detection

**Task.** Inside or across ontologies, decide whether two entities denote the same thing. This is alignment's atomic operation, but also surfaces inside a single ontology (duplicate concepts, hidden synonyms, label drift).

**String / lexical.** Edit distance, n-gram, stemmed match. Cheap, brittle.

**Taxonomic.** [Wu–Palmer](https://aclanthology.org/P94-1019.pdf) over WordNet (depth-weighted LCS); Resnik IC-similarity. Requires a backbone taxonomy.

**Distributional / contextual.** Word2Vec / fastText (label-level); SBERT, OpenAI/Anthropic text embeddings (definition-level); ontology-tailored embeddings such as [OWL2Vec*](https://github.com/KRR-Oxford/OWL2Vec-Star) and [OWL2Vec4OA, 2024](https://arxiv.org/pdf/2408.06310).

**Input requirement.** Lexical/embedding methods work directly on labels and (better) on definitions; an ad-hoc CSV is sufficient. Wu–Palmer requires a hierarchy. Embedding-based methods require care about what "same" means — they conflate near-synonyms, hyponyms, and topically-related terms unless thresholded carefully.

**Cost/expertise.** Low for embeddings (one API call per term); high for principled threshold setting and downstream curation.

**Failure mode.** Embeddings tend to over-merge: "borrower" and "co-borrower" come back highly similar but are policy-distinct; "default" and "delinquency" too. The assumption "same label ⇒ same concept" is the largest source of silent merging in lexical pipelines.

## 5. Granularity / consistency analysis

**Task.** Structural diagnostics on the class hierarchy: depth, breadth, sibling balance, tangledness, modularity, redundancy.

**Tools.** [OntoMetrics](https://ontometrics.informatik.uni-rostock.de/) (32 metrics across 7 categories — Schema, Knowledge-base, Class, Inheritance, Relationship, Axiom, Graph) and its successor [NEOntometrics](https://drops.dagstuhl.de/storage/08tgdk/tgdk-vol002/tgdk-vol002-issue002/html/TGDK.2.2.2/TGDK.2.2.2.html). [OOPS!](https://oops.linkeddata.es/) catalogues 41 pitfalls (e.g., P03 "creating unconnected ontology elements", P11 "missing domain or range in properties", P21 "using a miscellaneous class") graded critical/important/minor. [OQuaRE](https://sele.inf.um.es/oquare/) maps SQuaRE software-quality criteria onto ontologies. For biomedical-style depth/breadth issues, see [Ochs et al. 2011](https://pmc.ncbi.nlm.nih.gov/articles/PMC3041335/) on granularity differences across ontologies and [Alterovitz et al. 2010, PLOS Comp Bio](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1001055) ("Bigger or Better?").

**Input requirement.** OntoMetrics and OOPS! want OWL/RDF. The metrics themselves (depth distributions, sibling counts) can be computed on any tree-structured CSV with a parent/child column — but the off-the-shelf tools won't ingest that.

**Cost/expertise.** Low for running, moderate for interpreting. Many metrics correlate with size more than with quality.

**Failure mode.** A "well-balanced" ontology by these metrics can still be wrong. The metrics are descriptive; thresholds are conventional, not theoretically grounded. OOPS! catches surface pitfalls but says nothing about semantic adequacy.

## 6. Completeness diagnostics

**Task.** Flag what an ontology is *not* covering. Under the open-world assumption (OWA) that OWL adopts, the absence of an assertion is not a negation — so reasoners cannot, in general, tell you "this is missing".

**State of practice.** Partial-closed-world / closed-world relaxations: PCWA via completeness assertions ([Razniewski et al. on completeness statements](https://www.researchgate.net/publication/354646747)); the SWRL or SHACL closure-axiom pattern (declare a class's properties exhaustive). Debugging surveys: [Lambrix & Dragisic, JDIQ 2023, "Completing and Debugging Ontologies"](https://dl.acm.org/doi/full/10.1145/3597304); earlier [arXiv survey 2019](https://arxiv.org/pdf/1908.03171). Knowledge-graph completion via embeddings ([DELE 2024](https://arxiv.org/html/2411.01574v1)) addresses missing *facts* but not missing *vocabulary*. Recent work on ontology gaps in semantic parsing ([2024](https://arxiv.org/html/2406.19537v1)) treats unmodelled-concept detection as out-of-distribution detection on natural-language queries — closer to what governance needs, but still input-driven.

**Input requirement.** Mixed. PCWA needs a formal ontology. Corpus-and-CQ gap-finding (§2) works on lexical artifacts.

**Cost/expertise.** Very high. Writing the right completeness assertions is roughly equivalent to writing the missing axioms. Most teams skip it.

**Failure mode (the central one).** *Tools detect known unknowns, not unknown unknowns.* Every method above presupposes some external reference — a corpus, a CQ list, a closure assertion, a parallel ontology, a downstream query distribution — against which absence is measured. No tool in the standard inventory detects what an ontology fails to model when *the analyst is unaware the dimension exists*. (Uncertain claim: marked uncertain because the literature is fragmented; we have not found a tool that contradicts this characterization, but absence of evidence is not evidence of absence.)

## 7. Evolution tracking

**Task.** Compare versions of an ontology; characterize what changed and whether downstream semantics drift.

**Tools.** [OWLDiff](https://owldiff.sourceforge.net/) (axiom-level add/remove); [PROMPTDIFF](https://www.researchgate.net/publication/221603977) (fixed-point structural diff, Stanford); [SemaDrift](https://www.sciencedirect.com/science/article/abs/pii/S1570826818300258) plug-in for Protégé (hybrid identity-and-morphing-based concept stability across versions); [OnDeT, Ontology Development Tracker](https://github.com/) for Git-hosted ontologies with N-way temporal comparison. Bioportal and OBO Foundry track deprecation via `owl:deprecated` and `obo:IAO_0100001` (term replacement).

**Input requirement.** Tooling expects OWL/RDF. For ad-hoc artifacts (spreadsheet versions), Git + a diff of the underlying CSV gives the rows-changed signal but not the semantic-drift signal.

**Cost/expertise.** Low to run, moderate to interpret. SemaDrift's stability rankings are the most interesting output for governance use.

**Failure mode.** Structural diff cannot see semantic drift when labels stay constant (the "same word, different concept" failure that is endemic in policy text).

## 8. Provenance & traceability

**Task.** Record where each entity in the ontology came from (source document, decision, author, version) and reconstruct why a reasoner inferred what it inferred.

**Provenance schemas.** [PROV-O](https://www.w3.org/TR/prov-o/) (W3C Rec 2013; OWL2 encoding of the PROV-DM); [PAV](https://pmc.ncbi.nlm.nih.gov/articles/PMC4177195/) (Provenance/Authoring/Versioning, lightweight extension); domain extensions for scientific workflows. Justification chains ("minimal entailing subsets") are produced by Pellet/Openllet's `explain` and by the [OWL Explanation Workbench](https://github.com/matthewhorridge/owlexplanation). Protégé exposes these in its UI.

**Input requirement.** PROV-O annotations can be added to *any* RDF artifact, including a lifted spreadsheet. Justification chains require OWL + reasoner.

**Cost/expertise.** Annotation discipline is the dominant cost, not tooling. Justification interpretation needs DL fluency.

**Failure mode.** Provenance covers axiom origin, not modelling-decision rationale ("why this constraint, not the alternative"). Reasoner justifications explain *that* an entailment holds, not *whether the entailment is desirable*.

---

## Cross-cutting analysis

**Where tools are thinnest, governance-relevant edition.** Three places.

*Completeness diagnostics (§6) are the weakest leg.* Every tool we found measures coverage against a *given* reference — a corpus, a CQ list, a closure axiom, a sibling ontology. None of them confronts the unknown-unknown: dimensions of the domain that the modellers were not equipped to see. For regulatory contexts where the harms-of-omission story is the load-bearing one (silence-manufacture, [[project_silence_manufacture_result]]), this is the gap. PCWA gives you a *vocabulary* for asserting completeness, not a *method* for finding where assertion is warranted.

*Semantic-drift detection on ad-hoc artifacts (§7).* SemaDrift and friends require OWL versions. Most banking ontologies, by Aki's likely starting point, live in spreadsheets and policy documents. There is no off-the-shelf tool that watches a corpus of policy PDFs and flags concept drift; the closest are general-purpose embedding-drift detectors borrowed from ML monitoring, which are not policy-aware.

*Provenance of modelling decisions (§8).* PROV-O captures *who recorded what when*. It does not capture *which alternatives were considered and rejected, and why*. The pragmatic-annotation layer that [[project_pragmatics_linguistics_lens]] argues for is exactly here — and nothing in the standard inventory provides it.

**The completeness question, specifically.** Does any existing tool address "how does an ontology represent its own incompleteness"? The literature has *closure assertions* (you state which slots are complete) and *gap detection from queries* (an OOD signal on query-time inputs). Neither is a method for an ontology to carry, *in its own structure*, a representation of where its vocabulary thins out. This appears to be a genuine gap rather than an oversight on our part — though we mark this *uncertain*, because the closure-relevant literature is fragmented across DL, KG-completion, and information-systems-ontology communities and we have not exhaustively searched the last.

**Small flagged thought — Rashomon-as-equivalence-detector.** Speculative. Standard term-equivalence detection (§4) asks "do labels/contexts/embeddings agree?" An alternative would be: train a Rashomon set of predictive models for a downstream task using ontology entity A vs. entity B as inputs, and call A ≡ B if the ε-band of near-equivalent models is invariant under the substitution. This is a *functional* equivalence test ("equivalent for the decision at hand") rather than a *referential* one. It would fit between §3 alignment and §4 equivalence as a third leg: not lexical, not semantic-via-embedding, but task-grounded. Failure mode would be the obvious one — it would call distinct concepts equivalent whenever the downstream task doesn't distinguish them (which for some governance settings is the *desired* answer, and for others is exactly the wrong one). Worth a paragraph of follow-up, not a build.

**Bottom line for the Aki packet.** The map has well-developed legs (reasoners, alignment, structural metrics, provenance schemas) and underdeveloped legs (completeness-as-self-representation, ad-hoc semantic-drift, decision-rationale provenance). Position our work on the underdeveloped side; position the developed-side tools as complements he can adopt now.
