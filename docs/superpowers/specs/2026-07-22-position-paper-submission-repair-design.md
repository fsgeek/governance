# Position Paper Submission Repair Design

**Status:** active  
**Authority:** canonical for the bounded arXiv submission repair  
**Depends on:** `paper.tex`, `section1.tex` through `section7.tex`, `references.bib`, the FS AI RMF primary materials in `references/`  
**Invalidated by:** none yet  
**Last reconciled with manuscript:** 2026-07-22

## Purpose

Prepare *Architectures of Absence: AI Governance under the FS AI RMF* for responsible arXiv submission without reopening the research program or delaying the policy-constrained Rashomon work indefinitely.

The repaired paper should let a regulator recognize a familiar governance practice, discover an evidentiary gap, understand why the gap matters, and leave with a distinction or diagnostic question they can use. The paper should be engaging without theatrical accusation, informative without becoming dry, and forceful only where its evidence and structural argument warrant force.

## Audience and Register

The primary reader is a regulator, examiner, model-risk practitioner, or governance architect familiar with financial-institution constraints.

Use a **regulatory analytic voice**:

- direct, concrete, and inspectable;
- respectful of regulatory and institutional practice without presuming cooperative evidence where verification is required;
- firm about what an artifact does and does not establish;
- curious and discovery-oriented rather than accusatory;
- technically precise without requiring the reader to adopt the paper's vocabulary in advance.

The recurring narrative movement is:

1. Present a recognizable governance artifact or practice.
2. State what the artifact genuinely establishes.
3. Identify the additional conclusion commonly drawn from it.
4. Show why that inference does not follow.
5. State what evidence or architecture would close or honestly disclose the gap.
6. Name the recurring structure as silence-manufacture only after demonstrating it.

Rhetorical labels such as “governance theater,” “Potemkin accountability,” and “dishonest middle” must not carry the argument. Retain a strong phrase only when it names a precise structure already demonstrated in the surrounding text.

## Preserved Contributions

The repair preserves:

- empty-chair representation;
- the distinction between structural and produced absence;
- silence-manufacture;
- the three diagnostic techniques;
- the four provisional architectural requirements;
- the claim that reviewing an explanation does not, by itself, verify the process represented by that explanation.

Preservation does not require retaining every current formulation. A contribution may be restated, relocated, or narrowed so long as its substantive role remains.

## Revision Architecture

### 1. Establish the primary-source spine

Every worked FS AI RMF example must identify the exact Control Objective ID or IDs from which it is derived.

For every example, distinguish explicitly among:

- Control Objective name and description;
- framework implementation guidance;
- framework example controls or effective evidence;
- the paper's own hypothetical or composite implementation.

Do not present an author-created composite as framework text. If a current example cannot be bound to an adequate source, replace it with a traceable example rather than expanding the research scope.

### 2. Build the verification-artifact taxonomy

Define the evidentiary objects that the current manuscript sometimes collapses into “reasoning.” At minimum, distinguish:

- decision inputs and context;
- functional feature dependence;
- local behavioral approximation;
- internal computational state;
- generated rationale;
- human deliberative record;
- institutional authorization and review.

For each relevant artifact, state what it can establish and what it cannot establish by itself. Treat SHAP, LIME, attention attribution, chain-of-thought, ante-hoc interpretable models, contemporaneous human records, and institutional attestations according to their distinct mechanisms. Do not use evidence about one explanation class as direct confirmation of all classes.

The shared structural question is whether the conclusion attributed to an artifact exceeds the evidence the artifact warrants.

### 3. Recast worked examples as discoveries

Each principal example should follow the narrative movement specified above. Empty-chair representation identifies whose interest makes an evidentiary gap consequential. Silence-manufacture identifies the recurring pattern in which suppressed access and a substitute artifact support an inference that the artifact cannot warrant.

Claims about bad motives are outside scope unless evidence specifically establishes motive. Analyze artifacts, architecture, incentives, and warranted inference instead.

### 4. Propagate precision through the architecture

Give bounded meanings to “reasoning,” “verification,” “representation,” and “ground truth,” or replace them with more precise terms where a single definition would conceal material differences.

Present the four primitives as architectural requirements generated by the empty-chair frame and the diagnostic techniques, not as universally proven necessities. Preserve categorical language only where the paper establishes a structural boundary; otherwise identify a proposition, interpretation, or falsifiable prediction as such at the point where it appears.

### 5. Compress and close

Shorten Section 6 to uncertainties a regulator needs in order to interpret or use this paper responsibly. Remove detailed Rashomon experimental history from the main argument unless a result directly bounds a claim made in this paper. Relocated material may be preserved in an existing research note or a clearly identified companion artifact; this repair does not create a new empirical paper.

Revise the conclusion to provide a usable regulatory or examination posture. Do not rely on predictions that regulatory evolution will inevitably vindicate the paper.

## Explicit Scope Boundary

The repair includes only work necessary to:

- bind framework examples to primary sources;
- correct the explanation and verification taxonomy;
- define or replace ambiguous verification targets;
- reconcile claims with the paper's stated uncertainties;
- improve the regulator-facing narrative where those repairs touch it;
- clean and verify the archival submission package.

The repair excludes:

- new experiments;
- a systematic coding of all 230 control objectives;
- proof or implementation of the four architectural requirements;
- redesign of the three-paper sequence;
- a new general literature review except where a missing source is necessary to support a repaired load-bearing claim;
- global stylistic polishing unrelated to a submission gate;
- attempts to make the paper immune to disagreement or criticism.

A proposed change belongs in this repair only if it resolves a submission gate or corrects an error encountered while resolving one.

## Validation

The manuscript must pass three substantive checks:

### Traceability

A reader can follow every interpretation of the FS AI RMF to the relevant primary-source objective, guidance, example control, or evidence provision, and can distinguish source content from author analysis.

### Inference discipline

Every explanation, observation, attestation, or record supports the conclusion attributed to it. Limitations are stated where the claim occurs, not repaired only by a later uncertainty section.

### Reader utility

Each major section leaves a regulator with a usable question, distinction, examination test, or architectural implication. Engagement comes from discovery and consequence, not rhetorical escalation.

## Archival and Build Gate

Before submission:

- remove private drafting comments, stale status notes, internal review residue, and unused tracking macros from the public source;
- verify every cited bibliography entry against its source and correct entry types and metadata;
- cite the FS AI RMF primary materials for framework-specific claims;
- replace `\today` with a fixed manuscript date;
- compile the full paper with a LuaLaTeX/Biber toolchain compatible with arXiv;
- resolve build errors and inspect all warnings;
- inspect the rendered PDF for references, typography, links, and accidental drafting artifacts;
- build and test a minimal arXiv source package containing only required files.

If the local environment cannot provide the required toolchain, compilation remains an open gate rather than being inferred from source inspection.

## Completion Condition

The repair is complete when all substantive validation checks and the archival/build gate pass. Completion does not require eliminating vulnerability, disagreement, or open questions. Once these gates pass, the paper should be submitted rather than reopened for unbounded improvement.
