# Age-Residual Pricing Experiment — Design

**Date:** 2026-06-20
**Script:** `scripts/age_pricing_residual.py`
**Artifact:** `runs/lc_age_pricing_residual_2026-06-20.txt` (+ JSON coefficient sidecar)
**Lineage:** resolves the contradiction between [[project_age_extractable_surface]] (claims +47bps "MEASURED")
and [[project_age_mispricing_anchor_handoff]] (flags +47bps as the unverified blocking gap).
Forensic verdict (2026-06-20): the residual table and +47bps appear **nowhere** in git history or on disk —
the cited artifact `runs/lc_age_default_ushape_2026-06-12.txt` contains only the RAW-band U-curve and raw
monotone pricing gradient, no residualization. The "MEASURED" claim was confabulated. This run produces the
number for real, or falsifies it.

## Question

After controlling for lawful risk factors, does the young end pay **over** their lawful-risk profile
(does the ~+47bps overcharge survive controls), or does it evaporate into "they are genuinely riskier"?

A null result is a fine, publishable-to-ourselves outcome. We are hunting an insight, not defending a paper.
If the overcharge evaporates, we record it and move on.

## Frozen prediction ledger (set BEFORE the run)

- **Tony:** evaporates — the raw gradient is mostly risk confound.
- **Claude:** partial survival — young-band residual shrinks from +47 but stays positive,
  ~ **+10 to +25 bps**, not +47 and not zero. Old-end −88/−96 bps does NOT cleanly survive
  (censoring + n=729 at 70+).
- **Meta (already scored ✓):** the +47bps / residual-default table was confabulated, not lost.
  Confirmed by `git log -S` finding the numbers nowhere.

Scoring: the fresh artifact is ground truth, on (a) sign, (b) survives-vs-evaporates, (c) magnitude band.

## Data

- Source: `data/accepted_2007_to_2018Q4.csv`, full file (~1.67 GB, 151 cols).
- Resolved loans only: `loan_status ∈ {Fully Paid, Charged Off}` (matches U-shape run N≈1.34M).
- `est_age = 18 + (issue_d − earliest_cr_line)` in years; both parsed `%b-%Y`. Clip to [18, 95].
- Drop rows missing est_age / int_rate / any primary control.
- **est_age is a credit-tenure FLOOR, not true age** — a 70yo and a 45yo with 25+yr files collapse;
  old tail partially censored → old up-slope understated, young effect if anything understated.
  Carried as a caveat in the artifact; sign robust, magnitude is a floor.

## Model: load once, read across a grid

One dataframe load dominates cost; every cell below is a cheap readout or re-fit off it.

### Lawful controls (primary)
FICO (midpoint of `fico_range_low`/`fico_range_high`), `dti`, `annual_inc`, `loan_amnt`, `term`, `purpose`.
These constitute the "lawful risk profile." **Deliberately EXCLUDED from primary** (age-loaded, risk laundering
age into "lawful" controls): `emp_length`, `home_ownership`, `revol_util`. Revisited as a sensitivity ONLY if
a real effect survives — no sense armoring a null.

### Age functional form
- **Bands (PRIMARY):** [18,25) [25,30) [30,35) [35,40) [40,45) [45,50) [50,55) [55,60) [60,70) [70,95].
  Each band → a directly-readable bps residual vs. a mid-age reference band (40-45 or 45-50).
  Preserves the U-curvature that a single linear age term would erase — erasing it is the exact
  audit-blindness the U-shape finding documents.
- **est_age + est_age² (ROBUSTNESS):** confirms curvature is not a binning artifact.

### Outcome axis
- **(1) raw `int_rate`** — the harm claim: does the borrower pay over lawful-risk profile. **Read first.**
- **(2) `int_rate` net of LC grade/sub_grade** — decomposition: is the age signal inside LC's grade
  decision, or does it leak past it? Elevated to its own finding only if the raw-vs-net gap is interesting;
  otherwise reported as a decomposition of (1), not a third headline.

### Collinearity treatments (the est_age proxy is built from credit tenure, so controls can absorb it)
- **(A) all-controls residual** — most conservative; includes mechanical tenure overlap. **Co-primary.**
- **(B) collinearity diagnostics** — VIF + corr(est_age, each control); measures how much of any attenuation
  is tenure-overlap vs. genuine risk. A readout, not a re-fit.
- **(C) orthogonalized est_age** — residualize est_age on controls, use the age-not-explained-by-risk part.
- **(D) within-tenure-band stratification** — compare young-vs-old at EQUAL credit tenure, sidestepping
  collinearity by conditioning on it. **Co-primary with (A)** — the hardest falsification test:
  if the young overcharge survives even at equal tenure, the "they're just riskier" defense collapses hardest.

**The insight is the PATTERN across cells, not a single number.**
Agreement across A/C/D = robust. Disagreement (e.g. A evaporates but D survives) = the effect localizes to
within-tenure comparison, which is itself a finding. Any cell may return null.

## Old tail
Young-end (n>400k under 35) is the headline. Old-end (70+, n=729, censored) reported **with confidence
intervals and the credit-tenure-floor caveat**, explicitly NOT a headline.

## Testing
Analysis script, so TDD is narrow but real: a synthetic-data **positive control** — plant a known age residual
(e.g. +30 bps on the young band, controls neutral) and assert the residualization recovers it within tolerance.
Guards against the exact failure mode that produced the confabulated number: a procedure that reports a residual
it never actually computed.

## Output
- `runs/lc_age_pricing_residual_2026-06-20.txt` — self-describing: ledger, every caveat, the cell grid,
  per-band bps residuals with CIs, the A/C/D pattern readout, the raw-vs-net-of-grade decomposition.
- JSON sidecar of coefficients for reproducibility.
- No paper, no thread. Just: did we find an insight — yes or no.

## Caveats carried in the artifact
- est_age = credit-tenure floor, not true age (old up-slope understated; young effect understated if anything).
- Pricing reflects LC's grade model, not a counterfactual lawful price.
- Old tail censored (n=729) — old-end numbers are floor estimates with wide CIs.
