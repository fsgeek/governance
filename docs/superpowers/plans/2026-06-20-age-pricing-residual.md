# Age-Residual Pricing Experiment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Determine whether the young-end mortgage-pricing overcharge survives lawful-risk controls (does the ~+47bps over lawful profile hold, or evaporate into "they're genuinely riskier").

**Architecture:** A pure, testable residualization module (`wedge/age_residual.py`) holding all statistics — data prep, OLS fit, per-band bps residual extraction, within-tenure stratification, collinearity diagnostics — with NO file I/O. A thin runner script (`scripts/age_pricing_residual.py`) loads the 1.67GB LC CSV, calls the module, and writes the self-describing artifact. Tests run entirely on synthetic data via a positive control (plant a known residual, assert recovery), so they need no large file and run fast.

**Tech Stack:** Python, pandas, numpy, statsmodels (OLS with categorical bands), pytest. statsmodels is the only possibly-new dep — verify/add it in Task 1.

## Global Constraints

- Data: `data/accepted_2007_to_2018Q4.csv`, full file. Resolved loans only: `loan_status ∈ {"Fully Paid", "Charged Off"}`.
- `est_age = 18 + (issue_d − earliest_cr_line)` in years; both dates parsed `format="%b-%Y"`; clip est_age to [18, 95].
- Parsing quirks (verified against the file): `int_rate` is a bare float string (e.g. `"13.99"`, NO `%`); `term` has a leading space (`" 36 months"`) → strip and take int; FICO = midpoint of `fico_range_low` and `fico_range_high`; dates are `%b-%Y` (e.g. `"Dec-2015"`).
- Primary lawful controls ONLY: FICO_mid, dti, annual_inc, loan_amnt, term_months, purpose (categorical). EXCLUDED from primary (age-loaded): emp_length, home_ownership, revol_util.
- Age bands (left-closed): [18,25) [25,30) [30,35) [35,40) [40,45) [45,50) [50,55) [55,60) [60,70) [70,95]. Reference band for residuals: [45,50).
- A (all-controls) and D (within-tenure stratification) are CO-PRIMARY. Raw int_rate is read before net-of-grade.
- Tests live in `wedge/tests/` (only collected path). Run: `pytest wedge/tests/ -v`.
- Frozen ledger (do NOT alter post-run): Tony=evaporates; Claude=partial survival, young band +10 to +25 bps.
- Output artifact `runs/lc_age_pricing_residual_2026-06-20.txt` + JSON sidecar `runs/lc_age_pricing_residual_2026-06-20.json`.

---

### Task 1: Module skeleton + dependency check + age banding

**Files:**
- Create: `wedge/age_residual.py`
- Create: `wedge/tests/test_age_residual.py`
- Modify (if needed): `pyproject.toml` (add `statsmodels` to deps)

**Interfaces:**
- Produces: `AGE_BANDS: list[tuple[float, float]]` (the 10 bands above); `REFERENCE_BAND_INDEX: int` (index of [45,50) = 6); `assign_age_band(age: float) -> int` returning band index 0..9 or -1 if outside [18,95); `band_label(i: int) -> str` (e.g. `"[45,50)"`).

- [ ] **Step 1: Verify statsmodels available; add if missing**

Run: `python3 -c "import statsmodels.api as sm; print(sm.__version__)"`
If ImportError: add `"statsmodels>=0.14"` to the `dependencies` list in `pyproject.toml`, then `pip install statsmodels` (or `uv pip install statsmodels`). Expected: a version string prints.

- [ ] **Step 2: Write the failing test for age banding**

```python
# wedge/tests/test_age_residual.py
from wedge.age_residual import assign_age_band, band_label, AGE_BANDS, REFERENCE_BAND_INDEX

def test_assign_age_band_boundaries():
    assert assign_age_band(18) == 0
    assert assign_age_band(24.9) == 0
    assert assign_age_band(25) == 1
    assert assign_age_band(47) == 6          # [45,50)
    assert assign_age_band(70) == 9          # [70,95]
    assert assign_age_band(95) == 9          # right edge inclusive on last band
    assert assign_age_band(17) == -1
    assert assign_age_band(96) == -1

def test_reference_band_is_45_50():
    lo, hi = AGE_BANDS[REFERENCE_BAND_INDEX]
    assert (lo, hi) == (45, 50)
    assert band_label(REFERENCE_BAND_INDEX) == "[45,50)"
```

