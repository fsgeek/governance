# Pre-registration — Corpus collapse-audit (is premature-scalar-collapse our modal failure, and is margin its receipt?)

**Status:** DRAFT — predictions freeze on commit (hook auto-stamps). NOT yet stamped.
**Date:** 2026-05-22.
**Prior result this builds on:** `2026-05-22-codification-knob-robustness-result-note.md` (commit `e2b66dc`) — found the silence *count* was a premature scalar collapse; margin (effect-size spread) is what makes a collapse legitimate.

## 0. Claims under test

- **C1 (modal):** premature collapse of a multidimensional object to a scalar/boolean/flat-slot is the **modal** root cause of this project's falsifications — not one bug among many.
- **C2 (margin-as-receipt):** a scalar collapse is robust iff the **margin** (distance of the observed value from its decision threshold, relative to the relevant spread) is large; thin-margin scalars are the ones that broke.

## 1. The anti-confirmation problem (why this note exists)

I (Claude, this session) minted C1 and C2 three turns ago. They feel clean — which is peak confirmation-bias risk. If I run an audit *wanting* confirmation, I will narrate every cycle into the frame and learn nothing. Two safeguards, both frozen here:

1. **A per-cycle ledger of my predictions is frozen below (§3) before any margin is computed.** The audit scores my frozen bets; surprise = where the bets are WRONG.
2. **An independent blind classifier** (a dispatched agent, no access to this ledger, §4) codes each cycle's root cause. C1 is scored against the blind coding, not only mine. Me-vs-blind disagreement is reported, not hidden.

**Pre-committed counterexamples I am hunting (failing to find them is itself a finding against me):**
- **≥2 NON-instances** — cycles whose miss is an honest null or a *successful* collapse, NOT a premature-collapse burn. If I cannot find 2, I am forcing the frame.
- **≥1 C2 violation** — a high-margin-yet-untrustworthy verdict. Nominee: **#14's discriminator AUC → 1.000**, which has maximal margin from a naive 0.5 threshold yet is the canonical deceptive spike. If naive margin "blesses" it, margin=receipt is wrong *as stated* and must be redefined out-of-sample / vs-placebo.

## 2. Corpus

The 16 cycles carrying a falsifiable outcome (result-note pairs in `docs/superpowers/specs/`), plus the post-hoc saturation cycle as a positive control. Margins computed only where stored JSONs carry the scalar + a spread/threshold (else `MARGIN-INFEASIBLE`, not silently dropped). Cycles already margined in Arm 1 (silence/adequacy family) are marked **non-blind** and excluded from the blind C2 scoring.

## 3. FROZEN LEDGER — my per-cycle bets (before computing margins)

Columns: outcome (HIT/PARTIAL/MISS) · collapse-root? (Y/N) · layer (scalar/boolean/flat-slot/hypothesis/—) · predicted margin (HI/LO/NA) · note.

| # | cycle | outcome | collapse? | layer | margin | note |
|---|-------|---------|-----------|-------|--------|------|
| 1 | shap-vs-rashomon (05-09) | MISS | **N** | — | HI | SHAP's structural limit, a real finding, not our collapse → NON-instance nominee |
| 2 | v1-v2-predictive (05-09) | MISS | Y | scalar | LO | collapsed I-vector to a stability scalar |
| 3 | refinement #6 (05-12) | PARTIAL | Y | scalar | LO | plurality leg = single ρ; residual-dependent |
| 4 | within-tier-predictive (05-12) | MISS | Y | scalar | LO | uncertain — betting collapse |
| 5 | shap-vs-pricing (05-12) | MISS | Y | hypothesis | NA | we prematurely concluded "SHAP blind"; wrong |
| 6 | disagreement-geometry P1 (05-12) | HIT | **N** | scalar | HI | d(x) collapse SUCCEEDED (legible) → successful-collapse NON-instance |
| 7 | disagreement-routing (05-12) | MISS | Y | scalar | LO | canonical: reliability→per-case d; killed 6 ways |
| 8 | extension-admitted-band (05-12) | PARTIAL | Y | scalar | LO | de-dup-dependent collapse |
| 9 | routable-population (05-12) | MISS | Y | scalar | LO | routing booleans on ~1e-3 diffs |
| 10 | fm-rich #11 (05-13) | PARTIAL | Y | flat-slot | NA | mandatory_features flat slot does no work |
| 11 | variant-silence #12 (05-13) | HIT | Y | scalar | MIXED | count-collapse; rb00/09 HI, rb05 LO — **non-blind (Arm 1)** |
| 12 | hmda-trimodal (05-14) | MISS | **mixed** | scalar+null | LO | partly threshold-collapse (Arm 1), partly genuine substrate non-transport → mixed |
| 13 | expanded-vintage (05-18) | MISS | Y | scalar | LO | named_diff AUC + count — **non-blind (Arm 1)** |
| 14 | #14 discriminator AUC→1.000 | (deceptive) | Y | scalar | **HI-deceptive** | predicted **C2 VIOLATION**: high naive margin yet untrustworthy |
| 15 | frame-evocation (05-15) | MISS | Y | scalar | LO | search for a *universal* discriminator = collapsing variant-indexed silence |
| 16 | saturation-phase (05-14) | (post-hoc HIT) | **N** | — | HI | RESISTED collapse — found trimodal gaps → positive-control NON-instance |

