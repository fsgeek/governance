# Pre-registration: SBA 7(a) business-age pricing & charge-off decomposition

**Frozen:** 2026-06-29, branch `age-pricing-residual`, before any analysis code touches the data.
**Author:** Claude Opus 4.8 (1M), fresh-takeover session, Tony PI.
**Lineage:** first port of the validated empty-chair instrument to a NOVEL substrate after the
age-pricing arc re-labeled itself to credit-tenure. Frame: [[project_instrument_with_model_in_light_path]].

## Why this substrate

SBA 7(a) FOIA disclosure is the first axis where the instrument's required
**disparity + decomposition-by-realized-risk + declared-model + sensitivity** form can run on an
age-like axis the analyst did NOT pre-label — *and* it carries a realized outcome HMDA lacked.

Verified on disk (`data/sba/foia-7a-fy2010-fy2019-asof-260331.csv`, N=545,751) BEFORE freezing:
- `businessage` 99.7% populated (ORDINAL category, not continuous — like LC tenure bands).
- `initialinterestrate` 100% populated, mean 6.53%, sensible spread → the **disparity** variable.
- `grosschargeoffamount` 100% populated; **6.83% charge off >0** with sensible dollar magnitudes;
  corroborated by `loanstatus` (CHGOFF=30,849). → the **realized-risk benchmark** (HMDA had none).
- Lawful controls present: `terminmonths`, `grossapproval`, `naicscode`, `businesstype`, `jobssupported`.

## The declared risk-model (in the light path, named for the hostile expert)

1. **Default proxy** = `grosschargeoffamount > 0` (mirrors the LC `loss>0.01` proxy). Contestable:
   ignores recovery timing and partial charge-offs.
2. **Maturity / survivorship.** Charge-off is a matured outcome. Restrict to **matured window
   FY2010–2016** (median term 84mo fully elapsed by 2026 asof; resolved-share ≥78%). FY2017–2019
   EXCLUDED (resolved-share falls 74.6%→59.0%; FY18–19 shift to 120mo terms) — the same
   survivorship discipline that corrected `project_age_realized_return_result`.
3. **"Age" = firm age, not personal age.** Honest analog, not identity. No protected-class claim.
   `businessage` categories collapsed to an ordinal ladder; `Unanswered`/`Change of Ownership`/NaN
   dropped (~10%), documented as excluded, not imputed.
4. **Pricing controls = lawful business covariates only** (loan size, term, NAICS sector,
   business type, guaranteed share). No demographic fields exist in this substrate — so this is a
   firm-age disparity test, NOT a protected-class test. Stated, not hidden.

## The reference and the young end

- Reference band: **"Existing, 5 or more years"** (the established-firm analog of LC ref [45,50)).
- Young end: **"New, Less than 1 Year old"** + "Startup, Loan Funds will Open Business" (the
  thin-firm-history analog of the short-credit-tenure borrower the LC arc re-labeled to).

## FROZEN BETS (the coin-flips — I genuinely do not know)

**B1 — pricing disparity.** Do new/startup firms pay a higher `initialinterestrate` than
established firms, net of lawful controls?
- My prior: **~55% YES, small** (+10..+40bps). SBA rates are guaranteed/capped (max 13.5% observed,
  tight band) → less discretionary headroom than LC personal loans → I expect attenuation vs LC's
  +209bps, possibly to nothing. A NULL here is a real, publishable result (the instrument returning
  specific/defeasible on a third substrate, like the FM null).

**B2 — the decomposition (the load-bearing one, only runnable BECAUSE charge-off exists).**
Do new/startup firms charge off ABOVE what their business-age band's base rate predicts
(net-of-band positive → grade/age under-prices their risk, L2-ish), or AT it (honest, L3)?
- My prior: **genuinely 50/50.** This is the discriminant HMDA could not supply. If B1 shows a
  pricing premium AND B2 shows new firms charge off no more than priced → the SBA program prices
  thin-history firms honestly (instrument returns "no illegitimate harm here"). If B2 shows new
  firms charge off LESS than their premium implies → an empty-chair over-pricing harm on firm age,
  the first such finding on a substrate where the decomposition is real, not proxied.

**Combined read frozen NOW:** the four outcomes (premium×{under/over/honest-priced}) map to
launder / honest / subsidy exactly as the LC arc's L2/L3 lattice. I commit to reading the
**combined** cell, not B1 alone — B1 alone is the trap the LC +209bps headline fell into.

## Adversarial self-checks (mandatory, run before any reviewer asks)

- **Positive control:** plant +30bps on 50% of new-firm rows → confirm the pricing estimator
  recovers ~+15bps. Plant +3pp charge-off under-grading on new firms → confirm the decomposition
  recovers it. A null is only trusted if the control passes (the HMDA-null discipline).
- **Negative control:** a random 50/50 split (not business-age) must show ~0 on both.
- **Maturity sensitivity:** re-run on FY2010–2014 (most-matured) vs FY2010–2016; report whether the
  sign/magnitude moves (the survivorship audit).
- **NAICS-mix confound:** new firms may concentrate in riskier sectors. Report the disparity with
  and without NAICS control; the gap between them IS a declared sensitivity, not a nuisance to hide.

## Out of scope (named, not smuggled)

- No which-disparity-is-the-real-harm normative call inside the instrument (per the frame: that
  judgment is downstream, named, contestable).
- 504 program and FY2020+ deferred (different structure / immature).
- No protected-class claim — this substrate has no demographic fields. Firm age only.

