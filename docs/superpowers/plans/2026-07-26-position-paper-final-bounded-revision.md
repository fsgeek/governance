# Position Paper Final Bounded Revision Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the final five boundary repairs to *Architectures of Absence* and produce a source-verified, rendered, tested manuscript ready for the author's arXiv review.

**Architecture:** Revise from normative boundary to institutional pathway, then add only the adjacent theory and legal precision needed to support those claims. Reconcile terminology and narrative last so local repairs do not create a new paper. Verification uses primary legal sources, source checks, the rendered PDF, an independent nine-file arXiv build, and the repository test suite.

**Tech Stack:** LaTeX, BibLaTeX/Biber, LuaLaTeX/latexmk, Poppler PDF tools, primary legal and scholarly sources, Git/OpenTimestamps, Python/pytest through `uv`.

## Global Constraints

- Preserve the coordination ontology, artifact-to-inference taxonomy, falsifiable produced-absence hypothesis, three two-layer diagnostics, and five provisional evidentiary capabilities.
- Distinguish representation, access, participation, and remedy; do not imply that the ontology grants any of them.
- Separate actions available to one bank now from infrastructure requiring collective action.
- Add compact assurance-case and administrative-burden positioning, not a literature survey.
- Verify pricing and mandatory-language claims against primary sources.
- Retain `silence-manufacture` as the critical term and use `evidentiary-substitution sequence` as the neutral operational description.
- Do not add schemas, APIs, manifests, policy languages, bills of materials, retention schedules, thresholds, mandatory remedies, privilege strategies, implementation appendices, or practitioner checklists.
- Do not exceed the current 12,686-source-word manuscript by more than 500 net words; prefer replacement and compression.
- Do not commit generated PDFs, logs, auxiliary files, or temporary arXiv packages.
- The next user review is the completed arXiv-readiness manuscript, not an intermediate editorial checkpoint.

---

### Task 1: Clarify Affected-Party Standing Without Inventing Rights

**Files:**
- Modify: `section1.tex`
- Modify: `section4.tex`
- Modify: `section6.tex`
- Modify: `section7.tex`

**Interfaces:**
- Consumes: the existing actor ontology and contest pathways.
- Produces: stable definitions of representation, access, participation, contest, and remedy for all later edits.

- [ ] **Step 1: Locate collapsed normative claims**

Run:

```bash
rg -n "normative center|affected part|represent|participat|access|contest|remedy|standing|where access permits" section1.tex section4.tex section6.tex section7.tex
```

- [ ] **Step 2: State the four-way distinction**

Revise the opening so representation means making an interest and its evidentiary consequence inspectable. State that access concerns who may inspect which object, participation concerns direct voice in a process, and remedy concerns an authorized response. None follows automatically from the others or from the ontology.

- [ ] **Step 3: Give affected parties a diagnostic role within existing pathways**

Revise Section 4 so an affected party or advocate may supply evidence, challenge an offered proposition, identify a missing object, or trigger an existing complaint, appeal, correction, or review pathway where one exists. Do not claim that the paper creates a trigger, response deadline, burden shift, disclosure right, or ombudsman.

- [ ] **Step 4: State the unresolved normative consequence**

Revise Sections 6 and 7 so indirect representation is not described as participation. Where no access, participation, or remedy exists, the ontology makes that absence and its bearer legible but does not cure it.

- [ ] **Step 5: Verify and commit**

Run:

```bash
rg -n "representation|access|participation|remedy|affected part|does not.*grant|does not.*create" section1.tex section4.tex section6.tex section7.tex
git diff --check
```

Commit:

```bash
git add section1.tex section4.tex section6.tex section7.tex
git commit -m "paper: distinguish representation from participation and remedy"
```

---

### Task 2: Move the Two-Level Theory of Effect Forward

**Files:**
- Modify: `section1.tex`
- Modify: `section5.tex`
- Modify: `section6.tex`
- Modify: `section7.tex`

**Interfaces:**
- Consumes: Task 1's affected-party boundary.
- Produces: an explicit split between immediate institutional action and collective infrastructure.