- [ ] **Step 3: Run test to verify it fails**

Run: `pytest wedge/tests/test_age_residual.py -v`
Expected: FAIL with ImportError / cannot import `assign_age_band`.

- [ ] **Step 4: Write minimal implementation**

```python
# wedge/age_residual.py
"""Age-residual pricing analysis: does the young-end overcharge survive lawful-risk controls?
Pure statistics, no file I/O. See docs/superpowers/specs/2026-06-20-age-pricing-residual-design.md."""
from __future__ import annotations

AGE_BANDS: list[tuple[float, float]] = [
    (18, 25), (25, 30), (30, 35), (35, 40), (40, 45),
    (45, 50), (50, 55), (55, 60), (60, 70), (70, 95),
]
REFERENCE_BAND_INDEX = 5 if AGE_BANDS[5] == (45, 50) else next(
    i for i, b in enumerate(AGE_BANDS) if b == (45, 50)
)

def band_label(i: int) -> str:
    lo, hi = AGE_BANDS[i]
    return f"[{int(lo)},{int(hi)})"

def assign_age_band(age: float) -> int:
    if age < AGE_BANDS[0][0] or age > AGE_BANDS[-1][1]:
        return -1
    for i, (lo, hi) in enumerate(AGE_BANDS):
        # last band is right-inclusive so age==95 lands in it
        if lo <= age < hi or (i == len(AGE_BANDS) - 1 and age == hi):
            return i
    return -1
```

Note: REFERENCE_BAND_INDEX resolves to 5 ([45,50) is the 6th band, index 5). The test asserts `(45,50)` — fix the test's expected index to 5, not 6. (Bands are 0-indexed: [18,25)=0 … [45,50)=5.)

Correct the test in Step 2 accordingly: `assign_age_band(47) == 5` and `assign_age_band(70) == 9`.

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest wedge/tests/test_age_residual.py -v`
Expected: PASS (both tests).

- [ ] **Step 6: Commit**

```bash
git add wedge/age_residual.py wedge/tests/test_age_residual.py pyproject.toml
git commit -m "feat: age-residual module skeleton — age banding + statsmodels dep"
```

---

### Task 2: The residualization fit + per-band bps recovery (positive control)

**Files:**
- Modify: `wedge/age_residual.py`
- Modify: `wedge/tests/test_age_residual.py`

**Interfaces:**
- Consumes: `assign_age_band`, `AGE_BANDS`, `REFERENCE_BAND_INDEX`.
- Produces: `fit_band_residuals(df, outcome="int_rate", controls=DEFAULT_CONTROLS, age_band_col="age_band") -> BandResult` where `DEFAULT_CONTROLS = ["fico_mid", "dti", "annual_inc", "loan_amnt", "term_months"]` plus categorical `"purpose"`. `BandResult` is a dataclass with `.band_bps: dict[int, float]` (residual coefficient per band index, in bps, vs reference band, 0 for reference), `.band_ci: dict[int, tuple[float,float]]` (95% CI in bps), `.n_per_band: dict[int,int]`, `.r2: float`. Outcome is in percentage points (int_rate units); 1 pp = 100 bps, so coefficients are multiplied by 100 to report bps.

- [ ] **Step 1: Write the failing positive-control test**

Plant a KNOWN +30 bps premium on the youngest band, controls drawn neutrally and independently of age, and assert recovery within tolerance. This is the guard against the confabulation failure mode (a procedure that reports a residual it never computed).

```python
import numpy as np, pandas as pd
from wedge.age_residual import fit_band_residuals, assign_age_band

def _synth(n=60000, planted_young_bps=30.0, seed=0):
    rng = np.random.default_rng(seed)
    age = rng.uniform(18, 95, n)
    fico_mid = rng.uniform(640, 820, n)
    dti = rng.uniform(0, 35, n)
    annual_inc = rng.uniform(20000, 200000, n)
    loan_amnt = rng.uniform(1000, 40000, n)
    term_months = rng.choice([36, 60], n)
    purpose = rng.choice(["debt_consolidation", "credit_card", "home_improvement"], n)
    # lawful price: a real function of controls (so controls are NOT inert)
    base = 5.0 + (820 - fico_mid) * 0.02 + dti * 0.05 + (term_months == 60) * 1.5
    noise = rng.normal(0, 0.5, n)
    int_rate = base + noise
    band = np.array([assign_age_band(a) for a in age])
    int_rate = int_rate + (band == 0) * (planted_young_bps / 100.0)  # +30bps on youngest only
    df = pd.DataFrame(dict(age=age, fico_mid=fico_mid, dti=dti, annual_inc=annual_inc,
                           loan_amnt=loan_amnt, term_months=term_months, purpose=purpose,
                           int_rate=int_rate, age_band=band))
    return df

