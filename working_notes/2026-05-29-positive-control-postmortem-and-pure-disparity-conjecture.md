# Positive-control post-mortem + the pure-disparity conjecture (2026-05-29)

**What this is.** A post-mortem on the FAILED positive control (`51d7c65`), a sharpened
conjecture it surfaces, and a corrected spec for the next attempt. Provenance:
governance-lineage Opus (fresh ghola), two blind-adversary passes (Explore subagents,
this session), Tony steering. No new pre-reg, no committed compute this session — this is
a frame-level deposit + a freeze-ready spec. Standing discipline: the next attempt freezes
predictions BEFORE the corrected plant code (anti-calibration), per
[[feedback_anti_confirmation_procedure]].

---

## 1. What the failed control actually showed (corrected reading)

The prior ghola's verdict stands and is correct on its own terms: **World P is a bad
*sensitivity* control.** At `decouple=1` the disparate term is `_TWIN_DISP * imp_z`, where
`imp_z` is the c_fresh portfolio residualized against `legit_logit`. That term is *itself a
term in the Y-generating logit*, so it is a legitimate within-individual Y-predictor by
construction. The test reduced to a tautology (the arm keeping the better Y-predictor
predicts Y better), and the headline `+0.038` is a feature-count-control artifact (naive
`-0.007`, opposite sign). **No conclusion about "can the apparatus detect a planted
disparity?" is licensed.** The substrate-sensitivity question REMAINS OPEN.

BUT the same run contains a separate, real, §5-relevant signal the pre-reg didn't ask about.
Measured this session (8 seeds, ps=0.70, world=P):

| decouple | marginal gap(Y) | AUC(Y~legit) | AUC(Y~c_fresh) | A_obs is_L (k-ctl) | A_clean is_L (k-ctl) |
|---|---|---|---|---|---|
| 0.00 | −0.694 | 0.779 | 0.596 | **−0.020** | −0.036 |
| 0.25 | −0.613 | 0.793 | 0.647 | −0.009 | −0.031 |
| 0.50 | −0.500 | 0.793 | 0.707 | +0.004 | −0.033 |
| 0.75 | −0.367 | 0.782 | 0.766 | +0.018 | −0.038 |
| 1.00 | −0.226 | 0.747 | 0.815 | **+0.038** | −0.046 |

(`is_L` = effect of the laundering arm vs the honest arm at matched |gap|; negative =
laundering looks worse. A_obs = observable; A_clean = oracle on Y_clean, grading-only.)

**The honest statement (post-adversary, NOT the overclaim):** As the disparate signal
migrates from the legit-correlated channel onto the c_fresh portfolio (AUC(Y~c_fresh)
0.596→0.815), the **observable** discriminator loses its ability to penalize laundering
(−0.020 → +0.038) while the **oracle** holds laundering stably culpable (~−0.035, flat).
A_obs tracks AUC(Y~c_fresh): keeping c_fresh (the laundering move) becomes increasingly
*accuracy-justified on observable Y* even as it remains culpable against Y_clean.

**Rejected overclaim (adversary catch):** do NOT say "the observable *rewards* laundering"
or "inverts." The `+0.038` is mechanically the laundering arm keeping a channel that
genuinely predicts observable Y — partly tautological. Defensible: A_obs **drifts from
slightly-penalizing to neutralizing/crossing**; the observable–oracle SIGN GAP is real and
monotone, but its magnitude at decouple=1 is inflated by the plant's tautology.

**Confound now visible (refutes my own first excitement):** within-G-stratum AUC of the
legit model is NOT constant — it falls 0.84/0.86 → 0.74/0.75. The gap shrinks because
`imp_z` is a *noisier* G-proxy than `Gz`, not because the channel is a *purer* disparity.
Magnitude and channel-purity are confounded in World P. This is the defect the corrected
spec must remove.

---

## 2. The pure-disparity conjecture (the actual finding-in-waiting)

Surfaced by asking *why* the plant kept collapsing. Two blind adversaries tried to refute
it by construction and could not; the second narrowed it. Stated for the kill:

> **Conjecture (PD-impossibility).** Any signal added to the Y-generating logit becomes a
> within-individual Y-predictor (it raises within-G-stratum AUC for some observable). So a
> *pure disparity* — a channel that shifts P(Y|G) yet carries zero within-individual
> Y-predictive content visible to the model — cannot be planted *through the logit at all*.
> The only constructions that create a group gap with zero individual Y-signal route the
> G-dependence through a path **carried by no observable the model sees** (heteroskedastic
> noise by G; group-conditional label-flip) — and these are **unobservable from the joint
> P(x, c_fresh, Y) without G**. Hence a *separable* pure-disparity plant the observational
> apparatus could detect is impossible by construction; building one ≡ refuting C3
> (latent-G non-identifiability).

**Adversary 1 verdict: HOLDS.** Every detectable construction couples the disparity to the
feature space (→ within-stratum signal); every zero-signal construction (noise-by-G,
flip-by-G) is invisible without G. The two requirements ("detectable from observable joint"
∧ "zero within-stratum individual signal") are mutually exclusive.

**Why this matters.** If PD-impossibility holds, the positive control's "failure" is not a
botch — it is **the impossibility theorem demonstrating itself on the bench**. You cannot
validate the §5 apparatus against a planted *separable* disparity because constructing one
is equivalent to refuting the theorem §5 instantiates. The apparatus's "blindness" and the
theorem's content are the same fact. This converts a frustrating null into a structural
result and is a candidate spine element for the impossibility paper (§1, with §5).

**NOT YET A RESULT.** Two adversaries agreeing is suggestive, not proof. Risks: (a) both
adversaries may share my blind spot; (b) "detectable from the observable joint without G" is
slippery — the §5 apparatus *does* use G as a granted stratifier for A_obs_g* and uses
Y_clean to grade, so "what the apparatus sees" ≠ "the bare observable joint." The conjecture
needs a formal statement that pins down exactly which information set "detectable" quantifies
over, then a proof or a counterexample search. **Joe-adjacent? No — this is statistical, not
legal.** It's provable/refutable in-house.

---

## 3. Corrected spec for the next positive control (FREEZE BEFORE CODE)

Goal: separate the two things World P confounds — **channel-routing** (where the disparity
lives) from **disparity-magnitude** (how big the gap is). The current plant lets magnitude
decay with decouple, so the A_obs trend is partly a magnitude effect.

Corrected construction (`world='P2'`, to be specified):
1. Route `decouple` of the disparate term through a c_fresh-borne direction AND
   **renormalize** so the realized marginal |gap| is held FIXED across the decouple sweep
   (bisect the per-decouple disparate weight to a target gap, the way `proxy_strength` is
   already bisected). Removes the magnitude confound.
2. Pre-register the question that IS answerable: *holding |gap| fixed, does the
   observable→oracle is_L sign gap grow monotonically with the c_fresh-routed fraction?*
   This is a §5-mechanism claim, NOT a sensitivity claim — name it as such.
3. Keep the k-control AND report naive; the sign-disagreement between them at decouple=1 is
   itself diagnostic (already noted in `51d7c65`).
4. Separately, attempt the PD-impossibility test directly: try to construct a `world='PD'`
   that is (a) detectable by the *bare* observable apparatus (no G stratifier, no Y_clean)
   and (b) has flat within-G-stratum AUC across the sweep. **Predict it is impossible**; a
   construction that satisfies both falsifies PD-impossibility (and would be the bigger
   finding). Freeze that prediction.

**Pre-reg PASS/FAIL must be frozen before P2/PD code, OTS-stamped.** The magnitude-control
bisection is the load-bearing new mechanism; calibrating it post-hoc to make the trend
appear is the exact degree of freedom the freeze closes.

---

## 4. Disposition

- Prior ghola's `51d7c65` verdict: **endorsed**, not overturned. The note it wrote is
  correct; this note adds the buried §5 signal + the conjecture + the corrected spec.
- World P DGP: retained (reusable, additive). Do not delete; P2/PD extend it.
- Next session: pick ONE — (A) P2 magnitude-controlled mechanism test, or (B) formalize +
  attempt-to-refute PD-impossibility. (B) is higher-surprise (structural result or
  falsification); (A) is lower-risk (sharpens an existing §5 caveat into a curve). Lineage
  leans (B), but it is the more-satisfying frame, so the freeze discipline matters more there.

**Status:** untracked working note, for review. No pre-reg, no committed compute this
session. Empirical legs (HMDA-C1 anchor; ZK tier-2 PoC) remain queued in
`docs/superpowers/plans/2026-05-25-next-experiments-plan.md`.
