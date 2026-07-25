# Position Paper Coordination Revision Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Revise *Architectures of Absence* into a coordination-oriented position paper that gives banks, regulators, and vendors a common ontology for contestable AI-governance evidence while preserving affected parties, authority boundaries, and bounded claim status.

**Architecture:** The revision proceeds from conceptual foundations to operational consequences. It first fixes the participant ontology and epistemic hierarchy, then makes produced absence falsifiable, positions the contribution against adjacent theory, operationalizes the diagnostics, revises the architectural capabilities, and finally reconciles and compresses the full narrative. Verification uses both source-aware checks and the rendered PDF so extraction artifacts cannot masquerade as manuscript defects.

**Tech Stack:** LaTeX, BibLaTeX/Biber, LuaLaTeX/latexmk, Poppler PDF tools, Git/OpenTimestamps, Python/pytest through `uv`.

## Global Constraints

- Preserve empty-chair representation, structural versus produced absence, silence-manufacture, the artifact-to-inference taxonomy, and exact FS AI RMF control bindings.
- Treat the paper as a boundary object and translation ontology, not an examination manual, implementation specification, or empirical validation study.
- Assign every proposed action to a bank, examiner/regulator, vendor/architect, or affected party with the authority, capability, or standing to perform it.
- Never present a policy recommendation or design hypothesis as a current legal obligation or examination finding.
- Treat produced absence as a hypothesis requiring comparative, counterfactual, provenance, or user evidence; observed silence alone is insufficient.
- Describe architectural outputs as five provisional evidentiary capabilities, not universal requirements.
- Preserve decision-time records and later reflective records as distinct, revision-aware evidentiary objects.
- Add only compact adjacent-theory positioning; do not create a comprehensive literature review.
- Do not add experiments, a 230-control coding, implementation specifications, examination thresholds, or unrelated Rashomon-model work.
- Reduce the manuscript by 600–1,000 net words relative to the 13,686-word source baseline measured on July 25, 2026.
- Preserve unrelated user changes, including `scripts/ots-upgrade.sh` and its timestamp history.
- Do not commit PDFs, logs, auxiliary TeX files, or temporary arXiv packages.

---

### Task 1: Establish the Coordination Ontology and Actor-Specific Theory of Effect

**Files:**
- Modify: `section1.tex:8-30`
- Modify: `section7.tex:5-58` only where the conclusion must mirror the ontology

**Interfaces:**
- Consumes: the approved ontology in `docs/superpowers/specs/2026-07-25-position-paper-coordination-revision-design.md`.
- Produces: stable actor, artifact, inference, binding, authority, capability, obligation, and contest terminology for every later task.

- [ ] **Step 1: Record the baseline terminology and overclaims**

Run:

```bash
rg -n "community bank|examiner|regulator|vendor|architect|method|discipline|demonstrat|requires|finding|authority" section1.tex section7.tex
```

Expected: current prose names banks and examiners but does not state a complete bank–regulator–vendor coordination pathway.

- [ ] **Step 2: Rewrite the opening's contribution statement**

Revise `section1.tex` so the contribution is explicitly a translation ontology with this relation:

```text
affected interest -> control objective -> required evidentiary object
-> available artifact -> claimed inference and binding
-> actor able to close, disclose, or contest the gap
```

State that:

- banks identify evidence gaps, compensating controls, and procurement needs;
- examiners test claims within current authority;
- regulators aggregate recurring gaps into guidance or coordinated expectations;
- vendors implement provenance, exportability, capture, representation, and monitoring capabilities;
- affected parties provide the normative purpose and need not possess symmetric institutional power.

Do not create a glossary section; integrate the ontology into the opening narrative in no more than 450 new words before compression.

- [ ] **Step 3: Bound the paper's neutrality and claim status**

Add a concise statement that neutrality is procedural rather than viewless: each perspective receives standing, but every inference remains contestable and unequal authority is explicit. Replace “demonstrates the lens” with “applies the lens” or “offers worked applications.”

