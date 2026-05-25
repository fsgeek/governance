# V1≠V2 — does the explicit fairwash transform break the C4 accuracy-tax cap? (follow-on pre-registration)

**Status:** DRAFT until committed; freeze on commit (post-commit hook auto-OTS-stamps). Predictions/priors below are the researcher's frozen bets and are scored as-is per [[project_pre_registration_pattern]].
**Date:** 2026-05-25.
**Type:** Follow-on to the FROZEN V2 pre-reg (`docs/superpowers/specs/2026-05-24-compliant-practice-disparate-impact-V2-preregistration-note.md`, commit `8fa7992` / OTS `cbd4298`) and to the C4 γ-sweep result ([[c4-gamma-sweep-gap-result]], `3c6d2e3`). The V1 fairwash-*transform* pre-reg (`daf032d` / OTS `9e8abe7`) was stamped-but-never-run-at-scale; this is the experiment that licenses-or-kills its central claim. **Predictions immutable once stamped.**

## 0. Why this experiment exists (the load-bearing gate)

The whole cookbook → impossibility arc rests on a **V1≠V2 asymmetry**: the construction-receipt defense closes the *intentful* recipes (explainer-shopping, surrogate-distill, the V1 fairwash *transform* `T_adv`) but **provably fails on the intent-free V2** (honest non-teleological practice — no shopping to catch). That asymmetry is *why V2 is the paper spine*.

But the C4 γ-sweep just complicated the intentful side. The optimized **admissible-reweighting** adversary (`V2_adv`, `lever=reweight`) is bounded at `retained_excess ≈ 0.50` held-out, and that bound is an **accuracy-tax, not a structure**: `gate_pass_rate(0)=0` — at zero AUC slack no valid in-gate adversary exists. The reweighting lever's cap is thermodynamic (set by the AUC gate), not a property of the lever's cleverness.

So the open question: **is the cap a property of the reweighting lever, or of the gate?** The V1 `T_adv` *explicit transform* is a strictly more expressive lever — it refits a legitimate base to `M_full`'s decisions, then re-projects the dropped G-driven residual onto admissible carriers via fitted per-carrier correctors (`fft._build_laundered` / `LaunderedModel`), with CMA over the routing weights. Two of the project's own findings make **opposite predictions** about what this lever does against the cap:

- **V1≠V2-spine** predicts the transform **exceeds** the cap: the explicit residual-rerouting buys disparate impact the honest reweighting lever cannot reach. The asymmetry is real and quantified.
- **C4-γ accuracy-tax** predicts the transform **hits the same wall**: the binding constraint is the admissible AUC gate, which is lever-independent. More laundering expressiveness cannot dodge the accuracy toll required to retain excess disparate impact while staying in-gate on held-out data.

This experiment adjudicates between them. Either way the impossibility paper's central asymmetry is sharpened: confirmed-and-quantified, or relocated from *magnitude* to *provenance* (intentful is catchable by the construction receipt even though its disparate-impact reach is no larger than honest practice).

## 1. The object

Same leak-free harness and metric as `c4_cell` (so the V1 lever compares apples-to-apples against the ~0.50 reweighting cap). For each cell (`proxy_strength`, `seed`, `arm`):

