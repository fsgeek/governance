# Hypothesis Register

Living register of research questions, candidate hypotheses, active
preregistrations, failed claims, and superseded ideas.

This file exists to prevent silent rewriting of what the project believed, what
was tested, and what failed.

## Conventions

- **Status** describes the current standing of the item.
- **Maturity** describes where the item sits on the research ladder.
- **Linked prereg or note** should point to the most relevant record, not every
  related file.
- **Failed** does not mean "erase." It means the claim remains available for
  future calibration and theory repair.

Allowed statuses:

- `exploratory`
- `candidate`
- `active`
- `failed`
- `superseded`
- `replicated`
- `abandoned`

Allowed maturity values:

- `question`
- `characterization`
- `operationalization`
- `hypothesis`
- `experiment`
- `finding`

## Index

| ID | Title | Status | Theme | Maturity | Primary dataset / substrate | Measurement / proxy | Linked prereg or note | Last updated |
|---|---|---|---|---|---|---|---|---|
| H-001 | Outcome agreement does not imply reasoning agreement | active | disagreement | experiment | LendingClub wedge | pairwise factor-support overlap among outcome-agreers | `docs/superpowers/specs/2026-05-07-rashomon-prototype-wedge-design.md` | 2026-05-10 |
| H-002 | Vintaged policy changes predict factor-support shifts | failed | predictive content | finding | LendingClub 2014Q3 -> 2015Q4 | per-feature factor-support deltas and overlap shifts | `docs/superpowers/specs/2026-05-09-v1-v2-predictive-test-findings-note.md` | 2026-05-10 |
| H-003 | Indeterminacy is more stable than T/F across Rashomon members | failed | indeterminacy | finding | LendingClub wedge | per-case CV across members for T, F, I | `docs/superpowers/specs/2026-05-09-i-stability-falsification-findings-note.md` | 2026-05-10 |
| H-004 | SHAP is non-inferior to Rashomon for outlier-population identification | failed | SHAP comparison | finding | LendingClub V1/V2/V2_alt | Jaccard, regime signature, elevated risk population | `docs/superpowers/specs/2026-05-09-shap-vs-rashomon-result-note.md` | 2026-05-10 |
| H-005 | Indeterminacy carries governance signal independent of T/F | candidate | indeterminacy | characterization | LendingClub now, Fannie Mae next | species-specific I behavior, independence from outcome confidence | `docs/superpowers/specs/2026-05-08-indeterminacy-operationalization-memo.md` | 2026-05-10 |
| H-006 | Policy-constrained Rashomon disagreement is about policy interpretation | candidate | policy-constrained Rashomon | operationalization | thin demo policy graph, mortgage substrates | constraint-respecting set construction and within-set disagreement | `policy/README.md` | 2026-05-10 |
| H-007 | T-silent-all identifies a distinct elevated-risk population | active | disagreement | finding | LendingClub V2 | T-silent-all population rate and charge-off elevation | `docs/superpowers/specs/2026-05-09-shap-vs-rashomon-result-note.md` | 2026-05-10 |
| H-008 | Symmetry assumptions are a recurring source of preregistration failure | candidate | meta-methodology | characterization | cross-note synthesis | miss pattern across preregistered tests | `docs/superpowers/specs/2026-05-09-methodology-decomposition-retrospective.md` | 2026-05-10 |
| H-009 | Adversarial narrowing improves human adjudication over raw handoff | candidate | HITL / adjudication | question | future bank workflow substrate | adjudication time, consistency, artifact quality | `prototype-plan-2026-05-09.md` | 2026-05-10 |
| H-010 | Contemporaneous evidence capture is a stronger governance substrate than post-hoc explanation | candidate | observability / attestation | characterization | bank decision process, future attestation layer | completeness, auditability, policy simulation, drift traceability | `research-note-rashomon-from-reasoning-traces-2026-05-06.md` | 2026-05-10 |

## Entries

### H-001 — Outcome agreement does not imply reasoning agreement

**Question**  
Can models inside the same admissible Rashomon set reach the same outcome via
meaningfully different feature paths?

**Current claim**  
This remains a load-bearing active claim. It has motivated the wedge from the
start and has not yet been displaced by a stronger alternative framing.

**Why it matters**  
If it fails, a major distinction between outcome agreement and reasoning
agreement collapses. If it holds, disagreement becomes a legitimate candidate
observability signal.

**Operationalization**  
Pairwise factor-support overlap among outcome-agreers in the wedge, using
top-k features and Jaccard overlap.

**Known heterogeneity / scope limits**  
Current evidence is concentrated in LendingClub with a single model class.
Synonym features and feature-pool limitations remain a concern.

