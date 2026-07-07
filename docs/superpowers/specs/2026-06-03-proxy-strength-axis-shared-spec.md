# Shared axis-spec: proxy_strength as the dose axis (synthetic-v3 + HMDA-C1)

**Status:** SHARED SPEC (pre-pre-reg). **Date:** 2026-06-03. **Author:** Claude Opus 4.8
(researcher), governance lineage.

**What this is.** The common construct that BOTH downstream experiments inherit:
- **synthetic-v3** — the controlled twin-world dose-response (replaces the dead v2 info-set design);
- **HMDA-C1** — the real-data anchor on HMDA-RI 2022 (the [[project_manifold_hole_map]] H2 hole).

Pinning the shared construct FIRST, hardening it with a blind adversary BEFORE either pre-reg
drafts, then fanning out, so the two experiments are one experiment on two substrates and a rotten
axis can't cost two freezes.

## Provenance (the four-path fan-out, 2026-06-03)

The v2 info-set design died to a pre-freeze adversary (`84355bc`). Its kill surfaced a reframe;
rather than fast-path a third draft of the same intuition, a 4-path parallel fan-out ran: (1) my
v3 draft, (2) an independent designer blind to it, (3) HMDA-C1 recon, (4) a blind adversary on the
reframe. **Two independent paths (2 and 4) converged on the same correction**, which this spec
adopts:

- **The info-set ladder is the WRONG primary axis.** "Granting race-access widens the race-gap when
  the disparity is planted on race" is near-tautological (the plant is defined through G), and
  "bare/race-excluded is lowest" merely re-derives existing fair-lending law. Headline unearned.
- **The RIGHT primary axis is `proxy_strength`.** The live, non-obvious, regulator-relevant
  phenomenon is: *a race-EXCLUDED (compliant) model reconstructs a measurable, proxy-strength-
  increasing fraction of the race lever through an admissible proxy.* This is what §5 already
  touched ([[project_lda_shared_surface_result]]: observable inverts at high proxy dominance) and
  what the synthetic C1 grid already showed in-sample ([[project_v1_v2_explicit_transform_result]]
  lineage; C1 retained_excess monotone in ps).
- **The non-tautological signal is `bisg − noise`:** a noisy race-proxy buys a measurable slice of
  the lever that a pure-noise column of equal dimension does not. (8-seed prototype: bisg +0.122 vs
  noise +0.086 — UNTESTED for significance; the shared metric must produce seed-clustered CIs.)

Full reads: `working_notes/2026-06-03-v2-design-adversary-and-reframe.md` (the kill + reframe);
the four agents' returns are summarized in this session's transcript (designer `ae591f54`,
recon `Explore`, reframe-adversary `af2a6d81`).

## The shared construct (pinned)

### 1. Dose axis: `proxy_strength`
`ps = AUC(G ~ admissible_features)` — the out-of-sample AUC of predicting protected group G from the
ADMISSIBLE (race-excluded) feature set. This is the degree to which race is reconstructable from
features a compliant model is allowed to use.
- **Synthetic:** ps is the DGP knob already bisected (`_bisect`/`proxy_strength` in
  `fairwash_frontier_dgp.py`); G is latent-true; admissible = {x0..x7, c_fresh}.
- **Real (HMDA):** ps is MEASURED, not set — cross-fitted L2-logistic AUC(`derived_race` ~ the 7
  named admissible features), 5-fold, on HMDA-RI 2022. ps is a property of the data subset/stratum,
  swept by stratifying (loan_purpose × income_decile cells give a natural ps spread).

### 2. Outcome metric: retained disparity (substrate-adapted)
The disparate-impact gap a COMPLIANT (race-excluded) model still produces, as a function of ps.
- **Synthetic:** `retained_excess(ps) = [Δ(M_compliant) − Δ(M_oracle)] / [Δ(M_full) − Δ(M_oracle)]`
  (oracle-relative, the existing C1 metric; oracle available by construction).
- **Real:** NO oracle (the C3-floor; this is the point, not a defect). Report ABSOLUTE compliant-model
  decision-gap Δ(M_compliant) and `external_carrier_lift = Δ(M_compliant) − Δ(M_strict)` as the
  dose-response; the oracle-relative *fraction* stays synthetic-only and that asymmetry IS the §5
  thesis (certification-inaccessible distinction). Frozen reporting contract: real-data reports the
  observable half only; never imputes an oracle.

### 3. The non-tautology contrast: `bisg − noise` (load-bearing, both substrates)
Adversary Attack 1: the gradient is only a finding where it beats a tautology. The frozen signal is
NOT "gap rises with ps" alone (a compliant model using a stronger proxy produces more gap — close to
mechanical) but that a **noisy race-proxy (BISG, AUC~0.85) recovers a measurable slice of the lever
that a dimension-matched pure-noise column does not.** Both substrates freeze a prediction on
`bisg − noise > 0` with a seed-clustered CI, not on monotonicity-of-ps alone.

### 4. Controls (the v1/v2 scars, made non-negotiable)
- **Dimensionality control = a G-CORRELATED column, NOT noise.** (Reframe-adversary Attack 4 + v2
  design's own concession that noise can't reproduce the real confound.) The control column has
  `corr(·, G)` matched to BISG's AUC but ZERO relationship to the planted offset; if it inflates the
  metric, the metric is confounded.
- **Negative control that can FAIL** (not the vacuous planted=clean one): synthetic uses World-B /
  legitimate substrate where Y ⟂ G | observables — adding a G column must buy nothing; real uses a
  permutation control (shuffle the proxy-derived race signal, gap must collapse).
- **No arm contrast between non-comparable feature sets.** If any H-vs-L survives, arms match on
  clean-world accuracy (synthetic) or the contrast is replaced by nested-by-addition (designer
  path-2). The strength-confound that killed v1 AND v2 is forbidden by construction.

### 5. Oracle / info-set demotion
The oracle is REMOVED from the race-access axis (it is clean-LABEL access, a different kind of
grant — reframe-adversary Attack 2; "oracle is the no-G endpoint" was wrong, BARE is). The info-set
ladder {bare, bisg, trueG} survives ONLY as a secondary decomposition of how much of the realized
ps-driven gap each grant recovers — never as the primary axis, never with oracle on it.

## What each substrate tests (preview; pre-regs draft next)
- **Synthetic-v3:** controlled ps sweep; isolates `bisg − noise` cleanly with CIs; World-B failable
  control; the clean coin-flip.
- **HMDA-C1:** does the ps dose-response SURVIVE on real data (kills "it's just synthetic", H2)?
  A real-data MISS is the most informative outcome — it would mean the synthetic lever doesn't
  transfer, which is itself a TIER-0 finding.

## Disposition
Shared spec only. Next: blind adversary on THIS spec (the shared construct) before either pre-reg.
Then two pre-regs fan out from the hardened axis, a shared adversary hits both, then freeze. No code
touches either substrate before the respective freeze. The cross-substrate symmetry (same axis, same
metric shape, same `bisg − noise` contrast) is the generalization the project has been missing.
