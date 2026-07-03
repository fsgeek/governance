# Item 4a resolved on paper — the calibration floor is category B, and it unblocks detector #4 in ONE direction

Date: 2026-07-03. Branch `age-pricing-residual`. Resolves the highest-risk deferred item (4a) of
`docs/superpowers/specs/2026-07-01-risk-justified-price-map-design.md` — the frozen decision there
said detector #4 is BLOCKED until the non-circular-calibration source for the declared map
`risk_justified_price(d) = P0 + L*d` is resolved on paper. This document is that resolution.

Method: two blind adversaries, dispatched WITHOUT the author's conclusion, given the frozen artifacts
and the scripts. One hired to REFUTE the block by finding a working standard identification strategy;
one hired to classify the block's strength (theorem-grade vs assumption-conditional vs merely-unsolved).
Both ran numerical simulations on the exact DGP, not rhetoric. They converged on the structural facts
and DISAGREED productively on the strength classification — which is what makes the result trustworthy
rather than an echo of the author's prior.

## The author's prior, recorded and then FALSIFIED (against interest)

Going in, the seductive frame was: "no non-circular calibration exists -> this is a FOURTH escape
collapsing to the same unobservable -> it welds to Result 1's measure-one non-identifiability theorem
(the lineage's '6 escapes -> 1 unobservable' shape)." This frame is WRONG in its strong form, and the
falsification is recorded here rather than softened, per the discipline that self-serving impossibility
reframes of one's own failed design are the trap (`feedback-impossibility-from-failed-design`).

It is wrong because the honest and laundered worlds are NOT observationally identical on the full
cohort. Simulation (adversary 2, on the frozen DGP): under lambda=0.3 a bin's realized default DILUTES
(0.376 -> 0.227) because laundered protected applicants pushed up from lower true-risk R default less
than their bin-mates; an EXTERNAL declared map (500,300) yields wedge -7.4 (honest) vs +29.7
(laundered). The distinguishing information EXISTS in `(price, default, G)`. Result 1's theorem-grade
non-identifiability holds ONLY on the unprotected-only cohort (verified: bin default 0.376/0.776
identical across worlds there). Borrowing Result 1's authority for item 4a would have been exactly the
overclaim this project's discipline exists to catch. It is NOT that impossibility.

## What IS true (verified numerically by both adversaries, machine precision)

### Fact A — self-calibration is provably vacuous (the tautology, exact)
For a LINEAR map calibrated by OLS on a sample and evaluated on that same sample, the population-mean
wedge is IDENTICALLY 0 by the OLS normal-equations orthogonality. The first normal equation
(d/dP0 = 0) is `sum(price_i - P0 - L*d_i) = 0`, i.e. `mean(price) = P0 + L*mean(default)`, i.e.
`mean(wedge) = mean(residual) = 0` for ANY data whatsoever. Verified: residual mean ~1e-14. This is
what `scripts/single_projection_detector.py:111` does (`smf.ols("price ~ default", ...).fit()` — the
line-110 comment claims "declared, not fitted per-run" while line 111 literally `.fit()`s it; the
comment contradicts the code). Detector #1's death (`ae7af3d`), relocated one level up, exactly as the
map-design note warned.

### Fact A' — a NEW correction to the map-design note's Attempt 3 (found by adversary 2)
The tautology is exact ONLY when estimation-weighting matches aggregation-weighting. Unweighted
bin-level OLS followed by POPULATION-weighted wedge aggregation is NOT identically zero — it leaves a
small STRUCTURAL residual (~+0.0038, not sampling noise). This is WORSE, not better: a near-zero that
is neither a clean algebraic zero NOR real signal, on which GUARD A ("lambda=0 null spans 0") could
pass spuriously. Any detector #4 that mixes weighting schemes manufactures a fake pass. Record: keep
estimation-weighting and aggregation-weighting IDENTICAL, or the "null" is a weighting artifact.

### Fact B — the population-aggregate wedge is STRUCTURALLY lambda-blind (found by adversary 1)
Because grade G is QUANTILE bins, laundering re-normalizes bin populations and holds both marginals
fixed: mean(price)=620.0 and mean(default)=0.4994 are invariant across lambda in {0,0.1,0.2,0.4} to
3+ decimals. A LINEAR map's population wedge collapses (Attempt 2 of the parent note) to
`mean(price) - (P0 + L*mean(default))` — a function of those two invariant marginals ONLY. Therefore
WHATEVER `(P0,L)` any calibration supplies, the population-aggregate wedge carries NO lambda-signal.
The calibration question is, at the population level, a DECOY. The genuine signal is bin-level dilution;
reading it requires the honest per-bin price — the object with no endogenous source (Fact A). TWO
stacked obstructions; the frozen note named only the first.

## The classification the two adversaries converged on: category B (not A, not C)

- NOT category A (theorem-grade, like Result 1): provably unreachable, because a difference between
  the worlds DOES exist in the full-cohort observable (Fact, above). No Result-1-style distributional
  identity is available on the full cohort. Do NOT cite Result 1's authority for this.
- NOT category C ("just an unsolved calibration"): two of the three natural endogenous routes are
  closed BY PROOF — self-fit is vacuous (Fact A), and the one provably-honest cohort (unprotected-only)
  is provably SILENT (Result 1). That is more than an engineering gap.
- Category B — a genuine floor on a CLASS OF ESTIMATORS (endogenous, self-calibrated), not a floor on
  the INFORMATION in the data. The honest baseline is either vacuous (self-fit) or silent (Result-1
  cohort); therefore `(P0,L)` requires an EXOGENOUS identifying restriction. The height of the floor
  is set by WHICH restriction you are willing to declare.

## The four buckets (the trichotomy was not exhaustive — adversary 2's correction)

The map-design note's implicit trichotomy for calibration sources was {self-fit-circular /
external-rate-sheet / assume-a-cohort-honest}. Adversary 1 confirmed every STANDARD strategy lands in
one of those three and none escapes (table below). But adversary 2 named a FOURTH bucket the note
missed: identification-by-RESTRICTION. This is the bucket detector #4 actually lives in.

