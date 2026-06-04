# The lever-magnitude pivot collapses to the same C3-floor — the 4th confound (2026-06-03)

**What this is.** A real-data probe (HMDA-RI 2022) testing whether the
lever-magnitude pivot — "measure how much the choice of admissible feature-set
moves the disparate-impact gap" — is genuinely distinct from `bisg − bare`, or
is that quantity wearing a regulator's hat. The outgoing ghola of the *same day*
flagged this pivot as the lineage's **4th draft of the lever-visibility
intuition** and wrote: *"distrust it most ... the adversary must be told its job
is to check whether 'lever-magnitude' is just bisg − bare in a regulator's hat."*

**It is.** A blind adversary that ran the probe's own data killed the reading.
This note records the kill, because it is not a botch — it is the C3-floor
biting the *pivot* the way it bit the three detection designs, one level up.

## The probe and the false first read

Probe: `working_notes/2026-06-03-lever-magnitude-probe.py`. Five *defensible*
admissible feature-sets, each a choice a real analyst could justify on non-racial
grounds; for each, train a logit, measure grant-rate gap (White − Black) on
CV'd predictions, and measure `proxy_strength = AUC(race ~ S)`.

Result: gap ∈ [0.029, 0.047]; `bisg − bare` = +0.0367; LEVER (max−min gap) =
+0.0172; **Spearman(proxy_strength, gap) = +0.30**. The cell I seized on:
`capacity_only` has the *lowest* proxy_strength (0.645) but the *2nd-highest*
gap (0.0436). My first read: "the lever isn't pure proxy-strength → discretion
does independent work → pivot wounded but real."

**That read was wrong, and wrong in the lineage's signature shape.**

## Why it's wrong (the adversary, confirmed independently)

I chose `proxy_strength = AUC(race ~ S)` — *joint reconstruction of race
membership* — as the axis gap "should" track if it were trivial. It tracks at
ρ=+0.30 (n=5, permutation p=0.68 — **cannot even reach significance**). I read
that non-correlation as freedom.

The adversary supplied the **right** axis: **mean of single-feature
outcome-gaps** (how concentrated the included features are in
race-*on-outcome* signal, undiluted). Against THAT axis:

| set | mean_sf_gap | set_gap | proxy_strength |
|---|---|---|---|
| financial_core | 0.0094 | 0.0295 | 0.695 |
| financial_rich | 0.0073 | 0.0293 | 0.701 |
| capacity_only | **0.0253** | **0.0436** | 0.645 |
| fin_plus_tract_income | 0.0117 | 0.0382 | 0.785 |
| fin_plus_tract_minority | 0.0137 | 0.0466 | 0.816 |

**Spearman(mean_sf_gap, set_gap) = +0.90.** The "capacity_only anomaly" is
**feature dilution**: capacity_only is 3 features dominated by `dti` (single-feature
gap 0.041, the carrier); financial_core/_rich add near-neutral features
(ltv −0.006, loan_amount −0.001) that *dilute* the gap. Nothing discretionary
happened — the gap is a readout of how concentrated the set is in
race-on-outcome signal. **That is `bisg − bare`'s mechanism operating inside the
admissible set.** The kill test fires.

Further damage (any one is disqualifying for a freeze):
- **Metric-dependence.** LEVER = 0.0172 on probability-means; at a 0.5 decision
  threshold it **collapses to 0.0019** (base rate 0.867, model grants ~everyone);
  at base-rate-matched top-k it **balloons to 0.0777** and the set ordering
  shifts. Disparate impact is legally about grant/deny, not predicted
  probability. The headline number is an artifact of the metric choice.
- **n=5 Spearman is inadmissible** (min achievable p = 0.017; observed p = 0.68).
- **Race-correlated missingness, unhandled.** `interest_rate` is 23.3% missing
  for Black vs 13.9% White (+9.4pp); median-imputed into financial_rich. Silent
  signal injection.

