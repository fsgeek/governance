# Citations — FS AI RMF and adjacent regulatory documents

Anchoring sources for the position paper. Captured to persist across
sessions so this needle-in-haystack work doesn't have to be repeated.

Status as of 2026-05-06.

---

## FS AI RMF (the framework itself)

**Issuer (industry):** Cyber Risk Institute (CRI)
**Co-release partner (government):** U.S. Department of the Treasury
**Release date:** February 12, 2026
**Version:** v1.0
**Status:** Voluntary industry framework, government-endorsed

### Treasury press release (the load-bearing government anchor)

- **URL:** https://home.treasury.gov/news/press-releases/sb0401
- **Title:** "Treasury Releases Two New Resources to Guide AI Use in the Financial Sector"
- **Date:** February 19, 2026 (precise — full text confirmed)
- **Direct fetch:** intermittently times out (May 2026); content confirmed by direct paste from the live page on 2026-05-06.

#### Treasury's exact framing of its role

> the U.S. Department of the Treasury today released two new resources to guide AI use in the financial sector, a shared Artificial Intelligence Lexicon and the Financial Services AI Risk Management Framework (FS AI RMF)

#### Development credit (Treasury's framing)

> Developed through the Financial and Banking Information Infrastructure Committee and the Financial Services Sector Coordinating Council's Artificial Intelligence Executive Oversight Group (AIEOG), the publications advance implementation of the Action Plan by translating national AI priorities into practical tools for financial institutions, regulators, and technology providers.

So the development chain Treasury names is **FBIIC + AIEOG** (under FSSCC), not CRI directly. CRI is one of the participating industry organizations and is the document host; CRI's CEO is quoted in the release, but Treasury credits the development to the two government-coordinated bodies.

#### The framework is part of a 6-resource Treasury rollout

> The AI Lexicon and FS AI RMF are part of a coordinated series of AIEOG deliverables addressing priority areas such as **identity, fraud, explainability, and data practices**.

So FS AI RMF is the second of six planned deliverables under the President's AI Action Plan implementation. The paper may want to situate it within this broader Treasury program rather than treating it as a standalone artifact.

#### Treasury's own characterization of FS AI RMF scope (does not use the seven banking-domain categories)

> the Financial Services AI Risk Management Framework adapts the NIST AI Risk Management Framework to the specific **operational, regulatory, and consumer protection considerations** of financial services. The FS AI RMF provides practical tools and reference materials to help institutions evaluate AI use cases, manage risks across the AI lifecycle, and embed **accountability, transparency, and resilience** into AI deployment decisions.

#### Named officials on record

