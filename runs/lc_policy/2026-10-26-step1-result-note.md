# Step 1 result: LendingClub's written DTI policy GOVERNS its decisions

**Run:** 2026-10-26, frozen harness `scripts/lc_policy/governs.py` (sha256 `8451237b7f9f...`, unchanged since freeze
`65fe5f4`), output `runs/lc_policy/step1_result.json`, 5m46s. Pre-registration:
`docs/superpowers/specs/2026-10-26-lc-written-policy-governs-prereg.md`.

**Verdict: GOVERNS** (mechanical; R-only verdict R_GOVERNS). Every test passed. Data: 2,066,816 accepted loans kept of
2,260,701; 27,648,741 rejects, of which 89,047 were dropped as Policy Code 2 and 1,190,038 had their DTI excluded.

| Test | Result | Values |
|---|---|---|
| Construct check | ok | share of accepted loans at or above the written cap: **0.0%** in all three regimes |
| A1-ratio / A1-floor (C2, 2014-07-25, cap 35→40) | pass / pass | share in [35, 40): **0.0%** before, **3.89%** after |
| A2 (C3, 2016-06-07, cap 40→35) | pass | share in [35, 40): **3.98%** before, **0.0%** after |
| A3 (C1, 2012-06-01, cap 25/30→35) | pass | share in [30, 35): **0.0%** before, **6.09%** after |
| R1 (C1, rejects) | pass | z = −8.88, local placebo 5–95% [−1.73, 1.52], n = 32, exclusion shift 0.0 pp |
| R2 (C2, rejects) | pass | z = −8.94, placebo [−3.33, 2.00], n = 28, exclusion shift 3.3 pp (rule: null above 5) |
| R3 (C3, rejects; the reversal) | pass | z = +4.51, placebo [−2.95, 1.58], n = 13, exclusion shift 1.8 pp |

**Reading.** On the one criterion LendingClub quantified, its written policy is the operative policy, enforced
without exception in the kept population: no accepted loan sits at or above the written cap in any regime. The
decline boundary moves on the stated dates, *in both directions*, including the 2016 reversal (R3) that the
pre-registration expected might read null. As the pre-registration said in advance, this is a **positive control**:
documented behavior predicted it. It licenses step 2 (P vs G), and is not itself a finding. The near-threshold item is
R2's exclusion shift (3.3 pp against a 5 pp rule), which the "-1%" growth during 2014 predicted.

**Forecasts scored** (registered in the pre-reg §5 before any tabulation):

| ID | p | Outcome | Brier |
|---|---|---|---|
| A1-ratio holds | 0.90 | yes | 0.010 |
| A1-floor holds | 0.55 | yes | 0.203 |
| A2 holds | 0.70 | yes | 0.090 |
| A3 holds | 0.80 | yes | 0.040 |
| R1 passes | 0.60 | yes | 0.160 |
| R2 passes | 0.70 | yes | 0.090 |
| R3 passes | 0.55 | yes | 0.203 |
| Verdict GOVERNS | 0.45 | yes | 0.303 |
| Verdict DOES_NOT_GOVERN | 0.10 | no | 0.010 |

Mean Brier 0.123, with every miss on the side of underconfidence. The owner priced in confounds (April 2016, the
floor, exclusion growth) that turned out not to bite. Nine correlated forecasts on one dataset; no calibration claim.

## Caveat added after review (2026-10-26; the result above is unchanged)

Step 1 kept accepted loans with `policy_code == 1` and rejects with `Policy Code == 0`, as pre-registered. Policy Code 2
is LendingClub's own label for loans outside the public credit policy (e.g. FICO 640–659; step-2 adversary, item 1).
So "0.0% of accepted loans at or above the written cap" partly measures LendingClub's own sorting into the public
program. It isn't independent evidence that every loan it made followed the written policy. What stands without the
caveat is that the boundary moved on the stated dates, in both directions, in accepts and in declines. A post-hoc
sensitivity (labelled as such, not pre-registered) reporting the Policy Code 2 accepted loans' cap-violation share
is owed.
