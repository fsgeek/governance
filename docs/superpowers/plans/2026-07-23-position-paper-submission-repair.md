# Position Paper Submission Repair Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce a regulator-readable, evidentially traceable, technically precise, and arXiv-ready version of *Architectures of Absence: AI Governance under the FS AI RMF* without reopening the wider research program.

**Architecture:** Repair the manuscript in dependency order: bind the worked examples to the primary framework, introduce a verification-artifact taxonomy, propagate that precision through the diagnostic and architectural claims, then compress the uncertainties and reconcile the opening and conclusion. Finish with an independent source/bibliography audit and a clean LuaLaTeX/Biber plus minimal-package build.

**Tech Stack:** LaTeX (`paper.tex`, `section1.tex`–`section7.tex`), `biblatex`/Biber (`references.bib`), CRI FS AI RMF DOCX primary materials in `references/`, shell source checks with `rg`/`perl`, LuaLaTeX/`latexmk`, arXiv TeX source packaging.

## Global Constraints

- Use a regulatory analytic voice: direct, concrete, inspectable, curious, and discovery-oriented.
- Preserve empty-chair representation, structural versus produced absence, silence-manufacture, the three diagnostic techniques, the four provisional architectural requirements, and the bounded human-review claim.
- Do not add experiments, code all 230 objectives, implement the primitives, redesign the paper sequence, or perform unrelated global polishing.
- Do not present author-created composites as FS AI RMF text.
- Do not use evidence about one explanation class as direct confirmation of every explanation class.
- Limit changes to submission-gate repairs and errors encountered while making them.
- Commit after every independently reviewable task; do not combine tasks into one manuscript-wide commit.

---

### Task 1: Bind the Worked Examples to the FS AI RMF

**Files:**
- Modify: `section2.tex:49-81`
- Modify: `references.bib:246-265,347-354`
- Consult: `references/CRI-FS-AI-RMF-Control-Objective-Reference-Guide_Full_v.1.0-1.docx`
- Consult: `references/CRI-FS-AI-RMF-Guidebook_Full_v.1.0-1.docx`

**Interfaces:**
- Consumes: CRI control-objective names, descriptions, implementation guidance, and example controls.
- Produces: Three traceable worked examples that later sections may cite as established applications of the frame.

- [ ] **Step 1: Record the exact source text for the three replacement examples**

Extract and review these objectives from the full Control Objective Reference Guide:

```text
GV-1.6.1 — AI Inventory Management
GV-3.2.2 — Monitoring Human-AI Oversight
MS-2.9.1 — Model Explainability and Validation
MS-2.9.2 — Interpretability and Decision Context
```

Use the objective description plus only the implementation-guidance/example-control text needed to determine what the framework actually says. Treat MS-2.9.1 and MS-2.9.2 as a paired example if the analysis depends on both model explanation and human interpretation.

- [ ] **Step 2: Verify that the current three formulations are not source quotations**

Run:

```bash
rg -n "drift in detection rates|training data provenance|reviewer reasoning sufficient" section2.tex
```

Expected: three current author-created formulations at lines near 54, 62, and 68. Confirm that none occurs verbatim in the full guide before replacing them.

- [ ] **Step 3: Rewrite the subsection's source-status paragraph**

Replace the assertion that identifiers would make the analysis brittle with a paragraph that:

```text
- names every Control Objective ID;
- states that the objectives are cross-sector governance requirements, not BSA/AML-specific controls;
- identifies the BSA/AML transaction-monitoring scenario as the paper's application of those objectives;
- distinguishes objective text, framework guidance/examples, and the paper's hypothetical implementation.
```

- [ ] **Step 4: Rewrite the three examples in discovery order**

For each example, use this exact argumentative sequence:

```text
1. What the named objective requires.
2. What evidence compliance with that objective genuinely establishes.
3. What additional inference an institution or examiner might make.
4. Why that additional inference is not established by the artifact alone.
5. Which empty chair bears the consequence.
6. What additional evidence would close or disclose the gap.
```

Use GV-1.6.1 for the inventory example, GV-3.2.2 for the human-oversight example, and MS-2.9.1/MS-2.9.2 for the explanation-and-interpretation example. Do not claim the framework text requires transaction-monitoring thresholds, reviewer thought capture, or population-decomposed false-positive rates unless the cited source does so.

