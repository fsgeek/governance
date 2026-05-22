# B-recovery: bounded false-skip risk for skipping the band-B fit — pre-registration (#15)

**Date:** 2026-05-21 (drafted); 2026-05-22 (revised after six-instance external review). **Status:** PRE-REGISTRATION (DRAFT — not yet OTS-stamped; predictions freeze at the stamp). **Artifact class:** **internal governance-research-lineage pre-registration.** The `[[project_*]]` cross-references are load-bearing internal context; the OTS stamp's promise is *internal* freeze discipline (Git + OpenTimestamps provenance), not OSF-style external release. A reader outside the lineage needs the design doc + the linked memories to fully reconstruct the motivation; the experimental contract below is self-contained.

**Substrate:** Fannie Mae Single-Family Loan Performance, 30Y conforming. The full corpus (104 quarterly vintages, 2000Q1–2025Q4) is on disk via `data/fanniemae` → `/mnt/d/governance-data/Performance_All`. The #14 seven (2008Q1/2009Q1/2012Q1/2014Q3/2016Q1/2018Q1/2020Q2) are peek-tainted; the held-out vintages frozen in §2b are committed to before any band-construction code runs on them. **Design:** `docs/superpowers/specs/2026-05-21-b-recovery-cycle-design.md` (v2.2). **Companion to:** the #14 result note, `[[project_silence_manufacture_result]]`, `[[project_pre_registration_pattern]]`, `[[project_saturation_phase_characterization]]`. **Connects:** `[[project_goodhart_resistance_plural_objectives]]`, `[[project_shap_killer_strategic_seed]]`, `[[project_codification_infrastructure]]`, `[[project_three_deliverables]]`, `[[feedback_research_design]]`.

**Pre-registration discipline.** Inspected (peek-tainted): the #14 7-vintage corpus (n=171 in-scope cells), its per-cell `R²_A`/`R²_B`/Jaccard/reorganization labels, the in-sample false-skip anchors (§3), and the screen-threshold fit (§3.1). NOT inspected: any FM data outside the #14 seven, including held-out per-vintage volume/yield. **Held-out construction provenance (§2a/§2b):** regime boundaries are drawn from public macroeconomic chronology (NBER recession dating, Fed-funds regime, GSE program history) — not from any FM performance data; within-regime quarter choices follow a fixed rotation pattern (spread across each regime's years), made without reference to any held-out outcome, volume, or yield proxy beyond confirming the CSV/parquet exists on disk. The OTS stamp freezes: the held-out vintage list, the regime→quarter table, the seasoning rule, all population/threshold definitions, the **two frozen primary screen rules and their thresholds**, the **both-strata** run requirement, the predictor buckets and encodings, the precision target, and the primary estimand. **The stamp may precede the Task-2 parity suite and the §2b parquet build; execution of held-out scoring may not.**

**Honesty about peek-taint.** This pre-reg's author has read the #14 corpus and computed its in-sample B-failure rates and the screen threshold (§3.1). In-sample numbers are reported *as anchors*, not predictions; §3's outcome priors are calibrated against `[[project_pre_registration_pattern]]`, not against the in-sample fit. Per that pattern, clean in-sample structure is the overfit tell this cycle exists to test — and §3.1 shows the screen is in fact *weak* in-sample, which pre-justifies the low state-(i) prior. The bound is conservative (one-sided CP) precisely because the screen was fit on peeked data.

---

## 0. Key concepts (glossary)

