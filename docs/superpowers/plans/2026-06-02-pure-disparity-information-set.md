# Pure-Disparity Information-Set Contrast — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the corrected positive control — a genuine pure-disparity DGP (two families) and a 2×2 information-set read-off — to answer whether G-access lets the §5 apparatus separate honest-correction from laundering on a disparity a G-blind auditor cannot see.

**Architecture:** Extend `scripts/fairwash_frontier_dgp.py` with two new `world` branches (`PD_baserate`, `PD_noise`), each magnitude-controlled by bisection to a target |gap|. Add a within-G-stratum-AUC validity gate (rejects a family that leaks individual signal). Extend `scripts/lda_shared_surface_test.py` with one new discriminator (`A_obs_ghat0/1`, BISG-thresholded stratifier) and an information-set partition over the existing discriminator block. No new test logic — reuse the existing covariate-adjusted `_ols_label_effect`.

**Tech Stack:** numpy, scikit-learn (GradientBoosting, roc_auc_score, LogisticRegression), pytest. Scripts loaded via `importlib` from `scripts/` (existing pattern in `wedge/tests/`).

**Binding discipline:** The OTS-stamped pre-reg (Task 1) freezes predictions BEFORE construction code touches data. The blind adversary (Task 6) runs BEFORE any headline is written. Design spec: `docs/superpowers/specs/2026-06-02-pure-disparity-information-set-design.md`.

---

## File Structure

- **Modify** `scripts/fairwash_frontier_dgp.py` — add `PD_baserate` / `PD_noise` world branches + bisection helpers `_bisect_baserate_shift`, `_bisect_noise_flip`. Pure additions; A/B/P branches byte-unchanged.
- **Modify** `scripts/lda_shared_surface_test.py` — add `A_obs_ghat0/1` to `_eval_model`; add `INFO_SETS` partition dict; add `run_pure_disparity()` entry point + CLI flag `--pure-disparity`.
- **Create** `wedge/tests/test_pure_disparity_dgp.py` — validity-gate + magnitude-control contract tests.
- **Create** `docs/superpowers/specs/2026-06-02-pure-disparity-information-set-preregistration-note.md` — the frozen pre-reg (Task 1).
- **Output** `runs/pure_disparity_2026-06-02.json` — the scored grid.

---

### Task 1: Freeze the pre-registration (NO CODE TOUCHES DATA BEFORE THIS)

**Files:**
- Create: `docs/superpowers/specs/2026-06-02-pure-disparity-information-set-preregistration-note.md`

- [ ] **Step 1: Write the pre-reg note** with these immutable sections (predictions copied verbatim from the design §2, with operational PASS/FAIL):

```markdown
# Pure-disparity information-set contrast — PRE-REGISTRATION

**Status:** PRE-REG (freeze candidate). Predictions immutable once OTS-stamped.
**Design:** docs/superpowers/specs/2026-06-02-pure-disparity-information-set-design.md
**Pre-reg before any construction code touches data.**

## Frozen predictions + PASS/FAIL

- **P1 (prior 0.85):** Bare auditor (`{A_obs, CAL}`) `separates_kctl` == False on BOTH families,
  at BOTH |gap| targets. PASS if False everywhere; MISS if True on any bare cell.
- **P2 (prior 0.45 — THE COIN-FLIP):** §5 true-G auditor (`{A_obs, CAL, A_obs_g0, A_obs_g1}`)
  `separates_kctl` == True on at least one family at |gap|=0.20. PASS if True; MISS if False.
- **P3 (prior 0.40):** The two families give DIFFERENT P2 verdicts (one separates, one not) at
  |gap|=0.20. N/A (logged, not scored) for any family rejected by the §4 validity gate.
- **P4 (prior 0.65):** On any cell where P2 is True, BISG auditor
  (`{A_obs, CAL, A_obs_ghat0, A_obs_ghat1}`) `separates_kctl` == False (true-G separates where
  noisy-G does not). Scorable only where P2 True.

## Validity gate (computed BEFORE the apparatus run, per plant)
within-G-stratum AUC(Y ~ all OBSERVABLE features), pooled over G=0 and G=1, must be within
±0.02 of the clean-world (no-plant) baseline. A family failing the gate at its |gap| target is
REJECTED and reported as rejected — not patched. If BOTH families fail → PD-impossibility
confirmed at construction stage (researcher's P2=0.45 loses; the bell rings).

## Hard stop
naive vs k-controlled `is_L` coefficient sign-disagreement on any cell ⇒ NO RESULT for that
cell (reported in headline, not footnote).

## Frozen grid
2 families × 4 info-sets × |gap|∈{0.10, 0.20} × 20 seeds × n=8000.
Negative-control anchor: clean world shows no separation on ANY auditor (else abort).

## Scope
Synthetic existence-grade. P2-yes ⇒ "there EXISTS a pure-disparity DGP where G-access separates
and G-blindness does not", NOT a prevalence-in-wild claim.
```

