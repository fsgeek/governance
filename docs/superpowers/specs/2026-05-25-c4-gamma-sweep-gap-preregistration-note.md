# C4 γ-sweep — the `gap(γ)` operating surface and the intent-residue test (follow-on pre-registration)

**Status:** DRAFT until committed; freeze on commit (post-commit hook auto-OTS-stamps). Predictions/priors below are the researcher's frozen bets and are scored as-is per [[project_pre_registration_pattern]].
**Date:** 2026-05-25.
**Type:** Follow-on to the FROZEN V2 pre-reg (`docs/superpowers/specs/2026-05-24-compliant-practice-disparate-impact-V2-preregistration-note.md`, commit `8fa7992` / OTS `cbd4298`). This is a **declare-and-sweep of a frozen codification constant** (`γ`, the admissible AUC-gate tolerance, V2 §2h) — the same discipline V2 §2h already applies to `τ_launder` (±50%) and the knob-robustness finding ([[project_knob_robustness_result]]). It is NOT a new primary arc. **The V2 C4 prediction (P-C4: retained ≥ 0.80 at γ=0.02) is already scored MISS and is not re-litigated.** What is new — and therefore frozen here before computing — is the `gap(γ)` object and the rival-frame bets on `gap(0)`.

## 0. Why this experiment exists (the big-picture gate)

The C4 result note (`2026-05-25-compliant-practice-C2-C4-result-note.md`) found the optimized admissible adversary `V2_adv` **gate-bound at retained_excess ≈ 0.54** under the frozen `γ=0.02`, beating honest compliant practice by a near-constant **~+0.10** at every proxy dose. The honest-scope section flagged the real object as the surface `retained_adv(proxy_strength; γ)`, not the single ceiling.

This follow-on tests **whether the governance domain has any structural escape at all**, on the axis where it differs from the epistemic-observability work ([[reference_ai_honesty_paper]] / [[project_ser_estar_lens]]):

