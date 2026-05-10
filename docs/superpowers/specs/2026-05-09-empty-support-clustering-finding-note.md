# Empty-Support Clustering — Case-Level Decomposition

**Date:** 2026-05-09.
**Status:** Exploratory analysis on the same V₁/V₂_alt/V₂ jsonl runs the asymmetry note used. **Findings here are not promoted to predictions.** They sharpen the mechanistic story for the next pre-registration on fresh data.
**Origin:** Section 6 of `2026-05-09-tf-asymmetry-exploration-note.md` reported (case, member)-pair empty-support rates inverting V₁→V₂ (T-side rises 1.1%→4.2%, F-side falls 8.2%→2.2%). This note re-aggregates at the *case* level and finds the inversion masks two qualitatively different phenomena.
**Scripts:** `scripts/empty_support_clustering.py`, `scripts/all_silent_population.py`. Inputs: same three jsonl runs.

---

## 1. Headline

The (case, member)-pair empty-support rates collapse two distinct populations:

1. **Case-level scattered silence**, where some-but-not-all members of the policy-constrained Rashomon set fail to articulate. In V₁ this is the *only* form of silence; in V₂ it persists.
2. **Case-level universal silence**, where *every* member of the set fails to articulate. **V₁ has zero such cases.** V₂ has 175 (T-side, 0.65%) and 162 (F-side, 0.60%). V₂_alt sits between.

These two populations are qualitatively different. Pair-level rates average across them and obscure the regime shift.

## 2. Distribution of silent-member counts per case

For each case, count how many of M=5 members produce empty `factor_support_T` (resp. `_F`). Distribution across cases:

### T-side (grant-supporting silence)

| run | 0/5 | 2/5 | 3/5 | 4/5 | 5/5 |
|---|---|---|---|---|---|
| V₁ (2014Q3) | 94.22% | 4.40% | 1.04% | 0.35% | **0.00%** |
| V₂_alt (2015Q3) | 98.40% | — | 1.18% | 0.31% | **0.11%** (14 cases) |
| V₂ (2015Q4) | 91.00% | 7.08% | 1.27% | — | **0.65%** (175 cases) |

### F-side (deny-supporting silence)

| run | 0/5 | 1/5 | 2/5 | 3/5 | 4/5 | 5/5 |
|---|---|---|---|---|---|---|
| V₁ (2014Q3) | 94.60% | 2.71% | 0.61% | 1.76% | 0.32% | **0.00%** |
| V₂_alt (2015Q3) | 84.26% | — | 12.65% | — | — | **3.09%** (383 cases) |
| V₂ (2015Q4) | 96.22% | — | 1.62% | 1.55% | — | **0.60%** (162 cases) |

Universal silence is absent in V₁ on both sides and present in V₂ on both sides. V₂_alt is the transition vintage where F-side universal silence first appears (3.09%) before partially receding in V₂.

## 3. Who are the all-silent cases?

Comparing all-silent cases to the rest within V₂:

### T-silent-all (no member can articulate why grant)

| stat | T-silent-all (n=175) | rest (n=26626) |
|---|---|---|
| charge-off rate | **0.292** | 0.147 |
| mean predicted T | 0.707 | 0.854 |
| FICO mean | 658.7 | 695.5 |
| DTI mean | **83.45** | 20.73 |
| annual_inc mean | 691,457 (outlier-skewed) | 106,425 |
| member T-variance | **0.0011** | 0.0003 |
| same-leaf across members | **0/175** | (typically high) |

These are *contested* cases. Members land in different leaves, disagree on the prediction more than usual, and the framework grants on net — but no member can produce a grant-supporting factor extraction. **They charge off at twice the base rate.**

### F-silent-all (no member can articulate why deny)