- Derek Theurer — performing the duties of Deputy Secretary of the Treasury
- Paras Malik — Chief Artificial Intelligence Officer at the U.S. Department of the Treasury
- Josh Magri — CEO, Cyber Risk Institute (quoted as agreeing with Treasury's framing)

#### President's AI Action Plan

The release explicitly situates FS AI RMF within "the President's AI Action Plan, which calls for clear standards, shared understanding, and risk-based governance to ensure artificial intelligence is deployed safely and responsibly." The Action Plan itself is a separate document worth citing if the paper invokes it.

### CRI announcement (the industry-side anchor)

- **URL:** https://cyberriskinstitute.org/financial-services-industry-unites-to-launch-comprehensive-ai-risk-management-framework/
- **Date:** February 12, 2026 (specific date confirmed)
- **Framing:** Industry-led launch. CRI's announcement does *not* mention Treasury — frames the framework as a CRI initiative aligned with NIST AI RMF, coordinated with FSSCC. The asymmetry between Treasury's "partnership" framing and CRI's silence on Treasury is itself notable.
- **Quote:** Josh Magri (CRI CEO) on the framework offering "practical, scalable guidance tailored to the varying stages of AI adoption."

### CRI framework page (canonical)

- **URL:** https://cyberriskinstitute.org/artificial-intelligence-risk-management/
- Source location for all FS AI RMF documents.

### Direct document downloads (CRI hosting)

- Guidebook: https://cyberriskinstitute.org/wp-content/uploads/2026/02/CRI-FS-AI-RMF-Guidebook_Full_v.1.0-1.docx
- Control Objective Reference Guide: https://cyberriskinstitute.org/wp-content/uploads/2026/02/CRI-FS-AI-RMF-Control-Objective-Reference-Guide_Full_v.1.0-1.docx
- Risk and Control Matrix: https://cyberriskinstitute.org/wp-content/uploads/2026/02/CRI-FS-AI-RMF-Risk-and-Control-Matrix_Full_v.1.0-2.xlsx

### FSSCC published documents (sector coordinating council)

- **URL:** https://fsscc.org/aieog-ai-deliverables/
- This is the AIEOG (Artificial Intelligence Executive Oversight Group) deliverables page. AIEOG is the public-private partnership housed under FSSCC that *developed* the FS AI RMF. So the development chain is: AIEOG (developer) → CRI (publisher) → Treasury (releaser). All three attributions are factually correct depending on which role you're naming.

### ABA Banking Journal coverage (useful framing source)

- **URL:** https://bankingjournal.aba.com/2026/02/treasury-releases-first-of-ai-resources/
- Direct quote: "The Treasury Department has released the first two of six planned resources to help the financial services sector safely deploy artificial intelligence."
- Also: "The resources were developed by the Artificial Intelligence Executive Oversight Group, a private-public partnership that brought together financial institution executives with federal and state regulators and other stakeholders."
- **Implication:** FS AI RMF is part of a planned 6-resource rollout by Treasury. Worth noting in the paper if you address the framework as part of a broader regulatory program rather than a standalone document.

### Structural facts (verified against `references/CRI-FS-AI-RMF-Guidebook_Full_v.1.0-1.docx`)

- 230 Control Objectives total
- Distributed across 4 NIST Functions: Govern (81), Map (47), Measure (59), Manage (43)
- Categories and Sub-Categories within each Function (e.g., GV-1 → GV-1.1 → GV-1.1.1)
- 7 AI Trustworthy Principles (cross-cutting): Validity & Reliability; Safety; Security & Resiliency; Accountability & Transparency; Explainability & Interpretability; Privacy; Fairness with Mitigation of Harmful Bias
- 4 AI Adoption Stages (cross-cutting): Initial (21 COs apply), Minimal (126), Evolving (193), Embedded (230 — all)
- Applies to "all financial institutions, regardless of size, type, complexity, or criticality" — *no* applicability threshold

---

## SR Letter 26-2 / OCC Bulletin 2026-13 / FDIC FIL — Revised Model Risk Management Guidance

**Distinct from FS AI RMF.** This is the joint banking-agency guidance on model risk management generally; it explicitly excludes generative and agentic AI. The $30B threshold the paper invokes belongs here, not to FS AI RMF.

**Issuers:** Joint — Federal Reserve, OCC, FDIC
**Release date:** April 17, 2026
**Supersedes:** SR Letter 11-7 (April 2011) and SR Letter 21-8 (April 2021)
**AI scope:** "Generative AI and agentic AI models are novel and rapidly evolving. As such, they are not within the scope of this guidance." (footnote 3 of SR 26-2 attachment)

### Federal Reserve SR Letter

- **URL:** https://www.federalreserve.gov/supervisionreg/srletters/SR2602.htm
- **Attachment PDF:** https://www.federalreserve.gov/supervisionreg/srletters/SR2602a1.pdf
- Local copy: `references/SR2602a1.pdf`

### OCC Bulletin

- **URL:** https://www.occ.treas.gov/news-issuances/bulletins/2026/bulletin-2026-13.html
- **Bulletin attachment PDF:** https://www.occ.gov/news-issuances/bulletins/2026/bulletin-2026-13a.pdf

### OCC Press Release (this is the source Tony recalled)

- **URL:** https://www.occ.treas.gov/news-issuances/news-releases/2026/nr-occ-2026-29.html
- **Date:** April 17, 2026
- **Quote on threshold:** "The updated guidance is expected to be most relevant to banking organizations with over $30 billion in total assets."
- **Quote on AI exclusion:** "In addition, generative AI and agentic AI models are novel and rapidly evolving. As such, they are not within the scope of this guidance."
- **Quote on enforceability:** "non-compliance with this guidance alone will not result in supervisory criticism against a banking organization."
- **Forthcoming:** The release notes regulators plan to issue a separate request for information specifically addressing banks' use of AI technologies, including generative and agentic AI models.

### FDIC

- **Press release:** https://www.fdic.gov/news/press-releases/2026/agencies-issue-revised-model-risk-guidance
- **FIL:** https://www.fdic.gov/news/financial-institution-letters/2026/agencies-revise-interagency-model-risk-management-guidance

---

## Adjacent / supporting regulatory anchors

### NIST AI RMF (foundational document; FS AI RMF is a profile of this)

- **URL:** https://www.nist.gov/itl/ai-risk-management-framework
- Released January 2023. Cross-sector, voluntary. Four functions: Govern, Map, Measure, Manage. CRI's FS AI RMF "operationalizes" this for financial services.

### Crosswalks / third-party analyses (useful for fact-checking)

- **NIST AI RMF for Financial Services: Crosswalk to SR 26-02, OCC 2026-13, and FS AI RMF (RiskTemplate, April 2026):**
  https://risktemplate.com/blog/2026-04-24-nist-ai-rmf-sr-26-02-fs-ai-rmf-crosswalk-financial-services/
- **KPMG: Deconstructing the CRI FS AI RMF:**
  https://kpmg.com/us/en/articles/2026/deconstructing-cyber-risk-institute-fs-ai-rmf.html
- **Sullivan & Cromwell on revised model risk guidance:**
  https://www.sullcrom.com/insights/memo/2026/April/OCC-Fed-FDIC-Issue-Revised-Guidance-Model-Risk-Management
- **Lowenstein Sandler on operationalizing the 230 Control Objectives:**
  https://www.lowenstein.com/news-insights/publications/client-alerts/financial-services-ai-risk-management-framework-operationalizing-the-230-control-objectives-before-the-market-wakes-up-data-privacy
- **Cooley Finsights on Treasury's release:**
  https://finsights.cooley.com/us-treasury-releases-new-ai-risk-management-resources-for-financial-institutions/

---

## Implications for the paper's load-bearing claims

| Paper claim | Source status |
|---|---|
| FS AI RMF released by US Treasury, Feb 2026 | Defensible. Treasury press release frames as partnership release. Rigorous form: "released by the U.S. Treasury in partnership with the Cyber Risk Institute." |
| 230 control objectives | Confirmed (CRI Guidebook, 81+47+59+43). |
| Spans seven categories (governance, data, model dev, validation, monitoring, third-party risk, consumer protection) | Not how the framework structures itself. Framework structure is NIST 4 Functions × Categories × Sub-Categories, with 7 AI Trustworthy Principles as cross-cutting axis. The paper's seven may be substantive content gloss; phrasing could be refined to avoid implying structural claim. |
| Community banks under "primary applicability threshold" | Threshold belongs to SR 26-2 ($30B), not FS AI RMF (which has no threshold). Coherent argument but needs explicit cross-document framing in paper. |

## Recurring instability note

Treasury page (sb0401) timed out on direct WebFetch attempts on 2026-05-06. URL is in WebSearch results and confirmed via secondary coverage (ABA Banking Journal, Cooley, etc.). Re-fetch periodically.
