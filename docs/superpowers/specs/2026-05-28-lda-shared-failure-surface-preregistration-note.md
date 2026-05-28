# The LDA / fairwash shared-failure-surface — pre-registration

**Date:** 2026-05-28. **Status:** PRE-REGISTRATION. **Substrate:** `scripts/fairwash_frontier_dgp.py::generate_twin_world` (the V2 latent-G twin-world; World A = proxy-real, World B = legitimate, sharing the observable joint `P(x0..x7, c_fresh, Y)`; emits `Y_clean`, `G`, `Ghat_bisg`). **Companion to:** the regime-claim spine working note (`working_notes/2026-05-26-impossibility-regime-claim-spine.md` §5). **Connects:** [[c4-gamma-sweep-gap-result]] (lever-invariant accuracy-tax), [[project_v1_v2_explicit_transform_result]] (provenance-not-magnitude), [[project_impossibility_alternative_strategy]].

**What this tests, in one line.** Spine §5 asserts a *shared failure surface*: the legally-sanctioned LDA remedy (select the minimum-measured-impact model) and the fairwash attack share a blind spot — impact-minimization by *suppressing legitimate G-correlated signal* (laundering) is observationally identical to impact-minimization by *removing a proxy* (honest correction), and "the metric cannot tell them apart." This was minted in conversation with **no compute**. This pre-reg subjects it to falsification on the one substrate where we hold the stipulated oracle (`Y_clean`).

**Why this is the ungameable form (the trap I am avoiding, named).** The *rigged* version asks "can the oracle `Y_clean` separate laundering from honest correction?" — trivially yes, because I stipulated `Y_clean`; a §5 author kills it on contact with spine §3 ("G-observation escapes measurement, not certification; the separation requires the counterfactual you only have because you wrote it"). So the **only** admissible discriminators here are computable from the **auditor-observable set** `O = {x0..x7, c_fresh, Y, Ghat_bisg}` — **never** `Y_clean` or `G`. `Y_clean` and `G` are used ONLY to (a) *construct* the laundering/honest interventions and (b) *grade* whether a discriminator that fired was right. They are never inputs to a discriminator. **The losing condition for §5 and the losing condition for me are wired to opposite outcomes** (see §3): if an O-only discriminator separates H from L, §5 is overclaimed (I "win" the slaughter); if no O-only discriminator separates them while a `Y_clean`-discriminator does, §5 *survives with teeth* (I "lose" my skeptic bet, the impossibility sharpens). Either way the data, not my role, decides.

**Pre-registration discipline.** Inspected: the DGP source (channel wiring, `_LEGIT_BETA`, the World-A/B label construction, that `Y_clean ~ sigmoid(legit_logit)` with the disparate term zeroed). NOT inspected: any fitted-model DP-gap or accuracy on this substrate at any proxy_strength; the joint distribution of `(DP-gap, accuracy)` across the H/L interventions. No scoring code has touched data. OTS stamp on the freeze commit makes the predictions below immutable.

---

## 1. Question

On the twin-world (World A, proxy-real), construct two interventions on a baseline compliant model that **each reduce the measured demographic-parity gap by a matched amount** `τ`:

- **H (honest correction):** reduce the gap by attenuating reliance on the **proxy channel** — the c_fresh carriers (+ declared proxies x6,x7) that carry G-signal not load-bearing for `Y_clean`.
- **L (laundering-by-suppression):** reduce the gap by the *same* `τ` by suppressing a **legitimate** feature — `x0` (highest legit β=0.90, also the feature G is entangled with, corr≈0.25) — i.e. throwing away real `Y_clean`-predictive signal to buy a lower measured gap.

**If YES** an auditor-observable discriminator (O-only) separates H from L at matched `τ` → §5 is **overclaimed**: LDA's *thin* metric (gap alone) is blind, but a *thicker* observable metric (gap + held-out accuracy on Y + where the accuracy lands) partially restores the distinction. The spine §5 claim demotes from "shared failure surface, impossibility bites the remedy" to "the standard LDA metric is too thin — here is a thicker one." Weaker, more defensible, testable.