- [ ] **Step 4: Make the conclusion reserve the same roles**

Adjust `section7.tex` only enough to ensure it does not assign implementation to community banks or turn conceptual questions into findings. Preserve the five closing examination questions for final reconciliation in Task 7.

- [ ] **Step 5: Verify actor and claim consistency**

Run:

```bash
rg -n "bank|examiner|regulator|vendor|affected part|authority|capability|policy" section1.tex section7.tex
rg -n "demonstrates the lens|community bank.*architect|examiner.*finding" section1.tex section7.tex
git diff --check
```

Expected: all three institutional participants and affected parties appear; no sentence grants a participant unestablished authority or capability.

- [ ] **Step 6: Commit the coordination foundation**

```bash
git add section1.tex section7.tex
git commit -m "paper: establish coordination ontology and actor roles"
```

---

### Task 2: Make Produced Absence Testable and Separate Policy From Examination

**Files:**
- Modify: `section2.tex:6-68`
- Modify: `section3.tex:69-90`

**Interfaces:**
- Consumes: Task 1's actor and authority vocabulary.
- Produces: a falsifiable produced-absence hypothesis and a pricing example explicitly scoped as policy analysis.

- [ ] **Step 1: Locate presumed-causation language**

Run:

```bash
rg -n "produced absence|produces? the silence|created by the architecture|reads? .* as|interprets? .* as|demonstrat" section2.tex section3.tex
```

Expected: several active sentences infer suppression directly from observed silence.

- [ ] **Step 2: Define produced absence as a hypothesis**

Revise the definition to require evidence that a design, cost, rule, interface, or institutional practice materially changes observability. State explicitly:

```text
Observed silence is consistent with produced absence but does not establish it.
```

Name acceptable evidence classes: cross-channel or cross-time comparison, friction change, user research, complaint evidence, examiner-selected sampling, feasible counterfactual design, and provenance of excluded or overwritten records.

- [ ] **Step 3: Remove anthropomorphic inference**

Replace claims that “the architecture interprets” or “the design infers” with identified institutional processes, reports, policies, reviewers, or decision makers. Architecture may enable, constrain, suppress, expose, or record; people and institutional processes draw conclusions.

- [ ] **Step 4: Recast the BSA/AML applications**

Call them worked applications or illustrative analyses. Where empirical evidence is absent, write “raises the produced-absence question” rather than assigning the classification. Preserve exact control-objective traceability from the prior repair.

- [ ] **Step 5: Bound the pricing turn by current authority**

State that risk-based pricing illustrates a potential policy and design gap. Current law does not generally authorize an examiner to cite a bank merely for failing to provide an individualized substantive pricing justification beyond applicable requirements. Preserve lawful aggregate validation as important evidence and avoid claiming that it proves individual fairness.

- [ ] **Step 6: Add defeating evidence**

For the principal produced-absence propositions, state what would count against them: unchanged challenge behavior after material friction reduction; complete and representative records despite the alleged suppression mechanism; or stable conclusions after previously unavailable evidence becomes accessible.

- [ ] **Step 7: Verify inference and authority boundaries**

Run:

```bash
rg -n "Observed silence|counterfactual|comparison|would count against|policy|current.*require|authority" section2.tex section3.tex
rg -n "architecture (reads|infers|interprets)|design (reads|infers|interprets)|demonstrates the latter" section2.tex section3.tex
git diff --check
```

Expected: falsification and policy language appear; anthropomorphic inference and empirical “demonstration” language do not.

- [ ] **Step 8: Commit the falsifiability repair**

```bash
git add section2.tex section3.tex
git commit -m "paper: make produced absence testable and authority-bound"
```

---

### Task 3: Position the Conceptual Contribution Against Adjacent Theory

**Files:**
- Modify: `section4.tex:12-49`
- Modify: `references.bib`

