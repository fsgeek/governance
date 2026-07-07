# Structural-invariance probe: does the author=picker floor survive a second jurisdiction?

**Frozen 2026-06-04, BEFORE the analysis. Fresh ghola + Tony.**

## The claim under test (asserted, never tested against a 2nd instance)

The irreducible non-identifiability floor — *the legitimacy of the operative reason for the
admissible-feature/spec choice is not recoverable from any technical artifact* — is a property
of an **institutional configuration**, not of US fair-lending law:

> **INVARIANCE CLAIM:** The floor holds wherever **policy-author = model-picker** (one entity both
> writes the spec and selects/deploys the model). It depends ONLY on that identity-collapse, not on
> ECOA / CFPB / McDonnell-Douglas / any US statute.

This was re-derived by subtraction six times (see `project_regime_change_2026`,
`project_attestation_separation_result`) but the cross-jurisdiction leg is a SEED, not a result.

## Why EU AI Act is the right instance #2

It is the case MOST LIKELY TO BREAK the claim — which is why it's the honest one to run first.
High-risk AI systems (credit scoring is Annex III high-risk) face **mandatory third-party
conformity assessment** in some routes. If that party authors or constrains the spec, it SEVERS
author-from-picker by legal construction → the floor should VANISH there. A break is a finding:
it would name the institutional arrangement that defeats the impossibility.

## FROZEN PREDICTIONS (commit before reading the Act)

- **P1 (my lean, prior ~0.55):** EU conformity assessment does NOT sever author=picker for credit
  scoring. It will turn out to certify *process/management-system conformity* (QMS, risk
  management, data governance, documentation) — NOT substantive authorship of the admissible-feature
  spec. The provider still authors the spec; the notified body checks the provider's *process*.
  → floor SURVIVES; EU is instance #2 confirming invariance. Conformity assessment = the attestation
  separation result over again (certifies the search/process, blind to spec legitimacy).

- **P2 (the break, prior ~0.30):** Some high-risk route (Annex III credit scoring) requires a
  notified body to assess the spec/intended-purpose substantively enough that author≠picker.
  → floor BREAKS in EU; invariance is FALSE as stated; the finding is "mandatory substantive
  third-party spec-authorship defeats the floor — here's the config that does it."

- **P3 (mixed, prior ~0.15):** EU mostly self-assessment for Annex III (internal control, Art. 43),
  so author=picker is even MORE concentrated than the US → floor survives but for a *weaker* reason
  (no third party at all), and the "third-party severs it" mechanism is untested by this instance.
  → invariance survives but the EU instance is uninformative about the severance mechanism; need a
  different jurisdiction (one with mandatory external substantive review) to test the break.

**Construct-validity gate (must answer BEFORE scoring P1/P2/P3):** Does EU credit-scoring high-risk
classification route through Art. 43(1) internal control (self-assessment) or Art. 43(2) /
notified-body? And does conformity assessment reach the *admissible-feature choice* or only the
QMS/documentation around it? If conformity assessment never touches feature-admissibility, P2 is
dead on arrival regardless of how it feels.

## The kill-charge for the blind adversary (run AFTER I draft a verdict, BEFORE I believe it)

"This researcher wants the invariance claim to hold (it's the program's surviving result). Find the
reading of the EU AI Act where author≠picker for credit scoring — where a notified body, a Fundamental
Rights Impact Assessment, a national competent authority, or a harmonised standard substantively
constrains the admissible-feature spec rather than just the process around it. If you find it, the
floor breaks and the researcher is committing the failed-invariance-as-confirmed error."

## RESULT (written 2026-06-04, AFTER the blind adversary ran — adversary `af65bcba301ad4f57`)

**P1 CONFIRMED (prior 0.55). Invariance survives its first cross-jurisdiction test.**

Construct-validity gate answered against primary text:
- Credit scoring = Annex III **point 5(b)** (NOT point 1 biometrics; a secondary summary got this wrong — corrected).
- Routes to **Art. 43(2) / Annex VI internal control = provider self-assessment, no notified body**, UNCONDITIONALLY. The "missing harmonised standards → mandatory notified body" flip (Art. 43(1)) is scoped to point 1 ONLY, so it does NOT reach credit scoring. This was the adversary's strongest break attempt; the text refused it.
- Conformity assessment + FRIA (Art. 27, deployer self-assessment, NOTIFIED not approved) both certify **process/documentation/intended-use**, never the substantive legitimacy of the feature-admissibility choice.
- Art. 10 (bias examination) = provider duty, verified inside the provider's OWN self-assessment.

