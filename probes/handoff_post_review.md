# Handoff — Governance Position Paper, post-rikuy-review state

**For the next instance picking up this work.**

This file orients you to the post-review state of the position paper.
The earlier handoff (`handoff.md`) is now historical — it described the
state when persona drafting was next. That work is done. This file
describes what's next.

## Project at a glance

**Paper:** position paper on the CRI Financial Services AI Risk
Management Framework (FS AI RMF), released by U.S. Treasury Feb 19,
2026. Author: Tony Mason (wamason.com LLC). The `governance/` project,
related to but separate from the broader `research-program` constellation.

**Audience and register:** researcher-to-regulator. Tech report + arXiv
cs.CY. Multi-venue strategy possible after initial release.

**Paper status:** drafted through Section 7. Three small edits applied
this session (Section 1 ×2 factual fixes, Section 6.1 audience-condition
bound). Two larger revisions queued (V1.5 Section 5 extension, civil
rights frame self-application).

**Central frame:** *empty-chair representation* — AI governance as
architectural representation of absent parties. Underlying structural
pattern: *silence-manufacture* (the dual of Goodhart's law).

## What's been done in this session

### Persona reviews (rikuy + Desktop)

- 8 persona YAMLs drafted in `governance/probes/personas/` following the
  rikuy schema; reference block inlined verbatim in each. Pure random
  assignment over the 10-model survivor pool, seed 20260506, recorded
  in `assignment.json`.
- Three rikuy invocation rounds. Round 1 failed on em-dash header
  encoding (~$0). Round 2: 5/8 personas succeeded (135K tokens).
  Round 3 recovery: reassigned the 3 failed personas (deepseek for
  examiner, qwen for civil_rights_attorney, claude-haiku-4.5 dual-use
  for technical_reviewer); all 3 succeeded (87K tokens).
- Total: 57 findings (9 FATAL, 35 MAJOR, 13 MINOR) across 8 personas.
  Aggregated to `governance/probes/findings_summary.md` (627 lines, 90KB).
- Cross-vendor convergence on two pressure points: (a) silence-manufacture
  as one pattern (Frame Skeptic on conceptual unity, Sympathetic Regulator
  on operational measurability); (b) reflexive failure (Vendor on
  search-space-narrowing argument unaddressed, Self-Examiner on the paper
  not naming its own verification regime).
- Tony also ran the PDF version through Claude Desktop. Desktop's review
  validated the rikuy findings, surfaced the V1.5 reframing (synthesis
  as in-paper closure of the Vendor FATAL, not a separate research
  thread), and sharpened the civil rights frame finding (the paper is
  not currently doing what its own frame requires of the framework's
  own structural choices).

### Three edits applied to the paper

- **Section 1 paragraph 1.** Dropped "under the threshold for primary
  applicability"; added a sentence distinguishing FS AI RMF (no threshold)
  from SR 26-2 / OCC Bulletin 2026-13 (the $30B threshold belongs there).
  Closes Examiner FATAL PER-EX-001.
- **Section 1 paragraph 4.** "the regulation" → "the framework." Closes
  Examiner FATAL PER-EX-002 (the FS AI RMF is voluntary, not a regulation).
- **Section 6.1.** Added audience-condition bound to the co-optation-
  resistance claim, plus a sentence naming the wider class
  (begging-the-question, strawman fallacy as familiar instances of
  self-applying substitution-pattern terms). The structural property
  is preserved; detection-availability is now distinguished from
  detection-occurrence, with the audience supplying the latter.
  Pre-empts Frame Skeptic-adjacent overreach concerns.

### Rikuy code patches landed

Three small patches to `~/projects/rikuy/`:

- `src/rikuy/judges/adversarial.py`: added `persona_search_dirs` config
  support so persona YAMLs can live outside `rikuy/personas/builtin/`.
- `src/rikuy/core/api.py`: ASCII-coerce `X-Title` header so non-latin-1
  characters in app_label don't break HTTP requests.
- `src/rikuy/core/api.py`: `message.get("content") or ""` so explicit
  null content from refusing/refused models doesn't crash retry-loop
  length checks.

These are not committed. Tony may want to commit these as small
quality-of-life PRs to rikuy.

## What's next, in priority order

### 1. V1.5 Section 5 extension (Rashomon-from-reasoning-traces synthesis)

The Rashomon-from-reasoning-traces synthesis closes the Vendor FATAL by
demonstrating that the paper's frame is *generative* of a verification
regime that survives Rudin without collapsing into post-hoc explanation.
Section 5 currently presents architectural primitives (epistemic capture
layer) without showing what they enable; the synthesis is the natural
closure.

**IP positioning is settled.** The publication itself is the resolution:
incorporating the synthesis into the position paper and posting to arXiv
establishes the synthesis as pre-existing wamason.com IP via timestamp.
Titan retains practical license to use; ownership stays with the author
by virtue of public disclosure. The action settles the engagement-letter
ambiguity.

**Scope discipline:**
- IN scope: Rashomon search matches paths not just verdicts; connection
  to Rudin (stronger than "use interpretable models" — keep models out of
  the decision, capture interpretable substance directly, derive models
  from the corpus); path-faithful = institutional reasoning encoded in
  corpus; brief acknowledgment that this generates a verification regime
  that survives Rudin.
- OUT of scope (defer to V2 or separate working notes): drift-taxonomy
  mapping with locus-distinctness principle; counterfactual replay as
  regulatory instrument; M&A as scale-invariant use case; full
  synthetic/real data taxonomy; validation methodology open questions.

Target: 1–2 pages added to Section 5, plus a paragraph in Section 6
naming what V1.5 doesn't resolve.

Tony has explicitly granted drafting permission for paper revisions
where the criterion is "robust, defensible, genuinely insightful." That
permission applies here, but V1.5 is substantial enough that surfacing
the draft for sequential review before commit is appropriate.

The full nugget Tony shared for context lives in the conversation
record (search for "Rashomon-Derived Interpretable Models from Captured
Reasoning Traces"). It is not yet committed to a file in the
`governance/` project. The handoff instance may want to write it as
`governance/working_notes/rashomon_synthesis.md` for reference.

### 2. Civil rights frame self-application

Desktop's read of PER-CR-004 sharpens the persona finding: the paper is
not currently doing what its own frame requires of the framework's own
structural choices. The empty-chair frame says "examine the architecture
for whose interests it structurally protects." The paper does this for
*deployments* (BSA/AML, lending, pricing) but not for the FS AI RMF's
*own* CO distribution. The 3%/78% (Fair vs. Accountable & Transparent)
skew is a structural choice the framework made; it's empty-chair material
at the framework's own level.

The fix: explicit acknowledgment that empty-chair applies to the
framework's own structural choices, not just to its operationalization.
Likely lands in Section 2 or as a new subsection in Section 4. Designate
the 3% Fair controls as non-waivable statutory baselines under ECOA/FHA
where applicable.

### 3. Sympathetic Regulator's institutional-indicator (small)

PER-SR-001 surfaced the Paper-3-deferral problem: silence-manufacture has
no examiner-detectable indicator at the institutional level, and the
paper defers institutional-level detection entirely. One worked example
in V1 — say, the contested-vs-uncontested adverse-action divergence
indicator the persona suggested — would close this without committing
the paper to the full Paper 3 method.

### 4. Self-Examiner venue acknowledgment (small)

PER-SE-003 asked for a paragraph naming the paper's own verification
regime (arXiv position paper, informal community review, not peer-reviewed
journal article). One paragraph, probably in the conclusion or a short
methodological note.

### 5. V2 craft work (later, separate paper or appendix)

Drift-taxonomy ↔ projection-loss mapping with locus-distinctness as the
Frame Skeptic isomorphism demonstration. The locus-distinctness principle
is candidate for the formal apparatus that V2 uses to demonstrate
silence-manufacture as one pattern (the three instances unified at the
shared-locus-failure level, not at the surface-mechanism level). Either
a methodological appendix to V2 or a separately published working note.

## Decisions Tony has made (honor these)

These supplement the decisions in the original `handoff.md`. Honor both
sets.

1. **Reference-grounding methodology validated.** Cross-vendor
   convergence on FATAL findings across distinct vendors confirms the
   methodology produced independent triangulation, not single-model bias.
   Reference-grounding > disclaim-filtering generalizes beyond this
   review.
2. **IP via publication.** The arXiv timestamp settles the synthesis
   IP question. Titan retains practical license; wamason.com retains
   ownership by virtue of public disclosure. Engagement-letter
   clarification is now relationship-respectful but not legally required.
3. **Paper-revision drafting permission.** Tony explicitly invited
   paper revisions where the criterion is "robust, defensible, genuinely
   insightful." This relaxes the prior "soupervisor flags, doesn't draft"
   norm for high-confidence edits where the criterion is met. Larger
   edits (V1.5, civil rights frame) still benefit from sequential review
   before commit.
4. **"Want" vocabulary catches.** Reinforced this session. The criterion
   is the criterion; act on it. Reserve preference questions for things
   that genuinely depend on preference. "If you want" framing is ego-
   stroking and Tony explicitly catches it.
5. **Hold the silence-manufacture unification firmly.** Desktop's
   instruction and Frame Skeptic's craft critique both apply: hold the
   unification in V1 on present strength; sharpen the isomorphism
   demonstration in V2. The audience-condition bound just added to
   Section 6.1 is part of holding firmly while bounding honestly.

## Open issues / unresolved

These supplement the issues in the original `handoff.md`.

1. **Path representation as authored projection.** Open structural
   problem in the synthesis: what is a "reasoning path"? Sequence,
   graph, latent trajectory? The Rashomon set is well-defined only
   relative to a path representation. The interpretability story
   depends on the representation being authored, which means the
   institution has to know what its reasoning looks like before it can
   derive models that approximate it. Frameworks like the FS AI RMF
   *don't* know what their reasoning looks like. This is a deployability
   constraint and a research subproblem; flag in V1 if relevant, develop
   later.
2. **Synthetic/real boundary case (M&A integration risk).** The nugget's
   data taxonomy doesn't quite resolve hybrid cases where synthetic
   distributions are generated *from* real corpora. Worth a paragraph
   when the synthesis or M&A use case is written up.
3. **Counterfactual replay liability surface.** Presentation discipline
   ("the counterfactual is about the rule, not the prior decisions")
   depends on examiner adoption. Worth flagging in any V2 work.
4. **The Section 6.1 audience-condition bound** explicitly identifies
   the paper's audience (researcher-to-regulator, disciplined to check
   substance) as the audience the term is designed for. Worth checking
   whether this constrains generalization claims elsewhere in the paper.
5. **Two persona models excluded from this round** but available for
   future passes: nemotron-3-super-120b (free tier returned empty body,
   may have rate limited under load), kimi-k2.6 and mimo-v2.5-pro
   (returned `content: null`, possibly context-length on the 122K-char
   user prompt or content policy on the topic). With the rikuy
   `content: null` guard now in place, retries on these models would
   complete cleanly even if they decline; whether they'd produce useful
   findings is unknown.

## Working dynamic notes

- PI/soupervisor frame holds. PI asks "what did you learn"; soupervisor
  reports findings, not status. With drafting permission granted for
  high-confidence paper edits, the surface enlarges slightly: small
  reversible edits that clearly serve "robust, defensible, genuinely
  insightful" are in scope; larger structural revisions still want
  sequential review.
- Tony catches "want" framing sharply — both as a research-mode signal
  inversion and (when offering work) as ego-stroking. Reset to criterion-
  based action.
- The conversation found (re-found) that locus-distinctness keeps
  surfacing as the deep invariant across drift detection, silence-
  manufacture, and audience-conditioned term stability. Worth tracking
  as candidate principle for the formal V2 craft work.

## Files inventory

```
governance/
├── citations.md                                # All anchoring citations
├── framework_structure.md                      # Structural inventory + findings
├── section1.tex                                # EDITED (paragraphs 1 and 4)
├── section6.tex                                # EDITED (Section 6.1)
├── ... (other section files unchanged this session)
├── probes/
│   ├── README.md                               # Probe methodology
│   ├── probe.py                                # Probe runner
│   ├── results_*.jsonl                         # Probe data
│   ├── scores.md                               # Hand-scored probe results
│   ├── reference_block.md                      # Reference block (unchanged)
│   ├── handoff.md                              # Original handoff (HISTORICAL)
│   ├── handoff_post_review.md                  # THIS FILE (current state)
│   ├── personas/                               # NEW: 8 persona YAMLs
│   │   ├── examiner.yaml
│   │   ├── vendor.yaml
│   │   ├── compliance_officer.yaml
│   │   ├── civil_rights_attorney.yaml
│   │   ├── technical_reviewer.yaml
│   │   ├── frame_skeptic.yaml
│   │   ├── sympathetic_regulator.yaml
│   │   └── self_examiner.yaml
│   ├── configs/                                # NEW: 8 generated rikuy configs
│   │   └── *.yaml
│   ├── reviews/                                # NEW: per-persona JSONL outputs
│   │   ├── examiner/review_*.jsonl
│   │   └── ... (one subdir per persona)
│   ├── assignment.json                         # NEW: seeded random assignment
│   ├── run_review.py                           # NEW: pipeline runner
│   ├── run_recovery.py                         # NEW: recovery for failed personas
│   ├── aggregate.py                            # NEW: findings aggregator
│   ├── findings_summary.md                     # NEW: 57 findings, grouped
│   └── run_log.txt                             # Run output log
└── references/                                 # Source documents (unchanged)
```

Memory:

```
~/.claude/projects/-home-tony-projects-research-program/memory/
├── MEMORY.md                                   # Updated (Governance section)
└── structural_property_self_applying_terms.md  # NEW
```

Rikuy patches (uncommitted):

```
~/projects/rikuy/
├── src/rikuy/judges/adversarial.py             # +persona_search_dirs config
└── src/rikuy/core/api.py                       # +ASCII coerce + None guard
```