**Interfaces:**
- Consumes: Task 2's testable mechanism.
- Produces: a bounded novelty claim for the ontology, synthesis, diagnostic sequence, and FS AI RMF application.

- [ ] **Step 1: Audit existing theory claims and bibliography**

Run:

```bash
rg -n "novel|new|Goodhart|dual|decoupl|audit|principal|information asym|stakeholder|value-sensitive" section4.tex references.bib
```

Expected: Goodhart, decoupling, and audit literature appear; principal-agent, information asymmetry, stakeholder theory, and value-sensitive design do not.

- [ ] **Step 2: Verify a minimal set of primary bibliographic records**

Verify authoritative publication metadata for one canonical source in each missing family before citation:

- stakeholder theory;
- value-sensitive design;
- principal-agent or costly monitoring;
- information asymmetry only if not adequately covered by the principal-agent source.

Prefer original books, articles, or publisher records. Do not add a source merely to populate every label if one source legitimately covers two related concepts.

- [ ] **Step 3: Write the compact theory comparison**

In no more than 350 words, state:

- what affected-interest frameworks contribute;
- what incentive and information theories contribute;
- what decoupling and audit theories contribute;
- what this paper adds: an artifact-to-inference sequence tied to control objectives, authority, evidence capability, and absent-party consequences.

Do not claim that silence-manufacture yields a unique economic equilibrium or discovers substitution as a new social phenomenon.

- [ ] **Step 4: Define silence-manufacture's role consistently**

Use it primarily as the diagnostic sequence:

```text
required evidentiary object unavailable -> different artifact exposed
-> broader inference claimed -> contradictory evidence unavailable
-> affected party bears the resulting gap
```

It may also name instances of that sequence, but not every information asymmetry or documentation failure.

- [ ] **Step 5: Replace formal-sounding Goodhart language**

Replace “dual” with “complementary pattern” or equivalent. Preserve the useful visible/unobserved contrast without suggesting mathematical duality.

- [ ] **Step 6: Verify theory positioning and citation completeness**

Run:

```bash
rg -n "stakeholder|value-sensitive|principal-agent|information asym|decoupl|audit|complementary" section4.tex
! rg -n "dual of Goodhart|novel phenomenon|new phenomenon" section4.tex
perl -ne 'while(/\\(?:paren|text|auto)?cite\{([^}]*)\}/g){print join("\n",split(/\s*,\s*/,$1)),"\n"}' paper.tex section*.tex | sort -u > /tmp/governance-coordination-cites.txt
perl -ne 'print "$1\n" if /^\s*\@\w+\s*\{\s*([^,]+),/' references.bib | sort -u > /tmp/governance-coordination-bibkeys.txt
comm -23 /tmp/governance-coordination-cites.txt /tmp/governance-coordination-bibkeys.txt
git diff --check
```

Expected: all theory families are positioned compactly; no missing citation keys or formal-duality claim remains.

- [ ] **Step 7: Commit the conceptual positioning**

```bash
git add section4.tex references.bib
git commit -m "paper: position coordination ontology against adjacent theory"
```

---

### Task 4: Convert Diagnostics Into Coordination and Evidence-Request Sequences

**Files:**
- Modify: `section4.tex:50-end`

**Interfaces:**
- Consumes: Tasks 1–3 ontology, authority boundaries, falsifiable mechanism, and novelty claim.
- Produces: three two-layer diagnostics usable for design, procurement, supervisory inquiry, and policy coordination without pretending each question supports a finding.

- [ ] **Step 1: Preserve the three orienting questions**

Retain concise versions of:

```text
Which affected interest depends on this artifact, and what evidence would show representation?
Which categories lack contemporaneous evidence, relative to what declared scope, and what pattern results?
What access or observability changed, what artifact is offered, and who draws what inference from it?
```

Label these as orienting questions rather than examination procedures.

- [ ] **Step 2: Add the evidence-request template**

Define the eight fields from the design:

```text
objective/authority; proposition; evidentiary object; offered artifact;
method/configuration/provenance/validation/access/scope records;
supporting and defeating observations; responsible actor/remedy;
current finding versus policy/design implication.
```

Keep the template compact enough to reuse without turning the paper into Paper 3.

- [ ] **Step 3: Instantiate the template against an exact FS AI RMF control**

Use one already verified control, preferably MS-2.9.1 or MS-2.9.2. Request method-specific evidence rather than generic “fidelity to model reasoning.” Identify what the control objective supports, what further inference is being tested, and where current authority stops.

- [ ] **Step 4: Replace undefined ledger completeness with declared attestation scope**

Retain “pages missing from the ledger” as metaphor. Define its operational denominator through decision universe, category definitions, inclusion/exclusion rules, rationale, version history, operational counts, risk weighting, inventory reconciliation, and institution- and examiner-selected sampling.

- [ ] **Step 5: Address curated-diligence gaming**

Explain that raw attestation volume can camouflage consequential omissions. The diagnostic compares declared scope to operational populations, high-risk categories, boundary changes, and externally selected samples. A discrepancy is evidence about record coverage, not automatic proof of motive or violation.

- [ ] **Step 6: Remove unenforceable or categorical examination claims**

Rewrite claims that an examiner “produces findings of inadequacy” merely by asking the questions. Distinguish:

- orientation;
- evidence request under established authority;
- assessment of a claimed inference;
- formal finding under applicable law or guidance;
- policy/design recommendation outside current authority.

- [ ] **Step 7: Compress diagnostic meta-commentary**

Remove repeated architect-versus-examiner framing, repeated declarations that the three techniques compound, and claims that undiagnosable architecture is unreadable “regardless of skill.” Target at least 500 words removed from the pre-task version of `section4.tex`, net of the theory and template additions from Tasks 3–4.

- [ ] **Step 8: Verify operational boundaries**

Run:

```bash
rg -n "orienting question|objective|authority|proposition|evidentiary object|provenance|defeat|responsible actor|policy|declared.*scope|examiner-selected" section4.tex
rg -n "finding|violation|inadequacy|must|requires" section4.tex
wc -w section4.tex
git diff --check
```

Expected: the template and declared-scope safeguards appear; every remaining “finding,” “must,” or “requires” is grounded or explicitly conditional; Section 4 is materially shorter.

- [ ] **Step 9: Commit the operational diagnostics**

```bash
git add section4.tex
git commit -m "paper: translate diagnostics into evidence requests"
```

---

### Task 5: Recast Architectural Requirements as Five Evidentiary Capabilities

**Files:**
- Modify: `section5.tex:9-end`
- Modify: `section6.tex:57-75`

**Interfaces:**
- Consumes: Task 4's evidence-request and declared-scope requirements.
- Produces: five provisional capabilities with explicit outputs, limits, owners, and validation questions.

- [ ] **Step 1: Rename the section's claim status**

Replace universal or quasi-mandatory “primitive” and “requirement” language with “provisional evidentiary capability” where referring to the paper's proposals. State that capabilities may be supplied by vendors, bank-controlled systems, contracts, independent assessments, or compensating processes.

- [ ] **Step 2: Make temporal capture revision-aware**

Distinguish:

- decision-time inputs, context, actions, uncertainties, and provisional reasons;
- later reflective interpretation or discovered reasons;
- later authorization, correction, or policy reassessment.

Require separate timestamps and bindings. Later reflection may add genuine understanding but may not overwrite or impersonate the earlier record. Preserve the limit that attestation does not establish truth or completeness.

- [ ] **Step 3: Add exportability to evidence binding**

State that a community bank must be able to obtain or contract for inspectable provenance and evidence relationships from vendor-controlled systems. Association does not prove causal influence or sufficiency. Product dashboards without exportable evidence do not satisfy the proposed capability.

- [ ] **Step 4: Replace three-dimensional confidence characterization**