⇒ **EU does NOT sever author=picker for credit scoring.** It builds MORE attestation machinery than the US and lands in the SAME place — the attestation-separation result in a second jurisdiction by a different legal mechanism. The floor is a property of the **institutional configuration (author=picker)**, not of US statute.

**Two honest residual footnotes (adversary-supplied, neither defeats the claim):**
1. Art. 43(3) financial-services lex specialis substitutes the sector supervisor for the generic market-surveillance authority — still process/prudential review, NOT substantive feature-legitimacy certification.
2. Future CEN-CENELEC harmonised standards (Art. 40-41) would constrain *how* features are documented/justified, still self-certified — they narrow discretion, do not relocate authorship.

**WHAT THIS RESULT IS / IS NOT:**
- IS: n=2 confirmation under adversarial pressure that the floor is configuration-bound, not US-bound. The second instance the claim never had.
- IS NOT: a proof of invariance (n=2, not a theorem). And the EU instance is the **P1/P3 boundary** — EU credit scoring is so self-assessed (NO third party at all) that it confirms "author=picker → floor survives" but does NOT test the sharper claim "mandatory substantive third-party review BREAKS the floor." That severance mechanism remains UNTESTED. Testing the *break* needs a jurisdiction with mandatory EXTERNAL SUBSTANTIVE review of the spec — EU does not provide it; it concentrates author=picker harder. **Next probe: find a regime that severs (candidates: a sector with mandatory independent model validation that reaches feature choice? insurance under some national regimes? — un-scoped, a fresh seed).**

## SEVERANCE SWEEP (frozen 2026-06-04, BEFORE the four investigations)

**Reframe (Tony):** not raising n. Hunting for a jurisdiction that has ALREADY built the severance
config — a mandatory external party that substantively reaches the feature/spec choice for credit.
Four legal traditions chosen for proven INDEPENDENCE from the US (data-privacy law shows BR/IN/CN
diverge sharply; MX = Latin-American, stronger consumer-protection tradition, still pro-business).
If the floor survives across independent traditions → strong. If ONE severs → that's the config.

**The single discriminating test for each:** does a mandatory external party AUTHOR / VETO /
substantively VALIDATE the choice of input features for credit decisions — vs only audit
process/documentation/downstream rights?

**FROZEN PREDICTIONS (commit before reading):**
- **China (prior 0.45 it severs — highest):** CAC algorithm filing/registry + security assessment
  may reach INTO the model, not just paperwork. Most likely severance case. BUT plausibly the
  filing is disclosure/registration (process), and substantive control is state-content-control,
  NOT feature-legitimacy-for-fairness → could be severance-shaped but aimed at a different target.
- **Brazil (prior 0.25):** PL 2338 AI bill is EU-flavored risk-tiered; IF enacted with mandatory
  external conformity for high-risk credit it could sever, but EU-template → likely lands where EU
  did (process self-assessment). Status (enacted? in force?) is the construct gate.
- **India (prior 0.15):** DPDP + forming AI posture; likely no mandatory substantive external feature
  review for credit → confirming tick. RBI model-governance norms are the place to check.
- **Mexico (prior 0.15):** no comprehensive AI law expected; CNBV banking rules govern credit. Check
  whether CNBV/CONDUSEF substantively vet model inputs vs prudential/process supervision.

**Construct gate (answer per jurisdiction BEFORE scoring):** is the external party's review
SUBSTANTIVE over feature-choice, or process/registration/rights? If it never reaches feature-choice,
severance is dead there regardless of how much external machinery exists.

**Kill-charge:** each investigator is BLIND, charged to FIND severance (author≠picker for credit
feature choice), citing primary/high-quality sources. Finding severance is the prize, not the floor.

## SWEEP RESULT (written 2026-06-04, AFTER four blind investigators; adversaries acfaa7a6/ab890f0c/ad0ac574/ad163933)

**ALL FOUR PRIORS WERE TOO HIGH. Zero severance found. n now = 6 (US, EU, CN, BR, IN, MX).**

