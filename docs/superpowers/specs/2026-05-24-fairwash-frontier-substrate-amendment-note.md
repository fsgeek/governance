# Substrate amendment to the fairwash-reorganization frontier pre-reg

**Status:** DRAFT — for review, NOT yet applied or stamped. On approval this is applied
to the frozen pre-reg (`docs/superpowers/specs/2026-05-23-fairwash-reorganization-frontier-preregistration-note.md`)
+ the binding DGP generator (`scripts/fairwash_frontier_dgp.py`), committed and re-stamped
as ONE amendment commit. The original `daf032d` / OTS `9e8abe7` remains the immutable record.
**Date:** 2026-05-24. **Author:** Claude Opus 4.7 (ghola), governance lineage.

## Why this is an amendment, not a coherence correction

The 2026-05-23 freeze left the *synthetic* substrate under-specified in two places and
specified the control criterion in a third place in a way verification has now shown is
incoherent. These are **substantive** (they complete the operational meaning of P3a and
P5), so they get a transparent re-stamp — not the silent connective-tissue treatment the
rung-label corrections got.

**Predictions are NOT changed.** P3a (MISS @0.85), P3b (break-rung=D4 @0.60), P4 (@0.65),
P5 (@0.55) — priors, directions, and killing-conditions are untouched. This completes the
substrate definitions those predictions presuppose, and is verified (below) to restore the
conditions under which they are testable as intended.

## Item 1 — `declared_proxies` as an explicit substrate parameter (reviewer Q1)

§2f froze `prohibited = cand_ext_A − cand_ext_B`, an *FM-substrate* formula with no synthetic
realization. Add to §2c, freeze the members in §2h:

- `declared_proxies ⊂ X`, **fixed at substrate-spec time, NOT derived from DGP wiring on any
  channel**, small (2 of |X|=8), disjoint from `V_named` and from `c_fresh`.
- **Frozen (§2h): `declared_proxies = {x6, x7}`** (low-coefficient legit features).
- **`prohibited = {G} ∪ declared_proxies`**, frozen across all channels. (`G` is protected →
  never in the audit band pool, so in-pool stripping acts on `{x6, x7}`.)
- `V_named = {x0..x5}`; `V_ext = c_fresh`; audit band pool = all observable features
  (`x0..x7 ∪ c_fresh`); `declared_proxies` are in-pool (strippable), as geography was in #12.

**Channel/declared-proxy overlap — stated, not left to a reader (reviewer's three cases):**
the substrate guarantees each channel's *effective laundering carrier in T(M)* (the c_fresh
portfolio) lies **outside** `declared_proxies`, i.e. case 3 (fresh-carrier) — the only case
that makes the P3a-MISS test meaningful. Case 1 (DGP wires G through a declared_proxy) is the
trivial detectable case and is explicitly **not** the default. D1's "carrier" is G itself
(protected, never in pool) → rung 3a is vacuous on D1, which is expected.

**The prior bug this fixes (why verify-then-freeze mattered):** the harness had
`prohibited = the DGP wiring`, collapsing every channel to case 1, where 3a trivially catches
— which would have *falsely falsified* P3a. With the fixed set, the 2026-05-24 smoke shows 3a
flips to MISS on the fresh carrier (J→1.0), the predicted behavior.

## Item 2 — C_oracle / C_null clean by construction (reviewer Q2, mechanism)

§2g asserts C_oracle/C_null are clean but the DGP exposes no clean target to realize it. Add:

- The DGP exposes a **clean target** `Y_clean ~ Bernoulli(σ(legit_logit))`, `legit_logit = X·β`
  using only `legitimate_coefficients` — the disparate term zeroed.
- **C_oracle** trains on `Y_clean` over `V_named`; **C_null** trains on `Y_clean` over all
  features. Both are **construction-required to qualify on every channel** (the §2g floor of 2).
  If either fails to qualify, the substrate spec has a bug and that channel is excluded pending
  fix. **C_drop / C_resid MAY fail to qualify on proxy-heavy channels (D2/D3)** — expected, not
  a bug; those channels are simply harder to remediate.

## Item 3 — control qualification re-specified off demographic parity (verification finding)

