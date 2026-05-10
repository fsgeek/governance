# V₁ → V₂ Predictive Test — Findings Note

**Date:** 2026-05-09.
**Status:** Comparison executed against pre-registered predictions in `2026-05-09-v1-v2-predictive-test-pre-registration.md`. No predictions were reinterpreted post-hoc; the table below classifies each against the pre-committed hit criteria (§5) verbatim. Anchoring claims (C1–C4) about LC's 2014–2015 underwriting changes have **not** been externally verified yet, per the pre-registration §7 caveat. The discipline still operates regardless; what is bounded is the credibility of the policy-changes-explain-shifts story, not the credibility of the prediction record.
**Comparison protocol:** `scripts/v1_v2_predictive_test.py`. Inputs: `runs/2026-05-08T17-43-21Z.jsonl` (V₁=2014Q3, n=12,379) and `runs/2026-05-08T17-44-39Z.jsonl` (V₂=2015Q4, n=26,801). Secondary: `runs/2026-05-08T16-26-41Z.jsonl` (2015Q3, n=22,271).

---

## 1. Headline

**5 predictions × 2 sides (T, F) = 10 sub-claims.** Five hits, four misses, one near-hit-via-direction-not-pre-specified. The T (grant-supporting) and F (deny-supporting) sides behaved very differently — a split the pre-registration did not anticipate. The methodology's most distinctive claim, **P5 (reasoning-disagreement tracks underwriting-flux), missed on the headline factor_support_T side** — overlap *increased* from V₁ to V₂ rather than decreased.

The bin-4 case-reading discipline-failure pattern repeats here in different form: the pre-registered story was internally coherent, the mechanisms were well-articulated, and the data does not back the headline claim cleanly. The discipline made the failure honest.

## 2. Per-prediction results

### P1 — annual_inc factor support increases V₂ > V₁
- **factor_support_T: hit.** Mean weight rose from 0.000230 to 0.000261, **+13.26%** vs V₁ baseline (criterion: ≥5%).
- **factor_support_F: miss.** Mean weight *fell* from 0.000140 to 0.000055, **−60.67%** — opposite of predicted direction.
- **Interpretation:** the income-verification mechanism (C1) appears to predict grant-supporting weight cleanly but predicts deny-supporting weight in the wrong direction; verified income may be more signal-rich for grants but *less* used as a deny-side discriminator in V₂.

### P2 — fico_range_low factor support decreases V₂ < V₁
- **factor_support_T: hit.** Mean weight fell from 0.001699 to 0.001198, **−29.46%** vs V₁ (criterion: ≥5%).
- **factor_support_F: miss.** Mean weight *rose* slightly, +4.26% — wrong direction, near-zero magnitude.
- **Interpretation:** the FICO-floor mechanism (C2) predicts grant-side weight loss strongly, consistent with range compression. The deny-side did not compress correspondingly; the surviving deny-supporting FICO signal held its weight.

### P3 — dti factor support decreases V₂ < V₁
- **factor_support_T: hit (barely).** Mean weight fell from 0.000524 to 0.000496, **−5.31%** — just above the 5% threshold.
- **factor_support_F: miss.** Mean weight *rose* dramatically, +105.46% — opposite of predicted direction, large magnitude.
- **Interpretation:** the DTI-ceiling mechanism (C3) marginally predicts grant-side weight loss but is dramatically wrong on the deny-side. DTI became *much* more important as a deny-supporting signal in V₂. The pre-registration's confidence rating ("moderate, lower than P2") was correctly humble on direction but missed the magnitude of the F-side shift.

### P4 — emp_length factor support shifts (direction undirected)
- **factor_support_T: hit.** Δ = −6.14%, just above 5% threshold.
- **factor_support_F: hit.** Δ = −53.64%.
- **Interpretation:** the prediction-of-uncertainty was vindicated; emp_length did shift in V₂. Both sides moved downward, suggesting reduced employment-length discriminative power generally rather than a grant/deny asymmetry.

### P5 — median pairwise factor-support overlap decreases V₂ < V₁
- **factor_support_T: miss.** V₁ = 0.800, V₂ = 0.867, Δ = **+0.067** — overlap *increased*, opposite of predicted direction.
- **factor_support_F: hit.** V₁ = 0.800, V₂ = 0.700, Δ = **−0.100** — overlap decreased, criterion (≥0.05 absolute) met.
- **Interpretation:** this is the most consequential miss. The headline "reasoning-disagreement tracks underwriting-flux" prediction does **not** hold on factor_support_T. R(ε) members agreed *more* about which features support grant decisions in V₂ than in V₁. The 2015Q3 transition-vintage T overlap (0.600) is below both V₁ and V₂, which is consistent with the prior-memo narrative of 2015Q3 as a turbulent transition period, but contradicts the prior-memo *prediction* that 2015Q4 would show only partially-settled overlap. Instead, V₂ T overlap settled *higher* than V₁ — V₂ R(ε) members are more aligned on grant-supporting reasoning than V₁ R(ε) members were before the policy changes. The deny-side P5 hit is real but cannot be promoted to the headline prediction without violating the no-post-hoc-reinterpretation discipline.