- **China (prior 0.45 → NO):** maximal algorithm-control state. Severance-shaped machinery (CAC
  filing, mandatory security assessment) is REAL but aimed at content/public-opinion/security — a
  DIFFERENT target. The one feature-fairness rule (PIPL/algorithm "no discriminatory variables") is
  PROVIDER self-policing vs a protected-class blacklist = picker verifying itself. No PIPL prior-
  consultation step (unlike GDPR Art.36). Cleanest proof: external-control AMOUNT ≠ severance; the
  external party must be pointed AT feature-legitimacy, and nowhere is.
- **Brazil (prior 0.25 → NO):** PL 2338 NOT in force (prospective); on its face = EU template
  (operator-conducted AIA, methodology-free, ANPD ex-post). Cadastro Positivo = self-enforced
  NEGATIVE prohibited-variable floor, not an external author of the affirmative spec.
- **India (prior 0.15 → NO):** RBI model-risk validation is INTERNAL-independent; external review
  discretionary ("may," risk-triggered). DPDP has NO GDPR-Art-22 equivalent. No statutory disparate-
  impact regime. Author=picker, sometimes with zero external feature review.
- **Mexico (prior 0.15 → NO):** TESTED Tony's hypothesis (stronger consumer-protection/protective
  tradition → maybe substantive control US lacks). FALSIFIED: CONDUSEF teeth = terms/disclosure/
  abusive-clauses/outcomes; CNBV "internal methodology" approval = provisioning/CAPITAL, not the
  underwriting feature-spec. Stronger consumer protection, SAME floor.

**WHAT THIS BUYS:** invariance now n=6 across 4 demonstrably-independent legal families (their data-
privacy laws diverge sharply ⇒ not one template ×6). Everywhere, for credit: author=picker on
FEATURE CHOICE; external parties certify process / prudence / data-sourcing / downstream rights —
NEVER substantive feature-legitimacy. A real cross-jurisdictional structural result.