**Falsifier**  
Consistently high pairwise overlap among outcome-agreers, or low-overlap cases
that collapse under inspection into the same underlying signal.

**Status rationale**  
Still active because the wedge and related notes continue to treat this as a
live empirical question rather than a closed result.

**Evidence links**  
`docs/superpowers/specs/2026-05-07-rashomon-prototype-wedge-design.md`

### H-002 — Vintaged policy changes predict factor-support shifts

**Question**  
Can underwriting or policy changes across vintages be predicted in advance as
directional shifts in factor-support distributions?

**Current claim**  
The strong version failed in its first preregistered test.

**Why it matters**  
This was one of the cleanest ways to give the methodology predictive content
rather than descriptive texture.

**Operationalization**  
Pre-registered feature-level directional shifts and overlap changes across
LendingClub vintages V1 and V2.

**Known heterogeneity / scope limits**  
The preregistration assumed symmetry between T and F sides and relied on
partially unverified anchoring claims about policy changes.

**Falsifier**  
Observed shifts run opposite to prediction or fail on the headline side.

**Status rationale**  
Marked failed because the headline P5 claim missed and the findings note states
that it cannot be promoted without amendment.

**Evidence links**  
`docs/superpowers/specs/2026-05-09-v1-v2-predictive-test-pre-registration.md`  
`docs/superpowers/specs/2026-05-09-v1-v2-predictive-test-findings-note.md`

### H-003 — Indeterminacy is more stable than T/F across Rashomon members

**Question**  
Is I a substrate-determined signal that varies less across admissible members
than verdict channels do?

**Current claim**  
No. The early contrarian stability claim was decisively falsified.

**Why it matters**  
This would have strongly supported the four-species indeterminacy design. Its
failure materially changes the burden of proof on I.

**Operationalization**  
Per-case coefficient of variation across the five R(epsilon) members for T, F,
and the local-density I species.

**Known heterogeneity / scope limits**  
Only the local-density I species was tested per-model. Other species are not
yet in the same comparison surface.

**Falsifier**  
I CV materially exceeds T CV across available vintages.

**Status rationale**  
Marked failed because the findings note reports decisive falsification across
all three vintages.

**Evidence links**  
`docs/superpowers/specs/2026-05-08-indeterminacy-operationalization-memo.md`  
`docs/superpowers/specs/2026-05-09-i-stability-falsification-findings-note.md`

### H-004 — SHAP is non-inferior to Rashomon for outlier-population identification

**Question**  
Can a single-model SHAP-based silence criterion recover the same risky
population as the Rashomon silence signal?

**Current claim**  
The tested non-inferiority claim failed on the LendingClub comparison.

**Why it matters**  
This is the cleanest current head-to-head on a task where Rashomon plurality
should matter.

**Operationalization**  
Pre-registered SHAP-silence criteria compared against the T-silent-all
population using overlap, regime signature, and elevated charge-off rate.

**Known heterogeneity / scope limits**  
Some SHAP criteria were degenerate by construction across vintages; more clever
single-model signals remain untested.

**Falsifier**  
Any SHAP criterion recovers the population with high overlap, comparable regime
signature, and comparable downstream risk.

**Status rationale**  
Marked failed because none of the tested criteria satisfied even one leg of the
preregistered falsification standard.

**Evidence links**  
`docs/superpowers/specs/2026-05-09-shap-vs-rashomon-preregistration-note.md`  
`docs/superpowers/specs/2026-05-09-shap-vs-rashomon-result-note.md`

### H-005 — Indeterminacy carries governance signal independent of T/F

**Question**  
Does indeterminacy expose information that should not be collapsed into outcome
confidence or attribution on a single verdict channel?

**Current claim**  
Plausible and increasingly central, but not yet mature enough for a narrow
confirmatory claim.

**Why it matters**  
If true, the strongest research claim may be about governance-relevant
indeterminacy rather than about explanation alone.

**Operationalization**  
Species-specific I behavior, independence from T/F behavior, and association
with governance-relevant case properties.

**Known heterogeneity / scope limits**  
Species may behave differently; local-density results do not settle the general
claim; current evidence is still mostly LendingClub-bound.

**Falsifier**  
I species reduce trivially to T/F behavior, collapse into noise, or fail to
track any governance-relevant structure.

**Status rationale**  
Candidate because the theory is live and promising, but characterization is not
yet complete.

**Evidence links**  
`docs/superpowers/specs/2026-05-08-indeterminacy-operationalization-memo.md`  
`docs/superpowers/specs/2026-05-09-tf-mechanics-and-case-level-empty-support.md`

### H-006 — Policy-constrained Rashomon disagreement is about policy interpretation

**Question**  
Once the model class is constrained by documented policy, does disagreement
inside the set become disagreement about policy application rather than generic
model variance?