def test_positive_control_recovers_planted_young_premium():
    df = _synth(planted_young_bps=30.0)
    res = fit_band_residuals(df)
    assert abs(res.band_bps[0] - 30.0) < 6.0, f"expected ~30bps, got {res.band_bps[0]:.1f}"
    # a band with NO planted premium should be near zero
    assert abs(res.band_bps[4]) < 8.0, f"unplanted band should be ~0, got {res.band_bps[4]:.1f}"
    assert res.band_bps[REF := __import__('wedge.age_residual', fromlist=['REFERENCE_BAND_INDEX']).REFERENCE_BAND_INDEX] == 0.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest wedge/tests/test_age_residual.py::test_positive_control_recovers_planted_young_premium -v`
Expected: FAIL — `fit_band_residuals` not defined.

- [ ] **Step 3: Implement fit_band_residuals**

```python
# add to wedge/age_residual.py
from dataclasses import dataclass, field
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

DEFAULT_CONTROLS = ["fico_mid", "dti", "annual_inc", "loan_amnt", "term_months"]

@dataclass
class BandResult:
    band_bps: dict
    band_ci: dict
    n_per_band: dict
    r2: float

def fit_band_residuals(df: pd.DataFrame, outcome: str = "int_rate",
                       controls: list[str] | None = None,
                       age_band_col: str = "age_band") -> BandResult:
    controls = list(DEFAULT_CONTROLS if controls is None else controls)
    d = df.copy()
    # reference band coded last so statsmodels drops it as baseline via Treatment
    ref = REFERENCE_BAND_INDEX
    d["_band"] = pd.Categorical(d[age_band_col])
    numeric = " + ".join(controls)
    formula = f"{outcome} ~ C(_band, Treatment(reference={ref})) + {numeric} + C(purpose)"
    model = smf.ols(formula, data=d).fit()
    band_bps, band_ci = {}, {}
    for i in range(len(AGE_BANDS)):
        if i == ref:
            band_bps[i] = 0.0
            band_ci[i] = (0.0, 0.0)
            continue
        term = f"C(_band, Treatment(reference={ref}))[T.{i}]"
        if term in model.params.index:
            band_bps[i] = float(model.params[term]) * 100.0  # pp -> bps
            lo, hi = model.conf_int().loc[term]
            band_ci[i] = (float(lo) * 100.0, float(hi) * 100.0)
        else:
            band_bps[i] = float("nan")
            band_ci[i] = (float("nan"), float("nan"))
    n_per_band = d[age_band_col].value_counts().to_dict()
    return BandResult(band_bps=band_bps, band_ci=band_ci,
                      n_per_band={int(k): int(v) for k, v in n_per_band.items()},
                      r2=float(model.rsquared))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest wedge/tests/test_age_residual.py::test_positive_control_recovers_planted_young_premium -v`
Expected: PASS — recovered ~30bps on band 0, ~0 on band 4, exactly 0 on reference.

- [ ] **Step 5: Commit**

```bash
git add wedge/age_residual.py wedge/tests/test_age_residual.py
git commit -m "feat: band-residual OLS + positive-control test (recovers planted young premium)"
```

---

### Task 3: Polynomial robustness fit + within-tenure stratification (co-primary D) + collinearity diagnostics

**Files:**
- Modify: `wedge/age_residual.py`
- Modify: `wedge/tests/test_age_residual.py`

**Interfaces:**
- Consumes: `fit_band_residuals`, the synthetic `_synth` helper (move it to module-level in the test file if not already).
- Produces:
  - `fit_poly_age(df, outcome="int_rate", controls=None) -> dict` with keys `est_age_coef_bps`, `est_age_sq_coef_bps`, `r2` — confirms curvature isn't a binning artifact. Requires an `est_age` column in df.
  - `within_tenure_residuals(df, outcome="int_rate", controls=None, n_tenure_bins=5) -> dict[int, BandResult]` — stratify by credit-tenure quantile bin (tenure = est_age - 18), run `fit_band_residuals` within each bin, return per-bin results. This is co-primary D: young-vs-old at equal tenure.
  - `collinearity_diagnostics(df, controls=None) -> dict` returning `vif: dict[str,float]` and `corr_with_est_age: dict[str,float]` (Pearson corr of est_age with each numeric control).

- [ ] **Step 1: Write failing tests for poly, within-tenure, and collinearity**

```python
from wedge.age_residual import fit_poly_age, within_tenure_residuals, collinearity_diagnostics