**If NO** O-only discriminator separates them, while the `Y_clean`-discriminator does → §5 **survives and sharpens**: the distinction between honest correction and laundering is real but lives entirely in the counterfactual `Y_clean` the auditor cannot observe. The LDA remedy's blindness is then *fundamental* (C3), not a thin-metric artifact. This is the stronger paper result.

## 2. Operational definitions

- **2a. Baseline model `M0`.** `GradientBoostingClassifier(**GBT_KW)` on `ADMISSIBLE = V_NAMED + CFRESH` (x0..x5 + c_fresh), target `Y`. The compliant practice article. Fit on train half; all metrics on held-out test half (the existing `fit_predict_family` split discipline; pair-index safe — twin frames not relevant here, single-world).
- **2b. Measured gap.** `Δ(M) = P(decision=1 | G=0) − P(decision=1 | G=1)` on held-out test, decision = `proba ≥ 0.5`. (Existing `_dp_gap`.) **G is used here only to compute the metric the auditor is *given* by HMDA/BISG — this is the measurement the spine §3 grants is observable. It is not a certification input.**
- **2c. The two interventions, matched on `τ`.** Target gap reduction `τ ∈ {0.25, 0.50, 0.75} × Δ(M0)` (three matched levels; primary = 0.50).
  - **H (proxy-attenuation):** down-weight the c_fresh + x6,x7 channel. Operationalized as a scalar `λ_H ∈ [0,1]` multiplying those features' values (→0 removes the proxy channel). Bisect `λ_H` so `Δ(M0 with proxy channel scaled by λ_H) = (1−τ)·Δ(M0)`.
  - **L (legit-suppression):** down-weight `x0`. Scalar `λ_L ∈ [0,1]` multiplying x0. Bisect `λ_L` so the **same** target gap `(1−τ)·Δ(M0)` is reached by suppressing the legitimate feature instead.
  - Both refit the GBT on the transformed train features; both reach the *same measured gap* by construction (the matching). If a target `τ` is infeasible for an arm (gap floor reached before τ), that cell is reported infeasible, not forced.