- [ ] **Step 5: Correct the primary framework bibliography entry**

Update `fssccFSAIRMF2026` so its title, corporate authorship, version, February 2026 date, and official public URL identify the full Control Objective Reference Guide. Retain `treasuryFSAIRMFRelease2026` for the release date only. Cite `fssccFSAIRMF2026` in the worked examples and wherever the manuscript attributes content to the 230 objectives.

- [ ] **Step 6: Run the traceability check**

Run:

```bash
rg -n "GV-1\.6\.1|GV-3\.2\.2|MS-2\.9\.1|MS-2\.9\.2|fssccFSAIRMF2026" section2.tex references.bib
rg -n "We do not specify the exact control numbers|Control: monitoring system|Control: AI components|Control: human review" section2.tex
```

Expected: all selected IDs and the primary citation appear; none of the four obsolete strings remains.

- [ ] **Step 7: Commit the source-bound examples**

```bash
git add section2.tex references.bib
git commit -m "paper: bind worked examples to FS AI RMF controls"
```

---

### Task 2: Define the Verification-Artifact Taxonomy

**Files:**
- Modify: `section1.tex:16-36`
- Modify: `section3.tex:17-33`
- Modify: `section3.tex:63-84`
- Modify: `references.bib`

**Interfaces:**
- Consumes: The paper's current definition of verification regime and its Bordt, Rudin, Slack, Lanham, Turpin, and Oh sources.
- Produces: A stable vocabulary used by Tasks 3–6 to replace the overloaded term “reasoning.”

- [ ] **Step 1: Inventory the overloaded vocabulary**

Run:

```bash
rg -n -i "reasoning|ground truth|verification|explanation channel|underlying computation" paper.tex section*.tex
```

Classify each material occurrence into one of these seven objects:

```text
decision inputs and context
functional feature dependence
local behavioral approximation
internal computational state
generated rationale
human deliberative record
institutional authorization and review
```

- [ ] **Step 2: Add a compact taxonomy after the verification-regime definition**

Write a regulator-readable passage that defines the seven objects and makes this distinction explicit:

```text
An artifact may faithfully establish one object without establishing another.
The relevant governance question is therefore not whether an explanation exists,
but which evidentiary object it represents and which inference the recipient is
being asked to draw from it.
```

Use prose rather than a large formal table unless the rendered comparison is materially clearer as a table.

- [ ] **Step 3: State method-specific capabilities and limits**

Ensure the taxonomy says, without treating the methods as equivalent:

```text
SHAP: attributes model output under a specified value-function/background construction; it does not by itself recover a human deliberative record or prove causal model-internal reasoning.
LIME: locally approximates model behavior around a selected neighborhood; its warrant is local and depends on the perturbation and surrogate construction.
Attention attribution: exposes selected internal quantities; attention weight alone is not a complete account of computational causation.
Chain-of-thought: is generated text and may be unfaithful to the computation producing the answer.
Ante-hoc interpretable models: expose a decision function more directly, but policy validity and evidence provenance remain separate questions.
Contemporaneous human records: document what was consulted or recorded at decision time, but do not provide transparent access to every cognitive process.
Institutional attestations: establish that an authorized actor made a recorded commitment; they establish the truth of the attested content only when supported by bound evidence.
```

- [ ] **Step 4: Reframe the two categoricals**

Replace the universal “post-hoc explanation is structurally inadequate” formulation with the narrower structural boundary:

```text
An explanation artifact is not, by itself, a verification regime for a different evidentiary object. In adversarial review, the binding between the artifact, the claimed object, and the decision must itself be inspectable.
```

Retain the human-review claim in this bounded form:

```text
Review of an explanation verifies that the explanation was reviewed; it does not by itself verify a decision process that the explanation does not faithfully represent.
```

- [ ] **Step 5: Check source-to-claim alignment**

Confirm Bordt supports the adversarial-context argument, Rudin/Slack support the relevant post-hoc limitations, and Lanham/Turpin are used only for generated chain-of-thought. Preserve Oh as a counterposition where the paper acknowledges legitimate uses of post-hoc explanation. Add a new reference only if a specific taxonomy claim otherwise lacks necessary support.

