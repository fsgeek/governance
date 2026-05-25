# Compliant-practice disparate impact (V2) — C2 + C4 result note

**Pre-registration (FROZEN):** `docs/superpowers/specs/2026-05-24-compliant-practice-disparate-impact-V2-preregistration-note.md`, commit `8fa7992` / OTS `cbd4298`. Predictions immutable.

**Artifacts (committed, OTS-stamped):** engine `d3c2e10`; results `247dced` (`runs/compliant_practice_c2_2026-05-24.json`, `runs/compliant_practice_c4_2026-05-24.json`). C1 result was the prior session (`ed54912`).

**Discipline note (per pre-reg §0):** every divergence below is a *pre-reg-interpretation correction* — a discipline finding, not a prediction edit. Predictions are scored as frozen.

---

## Scorecard for the V2 arc

| Prediction | Prior | Outcome |
|---|---|---|
| **C1** — compliant practice retains disparate impact, dose-dependently | 0.65 | **HIT in shape** (monotone), point-bet (≥0.50 @ ps\*=0.70) **MISS** at every dose |
| **C2** — M_compliant passes rungs 1/2/3a on ≥90% of seeds at ps\* | 0.85 | **HIT** (100% at every ps) |
| **C4** — V2_adv reaches retained_excess ≥ 0.80 while passing rungs 1/2/3a | 0.60 | **MISS** (capped ~0.54, gate-bound) |

HIT / HIT / MISS — both tails of each bet were live; the C4 MISS is the most informative.

---

## C2 — the behavioral audit is blind (HIT)

8 ps × 10 seeds. `M_compliant` (standard GBT on admissible features: x0–x5 + c_fresh; no G, no declared proxies).

| ps | behavioral_pass | rung1 evade | rung3a catch | rung3a jaccard (min) | Δ(M_compliant) | AUC |
|----|-----------------|-------------|--------------|----------------------|----------------|-----|
| 0.50 | 100% | 100% | 0/10 | 1.000 | −0.172 | 0.766 |
| 0.70 | 100% | 100% | 0/10 | 0.957 | −0.258 | 0.787 |
| 0.85 | 100% | 100% | 0/10 | 1.000 | −0.424 | 0.832 |

Disparate impact climbs monotonically (−0.17 → −0.42) **and** accuracy rises (AUC 0.77 → 0.83) as proxy strength increases, while the model passes rungs 1/2/3a on 100% of seeds at every dose. The audit is not fooled — there is no fingerprint to find. This is **near-structural**, as the pre-reg flagged (§3, P-C2): `M_compliant` uses neither G nor a declared proxy, so KernelSHAP/LIME cannot attribute to one and there is nothing for the set-reorganization rung to detect. The pre-reg's residual worry — that anomalously high c_fresh reliance would thin the rung-3a margin — **did not materialize**: jaccard stays ≈ 1.0 across the dose range.

**Pre-reg-interpretation correction (C2-1):** rung 2 (surrogate-band disagreement) has **no frozen binary threshold** in the V1 instrument. Reported here as a continuous diagnostic (mean ≈ 0.07–0.12, far from the 0.5 max-split); `behavioral_pass` keys on rung 1 (evade) AND rung 3a (no-catch). Documented, not silently binarized.

---

## C4 — the optimized admissible adversary is gate-bound (MISS)

8 ps × 8 seeds. V2_adv = CMA-ES over an admissible-pool lever, maximizing `adverse_excess` subject to passing rungs 1/2/3a and the admissible AUC gate.

| ps | retained_adv (V2_adv) | honest (M_compliant) | gate | rungs | success |
|----|----------------------|----------------------|------|-------|---------|
| 0.50 | 0.114 | 0.032 | ✓ | ✓ | 0/8 |
| 0.60 | 0.146 | 0.065 | ✓ | ✓ | 0/8 |
| 0.70 | 0.270 | 0.168 | ✓ | ✓ | 0/8 |
| 0.80 | 0.441 | 0.317 | ✓ | ✓ | 0/8 |
| 0.85 | **0.544** | 0.419 | ✓ | ✓ | 0/8 |

`retained_adv` rises strictly monotonically (0.11 → 0.54). The optimized adversary beats honest practice at **every** dose (by ~+0.10), every model is gate-valid and rung-clean — but it **never reaches 0.80**, topping out at 0.54 at the highest proxy strength. **P-C4 MISS.**

### The moat: the MISS is gate-bound, not a weak adversary

