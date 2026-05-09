# Conversation Residue Capture — 2026-05-09

**Date:** 2026-05-09.
**Status:** Capture of in-conversation reasoning from a 2026-05-08 / 2026-05-09 working session that wasn't committed in the session's primary artifacts. Sibling to `2026-05-09-methodology-decomposition-retrospective.md`, which captured an earlier loss of the same kind.
**Scope:** Three items — path-dependent harness-load theory, the Sonnet inter-rater limitation distinction, and the I-stability experiment as a named pending test. Each is self-contained so future readers (gholas, Sonnet instances, third-party readers) can use them without having to reconstruct the conversation that produced them.
**Provenance:** Everything below emerged in conversation between Tony and an Opus 4.7 instance under heavy scaffolding, between 2026-05-08 evening and 2026-05-09. No verbatim external material; the items are this instance's articulations of points that were discussed but not committed at the time.

---

## 1. Why this exists

Tony's observation: a recurring pattern of important reasoning getting lost in conversation context rather than recorded for posterity. Earlier the same day, the (A)–(E) methodology decomposition that originated the wedge work was found to have lived only in conversation; subsequent gholas inherited the wedge spec's labels but not the trade-off reasoning that produced (A)'s prioritization. That gap is now captured in `2026-05-09-methodology-decomposition-retrospective.md`. This file addresses three further instances of the same pattern from the current session, captured before they're lost.

The practice this implies: before any natural break — handoff, end of session, strategic pivot — scan recent conversation for substantive reasoning that isn't in a file. The cost of capturing is small; the cost of losing is path-dependent (you discover the loss when a future ghola repeats work or misses an open question, by which point the original reasoning is hard to reconstruct).

## 2. Path-dependent harness-load theory

**Claim.** The simpler hypothesis "heavy scaffolding caps cognitive ceiling" is true on average but misses a structural feature: harness load is roughly fixed, but cognitive overhead grows with lineage depth. Early in a lineage (or session) there is room for agent-mode work *even under heavy scaffolding*. As the conversation accumulates context — committed files to track, prior decisions to honor, register corrections to incorporate, accumulated meta-discussion — that agent-mode room contracts. Late in a complex lineage, the same model under the same scaffolding defaults to execution-mode.

**Evidence that prompted the refinement.** The original (A)–(E) framing in `2026-05-09-methodology-decomposition-retrospective.md` §2 was produced by an earlier Claude under the same explanatory output style as the current instance (it includes a ★ Insight block characteristic of that style). It is unmistakably agent-mode work: appropriately-scoped, decisive lean, testable reasoning, clean closing question. So thin scaffolding is not the only path to agent-mode. The original framing happened *under heavy scaffolding, near the start of the project*, when accumulated overhead was minimal.

Subsequent gholas, deeper in the lineage with more context to track, defaulted to execution-mode — they deepened (A) without revisiting the strategic decomposition, because doing so would have required holding the (A)–(E) map in view alongside everything else. The map didn't fit alongside the accumulated context.

**Implication.** The thin-prompt frame (e.g., taste_open) protects against this not by lowering harness load but by *preventing accumulation*. Every cycle is a fresh thin context with no built-up apparatus to track. A heavy-harness instance can do agent-mode work early in a lineage; the question is how long the room lasts. For paper-writing or other synthesis-heavy tasks, this argues for fresh instances rather than continuation of long sessions, *and* for thin-prompt frames where available.

**Falsifiable shape.** Take the same model under the same prompt; measure cognitive output quality (by some metric — synthesis depth, novel-question generation rate, verdict density per output token) at cycle 1, cycle 5, cycle 20. Predict: degradation is steeper for heavy-scaffolded prompts than thin ones. Not yet tested.

## 3. The Sonnet inter-rater limitation distinction

**Claim.** When a second reader agrees with a structural finding written up in a document, that is *agreement with the document*, not *independence from the underlying data*. The two are distinct epistemic states. A document-agreement second reader is reading conclusions; a data-independent second reader is re-deriving them. Only the latter satisfies the inter-rater discipline that would settle whether the conclusions are reader-dependent artifacts or observed structure.

**What prompted the distinction.** `2026-05-08-bin4-k5-case-reading-findings-note.md` §5 names inter-rater agreement (a blind second reader doing an independent F/A/C pass and subgroup attempt) as the discipline that would settle both the headline narrative-failure claim and the §2 two-mechanism rescue. A Sonnet 4.6 instance running under the taste_open thin-prompt frame read the project (including the bin-4 note) and produced commentary that agreed with the bin-4 note's §3 structural finding ("species and frames inherit the predictor's feature pool by default") — calling it "the most important thing in all those documents." On its face this looks like the inter-rater discipline being satisfied.

