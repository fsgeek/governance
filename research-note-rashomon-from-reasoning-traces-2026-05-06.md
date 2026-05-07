# Rashomon-Derived Interpretable Models from Captured Reasoning Traces

**Author:** Tony Mason / wamason.com LLC
**Date:** May 6, 2026
**Status:** Working research note — not for distribution
**Origin:** Synthesis emerging from analysis following Anthropic's May 5, 2026 financial services agent announcement, building on the Titan Governance Architecture (April 2026) but extending in directions that warrant independent documentation.

---

## 1. Context

On May 5, 2026, Anthropic released ten financial services agent templates — pitchbook builders, KYC screeners, statement auditors, valuation reviewers, and others — packaged as combinations of skills (instruction sets), connectors (governed data access), and subagents (focused model calls). The release made several things simultaneously sharper:

- The "AI in compliance theater" failure mode now has a named, productized instance. The KYC screener, in particular, has Claude assigning risk ratings, applying rules, and producing structured outputs that humans review and approve. The audit trail is the AI's chain-of-thought, which is itself a generated artifact rather than a faithful trace of the computation that produced the output.
- Rudin's 2019 critique of post-hoc explanation for high-stakes decisions has a sharper LLM-era reading: with separate explanation models (SHAP, LIME), the explanation can at least in principle be measured against the underlying model's behavior. With chain-of-thought from the same model that produced the decision, the "explanation" is just another forward pass.
- The Titan governance architecture, framed as community-bank specific, is structurally a general theory of regulatory governance for AI-mediated decisions in audited contexts. The community-bank framing is a marketing wrapper.

