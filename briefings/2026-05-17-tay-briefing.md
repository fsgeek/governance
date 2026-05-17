<!--
Briefing draft prepared 2026-05-17 for the Olorin CEO (pseudonym: Tay).
Pre-send pseudonymized version preserved in the public repo as engagement
evidence; real-name version and any salutation / voice adjustments for the
actual send happen offline, separately from this artifact. Pseudonyms in
use: Olorin (layer-1 company name), Tay (layer-2 CEO name); see
[[feedback_pseudonym_discipline]] in auto-memory for the layering
discipline.
-->

# Catch-up note for Tay

Welcome back —

While you were out, the research arc hit several pivots worth your attention. Rather than send a status report, here are the three threads I think you'd want to know moved.

## 1. The Rashomon ensemble construction is the technical artifact that survives.

The construction methodology we've been developing — variant-A/B policy-band pairs at ε-AUC tolerance with feature-set deduplication — is empirically non-inferior to SHAP and LIME across every substrate we've tested. That's LendingClub loan-grade vintages, Fannie Mae 30-year loan performance, and HMDA-RI 2022 mortgage lending data. We didn't set out to beat post-hoc explainers; we set out to test whether a construction-based alternative could match them. It can.

What the construction adds beyond non-inferiority is workflow legibility. SHAP and LIME produce per-decision explanations calibrated on the model's outputs, not on the bank's policy. The Rashomon refinement set produces an artifact legible against the policy directly — admissible models, the disagreement region between them, and the features driving that disagreement. That's the artifact a regulator can read; the SHAP-vector is the artifact a regulator has to take on faith.

One thing I want to flag specifically: the academic literature on *constructing* Rashomon ensembles is unusually thin. The AI/ML community has favored theoretical analysis of these sets over empirical construction recipes. The methods paper I'm drafting is therefore not pitched as "a better construction" — it's one of the few empirical constructions in a literature that's been waiting for them. That's a sharper contribution than "we have a construction that works."

Operationally for production use: this is the explainability primitive robust enough to scale. Other findings in the program have moved, been refined, or been falsified. The construction has not.

## 2. We pre-registered a substrate-transfer test and it failed clean.

Two weeks ago I found a phenomenon on Fannie Mae data I've been calling "manufactured silence" — certain demographic-saturation profiles cause the model to reorganize its decision-feature set in a way that hides what it's actually doing under the formal policy vocabulary. The pattern was real, statistically clean, and bounded (three cells out of twenty-nine, all in one 2016 vintage).

I pre-registered the substrate-transfer test on HMDA-RI 2022 lending data — committed the predictions and stamped them before touching the data — and the prediction was falsified cleanly. The discriminator we used to detect manufactured silence was calibrated on Fannie Mae and didn't survive a substrate change.

The methodological consequence is more interesting than the falsified prediction itself. It suggests the verification machinery is not separable from the substrate it verifies on — the explainability artifact needs substrate-context declared explicitly, not buried in calibration. This is unusual for ML methodology and reorganizes how the explainability layer would be designed in production. It's also the kind of finding only available if the methodology imposes pre-registration discipline; SHAP-and-LIME-style workflows would have generated a different threshold on HMDA without noticing the substrate-indexicality.

This thread is the one that most reshapes the architecture going forward. Construction (thread 1) is the production-ready piece; this (thread 2) is the methodological surprise.

## 3. Manufactured silence is concrete for bank examination.

The Fannie Mae result is concrete in scope and concrete in what it would mean for examination. Three cells in the 2016 vintage show the reorganization pattern: decisions that look like they're using the policy vocabulary when they're actually routing through demographic-saturation channels invisible to post-hoc analysis. The volume is small; the structural meaning is not. This is exactly the kind of behavior an examiner would want a detection tool for, and SHAP/LIME reporting wouldn't surface it — post-hoc explanation will report whatever features the post-hoc method finds, regardless of whether the model is actually using them.

The Rashomon construction provides the basis for a detection tool. Comparing the disagreement region between policy-conforming and policy-relaxed model variants makes the reorganization visible. This is not yet a production tool — it's a result that says one is buildable. SR 11-7 expectations around model risk and current OCC concerns about explainability-vs-faithfulness would find this directly applicable.

## Closing

The work itself is in the public repository at github.com/fsgeek/governance — the trajectory, the pre-registrations and their results, the methods paper as it's being drafted. The consolidated path document I'm finalizing this week pulls the trajectory together; the methods paper that follows it will land in the same place.

If any of these threads are worth a longer conversation when you have time, I'd be glad to dig in.
