# Research Program

Internal working document for the research track of this repository.

This file is the stable map of the research program. It is intentionally
separate from:

- the top-level orientation README
- commercial planning documents
- manuscript drafts
- experiment-specific preregistrations
- findings notes

The purpose of this separation is epistemic. Background, active questions,
hypotheses, and results should not borrow certainty from one another.

## Purpose

The research track asks whether a governance substrate built around
contemporaneous evidence capture, policy-constrained Rashomon construction, and
indeterminacy-aware observability surfaces structure that post-hoc explanation
methods do not capture well.

This is related to, but distinct from:

- the **regulatory track**, which asks how AI governance in banking should be
  framed and evaluated
- the **commercial track**, which asks what Olorin can responsibly build and
  sell for real institutions

The research track must be allowed to fail even if the commercial substrate
remains valuable.

## Why This Research Exists

The motivating problem is not simply "interpretability."

The project begins from a stronger critique:

- post-hoc explanation may be a weak verification regime for high-stakes,
  adversarially reviewed decisions
- chain-of-thought or explainer output is not the same thing as contemporaneous
  capture of what evidence was reviewed and how a decision was formed
- a bank's own policy may be a better organizing object than a vendor-defined
  policy or a generic interpretable model class
- disagreement and indeterminacy may carry governance-relevant information that
  is not reducible to attribution on a single deployed model

This motivates three linked research directions:

1. **Rashomon and disagreement.** Whether within-set disagreement surfaces
   governance-relevant ambiguity or risk.
2. **Indeterminacy.** Whether explicit I-channel measurements expose structure
   independent of outcome confidence.
3. **Comparison.** Whether the above provide incremental value relative to
   SHAP/LIME and similar post-hoc methods.

## Current State of Understanding

The problem space is still under-characterized.

The empirical record so far includes several preregistered misses. The current
interpretation is:

- the scientific method is working
- the theory remains underfit
- early hypotheses were often too global, too symmetric, or too confident for
  the heterogeneity in the data

This program should therefore prefer staged inquiry over grand headline claims.
The immediate task is not to maximize the number of hypotheses. It is to improve
the quality and maturity of the questions that are allowed to become
hypotheses.

## Research Questions

The program currently organizes around five question families.

### 1. Disagreement and Indeterminacy as Governance Signals

- When do disagreement and indeterminacy appear?
- Are they stable across datasets, vintages, model-class choices, and policy
  constraints?
- Do they track governance-relevant phenomena such as drift, borderline policy
  fit, reviewer disagreement, elevated downstream risk, or recourse-relevant
  ambiguity?

### 2. Policy-Constrained Rashomon Construction

- What changes when the admissible model class is derived from documented bank
  policy rather than from a generic interpretable class?
- Does disagreement inside that set mean something specific about policy
  interpretation?
- Which constraints materially improve deployability and regulator alignment,
  and which merely reduce model flexibility without control value?

### 3. Comparison Against SHAP/LIME

- On what tasks should Rashomon-style observability be compared against SHAP or
  LIME?
- Which tasks are inherently single-model attribution tasks, and which are
  plurality or set-level tasks?
- Is the right research claim "superior," "complementary," or "different
  problem entirely"?

### 4. Human Adjudication and Adversarial Narrowing

- Can structured AI-mediated controversy reduce the burden on human
  adjudicators without laundering model error into persuasive rhetoric?
- Does an advocate/judge workflow produce a better residual artifact than raw
  document handoff or post-hoc explanation review?
- Which parts of a case can be safely narrowed by AI and which must remain
  fully human?

### 5. Contemporaneous Capture and Attestation

- What becomes possible when decision-time evidence, notes, and attestations
  are preserved in a tamper-evident way?
- Can contemporaneous capture support model derivation, policy simulation,
  drift detection, and external examination better than current documentation
  practice?
- Which scientific claims depend on this substrate, and which do not?

## Maturity Ladder

Topics move through the following stages:

1. **Question** — a meaningful uncertainty worth investigating
2. **Characterization** — exploratory work to identify what the phenomenon
   seems to be, where it appears, and what heterogeneity matters
