# Age-pricing results, retrofit into instrument-with-model-in-light-path form

2026-06-29 — synthesis/retrofit draft (no new runs). Branch `age-pricing-residual`.

The frame (`project-instrument-with-model-in-light-path.md`) requires every empty-chair
result to ship as **DISPARITY + DECOMPOSITION BY REALIZED RISK + DECLARED RISK-MODEL
(assumptions named as a hostile expert would attack them) + SENSITIVITY-TO-MODEL-WRONGNESS**,
never as a bare "harm found." Below, each of the five age-pricing results is recast into
that four-part form, every number tied to its on-disk artifact.

**Verification status:** every headline number in the five memos was cross-checked against
a JSON/txt artifact on disk. All tied out. The numbers that could NOT be tied to an artifact
are FLAGGED inline and collected at the end. (Author confidence: HIGH on the numbers; MEDIUM
on phrasing the hostile-expert attacks, which are my construction, not a defendant's brief.)

Convention: "young" = band `[18,25)` = band index 0. Reference band = `[45,50)` (index 5)
on LC, `45-54` on HMDA. bps = basis points of interest rate; pp = percentage points.

---

## 1. RESIDUAL — the raw price gradient survives lawful controls

**Artifact:** `runs/lc_age_pricing_residual_2026-06-20.json` (+`.txt`). N = 1,344,935 LC
resolved loans. Reference band `[45,50)`.

| Part | Content | Cite |
|---|---|---|
| **DISPARITY** | Young `[18,25)` pay **+208.7 bps** over reference on raw `int_rate`, net of lawful controls (FICO/DTI/income/loan/term/purpose). CI [205.1, 212.3], n_young = 91,650. Monotone decline +104.0/+52.1/+30.6/+17.5 through mid-bands; old end mildly negative (−11.7 to −14.5 @ 50–60); 70+ noisy (CI crosses 0). R²=0.41. | `A_raw.band_bps["0"]`=208.70; `band_ci["0"]`; `r2`=0.4059 |
| **DECOMPOSITION** | Add LC **grade** as a control → young drops **+208.7 → +26.7 bps** (CI not stored; point in JSON). **Grade carries ~182 bps** of the age pricing. Age is near-orthogonal to the lawful controls (corr ≤ 0.16, VIF ≈ 1.0) — *that* is why the gap survives FICO/DTI: they have no purchase on age. Orthogonalized-age cell ≈ raw (+207.5), confirming non-degeneracy. | `net_of_grade.young_bps`=26.67; `B_collinearity.corr_with_est_age` (max 0.1596 = loan_amnt); `vif` (all ≈1.0–1.3); `C_orthogonalized.band_bps["0"]`=207.51 |
| **DECLARED RISK-MODEL** | (1) **`est_age = 18 + credit_tenure`** — "age" is *credit tenure*, not observed age. A 25yo and 45yo with equal tenure are identical to this analysis. (2) **LC grade is treated as a candidate risk yardstick**, not assumed legitimate — the whole point is the +182 bps that lives *inside* grade. (3) Resolved-loans-only universe (survivorship boundary inherited). Cell D ("within-tenure") is reported **VOID** by construction (corr(est_age,tenure)=1.0) — not faked, named void. | `D_within_tenure.status`="void"; `frozen_ledger` |
| **SENSITIVITY** | *If `est_age` ≠ age* (the load-bearing attack): the entire +208.7 may be a credit-tenure gradient mislabeled. **This is exactly what result #5 (HMDA) tests and partly confirms** — see §5. *If grade is a legitimate risk instrument*: the lawful disparity is only +26.7 bps and the headline shrinks 8×. *If grade is age-laundering*: the +182 bps is the harm. The residual alone **cannot** decide grade's legitimacy — results #2/#3/#4 are the downstream discriminants. | — |

Hostile-expert one-liner: *"You measured how long someone has had credit and called it age,
then blamed a risk grade you never showed was illegitimate."*

---

## 2. GRADE-DEFAULT — does grade's age wedge float free of realized default?

**Artifact:** `runs/lc_age_grade_default_2026-06-22.json` (+`.txt`). N = 1,344,935, 20.0%
default (n_default = 268,488). Yardstick = **default-justified price** (the rate a loan's
realized default maps to, estimated empirically — NOT LC's own price).

| Part | Content | Cite |
|---|---|---|
| **DISPARITY** | Against a default-justified yardstick, young `[18,25)` are priced **+134.0 bps PAST** what their realized default justifies (isotonic map) / **+136.2** (decile map). CI [131.5, 136.4]. The gradient declines monotonically (+33.2 @ 25–30) then **flips sign negative**: −9.3/−26.1/−35.5/−53.5/−66.4/**−77.7** @ 55–60. **The old are SUBSIDIZED below their default-justified rate** by the same instrument. 70+ (n=728) −64.9, CI widens. | `map_isotonic.corpus.band_bps` ("0"=133.98 … "7"=−77.72); `map_decile.corpus.band_bps["0"]`=136.23 |
| **DECOMPOSITION** | Re-fit the default→price map **within each grade**: young excess collapses **+134.0 → +14.4 bps** (iso) / **+136.2 → +9.4** (decile). The **grade-laundering gap = +119.5 bps** (iso) — **~89–93% of the young excess vanishes once grade defines the yardstick.** Independent RAIL cross-check: grade's standardized young age-loading +0.41 ≫ default's +0.14 (gap +0.27); flips negative at the old end. Both map estimators agree on every sign and rank. | `map_isotonic.within_grade.band_bps["0"]`=14.43; `grade_laundering_gap_bps["0"]`=119.55; `rail.grade_age_loading_std["0"]`=0.4143, `default_age_loading_std["0"]`=0.1440, `grade_minus_default_loading["0"]`=0.2703 |
| **DECLARED RISK-MODEL** | (1) **`loss > 0.01` is the default proxy** (charge-off mass). (2) **The CORPUS map is age-blind / whole-population** — the young's higher thin-file default is BAKED INTO the yardstick, so the surviving young excess is **conservative** (biased toward zero). (3) `est_age = 18 + tenure` (lineage caveat). (4) Resolved-only. (5) The map itself (isotonic vs decile) is a modeling choice — addressed by running both. | `frozen_ledger.tony_caveat`; `pred_default_summary` (mean 0.1996) |
| **SENSITIVITY** | *If the corpus map under-counts young default* (proxy too coarse): the +134 is an over-estimate — but the within-grade collapse to +14 is robust to this because the same map fits both. *If grade is legitimate*: +134 → +14 says the residual harm is small (~14 bps), but the **+119.5 bps that grade absorbs is precisely the contestable quantity** — this result says grade *carries* the wedge, not that grade *is entitled* to. The L2-vs-L3 question (is grade honest?) is unresolved here and is what #3/#4 attack. *If `est_age` ≠ age*: see §5; on observed age the whole gradient may not exist. | — |

Hostile-expert one-liner: *"Your 'default-justified' rate is a curve you fit with a 1%-loss
cutoff; move the cutoff and your +134 moves with it."*

---

## 3. REALIZED-RETURN — did the overcharge become margin?

**Artifact:** `runs/lc_age_realized_return_2026-06-23.json` (+`.txt`). N = 1,344,935,
loss-positive 267,332 (19.9%). `realized_return = (total_pymnt + recoveries − funded_amnt)/funded_amnt`.

| Part | Content | Cite |
|---|---|---|
| **DISPARITY** | Pooled, the lender's **realized return on young `[18,25)` is −2.79 pp** net of lawful controls (CI [−3.05, −2.52]) — the lender LOSES 2.79 cents/dollar *more* on the youngest than on reference. **CORRECTED matured-vintage headline (2011–2014, ≥95% resolved, N=432,994): −1.76 pp** (CI [−2.20, −1.32]). Sign survives; ~1 pp of the pooled −2.79 was survivorship inflation. | `A_realized_return.band_val["0"]`=−2.785; `matured_vintage.A_band_val["0"]`=−1.760, CI [−2.200,−1.320]; `matured_vintage.n`=432994 |
| **DECOMPOSITION** | The overcharge IS realized cash but is eaten by default severity. Pooled: young interest collected **+1.18 pp**, young loss rate **+4.37 pp** → overcharge eaten **~3.7×**. **Matured: interest +1.11 pp, loss +3.27 pp → eaten ~3×.** Net-of-grade barely moves (−2.79 → −2.58 pooled): grade carries the realized-return gradient too. On matured data the gradient is *flat* — `[25,30)` (−1.91) is as negative as `[18,25)` (−1.76, CIs overlap) — the "worst at the very youngest / monotone" shading was a survivorship artifact and is DROPPED. | `C_interest.band_val["0"]`=1.181, `C_loss.band_val["0"]`=4.375; `matured_vintage` decomposition (interest 1.114, loss 3.275); `B_net_of_grade.young_net`=−2.579 |
| **DECLARED RISK-MODEL** | (1) **Resolved-only / survivorship** — THE attack here, and the reason for the matured-vintage correction: resolved-only pooling enriches the young for early-defaulters (they resolve faster); 2016–18 vintages are 11–67% resolved. The matured cell (2011–2014) is the survivorship-robust answer. (2) `est_age = 18 + tenure`. (3) Realized return UNDERSTATES the empty-chair harm by construction — the priced-out-profitable young who never borrowed are in NO file. (4) Deliberateness instrument: gradient cleanness, not height, signals intent. | `out_prncp_guard.pass`=true (median 0.0 → cashflow complete); `pos_control.recovered`=1.500 (planted +5pp on 30% → +1.50 recovered); `matured_vintage.gradient.slope_r2`=0.046 |
| **SENSITIVITY** | *If survivorship is worse than modeled*: the loss is anti-conservatively biased (young default faster → over-represented in resolved-early → return biased DOWN). Flag loudly; lean on the matured −1.76, not the pooled −2.79. *If the young are genuinely latently riskier* (the L3-honest story from `project-steering-detectability-result`): then −1.76 is **honest pricing of real risk**, and the "bias against the lender's own interest" reading has the sign backwards. **#4 is the discriminant that resolves this.** *If `est_age` ≠ age*: §5 — the population may be "short-tenure," not "young." | — |

Hostile-expert one-liner: *"Half your young loans haven't finished paying; you're scoring
a game at halftime and the young team's fastest losers already left the field."*

---

## 4. YOUNG-DEFAULT-vs-GRADE — do the young default ABOVE their grade (L2) or AT it (L3)?

**Artifact:** `runs/lc_young_default_vs_grade_2026-06-23.txt`. **FLAG: no JSON backing —
this result is `.txt`-only.** Matured 2011–2014, N = 432,994. default proxy = `loss > 0.01`.

| Part | Content | Cite |
|---|---|---|
| **DISPARITY** | Pooled net-of-grade, the young default **+0.70 pp above grade**, CI [+0.26, +1.13] (excludes 0). Statistically L2 (under-graded) but small and non-uniform. | `lc_young_default_vs_grade_2026-06-23.txt` L22 |
| **DECOMPOSITION** | Partitioned by grade, it's **BOTH**: **PRIME A/B/C: young +1.39 pp above grade**, CI [+0.91, +1.86], n=315,782 — grade UNDER-grades the good-credit young. **SUBPRIME D-G: −0.68 pp**, CI [−1.60, +0.24] (crosses 0) — grade prices young risk HONESTLY. Per-grade default table: A +1.90, B +2.02, C +2.04, D +0.23, E −0.85, F +0.64, G +9.89 (n~200 NOISE, ignored). | txt L26–L32, L13–L20 |
| **DECLARED RISK-MODEL** | (1) **`loss > 0.01` default proxy.** (2) **Grade A/B/C = "prime" partition** is a chosen cut. (3) Matured-vintage / survivorship-robust window (inherits #3's correction). (4) `est_age = 18 + tenure`. (5) Grade G excluded as noise (n~200) — read the n, not the verdict line. | txt L8–L9, L45–L46 |
| **SENSITIVITY** | *If grade is legitimate* (honest risk): the −0.68 in subprime says it IS honest there, so the harm is NOT "the bank over-prices all young." *The residual harm is the +1.39 pp prime sliver only* — this is the discriminant that **shrinks the headline** from "large general bias against interest (the +209 bps suggested)" to "modest, prime-grade-specific under-grading, right-signed, ~1.4 pp." *If `est_age` ≠ age* (§5): the +1.39 prime under-grading is a **tenure** under-grading, not an age one. | txt L34–L40 |

Hostile-expert one-liner: *"You found honest pricing in five of seven grades, threw out one
on sample size, and built a harm story on the two grades that survived."*

---

## 5. HMDA-NULL — the worked sensitivity test for the tenure-vs-age assumption

**This result IS the §1–§4 SENSITIVITY analysis for the single shared assumption
`est_age = 18 + tenure`.** Per the frame: take a stated model out of the light path
(here: tenure-as-age), re-measure, see if the photons survive.

**Artifact:** `runs/hmda_ri_age_pricing_2026-06-23.json` (+`.txt`). N = 18,218 (HMDA-RI 2022,
originated first-lien owner-occ purchase/refi). Lawful controls income/loan/ltv/term/purpose.
Reference `45-54`. Age is **observed** (bands), not imputed.

| Part | Content | Cite |
|---|---|---|
| **DISPARITY** | On observed age the young-pay-more gradient **EVAPORATES**: `<25` = **−6.6 bps**, CI [−18.3, +5.2] (**crosses 0**), n=395. Whole band structure flat-to-slightly-negative, NOT monotone, NO young premium: 25–34 = −5.8, 35–44 = −3.8, 55–64 = −4.4, 65–74 = −7.1, >74 = −2.9. R²=0.19. | `A_age_pricing["<25"].bps`=−6.568, ci [−18.31,+5.18], n=395 |
| **DECOMPOSITION** | **UNAVAILABLE — correctly reported, not faked.** HMDA has no realized default/return outcome, so the by-realized-risk decomposition cannot run. Per Tony's "no proxy = no theater" call, it is reported unavailable rather than proxied. | `hmda_ri_age_pricing_2026-06-23.txt` (memo: decomposition UNAVAILABLE) |
| **DECLARED RISK-MODEL** | The whole point: **removing** `est_age = 18 + tenure` from the light path. Remaining contestable assumptions of *this* substrate: one state (RI), one year (2022), **banded** (coarse) age, **NO credit score** (fewer risk controls than LC), MORTGAGE not personal-loan. The positive control is the declared-and-tested model-in-light-path. | `pos_control.recovered`=14.96 (planted +30 bps on 50% of `<25` → +14.96 recovered → estimator alive) |
| **SENSITIVITY (= the verdict on #1–#4)** | The positive control PASSES, so **the null is REAL, not a dead estimator** — the single strongest reason to trust a flat result. Therefore: the LC **+209 bps was substantially a CREDIT-TENURE artifact, not an age effect.** Re-LABELS (does not retract) the sprint: "young pay +209 bps" → "**short-credit-tenure borrowers** pay +209 bps"; the prime +1.39 pp under-grading is a **tenure** under-grading. BOUNDING (don't over-retract): one state/year/banded/no-score/mortgage — this guts the age-GENERALITY claim but does NOT make the LC tenure-gradient meaningless. The empty chair is real; its NAME was wrong ("thin-file / short-tenure," not "age"). | `A_age_pricing` (flat); `pos_control` PASS |

Hostile-expert one-liner — and here the expert is RIGHT: *"You measured tenure, not age."*
The HMDA null concedes it explicitly. That concession, not a harm, is the headline.

---

## CLOSING — the SHARED assumptions: the load-bearing joints of the whole arc

These are the joints a defendant's expert attacks first, and therefore the paper's real spine.
Listed by how much weight they carry across the five results.

| Shared assumption | Carried by | If it's wrong | Status |
|---|---|---|---|
| **`est_age = 18 + credit_tenure`** (tenure read as age) | #1 #2 #3 #4 (ALL LC results) | The entire age framing collapses to a *tenure* framing | **Already stress-tested by #5 — and it FAILED for "age."** The sprint is re-labeled to "short-credit-tenure." This is the single most load-bearing joint and it has been moved out of the light path. |
| **LC grade as the risk yardstick** (is it legitimate, or age/tenure-laundering?) | #1 (the +182 inside grade), #2 (grade-laundering gap +119.5), #3 (net-of-grade barely moves), #4 (the L2/L3 question) | If grade is legitimate, the lawful disparity is ~14–27 bps; if it launders, the ~120–182 bps is the harm | **Partly resolved by #4:** grade launders in PRIME (+1.39 pp) only, honest in subprime. The illegitimate sliver is small and prime-specific. |
| **Resolved-loans-only / survivorship** | #2 #3 #4 (every realized-outcome result) | Young over-represented among early-defaulters → loss/return biased DOWN at young end | **Audited in #3** via the matured-vintage (2011–2014, ≥95% resolved) cell; ~1 pp of the pooled −2.79 was survivorship; matured −1.76 is the robust number. |
| **`loss > 0.01` default proxy** | #2 #4 (every default-based decomposition) | Moving the cutoff moves the default-justified yardstick and the +134 / per-grade gaps | Least tested. Stated, not yet varied. The cleanest open sensitivity gap. |

**The spine in one sentence:** four LC results all rest on *tenure-as-age* + *grade-as-yardstick*
+ *survivorship* + *a 1%-loss default proxy*; the HMDA null already knocked out the first joint
(re-labeling "age" → "short-tenure"), result #4 bounded the second (laundering is prime-only and
~1.4 pp), result #3 audited the third (matured-vintage), and the fourth (the loss>0.01 cutoff)
is the one shared assumption still un-varied.

---

## FLAGGED — numbers NOT tied to an on-disk artifact

1. **Result #4 (young-default-vs-grade) has NO JSON** — only `lc_young_default_vs_grade_2026-06-23.txt`.
   All its numbers (+0.70 pooled, +1.39 prime, −0.68 subprime, the per-grade table) appear in the
   txt and tie out there, but there is no machine-readable artifact to re-derive them from. The other
   four results each have a JSON. **This is the weakest-provenance result of the five** (txt is still
   on-disk, so it is not a confabulation — but it is one regeneration step away from un-checkable).
2. **Memo claim "REPLICATES 2012-13: +1.33pp, CI [0.67,1.99]"** (`project-young-default-vs-grade-result.md` L18):
   the txt confirms the point estimate "**+1.33**" (L27) but does **NOT** print the CI [0.67, 1.99].
   **That specific CI is not on disk** — FLAG. The +1.33 point replication IS on disk.
3. **`net_of_grade` young value has no CI in the residual JSON** — `lc_age_pricing_residual_2026-06-20.json`
   stores `net_of_grade.young_bps`=26.67 as a point only (the raw cell A has CIs; the net-of-grade cell
   does not). The memo's "+27 bps, top of band" is the point; treat the "top of band" CI claim as
   un-artifacted phrasing.

Everything else cited above tied out exactly to a JSON/txt on disk. No headline number was
confabulated; the two gaps are missing-CI and missing-JSON, not invented values.
