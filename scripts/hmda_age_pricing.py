#!/usr/bin/env python3
"""Runner: HMDA real-age pricing disparity — does the LC young-pay-more gradient survive on OBSERVED age?

Removes the tenure-as-age assumption from the light path (per project_instrument_with_model_in_light_path).
HMDA has real applicant_age + interest_rate but NO realized outcome, so this is DISPARITY-ONLY: the
risk-decomposition is reported UNAVAILABLE (Tony's (i) call — no proxy benchmark, that would be theater).

See docs/superpowers/specs/2026-06-23-hmda-real-age-pricing-design.md for the frozen ledger.
"""
import json
import sys

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

sys.path.insert(0, ".")
from wedge.collectors.hmda import (  # noqa: E402
    load_pricing_frame, HMDA_AGE_BANDS, HMDA_AGE_REFERENCE,
)

PARQUET = "data/hmda/processed/hmda_2022_RI.parquet"
OUT_TXT = "runs/hmda_ri_age_pricing_2026-06-23.txt"
OUT_JSON = "runs/hmda_ri_age_pricing_2026-06-23.json"
CONTROLS = ["applicant_income", "loan_amount", "ltv", "loan_term_months"]
REF_IDX = HMDA_AGE_BANDS.index(HMDA_AGE_REFERENCE)


def fit_age_bands(df, outcome="interest_rate", extra_controls=None):
    """OLS of outcome on age-band dummies (reference 45-54) + lawful controls + C(purpose).
    Returns {band_idx: (coef_bps, lo_bps, hi_bps, n)}. dti added only if present and non-degenerate."""
    d = df.copy()
    d["_b"] = pd.Categorical(d["age_band"])
    ctrl = list(CONTROLS)
    if extra_controls:
        ctrl += extra_controls
    formula = (f"{outcome} ~ C(_b, Treatment(reference={REF_IDX})) + "
               + " + ".join(ctrl) + " + C(purpose)")
    m = smf.ols(formula, data=d).fit()
    conf = m.conf_int()
    res = {}
    counts = d["age_band"].value_counts().to_dict()
    for i in range(len(HMDA_AGE_BANDS)):
        n = int(counts.get(i, 0))
        if i == REF_IDX:
            res[i] = (0.0, 0.0, 0.0, n)
            continue
        term = f"C(_b, Treatment(reference={REF_IDX}))[T.{i}]"
        if term in m.params.index:
            lo, hi = conf.loc[term]
            res[i] = (float(m.params[term]) * 100.0, float(lo) * 100.0, float(hi) * 100.0, n)
        else:
            res[i] = (float("nan"), float("nan"), float("nan"), n)
    return res, float(m.rsquared)


def main():
    df = load_pricing_frame(PARQUET)
    out, payload = [], {"n": int(len(df))}
    out.append("HMDA-RI 2022 REAL-AGE PRICING DISPARITY — does the LC young-pay-more gradient survive "
               "on OBSERVED age? (2026-06-23)")
    out.append(f"Source: {PARQUET}, originated first-lien owner-occupied purchase/refi, N={len(df)}.")
    out.append("Outcome: interest_rate (%). Lawful controls: " + ", ".join(CONTROLS) + ", purpose. "
               "HMDA has NO credit score => fewer risk controls than LC => surviving disparity is "
               "LESS risk-purged (caution caveat).")
    out.append(f"Age = OBSERVED applicant_age bands (removes the LC tenure-as-age assumption). "
               f"Reference = {HMDA_AGE_REFERENCE}.")
    out.append("FROZEN LEDGER: Claude = young (<25) POSITIVE but attenuated vs LC +209bps, predicted "
               "+10..+90bps. Flat/negative => LC gradient was tenure, not age.")
    out.append("DECOMPOSITION: UNAVAILABLE — HMDA has no realized loan outcome (no default/loss). "
               "Reported absent, NOT proxied (Tony's (i): a proxy benchmark here is theater).")
    out.append("")

    res, r2 = fit_age_bands(df)
    out.append("[A] interest_rate residual by OBSERVED age band, lawful controls:")
    for i, b in enumerate(HMDA_AGE_BANDS):
        coef, lo, hi, n = res[i]
        tag = "  <- REF" if i == REF_IDX else ""
        out.append(f"  {b:8} n={n:>6}  resid={coef:+8.1f} bps  CI=[{lo:+8.1f},{hi:+8.1f}]{tag}")
    out.append(f"  R2={r2:.4f}  (reference band = {HMDA_AGE_REFERENCE})")
    payload["A_age_pricing"] = {HMDA_AGE_BANDS[i]: {"bps": res[i][0], "ci": [res[i][1], res[i][2]],
                                                    "n": res[i][3]} for i in range(len(HMDA_AGE_BANDS))}
    payload["A_r2"] = r2
    out.append("")

    # positive control: plant +30bps on youngest band, assert recovery
    dpc = df.copy()
    rng = np.random.default_rng(42)
    mask = dpc["age_band"] == 0
    idx = dpc.index[mask]
    chosen = rng.choice(np.asarray(idx), size=int(len(idx) * 0.5), replace=False)
    dpc.loc[chosen, "interest_rate"] = dpc.loc[chosen, "interest_rate"] + 0.30
    res_pc, _ = fit_age_bands(dpc)
    base0, pc0 = res[0][0], res_pc[0][0]
    recovered = pc0 - base0
    out.append(f"[pos-control] +30bps on 50% of <25 (expect ~+15bps recovery): base={base0:+.1f} -> "
               f"with-plant={pc0:+.1f}  recovered={recovered:+.1f}bps  "
               f"=> {'PASS' if 8 < recovered < 22 else 'CHECK'}")
    payload["pos_control"] = {"base": base0, "with_plant": pc0, "recovered": recovered}
    out.append("")

    # ledger scoring
    young0 = res[0][0]      # <25
    young1 = res[1][0]      # 25-34
    out.append("LEDGER SCORING (ledger frozen above; verdicts from this run):")
    sign = "POSITIVE" if young0 > 0 else ("~0" if abs(young0) < 5 else "NEGATIVE")
    hit = 10 <= young0 <= 90
    out.append(f"  Claude 'young <25 positive, +10..+90bps': <25 = {young0:+.1f}bps ({sign}) => "
               f"{'HELD' if hit else 'FALSIFIED'}. 25-34 = {young1:+.1f}bps.")
    out.append(f"  Tenure-vs-age: {'SURVIVES on real age (LC gradient not merely tenure)' if young0 > 5 else 'does NOT survive => LC gradient was substantially tenure'}.")
    out.append("  meta 'decomposition unavailable': HELD — no realized outcome on HMDA; reported absent.")
    out.append("")
    out.append("CAVEATS: observed age is BANDED (coarse); <25 is the young proxy. Fewer risk controls "
               "than LC (no credit score) => an UPPER reading of the lawful-residual, not magnitude-"
               "comparable to LC's grade-inclusive number. Single state/year, originated-only. "
               "DISPARITY ONLY — whether any is risk-justified is UNANSWERABLE on HMDA, by design.")

    with open(OUT_TXT, "w") as fh:
        fh.write("\n".join(out) + "\n")
    with open(OUT_JSON, "w") as fh:
        json.dump(payload, fh, indent=2, default=float)
    print("\n".join(out))
    print(f"\nWrote {OUT_TXT}")


if __name__ == "__main__":
    main()
