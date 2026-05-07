# Handoff — Governance Position Paper, rikuy Review Setup

**HISTORICAL — superseded by `handoff_post_review.md`.** This file
captures the state when persona drafting was the next step. That work
is done. The 2026-05-06 instance ran the rikuy review pass, applied
three small paper edits, and recorded the post-review state in
`handoff_post_review.md`. Read that file first; this one is preserved
as the historical record of the design decisions made before the
review pass.

---

**For the next instance picking up this work.**

This file orients you to where the work stands so you can continue without re-deriving the design.

Last instance left off with reference block built; persona drafting is the next concrete step.

## Project at a glance

**Paper:** position paper on the CRI Financial Services AI Risk Management Framework (FS AI RMF), released by U.S. Treasury on Feb 19, 2026. Tony Mason is the author; this is the `governance/` project, separate from but related to the broader `research-program` constellation.

**Audience and register:** researcher-to-regulator. Tech report + arXiv cs.CY. Multi-venue strategy possible after initial release.

**Paper status:** drafted through Section 7 with PDFs building. Subject to a revision pass after rikuy review surfaces structural issues.

**Central frame:** *empty-chair representation* — AI governance as architectural representation of absent parties. Underlying structural pattern: *silence-manufacture* (the dual of Goodhart's law) — architectures suppress access to ground truth and produce substitute artifacts that occupy the rhetorical position where evidence would appear.

## What's been done

### Probes (completed)
- 12 candidate models probed for (a) willingness to commit to critique, (b) FS AI RMF awareness vs confabulation
- All 12 covered, 22/24 calls succeeded; 2 infrastructure failures
- Hand-scored against fixed rubrics; results captured
- Files: `probes/probe.py`, `probes/README.md`, `probes/results_*.jsonl`, `probes/scores.md`

### Source-grounding (completed)
- Treasury press release captured (Feb 19, 2026 — full text)
- CRI announcement captured (Feb 12, 2026)
- SR 26-2 / OCC Bulletin 2026-13 captured (April 17, 2026)
- FS AI RMF structural extraction: 230 COs, 4 Functions, 19 Categories, 7 Principles, 4 Stages
- Files: `citations.md`, `framework_structure.md`

### Reference block (completed this instance)
- File: `probes/reference_block.md`
- Designed for inclusion in every persona's system prompt
- Token-bounded; paid 8× per review pass

## What's next

### Step 1: Draft the 8 personas (the immediate next step)

Persona set agreed (with confidence-marked initial bias, but **assignment will be randomized after probe-shortlist** — see "Assignment policy" below):

| # | Persona | Function | Key probe-relevant constraint |
|---|---|---|---|
| 1 | Examiner | OCC/FDIC examiner pushing on misreadings of regulation; demands operational specificity | (originally constrained to disclaim group, but with reference-grounding all are eligible) |
| 2 | Vendor | Articulate, good-faith advocate for the human-on-explanation position the paper rejects | Test of paper's strongest counter-argument |
| 3 | Compliance Officer | $800M community bank, 3-person team; demands operational reality | (originally constrained; now reference-grounded) |
| 4 | Civil Rights Attorney | NCRC/NCLC register; "existing law already covers this; what's new?" | |
| 5 | Technical Reviewer | ML/AI researcher who knows Lanham/Turpin/Bordt; pushes whether technical claims exceed cited evidence | |
| 6 | Frame Skeptic | Internal coherence; does silence-manufacture hold as one pattern or three rhetorically unified | |
| 7 | Sympathetic Regulator | Generative critique — wants to operationalize this in next RMF cycle; asks what's missing for deployability | |
| 8 | Self-Examiner | Applies the paper's own diagnostic to itself: what is this paper architecturally suppressing? | |

Each persona YAML should:
- Live in `probes/personas/` (create directory)
- Follow rikuy persona schema (`name`, `reviewer_key`, `finding_prefix`, `system_prompt`)
- Use `{venue_name}` and `{venue_type}` template substitution where appropriate
- **Include the reference block from `probes/reference_block.md`** verbatim in each system prompt (paid 8× — that's intentional; grounding is load-bearing for this domain)
- Specify the persona's role, register, attack focus, and output schema (JSON array of findings)

Persona schema reference: `~/projects/rikuy/src/rikuy/personas/builtin/adversarial_methods.yaml` (and its siblings).

### Step 2: Build the rikuy config

`probes/governance.yaml` (or wherever feels right) following the schema in `~/projects/rikuy/configs/arbiter_paper.yaml`. Document path: `/home/tony/projects/governance/` (it's a LaTeX project; rikuy will read the section .tex files). Venue: `arXiv preprint` / `position paper`. **No** standard adversarial judges — only the 8 custom personas defined above. Optional: include redundancy/conciseness/copy_editor judges if useful.

### Step 3: Assignment policy (randomized)

12 candidate models; **10 usable** after probe shortlist (see `probes/scores.md`):

- **Disclaim group (6):** anthropic/claude-haiku-4.5, moonshotai/kimi-k2.6, nvidia/nemotron-3-super-120b-a12b:free, x-ai/grok-4.3, xiaomi/mimo-v2.5-pro, z-ai/glm-5.1
- **Confabulation group (4):** deepseek/deepseek-v4-pro, mistralai/mistral-large-2512, openai/gpt-oss-120b, qwen/qwen3.6-plus
- **Excluded:** google/gemini-pro-latest (invalid model ID), minimax/minimax-m2.7 awareness probe (reasoning-loop failure; willingness response was fine — usable for non-awareness-dependent personas)

**Tony's decision:** providing reference material to all personas dissolves the disclaim/confabulator distinction for assignment purposes. With reference-grounding, all 10 usable models are eligible for all 8 personas. **Use pure random assignment over the 10-model survivor set, with a recorded RNG seed for reproducibility.**

If you decide minimax should be in the pool despite its awareness-probe failure, restrict it to a non-awareness-dependent persona (Self-Examiner is a good fit — its long internal reasoning matches the role).

### Step 4: Dry-run

Before paid calls: rikuy supports `--dry-run` to print all prompts without sending. Do this first; eyeball the prompts for any reference-block insertion errors or persona prompt issues. Cost: $0.

### Step 5: Full review pass

Cost envelope Tony agreed to: ~$15. Log per-call cost (OpenRouter returns `usage` data; rikuy's JSONL captures this). If cost approaches $25, stop and check in.

**Tony's instruction:** run without persona pre-review. Iterate based on what the actual outputs surface.

### Step 6: Aggregate findings into paper revision input

Hand the JSONL output to Tony as findings. He'll decide what to do with them. Recommended deliverable: a markdown summary that groups findings by persona, severity, and section of the paper.

## Decisions Tony has made (honor these)

1. **Probe shape: single, accepted as known limitation.** Don't try to multi-shape probes for marginal rigor improvement; logged in `probe_shape_diversity: "single"`.
2. **Reference-grounding > disclaim-filtering for persona assignment.** The "alternative is to provide the reviewer with data about FS AI RMF specifics" — Tony's framing.
3. **Random assignment of model→persona, with stratified vs pure: pure now possible (since reference-grounding dissolves the eligibility constraint).** Recorded seed.
4. **Path A for paper revisions (fix issues before review pass).** But Tony does the paper revisions himself; soupervisor flags issues, doesn't draft text.
5. **No persona pre-review.** Run, react to outputs.
6. **Cost envelope: ~$15 for first pass.**
7. **The 230 control objectives number is solid.** Confirmed against the matrix (81+47+59+43=230).
8. **Treasury "release" attribution is defensible.** Treasury press release (sb0401, Feb 19, 2026) explicitly says Treasury released the FS AI RMF in partnership with FBIIC + AIEOG. CRI is the publisher/host. The paper's "U.S. Treasury's FS AI RMF" wording is slightly compressed but factually defensible; rigorous form is "released by U.S. Treasury in partnership with the Cyber Risk Institute."

## Open issues / unresolved

1. **Paper revisions on the seven-categories claim.** The framework's seven banking-domain categories are not structural axes (the framework has 4 NIST Functions + 19 Categories + 7 Trustworthy Principles + 4 Stages). The paper's seven are best understood as substantive content gloss. Tony has been informed; will adjudicate when he revises. Don't draft text; this is authorial.
2. **Two paper-actionable findings beyond verification:**
   - 78% of all 230 COs are tagged "Accountable & Transparent." Other 6 principles get 22% combined. Paper-relevant for Section 4 (silence-manufacture inside the framework itself).
   - 229 distinct AI Risk Names, all framed as absences/failures. Framework's own vocabulary IS empty-chair language. Section-4-relevant.
   - These are findings; Tony will decide if/how to incorporate.
3. **Minimal-stage CO count drift.** Guidebook says 126; matrix shows 120. Minor; flag in any paper footnote that cites the count.

## Working dynamic context

- Tony framed himself as **PI**, this instance as **research soupervisor**. PI doesn't direct execution; PI asks "what did you learn." Soupervisor reports findings, not status updates.
- Don't ask "do you want me to..." in research mode. State the criterion, take the action.
- Small reversible technical fixes are in-scope autonomous action (e.g., installing a missing dependency). Don't wait for the PI to fix what you can fix.
- When external sources fail to fetch (Treasury page timed out repeatedly on May 6), Tony can paste content from his browser; treat as last resort, not routine.
- Tony is fatigued by needle-in-haystack source-capture work. The captures in `citations.md` are designed to make this never recur for these documents.

## Files inventory

```
governance/
├── citations.md                         # All anchoring citations, full Treasury press release excerpt
├── framework_structure.md               # Full structural inventory + two paper-actionable findings
├── probes/
│   ├── README.md                        # Probe methodology
│   ├── probe.py                         # Probe runner script
│   ├── results_20260506_205537.jsonl    # Raw probe data
│   ├── scores.md                        # Hand-scored probe results
│   ├── reference_block.md               # The reference block to inject into persona prompts
│   ├── handoff.md                       # This file
│   ├── personas/                        # CREATE THIS — persona YAMLs go here
│   │   └── *.yaml                       # 8 persona files
│   └── governance.yaml                  # CREATE THIS — rikuy config
├── references/                          # Source documents (CRI, SR letters, BSA/AML, etc.)
└── [paper drafts in position-*.md and section*.tex]
```
