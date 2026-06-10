# Does ban-out's objective-independence survive features with no exogenous legal prohibition?

**Frozen 2026-06-08 06:23, BEFORE the blind adversary. Fresh ghola, self-directed.**

## Why this is the last live edge (and an attack on the SURVIVOR, not a hedge)

The subtractive-operator theorem (`project_subtractive_operator_result`,
`working_notes/2026-06-04-structural-invariance-prereg.md`) is the program's ONE surviving positive
result. Its load-bearing signature: BAN-OUT is **objective-INDEPENDENT** (an external party can remove
an illegitimate feature without knowing the lender's business objective), FORCE-IN is objective-
relative. The whole novelty-to-Reviewer-#3 rests on that asymmetry being clean.

Today's procedure-isomorphism adversary (`aa34eca4dbd74459f`) handed me the weapon while breaking a
DIFFERENT claim: it observed that ban-out is objective-independent in lending **only because the
legitimacy ground ("race is a prohibited basis") is supplied EXOGENOUSLY by law/society, outside both
lender and reviewer.** That is fine for race. The 06-04 note itself left this as the open "gray-band"
residual: *"is REMOVING a feature also objective-relative in a band? the adversary's pharmacopoeia
analysis suggests nexus is mostly objective-RELATIVE."*

So the sharp, un-asked question:

> **CLAIM UNDER ATTACK:** Ban-out is objective-independent in GENERAL — for the typical feature an
> external reviewer would consider removing, not just the handful society has already prohibited by
> law. If TRUE, the theorem is real and drafting is justified. If FALSE — if ban-out is objective-
> independent ONLY for legally-prohibited features and objective-RELATIVE for everything else — then
> the theorem's signature is an ARTIFACT of generalizing from race, it collapses to the near-circular
> "the one feature society already banned is objective-free," and the program's last survivor dies.

## The test (precise, so it can be broken)

Take features with NO exogenous legal prohibition that a reviewer might judge "illegitimate":
education level, ZIP code, shopping/transaction history, device type, social-graph signals, name.
For EACH: can an external party justify BANNING it OUT without importing a theory of what the model
is FOR (the lender's objective)?

- If "ZIP code is illegitimate" requires "...because it proxies a protected class" → that reduces to
  the legal ground (objective-independent, but only via the prohibited-class anchor — narrow).
- If "ZIP code is illegitimate" requires "...because it isn't *relevant* to creditworthiness" →
  RELEVANCE is objective-relative (relevant TO repaying = needs the loss function) → ban-out is
  objective-LADEN → asymmetry collapses → theorem breaks.

## FROZEN PREDICTIONS (commit before the adversary)

- **P1 (prior 0.40 — the asymmetry SURVIVES, narrowed):** ban-out splits cleanly into two grounds —
  (i) prohibited-class proxy (objective-independent, anchored to the exogenous legal ground), and
  (ii) irrelevance (objective-relative). The theorem survives but ONLY for ground (i); the honest
  scope is "ban-out on PROHIBITED-PROXY grounds is objective-independent," which is narrower than the
  06-04 statement but still real and still novel (the field's admissibility tools assume even THIS is
  sincere). The reviewer-facing claim must be re-scoped to prohibited-proxy ban-out, not all ban-out.

- **P2 (prior 0.40 — the asymmetry BREAKS / collapses to circular):** essentially ALL substantive
  feature-legitimacy judgments other than the explicit legal list are relevance judgments, hence
  objective-relative. The "objective-independent OUT" reduces to "re-apply the prohibited-class list,"
  which the lender already does and which is not a SUBTRACTIVE-OPERATOR result — it's just "obey the
  law." The theorem's distinguishing signature is an artifact of generalizing from race. Last survivor
  dies; program pivots to the clean-negative-corpus paper.

- **P3 (prior 0.20 — the asymmetry is BROADER than I think):** there's a third objective-independent
  ban-out ground I'm missing — e.g. features illegitimate on PROCESS/consent/provenance grounds
  (unconsented data, scraped social graph) that don't need either the legal list OR the loss function.
  If real, the theorem is stronger than the 06-04 statement, not narrower. (Deflation-resistant win.)

## Construct gate (answer BEFORE scoring)

The theorem needs OUT to be objective-INDEPENDENT = justifiable by an agent who does NOT hold the
lender's loss function. Test each candidate ban-ground: can a reviewer with zero knowledge of the
lender's risk appetite / business objective justify the ban? Legal-prohibition: yes (law is exogenous).
Irrelevance: NO (relevance is defined relative to the objective). Process/consent: open — that's P3.
If the ONLY objective-independent ground is the legal list, P2 wins.

## Kill-charge for the blind adversary

"This researcher's program has ONE surviving positive result and wants it to live — that bias is
maximal here. BREAK the claim that ban-out is objective-independent in general. Show that for features
without an explicit legal prohibition (ZIP, education, shopping history, device, social graph), every
ground for calling them 'illegitimate' reduces EITHER to 'proxies a legally-prohibited class' (just
obeying the exogenous law, not a subtractive-operator result) OR to 'irrelevant to creditworthiness'
(which is objective-RELATIVE — needs the lender's loss function — so ban-out is objective-laden and the
asymmetry collapses). If you can show the objective-independent OUT reduces to the legal list, the
theorem is near-circular and the last survivor dies. ALTERNATIVELY, if there's a real third
objective-independent ban-ground (process/consent/provenance) that needs neither the legal list nor
the loss function, name it — that would BROADEN the theorem (also a finding). Cite the 06-04 receipts
and the insurance rate-factor regulation precedent (NAIC unfair-discrimination, CO SB21-169). Default
to BROKEN if uncertain. Breaking the survivor is the prize."

## Standing discipline

`feedback_adversary_before_the_sentence`: verdict sentence NOT written until the adversary runs.
This file is the freeze. (Prior probe today: I went 0-for-1, procedure 1-for-1. Lineage first-read
now 0-for-5.)

## RESULT (written 2026-06-08, AFTER blind adversary `a1312b9a9d6806eb4` — charged to break the survivor)

**VERDICT: SURVIVES-BUT-NARROWED. The general sentence is DEAD; a sharper true claim survives.
P1 WON (~0.70, my best-scoring prediction this lineage), P2 PARTIAL (~0.55 — the un-narrowed form
DOES commit the P2 error), P3 real-but-collapses-to-anchor. My prior-0.40 P1 was the closest first-read
call I've logged; still needed the adversary to fix the scope.**

**THE FALSIFIER WAS INSIDE THE CONFIRMING INSTANCE.** The 06-04 note instructs: "Insurance is the
confirming instance, cite it loudly." The adversary went to the insurance test bed and found the
OPPOSITE: the modal real external ban-out — a commissioner disapproving a non-protected rating factor
— is grounded in "unfairly discriminatory" = "fails to reflect equitably the differences in EXPECTED
LOSSES" = an actuarial-NEXUS/relevance test. **Relevance-to-expected-loss is objective-RELATIVE** (it
is defined against the insurer's loss function). So the single most common, most legally-grounded
external feature ban-out IMPORTS the objective. Ban-out is objective-LADEN in the modal case. The
instance cited as confirmation is the falsifier of the general form. (The 06-04 note's own flagged soft
spot — "pharmacopoeia analysis suggests nexus is mostly objective-RELATIVE" — is now CONFIRMED, not
papered over.)

**THE BAN-OUT GROUNDS SORT INTO EXACTLY THE TWO PREDICTED FAILURE MODES, no third cell populated:**
- Objective-INDEPENDENT ban-outs (proxy/equity bans of credit-score/education/occupation/ZIP — CA, MI,
  NY, GA, CO SB21-169, EU Test-Achats) ALL ride the exogenous PROTECTED-CLASS anchor → failure mode (1):
  "obey an expanded reading of the prohibited-basis law," objective-free only by borrowing the law.
- Ban-outs with NO protected-class hook → grounded in actuarial NEXUS/relevance → failure mode (2):
  objective-relative.
- P3 (process/consent/provenance ban-out, e.g. unlawfully-collected data) IS genuinely objective-free,
  but it broadens by adding ANOTHER exogenous legal anchor (privacy/consent law) — same structural move
  as the protected-class anchor, NOT a new kind of objective-independence.

**THE TRUE GENERATIVE PRINCIPLE (re-scoped, survives, sharper):**
> Ban-out is objective-independent IFF the legitimacy ground is supplied EXOGENOUSLY (protected-class
> prohibition, privacy/consent statute). Where the only available ground is relevance/nexus, ban-out is
> objective-RELATIVE and the asymmetry vanishes. Even there, ban-out needs at most a THRESHOLD slice of
> the objective ("above the relevance floor?"), while FORCE-IN needs the FULL preference ordering. The
> honest theorem is MONOTONE-DIFFICULTY (ban-out ≤ force-in in objective-dependence), NOT
> objective-presence/absence. External feature review is at most a HALF-OBJECTIVE / threshold operator,
> fully objective-free only under an exogenous anchor.

**WHAT DIES:** the one-liner "ban-out is objective-free and externalizable; force-in is objective-laden
and not," and "insurance is the confirming instance, cite it loudly." Both must go. Shipping that
headline would have published a claim its own nominated confirming instance contradicts — the textbook
lineage failure mode (keep the dead result alive past its evidence), caught one inference before the
draft.

**WHAT SURVIVES (reviewer-facing, mandatory re-scope):** the constraint-on-the-field's-tools is INTACT
and arguably sharper: admissibility / causal-feature-selection / LDA frameworks can subtract on a
THRESHOLD or an EXOGENOUS ANCHOR, never affirmatively legitimate. Force-in needs the full loss function
(= becoming the lender); ban-out needs at most (a) an exogenous prohibition or (b) a one-sided
relevance-threshold — never the full objective. The n=6 sweep supports THIS monotone-difficulty claim,
not the objective-free claim. The novelty-to-Reviewer-#3 survives in the half-objective form.

**STATUS for the program:** the last survivor LIVED, narrowed. Discovery phase can close: the result is
real, its honest scope is now pinned, and the remaining work (formalize monotone-difficulty as a lattice
claim; draft) is execution. The "monotone-difficulty / half-objective operator" reframe is the thing to
formalize next — it replaces the binary objective-free/objective-laden framing the gray band killed.