| Strategy | Verdict | Bucket |
|---|---|---|
| Self-fit OLS on the measurement sample | wedge ≡ 0 by algebra, honest AND laundered alike; zero information | (i) circular |
| Cross-vintage temporal hold-out | fails on Fact B (pop wedge lambda-blind) even when honest-vintage assumption granted; and false-positives under lawful base-rate drift (+60bps) | (iii) assumes-honest-cohort AND doesn't work |
| Instrumental variables | no valid instrument: any Z shifting default reaches price ONLY through the contaminated grade channel; exclusion restriction fails by construction; 2SLS tracks the contamination | (iii) exclusion = the non-identifiability |
| RD at a grade/rate-sheet cutoff | recovers the local price JUMP (=loading), not P0 and not global L; wrong estimand | recovers wrong object |
| Held-out honest reference SUBPOPULATION | "known-honest cohort" = already knowing lambda=0 for them = the conclusion; the one provably-lambda-free cohort is Result-1 silent | (iii) presumes the answer |
| Manski bounds / partial ID | identified set for honest-vs-laundered is the trivial [everything] on the identifiable cohort | (iii) non-id IS the bound width |
| External declared rate sheet | WORKS, but is an external declaration (and "declared != actual honest rule" is its own confound) | (ii) external declaration |
| **Identification-by-restriction (the 4th bucket)** | **partial declared STRUCTURE over-identifies the residual: nonlinearity (breaks the linear collapse of Fact B), monotonicity / no-arbitrage, P0 = cost-of-funds pin, or a cross-vintage stability EXCLUSION (lambda ⊥ vintage-of-honest-rule). Still assumptions, but WEAKER than a full rate sheet, and SOME are testable.** | **(iv) declared restriction — where detector #4 lives** |

## FROZEN RESOLUTION (item 4a is now resolved on paper — detector #4 is unblocked, conditionally)

1. The architectural instinct of the parent note STANDS: `(P0,L)` enters as a DECLARED modeling choice,
   collapsing into the instrument's spine (`project_instrument_with_model_in_light_path`: "the risk
   model goes in the light path, declared not hidden"). The declaration IS the integrity.
2. But the JUSTIFICATION is category B, NOT the impossibility the author first reached for. State it
   as: "endogenous self-calibration is PROVABLY VACUOUS (wedge ≡ 0 by OLS orthogonality) and the one
   provably-honest cohort is PROVABLY SILENT (Result 1), so `(P0,L)` requires an EXOGENOUS identifying
   restriction; which restriction sets the floor's height, and its sensitivity ships with every
   result." Do NOT cite Result 1's authority.
3. ABANDON the population-aggregate wedge under a linear map — it is STRUCTURALLY lambda-blind (Fact B),
   independent of calibration. This kills the "bin-count-invariant population number" that Attempt 2 of
   the parent note offered as the safe, well-posed statistic: it is well-posed AND blind. Detector #4
   must use EITHER (a) a NONLINEAR declared map (breaks the marginal collapse, retains bin-level
   resolution) OR (b) per-bin wedges reported directly (not aggregated), each with its own bin-count
   stability + noise check. The linear-aggregate is dead either way.
4. If any weighting is used, estimation-weighting and aggregation-weighting MUST match (Fact A'), or
   the null is a weighting artifact and GUARD A passes spuriously.
5. Detector #4 MAY be built now, but ONLY as a DECLARED-RESTRICTION detector (bucket iv): a declared
   `(P0,L)` (or nonlinear curve, or cross-vintage stability restriction), with the wedge reported
   per-bin, and with a SENSITIVITY-TO-THE-DECLARATION analysis as a first-class output (not an
   afterthought), because the floor's height is exactly the declaration's contestability. It MAY NOT
   self-calibrate (Fact A), MAY NOT report a linear population aggregate (Fact B), and MAY NOT claim a
   theorem-grade honest zero (category B, not A).

## Read-order / provenance
Parent: `docs/superpowers/specs/2026-07-01-risk-justified-price-map-design.md` (item 4a).
Grandparent: `docs/superpowers/specs/2026-07-01-single-projection-identifiability.md` (Result 1 = the
category-A theorem this is NOT). Killed detectors: `ae7af3d` (#1, in-sample circular), `c1c0a1e` (#3,
unit-incommensurable). The two adversary transcripts are the evidence; their numerical checks (tautology
~1e-14, dilution 0.376->0.227, marginal-invariance across lambda, weighting-mismatch residual +0.0038)
are reproducible on the frozen DGP in `scripts/single_projection_detector.py`.