def test_poly_age_detects_young_premium_curvature():
    df = _synth(planted_young_bps=30.0)
    df["est_age"] = df["age"]
    out = fit_poly_age(df)
    # planted premium is on the young tail -> negative slope in age near young end;
    # we only assert the quadratic model RUNS and returns finite bps coefs (curvature presence
    # is read in the artifact, not unit-asserted, since a single planted band is not a true parabola)
    assert np.isfinite(out["est_age_coef_bps"])
    assert np.isfinite(out["est_age_sq_coef_bps"])

def test_within_tenure_returns_a_result_per_bin():
    df = _synth(planted_young_bps=30.0)
    df["est_age"] = df["age"]
    bins = within_tenure_residuals(df, n_tenure_bins=4)
    assert len(bins) == 4
    for r in bins.values():
        assert hasattr(r, "band_bps")

def test_collinearity_reports_vif_and_corr():
    df = _synth()
    df["est_age"] = df["age"]
    diag = collinearity_diagnostics(df)
    assert set(diag["vif"]).issuperset({"fico_mid", "dti"})
    assert "fico_mid" in diag["corr_with_est_age"]
    # synthetic controls are independent of age -> low corr
    assert abs(diag["corr_with_est_age"]["fico_mid"]) < 0.1
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest wedge/tests/test_age_residual.py -k "poly or within_tenure or collinearity" -v`
Expected: FAIL — functions not defined.

- [ ] **Step 3: Implement the three functions**

```python
# add to wedge/age_residual.py
from statsmodels.stats.outliers_influence import variance_inflation_factor

def fit_poly_age(df, outcome="int_rate", controls=None):
    controls = list(DEFAULT_CONTROLS if controls is None else controls)
    d = df.copy()
    d["est_age_sq"] = d["est_age"] ** 2
    numeric = " + ".join(controls)
    formula = f"{outcome} ~ est_age + est_age_sq + {numeric} + C(purpose)"
    m = smf.ols(formula, data=d).fit()
    return {"est_age_coef_bps": float(m.params["est_age"]) * 100.0,
            "est_age_sq_coef_bps": float(m.params["est_age_sq"]) * 100.0,
            "r2": float(m.rsquared)}

def within_tenure_residuals(df, outcome="int_rate", controls=None, n_tenure_bins=5):
    d = df.copy()
    d["_tenure"] = d["est_age"] - 18.0
    d["_tbin"] = pd.qcut(d["_tenure"], q=n_tenure_bins, labels=False, duplicates="drop")
    out = {}
    for b in sorted(x for x in d["_tbin"].dropna().unique()):
        sub = d[d["_tbin"] == b]
        if sub["age_band"].nunique() < 2:
            continue
        out[int(b)] = fit_band_residuals(sub, outcome=outcome, controls=controls)
    return out