- **band A / band B** — the policy-constrained Rashomon refinement bands. Band A uses the documented 4-feature named-policy vocabulary; band B additionally admits extension features. `R²_A`, `R²_B` are their cross-validated predictive fits. *(Taken as given from #11/#12; see §8 on the band-partition assumption.)*
- **adequacy** — `R² ≥ 0.30`. A band is "adequate" if it predicts at threshold. **adequacy-flip** = `adq_A ≠ adq_B` (A inadequate, B adequate, in the common case).
- **reorganized** — `jaccard_primary < 0.5`: band B's used-feature set overlaps band A's by less than half (Jaccard on used-feature sets, primary band selection per `fm_rich_policy_vocab_adequacy_test` at the frozen commit). Reorganization is **B-defined** (needs both bands), so it is unavailable to a pre-B screen.
- **manufactured silence** — a reorganized ∧ adequacy-flip cell: the documented policy vocabulary is inadequate where a richer model is adequate, so the policy "is silent" on a determinable distinction. The #14 phenomenon.
- **B-recovery / B-failure** — `B_fails = (R²_B < 0.30)`: band B fails to reach adequacy. The load-bearing uncertain quantity (§1).
- **false-skip** — the screen says "skip the band-B fit" on a cell where `B_fails`. The expensive epistemic miss.

## 1. Question

#14 resolved silence-manufacture into **reorganization ∧ adequacy-flip**, with carrier-saturation a collinear regime-indexed *narration* of reorganization, not an independent separator (P1/P2/P4 MISS; P3 HIT — silence is FM-substrate-general). The adequacy-flip is `adq_A ≠ adq_B`; band B recovers adequacy in 50/53 reorganized cells, so the flip is almost entirely "A is inadequate" — making "R²_A predicts the flip" near-tautological on the *unconditioned* population. **The non-tautological content lives in the cells where B failed to recover**, and the deployable question is whether we can skip the expensive band-B fit without missing those failures.

Two estimands, deliberately split (the central v2 fix):

- **Q1 — scientific (descriptive).** Among `reorganized (Jaccard < 0.5) ∧ R²_A < 0.30` cells (identification requires fitting B), what is `P(R²_B < 0.30)`, and is it stable across regimes? Rate estimation + transport, **not** a hypothesis test. The `R²_A` distribution in B-failure vs B-recovery cells is non-tautological *within this conditioned population* (B is an independent fit; the tautology applies only to the unconditioned `R²_A → verdict_differs`).
- **Q2 — deployable.** Among A-inadequate cells identifiable **without** fitting B (population `R²_A < 0.30`; predictors A-side + external metadata only), can a frozen A-only screen decide "skip the B-fit" while keeping the **upper confidence bound on false-skip risk** below tolerance? Q2's population is **all A-inadequate cells**, broader than Q1's, because "reorganized" is B-defined.

## 2. Operational definitions

### 2a. Regime → quarter table (FROZEN)

Six macro-coherent classes spanning the held-out corpus, each a contiguous block with one dominant rate/credit regime, drawn from **public macro chronology** (see provenance note above). **Frozen at stamp; regime never enters by re-partitioning observed held-out data (§6 guard).**

| Regime class | Quarters | Rationale |
|---|---|---|
| **early-cycle** | 2000Q1 – 2006Q4 | Pre-GFC: dot-com recession, 2002–03 refi boom, 2004–06 housing-credit expansion. Unrepresented in #14. |
| **crisis** | 2007Q1 – 2009Q4 | Housing peak → subprime onset (2007) → GFC. Stress regime; 2007 = crisis-onset. |
| **recovery** | 2010Q1 – 2013Q4 | Post-GFC trough, HARP era, tight credit + slow recovery. |
| **expansion** | 2014Q1 – 2019Q4 | Long expansion; gradual rate normalization 2017–18. |
| **COVID** | 2020Q1 – 2021Q4 | Pandemic shock, ZIRP, refi surge, forbearance. |
| **post-COVID tightening** | 2022Q1 – 2025Q4 | Fed hiking, rate shock, collapsed origination volume. Unrepresented in #14. |

The #14 seven span only four of six classes; **early-cycle and post-COVID are absent from #14** — held-out coverage of them is the strongest transport test.

**Boundary-interpretation caveat.** Boundaries are economic-narrative-coherent but sharp where reality is gradual (2007 as crisis-onset; 2010 as recovery). A non-transport flag (§5) is therefore interpreted strictly as "the bound does not transport across **these frozen boundaries**," *not* as proof the regime is intrinsically different. Whether a flag reflects a genuine regime difference vs. a mis-drawn boundary is a **separate future pre-reg**; re-drawing boundaries post-hoc on this data is forbidden.

### 2b. Held-out vintage list (FROZEN)

42 vintages, **disjoint from the #14 seven**, **7 per regime class** (see equal-count rationale below), all **seasoned** per §2c, spread by fixed quarter-rotation.

| Regime class | Held-out vintages (7 each) |
|---|---|
| early-cycle | 2000Q1, 2001Q2, 2002Q3, 2003Q4, 2004Q2, 2005Q3, 2006Q4 |
| crisis | 2007Q1, 2007Q3, 2008Q2, 2008Q3, 2008Q4, 2009Q2, 2009Q4 |
| recovery | 2010Q1, 2010Q3, 2011Q1, 2011Q3, 2012Q3, 2013Q1, 2013Q3 |
| expansion | 2014Q1, 2015Q1, 2015Q3, 2016Q3, 2017Q1, 2017Q3, 2019Q1 |
| COVID | 2020Q1, 2020Q3, 2020Q4, 2021Q1, 2021Q2, 2021Q3, 2021Q4 |
| post-COVID tightening | 2022Q1, 2022Q2, 2022Q3, 2022Q4, 2023Q1, 2023Q3, 2023Q4 |

**Equal-count rationale (frozen design choice):** 7-per-regime gives **equal statistical leverage per regime for the transport (LORO) test**, which is a *per-regime* claim — calendar duration is irrelevant to it, so proportional-to-duration sampling is not used. Consequence: short regimes (COVID, 7/8 quarters) are near-exhaustively sampled while long regimes (early-cycle, 7/28) are sparse in calendar terms. This is intentional and is **not** a calendar-representativeness claim. **Cell count is endogenous** to macro conditions and volume (not controlled), so realized A-inadequate cells per regime will vary; the realized count governs the bound (§5).

**post-COVID restriction.** Only 2022–2023 vintages enter (all ≥24-month-seasoned as of the 2026-05 snapshot); 2024–2025 quarters are **excluded for want of a full 24-month horizon** (§2c) and enter only a future re-run when seasoned — a literal instance of transport-not-coverage (§8): we do not claim a regime-tail we cannot yet measure.

**Substitution rule (frozen):** a vintage is substituted **only** on a documented non-recoverable parquet-build error (schema mismatch, corruption) — **never** for low yield. Substitute = the next-closest **seasoned, unused, non-#14** vintage by quarter-distance within the same regime class; ties broken **earlier-quarter-first**. Logged in the result note.

**No post-hoc vintage addition (hard freeze):** the 42 are the cohort. **We will not add vintages to recover precision** after seeing held-out yield. If realized yield is low, the bound is reported at realized precision (state iv where folds starve); it is not retrofitted.

### 2c. Populations, labels, thresholds, seasoning (FROZEN)

- **Adequacy threshold** `R² ≥ 0.30`, inherited unchanged from #11/#12 — **not tuned for #15** (provenance feature).
- **In-scope cell** = the inclusion criterion in `fm_rich_policy_vocab_adequacy_test.py::usable_features`/`prep` (≥ `MIN_CELL_LOANS`, decile-stratum eligibility) at the **frozen commit hash recorded at stamp**. Not redefined here.
- **Edge handling:** comparisons are strict — `R²_A < 0.30` for A-inadequate; `B_fails = (R²_B < 0.30)`. A cell at exactly `R² = 0.30` is **adequate** (not inadequate; not a B-fail). Cells within ±0.05 of 0.30 are flagged near-threshold and reported.
- **Q2 population** = all in-scope `R²_A < 0.30`. **Q1 population** = Q2 ∩ `reorganized`.
- **Outcome label** `B_fails = (R²_B < 0.30)`. Single definition everywhere. **Cells weighted equally** (not volume-weighted); cell is the unit.
- **Genuine-recovery sensitivity arm (separate, secondary):** `B_genuine_recovers = (R²_B ≥ 0.30) ∧ (R²_B − R²_A ≥ 0.15)`; `B_genuine_fails = ¬B_genuine_recovers`. Produces a **second** false-skip table in an appendix; does **not** enter the primary four-state outcome and does **not** redefine the primary `B_fails` label.
- **Adequacy-threshold robustness (0.25 / 0.35):** at each sensitivity threshold, **both** the population (`R²_A < thresh`) **and** the label (`R²_B < thresh`) are recomputed. Reported as sensitivity; primary stays 0.30.
- **Seasoning rule (FROZEN):** `horizon_months = 24` (the #14 standard). A vintage is included **only if** originated ≥ 24 months before the data snapshot (2026-05), so every cell has a complete 24-month performance window. Unseasoned vintages are excluded and substituted per §2b. (This is why post-COVID stops at 2023.)

### 2d. Pipeline (parity-verified parallel; no math change)

For each held-out vintage, **strict serial across vintages** (FM-load discipline — `fm_rich_policy_vocab_adequacy_test.py` module docstring, "STRICTLY SERIAL"; per-vintage load peaks at tens of GB):

1. Convert CSV→parquet if absent (`scripts/convert_fm_csv_to_parquet.py`; chunked; built Windows-native).
2. `PYTHONPATH=. python scripts/fm_rich_policy_vocab_adequacy_test_parallel.py --vintage <V>` — the Task-2 parallelized band construction. **Both strata (`S_rate` ∪ `S_llpa`) are run for every held-out vintage (FROZEN).** This is load-bearing for yield: the cell grid is 10 `S_rate` (rate-band) + 49 `S_llpa` (LLPA-grid) = 59 cells/vintage, and the A-inadequate yield concentrates in `S_llpa` (in #14: 35% A-inadequate vs `S_rate`'s 11%). Three of the #14 seven (2008Q1/2016Q1/2018Q1) were run `S_rate`-only, which structurally halved their yield; the held-out runs must **not** replicate that — both strata, always.
3. `scripts/silence_manufacture_test.py` (held-out-scoped) — per-cell `R²_A`, `R²_B`, Jaccard, reorganization, stratum, regime.

**Parity standard (frozen, before any held-out scoring):** on the #14 seven, the parallel pipeline must reproduce all **discrete outputs bit-identically** — reorganization labels, adequacy labels, `B_fails`, and used-feature sets — and all **floats within ε = 1e-9**. **Any discrete-label flip = parity FAILURE**, not "within tolerance" (this matters because float-reduction-order roundoff would concentrate exactly at the 0.30 boundary, where the near-threshold population lives). **Post-stamp patch rule:** if a label-affecting patch to the pipeline is needed after the stamp, it requires a **new OTS-stamped commit** (re-running parity) before held-out scoring resumes. Orchestration-only changes (no math) are documented with the patch hash in the result note.

## 3. Primary estimand and outcome

**Primary metric:** false-skip risk = `P(B_fails | screen says skip B)`, with a **one-sided 95% Clopper-Pearson (exact binomial) upper bound** (Jeffreys companion). **Clustering companion:** because B-fails may cluster by vintage/regime (the cell-level binomial assumes independence), also report a **vintage-block bootstrap** upper bound (resample vintages with replacement, 10,000 iters, seed 20260521). The primary claim is stated as a **cell-level bound conditional on the 42-vintage sample**; if the block-bootstrap bound is materially wider than CP, the **block-bootstrap bound is treated as the transport-relevant bound.**

**Operating curve, not a threshold.** Report the false-skip upper bound vs **coverage** (fraction of A-inadequate cells skipped) and vs **compute saved**, swept over **{1%, 5%, 10%, 20%}**. **Compute saved (frozen def):** `(mean measured wall-core-hours of one band-B fit over the #14 seven) × (number of skipped cells)`; the per-fit cost is logged during the #14-corpus re-measurement and frozen at stamp. **No-scalarize narration rule (frozen):** report the bound at every grid point; do not collapse to one "safe" tolerance. **Presentation-order freeze:** the result note **leads with the 10% grid point**, then reports 1/5/20% — never leads with the most favorable point. (This converts author-discipline into a stamp-time freeze; it is the Goodhart defense of §9.)

### 3.1 The two frozen primary screens (resolves the "screen not pre-specified" gap)

Both deployable screens are pre-specified univariate rules of the form **skip the band-B fit ⟺ `c ≤ R²_A < 0.30`** (skip the *near-adequate* A-inadequate cells; fit B on the deeply-inadequate ones). Two cutpoints are frozen, each **mechanically defined from #14** (no hand-picking) and **fit on the peek-tainted #14 corpus only**; held-out data **evaluates these fixed rules**, never re-selects them:

| Screen | Definition (on #14) | Cutpoint | In-sample (44 A-inadequate) | Audience end |
|---|---|---|---|---|
| **screen-tight** | smallest `c` with in-sample false-skip ≤ **10%** | **`c = 0.22`** | skips 15 (34% cov), 1 false-skip (6.7%) | regulator (low false-accusation), evaluated **pooled** |
| **screen-loose** | smallest `c` with in-sample false-skip ≤ **15%** | **`c = 0.185`** | skips 20 (45% cov), 3 false-skip (15%) | bank/developer (high coverage); 45% cov ≈ 31 skipped/regime → **populates per-regime folds** |

**No screen-functional-form degrees of freedom remain:** model class (univariate threshold), predictor (`R²_A`), and both cutpoints (0.22, 0.185) are frozen. The two screens are the regulator/bank ends of §9's operating curve.

**The screen is non-monotonic in `c` — itself a #14 finding (disclosed):** false-skip is *worse than naive* for `c < 0.16` (e.g. `c=0.10`: 68% coverage but 23.3% false-skip > naive's 20.5%), because the deeply-inadequate (low-`R²_A`) cells are **not** the B-fail-heavy ones — B-fails are spread across `R²_A ∈ [0.018, 0.228]`. A screen only beats naive by being conservative (`c ≥ 0.185`). This non-monotonicity is exactly why the state-(i) prior is low (§3.3) and why a higher-coverage third point (`c=0.10`) is **excluded as dominated**.

**Multiplicity across screens:** two frozen screens × the tolerance grid are tested as one family; the family-wise (max-statistic) permutation correction (§6) spans both screens, so reporting "the better of two" is not free.

The cheap-predictor **family** (§4) remains **exploratory-secondary**: candidate *future* screens, reported with family-corrected permutation, **not** the state-(i) adjudication. State (i) is decided on the two frozen rules above.

### 3.2 Outcome (tolerance-indexed four states)

For each τ ∈ {1%, 5%, 10%, 20%}, report `state(τ)`; if states differ across τ, report the **crossing tolerance** and do not emit a single global state.

- **(i) targeted instrument** — the naive full-skip rule **fails** τ (its false-skip upper bound > τ), **but** at least one of the two frozen screens (§3.1) achieves false-skip upper bound **≤ τ** while skipping **≥ 10%** of A-inadequate cells (and ≥ 30 skipped cells for informativeness), is LORO-stable, and survives the family-wise (max-statistic) permutation gate spanning **both screens** × the tolerance grid (§6). Report which screen and which τ.
- **(ii) skip-B safe wholesale** — the naive full-skip false-skip *upper* bound is **≤ τ** and LORO-stable. (If naive passes τ, classify as ii, not i.)
- **(iii) must fit B** — the false-skip *lower* bound (one-sided 95% CP, same denominator) **exceeds τ** in some regime/LORO fold. Maximal epistemic strength, maximal adoption cost.
- **(iv) inconclusive** — the relevant denominator has **< 30** cells (skipped cells for the screen bound; A-inadequate cells for the naive bound), or CIs are otherwise too wide. A zero-failure fold reads as **(iv), not (iii)** — sample starvation ≠ regime-variance.

**Pooled vs. per-regime deployment (Gemini's question, made explicit).** The **pooled** bound is a substrate-level scientific summary; it does **not** license deployment to a regime whose own fold is state (iv). Per transport-not-coverage (§8), an instrument is deployable to regime R only if **R's fold** clears the bar — so if post-COVID starves to state (iv), skip-B is **not** authorized for 2022–2025 on the strength of the pooled bound; that regime waits for a seasoned, populated re-run. The pooled bound carries the *scientific* verdict forward; it does not carry the *deployment* license across an unmeasured regime.

### 3.3 Outcome priors (genuine predictions; calibrated vs `[[project_pre_registration_pattern]]`)

Marginal predictions (sufficient for the calibration corpus; a full joint table is not pre-registered — see note):
- P(state i at τ=10% — either frozen screen beats naive, safe, ≥10% coverage): **0.20.** Lowered from the draft's 0.25 after §3.1 showed the screens are in-sample-weak and non-monotonic; #14 burned us twice on clean-in-sample discriminators.
- P(pooled Q2 naive false-skip upper bound ≤ 10%): **0.30.** In-sample point ~20%; the upper bound is more conservative.
- P(≥ 1 regime fold flags state iii at τ=10%): **0.45.** Crisis-adjacent and unseen post-COVID rate-shock are where genuine B-failure should concentrate.
- **Implied P(iv)-heavy:** at least one fold (early-cycle or post-COVID) lands in state (iv) for want of ≥30 skipped/A-inadequate cells — treated as **likely** (>0.6), diagnostic not graded, because OOD yields are unknown.

## 4. Predictors — exploratory-secondary, bucketed against leakage

Primary inference is the bounded rate on the two frozen screens (§3.1); these are **exploratory candidate future screens**, reported as a family. **Frozen at stamp; no predictor added after stamp.**

| Bucket | Members | Use |
|---|---|---|
| **Cheap / deployable** | `R²_A` magnitude; `R²_A` residual (`0.30 − R²_A`); A feature **count** (cardinality of A's used-feature set); A named-features-used **binary vector** over the frozen 4-feature policy vocabulary; **stratum** (= the #11/#12 `S_rate`/`S_llpa` label, pinned to the frozen commit) | exploratory Q2 screens |
| **Oracle / diagnostic** | Jaccard magnitude; `prohibited_3` (carrier) saturation; B-side carrier destination | Q1 diagnosis only — **never** deployable |
| **Regime / calendar** | the six §2a classes | **reporting/stratification only — NOT in any deployable screen** (a categorical regime has no learned effect for an unseen regime; including it would leak/over-claim). LORO transport uses regime only to partition, never as a fitted predictor. |

**Encodings frozen:** "A named-features-used" = binary indicator vector over the 4 named policy features; "A feature count" = its cardinality; "`R²_A` residual" = `0.30 − R²_A`; "stratum" = `S_rate`/`S_llpa` at the frozen commit. **Cheap-audit (frozen, documented in result note):** for each deployable predictor, record the exact list of artifact fields it reads and verify none contain `band_B` coefficients or `R²_B`. **Any audit violation voids the deployable claim for that predictor.** **Multiplicity:** the family is tested with max-statistic permutation (FWER), not as independent hypotheses.

## 5. Structure: held-out + LORO, sized by precision

- **Primary held-out evaluation:** the **fixed #14-trained screen (§3.1)** evaluated on all 42 held-out vintages; the false-skip bound is computed on the realized skipped cells.
- **LORO (secondary transport diagnostic):** evaluate the **same fixed screen** separately on each withheld regime class (6 folds). **No refit** — there is no per-fold training step, so unseen regimes (early-cycle, post-COVID) are handled without needing #14 data that does not exist. LORO tests whether the bound *transports*; it does not fit regime coefficients.
- **Tiered precision target (FROZEN, planning quantity not success criterion):** **pooled** — `(CP upper bound) − (point estimate) ≤ 5 pp`; **per-regime/fold** — same quantity ≤ 10 pp, **aspirational/descriptive** (folds below the informativeness floor enter state iv; they are not "failures"). "Half-width" is replaced by this explicit one-sided definition.
- **Cohort-size derivation:** at the in-sample Q2 rate p ≈ 0.205, ≤5pp needs ≈ 245 cells under normal approx; exact CP is wider (the CP upper sits ~6–7pp above the point at n≈250), so ≈ 250–300 is the planning target. **Both-strata** #14 vintages yielded ~10 A-inadequate/vintage (range 4–21; the `S_rate`-only vintages' ~3 is a run-config artifact, §2d) ⇒ 42 vintages ≈ ~280 A-inadequate pooled — on target. **Realized yield (cell count, and the rate p itself) governs the actual bound; the precision target is a planning assumption, not a success gate, and no vintages are added post-hoc (§2b).** If realized p falls outside ≈[0.10, 0.30], the half-width assumption breaks and the result is reported at realized precision (state iv per starved fold).
- **Per-regime fold power (consequence of the 59-cell grid cap):** 7 both-strata vintages/regime ≈ ~70 A-inadequate. The **naive** per-regime bound (floor: ≥30 A-inadequate) is reachable in ~5 of 6 regimes; **screen-loose** (45% cov → ~31 skipped) **just** clears the ≥30-skipped floor in average/high-volume regimes; **screen-tight** (34% cov → ~24 skipped) mostly does **not** per-regime and is evaluated **pooled** (42 vintages → ~95 skipped, well-powered). **post-COVID tightening (2022–23, collapsed origination volume) is the regime most likely to starve to state (iv)** for all bounds — already its OOD status. The screen's transport story is therefore primarily *pooled* + screen-loose-per-regime; the naive transport story is per-regime.
- **Informativeness floor:** a bound is informative only if its denominator has **≥ 30 cells** — **skipped cells** for a screen bound, **A-inadequate cells** for the naive/wholesale bound. **Non-transport flag:** a fold's false-skip upper bound exceeds the pooled bound by **> 10 pp**, or the fold's lower bound exceeds τ (→ state iii).

## 6. Adversarial checks and statistics

- **Clustered/blocked permutation (PRIMARY FWER gate):** shuffle `B_fails` within vintage/regime (not cell-level), 10,000 iters, seed 20260521; max-statistic across the cheap family. This is the gate for the exploratory family and the §3.2 state-(i) companion check.
- **Placebo (label-shuffle null, DIAGNOSTIC only):** permute `B_fails` uniformly across held-out (same seed); verify no cheap predictor reaches its observed family-max at rate > 5% under the null. Reported as a sanity check, **not** the gate.
- **No-post-hoc-regime-fit guard (hard):** regime enters only as a §2a-frozen partition for LORO/reporting — never by re-partitioning observed held-out, never as a fitted deployable predictor, never by redefining boundaries after a non-transport flag.
- **Adequacy-threshold robustness:** margins `R²_B − 0.30` reported; near-threshold ±0.05 flagged; sensitivity at 0.25/0.35 (population **and** label recomputed); genuine-recovery arm (§2c). Sensitivity never redefines primary success.
- **Statistics:** CP one-sided 95% **upper** bound (primary) + Jeffreys companion + vintage-block bootstrap (clustering companion); CP one-sided 95% **lower** bound for state (iii), same denominator. AUC/accuracy diagnostic only (wrong primary metric at an ~80–90% recovery base rate — the v2 fix).

## 7. Stamp-time freeze checklist (numeric)

1. **Adequacy** `R² ≥ 0.30` (inherited, not tuned); genuine-recovery arm `R²_B − R²_A ≥ 0.15`; near-threshold ±0.05; edge = strict `<`.
2. **Bounds:** false-skip = one-sided 95% **CP upper** (Jeffreys + vintage-block-bootstrap companions); state (iii) = one-sided 95% **CP lower**; rule reported as the CP zero-event bound for zero-failure folds (not the 3/n approximation).
3. **Tolerance sweep** {1,5,10,20%}; no-scalarize; result note **leads with 10%**; report crossing tolerance if `state(τ)` differs.
4. **Two frozen primary screens:** screen-tight `c=0.22` (smallest #14 c with fsr ≤ 10%) and screen-loose `c=0.185` (smallest #14 c with fsr ≤ 15%), both `c ≤ R²_A < 0.30`; fit on #14 only; held-out evaluates the fixed rules; `c=0.10` excluded as dominated. **state (i)** requires: naive fails τ ∧ ≥1 screen's upper ≤ τ ∧ that screen's coverage ≥ 10% of A-inadequate ∧ ≥ 30 skipped cells ∧ LORO-stable ∧ family-wise (both-screens × grid) permutation pass.
5. **Precision (planning):** pooled `CP-upper − point ≤ 5pp`; per-fold ≤ 10pp aspirational; cohort = 42 (§2b); **no post-hoc vintage addition**.
6. **Informativeness:** ≥ 30 cells in the relevant denominator (skipped for screen, A-inadequate for naive); non-transport at > 10pp over pooled, or fold lower bound > τ.
7. **Predictors:** cheap/oracle/regime buckets + encodings locked (§4); regime not in any deployable screen; **no predictor added after stamp**; cheap-audit documented; violation voids that predictor's claim.
8. **Regime map:** the §2a six-class table; **seasoning** `horizon=24mo`, vintage seasoned ≥24mo before 2026-05. **Both strata** (`S_rate` ∪ `S_llpa`) run for every held-out vintage (§2d).
9. **Held-out:** the §2b 42 (by name) + substitution rule (build-error only, earlier-quarter-first tie-break); populations/thresholds (§2c); compute-saved def (§3); parity standard + post-stamp-patch-needs-new-OTS (§2d); primary estimand = bounded false-skip + operating curve.

Parity suite passes **before** held-out scoring; OTS stamp **before** held-out band construction touches data.

## 8. Scope of claim — transport, not coverage

The claim is a false-skip *bound that transports across regimes*, **not** a vintage tally. Coverage is a game lost by construction (always an N+1; a coverage claim is an implicit, unfalsifiable universality claim). Under transport, an unseen vintage is another draw from a characterized regime, and the honest output is "transports to its regime (covered)" or "non-transport flag." The strongest evidence we are not over-claiming universality is a **demonstrated non-transport case** — HMDA broke the trimodal claim cross-substrate (`[[project_hmda_trimodal_result]]`). A method that can *show where it stops generalizing* answers "but the (N+1)th dataset" better than one that claims it never stops. The receipt is the transport boundary, not the coverage count.

- **In scope:** substrate-internal FM 30Y conforming; held-out disjoint from the #14 seven (§2b); only ≥24mo-seasoned vintages.
- **NOT in scope:** cross-substrate (HMDA already broke; mixing confounds the rate); other FM portfolios (no alt-doc, jumbo, MFLPD); modifying band construction (the §2d parallelization is parity-verified, hence not an algorithm change); **performance on future vintages outside the characterized regimes or on non-30Y-conforming products** (no claim made); the **band-A/B partition itself** — taken as given from #11/#12. *If* the partition were an artifact of construction, B-recovery would be a question about an artifact; that upstream assumption is named here as out-of-scope for #15 and a candidate for separate falsification.
- **Narrow form:** "On 42 FM vintages spanning six rate/credit regimes 2000–2023[seasoned], the false-skip risk of skipping band-B under frozen screen [tight/loose] is bounded at [X]% (95% CP upper, cell-level conditional on this sample), and [transports / does not transport] to regime R." Not "skipping B is universally safe."

## 9. Audiences — the operating curve as polymorphic artifact

Audience of *this pre-reg* = researcher/scientific record. Regulator and bank consume the *result* by reading different axes of the same operating curve (the "one master form, per-buyer denormalized views" pattern of `[[project_codification_infrastructure]]` / `[[project_three_deliverables]]`):

- **Regulator** — lower bar on statistical machinery, *stricter* false-skip tolerance (a false-skip is a false accusation of manufactured silence, with fairness/legal consequence); sits at the tight end (1–5%), low coverage acceptable. **Consumes screen-tight (`c=0.22`, §3.1).**
- **Bank / developer** — metric is tractability: coverage = compute saved; sits at the loose end (high coverage), tolerating more false-skip when the label feeds downstream human review. **Consumes screen-loose (`c=0.185`, §3.1).**

The curve surfaces the **regulator-vs-bank tradeoff** as one explicit, negotiable object.

**Goodhart-resistance (and bound).** Two competing axes (regulator false-skip vs bank coverage, inversely coupled) + one validity gate (researcher CIs/transport) cannot be jointly maxed — no single-scalar spike to overfit (contrast #14's AUC→1.000 proxy-spike). Resistance holds **only while the three are not re-collapsed into one scalar** — hence the §3 no-scalarize + lead-with-10% freeze is the Goodhart defense, not just hygiene. **Codification attack surface (named):** this defends operating-*point* selection, not codification. The codification decisions **inherited (not gameable by this author for #15)**: the adequacy threshold 0.30, the 4-feature policy vocabulary, the band-A/B construction, the in-scope criterion (all from #11/#12/#14). The codification decisions **new in #15 (the author's degrees of freedom, hence the freezes above)**: the regime table, the held-out list, the screen threshold, the predictor buckets, the tolerance grid. Goodhart-resistant at deployment, still gameable at codification (`[[project_goodhart_resistance_plural_objectives]]`, `[[project_shap_killer_strategic_seed]]`).

## 10. Followups (terminal four-state; not a pre-determined chain)

- **(i)** deployable instrument → bank-facing artifact gets the skip-rule + bounded risk; next pre-reg cross-substrate-tests it (subject to HMDA's transport break).
- **(ii)** wholesale-safe in-substrate → feeds SHAP-killer Line A compute-tractability; regulator artifact reports the tight-tolerance bound.
- **(iii)** must-fit-B in some regime → strongest scientific result; the deployment recommendation lives downstream, not here.
- **(iv)** inconclusive folds → report variance; followup is corpus expansion within the starved regime (own trivial precision pre-reg) once seasoned.

## Declined reviewer suggestions

- **"Commit to recommending full B-fits in must-fit-B regimes."** Declined: this pre-reg reports *which branch fires*; the deployment recommendation belongs downstream (science/governance split).
- **"Report how much of Q1's R²_A signal is tautological."** Reframed: within `reorg ∧ A-inadequate`, `R²_A → B-recovery` is not tautological (B is an independent fit); the tautology is only on the unconditioned `R²_A → verdict_differs`.
- **"Sample regimes proportional to calendar duration"** (review pass 2). Declined: equal-count is intentional for per-regime transport leverage (§2b); calendar-representativeness is explicitly not the claim.
- **"Pre-register a full joint prior decomposition over 4 states × 4 tolerances."** Declined as over-engineering: marginal priors (§3.3) suffice for the calibration corpus; the implied P(iv)-heavy note covers the dependence qualitatively.

## Provenance

Design from the post-#14 exchange (2026-05-20 → 21): the four-way result, the carrier-membership reframe (proposed blind, tested and corrected — carrier is collinear, not the separator), the B-recovery circularity diagnosis, a four-instance adversarial review of v1. The §2a six-class regime table and §2b 42-vintage held-out list extend the design's four-class ~2008–2021 example to the on-disk 2000–2025 corpus. **2026-05-22 revision** integrates a six-instance external review (gemini/grok/deepseek/kimi/claude/chatgpt): conceded — the impossible state-(i) coverage criterion, the unfrozen screen functional form (now the §3.1 univariate rule, threshold fit on #14), tolerance-indexed outcomes + lead-with-10%, LORO-as-fixed-screen-evaluation (no refit), the state-(iii) lower bound, vintage-block-bootstrap clustering companion, the seasoning bug (2024Q3/2025Q1 → 2022Q2/2022Q4), and the frozen-definition gaps (compute-saved, in-scope, genuine-recovery binary, encodings, parity ε + post-stamp-OTS, skipped-cell informativeness floor, hardened no-add-vintages, glossary, internal-artifact framing); pushed back — equal-count sampling (per-regime transport leverage), the "design peek-taint" framing (public-macro boundaries + fixed rotation, disclosed), full joint prior decomposition (over-engineering), and acting on boundary-theory-ladenness now (separate future pre-reg). The §3 Q2-baseline correction (9/44 ≈ 20.5%, vs the design §4.2 anchor's 3/29) was caught while grounding the cohort derivation in #14 yields. A **second revision pass** (Tony's per-regime-power question) established the 59-cell/vintage grid cap (10 `S_rate` + 49 `S_llpa`), found that three of the #14 seven ran `S_rate`-only (deflating the yield estimate), and added: the **both-strata** run freeze (§2d), **two** frozen screens (screen-tight `c=0.22` regulator-end / screen-loose `c=0.185` bank-end, §3.1) replacing the single screen — with `c=0.10` excluded as dominated after the screen proved non-monotonic in `c` — and the per-regime fold-power analysis (§5). No held-out FM data outside the #14 seven has been touched at drafting time.

**Pre-reg author:** Claude Opus 4.7 (governance lineage), with Tony Mason. **OTS:** auto-applied by post-commit hook on stamping — *after* Tony's review (the STOP-FOR-REVIEW gate).