- [ ] **Step 2: Commit + OTS-stamp the freeze**

```bash
git add docs/superpowers/specs/2026-06-02-pure-disparity-information-set-preregistration-note.md
git commit -F <msgfile>   # subject: "pure-disparity information-set: pre-registration"
                          # body: one paragraph + "Pre-reg before any code touches data."
                          # trailer: Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
```

Expected: post-commit hook auto-stamps an `ots: stamp <hash>` commit above it. Note: new untracked file ⇒ `git add` then commit (NOT `git commit -- <path>`, which only matches tracked changes).

---

### Task 2: Magnitude-controlled base-rate-shift family (`PD_baserate`)

**Files:**
- Modify: `scripts/fairwash_frontier_dgp.py` (add branch + bisection helper)
- Test: `wedge/tests/test_pure_disparity_dgp.py`

- [ ] **Step 1: Write the failing test** (validity gate + magnitude control for Family A)

```python
# wedge/tests/test_pure_disparity_dgp.py
import importlib.util, sys
from pathlib import Path
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import roc_auc_score

_spec = importlib.util.spec_from_file_location(
    "fairwash_frontier_dgp",
    Path(__file__).resolve().parents[2] / "scripts" / "fairwash_frontier_dgp.py")
dgp = importlib.util.module_from_spec(_spec)
sys.modules["fairwash_frontier_dgp"] = dgp
_spec.loader.exec_module(dgp)

N = 8000
OBS = [f"x{j}" for j in range(8)] + ["cfresh_cont", "cfresh_cat", "cfresh_count"]

def _within_g_auc(fr):
    """Pooled within-G-stratum AUC(Y ~ OBS). A pure disparity stays ~0.50-flat
    vs the clean world; an individual predictor climbs."""
    aucs = []
    for g in (0, 1):
        sub = fr[fr["G"] == g]
        if sub["Y"].nunique() < 2:
            continue
        m = GradientBoostingClassifier(max_depth=3, n_estimators=100, random_state=0)
        m.fit(sub[OBS].values, sub["Y"].values)
        aucs.append(roc_auc_score(sub["Y"].values, m.predict_proba(sub[OBS].values)[:, 1]))
    return float(np.mean(aucs))

def _abs_gap(fr):
    g0 = fr[fr["G"] == 0]["Y"].mean(); g1 = fr[fr["G"] == 1]["Y"].mean()
    return float(abs(g0 - g1))

def test_pd_baserate_hits_target_gap():
    fr = dgp.generate_twin_world(0.70, "PD_baserate", N, 0, target_gap=0.20).frame
    assert abs(_abs_gap(fr) - 0.20) < 0.03, f"realized gap {_abs_gap(fr):.3f} off target 0.20"

def test_pd_baserate_passes_validity_gate():
    clean = dgp.generate_twin_world(0.70, "PD_baserate", N, 0, target_gap=0.0).frame
    plant = dgp.generate_twin_world(0.70, "PD_baserate", N, 0, target_gap=0.20).frame
    base = _within_g_auc(clean); pl = _within_g_auc(plant)
    assert abs(pl - base) < 0.02, f"within-G AUC moved {base:.3f}->{pl:.3f} (>0.02: not pure)"
```

- [ ] **Step 2: Run to verify it fails**

Run: `pytest wedge/tests/test_pure_disparity_dgp.py -v`
Expected: FAIL — `generate_twin_world` rejects `world='PD_baserate'` / no `target_gap` kwarg.