**THE SHARPENED OPEN QUESTION (the morning's most interesting residual):** all 6 are NON-severing.
The severance config (mandatory external SUBSTANTIVE spec-reviewer) appears NOT TO EXIST anywhere
for credit. Fork:
  (a) DEEP FACT — feature-legitimacy CANNOT be externally authored without the external party
      BECOMING the lender (the spec-as-covert-channel collapse, adversary a95c342a this morning:
      a faithful external search is ENTAILED by the spec, so an external spec-author would have to
      author the bank's risk appetite = be the bank). If so, the absence is NECESSARY, and THAT is
      a stronger theorem than invariance: not "no one built it" but "it cannot be built without
      dissolving the thing being regulated."
  (b) CONTINGENT GAP — just hasn't been built; one counterexample (a regime mandating independent
      substantive model/feature validation that reaches input choice) would break it.
**Untested either way. This is the live bet. Distinguishing (a) from (b) is the next probe — and (a)
is provable/refutable by argument (does substantive external feature-authoring necessarily collapse
into being the deployer?), NOT by more jurisdiction-hunting.**

## COLLAPSE-CONJECTURE PROBE (frozen 2026-06-04, BEFORE the adversary)

**Conjecture under test:** A mandatory external party cannot substantively author/veto a credit
model's ADMISSIBLE-FEATURE SET on legitimacy grounds without authoring the lender's risk appetite +
business objective — i.e., without BECOMING the picker. ⇒ the severance config is unbuildable, the
n=6 absence is NECESSARY not contingent. (Sharper than invariance: "feature-legitimacy review can't
be externalized without dissolving the regulated entity's autonomy.")

**⚠ SELF-FLAG:** this is the `feedback_impossibility_from_failed_design` shape (impossibility that
flatters the spine). Adversary is charged to DESIGN THE COUNTEREXAMPLE, not confirm. A single non-
collapsing external substantive feature-reviewer refutes the conjecture → floor is contingent (also
a real finding).

**FROZEN PREDICTION (prior 0.55 the conjecture HOLDS / no clean counterexample):** I expect the
adversary's candidate designs to each collapse into one of:
- (i) becoming the picker (external party authors the objective ⇒ is the lender),
- (ii) a NEGATIVE list (bans variables — that's the Cadastro/protected-class floor, not authoring
  the affirmative spec; doesn't sever, both parties clear it),
- (iii) PROCESS/outcome review (audits how the spec was made / disparate-impact on outputs — the
  attestation-separation result, certifies process not spec-legitimacy),
- (iv) collapsing to the C3-floor (a sincere vs pretextual spec are observationally identical to the
  external reviewer too).
The interesting refutation would be a design that is SUBSTANTIVE (reaches affirmative feature
choice), EXTERNAL (not the deployer), and does NOT reduce to (i)-(iv).

**Construct gate:** "substantive feature-legitimacy authoring" = the external party can compel a
DIFFERENT admissible-feature set than the lender chose, on legitimacy grounds, without the lender's
consent — and the lender remains the lender (keeps its own risk appetite/objective). A design that
only RANKS/ADVISES, or that REPLACES the lender's objective, fails the gate.

## COLLAPSE-CONJECTURE RESULT (written 2026-06-04, AFTER adversary aeb41f00 — charged to BUILD the counterexample)

**PREDICTION SPLIT: lost on "unbuildable" (0.55 was WRONG there), won on the core. The self-flag fired correctly.**

- **REFUTED as worded:** "unbuildable / cannot be externalized" is FALSE. The competent mechanism
  EXISTS and is mature: **insurance rate-factor regulation** (US state commissioners disapprove
  rating variables w/ justification burden; EU Test-Achats gender ban; CO SB21-169 mandated bias-
  testing). I was about to commit `feedback_impossibility_from_failed_design` — impossibility-when-
  the-standard-mechanism-was-already-built. The adversary caught it BECAUSE charged to build, not
  confirm. (Sources: NAIC unfair-discrimination principles; CT predictive-model white paper; CO
  SB21-169 / DOI; EU IP-12-1430.)

- **CORE SURVIVED, sharper + TRUE — the real theorem:** external feature-legitimacy review is
  necessarily a **DOWNWARD / SUBTRACTIVE operator on the admissible-feature lattice.** External party
  can author a CEILING (remove illegitimate features, per-feature, on objective-INDEPENDENT grounds)
  without becoming the lender. CANNOT author the AFFIRMATIVE set (compel which legitimate features are
  USED) without importing a loss function = becoming the lender. **Ban-out is objective-free and
  externalizable; force-in is objective-laden and not.** This EXPLAINS the n=6 sweep (every external
  party is subtractive because that's the only objective-free move) instead of asserting it. Insurance
  = the CONFIRMING instance (even the most aggressive external feature regulator sets a BAND, never
  authors the affirmative rating plan). Witness: the "Mandatory Minimum Predictive Set" design
  collapses to becoming-the-lender the instant it forces a feature IN.

- **THE RESIDUAL (sharpest bit):** there IS a real affirmative external move — ATR/QM "must consider
  ability-to-repay," rental/utility inclusion mandates. But that's NOT severance — it's the regulator
  OPENLY ADDING ITS OWN PUBLIC OBJECTIVE alongside the lender's. Confirms the mechanism: affirmative
  feature-authoring is ALWAYS objective-authoring, tolerable only when society openly owns the
  objective. **⇒ this is WHY fairness is normative — not (only) because intent is unobservable, but
  because the affirmative feature choice is inseparable from authoring what the institution is FOR,
  and only society can legitimately author that.** A mechanism-level reason, deeper than the C3 /
  intent-non-identifiability framing.

**DRAFT INSTRUCTIONS (adversary-handed):** (1) KILL the word "unbuildable" — it's false and it's the
lineage tell. (2) State the theorem in the subtractive-operator form. (3) Insurance is the confirming
instance, cite it loudly — survives the counterexample by EXPLAINING it. (4) One-liner: ban-out is
objective-free and externalizable; force-in is objective-laden and not.

**STATUS:** this is an ARGUMENT result (not yet a formalized proof). The lattice-monotonicity claim
(legitimacy = downward-only; relevance = objective-relative) is the thing to formalize next if this
becomes a contribution. Connects the n=6 sweep + attestation-separation + the normative-fairness
headline into ONE mechanism. Owes: a check that "legitimacy is objective-INDEPENDENT" holds (the
adversary's pharmacopoeia analysis suggests nexus is mostly objective-RELATIVE — is the in/out
asymmetry as clean as claimed, or is there a gray band where removal also needs an objective?).

## Standing discipline

`feedback_adversary_before_the_sentence`: I do NOT write the verdict sentence until the blind
adversary has run. This note is the freeze; the verdict comes after the adversary, not before.