Tally of my bets: collapse-root Y on **11**, N on **3** (#1, #6, #16), mixed on **1** (#12), plus #14 as a deliberate violation. Burned cycles (MISS/PARTIAL/deflated): #1–5,7–10,12,13,15 ≈ 13.

## 4. Blind classifier protocol (frozen)

Dispatch one agent with: the 16 result-notes, a fixed rubric (outcome; is the headline a scalar/boolean/flat-slot collapse of something multidimensional; root cause = premature-collapse vs honest-null vs successful-collapse vs other), and NO access to §3. It returns a per-cycle coding + one-line justification each. The agent is told to be adversarial to the collapse frame: actively look for misses that are NOT collapses.

## 5. Margin computation (frozen)

Per verdict-family, margin = (|observed − threshold|) normalized by the family's spread:
- **R²-adequacy:** |R²−0.30| / gap (have it; non-blind).
- **AUC:** (AUC − placebo/null mean) / null sd where a permutation null is stored; else distance to the pre-reg AUC threshold (flagged weaker).
- **Jaccard:** |J − J_threshold|.
- **routing (Brier/ECE):** effect size / baseline (the ~1e-3-on-0.15 cases → near-zero margin).
Cycles lacking a stored spread → `MARGIN-INFEASIBLE`.

## 6. Predictions + falsifiers (priors are mine)

- **P1 — modal (prior 0.70).** ≥70% of burned cycles have premature-collapse as root, by BOTH my ledger and the blind classifier. *Falsifier:* <70% on the blind coding → "modal" oversold.
- **P2 — non-instances exist (prior 0.80).** ≥2 cycles are NON-instances on the blind coding. *Falsifier:* blind classifier finds collapse everywhere → the frame is unfalsifiable / I (and it) forced it.
- **P3 — margin=receipt (prior 0.65, blind subset).** On margin-computable, blind cycles, robust/HIT↔HI margin and fragile/MISS↔LO margin. *Falsifier:* a thin-margin HIT or a fat-margin MISS that isn't #14.
- **P4 — the hunted violation (prior 0.60).** #14 (or another) is a high-margin-yet-deceptive case forcing margin to be redefined out-of-sample/vs-placebo. *This prediction WANTS to fire* — firing falsifies naive-C2 and improves it.
- **Meta (frozen):** zero non-instances AND zero violations will be reported as evidence I forced the frame, not as a clean win.

## 7. Bound (named, uncertifiable upstream)

I wrote the rubric and chose the 16 cycles; the blind classifier reduces but does not eliminate my hand (I briefed it). N+1 again. Stated, not closed.

## 8. Followups (four-state)

- **(i) C1+C2 both survive (blind-confirmed)** → premature-collapse is the empirically-earned Paper-1 spine; margin (out-of-sample) is the operational receipt; reissue the position paper's frame as instrument-on-itself.
- **(ii) C1 survives, C2 needs the out-of-sample refinement (#14 fires)** → strongest result: the receipt is *held-out* margin, naive margin blesses overfit. Feeds #14's own deceptive-spike narration in §4.8.
- **(iii) C1 fails on blind coding** → premature-collapse is a seductive over-fit of my own; report the disconfirmation and stop selling it as the spine.
- **(iv) me-vs-blind disagree sharply** → the classification is too author-dependent to bear weight; the audit becomes a finding about rubric subjectivity, not about collapse.
