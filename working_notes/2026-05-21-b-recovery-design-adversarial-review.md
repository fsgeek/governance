# B-recovery cycle design — adversarial review record (rikuy)

**Date:** 2026-05-21. **Artifact reviewed:** `docs/superpowers/specs/2026-05-21-b-recovery-cycle-design.md` (v1). **Reviewers:** four external model instances (ChatGPT, Gemini, Grok, Kimi), each given the v1 design doc without the underlying #14 analysis or this project's conversation history. **Purpose:** preserve the review trail and the adjudication that produced v2, since v1 was never committed (no git trace). Synthesis below is faithful and attributed; verbatim reviews live in the 2026-05-21 session transcript.

## Convergent findings (all four, or near-all)

| # | Finding | Raised by | Adjudication |
|---|---|---|---|
| 1 | **Estimand split.** Population is defined by `Jaccard<0.5`, which needs both bands → you can't know you're in-population without fitting B, so "skip the B-fit" (branch ii) is not operationally supported. Split scientific (B-fit to identify) from deployable (A-side only). | ChatGPT (sharpest); Kimi (leakage audit) | **Concede fully.** v2 §4: two estimands Q1/Q2. Q2 population = all A-inadequate cells (reorg is B-defined). Jaccard/p3_sat/B-carrier → oracle-diagnostic bucket. |
| 2 | **Rare-event metrics.** 90% base rate kills accuracy; AUC fragile / breaks in zero-failure folds. Use false-skip risk = P(B_fails \| skip) with upper CI bound vs a pre-set tolerance. | all four | **Concede fully.** v2 primary metric = bounded false-skip risk; AUC/accuracy demoted to diagnostics. |
| 3 | **Power reality.** n=29 / 3 failures is an anecdote; can't train 6 predictors. Reframe primary output as a measured failure-rate bound, predictors exploratory. | all four | **Concede fully.** v2: predictors exploratory-secondary, family-corrected; primary is the bound. |
| 4 | **Numeric branch criteria.** Verbal trichotomy thresholds need frozen numbers. | ChatGPT, Grok, Kimi | **Concede fully.** v2: operating-curve sweep over tolerances; four-state outcome with bound-vs-tolerance numeric rules. |
| 5 | **Clustered permutation + FWER.** Cell-level shuffle too optimistic under within-vintage/regime correlation; six predictors need family correction. | ChatGPT, Kimi | **Concede fully.** v2 §4.6: blocked permutation + max-statistic across predictors. |
| 6 | **Adequacy-threshold brittleness.** R²≥0.30 is a hard cliff; 0.29→0.31 = "recovery" on noise. Report margins, near-threshold cells, sensitivity at 0.25/0.35, min-ΔR². | all four | **Concede with note.** v2 adds robustness appendix. Threshold stays frozen — inherited from #11/#12, NOT tuned for #15 (a provenance feature). |
| 7 | **Regime-under-LORO.** Categorical regime can't generalize to an unseen regime; LORO is transport/stability, not a regime-predicts-recovery test. | ChatGPT, Gemini | **Concede fully.** v2: regime predictor only in all-regimes-present analysis; LORO is transport-only. |
| 8 | **Broaden parity gate.** One vintage insufficient; need a suite (per-regime, both strata, reorg + no-reorg), label-exact + float-tolerance, seeds + lib versions. Parallel CART tie-breaking may make bit-identical unachievable. | ChatGPT, Grok | **Concede fully.** v2 §3: parity suite + explicit determinism standard. |
| 9 | **Decouple stamp from parallelization.** Pre-reg can be stamped once #14 closes (committing to the parallel tool); only execution waits on parity. Resource ≠ logical gate. | Kimi | **Concede.** v2 §1: stamp may precede parity; execution gated on parity. |

## Precision added beyond the reviews (governance lineage)

- **Zero-failure LORO fold ≠ branch (iii)** (answers Gemini's direct question). With a *bounded* failure rate, a zero-failure fold yields a wide upper CI (rule-of-three ≈ 3/n) → **INCONCLUSIVE**, not "must fit B." Branch (iii) fires only when a fold's failure-rate **lower** bound exceeds tolerance — positive evidence of high failure, not absence of data. Separates sample-starvation from regime-variance.
- **The reframe collapses #15 to a cleaner study.** Estimand-split + rare-event-metric + power ⇒ the deployable instrument is *not a learned model* but "documented band inadequate ∧ bounded failure rate below tolerance ⇒ skip the compliant-band fit." A regulator-auditable bounded rate (grounds Blind Claude's "lookup not detector" instinct). Cohort sized by **precision on the bound** (~tens-to-low-hundreds of A-inadequate cells ≈ all feasible vintages post-parallelization), not "2 per regime."
- **Tolerance is a reported axis, not an input.** No party (Olorin included — "their choice") owns the regulatory risk appetite, and Tony is rightly uncertain of a number. So v2 reports the false-skip-risk bound across a declared sweep {1,5,10,20%} and the tolerance at which skip-B flips to must-fit-B. Stricter than the reviewers' "declare a tolerance" — declares the whole operating curve.

## Resisted / already-handled

- **Don't over-rotate to "pure pilot, drop the trichotomy"** (Kimi/ChatGPT lean here). The trichotomy survives, re-expressed as failure-rate-bound regions + an explicit INCONCLUSIVE 4th state (Grok's low-power fallback).
- **Recursive surface-salience note** (ChatGPT: keep out of #15 prereg) — already placed in the #14 *closing* note, not #15.
- **Regime/vintage collinearity** (Gemini's localized-vintage-artifact risk) — already flagged (v1 §2/§6); defused by per-regime-bound + LORO-as-transport rather than regime-coefficient claims.
- **"Fun criteria" wording** (Kimi) — reworded to "high surprise potential under a uniform prior" in §5; the prioritization heuristic itself is a deliberate lineage value, retained.