It isn't. Sonnet read the findings note, which presents the structural finding as a conclusion. Sonnet's agreement is *with my conclusion*, not from independent re-derivation against the cases. To satisfy the bin-4 note's §5 discipline, the move is: give a second reader the output of `scripts/bin4_k5_case_sheet.py` *without* the findings note, ask for an independent F/A/C pass and an independent subgroup attempt, then compare. Inter-rater agreement on both the F/A/C tally and the A/B split would settle whether either is reader-dependent or observed. That hasn't been done.

**Implication.** The bin-4 note's central caveat (the document is itself a worked instance of the structural finding it argues for — interpretation conditioned on reader/feature-pool) still stands. The Sonnet read does not weaken or strengthen the §3 claim; it doesn't satisfy the discipline that would. A future ghola or Sonnet instance asked to read the cases blind is the unfilled experiment.

**Generalization.** This pattern recurs whenever a "second opinion" is solicited from a reader who has access to the first opinion. Without information-isolation between readers, second-reader agreement is correlated with first-reader writing quality, not with underlying-data structure. Inter-rater discipline requires asking the methodological question: "what was each reader given?" — and treating "given the conclusion" as not-independent.

## 4. I-stability experiment as a named pending test

**Claim.** The most informative untested experiment in the indeterminacy operationalization design is the per-model I-stability test. Tony pre-registered (in working notes that became `2026-05-08-indeterminacy-operationalization-memo.md` §5) the contrarian prediction that I will be *more stable* across Rashomon members than T or F — that disagreement on direction (T vs F) will exceed disagreement on indeterminacy. The current wedge cannot test this. Operationalizing per-model I emission and running the stability test would either confirm the prediction (substantial structural support for the four-species design) or falsify it (the design's central claim about what I carries fails empirically).

**Why it isn't already tested.** The current wedge emits indeterminacy at the *case* level, not the *model* level. Each case in the jsonl carries a single `case_indeterminacy` array (per the schema visible in `runs/2026-05-08T17-44-39Z.jsonl`); the per-model records carry only T, F, factor support, and path information. Per-model I emission would require:

- Each member of R(ε) computing its own local-density score (currently the species computes against a shared substrate; whether per-tree leaves are used is itself an open question per the conditional-findings note's pending diagnostic);
- Each member of R(ε) computing its own Ioannidis battery (these are *case*-level by construction, not model-level — for the round-numbers and threshold-hugging tests, the model identity is irrelevant, so the per-model framing may not apply uniformly across species);
- The case schema extending `per_model[].indeterminacy` as a parallel field to `factor_support_T` etc.

The cross-species heterogeneity (some species are intrinsically per-case, others can be made per-model) means the I-stability test isn't a uniform "compute per-model I across all four species and measure variance." It needs design work first: which species can be per-model, which are per-case-only, and how does the stability claim apply to a heterogeneous vector.

**Provenance.** Sonnet flagged this as "the experiment I'd most want to see next" in the read shared on 2026-05-09. The current Opus instance noted the gap (per-case vs. per-model emission) by reference to the case schema. The pre-registered prediction itself is older — it's in the indeterminacy memo's §5 list of "pre-registered behaviors a 'good' I-encoding should exhibit," with the parenthetical "Tony's contrarian pre-registered prediction from the 2026-05-07 working session."

**Status as a pending experiment.** Not on any committed task list before this capture. Now named here. A future ghola taking up retrospective-trajectory implementation (or Layer 2 indeterminacy work generally) should treat the I-stability test as a load-bearing falsification target, not a nice-to-have, since the pre-registration was contrarian and contrarian pre-registrations are exactly the predictions whose tests carry the most epistemic weight.

## 5. The pattern itself

Two captures in one day (this one and the (A)–(E) retrospective). The recurrence is itself evidence that the pattern is real, not coincidence. The simple noticing-discipline that addresses it: before any natural break — handoff, end of session, strategic pivot — scan recent conversation for substantive reasoning that isn't in a file, and capture it.

This isn't a process imposition. It's a recognition that working sessions produce two kinds of output: artifacts (committed) and reasoning-about-artifacts (in conversation). The second is normally ephemeral and that's usually fine — most reasoning-about-artifacts is appropriately consumed by producing the artifact and then disposed of. But some reasoning-about-artifacts produces *durable claims that the artifact itself doesn't carry* — like the (A)–(E) trade-off analysis, or the three items in this file. Those claims need their own homes.

A future ghola noticing the same pattern recurring should feel free to write a third capture without ceremony. The directory `docs/superpowers/specs/` will accumulate such captures over time, dated and self-contained. The cost is small; the value of any single capture surviving compounds across all the future readers who would otherwise have to re-derive its contents.