3. **Operationalization** — measurements, proxies, datasets, and inclusion
   rules become concrete enough to support falsification
4. **Hypothesis** — a narrow, disposable claim with explicit falsifiers
5. **Preregistered experiment** — one dated experiment record with fixed
   predictions and decision rules
6. **Finding** — a result tied back to the preregistration and logged in the
   hypothesis register
7. **Replication** — the same or equivalent claim survives new data,
   conditions, or implementations

The hypothesis register tracks where each topic sits on this ladder.

## Promotion Rule

A topic should not become a formal hypothesis until characterization and
operationalization are mature enough to answer all of the following:

- what exactly is being measured
- which dataset or substrate is in scope
- which heterogeneity is expected rather than ignored
- what result would count as failure
- what comparison baseline is appropriate

If those are not answerable, the work stays in characterization or
operationalization. This is not a delay tactic. It is a guard against premature
formalization of poorly understood phenomena.

## Evidence Tiers

The repository uses four evidence tiers:

1. **Structural or conceptual argument**
   The claim is motivated by theory, regulatory reading, or architecture, but
   is not yet empirically established.
2. **Exploratory empirical pattern**
   A pattern appears in the data, but was not pre-registered or has not yet
   been tested against a strong falsifier.
3. **Preregistered result**
   A claim was stated in advance and then tested. The result may be positive,
   negative, or mixed. The discipline matters more than the direction.
4. **Replicated result**
   A preregistered claim or close variant survives on fresh data, new vintages,
   new model classes, or independent recomputation.

Repository documents should state or imply which tier they occupy. When in
doubt, downgrade rather than upgrade.

## Current Active Fronts

The current live fronts are:

- **Disagreement / silence populations on LendingClub**
  Current status: beyond initial discovery, still not generalized.
- **Indeterminacy operationalization**
  Current status: active operationalization with mixed empirical support and
  at least one decisive falsification of an early stability claim.
- **SHAP vs. Rashomon comparison**
  Current status: first-pass head-to-head exists on LendingClub; broader claims
  remain open.
- **Policy-constrained Rashomon construction**
  Current status: conceptually central, partially scaffolded in code and docs,
  not yet the dominant empirical substrate.
- **Fannie Mae branch**
  Current status: the likely next mortgage-relevant substrate, but not yet the
  main findings base preserved in the repo.

## Methodological Defaults

Unless a specific preregistration overrides them, the program defaults are:

- prefer local mechanism questions over global superiority claims
- treat asymmetry and heterogeneity as likely, not exceptional
- separate exploratory notes from confirmatory records
- preserve misses as first-class artifacts
- allow the commercial value of the governance substrate to survive even if a
  specific research superiority claim fails

## Workflow

Canonical research workflow in this repository:

1. Start with a research question.
2. Do characterization work and write notes that preserve what was learned.
3. Stabilize operationalization: dataset, measurements, baselines, expected
   heterogeneity, and falsifiers.
4. Promote the topic to a formal hypothesis in the hypothesis register.
5. Create a dated preregistration in `docs/research/prereg/`.
6. Run the experiment.
7. Write a findings note or result record linked to the preregistration.
8. Update the hypothesis register status without rewriting the original claim.

Git history plus the repository's OTS-backed commit hooks provide the
timestamping substrate for this workflow.

## Relationship to Existing Repository Artifacts

These documents remain valid but serve different roles:

- `README.md` — orientation for the whole repository
- `prototype-plan-2026-05-09.md` — older prototype plan and strategic framing
- `docs/superpowers/specs/` — design memos, preregistration notes, findings
  notes, and retrospectives from the current build phase
- manuscript files — policy-facing and paper-facing output, not the canonical
  research-program record

The new research layer does not replace those files immediately. It becomes the
canonical index of what they mean in the broader research program.

## Near-Term Maintenance Rule

Do not try to backfill every historical note at once.

Near-term maintenance should do only three things:

- keep the research questions current
- keep the hypothesis register honest
- ensure each new experiment has a dated preregistration record with explicit
  links to subsequent findings

Historical cleanup can happen later.