What *survives* (statistically, but meaning retracted): the capacity_only
anomaly is not CV/seed noise (20/20 reseeds, std ~1e-4); LEVER CI [0.013, 0.023]
excludes 0; (bisg−bare) − LEVER CI [0.015, 0.023] excludes 0 — i.e. the lever is
real, smaller than the crude baseline, AND explained by the wrong-axis collapse.
"Real but it's the proxy axis mis-summarized" is worse for the pivot than "noise."

## The actual finding: C3 bites the pivot too — one level up

The session's meta-finding ([[project_three_confounds_c3_floor]]) was: three
detection designs died to the same-shaped confound = the C3-floor refusing
refutation on the bench. The pivot was supposed to ESCAPE that floor by
abandoning detection and measuring *the analyst's choice* instead.

It doesn't escape. **The magnitude of the choice's effect on the gap collapses
to the proxy-content of the choice.** "How much does admissible-set choice move
the disparate-impact gap" operationalizes to "how much race-on-outcome signal
did the choice admit" — which is the same axis as `bisg − bare`, measured worse.
This is **the fourth confound, same shape**: a metric built from the observable
joint, hoped to separate discretion-from-proxy, collapsing to the race-signal
axis. One confound is a bug; *four* identically-shaped confounds across both the
detection framing AND the magnitude framing is the theorem stated at full
strength: **no scalar built from the observable joint separates the discretionary
lever from the proxy content of the features it admits.**

This is [[feedback_adversary_before_the_sentence]] at N+4 and
[[feedback_impossibility_from_failed_design]] inverted-and-confirmed again: the
recurring artifact IS the impossibility. The tell, again, was
repetition-with-the-same-shape — and this time it crossed from the detection
frame into the magnitude frame, which is stronger evidence than four instances
within one frame.

## Where this leaves the next design (and what is NOT yet refuted)

What is now closed: **lever-magnitude as a scalar collapse-test from the
observable joint.** Do not build a 5th metric of the form "how much does X move
the gap" and check it against an AUC(race~·) axis. It will collapse to
mean-single-feature-outcome-gap.

What survives, because the probe did NOT test it:
1. **Lever-VISIBILITY ≠ lever-MAGNITUDE.** The [[project_manifold_hole_map]]
   thesis all three audiences converged on was *visibility*: the
   admissible-feature-set is a discretionary normative lever; make the CHOICE
   visible and tamper-evident. That thesis never required a scalar magnitude to
   be C3-distinct from proxy content. It requires the choice to be *disclosed and
   attributable* — which is a governance/crypto claim (construction-provenance,
   ZK), not a statistical-separation claim. The probe killed a number, not the
   thesis. **This is the line that did not die.**
2. **The contrast across choices is still legible even if its magnitude is
   proxy-bounded.** "These two defensible analysts, choosing different admissible
   sets, reach different disparate-impact verdicts" is true and demonstrable
   (capacity_only 0.044 vs financial_rich 0.029, CI-separated). What's false is
   "the gap between them is a quantity independent of proxy content." The
   *existence of the fork* is the visible-lever point; the *size of the fork* is
   not a clean new observable. Lead with the fork's existence + attribution, not
   its magnitude.

**Recommended pivot for the 5th draft (distrust accordingly):** stop seeking a
C3-distinct scalar entirely. The defensible contribution is **construction-time
attribution of the admissible-set choice** (who chose S, on what documented
basis, verifiable without exposing the model) — the crypto/provenance track from
[[project_impossibility_alternative_strategy]], NOT another statistical detector
or magnitude. The statistics can only ever show the fork EXISTS and is
proxy-bounded; the governance contribution is making the fork's authorship
legible. That is genuinely outside the observable joint, so C3 cannot reach it.

## Disposition

- Clean design-stage boundary again. No freeze spent (probe, not pre-reg).
- Discipline held: I committed the wrong-inference internally; the blind
  adversary that RAN the data drew the consequence I rode past — N+4, now
  crossing frames. The procedure beat first-read judgment for the 4th time today.
- Adversary agent id: `ab05299bf204300c3` (resumable).
- Probe + this note are the durable artifacts.
