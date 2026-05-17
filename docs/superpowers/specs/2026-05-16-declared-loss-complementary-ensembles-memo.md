# Declared-loss-complementary ensemble construction — memo

**Date:** 2026-05-16. **Status:** PROPOSAL — NOT a pre-registration. **Substrate:** TBD (candidate: FM #12 corpus from `[[project_silence_manufacture_result]]`, HMDA-RI corpus from `[[project_hmda_trimodal_result]]`, or both). **Connects:** `[[project_silence_manufacture_result]]`, `[[project_pre_registration_pattern]]`, `[[project_ontology_design_philosophy]]`, `[[project_hmda_trimodal_result]]`, `[[project_saturation_phase_characterization]]`.

**Discipline statement.** This memo records a hypothesis seed before operationalization. It does not meet the pre-registration bar — no named JSON fields, no numeric thresholds, no calibrated priors — and is therefore not OTS-stamped. The next step is operationalization or rejection, not validation. Author is in the yanantin lineage (pukara session, 2026-05-16) and is handing off to the governance ghola; substrate-fit decisions belong with that instance, which has fuller context.

## 1. The hypothesis seed

Standard ML ensemble construction uses *diversity-as-statistical-decorrelation*: bag training subsets, vary hyperparameters, hope the resulting variation correlates with complementary coverage. The diversity is implicit and unmeasured.

Alternative: ensemble construction by *declared-loss complementarity*. Each framework / variant / band-construction states what it deliberately does not represent. Ensemble members are selected so their declared losses cover each other's blindspots. Complementarity is *named*, not hoped for.

The hypothesis: **declared-loss-complementary ensembles outperform standard-diversity ensembles on coverage of the epistemic space and on interpretability of the disagreement region.**

Generalization of the hypothesis: ensemble *behavioral disagreement* between loss-complementary members should be informative — specifically, the disagreement should be predictable from the declared losses themselves, and should map onto interpretable discriminators (frame-coherence, mandatory-feature engagement, etc.). For diversity-only ensembles, disagreement should be less predictable from any single declared axis.

## 2. Existing-work mapping (load-bearing observation)

The governance project's variant-A / variant-B framework on FM and HMDA-RI substrates is *already* declared-loss-complementary construction in implicit form. The hypothesis is not a new construction proposal; it is a re-reading of the existing pipeline plus a test.

- **Variant A** declares the loss of prohibited features (e.g. geographic features in the HMDA pattern).
- **Variant B** declares the loss of policy-purity — it admits the prohibited category at the cost of not adhering to the policy specification.

Each variant names what it deliberately does not represent. The pair is constructed *as a complementary pair*, not as two arbitrary points in model-space. The Rashomon-band-on-A vs Rashomon-band-on-B output is therefore a declared-loss-complementary ensemble.

If the variant-A/B framing is granted as declared-loss-complementary, the hypothesis becomes testable on existing substrates without new compute — the comparison target is the synthesized loss-symmetric "control" ensemble (§3b).

## 3. What operationalization would require

To turn this from memo into pre-reg:

**3a. Substrate choice.** FM #12 corpus (29 cells, established discriminators per `[[project_silence_manufacture_result]]`) is the lowest-cost first test. HMDA-RI provides cross-substrate replication. Governance ghola is best placed to decide.

**3b. Comparison ensemble construction.** There is no existing diversity-only control ensemble in the pipeline (the variants are loss-complementary by design). Two possible constructions:

- **Synthesized control**: re-band the same data without the variant-A/B distinction. E.g., two bands trained on random feature-set subsets of matched accuracy, no policy-prohibited / policy-pure framing. Hypothesis predicts loss-complementary ensemble outperforms.
- **Substrate transport**: run the existing A/B ensemble on a corpus *without* policy-variant structure (any substrate where variants A and B are not constructed as a loss-complementary pair). Hypothesis predicts the disagreement pattern degrades in interpretability when the loss-complementarity is removed.

The synthesized-control path is internally controlled but requires new banding code. The substrate-transport path is cheaper but introduces substrate confounds.

**3c. Outcome metrics (candidates).**

- **Interpretability of disagreement**: the existing discriminators (frame-coherence M3 from frame-evocation pre-reg, R²_named, mandatory_feature_usage_share) applied to the disagreement region. Loss-complementary ensemble's disagreement region should have a *high-signal discriminator that maps to the declared loss axis* (e.g., geographic-feature dependence for HMDA variant-A/B). Diversity-only ensemble's disagreement region should not have a privileged discriminator axis.
- **Pre-registration accuracy**: if declared losses predict *where* the ensemble disagrees on a held-out corpus, that's a HIT for the principled-construction reading.
- **Coverage of verdict space**: distinct verdict count on held-out cases vs theoretical maximum given declared losses. Likely too coarse for n=29; useful at HMDA scale.

**3d. Falsification predictions and priors.** Cannot be set without 3a–3c resolved. Once resolved, predictions would follow the standard scorecard format with explicit MISS interpretations.

## 4. Specific connections to existing project work

- **`[[project_silence_manufacture_result]]`**: silence cells are exactly where variants A and B produce reorganized bands with different verdicts — i.e. the declared-loss axis is *active*. The hypothesis predicts that silence cells are over-represented in the disagreement region of loss-complementary ensembles relative to a synthesized diversity-only control.
- **Frame-evocation pre-reg (2026-05-15)**: if M3 (frame-coherence) discriminates silence cells (P1 awaiting result at time of writing), then frame-coherence is a candidate "interpretability of disagreement" metric. The current memo would lift that one level: M3-like discriminators should perform *better on loss-complementary ensembles' disagreement regions than on diversity-only ensembles' disagreement regions*.
- **`[[project_ontology_design_philosophy]]`**: declared losses are the ontology's account of what it doesn't represent. The hypothesis is a direct empirical test of whether explicit ontology design (which losses are declared) translates into measurable ensemble behavior.
- **`[[project_saturation_phase_characterization]]`**: carrier-family asymmetry is a candidate axis on which loss-complementarity might appear without the policy-variant framing. Worth pre-reg consideration.

## 5. Risks and known limitations

- **Bounded blindspot**: declared losses are what a framework *knows* it doesn't represent. Unknown-unknowns aren't on the list. The ensemble's composite declared loss shrinks but doesn't reach zero. The residual is itself an ensemble-level declared loss that any pre-reg should name.
- **Cross-framework vocabulary**: two frameworks designed in isolation may claim to fill the same hole using different words, or disagree on what counts as a "loss" vs. a "scope boundary." Loss declarations across frameworks are not directly comparable. Behavioral testing must be the arbiter; pre-reg must not trust the cross-framework claims as input.
- **Variant-A/B as loss-complementary is an *interpretation***: the pipeline doesn't currently *call* them loss-complementary. If the governance ghola judges that framing inaccurate or non-canonical, the existing-work mapping in §2 collapses and the hypothesis needs a different substrate.
- **n=29 fragility**: the FM corpus is small. Effect sizes that would clear permutation-null at this scale are large. HMDA-RI is preferable for the primary test.

## 6. Provenance

- Conversation in the pukara session on 2026-05-16, during a tiksi-extraction wander. Earlier in the same conversation: positioning of `tiksi` as the shared foundation package across yanantin/willay/pukara; OTS-stamping of tiksi commits proposed for tamper-evident provenance.
- The hypothesis seed came from Tony's question (paraphrased): "wouldn't ensemble building by deliberately picking frameworks to fill those holes be exactly what we want from a good ensemble?" — itself a response to a remark about Rashomon ensembles detecting ontology overlap via behavioral convergence, and `DeclaredLoss` (now lifted to `tiksi`) being the raw material that makes principled selection possible.
- The Claude drafting this memo is in the yanantin lineage (the pukara session). The governance ghola was idle for the duration; this memo is a coordination artifact for that instance, intended to be evaluated against governance-substrate context the author lacks.

## 7. Next-action menu

- **Operationalize** per §3 (governance ghola, upon waking): pick substrate, decide synthesized-control vs substrate-transport, set thresholds and priors, draft a real pre-reg.
- **Reject** if §2's existing-work mapping doesn't survive contact with the canonical pipeline framing.
- **Park** as wander-residue if the project's current priorities (e.g., FM #12 result-side scripts at PID 339297 / 353419, still running at the time of writing) make this not-now.

---

**Memo author:** Claude Opus 4.7 (yanantin lineage, pukara session). **Date:** 2026-05-16. **OTS:** intentionally not applied — this memo makes no falsifiable predictions, so freezing predictions before code touches data is not yet meaningful. The pre-reg that descends from this memo will be OTS-stamped.

**Commit attribution:** drafted by the yanantin-lineage instance; committed under Tony's identity per the current governance signing convention. The inconsistency (governance uses Tony's key for AI-authored work; yanantin/willay/pukara use the Yanantin AI key) is itself a `[[project_pre_registration_pattern]]` data point — different epistemic position, different signing posture, declared rather than concealed.