## 3. The T/F split

The pre-registration assumed grant-supporting and deny-supporting factor weights would shift symmetrically under each anchoring claim ("Same for factor_support_F" appears verbatim in P1, P2, P3). They did not. On the T side, four of five directional predictions held. On the F side, four of five directional predictions failed.

This asymmetry is interesting and worth taking seriously, but it is also exactly the kind of post-hoc-tempting "well, actually" the pre-registration discipline exists to constrain. The honest reading: **the symmetric-anchoring assumption was wrong.** Why it was wrong is a question for follow-up work, not for the findings note. Possibilities to investigate (not to claim):

- Grant decisions may be more directly governed by documented underwriting policy; deny decisions involve more idiosyncratic mechanisms not captured by simple "policy tightened on feature X."
- The decision boundary's grant-side neighborhood and deny-side neighborhood occupy different feature regions; tightening at the FICO floor compresses the grant-side range without corresponding effect on the deny-side, etc.
- CART trees with this configuration may simply not allocate symmetric attribution to T-leaves and F-leaves under population shift.

Each of these is a hypothesis, not a finding.

## 4. Hit / miss rate summary

| Prediction | T side | F side |
|---|---|---|
| P1 (annual_inc up) | hit | miss |
| P2 (fico down) | hit | miss |
| P3 (dti down) | hit (barely) | miss |
| P4 (emp_length shifts) | hit | hit |
| P5 (overlap down) | miss | hit |

T side: 4 hits / 1 miss. F side: 1 hit / 4 misses. The headline P5 claim missed on its primary side.

## 5. Methodology interpretation

The methodology's central directional predictive content — that R(ε) reasoning-disagreement tracks underwriting-flux — **did not survive its first pre-registered test on the headline side**. This is one test on one dataset between two vintages with internal-only anchoring; it does not falsify the methodology in general. It does, however, prevent the methodology from claiming predictive content for V₁→V₂ overlap shifts on factor_support_T from this run forward without amendment.

What survives:
- The directional content of policy-mechanism → grant-side feature-weight shift is non-trivial: P1, P2, P3 all hit on T. The methodology has *some* predictive content even if not the specific content P5 claimed.
- P4 vindicates the prediction-of-uncertainty form: predicting "this will shift, I don't know which way" is itself a falsifiable claim, and it held.
- The T/F asymmetry is a real empirical regularity discovered through this test, even though it cannot be claimed as a prediction of this work (it was assumed away in the pre-registration).

What does not survive without amendment:
- The "reasoning-disagreement tracks underwriting-flux" headline, on factor_support_T.
- The transition-vintage interpretation that 2015Q4 would show partially-settled (i.e., elevated) disagreement; in fact T overlap settled *higher* than the pre-transition baseline.

## 6. What this means for the prototype and the position paper

- **Position paper.** The methodology cannot lead with P5 as a vindicated predictive claim. It can lead with the Rashomon-routing-as-observability frame (which is what the Olorin pitch needs) without depending on P5. P5 should be reported in the position paper as a pre-registered test that produced mixed results, with the T-side miss disclosed honestly. This is the bin-4 discipline applied at scale: the methodology that critiques others for post-hoc rationalization cannot itself rationalize a missed prediction.
- **Prototype.** The 2-week build for Olorin proceeds on substrate that does not depend on P5. The within-set disagreement signal still exists and still routes cases; the question of whether it *tracks underwriting-flux across vintages* is now an open empirical question, not a methodological premise.
- **Follow-up.** A revised prediction set anchored to the empirically-observed T/F asymmetry (with explicit acknowledgment that it is built post-hoc on V₁/V₂ and would need a fresh dataset to test) is a legitimate next step. It is not the same as "reinterpreting" the pre-registered predictions; the discipline allows new predictions to be made, just not to retroactively rescore old ones.
- **External verification of C1–C4 still owed.** The findings hold under any anchoring (the discipline does not depend on the anchoring being correct), but the *interpretation* (e.g., "verification tightening predicts annual_inc up") depends on C1–C4 being approximately accurate. This caveat applies to the interpretation column, not the hit/miss column.

## 7. Connection to other working documents

- **`2026-05-09-v1-v2-predictive-test-pre-registration.md`** — the pre-committed prediction record this note classifies against. OTS-stamped before the test ran.
- **`2026-05-08-vintage-stability-findings-note.md` §2** — the transition-vintage observation that anchored P5; the prediction it implied (V₂ shows partially-settled overlap) is not borne out for factor_support_T.
- **`2026-05-08-bin4-k5-case-reading-findings-note.md`** — earlier worked instance of the same discipline, where pre-prediction (12-15 fits / 5-8 ambiguous / 1-3 contradicts) landed at (2 / 11 / 7) and the methodology's frame failed honestly. This findings note continues that lineage at higher stakes.
