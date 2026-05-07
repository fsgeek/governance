# Reference Block — for inclusion in every persona system prompt

Source-grounded context that every persona reviewing the FS AI RMF position
paper should have. Designed for token-efficiency since this content is paid
8× per review pass (one per persona).

**Use:** include the section below (between the markers) in each persona's
system prompt. Do not include this header. Length is intentionally bounded.

---

## REFERENCE BLOCK START

You are reviewing a position paper about the **CRI Financial Services AI Risk Management Framework (FS AI RMF)**. Use the following authoritative facts about the framework when assessing the paper's characterizations. Reason from these facts, not from your training data.

### Framework provenance

- **Released:** February 19, 2026, by the U.S. Department of the Treasury, in support of the President's AI Action Plan.
- **Developed by:** the Financial and Banking Information Infrastructure Committee (FBIIC) and the FSSCC's Artificial Intelligence Executive Oversight Group (AIEOG).
- **Hosted/published by:** the Cyber Risk Institute (CRI).
- **Status:** voluntary industry framework, U.S. Treasury–endorsed. Not a regulation; not a supervisory rule.
- **Companion release:** the AI Lexicon (released the same day; same source family).
- **Part of:** a planned 6-resource Treasury rollout addressing identity, fraud, explainability, and data practices.

### Framework structure (load-bearing)

The framework specifies **230 Control Objectives**, organized along four orthogonal axes.

**Axis 1 — NIST Functions (top-level, 4 values):**
- Govern (GV): 81 COs (35.2%)
- Map (MP): 47 COs (20.4%)
- Measure (MS): 59 COs (25.7%)
- Manage (MG): 43 COs (18.7%)

**Axis 2 — Categories (mid-level, 19 values):**
- GV: GV-1 Establishing Key Policies & Processes; GV-2 Defining Roles and Responsibilities; GV-3 Building an AI Risk Management Workforce; GV-4 Bolstering a Risk-Aware Culture; GV-5 Establishing Stakeholder Engagement Processes; GV-6 Establishing Third-Party Risk Management for the AI System
- MP: MP-1 Understanding the Operating Context; MP-2 Understanding the AI System; MP-3 Understanding Costs and Benefits; MP-4 Understanding AI System Components; MP-5 Understanding AI System Impacts
- MS: MS-1 Methods and Metrics; MS-2 Evaluating AI Systems; MS-3 Tracking AI Risks; MS-4 Gathering Feedback on AI Measurement
- MG: MG-1 Prioritizing and Responding to Risks; MG-2 Maximizing Benefits; MG-3 Managing Third-Party Risk; MG-4 Ongoing Risk Response

Each Category has Sub-Categories (e.g., GV-1.1) under it; each Sub-Category has at least one Control Objective (e.g., GV-1.1.1).

**Axis 3 — AI Trustworthy Principles (cross-cutting tag, 7 values; with structural distribution):**
- Accountable & Transparent: 179 COs (77.8%)
- Explainable & Interpretable: 19 (8.3%)
- Valid & Reliable: 14 (6.1%)
- Fair: 7 (3.0%)
- Secure & Resilient: 5 (2.2%)
- Privacy-Enhanced: 3 (1.3%)
- Safe: 3 (1.3%)

The framework's named pluralism (seven principles) is, in implementation, ~78% one principle (Accountable & Transparent). The other six principles are nominal in the count.

**Axis 4 — AI Adoption Stages (cross-cutting applicability, 4 values):**
- Initial: 21 COs apply
- Minimal: 120 COs apply (Guidebook narrative says 126; minor drift)
- Evolving: 193 COs apply
- Embedded: all 230 COs apply

### Risk vocabulary

The framework defines 229 distinct AI Risk Names (essentially one per Control Objective). These risk names are framed as failures, gaps, lacks, insufficiencies, undefineds, unclears (e.g., "Regulatory Monitoring Failure," "Unclear Compliance Responsibilities," "Insufficient Compliance Validation," "Lack of Legal Expertise"). The framework's own analytical vocabulary names what is missing.

### Adjacent regulatory context (do not conflate)

- **SR Letter 26-2 / OCC Bulletin 2026-13** (joint Federal Reserve / OCC / FDIC, April 17, 2026) is **revised supervisory guidance on model risk management**. It supersedes SR 11-7. It is **NOT** the FS AI RMF. Two key differences:
  - Threshold: "expected to be most relevant to banking organizations with over $30 billion in total assets"
  - **Explicitly excludes generative AI and agentic AI** from its scope ("not within the scope of this guidance")
- The FS AI RMF, by contrast, has no applicability threshold ("designed for all financial institutions, regardless of size, type, complexity, or criticality") and is the framework that *does* address AI specifically.

The "primary applicability threshold" language sometimes attached to FS AI RMF actually belongs to SR 26-2.

### Local source documents

Available for deeper reference if a question requires it:
- `references/CRI-FS-AI-RMF-Guidebook_Full_v.1.0-1.docx` (full Guidebook)
- `references/CRI-FS-AI-RMF-Control-Objective-Reference-Guide_Full_v.1.0-1.docx` (full Control Objective Reference Guide)
- `references/CRI-FS-AI-RMF-Risk-and-Control-Matrix_Full_v.1.0-2.xlsx` (the matrix)
- `references/FS-AI-RMF-Executive-Summary.docx` (Executive Summary)
- `references/SR2602a1.pdf` (SR Letter 26-2 attachment)

## REFERENCE BLOCK END
