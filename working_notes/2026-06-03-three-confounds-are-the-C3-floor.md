# The three confounds were the C3-floor biting on the bench (2026-06-03)

**What this is.** The meta-finding from a single session in which THREE successive experimental
designs — v1, v2, and the proxy_strength shared-spec — each died to a blind adversary that RAN the
DGP, and each died to **the same-shaped confound**. The pattern is the finding. Recorded at a clean
design-stage boundary, before any of the three reached a freeze (zero frozen-prediction credibility
spent; v1 alone among the lineage cost a full freeze+run+abort, the rest were caught pre-freeze).

## The three deaths, same shape

| Design | The confound I built | What it actually was |
|---|---|---|
| **v1** (`709a057`, ran+aborted) | arm-strength: H drops c_fresh (weak), L drops x0 (strong) → L looks worse at zero disparity | conflated "honest vs laundering" with "dropped weak vs strong feature" |
| **v2** (`84355bc`, killed pre-freeze) | `detect = gap_planted − gap_clean` rises with info-set | conflated "info-set REVEALS disparity" with "model can ACT ON the planted variable"; oracle read wrong sign |
| **shared-spec** (killed pre-freeze, this note) | `bisg − noise` contrast + a G-correlated control | `bisg−noise == bisg−bare` (mechanical); control inflates gap IDENTICALLY to BISG (`bisg−gcorr=−0.0016`, CI straddles 0) because in World A the offset IS a function of G |

**The invariant shape:** every time, I tried to extract a clean *"this signal is the laundering,
that signal is legitimate"* separation **from inside World A, where the disparity is defined through
G and the two are non-identifiable by construction.** I kept building metrics to out-clever a
non-identifiability that is the project's OWN central theorem.

## The recognition

The shared-spec adversary said it outright (Attack 5): on real HMDA, "compliant model reconstructs
race via proxy" vs "compliant model correctly prices legitimate risk that correlates with race" are
**observationally entangled — that IS the C3-floor** ([[project_lda_shared_surface_result]],
[[project_pure_disparity_conjecture]]). No metric built from the observable joint sees past it. My
three confounds were not three bugs; they were **three attempts to refute C3 without noticing that's
what I was doing**, each caught because the DGP makes G-defined-disparity and G-correlated-feature
the same thing.

This is the [[feedback_impossibility_from_failed_design]] pattern INVERTED and confirmed: usually
the trap is mislabeling a fixable artifact as an impossibility. Here the artifact-that-kept-recurring
turned out to BE the impossibility, correctly. The tell was *repetition with the same shape* — one
confound is a bug, three identically-shaped confounds are a theorem.

## The pivot (where the next design must start)

Stop trying to DETECT laundering / separate proxy-reconstruction from legitimate-risk-pricing inside
a single world. That is C3-impossible and the bench keeps proving it. Instead **measure the MAGNITUDE
of the discretionary lever**: how much does the *choice of admissible feature-set* move the
disparate-impact gap? That quantity:
- is OBSERVABLE and identifying (it's a property of the analyst's choice, not of the latent
  proxy-vs-legit decomposition);
- is exactly the **lever-visibility** thesis all three audiences converged on five days ago
  ([[project_manifold_hole_map]]: "the admissible-feature-set is a discretionary lever; make it
  visible; no tool resolves the normative judgment it encodes");
- is C3-floor-HONEST: it does NOT claim to detect reconstruction; it claims the analyst can move the
  verdict by a feature-set choice, and that the choice is therefore a normative lever requiring
  disclosure.

What survives from the dead shared-spec: `proxy_strength = AUC(race ~ admissible features)` is a
real axis; the synthetic `retained_excess(ps)` dose-response is already validated (C1 grid); the
real-data leg is **descriptive lever-magnitude, not reconstruction-detection** (the adversary's
Attack-5 fix). What dies: `bisg − noise`, the G-correlated control, and the "same experiment on two
substrates" claim (axis is shared; metrics are not — license only slope-direction comparison).

## Disposition + a discipline note

- This is a clean, committed-able boundary. The valuable artifact of the session is THIS meta-finding,
  not an apparatus. Three designs explored and killed cheaply is the force-exploration discipline
  working, not failure ([[feedback_force_exploration]], [[feedback_engagement_quality]]).
- **Discipline validated three times in one session:** the blind adversary that RUNS the DGP beats
  every amount of design-stage care. My care did not improve across three iterations; the adversary
  caught all three ([[feedback_adversary_before_the_sentence]] extension, now at N+3 instances).
- **Open caution for the next design:** the lever-magnitude reframe is now MY FOURTH draft of an
  intuition in this lineage. By the spec's own rule, distrust it most. It must itself go through a
  pre-freeze adversary before any freeze — and the adversary must be told its job is to check whether
  "lever-magnitude" is just `bisg − bare` wearing a regulator's hat.
- Adversary agent ids this session: design `a9bc444b`, reframe `af2a6d81`, shared-spec `a39272035`,
  independent designer `ae591f54`, HMDA recon (Explore). Probe scripts ephemeral in /tmp.