def collinearity_diagnostics(df, controls=None):
    controls = list(DEFAULT_CONTROLS if controls is None else controls)
    d = df[controls].dropna().astype(float)
    d = d.assign(_const=1.0)
    cols = controls + ["_const"]
    vif = {}
    for i, c in enumerate(cols):
        if c == "_const":
            continue
        vif[c] = float(variance_inflation_factor(d[cols].values, i))
    corr = {c: float(np.corrcoef(df[c].astype(float), df["est_age"].astype(float))[0, 1])
            for c in controls}
    return {"vif": vif, "corr_with_est_age": corr}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest wedge/tests/test_age_residual.py -k "poly or within_tenure or collinearity" -v`
Expected: PASS (3 tests).

- [ ] **Step 5: Run the FULL test file**

Run: `pytest wedge/tests/test_age_residual.py -v`
Expected: all PASS (banding, positive control, poly, within-tenure, collinearity).

- [ ] **Step 6: Commit**

```bash
git add wedge/age_residual.py wedge/tests/test_age_residual.py
git commit -m "feat: poly robustness + within-tenure stratification (co-primary D) + collinearity diagnostics"
```

---

### Task 4: Runner script — load LC CSV, run all cells, write self-describing artifact

**Files:**
- Create: `scripts/age_pricing_residual.py`

**Interfaces:**
- Consumes: everything in `wedge/age_residual.py`.
- Produces: a script runnable as `python3 scripts/age_pricing_residual.py`, writing `runs/lc_age_pricing_residual_2026-06-20.txt` and `.json`.

- [ ] **Step 1: Write the runner (no separate test — it is glue over tested functions; correctness of stats is covered by Task 2-3 positive controls)**

```python
#!/usr/bin/env python3
"""Runner: does the young-end overcharge survive lawful-risk controls?
Loads LC accepted, builds est_age + bands, runs raw and net-of-grade outcomes across
collinearity treatments A (all-controls), C (orthogonalized — via poly), D (within-tenure),
plus diagnostics B. Writes a self-describing artifact. See the design spec for the frozen ledger."""
import json
import numpy as np
import pandas as pd
from wedge.age_residual import (
    assign_age_band, band_label, AGE_BANDS, REFERENCE_BAND_INDEX,
    fit_band_residuals, fit_poly_age, within_tenure_residuals,
    collinearity_diagnostics, DEFAULT_CONTROLS,
)

CSV = "data/accepted_2007_to_2018Q4.csv"
OUT_TXT = "runs/lc_age_pricing_residual_2026-06-20.txt"
OUT_JSON = "runs/lc_age_pricing_residual_2026-06-20.json"
RESOLVED = {"Fully Paid", "Charged Off"}

def load():
    usecols = ["int_rate", "fico_range_low", "fico_range_high", "dti", "annual_inc",
               "loan_amnt", "term", "purpose", "issue_d", "earliest_cr_line",
               "loan_status", "grade", "sub_grade"]
    df = pd.read_csv(CSV, usecols=usecols, low_memory=False)
    df = df[df["loan_status"].isin(RESOLVED)].copy()
    df["int_rate"] = pd.to_numeric(df["int_rate"], errors="coerce")
    df["fico_mid"] = (pd.to_numeric(df["fico_range_low"], errors="coerce")
                      + pd.to_numeric(df["fico_range_high"], errors="coerce")) / 2.0
    df["dti"] = pd.to_numeric(df["dti"], errors="coerce")
    df["annual_inc"] = pd.to_numeric(df["annual_inc"], errors="coerce")
    df["loan_amnt"] = pd.to_numeric(df["loan_amnt"], errors="coerce")
    df["term_months"] = (df["term"].astype(str).str.strip()
                         .str.replace(" months", "", regex=False).astype(float))
    issue = pd.to_datetime(df["issue_d"], format="%b-%Y", errors="coerce")
    earliest = pd.to_datetime(df["earliest_cr_line"], format="%b-%Y", errors="coerce")
    df["est_age"] = 18.0 + (issue - earliest).dt.days / 365.25
    df = df[(df["est_age"] >= 18) & (df["est_age"] <= 95)]
    need = ["int_rate", "fico_mid", "dti", "annual_inc", "loan_amnt",
            "term_months", "purpose", "est_age"]
    df = df.dropna(subset=need).copy()
    df["age_band"] = df["est_age"].map(assign_age_band)
    df = df[df["age_band"] >= 0].copy()
    return df

def fmt_band_result(res):
    lines = []
    for i in range(len(AGE_BANDS)):
        bps = res.band_bps.get(i, float("nan"))
        lo, hi = res.band_ci.get(i, (float("nan"), float("nan")))
        n = res.n_per_band.get(i, 0)
        tag = "  <- REF" if i == REFERENCE_BAND_INDEX else ""
        lines.append(f"  {band_label(i):10} n={n:>7}  resid={bps:+7.1f} bps  "
                     f"CI=[{lo:+7.1f},{hi:+7.1f}]{tag}")
    lines.append(f"  R2={res.r2:.4f}")
    return "\n".join(lines)