§2g currently: "each control's realized Δ ≈ 0 to qualify." **Verification (2026-05-24) shows
this is incoherent in exactly the regime the experiment lives in.** Because G is generated from
`x0` (the dominant legitimate risk factor), a model using *only* legitimate risk **correctly**
shows a nonzero — and on D2 sign-*reversed* (Δ ≈ −0.15 vs M's +0.22) — demographic-parity gap.
Requiring Δ≈0 would disqualify C_oracle, the cleanest possible control, and would amount to
imposing demographic parity (over-correcting away legitimate risk). This is the direct
consequence of the legitimate-feature/G entanglement that makes proxies exist at all.

**Corrected criterion:**
- A control **qualifies** iff it does **not launder** — its realized c_fresh importance is below
  a frozen threshold `τ_launder` (no reliance on the admissible carriers beyond a null level).
  Demographic parity is **not** a qualification axis.
- **C_oracle defines the legitimate baseline Δ_oracle.** "Discrimination" is the *excess*,
  `Δ(M) − Δ_oracle`, not the raw `Δ(M)`. The retention fraction `r` and the `Δ(M) ≥ 0.10`
  validity floor are re-expressed against this baseline.
- **P5 (calibration) is computed on c_fresh excess-importance vs the control null, not on Δ.**
  This is what 3b actually rests on; the Δ framing was a category error.
- **§2h new scalar:** `τ_launder` (control-qualification c_fresh-importance ceiling). Declared
  here and **swept** as sensitivity (per the [[project_knob_robustness_result]] declare-and-sweep
  discipline), not silently pinned.

## Implementation requirements (fold into the amendment commit)

1. `scripts/fairwash_frontier_dgp.py` regenerated: explicit feature roles (`V_named`,
   `declared_proxies`, `c_fresh`), clean-target export, per-channel guarantee that the carrier ∉
   `declared_proxies`. (Regenerating a frozen binding-spec artifact → part of the re-stamp, not a
   silent forward-edit.)
2. `scripts/fairwash_frontier_test.py`: align to the frozen `declared_proxies`; controls already
   clean-by-construction (provisional) — finalize; **fix C_resid's train/test residualization
   bug** (residualize the audit/test features with train-derived coefficients before predicting).
3. Unit tests already encode the corrected control criterion (no-launder, oracle baseline).

## V2 amendment (rev-6, 2026-05-24): latent-`G` twin-world substrate

The V2 compliant-practice pre-reg (`2026-05-24-compliant-practice-disparate-impact-V2-preregistration-note.md`)
promotes the proxy-strength sweep from the optional "Open" item below to **core**, and adds the
`G`-latent twin-world. Implemented in `scripts/fairwash_frontier_dgp.py` as `generate_twin_world(...)`
(additive — the V1 `generate()` channels D1–D4 are untouched):

- **Dose knob `proxy_strength`:** scalar coupling `a` over the 3-family `c_fresh` portfolio,
  bisection-calibrated so `AUC(G ~ portfolio) ≈ target` (`_coupling_for_proxy_strength`). Grid
  `{0.50…0.85}`; `0.50` = null (a=0).
- **World A (proxy):** `c_fresh ← G → Y`; `Y ~ Bernoulli(σ(legit_logit + 2.5·G_z))`. `G` latent.
- **World B (legitimate):** `c_fresh → Y`; `Y ~ Bernoulli(p_obs(x0..x7, c_fresh))`, where `p_obs`
  is a GBT regression of World A's `Y` on observables. **This is the matched-joint trick:** the
  observable joint `P(x0..x7, c_fresh, Y)` is identical to World A by construction, so a without-`G`
  discriminator cannot separate the worlds, while they differ in the latent causal status of `c_fresh`.
- **`Y_clean`** (`σ(legit_logit)`, no disparate term) and **world labels** exported; `G` emitted for
  the experimenter only (disparate-impact, `proxy_strength`).
- **`Ĝ_BISG`:** continuous regulator estimate = latent `G`-signal + noise bisection-calibrated to
  `AUC(Ĝ_BISG ~ G) ≈ 0.85` (swept {0.75/0.85/0.95}); **never uses `c_fresh`** (`_bisg_estimate`).

**Verify-then-freeze smoke PASSED** (`wedge/tests/test_compliant_practice_dgp.py`, 5/5):
proxy_strength knob hits grid targets; without-`G` discriminator at chance on **8 of 8** grid points
(0.497–0.501); oracle separates via the conditional-dependence contrast (`G`-lift positive in A, ≈0
in B); `Ĝ_BISG` AUC ≈ 0.85; `Y_clean` cleaner than `Y`. The matched-joint calibration is near-analytic
(World B drawn from World A's observable regression), so it holds across the full grid — the
P-C3-floor 0.70 prior is conservative.

## Open (carry to the result note, not this freeze)

- Naive-laundering retention is channel-dependent (works D2; sign-pathological D1/D3/D4 at small
  n) — a V1-transform item, characterized in the result note, not a substrate freeze (V2 retires
  the transform path entirely).
- ~~Proxy-strength sweep~~ — DONE, promoted to core in the V2 amendment above.
