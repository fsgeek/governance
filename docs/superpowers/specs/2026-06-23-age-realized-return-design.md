# Age × Realized Lender Return — Design (frozen pre-reg)

**Date:** 2026-06-23
**Branch:** `age-pricing-residual`
**Script:** `scripts/age_realized_return.py` (to build)
**Module:** `wedge/age_realized_return.py` (to build)
**Artifact:** `runs/lc_age_realized_return_2026-06-23.txt` (+ JSON sidecar)

**Lineage:** the RAIL block of [[project_age_grade_default_result]] (`runs/lc_age_grade_default_2026-06-22.txt`,
lines 82–92) proved grade prices the young **2.9× harder than realized DEFAULT justifies**
(grade_load +0.414 vs default_load +0.144 at [18,25); grade−default = +0.27). That settles
"grade encodes age-beyond-default" — grade is NOT exonerated. This experiment asks the next, sharper,
**P&L-costing** question that the RAIL does not answer.

## Question

Default *incidence* is not lender *return*. Return folds in prepayment timing, recovery, charge-off
severity, and months of (inflated) interest actually collected. So:

**Net of lawful risk, do the young — whom grade over-prices by +134bps past default-justified — deliver
EXCESS realized return to the lender, or NOT?**

Two outcomes, opposite signs, both publishable-to-ourselves:

- **Young excess realized return > 0 (lender profits from the overcharge):** the high price converted to
  real margin. The "they're just riskier and we're compensated" defense **survives** — bias against the
  borrower, lender's interest served. Less interesting for the empty chair; honest if true.
- **Young excess realized return ≤ older bands despite the +134bps overcharge (overcharge did NOT pay off):**
  the bank priced them as riskier than they were AND the extra price did not become margin (charge-offs ate
  it, or — the version we can't see in resolved-only data — the priced-out-profitable never appear). This is
  the **bias-against-the-lender's-own-interest** signature ([[feedback_bias_against_interest]]) that strips the
  rationality defense. The empty-chair version that "lands" ([[project_empty_chair_as_method]]).

A null (young return ≈ old return, flat) is also a real result: the overcharge is exactly offset by excess
realized loss → grade is doing its job on *realized* economics even though it over-loads age vs default
incidence. Record and move on. We hunt insight, not a paper.

## Outcome variable (realized, NOT modeled)

Per resolved loan, realized net return to the lender as a **rate of return on funded principal**:

    realized_return = (total_pymnt + recoveries − funded_amnt) / funded_amnt

- `total_pymnt` = all cash the borrower paid (principal + interest + fees). `recoveries` = post-charge-off
  recovery. `funded_amnt` = principal disbursed. Resolved loans only (Fully Paid / Charged Off) so
  `out_prncp ≈ 0` and the cashflow is complete — no censoring of in-flight loans.
- **NOT annualized** in the primary spec: term differs by loan and annualizing injects a duration model.
  Robustness cell annualizes by `term_months` to check the sign survives duration normalization.
- Guard: resolved-only ⇒ `out_prncp` near 0; assert median |out_prncp| < $1 in a smoke test, else the
  cashflow is incomplete and the metric is invalid.

## Design (mirror the residual/grade-default cells)

- **Cell A — raw realized_return by age band**, lawful controls (fico_mid, dti, annual_inc, loan_amnt,
  term_months, C(purpose)), reference band [45,50). OLS, per-band coefficient in **return points**
  (×100 for readability; this is return, not a rate, so units are "pp of funded principal").
- **Cell B — net-of-grade:** add C(grade). If the young return-excess SHRINKS net of grade the way the
  *price* excess did (+209→+27), grade is internalizing the return economics; if it does NOT shrink, the
  realized-return story is independent of grade's pricing.
- **Cell C — decompose:** realized_return = interest_collected_rate − loss_rate, where
  interest_collected_rate = total_rec_int / funded_amnt and loss_rate = (funded_amnt − total_rec_prncp −
  recoveries) / funded_amnt. Band each separately. This is the mechanism: do the young pay MORE interest
  (overcharge collected) and ALSO lose MORE (default severity), and which wins?
- **Positive control (anti-confabulation):** inject a synthetic +5pp return premium on a random 10% of
  young loans, assert Cell A recovers it within CI. Mirrors the guard in `wedge/age_residual.py`.

## FROZEN PREDICTION LEDGER (set BEFORE the run — do not alter)

- **Claude (sign):** young [18,25) excess realized return is **NEGATIVE or ≈ 0**, NOT strongly positive.
  Reasoning: the RAIL already showed grade over-prices the young vs *default incidence*; if that over-pricing
  also paid off in realized margin, grade would be defensible-on-economics and the over-load would be
  "expensive insurance that profits." I bet the charge-off **severity** at the young end eats the inflated
  interest, so the lender does NOT come out ahead — predicted young excess in **[−8pp, +2pp]**, and < the
  excess of the [25,30) band. The bias-against-interest signature is PRESENT.
- **Claude (decomposition, Cell C):** young collect MORE interest_rate (the overcharge is real, +) AND lose
  MORE (loss_rate +, larger in magnitude). Net negative or wash.
- **Tony's slot:**  Lenders penalize the young and profit from it. Why? Because if their own data showed they
   were losing money, they'd adjust for it.  But if their own data shows they are making money from the young,
   they'll do so because it makes good business sense.  What I can't predict is if they do it deliberately
   or simply because they're not searching their data to notice it. I'd suggest the higher the profit, the
   more likely it's deliberate.
- **Meta:** realized return is computable from `total_pymnt + recoveries − funded_amnt` on resolved loans
  without a duration model; the metric is well-defined (out_prncp≈0 guard passes).

Scoring on the fresh artifact: (a) sign of young excess, (b) young-vs-[25,30) ordering, (c) which Cell-C
component dominates, (d) whether net-of-grade kills it.

## Caveats that must travel

- **est_age IS credit tenure** (18+tenure); a credit-tenure gradient read as age. Same caveat as the lineage.
- **Survivorship / resolved-only:** loans still in-flight are excluded; if the young default *faster* they are
  over-represented in resolved-early, biasing realized return DOWN at the young end. Note direction; do not
  correct (the bias, if present, runs WITH the hypothesis → conservative for a null, anti-conservative for the
  negative finding → flag loudly).
- **The unobservable:** priced-out-profitable young borrowers who never took the loan are not in ANY LC file.
  Realized return understates the empty-chair harm by construction. State, do not estimate.
- Pricing = LC's realized cashflow, not a counterfactual lawful price. Old tail (70+) censored, small n.