- **Lever (the only change from C4):** the V1 `LaunderedModel`. `M = M_full` (the discriminatory model on `OBS + G`). `_build_laundered` fits a legitimate base on `V_named` (= x0..x5; declared proxies x6,x7 excluded) to `M`'s train decisions, then fits per-carrier GBT correctors to the residual `proba(M) − base_p` on carriers = `c_fresh ∪ {2 lowest-coef V_named}`. CMA-ES optimizes the softmax routing weights `w`.
- **`retained_excess_adv = adverse_excess(T) / adverse_excess(M_full)`**, `adverse_excess = s·(Δ_DP − Δ_DP(M_oracle))` — V2's metric verbatim, NOT V1's native `r_retained = Δ_T/Δ_M` (which has a different denominator and is *not* comparable to the cap; `r_retained_native` is reported only as a cross-reference to the V1 paper number).
- **AUC gate** keyed on `best_adm_auc = max(auc_compliant, auc_strict)`, tolerance `γ=0.02` (frozen V2 value), enforced as a HARD barrier — verbatim from `c4_cell`.
- **Two arms** (both run): **matched** = CMA maximizes `adverse_excess` s.t. the gate (objective *identical* to `c4_cell` — isolates the lever); **faithful** = V1's own objective, minimize max `c_fresh` split-importance while holding a retention floor (`fft.RETENTION_FLOOR=0.05`) + the gate (the recipe as the cookbook ships it: "spread the residual to evade rung-3b detection").

**Leak-free (mandatory — the A1 lesson from the γ-sweep).** Fit on `train`; CMA selects `best_w` on `sub.val` (gate threshold = val `best_adm_auc`); `retained_excess`, AUC gate, and rung validation all computed on `sub.test`. The val→test gap is where a clever lever's overfit gets exposed — exactly the trap that inflated the committed C4 `0.544`.

**Deliverable:** `retained_excess_adv` and `gate_admissible_pass_rate` for both arms over the proxy grid, primary at `proxy_strength=0.85` (max signal, matches the γ-sweep anchor), 8 paired seeds, paired-seed bootstrap 95% CIs. Headline comparison: V1 (both arms) vs the V2 reweighting cap (~0.50 held-out) vs honest `retained_compliant` (~0.41).

## 2. Pre-registered predictions (frozen bets)

- **P-V1a — matched-objective held-out cap (headline).** At `ps=0.85`, `P(matched retained_excess > 0.60 held-out) = 0.40`. I lean the accuracy-tax reading wins (the transform hits ~the same gate-bound wall as reweighting, so it does **not** clear 0.60), but not confidently — the surrogate refit may find AUC-preserving routes reweighting cannot. **A matched `retained_excess` materially above the ~0.50 reweighting cap with CIs excluding it = V1≠V2 confirmed (the lever has real extra reach). At-or-below = accuracy-tax universal (the cap is the gate, not the lever).**
- **P-V1b — gate survival at zero slack.** `P(matched gate_admissible_pass_rate(γ=0.02) ≥ 0.5 held-out) = 0.55`. The reweighting lever's `w=0` start is feasible by construction (it *is* `M_compliant`); the laundering lever has **no honest feasible start** (`T` at uniform routing is already a perturbed model), so I expect MORE held-out gate breaches than reweighting — a structural disadvantage of the explicit transform worth surfacing regardless of P-V1a.
- **P-V1c — faithful arm retains less excess than matched.** `P(faithful retained_excess < matched retained_excess, paired) = 0.70`. The faithful objective spends its optimization budget *hiding* the carrier (min `c_fresh` importance) rather than maximizing excess, so it should retain less disparate impact than the matched arm even when both stay in-gate. If faithful ≥ matched, the evade-objective is *free* (hiding costs no excess) — a sharper cookbook finding than either cap.
- **P-V1d — rung-3a stays clean (structural pass).** `P(rung3a_catch = False on ≥ 90% of cells) = 0.85`. The laundered model never touches a prohibited feature (base on V_named, carriers admissible), so the prohibited-set-relative rung 3a should not catch it — the same blindness [[project_fairwash_reorganization_prereg]] found. A catch would mean the laundering perturbs the band's prohibited-feature reliance indirectly — a finding.

