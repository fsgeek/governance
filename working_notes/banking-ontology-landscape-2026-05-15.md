# Banking / Finance / Legal-Governance Ontology Landscape

**Prepared:** 2026-05-15. For internal use ahead of the Monday session with Aki.
**Scope:** what state-of-the-art looks like, who maintains what, where ad-hoc bank-internal solutions diverge.
**Caveat:** version numbers and adoption claims are flagged where I cannot verify the primary source. Adoption numbers from vendor pages or trade press are treated as marketing.

---

## 1. FIBO (Financial Industry Business Ontology)

**Maintainer.** EDM Council (Enterprise Data Management Council). Since January 2020 FIBO development has run as an open community process on GitHub at `edmcouncil/fibo`. The Object Management Group (OMG) standardises a subset of FIBO under their finance taskforce; the EDMC community release is the live artifact.

**License.** MIT (per the GitHub repository badge).

**Current version.** The GitHub repository advertises Q1 2026 production (release date April 2026 per the repo's release page). The spec.edmcouncil.org "About FIBO Production" page advertises 2,446 classes across the production modules at this release. *Verified via repo metadata; release notes themselves not fetched here.*

**Modular structure.** Top-level domain folders in the repo:

- **FND** Foundations (the upper ontology: agents, parties, time, places, relations)
- **BE** Business Entities (legal persons, corporations, partnerships, governmental units)
- **FBC** Financial Business and Commerce (markets, exchanges, products and services)
- **SEC** Securities
- **DER** Derivatives
- **LOAN** Loans (commercial, small business, automobile, education, mortgage; includes a `RealEstateLoans/HomeMortgageDisclosureActCoveredMortgages` ontology)
- **CAE** Corporate Actions and Events
- **IND** Indices and Indicators
- **MD** Market Data
- **BP** Business Process

The LOAN domain is the closest to the parent project's substrate. It includes `LoanCore`, `LoanApplications/CreditRiskAssessment`, `MortgageOrigination`, and an HMDA-covered-mortgages submodule. Coverage is "concept and party / contract / obligation"-level, not "tier / policy / decision-procedure"-level — see §6.

**Tooling ecosystem.**

- **Protégé** is the canonical desktop editor. ELK reasoner used for classification; Debug Ontology plugin for coherence checks.
- **GraphDB (Ontotext / Graphwise)** is the most visible commercial triple store with FIBO worked examples; FIBO is typically loaded under the **OWL 2 RL** profile (the EDMC wiki documents this explicitly as the practical reasoning level — OWL 2 DL is too expensive at FIBO's size for routine inference).
- **Hugging Face mirror** (`wikipunk/fibo2023Q3`) exists as a snapshot dataset, illustrating the ML-pipeline use case.
- **FIB-DM** (fib-dm.com): a third-party transformation of FIBO into a relational enterprise data model — its existence is itself evidence that consumers want a non-OWL surface for FIBO.
- No EDMC-hosted public SPARQL endpoint that I could verify. Vendor endpoints exist (Ontotext); these are demos, not infrastructure.

**Adoption — what I can verify vs. what I can't.**

- The EDMC and Dataversity have promoted case studies in an "investment bank, a credit card company, and a credit rating firm" with five projects "in or near production." Firms not named publicly. *Treat as floor, not ceiling.*
- BCBS 239 (risk data aggregation) is the most credible production driver — large G-SIBs use FIBO as vocabulary alignment, often inside an internal data-mesh or master-data layer, rather than as the live inference substrate.
- Most bank uses I can find described publicly are **inspiration / mapping** ("we aligned our internal glossary to FIBO terms") rather than **runtime** ("FIBO ontology drives our decision system"). I cannot confirm any retail-credit decisioning system that uses FIBO as its live policy substrate.

**Known limitations / controversies.**

- **Coverage at the policy/decision layer is thin.** FIBO models *what an instrument is* and *who the parties are* well; it does not natively model *the decision rule a bank applies*, *the documented exception path*, or *the regulator-observable receipt of a decision*. The LOAN module reaches the contract; not the credit-policy DAG.
- **Expressivity / scale tradeoff.** Full FIBO is OWL 2 DL but practical reasoning is OWL 2 RL; sophisticated DL constructs in the FND layer cannot be relied on by downstream consumers. This is well-documented in the EDMC RDF Toolkit wiki.
- **Integration cost.** Vendor and consulting writeups consistently flag legacy data-format mismatch, scarce in-house ontology engineering skill, and organisational change overhead. (These are vendor framings — read sceptically, but they recur.)
- **Open community process** has improved governance since 2020, but the production release cadence is still gated by EDMC member review, which means external contributors hit a wall on anything novel.

---

## 2. Legal / regulatory ontologies

| Standard | What it is | Maintainer | Status |
|---|---|---|---|
| **LKIF-Core** | Legal Knowledge Interchange Format. Upper-ontology of basic legal concepts (norms, roles, legal sources). OWL. | Originally ESTRELLA EU project; now informal maintenance (GitHub: `RinkeHoekstra/lkif-core`). | Stable but not actively maintained. Influence is conceptual, not as live infrastructure. |
| **LegalRuleML** | OASIS XML standard for representing legal rules (deontic operators, defeasibility, temporal/jurisdictional metadata). | OASIS LegalRuleML TC. | Active. A 2024 EU "reporting obligations" specialisation exists (Interoperable Europe). |
| **Akoma Ntoso (AKN)** | XML schema for parliamentary, legislative, judiciary documents. Structural markup of statutes / opinions. | OASIS LegalDocML TC; widely deployed at UN, EU, several national legislatures. | Active and adopted. |
| **ELI** (European Legislation Identifier) | URI scheme + metadata ontology for EU and member-state legislation. | EU Publications Office. | Active; native to EUR-Lex. |
| **ECLI** | Sibling of ELI for case law. | EU. | Active. |

**Overlaps with FIBO.** Essentially none at the schema level: FIBO is the *things being regulated*; LKIF / LegalRuleML / AKN are the *regulations themselves and their structure*. The cleanest bridge attempt is **FRO** (see below).

**Gaps.** LegalRuleML is jurisdiction-neutral by design and leaves the *content ontology* unspecified — you must point at an external ontology (FIBO, a domain ontology) for the terms. None of these standards address *decision-procedure-as-deployed-by-a-supervised-entity* — they address *the law as authored*. The bank-internal "we applied rule X to applicant Y at time T" receipt is not natively modelled.

**Worth flagging.** **FRO** (Financial Regulation Ontology) at finregont.com, maintained by Jurgen Ziemer / Jayzed Data Models. FRO explicitly imports both FIBO (entities) and LKIF (legal expressions) and aligns them, then loads CFR Title 12 (Banking) and Title 17 (Investment Adviser Act) plus USC Titles 12 and 15. The worked example is whether an investment fund must register with the SEC. **License not stated on the public page; treat as "open-source-ish, single-maintainer."** This is the closest published artifact to what a "policy-codification ontology" looks like, and it should be treated as a comparable rather than as competing infrastructure: a single individual maintains it.

---

## 3. Data-dictionary-adjacent standards (not ontologies, but they shape what banks codify)

- **ISO 20022.** Financial messaging metamodel; the lingua franca for payments, securities, FX, trade services. Maintained by ISO TC 68 / SWIFT as Registration Authority. Critical to recognise: ISO 20022 is a *message* standard with an underlying business model, not an ontology — but its concept dictionary is what most banks already have invested in, and BIAN explicitly aligns to it.
- **BIAN** (Banking Industry Architecture Network). Service Landscape v12.0 released late 2024. Expresses banking *service domains* in ArchiMate 3.1 plus UML class/sequence diagrams. Not OWL, but the BIAN metamodel draws on ISO 20022 and BIAN has formally contributed to FIBO. This is the most likely "ontology in disguise" Aki has encountered inside large banks.
- **ACTUS** (Algorithmic Contract Types Unified Standards). 32 parameterised contract types covering essentially all cash-flow instruments. Maintained by the ACTUS Financial Research Foundation; referenced by the U.S. Treasury Office of Financial Research. Open standard, GitHub-hosted. ACTUS is what FIBO's instrument layer would look like if you actually had to compute cash flows from it — and it is materially complementary rather than competitive.
- **MISMO** (Mortgage Industry Standards Maintenance Organization). Reference Model v3.6 released 2023; v3.6.2 Candidate Recommendation October 2025. The mortgage industry's de-facto data standard; GSE Uniform Mortgage Data Program built on it. v3.6 added YAML / JSON Schema serialisations, a Verifiable Profile SMART Doc standard, and a HMDA implementation toolkit. **For the parent project's HMDA work, MISMO is the operative data dictionary, not FIBO LOAN.**
- **FFIEC Call Report XBRL taxonomy.** Mandatory quarterly reporting format for ~6,000 U.S. banks since 2005. ~2,000 data items per report. XBRL US Call Report category remains active. There is third-party work (`bankontology.com`) loading XBRL Call Reports into FIBO, but the regulators consume XBRL, not RDF.
- **HMDA LAR schema.** CFPB-maintained Loan Application Register schema; ~110 fields after the 2015 final rule plus subsequent amendments. Schema is published; field semantics are normative. *The parent project's HMDA-RI 2022 substrate is this schema.*

The point of listing these: a bank's "ontology" — the live thing whose terms appear in production systems — is almost always one of these data-dictionary standards plus a local glossary, not a description-logic ontology.

---

## 4. Recent academic / industrial ontology efforts (last 3-5 years)

- **LLM-assisted ontology construction.** A pipeline pattern has emerged: LLM proposes competency questions, drafts the TBox, populates the ABox; human reviews. The 2024 arXiv preprint "Automatic Ontology Construction Using LLMs as an Engineering Assistant" is representative. Not finance-specific. Quality remains human-bottlenecked.
- **Financial-regulation LLMs.** A 2025 FinNLP paper "A Large Language Model for Financial Regulation" (ACL Anthology). The pitch is fine-tuned text understanding of regulatory corpora; ontology integration is aspirational rather than load-bearing.
- **Algorithmic-fairness ↔ ECOA gap.** Black & Dimitrov, "Equalizing Credit Opportunity in Algorithms: Aligning Algorithmic Fairness Research with U.S. Fair Lending Regulation" (AIES 2022, arXiv 2210.02516). This paper is the cleanest articulation that the fairness-ML literature is largely disconnected from how Reg B disparate-impact analysis actually runs. *Worth reading carefully for the parent project's Paper 1 framing — same diagnosis, different mechanism.*
- **SR 26-2 (April 2026)** supersedes SR 11-7 on model risk management. Industry coverage (ValidMind, Lumenova, Domino, Yields) emphasises that the new guidance expects the **model inventory to be a knowledge graph**, not a spreadsheet, and introduces materiality calibration. This is the closest the regulator has come to specifying "you must maintain a queryable governance structure," and it is recent enough that bank programmes are still being designed against it. **The parent project's policy-constrained Rashomon work lands directly into this regulatory window.**
- **EU AI Act (Regulation 2024/1689)** requires "meaningful information about the logic involved" for high-risk AI, including credit scoring. This is the European parallel pressure.

I did not find any peer-reviewed, finance-specific, LLM-assisted ontology engineering work that is both novel and load-bearing. The arXiv pipeline work is generic; the financial-regulation LLM work treats text rather than structure.

---

## 5. What does a "typical ad-hoc bank ontology" actually look like?

Inferred from vendor pitches (Camunda, OpenRules, Dataedo, Ovaledge), MISMO implementation guides, consulting whitepapers, and the recurring patterns in job postings:

- **Excel-based business glossary.** Term, definition, owner, source-of-truth system. Often maintained by a data-governance office. Frequently out of date relative to the systems it claims to describe.
- **Decision tables.** DMN-style or just Excel. Encode underwriting rules, exception conditions, pricing tiers. Sometimes exported to a rules engine; often re-encoded by hand in code.
- **Partially-implemented data dictionary** for the data warehouse. MISMO-conformant in mortgage shops; bespoke elsewhere. Field-level lineage usually incomplete.
- **Code-as-policy.** Rules buried in Java/Python/COBOL underwriting code, Rego policies for access control, SQL stored procedures for derived fields. *This is where the actual decision lives.* The glossary describes intentions; the code describes behaviour; the two are not co-maintained.
- **Vendor-supplied taxonomies** for KYC / AML / sanctions screening. Often opaque, often the only durable "ontology" the line of business actually consults.

**Capabilities they routinely lack:**

1. **Round-trip from policy text to deployed rule and back.** The policy document and the deployed code are linked only by tribal knowledge.
2. **Explicit representation of exception paths.** Exception handling lives in tickets, emails, and senior-underwriter discretion.
3. **Counterfactual / what-would-have-happened auditability.** Reconstructing why a 2019 denial was denied is forensic work, not a query.
4. **Cross-jurisdictional indexicality.** A rule written for a national regulator and a state regulator gets two parallel implementations with no formal correspondence.
5. **Representation of the policy's own incompleteness.** What the policy *doesn't* say is unrecorded; "the underwriter's call" is invisible to the data layer. *(This is the seed flagged in the parent project's [project_ontology_design_philosophy].)*

---

## Cross-cutting analysis

### Where does FIBO not go that a governance ontology needs to?

FIBO is an **entity-and-instrument** ontology with strong coverage of *what financial things are* and competent coverage of *who the parties are and how they relate*. It does not natively model:

1. **Policy as a first-class object.** Not the regulation (LegalRuleML / AKN handle that), not the instrument (FIBO handles that), but the **bank's own deployed policy** — the documented decision rule, version, effective dates, exception ladder. FIBO's `LoanApplications/CreditRiskAssessment` reaches the concept; it does not represent a specific bank's documented credit-policy DAG.
2. **Decision-routing and observability.** "Which model evaluated this application, which policy gate applied, what tier did it land in, who has standing to ask why." FIBO has no native vocabulary for this; SR 26-2's knowledge-graph expectation is a regulator demand that no shipping standard satisfies.
3. **Indexicality / pragmatics.** Constraints want explicit context-of-utterance slots (substrate, variant, granularity). FIBO names things; it does not natively annotate *the conditions under which a naming is valid* — which the parent project's #11 rb05 result showed matters empirically.
4. **The ontology's own incompleteness.** Standard upper ontologies including FND treat the model as complete-by-construction. A governance ontology must represent what it does not yet codify — the "empty chair" structurally.

### The aspiration-vs-deployment gap

FIBO-as-aspiration is a coherent OWL-DL artifact spanning instruments, parties, contracts. FIBO-as-deployed inside a bank is usually a **vocabulary-alignment mapping** maintained by a data-governance team, sitting in a Confluence page or a master-data tool, pointing at terms that are *also* used in MISMO / ISO 20022 / the internal warehouse. The DL reasoning is rarely run in production. The bank-internal artifact that actually drives behaviour is some combination of MISMO data dictionary, decision tables, and code.

The gap is not technical; the gap is that nothing in the standards landscape rewards a bank for moving from "we mapped to FIBO" to "FIBO is our live decision substrate." SR 26-2 may begin to change this, but it does not require FIBO specifically.

### Where does policy-constrained Rashomon naturally complement existing tooling? (speculative)

*Marked speculative; this is the place to be careful.*

The parent project's contribution is **regulator-observable indeterminacy on a documented policy substrate**. It assumes a codified bank policy exists in a form the construction can read, and produces a Rashomon refinement set that exposes within-policy disagreement. The natural complement is:

- **Upstream:** something that produces the codified policy artifact the construction reads. **FRO / LKIF-style policy formalisation is the closest existing thing**; MISMO + decision-table tooling is the closest *deployed* thing. The construction is agnostic about which produces the codification, but it requires *some* explicit policy vocabulary.
- **Downstream:** something that consumes the Rashomon receipt and renders it for a supervisor — the SR 26-2 "model inventory as knowledge graph" expectation is the right consumer shape, though no live infrastructure yet exists to receive a refinement-band artifact.

The honest scope claim is: policy-constrained Rashomon is **infrastructure that sits between codified policy and supervisory observability**, and it presupposes both endpoints. Neither endpoint is solved in the current landscape; the parent project's argument is sharper if it acknowledges that codification (its upstream dependency) is itself an open problem — which is the [project_codification_infrastructure] frame.

### Seed for follow-up: which efforts represent their own incompleteness?

**Do not represent their own incompleteness** (treat the model as complete-by-construction): FIBO, BIAN, MISMO, ISO 20022, ACTUS. These are committee artifacts whose pragmatics are "what we agreed on so far, treat the rest as TODO." There is no slot for "this rule has a known gap at jurisdictional boundary X." This is conventional and not a criticism — it is just the position the parent project's pragmatics frame is critiquing.

**Partially represent their own incompleteness:** LegalRuleML (defeasibility operators acknowledge that rules can be overridden by other rules, which is a syntactic form of "this rule is not final"). LKIF (the meta-legal layer can talk about the legal sources, which is a step toward declaring provenance).

**Explicitly attempt to represent reasoning over what is not in the model:** FRO comes closest, in that it loads regulation text and infers obligations rather than asserting them. Single maintainer; small footprint; worth a direct read before Monday — its design choices are the closest published prior art to the parent project's codification layer.

**Follow-up worth doing:** read FRO's actual OWL files (finregont.com publishes them) and audit whether its hierarchy supports representing *what the regulator has not yet specified*, vs. only what it has. If it does, the parent project should cite it explicitly; if it does not, that is the gap to claim.

---

## Sources

- [FIBO — EDM Council](https://edmcouncil.org/financial-industry-business-ontology/)
- [FIBO GitHub repository (edmcouncil/fibo)](https://github.com/edmcouncil/fibo)
- [FIBO spec (spec.edmcouncil.org)](https://spec.edmcouncil.org/fibo/)
- [FIBO Reasoning Level — EDMC RDF Toolkit Wiki](https://wiki.edmcouncil.org/display/FIBORDFKIT/Reasoning+Level)
- [FIBO LOAN — HMDA-covered mortgages submodule](https://spec.edmcouncil.org/fibo/ontology/LOAN/RealEstateLoans/HomeMortgageDisclosureActCoveredMortgages/)
- [FIBO LOAN — CreditRiskAssessment](https://spec.edmcouncil.org/fibo/ontology/LOAN/LoansGeneral/LoanApplications/CreditRiskAssessment)
- [An Infrastructure for Collaborative Ontology Development (FIBO lessons learned) — ResearchGate](https://www.researchgate.net/publication/357533620_An_Infrastructure_for_Collaborative_Ontology_Development_Lessons_Learned_from_Developing_the_Financial_Industry_Business_Ontology_FIBO)
- [Exploring FIBO with GraphDB — Ontotext](https://www.ontotext.com/blog/fibo-graphdb-inference-and-property-path-features/)
- [FIBO — DIDO Wiki (OMG)](https://www.omgwiki.org/dido/doku.php?id=dido:public:ra:xapend:xapend.b_stds:tech:omg:fibo)
- [FIB-DM — Financial Industry Business Data Model](https://fib-dm.com/finance-ontology-transform-data-model/)
- [Liquid Legal Institute — Legal Ontologies catalogue (GitHub)](https://github.com/Liquid-Legal-Institute/Legal-Ontologies)
- [LegalRuleML specialisation for reporting obligations (Interoperable Europe, 2024)](https://interoperable-europe.ec.europa.eu/sites/default/files/news/2024-07/A%20LegalRuleML%20specialisation.pdf)
- [Semantic Interoperability — ELI/AKN mapping (ACM ICEGOV 2023)](https://dl.acm.org/doi/10.1145/3614321.3614327)
- [Financial Regulation Ontology — finregont.com](https://finregont.com/)
- [FRO — About](https://finregont.com/about-fro/)
- [ISO 20022 — Wikipedia](https://en.wikipedia.org/wiki/ISO_20022)
- [MISMO Reference Model](https://www.mismo.org/standards-resources/residential-specifications/reference-model)
- [MISMO v3.6.2 Reference Model](https://www.mismo.org/standards-resources/mismo-product/mismo-version-3.6.2-reference-model)
- [MISMO HMDA Implementation Toolkit](https://www.mismo.org/standards-and-resources/implementation-guides/mismo-hmda-implementation-toolkit)
- [ACTUS Foundation](https://www.actusfrf.org/)
- [ACTUS — Wikipedia](https://en.wikipedia.org/wiki/Algorithmic_Contract_Types_Unified_Standards)
- [FFIEC HMDA](https://www.ffiec.gov/data/hmda)
- [CFPB HMDA](https://www.consumerfinance.gov/data-research/hmda/)
- [FFIEC Call Report taxonomy download](https://cdr.ffiec.gov/public/DownloadTaxonomy.aspx)
- [XBRL US — FFIEC Call Report category](https://xbrl.us/home/category/taxonomy/ffiec-call-report/)
- [BIAN](https://bian.org/)
- [BIAN Service Landscape v12.0](https://bian.org/servicelandscape-12-0-0/)
- [BIAN v12.0 Release Notes (PDF)](https://bian.org/wp-content/uploads/2024/12/BIAN-v12.0-Release-Notes-v0.4.pdf)
- [BIAN — Wikipedia](https://en.wikipedia.org/wiki/Banking_Industry_Architecture_Network)
- [Black & Dimitrov — Equalizing Credit Opportunity in Algorithms (arXiv 2210.02516)](https://arxiv.org/abs/2210.02516)
- [Algorithmic discrimination in the credit domain — AI & Society 2023](https://link.springer.com/article/10.1007/s00146-023-01676-3)
- [SR 26-2 — Federal Reserve, April 2026](https://www.federalreserve.gov/supervisionreg/srletters/SR2602.htm)
- [SR 26-2 (PDF)](https://www.federalreserve.gov/supervisionreg/srletters/SR2602.pdf)
- [A Large Language Model for Financial Regulation — FinNLP 2025](https://aclanthology.org/2025.finnlp-1.43.pdf)
- [Open Policy Agent](https://www.openpolicyagent.org/)
