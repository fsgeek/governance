# Cross-Substrate Falsification — Pre-Registration

**Date:** 2026-06-23 (frozen BEFORE any run; branch `age-pricing-residual`)
**Standing hypothesis to falsify (Tony's):** **H0 — the LC age-graded pricing-past-default is an
OUTLIER. The discrimination will NOT appear on other substrates.**
**Lineage:** [[project_age_grade_default_result]] (LC: young +134bps past default-justified, old
−78bps subsidized, ~90% laundered through grade, robust across maps). This design tries to BREAK
H0 by finding the same-signed laundered gradient on a non-LC substrate. Per project discipline the
burden is flipped: I hunt for the pattern WITH a prior that it is absent (anti-confirmation).

## Why this is a falsification design, not a fishing trip
- H0 is the prediction. Finding the gradient on FM FALSIFIES it; a null SUPPORTS it.
- Signs + kill-conditions are frozen here, before code. No post-hoc reinterpretation.
- If any arm APPEARS to falsify H0, a blind adversary is hired to refute the hit BEFORE banking
  ([[feedback_adversary_before_the_sentence]], [[feedback_anti_confirmation_procedure]]) — a
  satisfying cross-substrate hit is exactly when self-deception is most likely.

## Substrate constraint (verified on disk 2026-06-23, drives the whole design)
The LC age-proxy is `est_age = 18 + credit_tenure` (issue_d − earliest_cr_line). The mortgage
substrates (Fannie Mae SF, HARP, multifamily) use the CRT 113-field disclosure schema, which
carries **no borrower age and no credit-line-history date** — the LC inference cannot be rebuilt.
The only age-shaped field is LTV. So a literal replication is impossible; the design adapts the
proxy per substrate and pairs each with a control that catches its specific artifact.

## ARM A — Fannie Mae Single-Family (the real falsification test)
**Substrate:** FM SF Loan Performance (symlink `data/fanniemae`, quarterly CSV; pick ONE vintage,
convert to parquet first). Triple: price = `orig_interest_rate`; default = collector's ever-90+-DPD
within 24mo label; age-proxy = **LTV cohort** (high LTV ≈ young/thin-equity, low LTV ≈ old/equity-rich).
**Benchmark:** the SAME default-justified-excess machinery as LC (`wedge/age_grade_default.py`),
with LTV cohorts in place of age bands.
**The tautology-breaking control (load-bearing):** the predicted-default model (the yardstick)
INCLUDES LTV as a risk factor. So LTV's default content is fully netted into the justified price.
A high-LTV-cohort excess that SURVIVES this is NOT LTV-risk rerouted — it is the FM analog of the
LC +134. (Parallel to LC putting FICO/DTI in the yardstick and still finding the gradient.)
**Frozen predictions:**
- Under H0 (expected): high-LTV cohort excess over the LTV-aware default-justified rate ≈ 0
  (CI includes 0), i.e. once default prices LTV, no residual cohort overcharge. H0 SURVIVES.
- Falsifier: high-LTV cohort priced materially ABOVE its LTV-aware justified rate (excess > +25 bps,
  CI excludes 0) AND a monotone decline toward low-LTV cohorts (sign-structure mirrors LC). That
  would FALSIFY H0.
- Laundering analog: if FM has a grade/risk-class field, repeat within-class; corpus-minus-within
  gap = FM laundering. (If no grade field, report the corpus result only and say so.)
**Kill-conditions (frozen):**
- K-A1: if LTV cohort and predicted-default are so collinear that the LTV-aware yardstick is
  rank-degenerate (cannot separate cohort from its own risk), Arm A is VOID for tautology, not
  scored as either result. Report void honestly (this is the failure mode the prior HMDA session hit).
- K-A2: if the default-rate map is non-monotone (guard fires), benchmark invalid — error loudly.

## ARM C — LC internal placebo (the artifact detector; runs FIRST)
**Purpose:** does the benchmark machinery invent a gradient on a variable with NO age content?
If it does, every cross-substrate finding is suspect.
**Test:** on LC, replace age bands with bands of a PERMUTED-tenure column (shuffle est_age across
rows, re-band) and run the identical corpus benchmark. Also a second placebo: band a genuinely
age-neutral field (e.g. loan_amnt decile) and check the young-analog band shows ~0 excess.
**Frozen prediction:** placebo young-analog excess ≈ 0 (|excess| < 30 bps, CI includes 0). The real
LC +134 must NOT reproduce on permuted tenure.
**Kill-condition K-C1:** if the placebo PRODUCES a +134-like excess on permuted/neutral data, the
method is artifact-generating; HALT — neither the LC result nor any Arm-A finding can be trusted
until the machinery is fixed. (This protects the already-committed LC result too.)

## Scope decision (Tony: "pick the option with best chance of falsifying H0")
Run **Arm A (falsification) guarded by Arm C (placebo first)**. Arm B (HMDA real-age convergent)
deferred: HMDA has no default outcome, so it cannot run THIS benchmark and cannot falsify H0 — only
convergent-validity, a separate weaker question. A-first is maximum honest falsification power.

## Outputs
- `runs/lc_placebo_<date>.txt` (Arm C) and `runs/fm_age_ltv_default_<date>.txt` (Arm A), JSON sidecars,
  self-describing with this pre-reg's predictions + kill-conditions inline, scored from the data.
- Result memory + commit + OTS stamp, scoring H0 explicitly (survived / falsified / void-per-K).

## Caveats carried in every artifact
- FM "age" is LTV-cohort, a DIFFERENT and weaker proxy than LC credit-tenure — a null on FM does
  not prove LC is artifactual; it proves the LTV-proxy doesn't carry the gradient on FM.
- est_age / LTV-cohort are both proxies; neither is observed age. True-age port remains HMDA (no
  default field) — out of scope for the default-justified benchmark.
- The default-rate map is the attack surface; report under isotonic + decile as on LC.