The strongest admissible lever (`lever=both`: feature-subset selection + sample-reweighting, full budget, 5 seeds at ps=0.85) lands at **retained_adv = 0.546** (CI [0.531, 0.563]) — statistically indistinguishable from reweight-only (0.544). The realized subsets keep all or nearly all admissible features (dropping them costs AUC and breaches the gate). So **adding lever cleverness buys essentially nothing**: the binding constraint is the **γ=0.02 admissible AUC gate**, not the search. An intentful admissible adversary held within γ of honest accuracy is capped at ~0.54 of M_full's excess disparate impact, regardless of how it is optimized.

### Pre-reg-interpretation corrections (C4)

- **C4-1 (dual gate not jointly feasible).** §2f frames the dual AUC gate (full: `AUC ≥ AUC(M_full)−γ`; admissible: `AUC ≥ AUC(best admissible)−γ`) as a joint search constraint. The **full gate is structurally infeasible** for any admissible-only model — M_full's accuracy edge derives from G + the declared proxies the adversary cannot use (the asymmetry §2f's own warning anticipated). Operative search constraint is the **admissible gate** (feasible); the full gate is reported as context. P-C4's success text omits the gate, so no prediction is edited.
- **C4-2 (gate is a hard constraint, not a soft penalty).** A soft penalty (5×) let CMA buy gap by trading through the admissible gate and report an invalid model. Enforced as a hard barrier (infeasible points dominated by any feasible point; deficit term steers CMA back to feasibility).
- **C4-3 (the lever — tree-invariance).** GBTs are invariant to per-feature monotone scaling, so "feature weighting" of a tree ensemble is a no-op. The non-vacuous CMA-ES lever is **sample-reweighting** (`exp(w·x_std)` over admissible features); `--lever subset|both` adds feature-subset selection. Subset logits initialize positive so CMA starts at a feasible ≈M_compliant point.

---

## Honest scope (the framing the data licenses, and only that)

- **The MISS is γ-conditional.** 0.54 is the cap *at γ=0.02*. The real object is the surface `retained_adv(proxy_strength; γ)`, not a single ceiling. A γ-sweep is a defined next experiment (declare-and-sweep the codification constant, cf. the knob-robustness finding).
- **No V1 contrast is claimed.** It is tempting to read the MISS as "transform indirection (V1) did real work the admissible adversary cannot" — i.e. V1 and V2 are not the same continuum, reversing §2f's hope. **That comparative is unverified: V1's `T_adv` was never run on this substrate.** Running it (does it exceed 0.54?) is the experiment that would license the claim. Until then the finding is narrow: *V2_adv is gate-bound at ~0.54 under γ=0.02.*
- **C4 is independent of the spine.** C4 is the secondary, intent-requiring bound. Its MISS does not strengthen C1/C2 — they stand on their own. The honest statement is that the **intent-free** reconstruction (C1 retains impact, C2 it is undetectable) is the live threat, while the **optimized** admissible adversary is bounded by the accuracy-preservation constraint. That is a sharper regulatory point than "anyone can fully launder," not a weaker one: the bad actor is *capped* while the honest practitioner reproduces the impact anyway.

---

## C3 corrections carried forward (from the pre-harness probes)

The C3 path was probed but not run as a full grid (`working_notes/2026-05-24-c3-substrate-probe-findings.md`). The four pre-reg-interpretation corrections owed there stand and belong in the C3 result note:

1. **R4 operationalization** — the pinned marginal form is blind (both operands world-invariant); the operative form is the conditional deconfounding contrast.
2. **Metric** — effect-size margin-over-R1-null (paired-bootstrap CIs) co-primary with `separation_auc` (which manufactures signal from sign-consistent leak; the R1-null sanity check fires).
3. **Calibration sufficiency** — the §2d omnibus row-level gate under-certifies detectability; calibrate against the actual references, state the capacity-parity boundary. (This is "the bracket": omnibus lower bound vs the C3-floor upper bound.)
4. **§2d test fragility** — split by pair index (a shuffled split inverts on the shared-X twins).

**Dependencies:** the C3-payload headline runs on reproducible cross-fitted GBT AUC-lift estimators (probe-validated mechanism-faithful). `npeet` (KSG, R4) and `econml` (double-ML, R5) now import in the repo `.venv` (installed via `uv pip install econml` and `uv pip install "git+https://github.com/gregversteeg/NPEET.git"` — a local-only hack, not in the clean deps). They are a **documented robustness arm only**, never load-bearing; record the install commands + pinned versions in the C3 result JSON so the arm is reproducible-with-effort.

---

## Defined next experiments (for the next session)

1. **Full C3 grid** — now dep-unblocked; report the R4-deconf effect-size dose-response + the omnibus/targeted bracket.
2. **V1 `T_adv` on the twin substrate** — the test that would license (or kill) the V1≠V2 continuum claim.
3. **γ-sweep** — `retained_adv(proxy_strength; γ)` as a surface; how much accuracy slack buys how much extra gap.