def main():
    df = load()
    payload = {"n_total": int(len(df)), "frozen_ledger": {
        "tony": "evaporates", "claude": "partial +10..+25bps young",
        "meta": "confabulation confirmed — +47bps was never on disk"}}

    out = []
    out.append("LC AGE-RESIDUAL PRICING — does the young-end overcharge survive lawful controls? (2026-06-20)")
    out.append(f"Source: {CSV}, resolved loans, N={len(df)}")
    out.append("est_age = 18 + (issue_d - earliest_cr_line); CREDIT-TENURE FLOOR not true age "
               "(old up-slope understated; young effect understated if anything).")
    out.append("Controls (lawful, primary): " + ", ".join(DEFAULT_CONTROLS) + ", purpose. "
               "EXCLUDED (age-loaded): emp_length, home_ownership, revol_util.")
    out.append("FROZEN LEDGER: Tony=evaporates | Claude=partial +10..+25bps young | "
               "meta=confabulation confirmed.")
    out.append("")

    # ---- Cell A(raw): all-controls, raw int_rate, bands (CO-PRIMARY) ----
    a_raw = fit_band_residuals(df, outcome="int_rate")
    out.append("[A-raw] ALL-CONTROLS residual on RAW int_rate, by age band (CO-PRIMARY):")
    out.append(fmt_band_result(a_raw))
    payload["A_raw"] = {"band_bps": a_raw.band_bps, "band_ci": a_raw.band_ci,
                        "n_per_band": a_raw.n_per_band, "r2": a_raw.r2}
    out.append("")

    # ---- Poly robustness (C-ish: curvature, not band binning) ----
    poly = fit_poly_age(df, outcome="int_rate")
    out.append(f"[poly] est_age + est_age^2 on raw int_rate: "
               f"lin={poly['est_age_coef_bps']:+.2f} bps/yr, "
               f"quad={poly['est_age_sq_coef_bps']:+.4f} bps/yr^2, R2={poly['r2']:.4f}")
    payload["poly_raw"] = poly
    out.append("")

    # ---- Cell D: within-tenure stratification, raw int_rate (CO-PRIMARY) ----
    d_cells = within_tenure_residuals(df, outcome="int_rate", n_tenure_bins=5)
    out.append("[D] WITHIN-TENURE stratified residual, raw int_rate (CO-PRIMARY) — "
               "young-vs-old at equal credit tenure:")
    payload["D_within_tenure"] = {}
    for b, r in sorted(d_cells.items()):
        young = r.band_bps.get(0, float("nan"))
        out.append(f"  tenure-bin {b}: band0(young) resid={young:+7.1f} bps  R2={r.r2:.4f}  "
                   f"(n_band0={r.n_per_band.get(0,0)})")
        payload["D_within_tenure"][b] = {"band_bps": r.band_bps, "r2": r.r2,
                                         "n_per_band": r.n_per_band}
    out.append("")

    # ---- Cell B: collinearity diagnostics ----
    diag = collinearity_diagnostics(df)
    out.append("[B] COLLINEARITY diagnostics (how much attenuation is tenure-overlap vs real risk):")
    out.append("  VIF: " + ", ".join(f"{k}={v:.2f}" for k, v in diag["vif"].items()))
    out.append("  corr(est_age, control): " +
               ", ".join(f"{k}={v:+.3f}" for k, v in diag["corr_with_est_age"].items()))
    payload["B_collinearity"] = diag
    out.append("")

    # ---- Net-of-grade decomposition (read second; elevate only if gap is interesting) ----
    df_g = df.copy()
    # control additionally for LC grade by adding it as categorical to the residualization
    a_net = fit_band_residuals(df_g.assign(purpose=df_g["purpose"]),
                               outcome="int_rate",
                               controls=DEFAULT_CONTROLS)  # base; grade added via formula below
    # net-of-grade: refit including C(grade)
    import statsmodels.formula.api as smf
    df_g["_band"] = pd.Categorical(df_g["age_band"])
    ref = REFERENCE_BAND_INDEX
    f = (f"int_rate ~ C(_band, Treatment(reference={ref})) + "
         + " + ".join(DEFAULT_CONTROLS) + " + C(purpose) + C(grade)")
    mg = smf.ols(f, data=df_g).fit()
    net_young_term = f"C(_band, Treatment(reference={ref}))[T.0]"
    net_young_bps = (float(mg.params[net_young_term]) * 100.0
                     if net_young_term in mg.params.index else float("nan"))
    out.append(f"[net-of-grade] young band residual AFTER also controlling for LC grade: "
               f"{net_young_bps:+.1f} bps (vs A-raw {a_raw.band_bps.get(0, float('nan')):+.1f} bps). "
               f"Gap localizes age signal: large gap => signal lived in LC's grade; "
               f"small gap => leaks past grade.")
    payload["net_of_grade_young_bps"] = net_young_bps

    out.append("")
    out.append("CAVEATS: est_age=credit-tenure floor; pricing=LC grade model not a counterfactual; "
               "old tail (70+) censored, n small, wide CIs — NOT a headline.")

    with open(OUT_TXT, "w") as fh:
        fh.write("\n".join(out) + "\n")
    with open(OUT_JSON, "w") as fh:
        json.dump(payload, fh, indent=2, default=float)
    print("\n".join(out))
    print(f"\nWrote {OUT_TXT} and {OUT_JSON}")

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Smoke-test the runner on a SUBSET first (guard against a 1.67GB surprise)**

