# Codebook pilot result (2026-10-28). Pilot codes never enter results.

**Run:** Phi-4 Q5_K (microsoft/phi-4-gguf@6edc2ef6), local, under an `ayllu-gpu` lease announced at plaza seq 195.
25 sampled files × 5 samples at T = 0.7; 125 of 125 responses parsed, none empty, none truncated. Seed `f40f038`,
sample and runner `949194b` (both stamped, before any coding). Raw: `codes.jsonl`; tables: `report.md`.

**Reading rule.** Phi is a weak 14B coder. A disagreement counts as a codebook defect only where the codebook's own
text fails to decide the case for a careful reader. Phi's plain errors (e.g. calling tessera's P9 probe "exploratory,
excluded") are listed in `report.md` and not acted on.

## Defects found (each checked against the plan text by the steward)

1. **The unit of analysis doesn't decide.** In 8 of 25 files the number of bets differed across samples, e.g.
   `[5, 1, 6, 5, 5]`, `[7, 7, 1, 1, 1]`, `[6, 2, 6, 1, 6]`. §2 defines a bet as "a forecast about a measurement
   outcome" but never says what one bet is in a file with numbered hypotheses, several thresholds, or a table. Only
   the clause-by-clause verdict rule (yupi) touches it. **Largest defect: Q1's denominators depend on it.**
2. **No default bettor rule.** The bettor rules are per project (tessera markers, quantumos attributions). For files
   without markers (hamutay's and governance's pre-regs) the codebook is silent. Phi split AI/PI within one file
   (`framework_field_reservation`: 8 AI, 12 PI), and coded governance's and hamutay's AI-written pre-regs as PI.
   Every commit carries Tony's git identity, so authorship can't come from git. Only AI bets enter Q1.
3. **`provenance_category` applies to tessera alone but is coded everywhere.** It was stable in 3 of 25 files, with
   tessera labels ("author ruling", 40 times) put on other projects' files.
4. **Project-specific rules leak across projects.** hamutay's `8c144c0` cutoff was applied to a governance file. The
   unconditional "header STATUS lines go stale" rule sits in tessera's paragraph, so a yupi file headed "draft" was
   read as unfrozen (0 bets in all 5 samples). Coders weren't told that freeze status comes from git, not the text.
5. **Two fields lack a "none / not applicable" value.** `record_scoring_error` and `observed_vs_descended` were
   stable in 7 and 6 of 25 files, with ad-hoc values (`no`, `no_error`, `no_record_scoring_error`, ...).
6. **Outcomes can't be located mechanically for 10 of 25 files.** The harness-side rules (same directory, topic
   name, citation) found none. Outcome fields need an owner-supplied bet→outcome convention or a coder lookup step.
   One tessera probe and its result share a commit, so the record can't order them.

## Proposed codebook changes (r3; owners see them before anything is adopted)

- §2: **one bet = one id'd prediction line** (`H70`, `P1`, `S3`, a table row with an id). A file with unnumbered
  thresholds gets one bet per stated threshold. The clause rule stays. The harness lists candidate id lines
  mechanically; the coder confirms.
- §3 `bettor`, default: **an AI-written registration with no verbatim PI stake is `AI`.** Git identity never decides.
  Project markers override the default.
- §3 `provenance_category`: **`n/a` outside tessera.**
- §3: project-specific rules move into one subsection per project, given to coders only with that project's files.
  The "STATUS headers go stale; freeze comes from git" rule moves to §2 for every project, and the harness passes
  freeze status to the coder.
- §3: `record_scoring_error` and `observed_vs_descended` get explicit `none` and `n/a` values.
- §2: each owner names its bet→outcome convention (or confirms the harness rule) at the §8 check.

The schedule forecast's S7 ("the pilot changes at least 3 codebook fields or rules", p = 0.80) is scored when owners
adopt or reject these changes, not here.