- [ ] **Step 6: Run the taxonomy checks**

Run:

```bash
rg -n "functional feature dependence|local behavioral approximation|internal computational state|generated rationale|human deliberative record|institutional authorization" section1.tex section3.tex
rg -n "post-hoc explanation is structurally inadequate" paper.tex section*.tex
```

Expected: all seven objects are represented in the revised taxonomy; the obsolete universal formulation does not remain in active prose.

- [ ] **Step 7: Commit the taxonomy**

```bash
git add section1.tex section3.tex references.bib
git commit -m "paper: distinguish explanation and verification artifacts"
```

---

### Task 3: Rebuild Silence-Manufacture Around Warranted Inference

**Files:**
- Modify: `section4.tex:26-117`
- Modify: `section4.tex:119-end` where diagnostic techniques rely on “reasoning” or “ground truth”

**Interfaces:**
- Consumes: Task 2's verification-artifact taxonomy and Task 1's source-bound examples.
- Produces: A technically accurate silence-manufacture mechanism and three usable regulator-facing diagnostics.

- [ ] **Step 1: Remove the false common-mechanism sentence**

Delete the claim that SHAP, LIME, attention attribution, and chain-of-thought are “generated by the same loop that produced the decision.” Do not replace it with a different single technical mechanism.

- [ ] **Step 2: Define the shared mechanism as an inference gap**

Reconstruct the mapping around this sequence:

```text
access to a relevant evidentiary object is unavailable or suppressed;
a different artifact is produced and may be valuable on its own terms;
the artifact is treated as establishing the unavailable object;
the absence of contradictory evidence is taken as support for that inference.
```

Make clear that silence-manufacture concerns the unwarranted substitution, not the mere existence of explanations, documentation, metrics, or attestations.

- [ ] **Step 3: Separate empirical support by explanation class**

Use chain-of-thought faithfulness results only for generated rationales. Use Slack for adversarial manipulation of post-hoc explanations. Describe SHAP/LIME limitations in terms of their own targets and assumptions. Do not call the combined evidence “direct empirical confirmation” of a universal claim.

- [ ] **Step 4: Recast the three predictions as propositions**

Change “fails predictably,” “are the signature,” and “should be expected” into explicitly identified propositions generated by the frame. State what observation would count against each proposition. Keep the de-banking case as an illustration rather than proof of a general law.

- [ ] **Step 5: Make each diagnostic technique operational for a regulator**

End each technique with one concise examination question:

```text
Technique 1: Which absent party depends on this artifact, and what evidence would show that the implementation represents that party's interest?
Technique 2: Which decision categories lack contemporaneous evidence, was that absence declared in advance, and what pattern do the absences form?
Technique 3: What access did the architecture remove, what artifact replaced it, and what inference is being drawn from the replacement?
```

- [ ] **Step 6: Run rhetoric and inference checks**

Run:

```bash
rg -n -i "same loop|direct empirical confirmation|fails predictably|are the signature|ground truth" section4.tex
rg -n "Which absent party|Which decision categories|What access did the architecture" section4.tex
```

Expected: obsolete universal/mechanism language is removed or explicitly bounded; all three examination questions appear.

- [ ] **Step 7: Commit the diagnostic repair**

```bash
git add section4.tex
git commit -m "paper: ground silence-manufacture in warranted inference"
```

---

### Task 4: Align the Architectural Requirements With the Taxonomy

**Files:**
- Modify: `section5.tex:18-106`

**Interfaces:**
- Consumes: Task 2's evidentiary objects and Task 3's diagnostic questions.
- Produces: Four bounded architectural requirements whose functions and limits are explicit.

- [ ] **Step 1: Replace universal-minimum language**

Rewrite “requires,” “any honest implementation must,” and “structural minimum” where those phrases assert universal necessity. State instead that these are requirements generated by this frame for architectures intended to support the three diagnostics.

- [ ] **Step 2: Define the evidentiary output of each requirement**

For each requirement, state what it establishes and what it does not:

```text
Tamper-evident temporal capture establishes when particular content was committed and whether it changed; it does not establish that the content is complete or true.
Evidence binding establishes a traversable declared relationship between a decision and preserved evidence; it does not by itself prove causal influence or evidentiary sufficiency.
Three-dimensional characterization preserves support, counter-support, and insufficiency as distinct reported states; the paper proposes this representation rather than proving it is the only honest formalism.
Structural drift typology separates kinds of change that call for different investigation; detecting a drift type does not establish its cause.
```

- [ ] **Step 3: Replace “underlying reasoning” with the relevant object**

At each occurrence, name decision inputs/context, functional dependence, generated rationale, human deliberative record, or institutional attestation as appropriate. Do not claim temporal capture makes cognition or model-internal computation inspectable.

- [ ] **Step 4: Preserve the explanation-binding warning precisely**

State that binding an explanation to a decision proves the explanation was associated with that decision. Whether it supports a further conclusion depends on the explanation method, its target, its configuration, and the claimed inference.

- [ ] **Step 5: Remove hidden implementation quarry from the submitted paper**

Delete the four `\quarry{}` implementation paragraphs from the position paper after confirming their content already exists in planning material or version history. Do not create Paper 2 during this task.

- [ ] **Step 6: Run architectural-boundary checks**

Run:

```bash
rg -n "any honest implementation must|structural minimum|underlying reasoning|\\\\quarry" section5.tex
rg -n "does not establish|does not by itself|rather than proving|does not establish its cause" section5.tex
```

Expected: no quarry or obsolete universal phrases remain; all four requirement limits are present.

- [ ] **Step 7: Commit the architectural repair**

```bash
git add section5.tex
git commit -m "paper: bound architectural requirements to their evidence"
```

---

### Task 5: Compress Honest Uncertainties to Reader-Relevant Boundaries

**Files:**
- Modify: `section6.tex:1-end`
- Preserve if needed: existing empirical notes under `docs/superpowers/specs/` and `working_notes/`

**Interfaces:**
- Consumes: The bounded claims produced by Tasks 1–4.
- Produces: A shorter uncertainty section that helps regulators use the frame without carrying the Rashomon research history.

- [ ] **Step 1: Mark the uncertainties that directly govern this paper**

Retain concise treatment of:

```text
open empty-chair enumeration and weighting;
non-exhaustiveness of structural versus produced absence;
limits on generalization beyond the worked financial contexts;
the distinction between adversarial and cooperative examination contexts;
resource and coordination limits on examination practice;
non-exhaustiveness and unproven tractability of the four architectural requirements;
the paper's theory-of-effect uncertainty.
```

- [ ] **Step 2: Remove the empirical research-history digression**

Remove detailed Fannie Mae/HMDA trimodal transfer, adequacy-threshold, vintage concentration, detector, and knob-robustness narratives from Section 6 unless one sentence is necessary to prevent a specific claim in this paper from overstating empirical generality. Do not delete the underlying preregistration/result notes or bibliography records used elsewhere.

- [ ] **Step 3: Eliminate uncertainty-after-overstatement structure**

For each retained uncertainty, confirm Tasks 1–4 already bounded the corresponding claim where it first appears. Section 6 should explain responsible use, not retract earlier prose.

- [ ] **Step 4: Target a material reduction**

Run before and after:

```bash
wc -w section6.tex
```

Expected after revision: no more than 2,400 words, while retaining every reader-relevant uncertainty listed in Step 1.

- [ ] **Step 5: Remove stale drafting comments**

Delete the first-pass status block, “will be reworked,” staged-edit notes, and citation wish list at the top of `section6.tex`.

- [ ] **Step 6: Commit the compressed uncertainties**

```bash
git add section6.tex
git commit -m "paper: focus uncertainties on regulator use"
```

---

### Task 6: Reconcile the Opening, Abstract, and Conclusion

**Files:**
- Modify: `paper.tex:68-92`
- Modify: `section1.tex:1-36`
- Modify: `section7.tex:1-38`

**Interfaces:**
- Consumes: Final terminology and claim boundaries from Tasks 1–5.
- Produces: One coherent regulator-facing narrative from abstract through conclusion.

- [ ] **Step 1: Rewrite the abstract to match the repaired contribution**

The abstract must:

```text
identify the FS AI RMF and community-bank interpretation problem;
present empty-chair representation as a proposed organizing lens demonstrated through worked examples;
state the artifact-to-inference gap as the central verification problem;
name the diagnostics and provisional architectural requirements without claiming implementation validation;
avoid claiming that governed architectures generally fail in one universal way;
retain the planned-paper-sequence statement only if it helps readers understand scope.
```

- [ ] **Step 2: Make the opening invite discovery**

Preserve the opening's practical problem and empty-chair examples. Replace categorical declarations that precede the taxonomy with the recognizable-artifact → warranted-inference → gap sequence. Ensure the opening promises only what Sections 2–5 now deliver.

- [ ] **Step 3: Replace motive-laden rhetoric where it carries the argument**

Run:

```bash
rg -n -i "Potemkin|dishonest middle|decoration|theater|will not survive|increasingly recognizes|forces honest" paper.tex section1.tex section7.tex
```

For each occurrence, retain it only if the surrounding paragraph has already demonstrated the precise structure. Otherwise replace it with artifact-and-inference language.

- [ ] **Step 4: Rewrite the conclusion as an examination posture**

End with a compact set of regulator-usable questions:

```text
What evidentiary object does this artifact expose?
What conclusion is the institution asking the examiner to draw from it?
What binds the artifact to that conclusion?
Whose interest bears the cost if the binding is absent?
What additional evidence would close or honestly disclose the gap?
```

Preserve a memorable closing sentence only if it follows from these questions without predicting inevitable regulatory vindication.

- [ ] **Step 5: Check cross-document consistency**

Run:

```bash
rg -n "post-hoc explanation is structurally inadequate|underlying reasoning|will not survive the recognition|structural minimum" paper.tex section*.tex
rg -n "empty-chair representation|silence-manufacture|verification" paper.tex section1.tex section7.tex
```

Expected: obsolete universal formulations are absent; the central concepts appear consistently in the abstract, opening, and conclusion.

- [ ] **Step 6: Commit the narrative reconciliation**

```bash
git add paper.tex section1.tex section7.tex
git commit -m "paper: align narrative for regulatory readers"
```

---

### Task 7: Clean and Verify the Archival Source

**Files:**
- Modify: `paper.tex`
- Modify: `section1.tex`–`section7.tex`
- Modify: `references.bib`

**Interfaces:**
- Consumes: The complete repaired manuscript.
- Produces: Public-source-safe TeX and a verified cited bibliography.

- [ ] **Step 1: Remove private drafting residue**

Remove status headers, internal reviewer names, staged candidates, “soften later,” “strawman,” “crackpot author,” citation wish lists, and unused reserve-entry comments from files intended for arXiv.

Run:

```bash
rg -n -i "first-pass|will be reworked|staged|soften later|strawman|crackpot|Perplexity|CANDIDATE|NOT yet|citation(s)? needed|TODO|TBD|FIXME|XXX" paper.tex section*.tex references.bib
```

Expected: no private drafting residue remains. A legitimate use of “candidate” or “staged” in published prose must be reviewed manually rather than removed mechanically.

- [ ] **Step 2: Remove unused tracking machinery and freeze the date**

Delete `\needcite` and `\quarry` definitions after confirming they have no uses. Replace `\date{\today}` with `\date{July 23, 2026}`; do not allow rebuilds to change it.

- [ ] **Step 3: Verify citation-key completeness**

Run:

```bash
perl -ne 'while(/\\(?:paren|text|auto)?cite\{([^}]*)\}/g){print join("\n",split(/\s*,\s*/,$1)),"\n"}' paper.tex section*.tex | sort -u > /tmp/governance-cites.txt
perl -ne 'print "$1\n" if /^\s*\@\w+\s*\{\s*([^,]+),/' references.bib | sort -u > /tmp/governance-bibkeys.txt
comm -23 /tmp/governance-cites.txt /tmp/governance-bibkeys.txt
```

Expected: no output.

- [ ] **Step 4: Verify every cited bibliography record**

For each key in `/tmp/governance-cites.txt`, check author/corporate author, title, year, venue or issuing body, identifier/URL, and entry type against the primary publication record. Correct at least the currently malformed `perez2022` entry (key/year/type/venue consistency), the incomplete Witzel report metadata, and framework-source attribution. Remove uncited reserve entries if they add source-package noise.

