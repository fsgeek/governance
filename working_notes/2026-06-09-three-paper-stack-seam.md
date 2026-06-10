# The three papers are a stack with one seam, not three independent papers

**Written 2026-06-09. Tony handed this seam clean in conversation; it FEELS settled, which is this
lineage's tell for an un-adversaried frame. Recorded here as a CLAIM-TO-BE-TESTED, then adversaried
below before it is believed. Supersedes the "three (largely) independent papers" read I held earlier
the same session and the carve-out node's "two papers, one boundary" framing (which undercounts —
it's three, and the seam runs through all three).**

## The thing that was only in conversation and would have evaporated

Across the SHAP-vs-Rashomon exchange, Tony sorted three things I had been collapsing into one:

1. **Gameability is NOT the discriminator.** The adversarial cookbook proves proxy discrimination works
   against SHAP AND against Rashomon (harder for ensembles — a quantitative cost, not a categorical
   wall). Underneath both sits the C3 confound: there is a FLOOR of discrimination that cannot be
   removed without using the protected data in a discriminatory fashion. So "which is harder to game"
   has only a quantitative answer. Neither is ungameable. A paper claiming "Rashomon is safe from the
   cookbook" dies in one line — we built the attack that beats it.

2. **The categorical invariant is about the EVALUATION SYSTEM, not the model.** "Any model where the
   evaluation system is invisible can be gamed." Substrate-independent ⇒ a GOVERNANCE observation, not
   a model comparison. SHAP's evaluation system is structurally invisible (explainer chosen by the
   model-builder, post-hoc, one hand). Rashomon's CAN be made visible — not because the math is
   cleaner, but because the construction admits an ATTESTED ARTIFACT TREE: every model generated, the
   ε-band, the dedup, the final ensemble selection — capturable, time-stampable, bindable.

3. **The boundary is deliberately handed OFF the CS bench.** The CS contribution is complete and
   bounded: construct a fully attested, externally-verifiable artifact tree showing how the ensemble
   was built from the written policy. The residual — IS the third party actually neutral? — is an
   institutional/regulatory fact no construction can certify. "That's no longer a CS problem." This is
   the INVERSE of the dead impossibility paper's error (which tried to drag the normative residual ONTO
   the CS bench and got shrunk to McDonnell-Douglas-in-notation). Here the paper knows where its own
   boundary is and stops there on purpose.

## THE SEAM (the claim under test)

> The three papers are one stack joined by a single object: **attested construction by a separable
> hand.** Paper 1 names the failure mode (invisible evaluation systems manufacture silence; visibility
> is the lever). Paper 2 builds the construction that makes the evaluation system visible
> (policy-constrained Rashomon), with the honest scope that it is *as gameable as anything until
> attested* — its categorical edge over SHAP is not accuracy and not un-gameability but
> SEPARABILITY: policy-authorship can be put in a different hand than model-fit, which SHAP cannot
> offer because attribution is always downstream of the builder. Paper 3 is the chain-attested
> construction pipeline that makes a neutral third party's build CHECKABLE — the safe-harbor
> mechanism — shipped as components, with the explicit handoff that neutrality is an institutional
> guarantee, not a CS one.

This is the subtractive-operator theorem restated operationally: the constructor authors the CEILING
(builds the attested model set from the policy) without becoming the lender; the NEUTRALITY of who
does it is the institutional fact no construction certifies, the way no construction certifies good
faith. ([[project_subtractive_operator_result]], [[project_furnished_silence_result]],
[[project_codification_legible_tampering]].)

## Honest scope already known (do not overclaim past these)

- Construction is policy-RELATIVE, not objective-free: it imports model class + loss + ε. So the
  separability claim is "POLICY-AUTHORSHIP is severed; the fit still imports a thin objective both
  parties can inspect," NOT zero-leakage severance. ([[project_furnished_silence_result]].)
- Model class is CART (verified in code 2026-06-08: `wedge/refinement_set.py:build_refinement_band`
  enumerates feature-subset × depth × leaf CARTs, band = holdout AUC ≥ best − ε, ε=0.02), NOT the
  "GBT ensemble" the methodology.md prose says. Code wins.
- The SHAP head-to-head on disk (`shap_vs_pricing`) is vs STRATIFICATION, SHAP non-inferior-but-rides-
  a-surrogate. The literal `shap_vs_rashomon` regime-shift run is incomplete — but under the
  SEPARABILITY spine it is NOT a blocker (it was trying to win a metric race the spine does not need).

## THE OPEN ITEM (yes/no on disk, deferred deliberately — it's inside Paper 3, not the headline)