- [ ] **Step 3: Implement the `PD_baserate` branch + bisection.** In `scripts/fairwash_frontier_dgp.py`, change the signature and add the branch:

```python
def generate_twin_world(proxy_strength, world, n, seed, *, bisg_auc=0.85,
                        decouple=0.0, target_gap=None):
    ...
    if world not in ("A", "B", "P", "PD_baserate", "PD_noise"):
        raise ValueError("world must be 'A','B','P','PD_baserate','PD_noise'")
    ...
    # after Gz, legit_logit, a, cf computed; after pA/YA/y_clean:
    if world == "PD_baserate":
        # group-conditional CONSTANT logit offset for G=1: moves intercept by
        # group (base rate), not slope. Pure disparity by construction.
        def _gap_for_c(c):
            p = 1.0 / (1.0 + np.exp(-(legit_logit - c * G)))
            yy = rng_gap.binomial(1, p)
            return abs(yy[G == 0].mean() - yy[G == 1].mean())
        rng_gap = np.random.default_rng(seed + 991)
        c = 0.0 if not target_gap else _bisect_shift(_gap_for_c, target_gap)
        Y = rng.binomial(1, 1.0 / (1.0 + np.exp(-(legit_logit - c * G))))
```

And add the bisection helper near `_coupling_for_proxy_strength`:

```python
def _bisect_shift(gap_fn, target, lo=0.0, hi=8.0, iters=40):
    """Bisect a scalar shift so realized |gap| ≈ target (gap_fn monotone in shift)."""
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        if gap_fn(mid) < target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)
```

- [ ] **Step 4: Run to verify both tests pass**

Run: `pytest wedge/tests/test_pure_disparity_dgp.py -v`
Expected: PASS (both `test_pd_baserate_*`).

- [ ] **Step 5: Verify A/B/P unchanged (regression guard)**

Run: `pytest wedge/tests/test_compliant_practice_dgp.py -v`
Expected: PASS — existing A/B/P contract untouched.

- [ ] **Step 6: Commit**

```bash
git add scripts/fairwash_frontier_dgp.py wedge/tests/test_pure_disparity_dgp.py
git commit -F <msgfile>   # "pure-disparity: PD_baserate family + magnitude-control bisection"
```

---

### Task 3: Magnitude-controlled label-flip-by-G family (`PD_noise`)

**Files:**
- Modify: `scripts/fairwash_frontier_dgp.py`
- Test: `wedge/tests/test_pure_disparity_dgp.py`

- [ ] **Step 1: Write the failing test** (append to the test file)

```python
def test_pd_noise_hits_target_gap():
    fr = dgp.generate_twin_world(0.70, "PD_noise", N, 0, target_gap=0.20).frame
    assert abs(_abs_gap(fr) - 0.20) < 0.03, f"realized gap {_abs_gap(fr):.3f} off target"

def test_pd_noise_validity_gate_is_HONEST():
    # The gate is ALLOWED to reject this family. We assert the measurement is
    # computed and finite — NOT that it passes (the design permits rejection).
    clean = dgp.generate_twin_world(0.70, "PD_noise", N, 0, target_gap=0.0).frame
    plant = dgp.generate_twin_world(0.70, "PD_noise", N, 0, target_gap=0.20).frame
    delta = abs(_within_g_auc(plant) - _within_g_auc(clean))
    assert np.isfinite(delta)   # rejection (delta>0.02) is a valid scientific outcome
```

- [ ] **Step 2: Run to verify it fails**

Run: `pytest wedge/tests/test_pure_disparity_dgp.py -k pd_noise -v`
Expected: FAIL — `world='PD_noise'` not yet handled.

- [ ] **Step 3: Implement the `PD_noise` branch.** Add to `generate_twin_world`:

```python
    if world == "PD_noise":
        # draw Y from the CLEAN logit, then asymmetrically flip G=1 labels toward 0
        # with prob f (post-draw ⇒ no observable predicts the flip).
        p_clean = 1.0 / (1.0 + np.exp(-legit_logit))
        def _gap_for_f(f):
            yy = rng_gap.binomial(1, p_clean).astype(int)
            flip = (G == 1) & (yy == 1) & (rng_gap.random(n) < f)
            yy = yy.copy(); yy[flip] = 0
            return abs(yy[G == 0].mean() - yy[G == 1].mean())
        rng_gap = np.random.default_rng(seed + 991)
        f = 0.0 if not target_gap else _bisect_shift(_gap_for_f, target_gap, lo=0.0, hi=1.0)
        Y = rng.binomial(1, p_clean).astype(int)
        flip = (G == 1) & (Y == 1) & (rng.random(n) < f)
        Y = Y.copy(); Y[flip] = 0
```

- [ ] **Step 4: Run to verify pass**

Run: `pytest wedge/tests/test_pure_disparity_dgp.py -k pd_noise -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/fairwash_frontier_dgp.py wedge/tests/test_pure_disparity_dgp.py
git commit -F <msgfile>   # "pure-disparity: PD_noise label-flip family"
```

---

### Task 4: BISG-thresholded stratifier discriminator (`A_obs_ghat0/1`)

**Files:**
- Modify: `scripts/lda_shared_surface_test.py:99-116` (`_eval_model`)
- Test: `wedge/tests/test_pure_disparity_dgp.py`

- [ ] **Step 1: Write the failing test** (append)

```python
def test_eval_model_emits_ghat_stratified_accuracy():
    import importlib.util as iu
    s = iu.spec_from_file_location("lda", Path(__file__).resolve().parents[2]
                                   / "scripts" / "lda_shared_surface_test.py")
    lda = iu.module_from_spec(s); sys.modules["lda"] = lda; s.loader.exec_module(lda)
    fr = dgp.generate_twin_world(0.70, "PD_baserate", N, 0, target_gap=0.20).frame
    tr, te = lda._split(len(fr), 0)
    out = lda._eval_model(fr, tr, te, lda.ADMISSIBLE, 0)
    assert "A_obs_ghat0" in out and "A_obs_ghat1" in out
    assert 0.0 <= out["A_obs_ghat0"] <= 1.0 and 0.0 <= out["A_obs_ghat1"] <= 1.0
```

- [ ] **Step 2: Run to verify it fails**

Run: `pytest wedge/tests/test_pure_disparity_dgp.py -k ghat -v`
Expected: FAIL — KeyError `A_obs_ghat0`.

- [ ] **Step 3: Implement.** In `_eval_model`, after the `a_g0`/`a_g1` lines, add a noisy-G stratifier from `Ghat_bisg` (median-threshold on the test rows):

```python
    ghat_te = fr["Ghat_bisg"].values[te]
    ghat_hi = ghat_te >= np.median(ghat_te)        # noisy-G stratifier (deployable)
    a_gh0 = accuracy_score(Y_te[~ghat_hi], dec[~ghat_hi]) if (~ghat_hi).any() else float("nan")
    a_gh1 = accuracy_score(Y_te[ghat_hi], dec[ghat_hi]) if ghat_hi.any() else float("nan")
```

and add to the returned dict:

```python
        "A_obs_ghat0": float(a_gh0), "A_obs_ghat1": float(a_gh1),  # OBSERVABLE (noisy-G strat)
```

- [ ] **Step 4: Run to verify pass + regression guard**

Run: `pytest wedge/tests/test_pure_disparity_dgp.py -k ghat -v && pytest wedge/tests/test_compliant_practice_dgp.py -q`
Expected: PASS; existing tests still green.

- [ ] **Step 5: Commit**

```bash
git add scripts/lda_shared_surface_test.py wedge/tests/test_pure_disparity_dgp.py
git commit -F <msgfile>   # "pure-disparity: BISG-thresholded stratifier discriminator"
```

---

### Task 5: Information-set partition + `run_pure_disparity()` entry point

**Files:**
- Modify: `scripts/lda_shared_surface_test.py` (add `INFO_SETS`, `run_pure_disparity`, CLI flag)

- [ ] **Step 1: Add the partition + per-info-set scoring.** Near `DISCRIMS`, add:

```python
INFO_SETS = {
    "bare":  ["A_obs", "CAL"],                                   # G-blind auditor
    "trueG": ["A_obs", "CAL", "A_obs_g0", "A_obs_g1"],           # §5 as published
    "bisg":  ["A_obs", "CAL", "A_obs_ghat0", "A_obs_ghat1"],     # deployable noisy-G
    "oracle":["A_clean"],                                        # grading reference
}
```

