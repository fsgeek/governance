#!/usr/bin/env python3
"""Runner: does LC grade price the young-end age gradient PAST what realized default justifies?

Descendant of scripts/age_pricing_residual.py. That runner found ~182 bps of the young-end age
pricing lives inside LC grade. This one anchors the yardstick to DEFAULT (not to LC's own price,
Tony's reframe) and asks whether that 182 tracks realized default (grade exonerated) or floats
free of it (lawful-but-illegitimate — the empty-chair instance), and whether the sign FLIPS at the
old end (old subsidized).

Two scopes, both under two default->rate map estimators (isotonic + decile):
  CORPUS (primary)      map fit age-blind on the whole population; surviving young excess is
                        CONSERVATIVE (thin-file default already in the yardstick).
  WITHIN-GRADE (foil)   map fit within each grade; corpus-minus-within-grade gap = how much grade
                        launders the age pricing.
Plus a sanity rail: age-in-grade vs age-in-default standardized loading.

All statistics live in the tested module wedge/age_grade_default.py; this script is glue + I/O.
See docs/superpowers/specs/2026-06-22-age-grade-default-design.md for the frozen ledger.
"""
import json
import sys

sys.path.insert(0, ".")
from scripts.age_pricing_residual import load  # noqa: E402  (identical universe + loader)
from wedge.age_grade_default import (  # noqa: E402
    band_excess_corpus, band_excess_within_grade, grade_vs_default_rail,
    predicted_default, fit_default_rate_map, assert_monotone,
)
from wedge.age_residual import AGE_BANDS, band_label  # noqa: E402

OUT_TXT = "runs/lc_age_grade_default_2026-06-22.txt"
OUT_JSON = "runs/lc_age_grade_default_2026-06-22.json"

FROZEN_LEDGER = {
    "claude_corpus_excess": "young [18,25) corpus excess SURVIVES, +40..+100 bps (positive, "
                            "conservative, smaller than the raw 182)",
    "claude_grade_laundering": "within-grade young excess drops to under half the corpus excess "
                               "(grade is where the age pricing hides)",
    "claude_old_end_sign": "old priced BELOW default-justified (subsidized) through 50-60; 70+ "
                           "too censored to sign (genuinely uncertain — the fun)",
    "tony_caveat": "corpus benchmark biases AGAINST the young (short histories -> higher-default "
                   "categories), so young excess ATTENUATED vs raw 182; a chunk is defensible risk",
}


def fmt_excess(res):
    lines = []
    for i in range(len(AGE_BANDS)):
        bps = res.band_bps.get(i, float("nan"))
        lo, hi = res.band_ci.get(i, (float("nan"), float("nan")))
        n = res.n_per_band.get(i, 0)
        sign = "PAST default" if bps > 0 else "SUBSIDIZED"
        crosses0 = "" if (lo > 0 or hi < 0) else "  (CI crosses 0)"
        lines.append(f"  {band_label(i):10} n={n:>7}  excess={bps:+8.1f} bps  "
                     f"CI=[{lo:+8.1f},{hi:+8.1f}]  {sign}{crosses0}")
    return "\n".join(lines)


