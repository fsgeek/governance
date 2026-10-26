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
consent of WebBank"). So this is a positive control for step 2, not a finding if it passes. Its information is in
failure: DOES_NOT_GOVERN means the disclosed policy is not the operative policy on the one criterion that is fully
quantified, which bears directly on the paper's record-versus-decision argument.

## 2. Data (public; already on disk)

- **Accepted:** `data/accepted_2007_to_2018Q4.parquet`. Columns used: `issue_d` (month), `dti` (excludes mortgage
  and the requested loan), `policy_code` (keep `== 1`, the public program), `application_type` (keep Individual).
- **Rejected:** `data/rejected_2007_to_2018Q4.csv`. Columns used: `Application Date` (day), `Debt-To-Income Ratio`
  (percent string). The "-1%" values (about 1.2M, meaning undocumented) and unparseable values are excluded and counted.
- The rejects file's DTI definition is undocumented, and rejects include declines for every reason. That dilutes a
  DTI effect but can't reverse its sign.

## 3. Tests

**A (accepted, monthly).** Share of issued loans with `dti` in a band, by month. Months that contain a change date are
dropped.
- **A1 (C2 up):** the share in [35, 40) averaged over 2014-08 to 2016-05 is ≥ 0.5%, and ≥ 10× its average over 2012-07 to 2014-06.
- **A2 (C3 down):** the share in [35, 40) averaged over 2016-07 to 2017-02 is ≤ 1/3 of its average over 2015-07 to
  2016-04 (1/3, not ~0, because exception programs such as direct-pay at 50% (V13) may continue).
- **A3 (C1 up):** the share in [30, 35) averaged over 2012-07 to 2013-06 is ≥ 10× its average over 2011-02 to 2012-04.

**R (rejects, daily).** For a change date d and an affected band b, with reference band [40, 50), above every cap ever written:
`r = n(b) / n([40, 50))` over a pre window [d−21, d−1] and a post window [d, d+20]. Effect `e = ln(r_post / r_pre)`, standardized as
`z = e / se` with se the Poisson standard error of e (`sqrt(1/b0 + 1/a0 + 1/b1 + 1/a1)`, counts +0.5). The placebo
is compared on z, because reject volume grows about 2000-fold from 2007 to 2018.
The window is 21 days so that C2's post window ends before the 2014-08-20 inquiry change (V12).
The reference band is above the caps, not below: a constructed test (pre-freeze) showed that a below-band control
lets a boundary that moved the *wrong* way, but below the band, read as a pass.
- **R1:** C1, b = [30, 35), predicted e < 0 (fewer declines in the newly allowed band)
- **R2:** C2, b = [35, 40), predicted e < 0
- **R3:** C3, b = [35, 40), predicted e > 0

**Placebo.** The same e, for each b, at every 1st and 15th of the month from 2011-03-01 to 2017-12-15, excluding
dates within 45 days of any dated policy change in the source table (V5–V18 effective dates, and the April 2016,
October 2016 and January 2017 tightenings). An R test **passes** if its z is beyond the placebo distribution's
5th percentile (for e < 0) or 95th percentile (for e > 0), on the predicted side. It **contradicts** only if |z| > 3 on the opposite side *and*
it's beyond every placebo z. A contradict alone decides DOES_NOT_GOVERN, so it gets the stricter
bar: with a 5% tail, a constructed no-break series read "contradict" by noise (pre-freeze test).

## 4. Decision rule (mechanical)

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
