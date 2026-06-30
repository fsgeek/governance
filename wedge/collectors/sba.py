"""SBA 7(a) FOIA loan-level collector — firm-age pricing & charge-off decomposition.

Loads the public SBA 7(a) FOIA disclosure file, restricts to the MATURED approval-FY
window (charge-off is a matured outcome; immature vintages are survivorship-poisoned —
the same discipline that corrected project_age_realized_return_result), maps the ordinal
`businessage` category to a young->old age-band index, and exposes a PRICING frame with
`initialinterestrate` (the disparity variable) and a `loss` proxy derived from
`grosschargeoffamount` (the realized-risk benchmark HMDA lacked).

This is the firm-age analog of the LC short-credit-tenure axis. `businessage` is firm age,
NOT personal age — an honest analog, no protected-class claim. There are NO demographic
fields in this FOIA file (race/gender/veteran were never collected on 7(a)); a protected-
class port would need a different data source (see the demographic-FOIA-ability question).

Frozen ledger: docs/superpowers/specs/2026-06-29-sba-businessage-pricing-prereg.md

DECLARED RISK-MODEL (in the light path, per project_instrument_with_model_in_light_path):
  - default proxy = grosschargeoffamount > 0 (mirrors LC loss>0.01). Ignores recovery timing
    and partial charge-offs — contestable, declared.
  - maturity: restrict to MATURED_FY_MAX (default FY2016); FY2017+ resolved-share falls and
    FY2018+ shift to 120mo terms => survivorship bias. Declared, not hidden.
  - "age" = firm age via the ordinal businessage ladder; Unanswered/Change-of-Ownership/NaN
    dropped (not imputed), documented as excluded.
  - controls = lawful business covariates only (loan size, term, NAICS sector, business type,
    guaranteed share). No demographic fields exist => firm-age disparity, NOT a protected-class
    test. Stated.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Firm-age bands. The FY2010-2019 FOIA file carries the FINE-GRAINED ladder
# (the FY2020+ file collapses to 3 coarse buckets — excluded by the matured
# window anyway). Ordered young -> old. Index 0 is the young end (reference for
# the residual machinery is the ESTABLISHED end, see SBA_AGE_REFERENCE).
# ---------------------------------------------------------------------------
# Raw businessage category -> ordinal band index. Categories that are not a
# point on the age ladder (Unanswered, Change of Ownership, NaN, and the coarse
# FY2020+ "New Business or 2 years or less" / "Existing or more than 2 years")
# map to None and are dropped.
# NOTE (2026-06-29, post blind-adversary): Startup and New-<1yr were ORIGINALLY pooled to band 0.
# The blind adversary refuted that pooling — pre-revenue Startups pay ~no premium (honestly priced)
# while New-<1yr is strongly over-priced; blending them produced a headline describing neither. They
# are now SEPARATE bands (0=Startup, 1=New<1yr) so the decomposition reads each on its own.
_BUSINESSAGE_TO_BAND = {
    "Startup, Loan Funds will Open Business": 0,  # pre-revenue startup
    "New, Less than 1 Year old": 1,
    "Less than 3 years old but at least 2": 2,
    "Less than 4 years old but at least 3": 3,
    "Less than 5 years old but at least 4": 4,
    "Existing, 5 or more years": 5,
}
# Human-readable band labels, index-aligned.
SBA_AGE_BANDS = [
    "Startup (pre-revenue)",
    "New (<1yr)",
    "2-3 years",
    "3-4 years",
    "4-5 years",
    "Existing 5+ years",
]
SBA_AGE_REFERENCE_IDX = 5  # "Existing 5+ years" — the established-firm reference (LC [45,50) analog)
SBA_AGE_YOUNG_IDX = 1      # "New (<1yr)" — the over-priced thin-history subgroup (NOT startup; see note)
SBA_AGE_STARTUP_IDX = 0    # pre-revenue startup — the adversary's honest-priced counterexample

# Categories explicitly dropped (documented exclusion, NOT imputed).
_DROPPED_BUSINESSAGE = {
    "Unanswered",
    "Change of Ownership",
    "Existing or more than 2 years old",     # coarse (mostly FY2020+); ambiguous on the ladder
    "New Business or 2 years or less",        # coarse (mostly FY2020+); n~26 in matured window
}

# Matured-window default: FY2010-2016 are fully resolved by the 2026 asof
# (median term 84mo elapsed; resolved-share >=78%). FY2017+ excluded by default.
MATURED_FY_MIN = 2010
MATURED_FY_MAX = 2016

DEFAULT_PROXY_THRESHOLD = 0.0  # grosschargeoffamount > 0 => default

_USECOLS = [
    "businessage", "initialinterestrate", "fixedorvariableinterestind", "loanstatus",
    "grosschargeoffamount", "terminmonths", "grossapproval",
    "sbaguaranteedapproval", "naicscode", "businesstype",
    "jobssupported", "approvalfy",
]


def _resolve_path(path: Path | str) -> Path:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(
            f"SBA FOIA CSV not found at {p!s}. Expected the public 7(a) disclosure file, "
            "e.g. data/sba/foia-7a-fy2010-fy2019-asof-260331.csv"
        )
    return p


def default_proxy(df: pd.DataFrame, charge_col: str = "grosschargeoffamount",
                  thresh: float = DEFAULT_PROXY_THRESHOLD) -> pd.Series:
    """Binary default = realized gross charge-off above `thresh`. 1=default (mirrors LC loss>0.01)."""
    co = pd.Series(pd.to_numeric(df[charge_col], errors="coerce")).fillna(0.0)
    return (co > thresh).astype(int)


def load_pricing_frame(
    csv_path: Path | str,
    *,
    fy_min: int = MATURED_FY_MIN,
    fy_max: int = MATURED_FY_MAX,
) -> pd.DataFrame:
    """Load SBA 7(a) as a PRICING + DECOMPOSITION frame over the matured FY window.

    Returns a DataFrame with:
      - interest_rate     (initialinterestrate, the disparity variable)
      - age_band          (ordinal firm-age index, 0=New/Startup .. 4=Existing 5+)
      - age_band_str      (human label)
      - loss              (gross charge-off amount, float; >0 => the default proxy fires)
      - defaulted         (1 if loss>0)
      - grade             (alias of age_band band-label for the decomposition reuse; SBA has
                           no credit grade, so the firm-age band IS the stratifier — the
                           net-of-band OLS uses C(grade) as the within-stratum control)
      - grossapproval, terminmonths, guaranteed_share, naics2, business_type  (lawful controls)
    Rows with missing rate / unmapped businessage / missing controls dropped (documented).
    """
    p = _resolve_path(csv_path)
    df = pd.read_csv(p, usecols=lambda c: c in _USECOLS, low_memory=False)

    # Matured-FY window (survivorship discipline).
    fy = pd.to_numeric(df["approvalfy"], errors="coerce")
    df = df[(fy >= fy_min) & (fy <= fy_max)].copy()

    # Firm-age band map; drop unmapped/ambiguous categories (not imputed).
    ba = df["businessage"].astype(str).str.strip()
    df["age_band"] = ba.map(_BUSINESSAGE_TO_BAND)
    df = df[df["age_band"].notna()].copy()
    df["age_band"] = df["age_band"].astype(int)
    df["age_band_str"] = df["age_band"].map(dict(enumerate(SBA_AGE_BANDS)))

    # Disparity variable + realized-risk benchmark.
    df["interest_rate"] = pd.to_numeric(df["initialinterestrate"], errors="coerce")
    loss = pd.to_numeric(df["grosschargeoffamount"], errors="coerce").fillna(0.0)  # type: ignore[union-attr]
    df["loss"] = loss
    df["defaulted"] = (df["loss"] > DEFAULT_PROXY_THRESHOLD).astype(int)

    # Lawful controls.
    df["grossapproval"] = pd.to_numeric(df["grossapproval"], errors="coerce")
    df["terminmonths"] = pd.to_numeric(df["terminmonths"], errors="coerce")
    guar = pd.to_numeric(df["sbaguaranteedapproval"], errors="coerce")
    df["guaranteed_share"] = (guar / df["grossapproval"].where(df["grossapproval"] > 0))
    # NAICS 2-digit sector (the confound the pre-reg names: new firms may concentrate in risky sectors).
    df["naics2"] = df["naicscode"].astype(str).str.strip().str.slice(0, 2)
    df["business_type"] = df["businesstype"].astype(str).str.strip()
    # Rate-timing controls. 79% of 7(a) loans are VARIABLE-rate, so the INITIAL rate depends on the
    # base-rate environment at origination. If New/Startup firms cluster in different approval years
    # than Existing firms, a raw rate-gap could be a base-rate-TIMING artifact, not a firm-age premium
    # (same shape as the FM PMI-threshold confound the blind adversary caught). The runner absorbs this
    # via C(approval_fy) + C(rate_type) fixed effects in the B1 residual.
    # approval_fy as STRING (it's a fixed-effect label, not a magnitude; patsy C() can't read Int64).
    df["approval_fy"] = pd.to_numeric(df["approvalfy"], errors="coerce").astype("Int64").astype(str)
    df["rate_type"] = df["fixedorvariableinterestind"].astype(str).str.strip()  # 'V' / 'F'

    # NOTE ON THE DECOMPOSITION (load-bearing design call): SBA has NO credit grade, so the LC
    # "do the young default above their GRADE" decomposition does NOT port — there is no lender-
    # supplied within-stratum risk yardstick to net out, and aliasing grade:=age_band would be
    # circular. The honest SBA decomposition is RESIDUAL-based (wedge/age_residual.fit_band_residuals):
    # fit the SAME age-band-on-lawful-controls residual for PRICE and for realized DEFAULT, then
    # compare the price-gap to the default-gap. price-gap > default-gap => over-priced (empty-chair
    # harm); ~equal => honestly priced; price-gap < default-gap => subsidized. This is cleaner than
    # the LC grade version: it never launders the risk judgment through a lender black box — price and
    # ground-truth charge-off sit on the same lawful-control footing. The runner owns that comparison.

    need = ["interest_rate", "age_band", "loss", "grossapproval", "terminmonths"]
    df = df.dropna(subset=need).copy()
    return df.reset_index(drop=True)
