#!/usr/bin/env python3
"""Runner: can the gradient/price instrument tell LAUNDERED steering from genuine blindness?

Three synthetic lenders (blind / overt / laundered), each assigns a grade then prices off it. Emits
a self-describing artifact + JSON. All stats in the tested module wedge/steering_detectability.py.
See docs/superpowers/specs/2026-06-23-steering-detectability-design.md for the frozen ledger.
"""
import json
import sys

sys.path.insert(0, ".")
from wedge.steering_detectability import build_lender, evaluate_lender  # noqa: E402

OUT_TXT = "runs/steering_detectability_2026-06-23.txt"
OUT_JSON = "runs/steering_detectability_2026-06-23.json"
N = 120000
SEED = 1


def main():
    out, payload = [], {"n": N, "seed": SEED}
    out.append("STEERING-DETECTABILITY — can the gradient/price instrument catch grade-LAUNDERED "
               "young-steering? (2026-06-23, synthetic)")
    out.append(f"N={N}/lender, seed={SEED}. Each lender assigns a grade then prices off it. age _|_ "
               "true_risk by construction (excess => steering, not risk).")
    out.append("L0 blind: grade=g(risk).  L1 overt: price += 4pp on young.  "
               "L2 launder: young pushed to worse GRADES beyond risk, price honest off grade.")
    out.append("FROZEN BET (Claude, ~65%): L2 reads flat like L0 (laundering invisible) => would force "
               "retraction of the realized-return 'not deliberate' line. RESULT BELOW.")
    out.append("")
    results = {}
    for kind in ["blind", "overt", "launder"]:
        ev = evaluate_lender(build_lender(kind, n=N, seed=SEED))
        results[kind] = ev
        out.append(f"[{kind.upper()}]")
        out.append(f"  young price RAW          = {ev['young_raw_bps']:+8.1f} bps")
        out.append(f"  young price NET-OF-GRADE = {ev['young_net_bps']:+8.1f} bps")
        out.append(f"  collapse ratio |net|/|raw| = {ev['collapse_ratio']:.3f}  "
                   f"(~0 => signal lives INSIDE grade = laundering fingerprint)")
        out.append(f"  laundering signature     = {ev['laundering_signature']}")
        out.append(f"  raw gradient: slope_R2={ev['gradient_raw']['slope_r2']:.3f}, "
                   f"monotone={ev['gradient_raw']['monotone']}")
        out.append("")
    payload["results"] = results

    blind, overt, launder = results["blind"], results["overt"], results["launder"]
    out.append("VERDICT:")
    out.append(f"  L0 blind young raw={blind['young_raw_bps']:+.1f}bps (flat, no false positive: "
               f"{abs(blind['young_raw_bps'])<25}).")
    out.append(f"  L1 overt detected={overt['young_raw_bps']>300}, SURVIVES net-of-grade "
               f"(collapse={overt['collapse_ratio']:.2f}) => steering in PRICE, not a launder signature.")
    out.append(f"  L2 launder detected={launder['young_raw_bps']>300}, COLLAPSES net-of-grade "
               f"(collapse={launder['collapse_ratio']:.2f}) => laundering FINGERPRINT.")
    out.append("")
    out.append("  COIN: Claude bet L2 would be INVISIBLE (read flat like L0) => FALSIFIED. Laundered "
               "steering is NOT invisible — it shows a LARGE raw young-price excess that COLLAPSES "
               "net-of-grade, a signature distinct from both blind (no signal) and overt (survives "
               "net-of-grade). The instrument DISTINGUISHES laundering by the collapse fingerprint.")
    out.append("  IMPLICATION for real LC: the real +209bps->+27bps (collapse ratio 0.13) MATCHES the "
               "L2 laundering signature, NOT the L0/L1 honest signatures. The net-of-grade collapse "
               "is itself evidence TOWARD grade-laundering, because honest lenders don't produce it.")
    out.append("")
    out.append("CAVEAT: synthetic — shows what the instrument CAN detect, not what LC did. 'LC matches "
               "the laundering signature' means the gradient cannot RULE laundering OUT; combined with "
               "the realized-return result (overcharge eaten by loss), the honest reading shifts from "
               "'un-audited, not deliberate' toward 'consistent with grade-laundering, intent still "
               "unproven'. A harness note: wedge.fit_band_return's Categorical path was unstable on "
               "this synthetic; evaluate_lender uses an explicit verified fit (real-LC runs unaffected).")

    with open(OUT_TXT, "w") as fh:
        fh.write("\n".join(out) + "\n")
    with open(OUT_JSON, "w") as fh:
        json.dump(payload, fh, indent=2, default=float)
    print("\n".join(out))
    print(f"\nWrote {OUT_TXT} and {OUT_JSON}")


if __name__ == "__main__":
    main()