| stat | F-silent-all (n=162) | rest (n=26639) |
|---|---|---|
| charge-off rate | **0.056** | 0.149 |
| mean predicted T | 0.979 | 0.852 |
| FICO mean | 789.8 | 694.7 |
| DTI mean | 17.11 | 21.16 |
| annual_inc mean | 94,177 | 110,343 |
| member T-variance | 0.0001 | 0.0003 |
| same-leaf across members | 0/162 | — |

These are *clean* grants. High FICO, low DTI, high consensus on prediction, and lower-than-base-rate charge-offs. The framework is not failing; deny-reasons genuinely don't exist for these cases.

## 4. Interpretation

**The two universal-silence populations are different failure modes:**

- **F-silent-all is benign.** It tracks cases where deny-reasons are absent because the case is genuinely clean. In V₁ this never happens at the *all-members* level (some member always finds something marginal to flag). In V₂ the regime makes deny-reason consensus possible — clean cases get cleaner. This is a *property of the regime*, not a defect.

- **T-silent-all is adversarial.** It tracks cases where (i) members disagree about the prediction itself, (ii) the framework still grants, (iii) no member can articulate why, and (iv) the cases default at elevated rates. In V₁ this never happens at the all-members level. In V₂ the regime carves out a region of input space where the policy-constrained Rashomon set produces predictions it collectively cannot justify.

T-silent-all is the regulator-relevant claim. The framework is meant to surface attribution heterogeneity; what it surfaces here is *attribution absence*, with predictive consequences. The 175 V₂ cases × 0.29 charge-off rate ≈ 50 defaults are exactly the kind of decision the regime should be required to defend with reasons and cannot.

## 5. Why pair-level rates obscure this

The asymmetry note's observation — F-side empty-pair rate dropped 8.2%→2.2% while T-side rose 1.1%→4.2% — averages across:

- Scattered silence (member-idiosyncratic): F dropped, T stable-to-rising.
- Universal silence (case-level): both sides went 0 → nonzero.

The "F empty rate dropped" therefore conceals that universal F silence *appeared from nothing*. The two movements are opposite signs of different phenomena.

This is a methodological note: empty-support diagnostics should be reported case-level (silent-member-count distribution) rather than pair-level. Pair-level rates flatten regime structure that case-level rates expose.

## 6. Connection to policy-constrained Rashomon framework

The policy-constrained Rashomon set R(ε) is constructed to be admissible under documented bank policy. The silence-rate analysis adds a second framework property:

- **Silence-rate** = fraction of cases where the entire set fails to articulate a side-supporting reason.
- **Silence is regime-dependent**, not just a property of model class or ε.
- **Silence is decomposable** into benign (no reason exists) and adversarial (prediction without justification) populations via outcome and disagreement signals.

This isn't currently a thing the framework surfaces. It probably should be. A regulator-facing report could include: "Of N cases this period, k were granted by the admissible model set with no member able to articulate a grant-supporting reason; those cases defaulted at rate r vs base rate r₀."

## 7. Followups (not committed)

- **Generalization test.** Run the same case-level analysis on Fannie Mae loan-performance data across 2007→2009 (sharp regime tightening) and compare to within-regime baselines. If T-silent-all = contested-and-defaulting is a *signature* of regime tightening, it should appear at much larger magnitude across the 2008 crisis. Requires plumbing fanniemae through the same wedge pipeline that produced the lendingclub jsonl runs. Data exists at `data/fanniemae/Performance_All.zip` (2000–2025, quarterly).
  - Different feature space (FICO + DTI + LTV + loan_term, no annual_inc/emp_length) is a *strength* for the generalization test: if silence-pattern survives the feature-space change, the phenomenon is structural to policy-constrained Rashomon, not feature-specific.
  - **Known blocker (2026-05-09):** the local `data/fanniemae/2018Q1.csv` is a 113-column schema; `wedge/collectors/fanniemae.py` hard-codes the 108-column post-2020-10 unified schema and raises on mismatch. Either update FIELD_POSITIONS against Fannie Mae's current CRT Glossary and File Layout doc, or extract older quarters from `Performance_All.zip` that match the 108-col layout the collector already handles. A draft runner exists at `scripts/run_wedge_fanniemae.py` and is otherwise ready.