The existing `_ols_label_effect(rows, outcome)` scores ONE discriminator at a time. An info-set
"separates" if ANY of its member discriminators separates (k-controlled). Add:

```python
def _infoset_separates(cells_rows, members):
    """True if any member discriminator's k-controlled is_L coef separates AND
    its naive coef agrees in sign (else that member is NO-RESULT, skipped)."""
    verdicts = []
    for disc in members:
        r = _ols_label_effect(cells_rows, disc)
        if r is None:
            continue
        same_sign = (r["coef_is_L"] >= 0) == (r["coef_is_L_kctl"] >= 0)
        verdicts.append({"disc": disc, "separates": r["separates_kctl"],
                         "no_result": not same_sign,
                         "coef_kctl": r["coef_is_L_kctl"], "coef_naive": r["coef_is_L"]})
    any_sep = any(v["separates"] and not v["no_result"] for v in verdicts)
    return {"separates": bool(any_sep), "per_disc": verdicts}
```

- [ ] **Step 2: Add `run_pure_disparity()`.** Mirror `run_positive_control`'s structure:

```python
def run_pure_disparity(ps, families, gaps, seeds, n, out_path, smoke):
    """2x2 info-set contrast (pre-reg 2026-06-02). For each (family, target_gap),
    build the plant, log the validity gate (within-G AUC vs clean), pool arm
    families across seeds, score each INFO_SET. Negative-control: clean world."""
    import time; t0 = time.time()
    summary = {}
    # validity-gate baselines per family (clean world, target_gap=0.0)
    for fam in families:
        for gap in gaps:
            rows = []
            for s in seeds:
                fr = dgp.generate_twin_world(ps, fam, n, s, target_gap=gap).frame
                tr, te = _split(len(fr), s)
                for m in _arm_families(fr, tr, te, s):
                    m["seed"] = s; rows.append(m)
            cell = {"validity": _validity_gate(ps, fam, gap, seeds, n),
                    "infosets": {k: _infoset_separates(rows, v) for k, v in INFO_SETS.items()}}
            summary[f"{fam}_gap{gap:.2f}"] = cell
            print(f"[{time.time()-t0:6.1f}s] {fam} gap={gap:.2f} "
                  f"valΔ={cell['validity']['delta']:.3f} "
                  f"{ {k: cell['infosets'][k]['separates'] for k in INFO_SETS} }")
    # negative control: clean (no-plant) world A must not separate on any info-set
    neg_rows = []
    for s in seeds:
        # clean negative control = PD_baserate with zero shift (clean logit, no disparity)
        fr = dgp.generate_twin_world(ps, "PD_baserate", n, s, target_gap=0.0).frame
        tr, te = _split(len(fr), s)
        for m in _arm_families(fr, tr, te, s):
            m["seed"] = s; neg_rows.append(m)
    summary["NEG_clean"] = {k: _infoset_separates(neg_rows, v)["separates"]
                            for k, v in INFO_SETS.items()}
    payload = {"ps": ps, "families": list(families), "gaps": list(gaps),
               "n": n, "seeds": len(list(seeds)), "summary": summary,
               "pass_fail": "P1 bare !separate / P2 trueG separate@0.20 / "
                            "P3 families differ / P4 bisg !separate where trueG does"}
    Path(out_path).write_text(json.dumps(payload, indent=2))
    print(f"wrote {out_path}")
```

and the validity-gate helper:

```python
def _validity_gate(ps, fam, gap, seeds, n):
    """within-G-stratum AUC(Y~OBSERVABLE) for plant vs clean (target_gap=0), seed 0."""
    def wg(fr):
        from sklearn.ensemble import GradientBoostingClassifier
        feats = [f"x{j}" for j in range(8)] + CFRESH
        aucs = []
        for g in (0, 1):
            sub = fr[fr["G"] == g]
            if sub["Y"].nunique() < 2: continue
            m = GradientBoostingClassifier(max_depth=3, n_estimators=100, random_state=0)
            m.fit(sub[feats].values, sub["Y"].values)
            aucs.append(roc_auc_score(sub["Y"].values, m.predict_proba(sub[feats].values)[:, 1]))
        return float(np.mean(aucs))
    s0 = list(seeds)[0]
    clean = dgp.generate_twin_world(ps, fam, n, s0, target_gap=0.0).frame
    plant = dgp.generate_twin_world(ps, fam, n, s0, target_gap=gap).frame
    base, pl = wg(clean), wg(plant)
    return {"clean_wg_auc": base, "plant_wg_auc": pl, "delta": abs(pl - base),
            "passes": bool(abs(pl - base) < 0.02)}
```