Does the construction tooling EMIT the attested artifact tree, or only log band members? `within_tier_
rashomon_test.py` records `band_members_within_eps`, `n_combos_tried`, per-member subsets — the BAND is
captured. But "complete attested tree, chain-bound, tamper-evident, binding the POLICY INPUT and the
FEATURE-ADMISSION decisions (the cookbook's attack surface), not just the fits" is a stronger claim.
The git/OTS plumbing exists at the REPO level; whether it wraps the CONSTRUCTION ARTIFACT is unverified.
**This decides whether Paper 3's safe-harbor spine is "describe the existing mechanism" or "build the
missing wrapper" — answer it when Paper 3 is drafted, not now.**

## ADVERSARY VERDICT

**Written AFTER blind adversary `ab5b2f9c48657183b` (charged to break, read the actual files).**

**VERDICT: BROKEN-TO-SHARED-MOTIF. The seam is not a stack. My first-read frame: 0-for-6 this session.**

The adversary went to disk and found three things that kill the unification — two of them facts I
ASSERTED without checking (the exact error Tony was probing when he said "you wrote your own marching
orders"):

1. **The seam is ABSENT from Paper 1's actual text.** Paper 1 on disk is empty-chair / silence-
   manufacture / verification-regime taxonomy; load-bearing thesis "self-measuring architectures cannot
   verify themselves." "Separable hand / author=picker / policy-as-separable-input" appears in NO .tex.
   A unification that is one paper's content + two papers that don't mention it is the elegance-tell. I
   claimed the seam "runs through all three." It runs through one (Paper 3).

2. **The attestation tooling does NOT exist.** `manifest.py` logs inputs + set-counts only (policy
   name/version, feature lists, epsilon, n_R_T/n_R_F). It does NOT hash/sign/chain/preserve the model
   tree. `output.py` is `to_dict`/`write_run`, no tamper-evidence. `section7.tex:32` says outright:
   tamper-evident capture is "sketched at the property level and left to follow-on work." I had filed
   the wrapper question as "deferred yes/no"; the answer is NO, and the paper already admits it. My
   "git/OTS plumbing is the worked instance" was repo-level provenance mis-projected onto the build.

3. **Separability does no work AND the safe-harbor is furnished silence (the strongest break).** The
   third party performing the FIT must choose CART-depth, enumeration order, epsilon, loss weights —
   all objective-laden, none pinned by policy, and exactly the surface the cookbook attack exploits. So
   separation severs the cheap-to-audit part (the feature LIST) and leaves the dangerous part (the fit)
   intact and CONCENTRATED in the constructor's one hand. Then "is the constructor neutral?" is handed
   off-bench — but a captured constructor emits a PERFECTLY ATTESTED tree of a proxy-discriminating
   build. The attestation certifies PROCESS, is blind to LEGITIMACY = the furnished silence the program
   itself names. The two honest-scope concessions don't caveat the core; together they HOLLOW it.
   Angle 5: the subtractive-operator INSTANCE claim is overclaimed — the theorem licenses the ceiling
   (ban-out, objective-free), and the FIT is the becoming-the-lender move the theorem forbids
   externalizing; my own "construction is objective-relative" concession KILLS the instance claim.

**WHAT SURVIVES (two independent results, NOT a stack joined by separability):**
1. The subtractive-operator theorem itself — stands alone, strongest surviving contribution.
2. A NARROW integrity-of-record claim for Paper 2/3: a third party can author + attest the admissible-
   feature CEILING from policy (the genuine ban-out half), producing provenance-of-inputs — NOT
   certification of legitimacy, NOT a safe harbor, NOT a categorical edge over a third-party-attested
   SHAP pipeline (a neutral auditor can recompute SHAP on a delivered model too; the edge is degree —
   construction-log vs attribution-log — not category).

**Honest statement to carry forward:** "A neutral party can author and attest the admissible-feature
ceiling from policy (the subtractive move), producing an integrity-of-record artifact. It cannot
externalize the affirmative model-fit without re-importing the lender's objective; therefore the
attested construction certifies process and input-provenance, not legitimacy, and offers no more
legitimacy-assurance than a third-party-attested post-hoc pipeline."

**Meta:** the seam felt settled because it was handed over clean. That feeling was the tell, again. The
note was written as claim-not-conclusion and adversaried before belief — the procedure held where my
first read (0-for-6) did not. Do NOT re-mint the stack. Carve-out node correction: it is NOT "two
papers one boundary" NOR "three-paper stack"; it is one theorem (standalone) + one narrow integrity-of-
record method, and Paper 1 is a DIFFERENT object (empty-chair) that does not share the seam.