This note documents a synthesis that goes further than the governance architecture as written: the architecture is not only a defensive substrate (keeping AI out of where it doesn't belong) but a *generative* substrate (producing the conditions under which AI can be deployed in high-stakes regulated decisions in a way Rudin would endorse).

## 2. Core Synthesis: Rashomon Sets from Reasoning Traces

The standard interpretable-ML pipeline (Rudin, 2019) collects outcome data, trains models, and searches the Rashomon set — the set of models within ε of optimal loss — for an interpretable variant. The argument is that the Rashomon set is typically populous enough that an interpretable model exists; one should select it directly rather than train a black box and explain it post hoc.

The proposed methodology collects something richer than outcomes. The epistemic capture layer of the governance architecture records reasoning *traces*: case features, consultation patterns, relational weightings between considerations, references to institutional precedent, and the resulting decision. This changes what the Rashomon set means.

Models in the search space aren't just matching verdicts; they're matching reasoning paths. The interpretability criterion sharpens: a model whose internal structure mirrors how the institution's officers actually reason is interpretable in a structurally meaningful sense — its operations correspond to the operations a human officer performs on the same case. Post-hoc explanation isn't required because the model's structure is the explanation.

The pipeline:

1. Capture reasoning traces via the epistemic capture layer (architecture Layer 1).
2. Augment with historical decisions where reasoning context can be reconstructed from secondary records.
3. Search the Rashomon set of models reproducing both verdicts and reasoning paths.
4. Validate selected models via back-testing against the real corpus.
5. Deploy with continuing attestation (architecture Layer 2) against new captured decisions; the corpus and the deployed model evolve together.

## 3. The Synthetic / Real Data Taxonomy

Synthetic and real data have distinct, non-interchangeable roles. Conflating them collapses the validity story.

**Synthetic data — three roles:**

- *Demonstration.* PII-free illustration of system capabilities for sales conversations, regulator briefings, peer-institution discussions. Validity bar: representative enough to illustrate. The lowest bar of the three.
- *Hypothetical-scenario modeling.* Mergers, expansions, demographic shifts, new product lines, market entry into novel geographies, divestitures. No real data exists for situations that haven't occurred. Validity bar: faithful modeling of the hypothesized condition. Higher than demonstration; the synthetic distribution must reflect the structural features of the hypothesized population.
- *Model regression-testing.* A fixed synthetic suite replayed through derived models over time, surfacing behavioral divergence on cases the model has previously processed consistently. Validity bar: stability of the test set across deployments.

**Real data — two roles:**

- *Back-testing for model fidelity.* Validating that derived models reproduce institutional decisions on the actual historical corpus. Validity criterion: fidelity to what was actually decided. Synthetic decisions cannot answer this question, because the question is whether the model captures *this* institution's reasoning.
- *Compliance-change-impact analysis.* Applying modified rules to historical decisions to estimate the distributional impact of regulatory or policy change. The downstream application of validated models.

The synthetic/real boundary is not a privacy convenience. Synthetic data can encode the assumptions being tested, contaminating downstream inferences in ways that are difficult to detect and harder to undo. Each pipeline must remain segregated by design.

## 4. Counterfactual Replay as Regulatory Instrument

Once derived models are validated against the real corpus, counterfactual replay becomes possible: replay historical decisions through modified rules, modified model variants, or modified institutional policies. This shifts the epistemic standard for compliance from precedent-based argument to experimental analysis.

For the institution: quantified impact analysis of regulatory changes before adoption, identification of marginal cases that would shift under new thresholds, principled identification of officer training needs, and pre-emptive analysis of where existing practice diverges from proposed standards.

For the examiner: a community bank can answer "is your governance commensurate with your risk profile?" not by argument but by demonstration. Here is the distribution of cases under current standards. Here is the distribution under stricter standards. Here is the threshold at which we believe risk is appropriately controlled, with the supporting evidence drawn from our own history.

For the regulator: if multiple institutions contribute model-level analysis to an anonymized meta-corpus, industry-level impact analysis of proposed rule changes becomes feasible — a capability that does not currently exist.

A liability surface deserves explicit attention. A bank presenting "here is what would have happened under the new rule" is also implicitly presenting "here is what we would have done differently." The framing must be that the counterfactual is *about the rule*, not about the prior decisions, which were appropriate at the time they were made under the standards then in force. This is a presentation discipline more than an architectural one, but it is decisive for adoption.

## 5. M&A and Expansion: A Scale-Invariant Application

The methodology is scale-invariant across institutional events that change the population of cases an institution decides upon:

- **Mergers and acquisitions.** Project divergence between institutional decision patterns of acquirer and target. Identify integration risk by case category. Quantify projected post-merger compliance posture. Surface cultural integration questions before they become operational ones.
- **Expansion.** Branch network growth, new product lines, market entry into demographically different geographies.
- **Contraction.** Divestitures, branch closures, product line discontinuation.
- **Demographic change.** Aging customer base, migration patterns, generational shifts.

M&A is the highest-stakes recurring event, with several properties that make it a particularly strong use case:

- Recurring across institutions of every size on some cadence.
- High stakes per event: transaction values from $50M for community-bank tuck-ins to $50B+ for Tier-1 combinations.
- Three regulatory stakeholders per deal: acquirer's primary regulator, target's primary regulator, deal-approval regulator.
- Three buyers per deal: acquirer wants integration risk analysis, target wants to understand its negotiating position, regulator wants quantified post-merger compliance posture.
- Methodology compounds across deals: each integration provides post-mortem data on where projections matched outcomes.

This use case is independent of bank size. The methodology applies across community, regional, and Tier-1 banks with the same structural validity. The community-banking framing in the original architecture is a calibration choice for a particular regulatory narrative, not a structural constraint on the methodology.

## 6. Connection to Rudin: Extending Interpretability for LLM-Mediated Decisions

Rudin (2019) argued that for high-stakes decisions, post-hoc explanations of black-box models are inadequate; the Rashomon set typically contains interpretable models, and one should be selected directly rather than producing post-hoc explanations of opaque ones.

The synthesis extends this position in two ways:

First, the LLM-era failure mode is sharper than the SHAP/LIME case Rudin originally critiqued. With separate explanation models, the explanation is at least in principle measurable against the underlying model's behavior. With chain-of-thought from the same model that produced the decision, the explanation is itself a generated artifact — another forward pass, not a trace of the computation that produced the output. Selling chain-of-thought logs as compliance evidence instantiates exactly the failure Rudin warned against, in newer language and with weaker epistemic grounding.

Second, the architecture proposes a stronger position than Rudin's prescription. Not "use interpretable models for the decision," but: *keep models out of the decision and capture the interpretable substance directly* — the human's contemporaneous reasoning. The AI's role becomes pattern recognition over the corpus of those decisions, a use case where post-hoc explanation is not asked for because the AI is not making the call. Models derived from the corpus, via the Rashomon-from-reasoning-traces pipeline above, can subsequently handle routine cases under the principle that they replicate institutional reasoning paths rather than approximating institutional verdicts.

This is a structural position rather than a methodological one. It does not depend on the choice of model architecture, the loss function, or the specific interpretability technique. It depends on where the AI sits relative to the decision.

## 7. Drift Taxonomy Refinement

The four-type drift taxonomy from the governance architecture, refined with data sources:

- **Institutional drift** (de facto practice vs. de jure policy): real corpus, direct observation. Surfaces divergence between what the bank says it does and what its officers actually do.
- **Decision-maker drift** (officer inconsistency): real corpus, direct observation. Surfaces inconsistency across officers and shifts within a single officer's patterns over time.
- **Model drift** (derived-model divergence from baseline): synthetic regression-testing suite, replayed through deployed models over time. The fixed synthetic test set is the stable reference point.
- **Adversarial drift** (multi-round behavioral manipulation by external actors): real corpus with retrospective augmentation, as architecture Layer 4 specifies. The detection mechanism is the combinatorial sampling against multiple analytic perspectives.

Each drift type now has a clearly delineated data source and methodology. The synthetic/real boundary is what makes each drift methodology epistemically defensible. Mixing data sources across drift types — using real cases for model regression testing, or synthetic suites for institutional drift detection — collapses the validity story.

## 8. Open Questions

- **IP attribution.** Which elements of this synthesis pre-existed the Titan engagement and which emerged within it. The Rashomon-set methodology is Rudin's. The reasoning-trace capture is from the wamason.com governance architecture (April 2026). The Rashomon-from-reasoning-traces synthesis itself was articulated on May 6, 2026, in conversation following the Anthropic announcement. The M&A scaling application was articulated in the same conversation. Where these fall under "Pre-existing wamason.com LLC IP licensed to Titan on a non-exclusive basis" versus "All work product belongs to Titan" is a question for the engagement letter and possibly for a clarifying email.

- **Validation methodology.** What empirical tests demonstrate that derived models are matching reasoning paths and not just verdicts. Candidate tests: held-out reasoning-path prediction; ablation of consultation-pattern features; comparison against verdict-only-trained baselines on cases where the same verdict could have arisen from different paths.

- **Synthetic-distribution validation for hypothetical-scenario modeling.** Independent measures for evaluating whether synthetic distributions faithfully model hypothesized conditions — particularly for M&A integration analysis, where the "hypothesized institution" is a structured combination of two real institutions.

- **Regulatory acceptance.** Examiner readiness for counterfactual evidence as compliance posture. Pilot conversation with the OCC, possibly via Titan's existing relationship, to test the framing.

- **Vendor positioning.** How this methodology positions against Anthropic's general-purpose financial services agents (KYC screener, statement auditor) and analogous offerings as they emerge. The structural argument — generic vendor model vs. institution-specific Rashomon-derived model — is sharp, but adoption depends on whether the market sees the difference.

- **Multi-institution federation.** Whether an industry-level meta-corpus is feasible while preserving institutional confidentiality. Federated learning over derived models, rather than over raw decisions, may be the right primitive.

---

*End of working note. Threads worth picking at first: the IP attribution question, since it has the lowest cost to address and the highest cost if neglected; and the validation methodology section, since it determines whether the synthesis is a research artifact or a deployable approach.*