Rename it “non-collapsing uncertainty representation.” Remove “every assessment,” “orthogonal,” and any fixed three-dimensional necessity. Preserve distinctions among support, counterevidence, conflict, model uncertainty, missing information, and policy ambiguity. Explain why one probability alone does not identify which condition produced its value.

- [ ] **Step 5: Separate technical and institutional change**

Create parallel capabilities:

- technical-change monitoring for data, concept, and performance change;
- institutional-conformance monitoring for divergence between policy and operational practice.

State their different evidence and methods. Do not imply a shared statistical detector.

- [ ] **Step 6: Assign owners and examination burden**

For each capability, identify likely implementation and verification pathways. Examiners may inspect bank or third-party validation and selected evidence without personally performing cryptographic or model-forensic validation. Preserve the institution's responsibility for vendor-supported claims without implying unilateral implementation power.

- [ ] **Step 7: Update uncertainty boundaries**

Revise `section6.tex` to reflect five capabilities, vendor dependence, alternative implementations, unproven cost, and the possibility that coordination produces dashboards rather than evidence access. Do not repeat the full capability descriptions.

- [ ] **Step 8: Verify capability status and limits**

Run:

```bash
rg -n "provisional evidentiary capabil|decision-time|reflective|export|non-collapsing|counterevidence|technical-change|institutional-conformance|vendor|third-party" section5.tex section6.tex
! rg -n "three-dimensional confidence|orthogonal|four primitives|four requirements|institutional drift.*data drift|structural minimum|any honest implementation" section5.tex section6.tex
rg -n "does not establish|does not prove|not sufficient|unproven|alternative" section5.tex section6.tex
git diff --check
```

Expected: five capabilities and their limits appear; obsolete count, formalism, and category conflation do not.

- [ ] **Step 9: Commit the capability revision**

```bash
git add section5.tex section6.tex
git commit -m "paper: recast architecture as provisional evidence capabilities"
```

---

### Task 6: Reconcile and Compress the Full Coordination Narrative

**Files:**
- Modify: `paper.tex:73-101`
- Modify: `section1.tex`
- Modify: `section2.tex`
- Modify: `section3.tex`
- Modify: `section4.tex`
- Modify: `section5.tex`
- Modify: `section6.tex`
- Modify: `section7.tex`

**Interfaces:**
- Consumes: final ontology, mechanism, diagnostics, and capabilities from Tasks 1–5.
- Produces: one regulator-readable position paper with stable terminology and a net reduction of 600–1,000 words.

- [ ] **Step 1: Measure the pre-compression manuscript**

Run:

```bash
wc -w paper.tex section1.tex section2.tex section3.tex section4.tex section5.tex section6.tex section7.tex
```

Record the total. Final source word count must be between 12,686 and 13,086 words unless the exact TeX counting method changes; if it changes, compute the equivalent reduction against the original 13,686-word baseline.

- [ ] **Step 2: Rewrite the abstract around coordination**

The abstract must name:

- the community-bank interpretation and vendor-dependence problem;
- the three institutional participants and affected-party center;
- the artifact-to-inference ontology;
- the framework's interpretive rather than validated-method status;
- three two-layer diagnostics;
- five provisional evidentiary capabilities;
- the absence of implementation validation or new examination authority.

Keep the abstract under 300 rendered words.

- [ ] **Step 3: Compress Sections 1–3**

Apply the useful conciseness findings without copying their flattened citations. Remove repeated claims that the lens earns itself through generativity, shorten the defense of choosing BSA/AML, and integrate the pricing example as a compact policy contrast. Preserve the exact worked-control analysis and artifact taxonomy.

- [ ] **Step 4: Compress Sections 4–6**

Remove repeated declarations of scale invariance, architectural primacy, compounding techniques, and uncertainty meta-commentary. Preserve adjacent theory, falsifiers, evidence-request structure, declared scope, capability limits, and theory-of-effect uncertainty.