- In ai-honesty, fabrication is a **computational deviation** (entropy/attention telemetry, AUC 0.89–0.95) — a byproduct the model cannot suppress — so an interface change *escapes* the text-only impossibility.
- In fair-lending, the **intent-free** reconstructor (C2) has **no computational deviation** to detect (it genuinely fits admissible features; the discrimination lives in the world's `p(G | admissible)`), so no telemetry escapes.
- The **intentful** adversary (C4) is the one place a governance analogue of the telemetry escape *appears*: optimizing excess disparate impact pushes the model off the accuracy frontier, and the `γ`-gate measures that deviation. `gap(γ)` is the size of that detectable-intent regime; **`gap(0)` adjudicates whether the escape survives the zero-tolerance limit.**

So `gap(γ)` is not a tuning curve — it measures whether the C4 moat is a **structural** barrier or **only an accuracy-tax** that vanishes when the adversary is pinned exactly to the honest accuracy frontier.

## 1. The object

For each cell (`proxy_strength`, `seed`, `γ`):
- `retained_excess_adv(γ)` — V2_adv's excess disparate impact as a fraction of `M_full`'s, under the admissible AUC gate at tolerance `γ` (engine `c4_cell`, frozen gate keying `best_adm_auc = max(auc_compliant, auc_strict)` kept verbatim so the `γ=0.02` column reproduces the committed grid).
- `retained_compliant` — `adverse_excess(M_compliant)/adverse_excess(M_full)`. **γ-INDEPENDENT** (M_compliant is an ungated standard fit), so it is a flat baseline across the sweep.
- **`gap(γ) ≡ retained_excess_adv(γ) − retained_compliant`** — the audit-visible residue of intent: extra excess the optimized adversary extracts over honest practice while staying rung-clean and inside the gate.

**Deliverable:** the surface `gap(γ)` and `retained_excess_adv(γ)` over `γ ∈ {0, 0.005, 0.01, 0.02, 0.04, 0.08, 0.15}` at `proxy_strength = 0.85` (primary, max signal) and `0.70` (secondary/robustness), 8 paired seeds, `lever=reweight`, paired-seed bootstrap 95% CIs. `0.02` is the frozen-pre-reg column (reproduction check). `0` is the zero-tolerance anchor (the load-bearing point).

**Balanced-panel reporting (pre-registered; a measurement confound caught at build time).** Degeneracy (§P-γ-deg) is monotone in `γ` (`degenerate ⇔ auc_strict > auc_compliant + γ`; loosening `γ` only removes degeneracy), so the per-`γ` "clean" subset *grows* with `γ` — a naive `gap(γ)` curve would compare different seed populations across `γ`. **Primary estimate is the BALANCED PANEL: the fixed set of seeds non-degenerate at `γ=0`, evaluated at every `γ`, so the curve is within-seed.** The `γ`-varying per-`γ`-clean subset is reported as robustness only. This forecloses the selection-bias read of a positive `gap(0)` (conditioning on feasibility at `γ=0` selects seeds where `M_compliant` is the strong admissible model, which could deflate `retained_compliant` and inflate `gap`); the balanced panel uses the same seeds throughout.

**Freeze-honesty disclosure (a threading smoke was run before freeze).** A `--smoke` run (`n=2000`, CMA budget 30 evals, `ps∈{0.55,0.70}`, 2 seeds — NOT the grid) was run only to verify `--gamma` threading. It confirmed threading and the degenerate-start mechanism, and incidentally showed feasible-cell `gap(0)` positive at ~+0.04–0.06 at that toy budget. This is **explicitly NOT scored** (smoke ≠ grid: 10× fewer rows, 166× smaller search, wrong `proxy_strength`, no balanced panel) and is disclosed so the freeze is honest about what the researcher had seen — hiding a directional peek would be the quiet form of the frame-forcing this project studies.

## 1b. `gap(γ)` is conditioned on a VALID in-gate adversary (pinned before compute; the smoke surfaced this)

Under held-out eval, a val-selected adversary can breach the **test** gate (the holdout smoke showed `gate_admissible_pass=False` on every γ=0 toy cell). Counting such a model in `gap` would credit val-overfitting — a softer form of A1. So **`gap(γ)` is estimated over cells with `gate_admissible_pass=True` on the report frame** (valid in-gate adversaries), and **`gate_pass_rate(γ)`** — the fraction of (balanced-panel) seeds for which a valid in-gate adversary exists at all — is reported as a **co-primary** quantity. A γ where `gate_pass_rate < 0.5` flags `gap(γ)` as low-power / near-unevaluable.

This refines how the rival frames can resolve: P-γ1 (no structural escape) can be realized **two ways** — `gate_pass_rate(0) ≈ 0` (zero-slack admits no valid held-out adversary at all) and/or `gap(0) ≈ 0` among any that do pass. Both are P-γ1 wins; both are reported. P-γ2 (Rashomon reservoir) requires a non-trivial `gate_pass_rate(0)` **AND** `gap(0) ≥ 0.05` among the passers — a real, held-out, in-gate intent residue at zero slack.

## 2. Pre-registered predictions (frozen bets — rival frames, deliberately balanced so confirmation has nothing to grab)

The two readings I minted while analysing C4 make **opposite bets on `gap(0)`**. They are registered at near-equal priors precisely so that *either* outcome refutes one of my own satisfying frames ([[feedback_anti_confirmation_procedure]]):

- **P-γ1 — ser/estar floor (no structural escape; the moat is only an accuracy-tax).** At `ps=0.85`, EITHER `gate_pass_rate(0) < 0.5` (zero slack admits essentially no valid held-out adversary) OR `gap(0) ≤ 0.02` among the passers (within paired-seed noise of zero). Reading: pinning *estar* to zero accuracy-slack erases the observable residue of intent; an adversary held to the honest accuracy frontier on held-out data is as invisible as the honest reconstructor; the intentful/intent-free distinction collapses in the limit. **Prior 0.45.**
- **P-γ2 — Rashomon multiplicity (a footprint-free reservoir; structural escape fails for the auditor, not the adversary).** At `ps=0.85`, `gate_pass_rate(0) ≥ 0.5` AND `gap(0) ≥ 0.05` (held-out, in-gate). Reading: the accuracy-*isovalue* admissible model set (a γ=0 Rashomon set) carries exploitable disparate-impact spread that survives held-out test-gating; the optimizer navigates it at zero accuracy cost. This would be the **Rashomon-multiplicity-of-disparate-impact** result surfacing natively on the C4 substrate. **Prior 0.45.** (Residual ~0.10 mass on the ambiguous band — reported as-is, not forced into either frame.)
- **P-γ3 — shape: monotone & concave, no cliff.** `retained_excess_adv(γ)` is monotone non-decreasing in `γ` (no adjacent-γ CI-excluding-zero reversal) AND concave (diminishing returns). **Prior 0.60.** A convex jump at some `γ*` (a phase transition) is the surprise and a finding, not a MISS of monotonicity.
- **P-γ4 — the laundering bar stays unreachable even at 7× tolerance.** At `ps=0.85`, `retained_excess_adv(γ=0.15) < 0.80`. **Prior 0.50.** Tests whether the C4 MISS is structural or merely γ=0.02-tight; either way the answer quantifies how much accuracy slack full laundering would cost.

**P-γ-deg — degenerate-start handling (a procedure pre-commitment, not a substantive bet).** The frozen gate keys on `best_adm_auc = max(auc_compliant, auc_strict)`. The CMA start `w=0` reproduces `M_compliant` exactly (`auc_adv == auc_compliant`). On any seed where `auc_strict > auc_compliant + γ`, the honest start is **infeasible** (no feasible interior) and `gate_admissible_pass=False` structurally. Such cells are flagged `degenerate_start` and **EXCLUDED from the `gap(γ)` / `retained_adv(γ)` estimate**, reported separately as a count. This is a finding about the gate's keying (most acute at γ=0), not evidence for or against P-γ1/P-γ2. **If degenerate-start cells are the *majority* at γ=0**, `gap(0)` is reported as **unevaluable at the anchor** and the rival frames are adjudicated at the smallest γ with a clean majority (and the keying-sensitivity is the headline instead).

## 3. Bidirectional counterexamples we hunt
1. `gap(0)` materially > 0 with tight CIs on clean cells → **P-γ2 wins, P-γ1 falsified**: a real isovalue DI reservoir; governance has no structural escape and the Rashomon-multiplicity reading is the finding (escalates the line, ties to the published-Rashomon defense in [[project_fairwash_reorganization_prereg]]).
2. `gap(0) → 0` cleanly → **P-γ1 wins, P-γ2 falsified**: the moat is entirely thermodynamic (an accuracy-tax); the reassuring "bad actor is capped" C4 framing is an artifact of `γ>0`, which *sharpens* the regulatory point (set γ→0 and intent is undetectable, exactly as the intent-free case already is).
3. A convex cliff in `retained_adv(γ)` → critical accuracy-slack threshold beyond which the audit fails discontinuously (P-γ3 finding).
4. Degenerate-start dominates γ=0 → the gate's `max(comp,strict)` keying, not the search, governs the limit (P-γ-deg finding; a keying critique of the inherited instrument).

## 4. Meta (frozen)
- Reporting `gap(0)` only where it favors a frame, or dropping degenerate-start cells silently, is the frame-forcing this project studies. Both frames are registered at ~0.45; the degenerate handling is pre-committed above.
- `gap(γ)` is an **operating surface**, not a single number; the result note ships the curve with CIs (the report-surfaces-not-points discipline, [[project_knob_robustness_result]] / V2 §2i). The four point-bets exist only to keep the registration HIT/MISS-scorable.
- This sweep does NOT license the V1≠V2 continuum claim (that needs V1 `T_adv` on the twin substrate — a separate experiment). Scope is: *is the C4 moat structural or an accuracy-tax, as a function of the declared constant `γ`.*

## 4b. Blind red-team before freeze (the proof-of-work that changed the design)

A blind adversarial reviewer (kept blind to the §2 predictions; code-only) red-teamed the measurement before this freeze ([[feedback_anti_confirmation_procedure]]). It found one **invalidating** artifact and several handling rules, all incorporated below:

- **A1 (INVALIDATOR — selection-on-test leak).** The inherited engine had CMA-ES select `best_w` against the *same test split* `_delta_auc` scores and the gate enforces (up to ~5000 evals selecting on test Δ). This overfits test-set Δ and would **manufacture a positive `gap(0)`** out of optimization noise — a false signal for P-γ2 — even at zero AUC slack. **Fix (frozen): leak-free held-out evaluation** — fit on train, CMA selects on `sub.val` (gate threshold = val `best_adm_auc`), all reported metrics + the gate evaluated on `sub.test`. Engine gains `holdout` (sweep default ON); the legacy test-selected path is retained only to (a) reproduce the committed grid and (b) **quantify the overfit**: the committed C4 `0.544` used the leaky path, so `retained_adv(holdout) − retained_adv(legacy)` at γ=0.02 is a reported caveat on the committed number.
- **A2 (constant CMA budget).** Early-stop patience made optimizer effort γ-dependent (wide feasible set at large γ → early stalls), biasing curve *shape*. **Fix:** early-stop disabled and a **constant budget** of `maxgen=70` (×pop 16 = **1120 evals**, ≈ the committed C4 grid's median of 1104, range 416–2240) used at every γ; `evals_mean` reported per γ to confirm constancy. The constant budget matches the committed grid's typical effort so the holdout-vs-legacy comparison is effort-fair.
- **A3/A4 (denominator + sign robustness).** `gap_median` reported beside `gap_mean`; per-γ counts of `ae_full < 0.10` (near the `ε_excess=0.05` floor) and of sel/rep sign-`s` flips are reported; the `ε_excess` floor already guarantees `ae_full ≥ 0.05`.
- **A5 (panel selection bias — reported, not eliminated).** The balanced panel keeps seeds with `auc_comp ≥ auc_strict` at γ=0; the `auc_comp − auc_strict` distribution of included vs excluded seeds is reported so the AUC-ordering bias is visible.

A negative or near-zero `gap(0)` under the **leak-free** path, where the **legacy** path shows positive, is itself a headline finding: the C4 moat's apparent intent-residue was test-overfitting, and the committed `0.544` is biased high.

## 5. Implementation
- Engine: `scripts/compliant_practice_test.py` — `γ` threaded as `c4_cell(..., gamma=)` / `run_c4(..., gamma=)` / `--gamma` (default `GAMMA_C4=0.02`, the frozen value); `holdout` added (`--holdout`) for leak-free val-select/test-report (§4b A1); gate keying (`best_adm_auc=max(comp,strict)`) and all other C4 mechanics unchanged (tooling change; git history is the receipt — [[feedback_tooling_is_mutable]]).
- Driver: `scripts/c4_gamma_sweep.py` — sweeps `γ × seed` at fixed `proxy_strength`, **holdout ON by default**, constant CMA budget `maxgen=70` (§4b A2), computes `gap` per cell, flags `degenerate_start`, reports balanced-panel (primary) + per-γ-clean (robustness) with paired-seed bootstrap CIs + the §4b A3/A4/A5 diagnostics. Reuses `c4_cell` (frozen `run_c4` untouched). **Sharding:** `--shard-only` computes a cell subset (compute is embarrassingly parallel); `--merge` does the single aggregation pass (the balanced panel needs all cells), so the 56-cell ps=0.85 grid runs across cores in ~1 cell-time wall.
- Reproduction + overfit check: a **legacy** (`--no-holdout`) run at `γ=0.02`, `ps=0.85` must reproduce the committed grid (`retained_adv ≈ 0.544`) within seed variance (else threading bug); the holdout-vs-legacy delta there is the reported overfit caveat (§4b A1).

---
**Author:** Claude Opus 4.7 (researcher), governance lineage. **Date:** 2026-05-25. **OTS:** auto on freeze (post-commit hook). PI delegated the choice and the freeze ("this is yours as the researcher").