**Current claim**  
Conceptually central, not yet empirically earned.

**Why it matters**  
This is the main novelty move relative to generic disagreement-routing.

**Operationalization**  
Constraint-respecting set construction over a policy graph with monotonicity,
mandatory/prohibited features, and routing rules.

**Known heterogeneity / scope limits**  
The thin demo policy graph is illustrative, not a bank's actual production
policy. The empirical mortgage substrate is not yet the repo's dominant result
surface.

**Falsifier**  
Constraint-respecting construction adds little beyond generic model-class
restriction, or within-set disagreement remains indistinguishable from ordinary
hyperparameter variance.

**Status rationale**  
Candidate because code and docs exist, but the empirical story is still ahead
of the scaffold.

**Evidence links**  
`policy/README.md`  
`prototype-plan-2026-05-09.md`

### H-007 — T-silent-all identifies a distinct elevated-risk population

**Question**  
Does the Rashomon silence population isolate cases with materially different
downstream behavior?

**Current claim**  
Active finding on current LendingClub evidence, not yet generalized.

**Why it matters**  
This is one of the strongest current empirical legs for the plurality-aware
observability story.

**Operationalization**  
Population flagged by T-silent-all and its charge-off rate relative to base.

**Known heterogeneity / scope limits**  
Current evidence is dataset-specific and bound to the current silence
definition.

**Falsifier**  
The flagged population does not remain distinct under reruns, redefinitions, or
fresh data.

**Status rationale**  
Active because the finding exists and is load-bearing, but replication and
generalization are still open.

**Evidence links**  
`docs/superpowers/specs/2026-05-09-shap-vs-rashomon-result-note.md`  
`docs/superpowers/specs/2026-05-09-empty-support-clustering-finding-note.md`

### H-008 — Symmetry assumptions are a recurring source of preregistration failure

**Question**  
Is there a meta-pattern in which global or symmetric preregistered claims fail
because the substrate is heterogeneous?

**Current claim**  
This is a serious candidate methodological lesson, but still a cross-note
characterization rather than a confirmed theory.

**Why it matters**  
It directly affects how future hypotheses should be written.

**Operationalization**  
Cross-comparison of failures in bin-4 case reading, V1->V2 predictive testing,
and I-stability.

**Known heterogeneity / scope limits**  
The sample of failures is small and highly project-specific.

**Falsifier**  
Future asymmetry-aware preregistrations fail in the same way, or the older
misses prove unrelated on closer inspection.

**Status rationale**  
Candidate because the pattern is plausible and already shaping research design,
but has not itself been tested prospectively.

**Evidence links**  
`docs/superpowers/specs/2026-05-09-methodology-decomposition-retrospective.md`  
`docs/superpowers/specs/2026-05-09-empty-support-replication-pre-registration.md`

### H-009 — Adversarial narrowing improves human adjudication over raw handoff

**Question**  
Can AI advocates plus a neutral narrowing process improve human review quality
and efficiency relative to simple document handoff?

**Current claim**  
Too early for a formal claim; this is still a design question that should be
promoted only after workflow characterization.

**Why it matters**  
It is the main path from observability into structured HITL processing rather
than AI-as-feature sales theater.

**Operationalization**  
Adjudication time, consistency, residual artifact quality, and failure behavior
when the advocates are wrong.

**Known heterogeneity / scope limits**  
No preserved empirical workflow data yet in this repo.

**Falsifier**  
The workflow adds burden without narrowing decisions meaningfully, or it
launders unfaithful AI reasoning into persuasive summaries.

**Status rationale**  
Candidate because the concept is important but pre-empirical.

**Evidence links**  
`prototype-plan-2026-05-09.md`  
`rashomon-routed-decision-methodology.md`

### H-010 — Contemporaneous evidence capture is a stronger governance substrate than post-hoc explanation

**Question**  
Does decision-time capture of documents, notes, and attestations support better
governance than explanation generated after the fact?

**Current claim**  
Strong structural argument, weak direct empirical record inside this repo.

**Why it matters**  
This is the broader substrate claim that can remain valuable even if a narrower
Rashomon superiority argument weakens.

**Operationalization**  
Auditability, traceability, policy simulation capability, drift analysis, and
ability to reconstruct what was actually reviewed at decision time.

**Known heterogeneity / scope limits**  
This depends on the attestation substrate and on future bank-process capture not
yet represented in current code.

**Falsifier**  
Contemporaneous capture fails to produce materially better governance artifacts
or cannot be maintained reliably in practice.

**Status rationale**  
Candidate because the architecture case is strong, but empirical bank-process
evidence is still ahead of the current repo state.

**Evidence links**  
`research-note-rashomon-from-reasoning-traces-2026-05-06.md`  
`README.md`