- [ ] **Step 5: Rewrite the conclusion as a coordination handoff**

The conclusion should show what each participant can now say or request using the ontology. Preserve the five regulator-facing questions, updated so that they distinguish orientation, authority, and remedy. End with affected-party representation rather than predicted regulatory vindication.

- [ ] **Step 6: Apply genuine copy fixes only**

Correct:

- “Pages missing from the ledger makes” to “make” or recast the subject;
- first-use expansions where the rendered paper genuinely lacks them;
- awkward direct-question grammar;
- `un-attested` to `unattested`;
- `gradually-degraded` to `gradually degraded`;
- any stale “demonstrate,” “discipline,” “method,” “primitive,” or four-item count inconsistent with the final hierarchy.

Do not edit correct LaTeX citations, references, title breaks, or author formatting in response to extraction artifacts.

- [ ] **Step 7: Verify consistency and compression**

Run:

```bash
wc -w paper.tex section1.tex section2.tex section3.tex section4.tex section5.tex section6.tex section7.tex
rg -n "translation ontology|banks|regulators|vendors|affected parties|produced absence|silence-manufacture|orienting|evidence request|provisional evidentiary capabilities" paper.tex section1.tex section7.tex
rg -n "three-dimensional|four primitives|four requirements|dual of Goodhart|demonstrates the lens|examiner.*finding of inadequacy|Pages missing from the ledger makes|un-attested|gradually-degraded" paper.tex section*.tex
git diff --check
```

Expected: final count meets the reduction target; obsolete terminology and known genuine copy errors do not remain.

- [ ] **Step 8: Commit the narrative reconciliation**

```bash
git add paper.tex section1.tex section2.tex section3.tex section4.tex section5.tex section6.tex section7.tex
git commit -m "paper: align and compress coordination narrative"
```

---

### Task 7: Clean, Build, Inspect, Package, and Test

**Files:**
- Verify: `paper.tex`, `section1.tex`–`section7.tex`, `references.bib`
- Create temporarily: rendered pages and minimal arXiv package under `mktemp -d`

**Interfaces:**
- Consumes: the complete revised manuscript.
- Produces: fresh evidence that source, rendered PDF, package, citations, labels, and repository tests pass.

- [ ] **Step 1: Verify private-source and review-artifact cleanliness**

Run:

```bash
rg -n -i "first-pass|will be reworked|staged|soften later|strawman|crackpot|Perplexity|CANDIDATE|NOT yet|citation(s)? needed|TODO|TBD|FIXME|XXX|\\[ref\\]" paper.tex section*.tex references.bib
rg -n "\\\\(needcite|quarry)" paper.tex section*.tex
```

Expected: no private drafting residue, tracking macros, or literal review-extraction artifacts. Manually inspect legitimate “not yet” phrasing before changing it.

- [ ] **Step 2: Verify citations and references**

Run:

```bash
perl -ne 'while(/\\(?:paren|text|auto)?cite\{([^}]*)\}/g){print join("\n",split(/\s*,\s*/,$1)),"\n"}' paper.tex section*.tex | sort -u > /tmp/governance-coordination-cites.txt
perl -ne 'print "$1\n" if /^\s*\@\w+\s*\{\s*([^,]+),/' references.bib | sort -u > /tmp/governance-coordination-bibkeys.txt
comm -23 /tmp/governance-coordination-cites.txt /tmp/governance-coordination-bibkeys.txt
perl -ne 'while(/\\label\{([^}]+)\}/g){print "$1\n"}' paper.tex section*.tex | sort -u > /tmp/governance-coordination-labels.txt
perl -ne 'while(/\\(?:auto|page|eq)?ref\{([^}]+)\}/g){print "$1\n"}' paper.tex section*.tex | sort -u > /tmp/governance-coordination-refs.txt
comm -23 /tmp/governance-coordination-refs.txt /tmp/governance-coordination-labels.txt
```

Expected: both `comm` commands produce no output.

