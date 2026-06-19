# The shuffle-set is the margin-ambiguous population, and it is protected-BLIND

**2026-06-09. Goal: characterize the shuffle-set (borrowers whose decision flips across tied-on-loss
band members) — is it the C3 floor with protected names, or diffuse? Script:
`scripts/shuffle_set_probe.py`. Output: `runs/shuffle_set_margin.json`. Fable supplied the
margin-confound control that made the result trustworthy.**

## FROZEN PREDICTION — REFUTED

H (prior 0.55): shuffle-set is G-concentrated (P(flip|G1)/P(flip|G0) ≥ 1.3, flippers near boundary).
Tony's "switching models shuffles the discrimination around the same protected people."

**Refuted on all four disparity channels.** Raw g_ratio ≈ 1 (D1 1.09, D2 0.95, D3 1.05, D4 0.98).
But raw ratio is confounded — so the load-bearing measure is the MARGIN-CONTROLLED one (Fable
point 1): at the SAME distance-from-threshold, do protected-correlated borrowers flip more?

**margin_pooled_g_diff ≈ 0 in every channel: D1 0.005, D2 0.002, D3 0.006, D4 0.007.** Holding
margin fixed, the protected group flips at the same rate as everyone else. flip-direction
correlation with G ≈ 0 (−0.01, −0.09, +0.09, +0.06 = noise). The shuffle-set is G-BLIND even
controlling for margin, including D1 (direct un-laundered disparity) and D4 (distributed, fiendish).

## The boundary-concentration finding was a MECHANICAL ARTIFACT (Fable point 1, confirmed)

My uncontrolled "flippers cluster near 0.5" was circular: a flip MEANS members disagree, which
happens at the boundary. The margin bins show it directly — mid-margin bins [0.2,0.8) have
P(flip)=1.000 for BOTH groups (definitional), and the only bins with variation (the confident tails)
show small G-diffs that SIGN-FLIP across channels (D1 +0.054/−0.072; D2 −0.050/+0.049) = noise.
Without the margin control I would have shipped a mechanical artifact as a finding. A referee deletes
that in one sentence; Fable caught it before the sentence.

## WHAT THIS MEANS (calibrated; the refutation is the finding)

- **The discrimination floor and the model-multiplicity shuffle are DIFFERENT objects.** The band
  relocates decisions among the genuinely MARGIN-AMBIGUOUS, without respect to G. Tony's
  "shifting it around the same protected people" intuition does not hold on this substrate.
- **This is arguably BETTER for the project than H.** The harm from "pick one" is not "the same
  protected people keep getting moved." It is that **genuinely-marginal applicants get a coin-flip
  whose outcome depends on an unaudited model choice, regardless of protected status.** That is a
  DUE-PROCESS / arbitrariness problem broader than disparate impact — and it SURVIVES the post-2026
  regime where disparate-impact enforcement is being dismantled ([[project_regime_change_2026]]),
  because it is about arbitrariness, not protected-class disparity. The empty chair here is the
  marginal applicant, not (only) the protected one.
- **Stability holds (Jaccard 0.25–0.30):** it is substantially the SAME marginal people flipping
  across member pairs — a stable arbitrarily-treated population, not random churn. So "make the
  shuffle-set a first-class audited quantity" still stands; what changed is WHO it is (margin, not
  protected).
  > ⚠ CORRECTION (2026-06-10, Fable): this bullet is WRONG twice. (1) `mean_pairwise_jaccard`
  > measures WITHIN-band member-pair overlap, NOT across-seed membership — so "the same people
  > across seeds" was unmeasured and asserted. (2) Across-seed flip-SET membership is only weakly
  > conserved (Jaccard ~0.5 even restricted to common rows): the set whose outcome is arbitrary is
  > itself seed-arbitrary. What IS stable is the per-applicant P(flip) SCORE (bimodal, margin-tracking,
  > G-blind). The audited quantity is the SCORE, not the SET. See [[2026-06-10-set-to-score-pflip]].

## SCOPE / LOSSES BANKED (Fable points 2–4 — honest limits, declare in any write-up)

2. **ε is a researcher degree of freedom.** Shuffle-set size is violently ε-sensitive
   ([[project_band_epsilon_inert]]). MUST report the shuffle-set-vs-ε curve, never a point. This run
   used one normalised tol (epsilon_frac=0.01); the ε-curve is OWED before any claim. [open item]
3. **The band is SAMPLED, not enumerated.** This is multiplicity under one sampler S (CART
   feature-subset × depth × leaf sweep). Different samplers (seeds, regularization paths) surface
   different multiplicity. The claim is "multiplicity under sampler S," declared, not implied.
4. **THE REFLEXIVE C3 LOSS (Fable point 4, the most honest paragraph).** This result used the
   SYNTHETIC DGP where G is ground-truth. On REAL data (FM/LC carry no protected attribute),
   "protected-correlated" must itself be CONSTRUCTED (HMDA linkage / BISG proxy) — so the apparatus
   that would make the C3 floor visible STANDS ON the C3 floor. The impossibility applies to its own
   measurement apparatus. This is why the synthetic G-blind result CANNOT be ported to a real-data
   claim about protected groups without inheriting the proxy's own non-identifiability. Declare as a
   loss; severity nontrivial.

## RESIDUAL CIRCULARITY IN THE MARGIN CONTROL — FIXED (and a silent-no-op caught)

The first margin bins used `consensus_p` (the band's own mean prediction), which is mechanically
linked to flip-rate (consensus≈0.5 ⟺ high flip): mid-bins saturated at P(flip)=1.000 for both
groups — informative-looking but circular. Fixed by using a BAND-INDEPENDENT margin: the best
member's `predict_proba` on the holdout (a single reference model's graded score).

**Caught a silent no-op in the process** (logged for the discipline): my first `_independent_margin`
looked for `best_member.feature_subset`, which does not exist — the subset lives on
`best_member.spec.feature_subset`. The helper silently fell back to `consensus_p` and produced
BYTE-IDENTICAL bin counts to the consensus run. I noticed only because the counts were suspiciously
identical. Changed the fallback to a hard `raise` so it can never silently no-op again, fixed the
attribute path, re-ran.

**With the genuine independent margin** (`runs/shuffle_set_indep_margin.json`): the bins redistribute
into a smooth flip-rate curve (no saturated mid-bins), and **pooled_g_diff stays ≈0: D1 +0.015,
D2 +0.002, D3 −0.009, D4 −0.005.** Per-bin diffs are small and sign-flip with no consistent
direction. The refutation is now referee-grade ON THE SYNTHETIC SUBSTRATE: at equal creditworthiness
(independent margin), the protected group is shuffled no more than anyone else. (Real-data claim
still blocked by Fable point 4 — the C3 reflexive loss.)

## Live successors (this is a refutation WITH successors, NOT a stall)

1. **The arbitrariness reframe** (strongest): quantify the marginal-applicant coin-flip as the
   audited quantity — P(flip) and its ε-curve as a due-process metric independent of protected
   status. Connects to [[project_pick_one_hides_choice]] and survives the regime change.
2. **Independent-margin re-test** (owed correctness): wire p_ref as the margin axis, confirm g_diff≈0
   is not an artifact of the consensus-bin circularity.
3. **ε-curve** (owed, Fable 2): shuffle-set size and g_diff as functions of ε.

## Meta

Engagement first-read now 0-for-6 (added: shuffle-set-is-protected). Procedure 6-for-6: Fable's
margin control turned a would-be-shipped mechanical artifact into a clean, counterintuitive, regime-
robust refutation. The blind-adversary-before-the-sentence discipline, applied by an actual external
adversary this time, did exactly its job.