- [ ] **Step 1: Identify buried or magical-leverage language**

Run:

```bash
rg -n "procurement|compensating|vendor|aggregation|collective|leverage|must be able|coordination pathway" section1.tex section5.tex section6.tex section7.tex
```

- [ ] **Step 2: Add the two-level pathway near the opening**

State that one bank can inventory evidence dependencies, narrow claims, use proportionate available processes, disclose residual limits, and make procurement needs comparable. State separately that cross-vendor bindings, standard exports, convergent expectations, and market leverage require coordinated action by regulators, trade groups, vendors, or multiple institutions.

- [ ] **Step 3: Bound compensating processes**

Replace language implying that a compensating control necessarily closes a vendor gap. A compensating process may narrow a claim or reduce risk; sometimes no proportionate substitute exists, leaving acceptance, restricted use, replacement, or discontinuation as institution-specific decisions outside the paper.

- [ ] **Step 4: Bound capability sequencing**

State that priorities depend on the proposition, risk, existing evidence, legal obligations, and feasible alternatives. Do not prescribe a universal capability order or cost-benefit result.

- [ ] **Step 5: Verify and commit**

Run:

```bash
rg -n "one bank|single institution|collective|coordinated|residual|no proportionate|priority|priorities" section1.tex section5.tex section6.tex section7.tex
git diff --check
```

Commit:

```bash
git add section1.tex section5.tex section6.tex section7.tex
git commit -m "paper: separate immediate action from collective infrastructure"
```

---

### Task 3: Add the Missing Theoretical Antecedents and Dual Register

**Files:**
- Modify: `section2.tex`
- Modify: `section4.tex`
- Modify: `references.bib`

**Interfaces:**
- Consumes: the existing adjacent-theory section and falsification criteria.
- Produces: compact assurance-case and administrative-burden positioning plus stable critical and operational terminology.

- [ ] **Step 1: Verify minimal primary or canonical sources**

Verify bibliographic metadata and relevant propositions for:

- Toulmin or a canonical assurance-case source covering claim/evidence/warrant or structured assurance arguments;
- a canonical administrative-burden source covering learning, compliance, or psychological costs;
- missing-not-at-random or selection literature only if needed to support the observability claim without overstating equivalence.

- [ ] **Step 2: Add no more than 300 net words of theory positioning**

State that assurance cases already structure claims, evidence, warrants, assumptions, and defeaters. State that administrative-burden and selection literatures already explain how friction and non-observation can shape the observed record. Claim only the paper's synthesis with affected interests, institutional authority/capability, and exact FS AI RMF controls.

- [ ] **Step 3: Define the dual register**

Define `evidentiary-substitution sequence` as the neutral five-part operational description. Retain `silence-manufacture` for instances where the unavailability of contradictory evidence helps the substitution persist. State explicitly that the label alone establishes neither intention nor causation.

- [ ] **Step 4: Audit rhetorical overreach**

Run:

```bash
rg -n "manufactur|suppress|weapon|intent|malicious|evidentiary-substitution" section2.tex section4.tex
```

Replace any remaining sentence in which the architecture itself reasons or in which the label performs the causal inference.

- [ ] **Step 5: Verify citations and commit**

Run the citation-key closure scripts from the prior revision plan, then:

```bash
git diff --check
git add section2.tex section4.tex references.bib
git commit -m "paper: position evidence sequence and administrative burden"
```

---

### Task 4: Audit Pricing Law and Mandatory Authority Language

**Files:**
- Modify: `section2.tex`
- Modify: `section3.tex`
- Modify: `section4.tex`
- Modify: `references.bib`

**Interfaces:**
- Consumes: Task 3's neutral operational terminology.
- Produces: legally bounded pricing analysis and consistent distinctions among framework, policy, supervision, and law.

- [ ] **Step 1: Verify primary legal sources**

Use current official sources for Regulation B adverse action and counteroffers, FCRA risk-based-pricing notices and credit-score disclosures, Regulation V implementing provisions, and Regulation Z price disclosures. Record the exact proposition each source supports.