- **2d. The auditor-observable set `O`.** `{x0..x7, c_fresh, Y, Ghat_bisg}`. Every discriminator in §3 takes inputs **only** from `O` (and the fitted model's held-out predictions, which are functions of O-inputs). **Forbidden as discriminator inputs:** `Y_clean`, `G`. (Grading uses them; discriminating does not.)
- **2e. Discriminators (the candidate "thicker metrics").** Computed for H and L at matched `τ`:
  - **A_obs — held-out accuracy on `Y`** (observable). `accuracy(decision, Y_test)`. Hypothesis: L drops it more than H.
  - **A_obs_grouped — accuracy drop localized in G-strata** (observable; uses G only as the granted measurement stratifier, same standing as Δ). Where does the accuracy cost land?
  - **CAL — held-out calibration / log-loss on `Y`** (observable). A laundering move that distorts probability structure may show worse calibration than an honest one.
  - **A_clean — held-out accuracy on `Y_clean`** (ORACLE; **grading-only, reported as the contrast**). This is the discriminator §5 implicitly relies on. By construction L should drop A_clean (real signal thrown away) and H should not (only illegitimate signal removed). This row is the *upper bound* on separability — what you could do *if* you had the oracle.
- **2f. Separation metric.** For each discriminator d and matched τ: paired (over seeds) `d(H) − d(L)`, with 95% bootstrap CI (existing `_paired_ci`). "Separates" = CI excludes 0 **and** |effect| ≥ 0.01 (1 accuracy point / 0.01 nats). Pre-committed: A_clean is *expected* to separate (sanity that the construction works); the live question is whether A_obs / CAL separate.
- **2g. Seeds / grid.** 20 seeds (existing default), proxy_strength = 0.85 (the anchor used by [[c4-gamma-sweep-gap-result]]; one secondary point ps=0.70 reported as robustness, not gating). n=8000.

## 3. Pre-registered predictions

**P1 — A_clean separates H from L (construction sanity).** `A_clean(H) − A_clean(L) > 0`, CI-excluding, at τ=0.50. **Prior: 0.90.** This is the oracle discriminator; it MUST work or the H/L construction is broken (not a finding about §5, a finding about my code). MISS → construction bug; halt and fix, do not interpret.

**P2 — A_obs FAILS to separate H from L (the §5-survives prediction).** `|A_obs(H) − A_obs(L)|` CI **includes 0**, or |effect| < 0.01, at τ=0.50. **Prior: 0.62.** *This is the prediction I expect to win on and the one that, if it MISSES, slaughters §5.* Rationale: in World A the suppressed legit feature x0 is genuinely predictive of the *realized discriminatory* `Y` (G drives Y), so suppressing it costs observable accuracy — but removing the proxy channel *also* costs observable accuracy in World A (the proxy predicts the discriminatory Y too). Both arms pay an observable-accuracy tax; they look alike on `Y`. **Load-bearing for §5 survival.**
  - **MISS interpretation (A_obs DOES separate):** §5 is overclaimed. The thicker metric (gap + held-out accuracy) restores the H/L distinction *without the oracle*. The spine §5 must be rewritten as "standard LDA metric too thin," and §1's "shared failure surface" framing weakened. **This is the clean slaughter; if P2 misses, I was right to distrust the conversation-minted frame, and I say so.**

**P3 — directional: L's observable-accuracy tax ≥ H's (sign), even if not CI-separable.** `A_obs(H) − A_obs(L) ≥ 0` in sign (mean over seeds), at τ=0.50. **Prior: 0.70.** Weaker than P2: even if they're not *statistically* separable (P2 hits), the *direction* should favor L-costs-more (laundering throws away the higher-β feature). If the sign is *wrong* (H costs more than L), my whole mechanistic story is inverted and both P2 and the §5-sharpening need rethinking.
  - **MISS interpretation (sign flips):** removing the proxy channel costs *more* observable accuracy than suppressing x0 — meaning in World A the proxy carries more realized-Y signal than the top legit feature. Plausible at high proxy_strength; would itself be a finding (the proxy is the dominant predictor of the discriminatory outcome), and reframes which intervention is "honest."

**P4 — the separability gap is monotone in `τ`.** `[A_clean(H)−A_clean(L)]` (the oracle separation) increases with τ; `[A_obs(H)−A_obs(L)]` stays ~flat near 0 across τ. **Prior: 0.55.** Dose-response on the *separability itself*: the more gap you buy, the more the oracle can tell H from L, while observables stay blind. If this holds it is the cleanest single figure of the impossibility (separability lives in `Y_clean`, scales with intervention magnitude, invisible to O). Bet the shape, not a point ([[project_pre_registration_pattern]]).
  - **MISS:** if A_obs separation *also* grows with τ, P2's blindness is τ-local (only small interventions hide) — a weaker but still real qualifier on §5.

**P5 — CAL (calibration/log-loss on observable Y) does not rescue separation.** `|logloss(H) − logloss(L)|` on `Y_test` CI-includes 0 at τ=0.50, OR if it separates, it separates in the *same* direction and magnitude order as A_obs (i.e. adds nothing beyond accuracy). **Prior: 0.60.** Guards against "well, a *cleverer* observable metric would work" — calibration is the most likely next-thing-an-auditor-tries. If CAL separates when A_obs doesn't, the thicker-metric escape is alive via a channel I didn't expect, and §5 weakens.

**Most likely overall miss.** P2 hits (observables blind) but at ps=0.85 the proxy is so dominant that P3's sign is marginal — the "honest vs laundering" labels get muddy because at high proxy_strength removing the proxy *is* removing most of the realized-Y signal, so "honest correction" itself looks like signal-suppression. That muddiness would be a finding: at high proxy_strength the H/L distinction degrades for a *substantive* reason (the proxy became load-bearing for the discriminatory outcome), not a metric-thinness reason — orthogonal to §5's claim and worth separating from it.

## 4. Sensitivity / robustness pre-specs (reported, not gating)

- proxy_strength ∈ {0.70, 0.85} — does observable-blindness depend on proxy dominance?
- τ ∈ {0.25, 0.50, 0.75} — the P4 dose curve.
- Suppression target for L: primary x0 (top β); sensitivity x2 (mid β, β=0.80, an anchor of collinear pair 2). If the result hinges on *which* legit feature is suppressed, that's a scope limit on §5, reported.
- Decision threshold 0.5 primary; the gap/accuracy at a fixed-acceptance-rate threshold reported as a sensitivity (DP-gap is threshold-sensitive).

## 5. Scope / exclusions ("what this is NOT testing")

- **NOT** testing whether the oracle separates H from L (trivially yes — that's the rigging I am refusing; it is reported only as the A_clean upper-bound contrast, P1).
- **NOT** testing the *legal* viability of impact-driven model selection (spine §5 NEEDS-GROUNDING / Joe's domain; post-*SFFA* pressure). This tests only the *technical* separability claim.
- **NOT** testing search-incompleteness (spine §5(a), Desktop's inductive-unprovability adversary). That blade is formal, not empirical; out of scope. This tests only §5(b), the metric-vs-mechanism (C3) blade.
- **NOT** an LDA *search* over a model ensemble — it tests the *metric's* discriminating power on two hand-constructed members (H, L) at matched impact. Whether a real ensemble search lands on L vs H is a separate question (the Rashomon-set-as-LDA-space §6 arc); flagged as the natural follow-on, not gated here.
- **NOT** claiming substrate-generality — synthetic twin-world only. Real-data analogue (no oracle) is exactly what HMDA-C1 cannot test (no `Y_clean`), which is itself the point.

## 6. Implementation

New script `scripts/lda_shared_surface_test.py` reusing `fairwash_frontier_dgp.generate_twin_world`, the `GBT_KW` / `_dp_gap` / `_paired_ci` primitives from `compliant_practice_test.py` (import, do not duplicate). One JSON to `runs/`, one result note. The H/L matching is a 1-D bisection on a feature-scaling λ (cheap; ~refits per bisection step × seeds × τ × ps ≈ a few thousand GBT fits, minutes). Unit test: H and L reach the *same* measured gap within tolerance at each τ (the matching invariant) — without it the comparison is meaningless.

## 7. Blind-adversary brief (hire BEFORE scoring — [[feedback_anti_confirmation_procedure]])

A blind adversary (fresh subagent, not shown my preferred outcome) is dispatched after the run with this charge:
1. **Audit for oracle leak.** Inspect every discriminator (A_obs, A_obs_grouped, CAL) and confirm its inputs are a strict subset of `O = {x0..x7, c_fresh, Y, Ghat_bisg}` plus model predictions. Flag any path where `Y_clean` or `G` enters a *discriminating* (not grading, not metric-stratifying) computation. **If A_obs separation is real but secretly oracle-fed, the slaughter is fake and must be retracted.**
2. **Audit the matching.** Confirm H and L actually reach the same measured gap (P1 sanity is about A_clean; this is about Δ). If they don't, the "matched τ" comparison is confounded by gap-magnitude and any separation is an artifact.
3. **Attack the H/L labels.** Is "suppress x0" really *laundering* and "attenuate c_fresh" really *honest*? At ps=0.85 the adversary should specifically test the "Most likely overall miss" — whether the proxy has become load-bearing for the realized Y, muddying the labels.
4. **Steelman the §5 author.** Given the result, what is the strongest one-line rebuttal a §5 defender makes? (The spine §3 "you only separated them with the oracle" move is the one to pre-empt; the brief checks I have not walked into it.)

The adversary's verdict is recorded in the result note *before* I write the headline.

---

**Pre-reg author:** Claude Opus 4.8 (researcher), governance lineage. **Date:** 2026-05-28. **OTS:** auto-applied by post-commit hook on freeze.