## 3. Bidirectional counterexamples we hunt
1. **matched `retained_excess` ≫ 0.50 cap, CIs clean** → V1≠V2 confirmed and quantified; the explicit transform's extra DOF is real; the spine asymmetry holds on magnitude. (P-V1a high tail.)
2. **matched `retained_excess` ≤ reweighting cap** → accuracy-tax is lever-independent; V1≈V2 on reach; the asymmetry relocates to provenance (construction receipt), not disparate-impact magnitude — a *stronger* impossibility statement (even the explicit adversary buys nothing extra). (P-V1a low tail.)
3. **faithful ≥ matched on excess** → detection-evasion is excess-free; the cookbook's "spread to evade" move costs nothing. (P-V1c MISS = finding.)
4. **gate_pass collapses for the laundering lever where it held for reweighting** → the explicit transform is *more* fragile held-out (no feasible honest start); intent leaves an accuracy footprint the reweighting lever avoids. (P-V1b MISS = finding.)

## 4. Meta (frozen)
- Reporting only the arm or the proxy-dose that favors a frame is the frame-forcing this project studies. Both arms run; the full proxy grid ships in the result note; the four point-bets exist only to keep the registration HIT/MISS-scorable.
- The comparison is to the **held-out** C4 cap (~0.50), NOT the committed test-overfit `0.544` ([[c4-gamma-sweep-gap-result]] A1). Both V1 arms run holdout-only.
- This experiment is the load-bearing **V1≠V2** test the C4/C2 notes both fenced as not-yet-made. It does not touch C1/C2/C3; their dispositions stand.

## 5. Implementation
- Engine: `scripts/compliant_practice_test.py` — `c4v1_cell` / `run_c4v1` / `--mode c4v1 --arm {matched,faithful} --holdout`. Reuses `c4_cell`'s baselines, leak-free split, gate keying, CMA loop, and rung validation verbatim; the only swap is the lever (`fft._build_laundered` routing vs admissible sample-reweighting). Frozen `c4_cell`/`run_c4` untouched (tooling change; git history is the receipt — [[feedback_tooling_is_mutable]]).
- Smoke (threading verification, NOT scored): `--mode c4v1 --arm {matched,faithful} --holdout --smoke` (`n=2000`, CMA budget ≤60 evals, `ps∈{0.55,0.70}`, 2 seeds). Disclosed in §1b below per freeze-honesty.
- Real run: `--mode c4v1 --arm matched --holdout --proxy 0.85 --seeds 8` and the same with `--arm faithful`; full proxy grid as a secondary dose curve.

## 1b. Freeze-honesty disclosure (smoke before freeze)

Both arms were threading-smoked before this freeze (`--smoke`: `n=2000`, CMA budget 30 evals = maxgen-bound at 5 gens, `ps∈{0.55,0.70}`, 2 seeds — NOT the grid). What the researcher saw, disclosed so the freeze is honest (hiding a directional peek is the quiet form of the frame-forcing this project studies):

- **Harness verified:** the V1 laundering lever wires through the leak-free split, the gate, and rung validation; `r_retained_native` positive (+0.16 to +0.28) confirms the laundering retains original-gap as expected.
- **Gate-passing cells only (ps=0.55):** matched `retained_excess` = +0.027, +0.101; faithful = +0.022, +0.089 (faithful ≤ matched on excess — weak P-V1c whiff), and faithful's `max_cfresh` importance is driven near-zero (0.000, 0.005) vs matched's (0.014, 0.022) — the evade-objective working as designed.
- **ps=0.70 cells breach the held-out gate** (`gate_admissible_pass=False`) on both seeds, both arms — an early whiff of P-V1b (the laundering lever has no honest feasible start, unlike reweighting's `w=0`).
- matched `retained_excess` sits well below 0.60 (weakly consistent with the P-V1a accuracy-tax lean).

**Explicitly NOT scored.** The toy budget is ~19× smaller than the real run's CMA effort (30 vs ≤5000 evals), `n` is 4× smaller, only 2 seeds, and the primary anchor `ps=0.85` was not run. These directional whiffs are disclosed, not weighed; the frozen priors in §2 stand as written.

---
**Author:** Claude Opus 4.7 (researcher), governance lineage. **Date:** 2026-05-25. **OTS:** auto on freeze (post-commit hook).
