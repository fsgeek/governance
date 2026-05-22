# Result note — Codification-knob robustness (Arm 1: adequacy threshold)

**Pre-reg (FROZEN, OTS-stamped):** `docs/superpowers/specs/2026-05-22-codification-knob-robustness-preregistration-note.md` — commit `02fc921`, stamp `5a7f8d6`.
**Run:** `scripts/knob_robustness_arm1.py` → `runs/knob_robustness_arm1_2026-05-22.json`. Recompute-only (re-threshold stored per-cell R²_named; no re-fit). Tests: `wedge/tests/test_knob_robustness.py` (8 passing).
**Date:** 2026-05-22.

## Scorecard against the frozen predictions

- **P1 (HMDA ≥20% of cells flip) — MISS** (prior 0.80; surprised). Only **10.7%** of in-scope HMDA cells change silence label across the sweep. The population is mostly *robustly both-inadequate*; fragility concentrates in the handful of verdict-determining boundary cells, not the population. The prediction was operationalized on the wrong target (population flip-fraction); the right target is verdict-determining-cell fragility, where HMDA's lone silence positive is 100% fragile.
- **P2 (the 3 FM silence cells never flip) — FALSIFIED, 2/3 robust** (prior 0.75; partial). rb00 (gap 0.733, R²_named_A=0.035) and rb09 (gap 0.721, R²_named_A=0.022) are silent at **every** sweep point. rb05 (gap 0.480, R²_named_A=0.2077) **flips** — it loses silence at threshold 0.20 because its named-only R² sits just above that sweep point. Margin, not the freeze, is what makes rb00/rb09 unbreakable.
- **P3 (flips track inherited, not declared, knobs) — structurally confirmed but uncontrastable.** Every silence cycle (#12, expanded, frame-evocation, hmda) **inherited** the 0.30 threshold from #11; none declared or justified it. All are fragile (frac-positives-fragile 0.33–1.0). There is **no declared-knob silence cycle** to contrast against — which is the finding: the silence-manufacture verdict was never built on an owned threshold.
- **P4 (treatment more robust than control) — NOT ADJUDICATED.** The natural control (saturation-phase) shares #12's exact cells, so per-cell fragility is identical by construction; lc-centrality is a different verdict family. P4 as operationalized is degenerate-by-shared-substrate — a flaw in the pre-reg design, surfaced by the run (the kick-point flagged pre-freeze).
- **Global falsifier (P2 fails AND P1 holds → every adequacy verdict is a knob artifact → H_DnS false) — NOT triggered.** P1 missed and P2 failed only partially (large-gap cells hold). The harshest falsifier does not fire.

## Verdict on H_DnS: relocated, not confirmed or refuted

The discipline-vs-structure binary was the wrong frame. The sweep exposes a **third protective mechanism the dichotomy missed: effect-size margin.**

- What keeps the **core** FM silence finding from being a knob artifact is neither the OTS freeze (which never pinned the threshold — inherited everywhere) nor the frame's self-applying form. It is that the genuine silence cells have R²_named_A ≈ 0 and gaps of 0.72–0.73: the named vocabulary explains *essentially nothing* while the full vocabulary explains nearly everything. Those cells are silent at any threshold in [0, 0.74]. **Margin is load-bearing; discipline and structure are not, for robustness.**
- The **receipt-leak the bound predicted is real and material.** "Manufactured silence: N cells" has N ∈ [17, 30] on the expanded corpus (a 76% swing) under an inherited, never-declared threshold; **54% of expanded silence cells are marginal cells that wink in and out with the knob.** The freeze defends the prediction, not the threshold-selection upstream of it — and this is the empirical proof the leak is material, not theoretical (pre-reg §1 named exactly this upstream).
- HMDA's "structural inertness" (the falsification that tightened the trimodal claim to FM-only) is **partly a knob artifact**: HMDA's verdict routes through `verdict_differs = (adq_A != adq_B)`, and HMDA's R²_named values cluster on top of 0.30, so its verdict-determining cell is maximally knob-fragile.

## What this changes (forward)

1. **Silence findings must report margin, not just a count.** Report R²_named_A and the A–B gap per silence cell; separate **margin-backed silence** (gap wide, A near 0 — rb00/rb09) from **knob-dependent silence** (gap thin or A near a plausible threshold — rb05, the 14 marginal expanded cells, HMDA's lp32_dec5).
2. **Report the count as an operating curve, not a scalar.** "N cells of silence" should be N(threshold) across a declared sweep — the §4.8 operating-curve / collapse-with-a-receipt pattern, applied to the project's own verdict. The threads close: the experiment that started from §4.8 lands back on it.
3. **Codification constants must be declared and swept as part of the verdict**, not inherited. The freeze's real gap is the un-declared threshold; that gap is invisible without exactly this post-hoc sweep, which the project had never run on the silence axis.

## Followups (four-state)

- **(i)** Arm 2 (ε-band) and Arm 3 (vocabulary) — re-fit experiments, each its own pre-reg; test whether the *margin* finding survives perturbing the band-construction knobs, not just the threshold.
- **(ii)** Re-issue the silence finding as margin-stratified + N(threshold) operating curve; this is a paper-facing artifact change (the silence-detector claim in section4 should carry the operating curve, not a point count).
- **(iii)** The blind-adjudication experiment (Tony's paired second arm) now has a sharper hypothesis: does a no-stake adjudicator, given only the frozen pre-reg, *re-derive the same silence count* — or does the inherited threshold leave enough latitude that the count is author-discretionary? Arm-1 predicts the count is latitude-laden (knob-fragile).
- **(iv)** Honest correction to the pre-reg: P1 mis-targeted (population vs verdict-cell), P4 degenerate (shared substrate). Recorded, not re-narrated.