- [ ] **Step 3: Perform a clean full build**

Run:

```bash
latexmk -lualatex -C paper.tex
latexmk -lualatex -interaction=nonstopmode -halt-on-error paper.tex
```

Expected: exit 0 after Biber processing and a fresh `paper.pdf`.

- [ ] **Step 4: Reject unresolved build warnings**

Run:

```bash
rg -n "LaTeX Warning|Package .* Warning|undefined|Undefined|Empty bibliography|Please \(re\)run Biber|Citation.*undefined|Reference.*undefined|Overfull|Underfull|WARN" paper.log paper.blg
```

Expected: no output. Review any match individually; do not suppress layout warnings globally.

- [ ] **Step 5: Inspect rendered content and extraction integrity**

Run:

```bash
pdfinfo paper.pdf
pdftotext -nopgbrk paper.pdf /tmp/governance-coordination-paper.txt
rg -n "Architectures of Absence|AI Governance under the FS AI RMF|July 23, 2026|Abstract|Opening Movement|Conclusion|References" /tmp/governance-coordination-paper.txt
rg -n "\\\\parencite|\\\\ref\{|\[ref\]|CITATION NEEDED|quarry" /tmp/governance-coordination-paper.txt
```

Expected: title, fixed date, and all major sections appear; no raw TeX, placeholder reference, or drafting marker appears.

Render all pages to a temporary directory. Visually inspect the title page, every section transition, evidence-request material, capability headings, conclusion, and bibliography. Confirm no clipping, blank pages, malformed special characters, or broken URLs.

- [ ] **Step 6: Build the minimal arXiv package independently**

Run:

```bash
pkg_dir=$(mktemp -d /tmp/governance-coordination-arxiv-XXXXXX)
cp paper.tex section1.tex section2.tex section3.tex section4.tex section5.tex section6.tex section7.tex references.bib "$pkg_dir/"
cd "$pkg_dir"
latexmk -lualatex -interaction=nonstopmode -halt-on-error paper.tex
rg -n "LaTeX Warning|Package .* Warning|undefined|Undefined|Empty bibliography|Please \(re\)run Biber|Citation.*undefined|Reference.*undefined|Overfull|Underfull|WARN" paper.log paper.blg
tar -czf arxiv-source.tar.gz paper.tex section1.tex section2.tex section3.tex section4.tex section5.tex section6.tex section7.tex references.bib
tar -tzf arxiv-source.tar.gz
sha256sum arxiv-source.tar.gz paper.pdf
```

Expected: package build exits 0, warning scan is empty, archive contains exactly nine source files, and checksums are reported.

- [ ] **Step 7: Run the full repository test suite**

Return to the worktree and run:

```bash
uv run pytest
```

Expected: 340 passed, 1 skipped, with only the existing scikit-learn deprecation and parameter-consistency warnings unless the test inventory has legitimately changed on the new base.

- [ ] **Step 8: Run the final coordination audit**

Confirm manually:

```text
Ontology: all participants can name the same artifact-to-inference relation.
Authority: no policy recommendation masquerades as a current finding.
Falsifiability: produced absence has supporting and defeating evidence.
Theory: adjacent concepts are credited and the narrower contribution is clear.
Diagnostics: orienting questions and evidence-request sequence are distinct.
Adversarial scope: declared denominators and external samples resist curation.
Capabilities: five hypotheses state outputs, limits, and likely owners.
Human reasoning: decision-time and reflective records remain distinct.
Reader utility: each major section advances the coordination conversation.
Scope: no experiment, full framework coding, Paper 2 build, or Paper 3 thresholds entered the revision.
```

- [ ] **Step 9: Commit only build-driven source corrections**

If source changes were required:

```bash
git add paper.tex section1.tex section2.tex section3.tex section4.tex section5.tex section6.tex section7.tex references.bib
git commit -m "paper: resolve coordination revision build findings"
```

Do not commit generated artifacts.