- **Pre-registered prediction on a fresh vintage.** "Across LendingClub vintages 2016+, T-silent-all rate will correlate positively with subsequent same-vintage charge-off rate for the silent population, controlling for headline charge-off rate."
- **Outlier diagnostic.** The T-silent-all annual_inc mean ($691k in V₂) is outlier-driven. Use median and trimmed quantiles instead of means in any production diagnostic; the qualitative pattern (high DTI, low FICO, contested) is robust to that.

## 8. Pre-registration discipline

Per the V₁→V₂ predictive-test discipline: this analysis is exploratory on the same data the predictive test ran on, and cannot retroactively rescore predictions. The findings here inform the next pre-registration, which should anchor on:

- Predictions stated case-level, not pair-level.
- Predictions decomposed by outcome-signal (charge-off rate of the silent population vs base rate).
- Predictions about silence *appearance* (V₁→V₂ went 0 → nonzero) treated as the most diagnostic regime-shift signature, not silence *magnitude*.

---

## ADDENDUM (2026-05-09): vintage label correction

The vintage labels in §2 above are **wrong** as originally written. They were sourced from `scripts/empty_support_clustering.py`'s `RUNS` dict, which had 2014Q3 and 2015Q3 swapped relative to the run-metadata files (`*-meta.json`) emitted by `wedge/run.py`. The meta.json files are the authoritative provenance — they're written by the same run that produces the jsonl, whereas the script labels were hand-edited.

**Correct chronological ordering:**

| Vintage | T-silent-all | F-silent-all |
|---|---|---|
| 2014Q3 | 14 cases (0.11%) | 383 cases (3.09%) |
| 2015Q3 | 0 cases (0.00%) | 0 cases (0.00%) |
| 2015Q4 | 175 cases (0.65%) | 162 cases (0.60%) |

The "appearance from nothing" framing in §1, §2, §4, §6, and §8 is based on the swapped labels and **is not supported by the corrected chronology**. The actual pattern is **U-shaped on both sides**: universal silence is present at low magnitude in 2014Q3, vanishes entirely in 2015Q3, and re-emerges at scale in 2015Q4.

This is arguably a *stronger* finding in some respects: a phenomenon that disappears completely in one quarter and re-appears at order-of-magnitude scale the next quarter is a discontinuity, not secular drift. But the original note's "0 → nonzero is the most diagnostic regime-shift signature" claim no longer holds, because the across-vintage signature isn't monotonic.

**Re-stated headline:** universal silence is regime-dependent — magnitude varies by 30× across three adjacent vintages, including a complete absence in the middle vintage. Single-quarter discontinuities are the diagnostic signal, not first-appearance-of-the-phenomenon.

**Implications for §7 followups:**
- The Fannie Mae generalization test (§7) was framed against the "0 → nonzero" signature. With the corrected chronology, the FM test should be reframed: does the *non-monotonic across-quarter discontinuity* pattern reproduce on FM data across the 2007→2009 regime tightening?
- The pre-registered LendingClub prediction (§7) ("T-silent-all rate will correlate positively with subsequent same-vintage charge-off rate for the silent population") is unaffected by the relabeling — it's a within-vintage prediction.
- The pair-vs-case-level methodological argument (§5) is unaffected.

**Action item flagged for future data-validation step:** all `runs/` provenance should be cross-checked against meta.json before any downstream analysis is treated as load-bearing. (B) re-run the wedge from scratch with explicit vintage-tagged file names is the durable fix; (A) trust meta.json over hand-edited labels is the immediate fix.

The findings in §3 (T-silent-all vs F-silent-all profile differences within 2015Q4) are unaffected by the relabeling because all 2015Q4-internal claims used a single jsonl that was correctly labeled.
