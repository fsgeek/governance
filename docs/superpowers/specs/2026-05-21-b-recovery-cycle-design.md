# B-recovery cycle — design v2 (the next cycle after #14)

**Date:** 2026-05-21. **Status:** DESIGN v2 (post-adversarial-review; pre-implementation; not yet OTS-stamped). **Author:** Claude Opus 4.7 (governance lineage), with Tony Mason; revised after a four-instance adversarial review (record: `working_notes/2026-05-21-b-recovery-design-adversarial-review.md`). **Speech-act class:** constative (states the cycle's structure) + directive (the four-step plan). **Connects:** the #14 expanded-vintage result (`docs/superpowers/specs/2026-05-18-expanded-vintage-replication-result-note.md`), [[project_silence_manufacture_result]], [[project_pre_registration_pattern]], [[project_saturation_phase_characterization]], [[project_cookbook_adversarial_manual]], [[project_current_anchor]], [[feedback_research_design]], [[feedback_fun_criteria]].

---

## 0. Why this cycle exists, and what the review changed

#14 (expanded-vintage replication) resolved into a clean four-way result: **P3 HIT** (silence-manufacture is FM-substrate-general — 26 cells across crisis / expansion / recovery / COVID, including the designated null vintage) and **P1/P2/P4 all MISS** (no simple discriminator — binary `named_diff` or continuous M-family — is silence-*specific*; they all detect band-reorganization-in-general). In-sample discriminator perfection was 2016Q1 overfitting, exactly as the pre-reg's deliberately-low priors bet.

**Corrected decomposition:** silence = reorganization (Jaccard) ∧ adequacy-flip (`verdict_differs`), with carrier-destination (p3_sat) as a **collinear regime-indexed mechanism** that narrates reorganization, *not* an independent separator. Carrier saturation is flat among reorganized cells (silence 0.87 vs reorg-agreement 0.84), so it does not separate silence from its nearest neighbor; the separator is the adequacy-flip, a predictive-adequacy fact. `verdict_differs` correlates with reorganization (49% among reorg vs 7.6% among no-reorg), so the honest framing is "conjunction of two correlated conjuncts plus a named collinear mechanism," not "orthogonal axes."

**The circularity that defines #15:** the adequacy-flip is `adq_A ≠ adq_B`. Band B recovers adequacy in 50/53 reorganized cells, so the flip is almost entirely "A is inadequate" — making "R²_A predicts the flip" near-tautological. The non-tautological content lives in the **3 cells where B failed to recover.** The load-bearing uncertain quantity is therefore **B-recovery**.

**What the adversarial review changed (v1 → v2).** Four external reviewers converged on: (a) the v1 "predict B-recovery without fitting B" claim was undercut because the population was defined via Jaccard (which needs both bands) — the scientific and deployable questions must be split; (b) at a 90% base rate with 3 failures, accuracy/AUC are the wrong metrics and a 6-predictor classifier is underpowered; (c) the primary output should be a **bounded false-skip risk**, not a trained predictor. v2 adopts all three. The governance tolerance is **not** fixed in the pre-reg — none of the relevant parties (Olorin included) owns the regulatory risk appetite — so v2 reports the bound across a tolerance **sweep** and the operating point at which the verdict flips. Full adjudication: see the review record.

## 1. The arc (four steps)

1. **Close #14** — finalize result note, apply memory deltas, OTS-stamp. (Provenance gate: freeze the result before building on it.)
2. **Parallelize `build_refinement_band`** — joblib, verified by a parity *suite*. (Affordability gate: makes Step 3's held-out cohort affordable.)
3. **#15 B-recovery pre-registration** — the science. **Stamping** depends only on Step 1 (clean provenance) and a commitment to use the parallel tool; **execution** of held-out scoring depends on Step 2's parity suite passing. (Resource dependency, not a stamp-time logical one — per review item 9.)
4. **Scope 4d** — characterize the stress-regime asymmetry mechanism (descriptive, not a classifier). Independent thread; out of #15.

## 2. Step 1 — Close #14

**Result note** (`2026-05-18-expanded-vintage-replication-result-note.md`; retitle PARTIAL → final, scope = 7 vintages):

- Fill P1/P2/P4 — all **MISS** (P1 fresh-cell legs 74% / 44% / 18%; P2 M2_mean silence-only AUC 0.763 vs ≥0.95; P4 M3_max−M1 = +0.020, p=0.66, AUC tie persists at n=171).
- Adversarial: 4a placebo clean (null-AUC>0.95 rate 0.000 — signal real); 4d flags (2009Q1 no-reorg `named_diff` rate 30%, stress-regime-conditioned — feeds Step 4).
- **Corrected decomposition** (reorg ∧ adequacy-flip; carrier collinear regime-indexed mechanism; explicitly not "orthogonal").
- **Detector → signal** reshaping (no silence-specific discriminator; what survives is a placebo-clean reorganization signal of which silence is the regulatorily-salient subset). The line the cookbook's Position 2 cites.
- **Regime-carrier finding** as hypothesis-not-claim (geographic in expansion, institutional/servicer in COVID; regime and vintage collinear at 1–2 vintages/regime, so the regime-conditioned claim is unearnable here — it is what #15 begins to test).
- **Recursive surface-salience note** (methodology silenced findings by undeclared scope-omission; bank policy by feature-omission; a blind reviewer silenced the load-bearing conjunct by surface-salience — same mechanism three levels up). Lives here, **not** in the #15 prereg.

**Memory deltas:** [[project_silence_manufacture_result]] (FM-substrate-general; four-way discriminator falsification; reorg ∧ documented-band-inadequacy decomposition), [[project_saturation_phase_characterization]] (trimodal dead at n=171), [[project_pre_registration_pattern]] (low priors vindicated again), [[project_cookbook_adversarial_manual]] (signal-not-classifier spine; regime-indexed laundering vector), [[project_current_anchor]] (new HEAD; #14 closed; arc → parallelize → #15 → 4d). One commit → auto-OTS-stamp.

## 3. Step 2 — Parallelize `build_refinement_band`

**What:** `wedge/refinement_set.py:142-162` inner loop is embarrassingly parallel (independent CART fits over `(subset, depth, leaf_min)`). `joblib.Parallel(n_jobs=-1)`, expected 50–80×.

**Verification — parity suite (not one vintage):**
- ≥1 vintage per major regime class; both `S_rate` and `S_llpa`; at least one known-reorganization and one no-reorganization cell.
- **Determinism standard, declared up front:** exact equality for discrete outputs and derived labels; explicit numeric tolerance for floats; fixed seeds; recorded library versions. If parallel CART tie-breaking or float-summation order makes bit-identical unachievable, the standard is **label-exact + within-declared-tolerance**, not bit-identical — stated before running, not chosen after.
- Run via `scripts/parity_check_fm_rich_policy.py` (extended to a suite). Optional: a timing benchmark to confirm the speedup.
- **Archive the suite as a durable regression harness** — re-runnable against any future pipeline change, not a one-off gate.

**Why now:** #14 is stamped, so a pipeline change cannot retroactively contaminate it. Durable tool for #15, full-archive characterization, HARP, MFLPD, and every future pre-reg — independent of how #15 resolves.

## 4. Step 3 — #15 B-recovery pre-registration

### 4.1 Two estimands (the central v2 fix)

The scientific question (what is true among cells we can only identify *after* fitting B) is distinct from the deployable question (what we can decide *before* fitting B). Conflating them was v1's error.

- **Q1 — scientific.** Among cells with `reorganized (Jaccard < 0.5) ∧ R²_A < 0.30` (identification requires fitting B), what is the **B-failure rate** `P(R²_B < 0.30)`, and is it stable across regimes? **Treated as descriptive** (rate estimation + regime-stability via the §4.6 LORO non-transport flag), **not** a hypothesis test. Report the distribution of `R²_A` in B-failure vs B-recovery cells — note this is **non-tautological** within the conditioned population (B is a separate fit; the tautology applies only to the *unconditioned* flip-prediction `R²_A → verdict_differs`).
- **Q2 — deployable.** Among A-inadequate cells identifiable **without** fitting B — population `R²_A < 0.30`, features A-side + external metadata only — can an A-only screen decide "skip the B-fit" while keeping the upper confidence bound on **false-skip risk** below a chosen tolerance?

Note Q2's population is **all A-inadequate cells**, broader than `reorg ∧ A-inadequate`, because "reorg" is itself B-defined.

### 4.2 Primary metric and outcome (no fixed tolerance)

**Primary:** false-skip risk = `P(B_fails | screen says skip B)` with an upper confidence bound (binomial / bootstrap), reported **overall, per-regime, and per-LORO-fold**. Recovery is the common event; **failure is the expensive epistemic miss**, so the binary is framed as `B_fails = (R²_B < 0.30)`.

**Operating curve, not a threshold:** report the false-skip-risk bound vs **coverage** (fraction of A-inadequate cells the screen skips), and the **tolerance at which skip-B becomes unsafe**, swept over a declared grid **{1%, 5%, 10%, 20%}**. Decision-relevant anchor: the naive "skip all A-inadequate" rule has in-sample false-skip ≈ 3/29 ≈ 10%. **Coverage is the bank/developer tractability metric** — also report **compute saved (core-hours)** at each coverage level, translating "fraction of cells that skip the B-fit" into the operational quantity that audience actually optimizes.

**Four-state outcome:**
- **(i) targeted instrument** — a cheap A-only screen achieves materially higher coverage than the naive rule at a given tolerance (passes clustered/family-corrected permutation; bound holds in LORO).
- **(ii) skip-B safe wholesale** — the naive full-skip false-skip *upper* bound is below tolerance and LORO-stable.
- **(iii) must fit B** — the false-skip *lower* bound **exceeds** tolerance in some regime/LORO fold (positive evidence of high failure). Maximal epistemic strength, maximal adoption cost — both stated.
- **(iv) inconclusive** — CIs too wide (zero-failure or tiny folds) → report variance estimate and expand corpus. A zero-failure fold yields a wide upper bound (rule-of-three ≈ 3/n) and reads as (iv), **not** (iii) — sample starvation is not regime-variance.

### 4.3 Predictors — exploratory-secondary, bucketed against leakage

Primary inference is the bounded rate (§4.2); predictors are exploratory. Three buckets:

| Bucket | Members | Use |
|---|---|---|
| **Cheap / deployable** | R²_A magnitude, A feature count, A named-features used, stratum, vintage metadata available pre-B | Q2 screen |
| **Oracle / diagnostic** | Jaccard magnitude, p3_sat, B-side carrier destination | Q1 diagnosis only — **never** in the deployable screen |
| **Regime / calendar** | expansion / crisis / recovery / COVID-era | All-regimes-present analysis only; **transport check** under LORO (a categorical regime cannot generalize to an unseen regime, so LORO never tests "regime predicts recovery") |

**Cheap-audit procedure (frozen):** for each deployable predictor, record exactly which artifacts it reads and verify none contain `band_B` coefficients or `R²_B`. **Feature-engineering freeze:** exact encodings (e.g. "A named-features used" = the named-feature set of A's bands; "R²_A residual" = `0.30 − R²_A`) pinned at stamp. **Multiplicity:** the cheap predictors are tested as a **family** with max-statistic permutation (FWER control), not as independent hypotheses.

**Declared naive baseline (= state ii):** "skip all A-inadequate cells." Its held-out false-skip rate = the cost of skipping B wholesale. Prior deliberately low despite 90% in-sample, because high-in-sample is the overfit tell #14 burned us on twice.

### 4.4 Structure: A + LORO, cohort sized by precision

- **Approach A (primary):** freeze the held-out FM vintages **by name**; train any predictors on the #14 7-vintage corpus; estimate the false-skip-risk bound on held-out.
- **Cohort size by precision, not "2 per regime":** to bound a ~10% failure rate tightly you need tens-to-low-hundreds of A-inadequate cells (~4 target cells/vintage in #14 ⇒ ~25 vintages for ~100 cells). Use **all feasible unused FM vintages** post-parallelization, regime-stratified. Pre-register a **precision target** (e.g. upper-CI half-width on the failure rate).
- **LORO (transport/stability check):** train on three regime-classes, estimate the false-skip-risk bound on the withheld fourth. Tests whether the bound *transports*; does not fit regime coefficients.

### 4.5 Adversarial checks and statistics

- **Clustered/blocked permutation:** shuffle `B_fails` within vintage/regime (not cell-level), 10,000 iters, fixed seed; max-statistic across cheap predictors for family-wise control.
- **No-post-hoc-regime-fit guard (hard):** regime enters only as a predictor trained on the #14 corpus and scored on held-out — never by re-partitioning the held-out by observed regime.
- **Adequacy-threshold robustness:** threshold frozen at R² ≥ 0.30 (inherited from #11/#12, **not** tuned for #15 — a provenance feature). Report margins `R²_B − 0.30`, flag near-threshold cells (±0.02, ±0.05), sensitivity at 0.25/0.35, and a minimum-ΔR² variant so a 0.29→0.31 noise-flip need not count as recovery. Sensitivity does **not** redefine success.
- **Statistics:** binomial / bootstrap CIs on the failure rate (overall, per-regime, per-LORO-fold); operating curve with CIs; AUC/accuracy as diagnostics only.

### 4.6 Stamp-time freeze checklist (numeric — no verbal criteria survive to stamp)

Every threshold below is frozen as a number at stamp; none may be set or reinterpreted after held-out data is touched. (Consolidated from the fifth-review "tighten every knob" pass.)

1. **Adequacy threshold:** `R² ≥ 0.30` (frozen, inherited from #11/#12 — not tuned). **Genuine-recovery sensitivity arm:** `R²_B − R²_A ≥ 0.15`. **Near-threshold flag:** report cells within ±0.05 of 0.30.
2. **False-skip-risk bound:** primary = one-sided 95% **Clopper-Pearson (exact binomial) upper bound** (Jeffreys reported as a less-conservative companion). The rule-of-three for zero-failure folds is the Clopper-Pearson zero-event special case, so it is principled, not post-hoc.
3. **Tolerance sweep:** {1%, 5%, 10%, 20%}. **Narration rule:** report the bound at each grid point; do **not** scalarize to a single "safe" tolerance; if the branch verdict differs across the grid, report the crossing tolerance.
4. **"Material coverage" (state i vs ii):** the cheap A-only screen must raise coverage at the operative tolerance by **≥ 10 percentage points** over the naive rule **and** pass family-corrected (max-statistic) permutation. (Margin is a knob — see §6.)
5. **Precision target → cohort size:** target overall false-skip-rate upper-CI half-width **≤ 5 pp**; the held-out vintage count is whatever yields that, computed from per-vintage A-inadequate yield (≈ tens of vintages), **not** "2 per regime."
6. **LORO interpretation:** a fold-bound is **informative** only if the fold has **≥ 30** A-inadequate cells; otherwise it is reported descriptively (state iv). **Non-transport flag:** a fold's false-skip upper bound exceeds the pooled bound by **> 10 pp**, or the fold's lower bound exceeds tolerance (→ state iii).
7. **Predictor freeze:** the cheap/oracle/regime bucket lists are locked at stamp; **no predictor is added after stamp**, even if an "obvious" A-side signal surfaces during implementation.
8. **Regime-class mapping:** an explicit quarter-by-quarter table with a rationale column ("COVID-era starts at X because Y"), frozen at stamp.
9. Held-out vintage list (by name); population + threshold definitions; predictor encodings; precision target; primary estimand (bounded false-skip risk + operating curve).

OTS-stamped **before** held-out band construction touches data. Stamp may precede the Step-2 parity suite; **execution** of held-out scoring may not.

### 4.7 Scope of claim

- **In scope:** substrate-internal FM 30Y conforming corpus, held-out vintages distinct from the #14 seven.
- **NOT in scope:** cross-substrate (HMDA already broke per [[project_hmda_trimodal_result]]; mixing it confounds a B-failure-rate claim); other FM portfolios; modifying band construction (Step 2 parallelization is parity-verified, so not an algorithm change).

### 4.8 Audiences — the operating curve as polymorphic artifact

The #15 pre-reg's audience is the **researcher / scientific record** (rigor-for-the-record; full bounds, CIs, LORO transport). The regulator and bank audiences consume the *result*, not the pre-reg, by reading different axes of the same operating curve — the "one master form, per-buyer denormalized views" pattern of [[project_codification_infrastructure]] / [[project_three_deliverables]]:

- **Regulator** — lower bar on statistical machinery (wants the verdict + the tolerance dial, not Clopper-Pearson), but a *stricter* false-skip tolerance, because a false-skip is a false accusation of manufactured silence with fairness/legal consequence. Sits at the **tight end** of the sweep (1–5%); low coverage acceptable.
- **Bank / bank-software-developer** — metric is **tractability**: coverage = compute saved. Sits at the **loose end** (high coverage), tolerating more false-skip when the label feeds downstream human review.

The curve's value is that it surfaces the **regulator-vs-bank tradeoff** (false-accusation-safety vs compute-tractability) as one explicit, negotiable object instead of hiding it. The pre-reg stays researcher-facing; the regulator-doc and bank-doc views are downstream denormalizations, **not** new pre-reg machinery.

**Goodhart-resistance (and its bound).** Two competing axes (regulator false-skip vs bank coverage, inversely coupled on the curve) plus one validity gate (researcher CIs/transport) cannot be jointly maxed — so there is no single-scalar spike to overfit (contrast #14's discriminator AUC → 1.000, the deceptive proxy-spike). The resistance holds **only while the three are not re-collapsed into one scalar**, which is why the §4.6 no-scalarize narration rule is the Goodhart defense, not just statistical hygiene. **Bound:** this defends the operating-*point* selection, not the upstream codification (which objectives/regimes/corpus are admitted) — Goodhart-resistant at deployment, still gameable at codification ([[project_goodhart_resistance_plural_objectives]], [[project_shap_killer_strategic_seed]]).

## 5. Step 4 — Scope 4d (characterize, do not classify)

`named_diff` fires on 30% of 2009Q1 no-reorg cells — cells that reorganize in feature *name* but not by Jaccard, and are not silence. **Question:** what is the stress-regime asymmetry mechanism, and is it crisis-vintage-specific (2008Q1 + 2009Q1) vs expansion?

- **Deliverable:** a descriptive characterization note (carriers, features, R², vintage-specificity). **Not** a pre-registration; **not** a classifier — engineering a classifier for an uncharacterized mechanism is exactly what P1/P2/P4 did to silence. Characterize first.
- Kept out of #15. Selection rationale: high surprise potential under a uniform prior ([[feedback_fun_criteria]]).
- **Any classifier that later emerges from 4d requires its own pre-registration** — never an add-on to #15. The 30% `named_diff` rate is a characterization target, not a stamped prediction.

## 6. Open knobs (flagged for review)

- **Regime-class boundaries** — must be frozen precisely (which quarters are "COVID-era," expansion/crisis/recovery cutoffs, handling of 2008/2009Q1) before vintage selection.
- **Precision target** for the failure-rate bound — sets the held-out cohort size (§4.4); trades compute (even parallelized) against CI width.
- **Tolerance-sweep grid** — {1,5,10,20%} is a first proposal; the operating point itself is *not* ours to fix (it is reported, then chosen downstream).
- **Predictor encodings** — pinned at stamp per §4.3; the cheap-bucket membership is the leakage-critical decision.

## 7. Revision log

- **v1 → v2 (2026-05-21):** spine changed from "predict B-recovery (classifier) without fitting B" to "estimate the bounded false-skip risk; two estimands (scientific Q1 / deployable Q2); operating-curve sweep instead of a fixed tolerance; predictors demoted to exploratory family-corrected; cohort sized by precision; four-state outcome with an explicit INCONCLUSIVE state." Driven by a four-instance adversarial review (ChatGPT / Gemini / Grok / Kimi); full adjudication in `working_notes/2026-05-21-b-recovery-design-adversarial-review.md`.
- **v2 → v2.1 (2026-05-21):** no spine change (a fifth review endorsed the spine). Converted verbal criteria to the numeric §4.6 stamp-time freeze checklist (Clopper-Pearson upper bound, tolerance-narration rule, material-coverage margin, precision half-width, LORO informativeness/non-transport thresholds, predictor-no-additions, regime quarter-table); Q1 declared descriptive; parity suite archived as a regression harness; 4d-classifier requires its own pre-reg. Two reviewer suggestions **declined** (see §8).
- **v2.1 → v2.2 (2026-05-21):** added §4.8 (three-audience framing — the operating curve as polymorphic artifact; regulator at the tight tolerance end, bank/dev at the high-coverage end; the curve surfaces the regulator-vs-bank tradeoff) and compute-saved as a reported quantity. No spine or estimand change.

## 8. Declined reviewer suggestions

- **"Commit in the pre-reg to recommending full B-fits in must-fit-B regimes."** Declined for the #15 pre-reg: it reports *which branch fires* (a scientific verdict); the deployment recommendation ("don't cut corners") belongs to the downstream deployment / regulator-facing artifact, not the pre-reg. Keeping them separate preserves the science/governance split the reviewers otherwise praised.
- **"Report how much of Q1's R²_A signal is tautological."** Reframed rather than adopted as stated: within the conditioned population (`reorg ∧ A-inadequate`), `R²_A → B-recovery` is *not* tautological — B is an independent fit. The tautology applies only to the unconditioned `R²_A → verdict_differs`. §4.1 reports the distribution with the caveat scoped correctly.

## 9. Provenance

Design emerged from the post-#14 exchange (2026-05-20 → 2026-05-21): the four-way result, the carrier-membership reframe (proposed blind, tested and corrected against the data — carrier is collinear, not the separator), the B-recovery circularity diagnosis, the reviewing instances' corrections, and the four-instance adversarial review of v1. No held-out FM data outside the #14 seven has been touched at design time.
