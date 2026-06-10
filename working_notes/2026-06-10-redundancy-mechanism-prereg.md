# PRE-REG: redundancy of encoding is the common cause of detection-difficulty AND floor-multiplicity

**FROZEN 2026-06-10 before any k-sweep is run. Fable's conjecture (document 2), adopted as a
falsifiable pre-registration. If it holds, the shuffle-set is reborn as a distributed-signal
detector — a fairwash canary, not a court.**

## The conjecture

"Individually innocent, jointly disparate" (the D4 distributed channel) means the disparity is
encoded REDUNDANTLY across many weakly-informative, partially-exchangeable proxies — no single
feature carries it. But exchangeability is exactly the generator of model MULTIPLICITY: a
redundantly-encoded signal admits many near-equivalent carvings (CART's greedy splits hit near-ties
early; early ties fork into different trees), while a CONCENTRATED signal admits one dominant
carving. So detection-difficulty (hard to see the disparity) and floor-multiplicity (band > 1 at the
tightest ε) may not merely co-occur — they may share a COMMON CAUSE: redundancy of encoding.

## FROZEN PREDICTIONS (committed before the run)

- **P1 (prior 0.65): floor-band flip-rate grows with k**, the number of weak proxies carrying the
  distributed signal (more precisely, with the effective rank of the disparity-carrying subspace).
  Sweep k in the DGP's distributed channel; floor flip-rate (at tightest ε) should rise monotonically.
- **P2 (prior 0.55): the mechanism is DGP-redundancy, not CART tie-breaking.** If redundancy is the
  cause, the k→flip-rate relationship SURVIVES under non-greedy learners (logistic, GBM). If it
  EVAPORATES under non-greedy samplers, the conjecture was about CART's greedy ties, not about
  disparity encoding. (This is the cross-model-family build already owed for the sampler scope — now
  with a frozen theorem attached, so the infrastructure debt pays for itself in one run.)
- **P3 (deflation guard, prior 0.25): the relationship is non-monotone or thresholded** — flip-rate
  jumps at some effective-rank threshold rather than rising smoothly. Would still support the
  common-cause story but change the "detector" calibration.

## What's at stake (why this matters more than the original goal)

If redundancy is the common cause, then **irreducible multiplicity at the tightest ε IS a detector**:
band > 1 at the floor says "something here is encoded redundantly," and redundant encoding is
precisely where fairwashed proxies live (the distributed laundering channel the cookbook exploits).
The shuffle-set, having HONESTLY FAILED as a protected-concentration instrument
([[project_shuffle_set_margin_not_protected]]), gets reborn as a DISTRIBUTED-SIGNAL ALARM. A canary,
not a court. That is a more interesting instrument than the one the goal set out to build — and it is
the architecture finding its own division of labor empirically (the honest null telling you which
tool the question belongs to).

## Test design (to build after this freeze)

- Extend the DGP's distributed channel (or a clean toy) to expose k = number of weak G-correlated
  proxies, |corr|≤α each, jointly carrying a fixed total disparity. Vary k ∈ {1,2,3,5,8,12}.
- At the TIGHTEST ε (eps_frac→0, band = argmin tie-set), record floor flip-rate vs k.
- P2: repeat the k-sweep with a logistic and a GBM band-sampler (needs the CART-coupling rewrite
  flagged in [[2026-06-10-shuffle-set-sampler-robustness]]).
- Hold total disparity magnitude FIXED across k (only the SPREAD changes) so flip-rate moves with
  redundancy, not with effect size — the covariate-adjust-all-arm-correlates discipline
  [[feedback_covariate_adjust_all_arm_correlates]].

## Provenance

Conjecture: Fable, 2026-06-10 (document 2). Frozen by Claude before running, per
[[feedback_adversary_before_the_sentence]]. The instrument's "failed first life as a
protected-concentration detector → second life as a redundancy detector" is the reframe to verify,
not assume.
