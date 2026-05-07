# FS AI RMF Structural Analysis

Structural inventory and quantitative observations about CRI's FS AI RMF v1.0,
extracted from the local source documents:
- `references/CRI-FS-AI-RMF-Guidebook_Full_v.1.0-1.docx`
- `references/CRI-FS-AI-RMF-Risk-and-Control-Matrix_Full_v.1.0-2.xlsx`

Captured 2026-05-06. Document version stamp inside the matrix: `Ver. 1.0 | 02-09-2026`.

## Structural axes

The framework organizes 230 Control Objectives along four orthogonal axes:

### Axis 1: NIST Functions (top-level structural organizer; 4 values)

| Function | COs | % |
|---|---|---|
| Govern (GV) | 81 | 35.2% |
| Map (MP) | 47 | 20.4% |
| Measure (MS) | 59 | 25.7% |
| Manage (MG) | 43 | 18.7% |
| **Total** | **230** | **100%** |

Govern dominates structurally — 35% of all COs are governance-related. Adding Map (which is largely about understanding context and components), the front-half of the framework (Govern + Map = 128 COs, 56%) outweighs the back-half (Measure + Manage = 102 COs, 44%).

### Axis 2: Categories (mid-level structural organizer; 19 values)

| Function | Categories |
|---|---|
| GV | GV-1 Establishing Key Policies & Processes; GV-2 Defining Roles and Responsibilities; GV-3 Building an AI Risk Management Workforce; GV-4 Bolstering a Risk-Aware Culture; GV-5 Establishing Stakeholder Engagement Processes; GV-6 Establishing Third-Party Risk Management for the AI System |
| MP | MP-1 Understanding the Operating Context; MP-2 Understanding the AI System; MP-3 Understanding Costs and Benefits; MP-4 Understanding AI System Components; MP-5 Understanding AI System Impacts |
| MS | MS-1 Methods and Metrics; MS-2 Evaluating AI Systems; MS-3 Tracking AI Risks; MS-4 Gathering Feedback on AI Measurement |
| MG | MG-1 Prioritizing and Responding to Risks; MG-2 Maximizing Benefits; MG-3 Managing Third-Party Risk; MG-4 Ongoing Risk Response |

19 Categories total. Each Category has Sub-Categories beneath it (not enumerated here; they are the GV-1.1, GV-1.2 etc. layer).

### Axis 3: AI Trustworthy Principles (cross-cutting tag; 7 values)

| Principle | COs tagged | % |
|---|---|---|
| Accountable & Transparent | 179 | 77.8% |
| Explainable & Interpretable | 19 | 8.3% |
| Valid & Reliable | 14 | 6.1% |
| Fair | 7 | 3.0% |
| Secure & Resilient | 5 | 2.2% |
| Privacy-Enhanced | 3 | 1.3% |
| Safe | 3 | 1.3% |
| **Total** | **230** | **100%** |

**Striking asymmetry:** 78% of the framework's content is tagged "Accountable & Transparent." Fairness gets 3%, Safety gets 1.3%, Privacy gets 1.3%. The framework's stated alignment to seven trustworthy principles is, in implementation, overwhelmingly one principle.

### Axis 4: AI Adoption Stages (cross-cutting applicability; 4 values)

| Stage | COs applicable |
|---|---|
| Initial | 21 |
| Minimal | 120 |
| Evolving | 193 |
| Embedded | 230 (all) |

Note: a Control Objective can apply to multiple stages. The Guidebook narrative lists Minimal as 126; the matrix shows 120 marked "Yes" for Minimal. Small discrepancy worth flagging but not load-bearing.

## The paper's "seven categories" claim, finally resolved

Paper claim: "230 control objectives spanning governance, data, model development, validation, monitoring, third-party risk, and consumer protection."

| Paper's category | Closest framework structural element | Match? |
|---|---|---|
| Governance | Govern function (GV, 81 COs) | partial — name overlaps but Govern is one of four functions, not one of seven categories |
| Data | No structural axis labeled "data"; data appears in many Sub-Category descriptions | no — content theme, not structural axis |
| Model development | Roughly Map function | no — Map is wider than model-dev |
| Validation | Roughly Measure function | partial |
| Monitoring | Roughly MS-3 (Tracking AI Risks) and MG-4 (Ongoing Risk Response) | partial — split across Functions |
| Third-party risk | GV-6 + MG-3 (Categories explicitly named for third-party) | matches at Category level, in two places |
| Consumer protection | No structural axis; appears in some Risk Statements | no — content theme, not structural axis |

**Resolution:** the paper's seven categories are a substantive content gloss, not a structural feature of the framework. Three of the seven (governance, third-party risk, monitoring) have weak structural anchors; four (data, model development, validation, consumer protection) don't appear as structural axes at all.

Recommended paper revision: drop "spanning [seven X]" wording, replace with a brief description of the actual structure ("organized around four NIST AI RMF functions — Govern, Map, Measure, Manage — with 19 sub-categories and tagged against seven AI Trustworthy Principles") OR explicitly mark the seven as "the substantive content areas the framework addresses include..." (which is defensible).

## Two findings that may be paper-relevant beyond verification

### 1. The framework's normative weight is overwhelmingly on accountability/transparency

78% of the 230 COs are tagged "Accountable & Transparent." This is not a balanced framework against the seven NIST Trustworthy Principles. Fairness (3%), Privacy (1.3%), and Safety (1.3%) are *named* but barely *instantiated*. The empty-chair frame applied to the framework itself surfaces a question: which principles are structurally underweighted, and what absences does that produce?

This is a finding the paper could use directly — the framework's named pluralism (seven principles) and structural monism (one principle dominates) is itself an instance of the silence-manufacture pattern. The other six principles occupy the rhetorical position of full coverage; the structural reality is nominal coverage.

### 2. The framework's vocabulary is built around absence-language

229 distinct AI Risk Names for 230 Control Objectives — essentially a 1:1 mapping. The risk names are framed as failures, gaps, lacks, insufficiencies:
- "Regulatory Monitoring Failure"
- "Unclear Compliance Responsibilities"
- "Insufficient Compliance Validation"
- "Lack of Legal Expertise"
- "Undefined AI Trustworthy Principles"
- "Inadequate Risk Assessment"
- "Unmanaged Shadow IT"
- "Inaccessible Documentation Repository"
- ...

The framework's own vocabulary is about naming what's missing. Each Control Objective addresses a specific named absence. The empty-chair frame is, in this sense, native to the framework's own language — the paper's frame is not imposed from outside; it is the framework's own analytical posture made explicit.

This is a methodologically strong move for the paper: the frame's value is not "outsider critique" but "explicit articulation of what the framework is already doing." Section 4 might note this directly.

## Minor flag

Minimal stage CO count: Guidebook narrative says 126; matrix data column shows 120 "Yes" entries. Could be document-version drift, or differing counting logic (e.g., primary applicability vs all applicability). Worth noting in a footnote rather than treating as a paper claim.
