# Pre-registration (DRAFT, not frozen): does LendingClub's written DTI policy govern its decisions?

**Status: DRAFT.** It freezes together with its harness (`scripts/lc_policy/governs.py` and tests) in one stamped
commit, after a blind adversary and after the harness passes on constructed violators. **No model is fit, and no
DTI-by-date tabulation of real data is made, before that commit.** The owner has seen only the column names, the
row counts and the format profile in `docs/research/lc-policy/2026-10-26-lc-credit-policy-history.md`.

**Program context.** This is step 1 of the reopened experiment (closing-note addendum, 2026-10-26). Step 2 is P vs G:
compiled written policy against generic monotone. Step 2 is designed and registered only if step 1 says GOVERNS.

## 1. Question and why it's a control

The written policy changed the DTI-excluding-mortgage cap three times on stated dates (source document, rows V7,
V11, V15):
- **C1, 2012-06-01:** 25% (30% if score ≥ 720) → 35%
- **C2, 2014-07-25:** 35% → 40%
- **C3, 2016-06-07:** 40% → 35% (now also excluding the requested loan)

If the written policy is the policy applied, the decline boundary moves with it: up at C1 and C2, *down* at C3.

**Documented behavior predicts GOVERNS** (the filings announce each change, and C3 "may not be changed without the
consent of WebBank"). So this is a positive control for step 2, not a finding if it passes. A positive control
that rarely fails mostly checks the harness, not the policy (finding 6); the thresholds above were set so it *can*
fail. Its information is in
failure: DOES_NOT_GOVERN means the disclosed policy is not the operative policy on the one criterion that is fully
quantified, which bears directly on the paper's record-versus-decision argument.

## 2. Data (public; already on disk)

- **Accepted:** `data/accepted_2007_to_2018Q4.csv`. The parquet copy lacks the filter columns (adversary finding 1).
  Columns used: `issue_d` (month), `dti` (excludes mortgage and the requested loan). Kept: `policy_code == 1` (public
  program), `application_type` Individual, `disbursement_method` Cash (direct-pay had a 50% cap, V13). Blank
  application type or disbursement method counts as Individual or Cash, since those columns were added late.
- **Rejected:** `data/rejected_2007_to_2018Q4.csv`. Columns used: `Application Date` (day), `Debt-To-Income Ratio`
  (percent string), `Policy Code`. Kept: `Policy Code == 0` (code 2, about 88k rows from 2014, is non-public credit
  policies, finding 4). The "-1%" values (about 1.2M, meaning undocumented, share rising about 20× in 2014) and
  unparseable values are excluded and **counted per month**; the report gives the exclusion rate in every test window.
- **Unknowns, stated:** the rejects-file DTI definition comes from a secondary dictionary, not LendingClub's own.
  Rejects include declines for every reason and incomplete applications, which dilutes a DTI effect but can't reverse
  its sign. The 2013-11-05 FICO-to-Vantage switch doesn't touch DTI and needs no exclusion.

## 3. Tests

**A (accepted, monthly).** Share of issued loans with `dti` in a band, by month. Each window skips the change month **and the month after it**
(application-to-issue lag, finding 7). A window with fewer than 6 usable months makes its test fail, never pass
(finding 9).
- **A1 (C2 up):** the share in [35, 40) averaged over 2014-09 to 2016-05 is ≥ 2%, and ≥ 10× its average over
  2012-08 to 2014-06. (2%, not 0.5%: 0.5% was trivially easy, finding 6. A uniform-ish spread under a 40% cap puts
  several percent in [35, 40).)
- **A2 (C3 down):** the share in [35, 40) averaged over 2016-08 to 2017-02 is ≤ 1/3 of its average over 2015-07 to
  2016-03. **Confound, stated:** the undisclosed April 2016 tightening targeted "high indebtedness". A2 can't separate it
  from the June cap cut, so A2 tests "the [35, 40) band closed by mid-2016", not C3 alone. R3 is the test aimed at C3 (1/3, not ~0, because exception programs such as direct-pay at 50% (V13) may continue).
- **A3 (C1 up):** the share in [30, 35) averaged over 2012-08 to 2013-06 is ≥ 10× its average over 2011-02 to 2012-04.
- **Construct check (finding 5):** the share of accepted loans with `dti` at or above the written cap, per regime
  (2012-08 to 2014-06 at 35%; 2014-09 to 2016-05 at 40%; 2016-08 to 2017-02 at 35%). If any regime is above 2%, the
  accepted tests are uninformative. A lender ignoring its cap and an accepted `dti` that isn't the policy's DTI look the
  same on this file, so the verdict is CONSTRUCT_INVALID, never DOES_NOT_GOVERN, and the R tests are reported on their own.

**R (rejects, daily).** For a change date d and an affected band b, with reference band [40, 50), above every cap ever written:
`r = n(b) / n([40, 50))` over a pre window [d−21, d−1] and a post window [d, d+20]. Effect `e = ln(r_post / r_pre)`, standardized as
`z = e / se` with se the Poisson standard error of e (`sqrt(1/b0 + 1/a0 + 1/b1 + 1/a1)`, counts +0.5). The placebo
is compared on z, because reject volume grows about 2000-fold from 2007 to 2018.
The window is 21 days so that C2's post window ends before the 2014-08-20 inquiry change (V12).
The reference band is above the caps, not below: a constructed test (pre-freeze) showed that a below-band control
lets a boundary that moved the *wrong* way, but below the band, read as a pass.
- **R1:** C1, b = [30, 35), predicted e < 0 (fewer declines in the newly allowed band)
- **R2:** C2, b = [35, 40), predicted e < 0
- **R3:** C3, b = [35, 40), predicted e > 0. **Expected failure mode, stated:** the April 2016 tightening plausibly
  raises [35, 40) declines inside R3's pre window, which would make R3 read null. Null here isn't evidence against
  the policy.

**Placebo.** The same z, for each b, at every 1st and 15th of the month from 2011-03-01 to 2017-12-15, excluding
dates within 45 days of any dated policy change in the source table (V5–V18 effective dates, and the April 2016,
October 2016 and January 2017 tightenings), and the whole undated V18 reversion interval 2017-03-09 to 2017-05-22
plus 45 days each side (finding 3). **Each test uses only placebo dates within 365 days of its own change date.**
With daily drift in the DTI mix, the Poisson z grows with volume, so late high-volume dates would otherwise set the
bar for the 2012 test (finding 2). An R test **passes** if its z is beyond the placebo distribution's
5th percentile (for e < 0) or 95th percentile (for e > 0), on the predicted side. It **contradicts** only if |z| > 3 on the opposite side *and*
it's beyond every placebo z. A contradict alone decides DOES_NOT_GOVERN, so it gets the stricter
bar: with a 5% tail, a constructed no-break series read "contradict" by noise (pre-freeze test).

## 4. Decision rule (mechanical)

- **CONSTRUCT_INVALID:** the construct check fails. The R-only verdict is reported beside it (R_GOVERNS: at least 2
  pass and none contradicts; R_CONTRADICTS: any contradicts; else R_MIXED). Step 2 is not registered.
- **GOVERNS:** A1, A2 and A3 all hold, at least 2 of R1–R3 pass, and none contradicts.
- **DOES_NOT_GOVERN:** A1 fails, *or* any R test contradicts.
- **MIXED:** anything else. Reported as such; step 2 is not registered on a MIXED result.

Documented behavior that would trigger each branch: GOVERNS, the filings enforced as written. DOES_NOT_GOVERN,
LendingClub applied a different DTI rule than it disclosed, or the accepted-file `dti` isn't the policy's DTI.
MIXED, exception programs or concurrent undisclosed tightenings (April 2016) dominate a window.

## 5. Forecasts (owner, before any tabulation)

| ID | p |
|---|---|
| A1 holds | 0.90 |
| A2 holds | 0.70 |
| A3 holds | 0.80 |
| R1 passes | 0.60 |
| R2 passes | 0.70 |
| R3 passes | 0.55 |
| Verdict GOVERNS | 0.65 |
| Verdict DOES_NOT_GOVERN | 0.10 |

## 6. Harness discipline

The harness is frozen with this file, and it is tested before the freeze on constructed data: a planted up-break, a
planted down-break, no break, and a reversed break. Each must produce the verdict the rule says. Percent parsing is
tested on "-1%", "35%", "35.0%" and junk. Band edges are half-open and tested at exactly 35.0 and 40.0. Nothing reads
the real files until the freeze commit exists.
