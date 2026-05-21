# B-recovery Cycle Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Execute the four-step post-#14 arc — close #14, parallelize the band-construction pipeline, write and stamp the #15 B-recovery pre-registration, and characterize the 4d stress-regime asymmetry.

**Architecture:** Sequential, gated. #14 is frozen before the pipeline changes (provenance); parallelization is parity-verified before #15 execution (affordability + cleanliness); #15 predictions freeze at an OTS stamp before any held-out data is touched; 4d is descriptive only.

**Tech Stack:** Python 3, numpy, scipy, scikit-learn (CART), joblib (new), pandas/pyarrow (parquet), OpenTimestamps (commit hook). Design spec: `docs/superpowers/specs/2026-05-21-b-recovery-cycle-design.md`.

---

## File Structure

- `docs/superpowers/specs/2026-05-18-expanded-vintage-replication-result-note.md` — #14 result note (finalize).
- `scripts/silence_manufacture_test.py`, `scripts/frame_evocation_test.py`, `scripts/expanded_vintage_aggregate.py` — #14 analysis (already edited this session; commit in Task 1).
- `runs/silence_manufacture_2026-05-20.json`, `runs/frame_evocation_2026-05-20.json`, `runs/expanded_vintage_2026-05-20.json` — #14 outputs (commit in Task 1).
- `wedge/refinement_set.py` — band construction; parallelize the inner loop (Task 2).
- `scripts/parity_suite_fm.py` — NEW: multi-vintage parity harness (Task 2).
- `docs/superpowers/specs/2026-05-21-b-recovery-preregistration.md` — NEW: the stamped #15 pre-reg (Task 3).
- `scripts/b_recovery_analysis.py` + `tests/test_b_recovery_analysis.py` — NEW: #15 metric module (Task 4).
- `scripts/stress_regime_asymmetry.py` — NEW: 4d descriptive characterization (Task 5).

---

## Task 1: Close #14 (provenance gate)

**Files:**
- Modify: `docs/superpowers/specs/2026-05-18-expanded-vintage-replication-result-note.md`
- Modify (auto-memory, outside repo): `~/.claude/projects/-home-tony-projects-governance/memory/{project_silence_manufacture_result,project_saturation_phase_characterization,project_pre_registration_pattern,project_cookbook_adversarial_manual,project_current_anchor}.md`
- Commit (already in working tree): `scripts/silence_manufacture_test.py`, `scripts/frame_evocation_test.py`, `scripts/expanded_vintage_aggregate.py`, `runs/silence_manufacture_2026-05-20.json`, `runs/frame_evocation_2026-05-20.json`, `runs/expanded_vintage_2026-05-20.json`

- [ ] **Step 1: Finalize the result note** — retitle `PARTIAL` → final; set scope = 7 vintages, n=171 in-scope, 26 silence cells. Fill the P-scorecard rows with the verified numbers:
  - P1 named_diff (FRESH): **MISS** — silence 74% / reorg-agreement 44% / no-reorg FP 18%.
  - P2 M2_mean silence-only AUC (FULL): **MISS** — AUC 0.763 (need ≥0.95), perm p≈0.000.
  - P3 silence outside 2016Q1: **HIT** — 23 fresh silence cells across all 4 fresh vintages (incl. 2012Q1 the designated control, 2020Q2 COVID = 14).
  - P4 M3_max vs M1 (FULL primary): **MISS** — Δ=+0.020, p=0.66 (tie persists at n=171).
  - 4a placebo: clean (null-AUC>0.95 rate 0.000). 4d: flags (2009Q1 no-reorg named_diff 30%).

- [ ] **Step 2: Add the four interpretive sections to the note** (prose): (a) corrected decomposition — silence = reorganization ∧ adequacy-flip, carrier collinear regime-indexed mechanism (NOT orthogonal; `verdict_differs` 49% reorg vs 7.6% no-reorg); (b) detector→signal reshaping; (c) regime-carrier finding as hypothesis-not-claim (geographic in expansion, servicer/institutional in COVID; regime/vintage collinear); (d) recursive surface-salience note.