def main():
    df = load()
    df["default"] = (df["loan_status"] == "Charged Off").astype(int)
    n_default = int(df["default"].sum())
    out, payload = [], {"n_total": int(len(df)), "n_default": n_default,
                        "frozen_ledger": FROZEN_LEDGER}

    out.append("LC AGE GRADE-vs-DEFAULT — does grade price the young PAST realized default? "
               "(2026-06-22)")
    out.append(f"Source: {load.__module__} loader, resolved loans, N={len(df)}, "
               f"defaults={n_default} ({100*n_default/len(df):.1f}%).")
    out.append("Yardstick = DEFAULT-justified price (Tony's reframe): the rate a loan's realized-"
               "default risk maps to, estimated empirically. NOT normalized to LC's own price.")
    out.append("CORPUS map = age-blind whole-population (primary; young thin-file default baked in "
               "=> surviving young excess is CONSERVATIVE). WITHIN-GRADE map = per-grade (foil).")
    out.append("Predicted default: logistic on FICO/DTI/income/loan/term/purpose — NOT age.")
    out.append("FROZEN LEDGER (do not alter): " + json.dumps(FROZEN_LEDGER))
    out.append("CAVEAT: 'age' IS credit tenure (est_age=18+tenure). Pricing = LC grade model. "
               "Old tail (70+) censored, small n.")
    out.append("")

    # ---- default->rate map description (for the artifact's attack-surface transparency) ----
    p_hat = predicted_default(df)
    payload["pred_default_summary"] = {"min": float(p_hat.min()), "max": float(p_hat.max()),
                                       "mean": float(p_hat.mean())}
    for kind in ("isotonic", "decile"):
        m = fit_default_rate_map(p_hat, df["int_rate"].to_numpy(), map_kind=kind)
        assert_monotone(m)
        out.append(f"[map:{kind}] justified rate ranges "
                   f"{m.justified_rate(p_hat).min():.2f}% .. {m.justified_rate(p_hat).max():.2f}% "
                   f"(monotone non-decreasing — guard passed).")
    out.append("")

    results = {}
    for kind in ("isotonic", "decile"):
        # p_hat computed once above — thread it through so the 1.34M logistic isn't refit per call
        corpus = band_excess_corpus(df, map_kind=kind, p_hat=p_hat)
        within = band_excess_within_grade(df, map_kind=kind, p_hat=p_hat)
        results[kind] = {"corpus": corpus, "within": within}

        out.append(f"=== MAP = {kind.upper()} ===")
        out.append(f"[CORPUS] per-band excess over DEFAULT-justified rate (primary; conservative):")
        out.append(fmt_excess(corpus))
        out.append(f"[WITHIN-GRADE] per-band excess (foil; grade-internal yardstick):")
        out.append(fmt_excess(within))
        out.append("[GRADE-LAUNDERING gap] corpus excess − within-grade excess, per band "
                   "(large young-end gap = grade absorbed the age pricing):")
        gap = {}
        for i in range(len(AGE_BANDS)):
            cb = corpus.band_bps.get(i, float("nan"))
            wb = within.band_bps.get(i, float("nan"))
            g = cb - wb
            gap[i] = g
            out.append(f"  {band_label(i):10} corpus={cb:+8.1f}  within={wb:+8.1f}  "
                       f"gap={g:+8.1f} bps")
        out.append("")
        payload[f"map_{kind}"] = {
            "corpus": {"band_bps": corpus.band_bps, "band_ci": corpus.band_ci,
                       "n_per_band": corpus.n_per_band},
            "within_grade": {"band_bps": within.band_bps, "band_ci": within.band_ci,
                             "n_per_band": within.n_per_band},
            "grade_laundering_gap_bps": gap,
        }

    # ---- sanity rail ----
    rail = grade_vs_default_rail(df)
    out.append("[RAIL] age-in-grade vs age-in-default standardized loading, per band "
               "(positive grade−default = grade prices age the default data doesn't justify):")
    for i in range(len(AGE_BANDS)):
        gl = rail["grade_age_loading_std"].get(i, float("nan"))
        dl = rail["default_age_loading_std"].get(i, float("nan"))
        gd = rail["grade_minus_default_loading"].get(i, float("nan"))
        out.append(f"  {band_label(i):10} grade_load={gl:+.4f}  default_load={dl:+.4f}  "
                   f"grade−default={gd:+.4f}")
    payload["rail"] = rail
    out.append("")

    # ---- ledger scoring (computed from the data; ledger above unaltered) ----
    iso_corpus = results["isotonic"]["corpus"]
    iso_within = results["isotonic"]["within"]
    young_corpus = iso_corpus.band_bps[0]
    young_within = iso_within.band_bps[0]
    young_gap = young_corpus - young_within
    out.append("LEDGER SCORING (ledger frozen above; verdicts computed from this run; isotonic map):")
    surv = "SURVIVES" if young_corpus > 0 else "DOES NOT survive"
    in_band = 40.0 <= young_corpus <= 100.0
    out.append(f"  Claude 'corpus excess +40..+100 survives': young [18,25) corpus excess = "
               f"{young_corpus:+.0f} bps -> {surv}; in predicted band: {in_band}.")
    laundered_half = young_within < 0.5 * young_corpus if young_corpus > 0 else None
    out.append(f"  Claude 'within-grade drops to <half corpus': within={young_within:+.0f} vs "
               f"corpus={young_corpus:+.0f} (gap {young_gap:+.0f}); <half: {laundered_half}.")
    # old-end sign: report the most-populated old bands' sign
    old_signs = {band_label(i): ("subsidized" if iso_corpus.band_bps[i] < 0 else "past-default")
                 for i in (6, 7, 8)}
    out.append(f"  Claude 'old-end subsidized through 50-60': {old_signs}.")
    out.append(f"  Tony 'attenuated vs raw 182': raw grade wedge was ~182 bps; corpus young excess "
               f"is {young_corpus:+.0f} bps ({'attenuated' if young_corpus < 182 else 'NOT attenuated'}).")
    out.append("")
    out.append("READ: corpus young excess = how much the young pay past what their OWN realized "
               "default justifies (conservative — thin-file risk already netted). within-grade "
               "young excess = what survives once grade defines the yardstick. The gap = grade's "
               "age-laundering. Old-end negative excess = subsidized by the same instrument.")

    payload["scoring"] = {"young_corpus_bps": young_corpus, "young_within_bps": young_within,
                          "young_grade_laundering_gap_bps": young_gap}

    with open(OUT_TXT, "w") as fh:
        fh.write("\n".join(out) + "\n")
    with open(OUT_JSON, "w") as fh:
        json.dump(payload, fh, indent=2, default=float)
    print("\n".join(out))
    print(f"\nWrote {OUT_TXT} and {OUT_JSON}")


if __name__ == "__main__":
    main()
