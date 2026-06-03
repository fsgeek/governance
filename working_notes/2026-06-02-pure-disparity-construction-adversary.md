# Pure-disparity construction — blind-adversary record (2026-06-02)

**What this is.** The blind-adversary pass against the PD construction, dispatched BEFORE any
headline was written (per [[feedback_adversary_before_the_sentence]]). The adversary was blind to
the researcher's priors and to the researcher's preliminary "arm-strength asymmetry" reading of
the negative control; charged to BREAK the construction. It did.

## Verdict by attack

- **Attack 1 (validity gate fooled?) — PARTIALLY.** The within-G-stratum *AUC* gate is flat for
  PD_baserate (poolΔ ≤ 0.004), but every apparatus discriminator is *accuracy*/*calibration*, not
  AUC. PD_baserate at gap=0.20 shifts G=1 stratified accuracy ~0.03–0.05 and CAL +0.022 (a
  pooled-train miscalibration under a threshold-only shift). The gate certifies "no rank-AUC
  signal," NOT "no signal the apparatus exploits." Not fatal alone (that calibration shift is
  arguably the legitimate disparity signal), but the gate is narrower than advertised.

- **Attack 2 (PD_baserate truly pure?) — SURVIVES.** within-G AUC poolΔ ≤ 0.004 over seeds 0–4;
  the x0–G correlation does not manufacture within-stratum rank structure. PD_baserate is a genuine
  pure base-rate shift by the AUC criterion. PD_noise is correctly REJECTED (poolΔ ≈ 0.026–0.031,
  G=1 AUC drops ~0.06, G=1 CAL ~0.60). Bisection accurate + seed-stable (excess gap within mean
  0.006, sd 0.008 of target).

- **Attack 3 (arm contrast measures disparity or construction?) — BROKEN. FATAL.** On the CLEAN
  world (target_gap=0, ZERO disparity), is_L separates on EVERY discriminator and EVERY info-set:
  A_obs k-ctl=−0.018, CAL +0.024, A_obs_g0=−0.018, A_obs_g1=−0.019, A_clean=−0.018 → bare, trueG,
  bisg, oracle ALL True. **Cause:** H drops c_fresh (≈no clean Y-signal); L drops the highest-β
  legit features (x0 β=0.90, …) which gut accuracy. Clean-world mean A_obs: H=0.759 vs L=0.688 —
  a **7-point accuracy gap from arm construction alone, zero planted disparity.** The OLS controls
  for abs_gap and k; the confound is neither — it is feature predictive-*strength*. Artifact
  magnitude (~0.018–0.024 is_L units) is the same order as / at gap=0.20 larger than any planted
  signal.

- **Attack 4 (k-control removes the confound?) — NO.** On the clean world naive and k-ctl AGREE in
  sign on all five discriminators (hard-stop never fires) and BOTH report separation. The hard-stop
  guards feature-*count*; the live confound is feature-*strength*. Sign-agreement here is evidence
  the artifact is STABLE, not absent — false reassurance.

- **Attack 5 (does the answer follow?) — NO.** Y_clean/Ghat_bisg/x0 identical across worlds at
  fixed seed (the cross-world stream worry is benign — confirmed). But because the negative control
  separates on all info-sets, there is no "off" state for G-access to switch ON from — the headline
  question ("what does G-access buy") is unanswerable from this apparatus as built.

## Bottom line

Fatally undermined by the arm-construction artifact (Attack 3): the H-vs-L contrast confounds
"honest vs laundering" with "dropped low-value vs high-value features," producing a ~7-point clean-
world accuracy gap that trips the pre-reg's explicit negative-control abort condition (NEG_clean
separates on bare/trueG/bisg/oracle alike). Covariate adjustment cannot remove it (confound is β-
strength, not gap or count). The artifact swamps any plausible disparity signal.

**What still holds honestly:** (1) PD_baserate is a genuine pure base-rate disparity under within-G
AUC (poolΔ<0.004); (2) PD_noise leaks and is correctly gate-rejected (poolΔ≈0.03 — a real
distinction between the two pure-disparity mechanisms: conditioning on G alone is observationally
pure, conditioning on the realized label leaks); (3) the magnitude-control bisection is accurate.

**The fix (for the next freeze):** match the H and L arms on predictive content — e.g. L drops
features of β comparable to what H drops, or match arms on clean-world A_obs — so the negative
control shows no separation. Only then are P1–P4 interpretable. The frozen predictions stand
unscored; this is a negative-control failure, not a scored MISS.

## Researcher's note (own failure, recorded wrong-and-all)

I saw the negative-control separation (−0.02), correctly guessed the mechanism (arm asymmetry),
and then FAILED to draw the consequence — that it invalidates P1–P4 — instead reframing it as "a
clean finding about the apparatus's limits" and proceeding to run the grid as frozen. The adversary
drew the consequence I rode past. Same shape as the lineage scar ([[feedback_adversary_before_the_sentence]]):
the satisfying frame formed and concealed the flaw it was built on. The procedure (blind adversary
before the headline) caught it; my care did not. Logged as the Nth instance; the procedure earns
its cost again.
