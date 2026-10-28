# Step 2 result: INCONCLUSIVE (5 of 5 seeds VOID)

**Run:** 2026-10-28, frozen harness `scripts/lc_policy/pvg.py` (sha256 `7a5638a4882f...`, unchanged since freeze
`424db92`). Output: `runs/lc_policy/step2/step2_result.json`, 24 min. Pre-registration:
`docs/superpowers/specs/2026-10-28-lc-step2-policy-vs-generic-prereg.md`. Data: 348,848 applications (322,366 rejects,
33,749 accepts; 7,267 excluded for missing score, DTI or amount); accept share 9.7%.

## Verdict (mechanical): INCONCLUSIVE

All 5 seeds are **VOID**. About 2,000 of 4,000 sampled trees per seed passed the monotonicity check, but only **27–43**
had a log-loss excess ≤ 0.05, against the pre-registered floor of 200. ε\* is undefined. The capacity check didn't
run, because it applies only to a non-INCONCLUSIVE verdict. Per §9, **INCONCLUSIVE is reported as such, with no
second attempt on this window.** Step 2 is closed.

**Why the design failed:** the synthetic power check predicted about 2,600 trees in the band. Real LendingClub decisions
give a far more spread-out model landscape: most monotone trees are more than 5% worse than the best. The power check
was wrong about the one thing it existed to check. A synthetic follower isn't a model of the real decision process,
and that should have been treated as an open risk, not as evidence.

## Pre-registered quantities, reported (not the verdict)

- **Construct share = 0.0.** No accepted loan, 2011-03 to 2012-05, lies inside the written V5/V6 rule's declined region
  (with tolerances). LendingClub enforced the FICO-720 × DTI interaction rule exactly. This closes the cell step 1
  never checked (second-adversary finding 1). It's the cleanest result of step 2, and it's a construct check, not the
  test.
- **Every tree in the band is materially corrected by the gate, including the best tree in every seed:** best-tree
  z = 20.6–21.9, gain 0.0015–0.0017 nats. So the best-fitting monotone depth-≤4 tree of LendingClub's decisions
  misstates its written rule. The record corrects even the best model. With n_G of about 40, this is a description of
  a small set, not a verdict.
- **Reason fidelity:** over applicants the written rule declines and the ε = 0.01 band, **about 92% of (applicant,
  model) pairs give a first reason outside the rule's own reasons** (92.0–92.1% in all 5 seeds). **Caution before any
  reading:**
  - Employment length is coded −1 for 3.4% of accepts but 0.9% of rejects, so `emp` can partly mark the file of
    origin (third-adversary finding 6).
  - Which feature was given as the reason wasn't recorded.
  - It's a secondary metric over a band of about 30–40 trees.

  It's a lead for a separately pre-registered study, not a finding.

## Forecasts scored (pre-registration §8)

| ID | p | Outcome |
|---|---|---|
| Verdict KILL | 0.20 | no |
| Verdict POLICY_MATTERS | 0.20 | no |
| Verdict DEPENDS_ON_EPSILON | 0.45 | no |
| Verdict CONSTRUCT_INVALID | 0.10 | no (share 0.0) |
| Verdict CAPACITY_DEPENDENT or INCONCLUSIVE | 0.05 | **yes** |
| ε\* median in [0.005, 0.02] | 0.50 | no (undefined) |

The owner put 0.05 on the outcome that happened, and 0.70 (r4 table) on "at least 4 of 5 seeds non-VOID". Both are
bad misses, from trusting the synthetic power check.

## What the reopened program now holds

- **Step 1 (GOVERNS):** LendingClub's written DTI cap was its operative policy, moving on the stated dates in both
  directions.
- **Step 2 construct check:** the 2011–12 FICO-conditional rule was also enforced exactly.
- **Step 2 test (INCONCLUSIVE):** whether compiling the written policy changes the set of near-optimal models couldn't
  be decided, because too few trees are near-optimal at all.
- **One observation consistent with "a model of the decisions isn't evidence of the rule":** the best tree is
  corrected by the record. It needs its own pre-registration (with richer model classes, and an `emp` coding fix)
  before it can carry weight.
