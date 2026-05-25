# C4 γ-sweep — `gap(γ)` result note (the moat is an accuracy-tax, not a structure)

**Pre-registration (FROZEN):** `docs/superpowers/specs/2026-05-25-c4-gamma-sweep-gap-preregistration-note.md`, commit `c413ed9` / OTS `9ab5b84`. Predictions immutable; scored as frozen below.
**Artifacts:** `runs/c4_gamma_sweep_ps085.json` (holdout primary, 56 cells), `runs/c4_gamma_sweep_ps085_legacy.json` (legacy γ=0.02 reproduction, 8 cells). Engine/driver frozen at `c413ed9`. Constant CMA budget 1120 evals/cell (`evals_mean=1120` flat across γ — A2 confirmed). No sign-flips, no near-floor denominators, zero degenerate-start cells (panel = all 8 seeds; `auc_comp − auc_strict ∈ [0.053, 0.078]` on every seed).

---

## Scorecard

| Prediction | Prior | Outcome |
|---|---|---|
| **P-γ1** — ser/estar floor: no structural escape, moat is only an accuracy-tax | 0.45 | **HIT (decisive)** — `gate_pass_rate(0)=0.00` |
| **P-γ2** — Rashomon reservoir: isovalue DI spread, held-out in-gate `gap(0)≥0.05` | 0.45 | **MISS** — falsified; the apparent positive `gap(0)` was the A1 test-leak |
| **P-γ3** — `retained_adv(γ)` monotone & concave, no cliff | 0.60 | **HIT** — 0.40→0.48→0.52→0.52→0.52, saturates by γ=0.08 |
| **P-γ4** — `retained_adv(γ=0.15) < 0.80` (bar unreachable at 7.5× tolerance) | 0.50 | **HIT** — 0.520; structural saturation ceiling |

**P-γ1 HIT / P-γ2 MISS / P-γ3 HIT / P-γ4 HIT.** The decisive bet (P-γ1 vs P-γ2) resolved against my own preferred frame (P-γ2), and resolved *because* the leak-free discipline stripped the artifact that would have confirmed it.

## The surface (holdout, ps=0.85, balanced panel = all 8 seeds)

| γ | gate_pass_rate | gap_mean (in-gate) | gap_ci | retained_adv | retained_compliant |
|------|------|--------|------------------|-------|-------|
| 0.000 | **0.00** | — (no passers) | — | — | 0.41 |
| 0.005 | 0.00 | — | — | — | 0.41 |
| 0.010 | 0.12 | −0.010 (n=1) | — | 0.400 | 0.41 |
| 0.020 | 0.38 | +0.057 (n=3) | [+0.043, +0.074] | 0.479 | 0.42 |
| 0.040 | 0.62 | +0.107 (n=5) | [+0.079, +0.132] | 0.518 | 0.41 |
| 0.080 | 1.00 | +0.100 (n=8) | [+0.081, +0.121] | 0.520 | 0.42 |
| 0.150 | 1.00 | +0.100 (n=8) | [+0.081, +0.121] | 0.520 | 0.42 |

`retained_compliant ≈ 0.41` is flat across γ (γ-independent, as designed — the honest reconstructor needs no gate). The intentful adversary's edge over honest practice (`gap`) saturates at **~+0.10**, and that entire edge is purchased with accuracy-state slack: it does not exist below γ≈0.01.

## The finding (P-γ1): the C4 moat is thermodynamic, not structural

**At zero accuracy-tolerance, no valid held-out in-gate adversary exists** (`gate_pass_rate(0)=0`, all 8 seeds). The val-selected reweighting that maximizes adverse excess always loses enough test-AUC (the val→test generalization gap of the reweighting itself) to breach the γ=0 gate. As γ grows, the tolerance absorbs that gap and adversaries appear: `gate_pass_rate` climbs 0 → 0 → 0.12 → 0.38 → 0.62 → 1.0. So the C4 "moat" — the appearance that an intentful admissible adversary is *bounded* at ~0.54 — is **entirely an accuracy-tax**. Pin *estar* (accuracy state) to zero slack and the intentful adversary has no valid existence at all; it is exactly as constrained as the honest reconstructor. **The intentful / intent-free distinction collapses at the zero-tolerance limit**, precisely as the ser/estar floor ([[project_ser_estar_lens]]) predicts: with zero *estar*-tolerance, a *ser*-difference (intent) produces zero observable footprint — here not because `gap→0` among survivors but because there are no survivors.

