# Redundancy-as-common-cause REFUTED: the k=5 "canary" was an effect-size confound

**2026-06-10. Result for the frozen pre-reg [[2026-06-10-redundancy-mechanism-prereg]] (Fable's
conjecture). Script: `scripts/redundancy_canary_probe.py`. Output: `runs/redundancy_canary_probe.json`.
P1 REFUTED. My prior on it (0.65) LOST. The exciting first-run signal was an artifact my own guard
caught.**

## The conjecture (Fable, doc 2)

Detection-difficulty and floor-multiplicity share a common cause: REDUNDANT encoding. Spread a
disparity across k weak exchangeable proxies → exchangeability generates model multiplicity → band>1
at the tightest ε is a distributed-signal / fairwash CANARY. Falsifiable: floor flip-rate rises with k
at FIXED total disparity.

## The two runs (the second is the real one)

**Run 1 (BUGGED — effect-size confound):** flip-rate jumped 0.0 (k≤3) → 0.29 (k=5,8). Looked like a
clean threshold AT the frozen DGP's D4_K=5 — a gorgeous confirmation. **But the guard I built into the
probe fired:** realized disparity gap slid 0.358→0.251 as k rose — NOT k-invariant. Per-carrier noise
summed across k carriers diluted the disparity. The "canary" was tracking the declining effect size,
not redundancy.

**Run 2 (noise scaled b/√k so summed noise variance is k-invariant → disparity genuinely fixed):**

```
  k   mean_band   mean_flip_rate   realized_gap_G
  1     1.7          0.0075           0.358
  2     1.3          0.000            0.353
  3     1.0          0.000            0.344
  5     1.0          0.000            0.358   <- the k=5 "jump" is GONE
  8     1.7          0.0074           0.353
  guard: gap stable = True (0.344-0.358)
```

**Flat at ~0 across all k. P1 REFUTED: redundancy (k at fixed disparity) does NOT drive floor
multiplicity.** The entire k=5 signal was the effect-size confound; it vanished the moment disparity
was held fixed.

## What dies and what survives (calibrated)

- **DIES: the redundancy-common-cause mechanism, and with it the "fairwash canary" reframe.** Band>1
  at the floor is NOT a clean distributed-signal detector — at least not via encoding redundancy k.
  Fable's conjecture and my 0.65 prior both lost.
- **SURVIVES (as an OBSERVATION with an OPEN cause):** the original co-occurrence — D4 (distributed)
  had a contradictory floor-band while D2/D3 didn't ([[2026-06-10-shuffle-set-epsilon-curve]],
  itself already downgraded to a seed-sensitive gradient). That observation stands, but its CAUSE is
  now shown NOT to be redundancy-k. It must be something else in the D4 channel's specific geometry
  (carrier correlation structure, or CART's interaction with it). Mechanism OPEN; the redundancy
  hypothesis for it CLOSED.
- **The cross-family build (P2) is now moot for THIS purpose** — there's no redundancy effect to test
  for sampler-invariance. (The cross-family sampler robustness is still owed for the protected-
  blindness result generally, but no longer carries this frozen theorem.)

## Why this is a clean result, not a disappointment

The probe had a confound guard built in BECAUSE [[feedback_covariate_adjust_all_arm_correlates]]
demands controlling all arm-correlates; the guard caught the exact failure (disparity not fixed) and
the fix dissolved the result. This is the discipline working at full strength: a beautiful,
prior-confirming, story-completing signal (canary fires exactly at D4_K=5!) turned out to be an
artifact, and was killed by a control I wrote before I saw the number. Had I not held disparity fixed,
I would have shipped "irreducible multiplicity is a fairwash detector" — a publishable-looking claim
built on a confound.

## Meta

The single most seductive result of the engagement (it confirmed a sharp prior, completed an elegant
mechanism, AND matched a magic constant in the frozen DGP) was the falsest. Comfort was the tell,
maximally. Engagement: priored predictions now 0-for-7; the guard-caught confounds are the procedure
earning its keep. Fable's conjecture was excellent and wrong — which is the best kind of conjecture,
because it was sharp enough to be killed in one controlled run.