- [ ] **Step 3: Apply memory deltas** — edit each of the five memory files per design §2: silence-manufacture (FM-substrate-general, four-way falsification, reorg∧A-inadequacy decomposition), saturation-phase (trimodal dead at n=171), pre-reg-pattern (low priors vindicated), cookbook (signal-not-classifier spine), current-anchor (HEAD, #14 closed, arc→parallelize→#15→4d).

- [ ] **Step 4: Commit the #14 closing artifacts**

```bash
git add docs/superpowers/specs/2026-05-18-expanded-vintage-replication-result-note.md \
        scripts/silence_manufacture_test.py scripts/frame_evocation_test.py \
        scripts/expanded_vintage_aggregate.py \
        runs/silence_manufacture_2026-05-20.json runs/frame_evocation_2026-05-20.json \
        runs/expanded_vintage_2026-05-20.json
git commit -m "Close #14: finalize expanded-vintage result note (P1/P2/P4 MISS, P3 HIT)"
```

- [ ] **Step 5: Verify the OTS stamp commit landed**

Run: `git log --oneline -3`
Expected: an `ots: stamp <hash>` commit on top of the close-#14 commit.

---

## Task 2: Parallelize `build_refinement_band` (affordability gate)

**Files:**
- Modify: `wedge/refinement_set.py:142-162` (inner CART loop over `(subset, depth, leaf_min)`)
- Create: `scripts/parity_suite_fm.py`
- Reference: committed serial JSONs `runs/fm_rich_policy_vocab_adequacy_{2008Q1,2014Q3,2020Q2}.json`

- [ ] **Step 1: Write the parity-suite harness (the test)**

```python
# scripts/parity_suite_fm.py — compare a freshly-recomputed vintage JSON to its
# committed serial reference across a regime/stratum-spanning suite.
# Determinism standard: labels/discrete EXACT; floats within tol. Declared up front.
SUITE = ["2008Q1", "2014Q3", "2020Q2"]   # crisis(S_rate) / expansion(both) / COVID(both,large)
FLOAT_TOL = 1e-9
# Reuse scripts/parity_check_fm_rich_policy.py compare() per vintage; assert exit 0 for all.
```

- [ ] **Step 2: Run the harness against the UNMODIFIED pipeline to confirm it passes (sanity)**

Run: recompute 2008Q1 with the current serial code, `python scripts/parity_check_fm_rich_policy.py runs/fm_rich_policy_vocab_adequacy_2008Q1.json <recomputed>`
Expected: PARITY OK — confirms the harness compares correctly before any change.

- [ ] **Step 3: Implement joblib parallelization of the inner loop**

```python
# wedge/refinement_set.py ~142-162: replace the serial for-loop over candidate
# (subset, depth, leaf_min) tuples with:
from joblib import Parallel, delayed
results = Parallel(n_jobs=-1, backend="loky")(
    delayed(_fit_one)(subset, depth, leaf_min, X, y, seed)
    for subset, depth, leaf_min in candidates
)
# _fit_one must be deterministic: pass an explicit random_state/seed per CART fit;
# do NOT rely on global RNG state (parallel workers fork it).
```

- [ ] **Step 4: Run parity on the smallest vintage first**

Run: recompute 2008Q1 (S_rate only, fast) with the parallel code; `python scripts/parity_check_fm_rich_policy.py runs/fm_rich_policy_vocab_adequacy_2008Q1.json <parallel-out>`
Expected: PARITY OK (0 divergences). If discrete labels differ → tie-breaking nondeterminism; fix by sorting candidates deterministically before dispatch and seeding each fit. If only floats differ within tol → acceptable per declared standard.

- [ ] **Step 5: Run the full parity suite**

Run: `python scripts/parity_suite_fm.py`
Expected: PARITY OK for 2008Q1, 2014Q3, 2020Q2 (both strata). Record wall-clock to confirm the speedup.

- [ ] **Step 6: Commit (with the suite archived as a regression harness)**

```bash
git add wedge/refinement_set.py scripts/parity_suite_fm.py
git commit -m "Parallelize build_refinement_band (joblib); parity-verified vs serial"
```

---

## Task 3: Write and stamp the #15 B-recovery pre-registration (the IP freeze)

**Files:**
- Create: `docs/superpowers/specs/2026-05-21-b-recovery-preregistration.md`

> **STOP-FOR-REVIEW:** Task 3's commit OTS-stamps and freezes the #15 predictions. Pause for Tony's review of the written pre-reg before Step 5 (the stamp), per the leave-room-before-freeze discipline.

- [ ] **Step 1: Pin the regime-class quarter mapping (frozen table)** — e.g. crisis = 2008Q1–2009Q4; recovery = 2011Q1–2013Q4; expansion = 2014Q1–2019Q4 + 2004Q1–2006Q4; COVID-era = 2020Q1–2021Q4. Each row with a one-line rationale. (Defaults; Tony may adjust at review.)

- [ ] **Step 2: Select the held-out vintage list by the precision target** — target overall false-skip-rate upper-CI half-width ≤ 5pp ⇒ from per-vintage A-inadequate yield (~tens/vintage in Q2's broader population) compute K; pick K vintages stratified across regime classes, **distinct from the #14 seven** (2008Q1/2016Q1/2018Q1/2009Q1/2014Q3/2012Q1/2020Q2). Freeze the list by name.

- [ ] **Step 3: Write the pre-reg body** — Q1 (scientific, descriptive) + Q2 (deployable); primary = false-skip-risk upper bound (Clopper-Pearson) + operating curve (false-skip vs coverage vs compute-saved) over tolerance grid {1,5,10,20%}; predictor buckets (cheap/oracle/regime) with frozen encodings + cheap-audit; LORO transport (≥30-cell informativeness floor, >10pp non-transport flag); four-state outcome; adversarial (clustered permutation, no-post-hoc-regime-fit, threshold robustness ±0.05/0.25/0.35 + min-ΔR²≥0.15); scope. Copy the §4.6 numbers verbatim from the design.

- [ ] **Step 4: Self-review** — placeholder scan, internal consistency (numbers match design §4.6), every threshold numeric.

- [ ] **Step 5: Commit → OTS stamp (predictions freeze)** — ONLY after Tony's review.

```bash
git add docs/superpowers/specs/2026-05-21-b-recovery-preregistration.md
git commit -m "Pre-register #15 B-recovery (bounded false-skip risk, operating curve)"
git log --oneline -2   # confirm ots: stamp commit
```

---

## Task 4: Build the #15 analysis module + execute on held-out

**Files:**
- Create: `scripts/b_recovery_analysis.py`
- Test: `tests/test_b_recovery_analysis.py`

> Steps 1–6 (the metric module) are TDD-able now and do NOT depend on held-out data. Steps 7–9 (the runs) execute only after Task 2 parity passes and Task 3 is stamped.

- [ ] **Step 1: Write failing tests for the metric primitives**

```python
# tests/test_b_recovery_analysis.py
from scripts.b_recovery_analysis import false_skip_risk, clopper_pearson_upper, operating_point

def test_false_skip_risk_counts_b_fails_among_skipped():
    # cells: (skip?, b_fails?)
    cells = [(True, False), (True, True), (True, False), (False, True)]
    # among skipped (3): one b_fails -> 1/3
    assert abs(false_skip_risk(cells) - 1/3) < 1e-12

def test_clopper_pearson_upper_zero_failures_rule_of_three():
    # 0 failures in 30 -> ~0.095 upper 95% (one-sided ~3/n)
    ub = clopper_pearson_upper(failures=0, n=30, conf=0.95)
    assert 0.085 < ub < 0.115

def test_clopper_pearson_upper_known_value():
    # 3 failures in 29, one-sided 95% upper bound ~ 0.24-0.27
    ub = clopper_pearson_upper(failures=3, n=29, conf=0.95)
    assert 0.20 < ub < 0.30
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_b_recovery_analysis.py -v`
Expected: FAIL (module/functions not defined).

- [ ] **Step 3: Implement the metric primitives**

```python
# scripts/b_recovery_analysis.py
from scipy.stats import beta

def false_skip_risk(cells):
    skipped = [b_fails for skip, b_fails in cells if skip]
    return (sum(skipped) / len(skipped)) if skipped else 0.0

def clopper_pearson_upper(failures, n, conf=0.95):
    if n == 0: return 1.0
    if failures == n: return 1.0
    return float(beta.ppf(conf, failures + 1, n - failures))  # one-sided upper

def operating_point(cells, tolerance):
    """Return (coverage, false_skip_upper) for skipping all cells the screen
    marks skip; here the naive 'skip all' rule; richer screens passed as a mask."""
    skip_mask = [skip for skip, _ in cells]
    n_skip = sum(skip_mask)
    fails = sum(b for s, b in cells if s)
    ub = clopper_pearson_upper(fails, n_skip)
    coverage = n_skip / len(cells) if cells else 0.0
    return {"coverage": coverage, "false_skip_upper": ub, "safe": ub <= tolerance}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_b_recovery_analysis.py -v`
Expected: PASS (3 tests).

- [ ] **Step 5: Add operating-curve + LORO + compute-saved (TDD)** — write failing tests for `operating_curve(cells, grid)` (returns per-tolerance verdicts), `loro_folds(cells_by_regime)` (per-fold bound; flags <30-cell folds descriptive, >10pp-over-pooled non-transport), and `compute_saved(coverage, per_cell_corehours)`; then implement; then verify pass.

- [ ] **Step 6: Commit the analysis module**

```bash
git add scripts/b_recovery_analysis.py tests/test_b_recovery_analysis.py
git commit -m "Add #15 B-recovery analysis module (false-skip bound, operating curve, LORO)"
```

- [ ] **Step 7: Run band construction on the frozen held-out vintages** (procedure; long, parallel) — for each vintage in the pre-reg's frozen list: convert CSV→parquet if needed (`scripts/convert_fm_csv_to_parquet.py`), run `PYTHONPATH=. python scripts/fm_rich_policy_vocab_adequacy_test_parallel.py --vintage <V>` (the parallel pipeline from Task 2), STRICTLY SERIAL across vintages per the load discipline. Record exit codes to `runs/expanded-vintage-logs/`.

- [ ] **Step 8: Derive the A-inadequate population + B-recovery labels on held-out** — extend `scripts/silence_manufacture_test.py` VINTAGES to the held-out list (or a held-out-scoped copy), producing per-cell `R²_A`, `R²_B`, reorg, stratum, regime. The Q2 population = all `R²_A < 0.30` cells; label `B_fails = R²_B < 0.30`.

- [ ] **Step 9: Apply `b_recovery_analysis` and write the #15 result note** — compute the operating curve (false-skip vs coverage vs compute-saved), Clopper-Pearson bounds overall + per-regime + per-LORO-fold, and the four-state verdict per the frozen rules. Write `docs/superpowers/specs/2026-05-2X-b-recovery-result-note.md`; commit (OTS stamps).

---

## Task 5: 4d stress-regime asymmetry characterization (descriptive)

**Files:**
- Create: `scripts/stress_regime_asymmetry.py`
- Create: `docs/superpowers/specs/2026-05-2X-stress-regime-asymmetry-note.md`

- [ ] **Step 1: Extract the target cells** — from `runs/frame_evocation_2026-05-20.json`, select 2009Q1 (and 2008Q1) **no-reorg** cells where `named_diff == 1` (the 30% firing population), plus a comparison set of expansion no-reorg cells.

- [ ] **Step 2: Characterize (no classifier)** — for each target cell tabulate: peak named feature in A vs B, carrier saturations (p_sat, p3_sat), R²_A/R²_B, used-feature sets. Compare crisis (2008/2009) vs expansion distributions descriptively.

- [ ] **Step 3: Write the descriptive note** — what distinguishes the stress-regime named-feature asymmetry from silence; whether it is crisis-vintage-specific. Explicitly state: any classifier emerging from this requires its own pre-registration (design §5). Commit.

---

## Self-Review

- **Spec coverage:** Task 1 = design §2; Task 2 = §3 (parity suite, determinism standard); Task 3 = §4 + §4.6 freeze list; Task 4 = §4.1/§4.2/§4.4/§4.5 (estimands, bounded metric, LORO, stats); Task 5 = §5. §4.8 (audiences/Goodhart) is reporting framing, surfaced in Task 4 Step 9 (compute-saved + operating curve) and the #15 result note. All design sections map to a task.
- **Placeholder scan:** the only deferred specifics are the held-out vintage list and regime quarter-table — both are *produced as frozen artifacts in Task 3* (with proposed defaults), not left blank, so downstream references ("the pre-reg's frozen list") resolve to a defined object.
- **Type consistency:** `false_skip_risk`, `clopper_pearson_upper`, `operating_point`, `operating_curve`, `loro_folds`, `compute_saved` are used consistently across Task 4 steps; `B_fails = R²_B < 0.30` is the single label definition used in Steps 1, 8, 9.