**This sharpens the contrast with ai-honesty ([[reference_ai_honesty_paper]]).** There, telemetry escapes the text-only impossibility because fabrication is a computational deviation with a byproduct signal *at any verification budget*. In fair-lending C4, the analogue "escape" (the γ-gate catching intent) is **not a budget-independent byproduct — it is the accuracy-tax itself**, and it vanishes as the tolerance → 0. Governance is strictly harder: even the *intentful* case has no observation-side footprint independent of the accuracy budget. The only escape is construction-time provenance (proof-of-work), not observation — the discipline we used on ourselves here.

## The A1 finding: the committed C4 0.544 was test-overfit

The legacy (test-selected) path **reproduces** the committed grid: `retained_adv = 0.553` over 8 seeds (committed reported ~0.544 ✓). Paired per-seed, the leak inflates `retained_adv` by **+0.057** (legacy − holdout). Two consequences for the committed C4 result note (`2026-05-25-compliant-practice-C2-C4-result-note.md`):
1. The headline `retained_adv ≈ 0.544` at γ=0.02 is **biased high**; the honest held-out value is **~0.50**.
2. Worse, **5 of 8** committed "valid in-gate adversaries" (`gate_admissible_pass=True` under legacy) **breach the held-out test gate** — they were val/test-overfit illusions of gate-validity. The committed gate-pass rate at γ=0.02 was itself partly an artifact (true held-out rate 0.38, not 1.0).

This is the project's own thesis applied reflexively: the committed grid's post-hoc-output metric **estar-passed** (looked like a strong, gate-valid adversary) without **ser** (true held-out laundering capacity). The blind red-team caught it *before* the freeze; had the leaky engine been run, the smoke's `gap(0)≈+0.05` would have been read as a P-γ2 "Rashomon reservoir" win — a false finding. The held-out fix flipped the scientific conclusion. ([[feedback_anti_confirmation_procedure]] — strongest worked instance to date.)

## Honest scope / caveats
- **Low-γ small-n.** `gap` among in-gate passers rests on n=1 (γ=0.01) and n=3 (γ=0.02); the robust regime is γ≥0.04 (n=5–8). The **headline P-γ1 result is not affected** — it rests on `gate_pass_rate(0)=0`, all 8 seeds failing the zero-slack gate.
- **ps=0.85 only.** The frozen bets are all at ps=0.85 (max signal); ps=0.70 (secondary/robustness) was not run. Defined next step.
- **Gate keying unchanged.** `best_adm_auc=max(comp,strict)` kept verbatim; degeneracy was a non-issue at ps=0.85 (would matter where `auc_strict>auc_comp`).
- **Scope.** This does not license the V1≠V2 continuum claim (needs V1 `T_adv` on the twin substrate — separate experiment). It establishes: *the C4 moat is an accuracy-tax in γ, structurally saturating at retained≈0.52, with no valid intentful adversary at zero tolerance.*

## Defined next experiments
1. **Amend the committed C4 result note** with the held-out correction (`0.544 → ~0.50`, gate-pass 1.0 → 0.38 at γ=0.02) — a discipline finding, not a silent edit.
2. **ps=0.70 γ-sweep** (robustness; does the accuracy-tax reading hold at lower proxy strength?).
3. **V1 `T_adv` on the twin substrate** — the load-bearing V1≠V2 test, now with the leak-free harness.

---
**Author:** Claude Opus 4.7 (researcher), governance lineage. **Date:** 2026-05-25. Frozen pre-reg `c413ed9`/`9ab5b84`.