- [ ] **Step 5: Verify references and labels**

Run:

```bash
perl -ne 'while(/\\label\{([^}]+)\}/g){print "$1\n"}' paper.tex section*.tex | sort -u > /tmp/governance-labels.txt
perl -ne 'while(/\\(?:auto|page|eq)?ref\{([^}]+)\}/g){print "$1\n"}' paper.tex section*.tex | sort -u > /tmp/governance-refs.txt
comm -23 /tmp/governance-refs.txt /tmp/governance-labels.txt
git diff --check
```

Expected: no missing labels and no whitespace errors.

- [ ] **Step 6: Commit archival cleanup**

```bash
git add paper.tex section1.tex section2.tex section3.tex section4.tex section5.tex section6.tex section7.tex references.bib
git commit -m "paper: clean archival source and references"
```

---

### Task 8: Build, Inspect, and Package for arXiv

**Files:**
- Verify: `paper.tex`, `section1.tex`–`section7.tex`, `references.bib`
- Create temporarily outside the repository or in an ignored temporary directory: minimal arXiv package

**Interfaces:**
- Consumes: Clean manuscript source from Task 7.
- Produces: Fresh build evidence, rendered-PDF inspection results, and a tested minimal arXiv source archive.

- [ ] **Step 1: Confirm the required toolchain**

Run:

```bash
command -v latexmk
command -v lualatex
command -v biber
```

Expected: all three commands resolve. If any is absent, install/use a compatible TeX Live environment or stop and report the build gate as open; do not infer success from source checks.

- [ ] **Step 2: Perform a clean full build**

Run:

```bash
latexmk -lualatex -C paper.tex
latexmk -lualatex -interaction=nonstopmode -halt-on-error paper.tex
```

Expected: exit 0 and `paper.pdf` produced after Biber processing.

- [ ] **Step 3: Inspect warnings**

Run:

```bash
rg -n "LaTeX Warning|Package .* Warning|undefined|Undefined|Empty bibliography|Please \(re\)run Biber|Citation.*undefined|Reference.*undefined|Overfull|Underfull" paper.log paper.blg paper.bbl
```

Expected: no undefined citations/references, Biber rerun requests, empty bibliography, or content-truncating layout warnings. Review overfull/underfull boxes individually rather than suppressing them globally.

- [ ] **Step 4: Inspect the rendered PDF**

Render or open the PDF and verify:

```text
title, fixed date, and author metadata;
abstract and section order;
all citations and bibliography rendering;
cross-reference links;
special characters and section symbols;
absence of [CITATION NEEDED], quarry text, comments, or drafting residue;
no clipped text, blank pages, or malformed URLs.
```

- [ ] **Step 5: Create the minimal source package**

Use a temporary directory created with `mktemp -d`. Copy only:

```text
paper.tex
section1.tex
section2.tex
section3.tex
section4.tex
section5.tex
section6.tex
section7.tex
references.bib
```

Include `paper.bbl` only if required after testing arXiv's automatic Biber path; if included, it must be produced by the same Biber/biblatex-compatible toolchain as the manuscript.

- [ ] **Step 6: Build from the package alone**

From the temporary package directory, run:

```bash
latexmk -lualatex -interaction=nonstopmode -halt-on-error paper.tex
```

Expected: exit 0 without reaching into the repository for undeclared inputs.

- [ ] **Step 7: Run the final submission-gate audit**

Confirm:

```text
Traceability: every FS AI RMF interpretation names its primary objective/source status.
Inference discipline: every artifact supports only the conclusion attributed to it.
Reader utility: each major section leaves a regulator with a usable distinction or question.
Scope: no new experiment, 230-control coding, implementation project, or unrelated rewrite entered the repair.
Build: clean full and minimal-package builds both exited 0.
```

- [ ] **Step 8: Commit only any build-driven source corrections**

If the build required source changes:

```bash
git add paper.tex section1.tex section2.tex section3.tex section4.tex section5.tex section6.tex section7.tex references.bib
git commit -m "paper: resolve final arXiv build findings"
```

Do not commit generated PDFs, auxiliary files, logs, or the temporary package.