## Build plan (after this freezes)

1. `wedge/collectors/sba.py` — load + collapse + parquet cache (no SBA collector exists yet;
   this is the gating build, NOT a port of an existing one). Matured-window filter, businessage
   ordinal map, charge-off proxy, control selection.
2. Reuse `wedge/young_default_vs_grade.py` decomposition logic (net-of-band OLS) — it is
   substrate-agnostic given an (age-band, default, grade/band) triple; SBA's band IS the grade analog.
3. Runner writes `runs/sba_businessage_pricing_2026-06-29.json` with frozen-bet outcomes + all controls.

## AMENDMENT 2026-06-29 (build-time, before any data was analyzed — method change, bet unchanged)

While building `wedge/collectors/sba.py` I confirmed on disk that **SBA has NO credit grade
field** (verified: the FOIA schema has no grade/risk-tier column). The frozen build-plan step
"reuse young_default_vs_grade.py net-of-GRADE OLS" therefore does NOT port — there is no
lender-supplied within-stratum risk yardstick to net out, and aliasing grade:=age_band is
circular. This was discovered by reading the schema, NOT by running any analysis (no bet peek).

**Method change (B2):** the SBA decomposition is RESIDUAL-based, not grade-based. Fit the same
age-band-on-lawful-controls residual (`wedge/age_residual.fit_band_residuals`) for PRICE and for
realized DEFAULT, then compare:
  - price-gap > default-gap  => New/Startup OVER-priced (the empty-chair over-pricing harm)
  - price-gap ~= default-gap => honestly priced
  - price-gap < default-gap  => subsidized
This is CLEANER than the LC grade version (it never launders the risk judgment through a lender
black box; price and ground-truth charge-off sit on the same lawful-control footing) and it is the
instrument-with-declared-model in its purest form.

**The frozen BETS are UNCHANGED.** B1 (pricing premium for New/Startup, ~55%, small, null is real)
and B2 (over-priced vs honest — genuinely 50/50, now read as price-gap vs default-gap) stand exactly
as frozen. Only the B2 ESTIMATOR changed, forced by a missing field, named here before any run.

**Added control (build-time, named before any run): RATE-TIMING.** Confirmed on disk that 79% of
7(a) loans are VARIABLE-rate (V=430k vs F=116k), so `initialinterestrate` depends on the base-rate
environment at origination — and base rates moved across FY2010-2016. If New/Startup firms cluster in
different approval years than Existing firms, a raw rate-gap could be a base-rate-TIMING artifact, not
a firm-age premium (the SAME shape as the FM PMI-threshold confound the blind adversary caught and the
whole instrument exists to localize). B1 therefore absorbs `C(approval_fy) + C(rate_type)` fixed
effects. Reporting the disparity WITH and WITHOUT these is itself a declared sensitivity.

Also confirmed at build time: the FY2010-2019 file carries the FINE-GRAINED businessage ladder
(New<1yr / 2-3 / 3-4 / 4-5 / Existing 5+); the FY2020+ file collapses to 3 coarse buckets. The
matured window (FY2010-2016) sits ENTIRELY inside the fine-grained file — the rich axis and the
matured-outcome window coincide, so excluding FY2017+ costs no axis resolution.

## ADVERSARY DISPOSITION 2026-06-29 (blind scientific-integrity-auditor ran BEFORE the result memo)

Per the standing "adversarial review before stamp" invariant — and because this result flattered my
empty-chair prior — a blind adversary (no narrative, told to REFUTE) audited the first-cut result. It
ruled the first cut **OVERSTATED** (not broken: data/code/replication clean, no fabrication, the LGD
conversion dimensionally sound). Three corrections, all CONCEDED and folded into the committed runner:

1. **Attack-3 (CONCEDE FULLY): Startup/New pooling.** Band 0 pooled pre-revenue "Startup" with "New
   <1yr"; the adversary showed Startup pays ~no premium (HONEST) while New(<1yr) is strongly over-
   priced. Pooling produced a blended headline describing NEITHER, and the empty-chair "thin-history"
   framing is REFUTED by the thinnest firms (startups). FIX: bands split (0=Startup, 1=New<1yr);
   B2 scored PER SUBGROUP.
2. **Attack-5 (CONCEDE FULLY): window inflation.** FY2015-16 inflated the premium ~30%. FIX: headline
   is now matured FY2010-2014; FY2010-2016 kept only as the inflated comparison.
3. **Attack-1 (CONCEDE PARTIALLY): justified-spread params.** My LGD=0.5/term=7 was a coincidence of
   offsetting errors and the grid varied only LGD. FIX: use REALIZED LGD (0.67) + term (9.9yr) +
   guarantee-share (0.66), and sweep LGD x term x loss-bearer (12 cells).

CORRECTED VERDICT (committed): **B1 WIN** (New<1yr +36.6bps matured, CI excludes 0, survives NAICS).
**B2 PARTIAL** — New(<1yr) OVER-priced (+36.6 vs ~18.9 justified, robust across ALL 12 sensitivity
cells incl. worst-case) but Startup HONESTLY priced (+9.3 vs ~10.8). The empty-chair over-pricing harm
is REAL and robust for New(<1yr) ONLY, not thin-history firms generally. B2-as-pooled-OVER-priced is a
PARTIAL LOSS on my prior — recorded as such, not softened (criterion 5).

Pre-reg before any code touches data.
