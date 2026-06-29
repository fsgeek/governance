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

Pre-reg before any code touches data.