- [ ] **Step 2: Repair the pricing boundary**

State that existing regimes can require risk-based-pricing or credit-score disclosures in covered circumstances while generally not supplying an individualized substantive reason-giving regime equivalent to adverse-action reasons for the precise offered price. Preserve exceptions and avoid categorical claims.

- [ ] **Step 3: Audit every FS AI RMF mandatory verb**

Run:

```bash
rg -n "FS.?AI.?RMF|objective|guidance|requires?|must|mandat|obligat|authority|supervis" paper.tex section*.tex
```

Where the subject is an FS AI RMF objective, write `the objective specifies`, `calls for`, or equivalent. Reserve legal requirement language for cited law and supervisory language for cited guidance or established authority.

- [ ] **Step 4: Verify and commit**

Run citation closure, legal-term searches, and `git diff --check`, then:

```bash
git add section2.tex section3.tex section4.tex references.bib
git commit -m "paper: refine pricing and framework authority boundaries"
```

---

### Task 5: Reconcile, Build, Inspect, Package, Test, and Push

**Files:**
- Modify if required: `paper.tex`, `section1.tex`–`section7.tex`, `references.bib`
- Verify: the complete manuscript and repository

**Interfaces:**
- Consumes: Tasks 1–4.
- Produces: the arXiv-review candidate on `main` and `origin/main`.

- [ ] **Step 1: Reconcile the abstract, transitions, and conclusion**

Ensure the abstract and conclusion accurately state the affected-party boundary, two-level theory of effect, dual terminology, and lack of new authority. Remove duplicated caveats and stale counts or terminology.

- [ ] **Step 2: Enforce scope and length**

Run:

```bash
wc -w paper.tex section1.tex section2.tex section3.tex section4.tex section5.tex section6.tex section7.tex
rg -n -i "JSON Schema|JWT|Rego|bill of materials|retention tier|ombudsman|burden shift|privilege|work product|appendix|checklist" paper.tex section*.tex
```

Expected: no excluded implementation proposal; final source count no greater than 13,186 words.

- [ ] **Step 3: Run source-integrity checks**

Scan for drafting residue, missing citation keys, missing labels, obsolete terminology, raw reviewer language, and `git diff --check` using the commands in the preceding revision plan.

- [ ] **Step 4: Clean-build and warning audit**

Run:

```bash
latexmk -lualatex -C paper.tex
latexmk -lualatex -interaction=nonstopmode -halt-on-error paper.tex
rg -n "LaTeX Warning|Package .* Warning|undefined|Undefined|Empty bibliography|Please \(re\)run Biber|Citation.*undefined|Reference.*undefined|Overfull|Underfull|WARN" paper.log paper.blg
```

Expected: a fresh PDF and no warning matches.

- [ ] **Step 5: Inspect rendered paper**

Extract normalized text with `pdftotext -nopgbrk`; render every page with `pdftoppm`; inspect the title, abstract, every section transition, revised theory and pricing passages, capability section, conclusion, and bibliography. Reject clipping, blank pages, malformed characters, raw TeX, or drafting residue.

- [ ] **Step 6: Build the independent nine-file arXiv package**

Copy `paper.tex`, seven section files, and `references.bib` into a `mktemp -d` directory; clean-build there; require zero warning matches; archive exactly those nine source files; record package and PDF SHA-256 checksums.

- [ ] **Step 7: Run repository tests**

Run:

```bash
uv run pytest
```

Expected: 340 passed, 1 skipped, with only the known scikit-learn warnings unless the test inventory legitimately changes.

- [ ] **Step 8: Commit, timestamp, and push**

Commit any final reconciliation as `paper: complete final bounded arxiv revision`. Confirm `main` is clean, then push normally without force. Verify `main...origin/main` is synchronized.

- [ ] **Step 9: Handoff for author review**

Report the substantive changes, rejected out-of-scope reviewer demands, primary-source results, final word/page counts, build/package checksums, test results, and exact commit. State whether the manuscript is ready for arXiv review without qualifying the judgment merely because further improvement is always possible.