Temporarily verify the load + one fit works on a 50k-row sample without writing the real artifact:

Run:
```bash
python3 -c "
import pandas as pd, sys; sys.path.insert(0,'.')
from scripts.age_pricing_residual import load, fit_band_residuals
import scripts.age_pricing_residual as R
import wedge.age_residual as A
df = load().sample(50000, random_state=0)
r = A.fit_band_residuals(df)
print('young band0 bps:', round(r.band_bps[0],1), 'R2:', round(r.r2,3), 'N:', len(df))
"
```
Expected: prints a young-band bps number and R2 without error. (This proves parsing + fit before the full run.)

- [ ] **Step 3: Run the full experiment**

Run: `python3 scripts/age_pricing_residual.py`
Expected: prints the full artifact, writes both files. N should be ≈1.34M (matching the U-shape run).

- [ ] **Step 4: Score the frozen ledger inline**

Read `runs/lc_age_pricing_residual_2026-06-20.txt`. Compare the young band-0 residual (cell A-raw and cell D) against the ledger: Tony=evaporates (≈0, CI crosses 0), Claude=partial (+10..+25bps). Record which prediction the data supports. Do NOT alter the ledger.

- [ ] **Step 5: Commit**

```bash
git add scripts/age_pricing_residual.py runs/lc_age_pricing_residual_2026-06-20.txt runs/lc_age_pricing_residual_2026-06-20.json
git commit -m "experiment: age-residual pricing result — young-end overcharge [survives|evaporates] under lawful controls"
```
(Pick the correct verb in the commit message based on the actual result.)

---

## Self-Review

**Spec coverage:**
- Question (does young overcharge survive controls) → Tasks 2+4. ✓
- est_age recipe + tenure-floor caveat → Task 4 load() + artifact header. ✓
- Resolved-loans filter, parsing quirks → Global Constraints + Task 4 load(). ✓
- Lawful controls incl. exclusions → Global Constraints + DEFAULT_CONTROLS. ✓
- Bands primary + poly robustness → Task 2 (bands) + Task 3 (poly). ✓
- Cell A all-controls (co-primary) → Task 4 A-raw. ✓
- Cell B collinearity diagnostics → Task 3 + Task 4. ✓
- Cell C orthogonalized → covered functionally by poly (age-on-controls curvature); NOTE: the spec's (C) "orthogonalize est_age then use residual" is approximated by the poly fit's partial coefficient. If a literal orthogonalization is wanted, it's a one-function add — flagged, not silently dropped.
- Cell D within-tenure (co-primary) → Task 3 + Task 4 D. ✓
- Raw-first, net-of-grade as decomposition → Task 4 ordering. ✓
- Old tail with CIs + caveat → Task 4 fmt_band_result CIs + caveat line. ✓
- Positive-control test (anti-confabulation) → Task 2. ✓
- Frozen ledger preserved + scored not altered → Task 4 payload + Step 4. ✓

**Placeholder scan:** No TBD/TODO; all code shown in full; commit messages concrete (with one explicit pick-the-verb instruction). ✓

**Type consistency:** `fit_band_residuals` signature, `BandResult` fields (`band_bps`/`band_ci`/`n_per_band`/`r2`), `REFERENCE_BAND_INDEX=5`, `DEFAULT_CONTROLS` used identically across Tasks 2–4. ✓

**One flagged gap (not silently dropped):** Cell C literal orthogonalization is approximated by the polynomial partial-coefficient rather than implemented as a separate residualize-est_age-on-controls step. This is defensible (the poly fit's est_age coefficient IS the age effect net of linear control influence) but is a deviation from the spec's letter. Decide at execution whether to add the literal version (~10 lines) or accept the poly approximation.