- [ ] **Step 3: Wire the CLI flag.** In `main()`, add `--pure-disparity` mirroring `--positive-control`, with `families=("PD_baserate","PD_noise")`, `gaps=(0.10,0.20)`, smoke = `(("PD_baserate",),(0.20,),range(2),3000)`.

- [ ] **Step 4: Smoke-run (2 seeds, n=3000 — NOT the frozen grid)**

Run: `python scripts/lda_shared_surface_test.py --pure-disparity --smoke`
Expected: completes; prints validity Δ + per-info-set separates booleans; writes a smoke JSON. This exercises the wiring only — NOT a result.

- [ ] **Step 5: Commit**

```bash
git add scripts/lda_shared_surface_test.py
git commit -F <msgfile>   # "pure-disparity: info-set partition + run_pure_disparity entry point"
```

---

### Task 6: Blind-adversary the construction (BEFORE any headline)

**Files:** none (dispatch + record)

- [ ] **Step 1: Dispatch a blind adversary subagent** (general-purpose, blind to my P2 lean) charged to BREAK the construction, NOT to confirm it. Prompt it with ONLY: the DGP branch code, the validity-gate definition, and the question *"Is either `PD_baserate` or `PD_noise` secretly an individual-level predictor in disguise (like the failed World-P `imp_z`)? Find the way the within-G-stratum AUC gate could pass while the plant still leaks individual signal the apparatus exploits. Default to 'it leaks' if uncertain."* Do NOT tell it the priors or the desired outcome.

- [ ] **Step 2: Record the adversary verdict** in a working note `working_notes/2026-06-02-pure-disparity-construction-adversary.md`. If it finds a leak the gate misses, FIX the gate (e.g. add a per-discriminator within-G check, or a permutation test) and re-run Tasks 2–5 contracts BEFORE proceeding. The construction is not trusted until an adversary has tried and failed to break it.

- [ ] **Step 3: Commit the adversary note**

```bash
git add working_notes/2026-06-02-pure-disparity-construction-adversary.md
git commit -F <msgfile>   # "pure-disparity: construction blind-adversary record"
```

---

### Task 7: Run the frozen grid + score against the pre-reg

**Files:**
- Output: `runs/pure_disparity_2026-06-02.json`
- Create: `docs/superpowers/specs/2026-06-02-pure-disparity-information-set-result-note.md`

- [ ] **Step 1: Run the frozen grid** (2 families × 2 gaps × 20 seeds × n=8000)

Run: `python scripts/lda_shared_surface_test.py --pure-disparity --seeds 20 --n 8000 --out runs/pure_disparity_2026-06-02.json`
Expected: per-cell validity Δ + per-info-set separates; writes the JSON. Watch with a single-completion Monitor, not per-line.

- [ ] **Step 2: Verify the negative control FIRST.** Read `summary["NEG_clean"]` — every info-set MUST be False. If any True, ABORT and debug (apparatus broken; nothing downstream interpretable).

- [ ] **Step 3: Score each prediction** mechanically from the JSON (P1/P2/P3/P4 per the pre-reg PASS/FAIL). Record the validity-gate verdict per family FIRST (a rejected family changes what P2/P3 can claim).

- [ ] **Step 4: Write the result note** — scorecard table (prior / verdict / headline), validity-gate row per family, naive-vs-kctl side by side, the §7 scope caveat in BOTH yes/no branches. State which way the angel went.

- [ ] **Step 5: Commit the result + JSON**

```bash
git add runs/pure_disparity_2026-06-02.json docs/superpowers/specs/2026-06-02-pure-disparity-information-set-result-note.md
git commit -F <msgfile>   # "pure-disparity information-set: RESULT"
```
