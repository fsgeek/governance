# FS AI RMF Position Paper — Persona Review Findings

**Total findings:** 57 (9 FATAL / 35 MAJOR / 13 MINOR)

## Per-persona summary

| Persona | Model | F | M | m | Total |
|---|---|---:|---:|---:|---:|
| civil_rights_attorney | `qwen/qwen3.6-plus` | 1 | 3 | 1 | 5 |
| compliance_officer | `mistralai/mistral-large-2512` | 1 | 4 | 3 | 8 |
| examiner | `deepseek/deepseek-v4-pro` | 2 | 3 | 2 | 7 |
| frame_skeptic | `x-ai/grok-4.3` | 2 | 3 | 1 | 6 |
| self_examiner | `openai/gpt-oss-120b` | 1 | 3 | 2 | 6 |
| sympathetic_regulator | `z-ai/glm-5.1` | 1 | 5 | 1 | 7 |
| technical_reviewer | `anthropic/claude-haiku-4.5` | 0 | 9 | 1 | 10 |
| vendor | `anthropic/claude-haiku-4.5` | 1 | 5 | 2 | 8 |

## FATAL findings (9)

### `PER-CR-004` — civil_rights_attorney @ Section 2: The Frame as Method

**Paper claim:**

> The 230 control objectives do not talk about controls this way. They specify what the institution must do... without naming whose interest each requirement structurally protects...

**Concern:** The paper critiques the FS AI RMF for failing to name protected interests, yet ignores the framework’s actual structural distribution: only 7 of 230 Control Objectives (3.0%) are tagged 'Fair,' while 179 (77.8%) are 'Accountable & Transparent.' By treating all 'empty chairs' as equivalent architectural constraints, the paper implicitly legitimizes a Treasury-endorsed framework that structurally marginalizes anti-discrimination mandates. This creates a severe parallel-regime risk where 'accountability' and 'transparency' controls are cited as compliance, while the statutory floor for prohibited-basis discrimination remains functionally unaddressed.

**Suggested fix:** Acknowledge the FS AI RMF’s 3.0% 'Fair' control distribution and explicitly designate those controls as non-waivable statutory baselines under ECOA and FHA. Require that any implementation prioritize prohibited-basis discrimination over general transparency metrics, and warn that over-indexing on 'Accountable & Transparent' controls cannot satisfy fair-lending obligations.

### `PER-CO-001` — compliance_officer @ Section 4: Diagnostic Techniques, Technique 1: Empty-chair enumeration as design pre-condition

**Paper claim:**

> The architect designing an AI governance system for a community bank's lending operation asks first: whose interest is this system structurally protecting?

**Concern:** This claim assumes I have the luxury of starting from a blank sheet. In reality, my AI systems are vendor-built (loan origination, fraud detection, deposit pricing). I cannot enumerate empty chairs for a model I did not design, whose training data I never saw, and whose internal logic is a black box. The paper does not engage with the fact that community banks are buyers, not builders. Asking me to enumerate empty chairs is like asking me to redesign the engine of a car I leased.

**Suggested fix:** Add a subsection titled 'Vendor-Mediated AI: Empty-Chair Enumeration for Buyers' that provides a concrete protocol: (1) a template RFP clause requiring the vendor to enumerate the empty chairs their system affects, (2) a due-diligence checklist for reviewing the vendor's enumeration, and (3) a fallback enumeration I can use when the vendor refuses or provides boilerplate.

### `PER-EX-001` — examiner @ Section 1: Opening Movement

**Paper claim:**

> community banks under the threshold for primary applicability still face the question of what commensurate compliance means

**Concern:** The phrase 'threshold for primary applicability' belongs to SR 26-2 / OCC Bulletin 2026-13 (joint supervisory guidance on model risk management), which applies a $30 billion asset threshold. The FS AI RMF has no such threshold; it is explicitly 'designed for all financial institutions, regardless of size, type, complexity, or criticality.' Conflating the two instruments misstates the framework's scope and could lead community banks to believe they are exempt from a framework that in fact has no size-based exclusion.

**Suggested fix:** Remove the reference to a threshold. If discussing SR 26-2, clearly distinguish it from the FS AI RMF and note that the FS AI RMF applies to all institutions without a size threshold.

### `PER-EX-002` — examiner @ Section 1: Opening Movement

**Paper claim:**

> Examiners reviewing AI deployments at community banks face a problem the regulation does not solve for them: 230 control objectives without an interpretive frame collapse into compliance theater

**Concern:** The FS AI RMF is a voluntary industry framework, not a regulation. Calling it a 'regulation' misrepresents its legal status. An examiner would not treat it as a binding rule; they examine against applicable statutes, regulations, and supervisory guidance. This conflation could mislead readers into believing the framework carries mandatory compliance weight, distorting the supervisory conversation.

**Suggested fix:** Replace 'the regulation' with 'the voluntary framework' or 'the FS AI RMF.' Clarify that the framework is not a regulation and that examiners do not enforce it directly, though they may consider its adoption as a risk-management practice.

### `PER-FS-001` — frame_skeptic @ Diagnostic Techniques

**Paper claim:**

> We name the mode silence-manufacture and develop it in this section as the organizing concept beneath the empty-chair frame. The three diagnostic techniques that follow are silence-breaking instruments against silence-manufactured artifacts.

**Concern:** The paper defines silence-manufacture as one structural pattern (suppress access to ground truth, then produce a substitute artifact read as evidence) and maps it onto three instances: post-hoc explanation at the model-output level, human oversight at the accountability level, and governance documentation at the institutional level. These instances operate through distinct mechanisms—epistemic binding failure between explanation and internals, visibility constraints on reviewers, and retroactive narrative substitution in records—without a demonstrated isomorphism that would make them tokens of a single type. The unification therefore risks being rhetorical yoking of analogous-but-distinct suppression modes rather than identification of one pattern.

**Suggested fix:** The clarification could land in the subsection 'Mapping the three earned positions onto silence-manufacture' by specifying the precise structural mapping (e.g., a shared formal property or transformation rule) that renders the three instances identical rather than merely similar in effect.

### `PER-FS-002` — frame_skeptic @ The Frame as Method; Verification Regimes as Taxonomic Move

**Paper claim:**

> The empty chairs in BSA/AML monitoring... The empty-chair reading of the situation... A turn: pricing as produced-absence canonical case... The lending example demonstrates the categoricals at the regulatory location where the dishonest middle is most directly addressable.

**Concern:** The paper traces silence-manufacture across BSA/AML (appeal-cost suppression of false-positive customers and marginalized populations), adverse-action notices (post-hoc explanation failing to bind to model reasoning), and risk-based pricing (absence of negotiation channels read as acceptance). These are treated as instances of the same mechanism, yet one is an economic barrier to voice, one an epistemic gap between artifact and computation, and one a procedural omission of a channel altogether. Without an argument that these are transformations of a single operation rather than family-resemblance cases of suppressed challenge, the claim that silence-manufacture is one pattern does not survive translation into precise language.

**Suggested fix:** A defense could be added in 'Silence-manufacture as the underlying structural pattern' that abstracts the common operation at a level that renders the economic, epistemic, and procedural cases identical (for example, by formalizing 'substitute inference from suppressed counter-evidence' as a single rewrite rule).

### `PER-SE-003` — self_examiner @ Opening Movement (final paragraph)

**Paper claim:**

> "The paper invites this examination by the very fact of proposing the diagnostic."

**Concern:** The manuscript never names or reflects on its own verification regime—the fact that it is a position paper posted on arXiv, subject to informal community review, and not a peer‑reviewed journal article. By treating the diagnostic as universally applicable while exempting its own genre from scrutiny, the paper creates a load‑bearing silence: the very mechanism that would validate its claims is left invisible, undermining the credibility of the entire argument.

**Suggested fix:** Insert a short meta‑section that describes the paper’s venue, its informal peer‑review process, and the limitations this imposes on the strength of its claims, thereby applying the empty‑chair frame to its own publication context.

### `PER-SR-001` — sympathetic_regulator @ Section 4, opening paragraph

**Paper claim:**

> We name the mode silence-manufacture and develop it in this section as the organizing concept beneath the empty-chair frame. The three diagnostic techniques that follow are silence-breaking instruments against silence-manufactured artifacts.

**Concern:** Silence-manufacture is the paper's load-bearing unifier—the concept that makes three separate critiques 'cohere into a structural argument rather than a list of related concerns.' But the paper provides no institutional-level measurable indicator for it. The empirical signatures cited (chain-of-thought perturbation, sycophancy under RLHF) are model-level observations from ML research, not examination-detectable patterns in a deployed governance architecture. An examiner arriving at a community bank cannot run a perturbation test on the institution's compliance posture. The paper explicitly defers examination methodology to 'Paper 3,' which means the unifying concept enters the revision cycle with no supervisory detection procedure. A framework revision cannot encode a concept it cannot examine for.

**Suggested fix:** Provide at least one examination-detectable indicator of silence-manufacture at the institutional level—for example, a protocol where the examiner compares the rate of contested-versus-uncontested adverse actions against the institution's reported confidence in those actions, with divergence as the indicator. Alternatively, draft a minimum examiner evidence-request list that would surface silence-manufacture in a BSA/AML or lending deployment.

### `PER-VN-001` — vendor @ Opening Movement

**Paper claim:**

> post-hoc explanation is structurally inadequate for high-stakes AI decisions... post-hoc explanation methods fail specifically in adversarial contexts, where the explanation's recipient cannot assume cooperative intent from the system being explained.

**Concern:** The paper conflates post-hoc explanation methods applied to black-box models with all explanation-based verification regimes. The strongest vendor position is not that post-hoc Shapley values are faithful; it is that explanation methods, even when individually unreliable, narrow the search space for examiners and affected parties by orders of magnitude. A denied applicant who receives a Shapley-attributed adverse action notice has a bounded set of features to interrogate, not an unbounded model. The paper cites Lanham/Turpin/Bordt on faithfulness failures but does not engage the search-space-narrowing argument, which does not depend on individual explanations being faithful. The paper's categorical forecloses an entire class of verification regimes (bounded-search-space verification) without addressing it.

**Suggested fix:** Section 3 (Verification Regimes as Taxonomic Move) should distinguish between two verification claims: (1) post-hoc explanations faithfully represent model reasoning (which the paper correctly rejects), and (2) post-hoc explanations reduce the space of hypotheses an examiner must evaluate, enabling verification through bounded interrogation rather than full reasoning reconstruction. The paper should either engage the second claim or explicitly mark that it is not addressing search-space-narrowing as a verification regime.

## MAJOR findings (35)

### `PER-CR-001` — civil_rights_attorney @ Section 3: Verification Regimes as Taxonomic Move

**Paper claim:**

> The empty chair the regime addresses is the denied applicant. ... The applicant receives reasons. The applicant does not receive verifiable reasoning.

**Concern:** The paper reduces ECOA’s adverse-action requirement to an epistemic verification gap for examiners, ignoring that ECOA § 701(a) and Regulation B § 1002.9 grant applicants a private right of action with actual damages, punitive damages, and attorney fees. By framing the applicant as an abstract architectural constraint rather than a rights-holder with statutory standing, the paper creates a parallel compliance vocabulary that institutions could cite to deflect disparate-treatment or disparate-impact claims. If regulators adopt this as a supervisory benchmark, it risks functionally displacing private litigation by treating architectural attestation as a substitute for statutory liability.

**Suggested fix:** Explicitly map the 'empty chair' to ECOA’s private right of action and clarify that architectural verification does not preempt, satisfy, or shield against statutory disparate-impact or disparate-treatment claims. State that compliance with this voluntary framework cannot be invoked as a defense to ECOA liability.

### `PER-CR-002` — civil_rights_attorney @ Section 2: The Frame as Method

**Paper claim:**

> The training-distribution gap is structural absence: the model was not trained to represent these populations as separate.

**Concern:** The paper diagnoses historical bias and training-distribution gaps but entirely omits ECOA’s disparate-impact/effects test and proxy-discrimination jurisprudence. Under *Texas Dep't of Housing v. Inclusive Communities* and longstanding CFPB/DOJ guidance, algorithmic proxies for race, national origin, or age are actionable regardless of intent or architectural transparency. Treating bias as a 'structural absence' rather than a statutory violation risks manufacturing a technical governance regime that ignores the legal reality that disparate impact on prohibited bases is already unlawful.

**Suggested fix:** Integrate ECOA’s disparate-impact framework and proxy-discrimination doctrine into the 'structural absence' analysis, specifying that architectural representation must be evaluated against protected-class statistical disparity and legally recognized proxy variables. Clarify that technical transparency does not cure statutory disparate impact.

### `PER-CR-003` — civil_rights_attorney @ Section 3: Verification Regimes as Taxonomic Move

**Paper claim:**

> The architecture produces pricing decisions through models whose reasoning is not communicated to the customer... The institution reads the customer's silence as evidence that pricing is fair.

**Concern:** The paper identifies pricing opacity and 'produced silence' but never names UDAAP’s unfairness standard (substantial injury not reasonably avoidable) or FCRA’s reasonable-procedures and adverse-action requirements. By inventing a novel 'silence-manufacture' diagnostic, the paper rhetorically occupies space where UDAAP and FCRA already provide actionable hooks for plaintiffs and regulators. This risks a parallel-regime substitution where institutions claim architectural compliance with 'silence-breaking' primitives to deflect UDAAP unfairness claims, despite the framework being voluntary and lacking statutory teeth.

**Suggested fix:** Explicitly tether 'produced silence' and pricing opacity to UDAAP unfairness/abuse standards and FCRA § 613/614 requirements. State that the framework’s architectural primitives are supplementary to, not substitutes for, existing UDAAP/FCRA enforcement mechanisms.

### `PER-CO-002` — compliance_officer @ Section 5: Architectural Primitive Categories, Primitive 1: Tamper-evident temporal capture

**Paper claim:**

> Tamper-evident temporal capture is valuable because designing-for-pages-missing requires the ability to attest both presence and absence of records, and because the silence-manufacture pattern at the institutional level is sustained by retroactive narrative substitution that contemporaneous capture forecloses.

**Concern:** The paper treats tamper-evident capture as a design-time discipline, but my systems are already built. Retrofitting tamper-evident capture onto a vendor system I do not control is operationally impossible. The paper does not acknowledge that community banks lack the technical staff to implement cryptographic anchoring or append-only event-sourced storage. It also does not address the cost: a $50k annual SaaS fee for a system that already exists is a non-starter at an $800M bank.

**Suggested fix:** Add a subsection titled 'Retrofit Pathways for Community Banks' that (1) identifies which of the four primitives can be retrofitted via vendor APIs or third-party attestation services, (2) provides a cost-estimate range for each pathway, and (3) flags which primitives are effectively unavailable to banks below $1B in assets.

### `PER-CO-003` — compliance_officer @ Section 3: Verification Regimes as Taxonomic Move, The taxonomic move

**Paper claim:**

> The categoricals divide AI applications in lending into two categories, and the empty-chair frame makes the division visible. Applications where verification is structurally available ... Applications where verification is not structurally available ... The line between them is structural: it is determined by where the reasoning lives, not by how risky the decision is.

**Concern:** The paper's categorical line is drawn at the architectural level, but examiners do not examine architecture—they examine documentation. If I tell my examiner 'this vendor model is in the structurally unavailable category,' they will ask for a model risk management policy that addresses the gap. The paper does not provide a template policy or a safe-harbor language I can use. Without that, the categoricals are a critique without substitution: I am left explaining to the examiner why the framework is flawed, not how I am complying with it.

**Suggested fix:** Add an appendix titled 'Examiner-Facing Artifacts' that provides (1) a model risk management policy addendum for vendor models in the 'structurally unavailable' category, (2) a sample examiner briefing slide deck that maps the categoricals to SR 26-2 and FS AI RMF, and (3) a one-page FAQ for examiners that anticipates pushback.

### `PER-CO-004` — compliance_officer @ Section 4: Diagnostic Techniques, Technique 3: The produced-silence question pair as design constraint

**Paper claim:**

> The produced-silence question pair, applied at design time, has the same structure as at examination time but different effect. At design time, it constrains what the architecture will do. At examination time, it diagnoses what the architecture has already done.

**Concern:** The paper assumes I can apply the question pair at design time, but most of my AI systems are already in production. Applying the question pair retroactively to a live system is not a design constraint—it is an examination finding. The paper does not tell me what to do when the answer to 'what is this design doing that creates silence?' is 'everything.' Without a remediation playbook, the question pair is just another way to document non-compliance.

**Suggested fix:** Add a subsection titled 'Retroactive Silence-Breaking' that provides (1) a decision tree for prioritizing which silences to break first (e.g., high-risk decisions, decisions affecting vulnerable populations), (2) a template vendor escalation letter demanding architectural changes, and (3) a fallback plan for when the vendor refuses (e.g., compensating controls, examiner disclosure).

### `PER-CO-008` — compliance_officer @ Section 4: Diagnostic Techniques, Examination as consequence

**Paper claim:**

> The frame's claim is that AI governance systems for community banking should be architected to be diagnosable, and the diagnostic techniques developed here should shape the architecture rather than only its evaluation.

**Concern:** The paper's architectural focus ignores the reality that community banks are not architects—they are framework consumers. The FS AI RMF is already a 230-CO checklist. If the diagnostic techniques do not map cleanly to the COs, they will be ignored. The paper needs to show how the techniques reduce burden, not just add interpretive leverage.

**Suggested fix:** Add a subsection titled 'Burden Reduction' that identifies (1) which COs can be satisfied by applying the diagnostic techniques, (2) which COs become redundant if the techniques are applied, and (3) which COs still require additional work. Include a net burden calculation (e.g., 'applying the techniques satisfies 47 COs and reduces the remaining 183 by 30%').

### `PER-EX-003` — examiner @ Section 2: The Frame as Method (The empty chairs in BSA/AML monitoring)

**Paper claim:**

> They specify what the institution must do (record-keeping, suspicious-activity reporting, customer due diligence, transaction monitoring thresholds) without naming whose interest each requirement structurally protects

**Concern:** The control objectives in the FS AI RMF are voluntary; they do not impose mandatory 'must do' requirements. Using prescriptive language blurs the line between a voluntary framework and binding regulatory obligations. An examiner would distinguish between what a regulation requires and what a framework recommends. This phrasing could cause institutions to misinterpret the framework as a compliance mandate.

**Suggested fix:** Replace 'must do' with 'recommend that institutions do' or 'describe practices such as.' Emphasize that the framework is voluntary and that specific regulatory requirements (e.g., BSA/AML obligations) come from statutes and regulations, not from the FS AI RMF itself.

### `PER-EX-004` — examiner @ Section 1: Opening Movement

**Paper claim:**

> The frame gives examiners diagnostic leverage the checklist does not.

**Concern:** This assumes examiners are using the FS AI RMF as a compliance checklist. In practice, examiners do not examine against voluntary industry frameworks; they apply supervisory guidance (e.g., SR 26-2, OCC bulletins) and regulations. The claim overstates how examiners would use the FS AI RMF and implies a supervisory practice that does not exist. An examiner would not treat the framework's control objectives as a checklist to be checked off.

**Suggested fix:** Reframe the claim to acknowledge that the FS AI RMF is a voluntary resource. If arguing that the empty-chair frame could inform examiner judgment, state that it offers a conceptual lens for evaluating an institution's AI risk management, not a replacement for regulatory examination standards.

### `PER-EX-005` — examiner @ Section 6: Honest Uncertainties (Uncertainties about the categoricals)

**Paper claim:**

> The prediction is consistent with the trajectory of the FS AI RMF and with the April 2026 revised model-risk guidance, but it remains a prediction

**Concern:** The April 2026 revised model-risk guidance (SR 26-2 / OCC Bulletin 2026-13) explicitly excludes generative AI and agentic AI from its scope. The paper's categoricals about post-hoc explanation and human oversight are centrally concerned with generative AI outputs (e.g., chain-of-thought explanations). Claiming consistency with SR 26-2 is misleading because the guidance does not address the AI applications the paper critiques. This mischaracterizes the regulatory direction.

**Suggested fix:** Acknowledge that SR 26-2 excludes generative AI and agentic AI, and therefore does not directly support the paper's predictions about verification regimes for those systems. If citing SR 26-2, clarify its limited scope and distinguish it from the FS AI RMF, which does address AI broadly.

### `PER-FS-003` — frame_skeptic @ Diagnostic Techniques

**Paper claim:**

> Silence-manufacture is the dual of Goodhart's law goodhart1984problems, not strictly its inverse. The relationship is rhetorically useful for orienting readers (Goodhart provides a known landmark) but the load-bearing name is silence-manufacture, not extended-Goodhart.

**Concern:** The paper explicitly characterizes the duality as rhetorical rather than formal: Goodhart corrupts visible metrics under optimization pressure; silence-manufacture sustains visible artifacts by suppressing disconfirming evidence. No structural mapping (e.g., a categorical duality, an optimization dual, or a precise inversion of quantifiers) is supplied that would allow the claim to generate new theorems or predictions beyond the already-stated suppression-substitution description. The 'dual' therefore functions as memorable framing that orients readers toward an existing landmark without adding load-bearing analytical content.

**Suggested fix:** The paper could either drop the dual language or supply the missing formal relationship in the same subsection, for instance by showing how silence-manufacture can be expressed as a dual problem in a shared formal language (e.g., missing-data mechanisms or observability constraints).

### `PER-FS-004` — frame_skeptic @ Opening Movement

**Paper claim:**

> the blueprint has a normative structure, and that structure is empty-chair representation: the design of AI governance such that specific absent parties are structurally represented in the architecture of decision-making, not merely in its documentation.

**Concern:** The FS AI RMF is defined by four orthogonal axes (NIST functions with GV at 35.2 %, 19 categories, 7 trustworthy principles of which Accountable & Transparent covers 77.8 % of control objectives, and 4 adoption stages). The paper asserts that nearly every control objective protects an absent party's interest, yet this reading is not derived from the axes; it is an external overlay. The framework's own risk vocabulary names gaps, lacks, and insufficiencies without reference to empty chairs or verification regimes that bind to underlying reasoning; the metaphor therefore organizes pre-existing observations rather than producing a finding internal to the document's structure.

**Suggested fix:** The claim could be grounded by showing how the empty-chair reading is entailed by one or more of the framework's published axes (for example, by demonstrating that the heavy skew toward Accountable & Transparent is itself an architectural commitment to absent-party audibility).

### `PER-FS-006` — frame_skeptic @ Opening Movement

**Paper claim:**

> Controls that protect those interests have substance; controls that do not are decoration. ... A control represents an absent party only if it induces observable, auditable constraints on system behavior or evidence production that a later examiner could use to assess whether that party's interests were respected.

**Concern:** The paper's judgments that a control is 'decoration' or that an implementation produces 'silence' rest on an external verification standard: the requirement that controls bind to underlying reasoning or ground truth via contemporaneous, traversable evidence. The FS AI RMF's own 230 control objectives and risk names emphasize documentation, policies, and processes (especially under the dominant Accountable & Transparent principle) without articulating this binding requirement. The normativity is therefore not immanent to the framework but imported; the paper does not show that the framework's standards themselves classify non-binding implementations as failures.

**Suggested fix:** The paper could either derive the binding requirement from the framework's published categories and sub-categories or explicitly mark the verification regime as an external normative commitment brought to the framework rather than read out of it.

### `PER-SE-001` — self_examiner @ Opening Movement

**Paper claim:**

> "In others, the examiner applying updated model‑risk guidance that had not yet been issued when the system was deployed."

**Concern:** The paper repeatedly foregrounds the “examiner” as an absent‑party proxy, yet it never seats the very examiners who would be applying the FS AI RMF in practice – community‑bank examiners, OCC/OFR supervisors, and the Treasury’s own oversight staff. By omitting their perspectives, the analysis silently assumes a monolithic examiner stance and masks the diversity of constraints (resource limits, policy priorities, risk‑based focus) that shape how the framework is interpreted. This is an empty‑chair omission that the paper’s own diagnostic would flag as a structural silence.

**Suggested fix:** Add a brief subsection that interviews or surveys actual examiners (e.g., community‑bank examiners, OCC staff) and reflects on how their practical concerns align or clash with the empty‑chair frame, acknowledging the limits of the current analysis.

### `PER-SE-002` — self_examiner @ Diagnostic Techniques – Definition

**Paper claim:**

> "We define silence‑manufacture as the structural pattern in which an architecture suppresses access to ground truth in some domain, then produces a substitute artifact (a metric, a document, a signature, an explanation) that occupies the rhetorical position where evidence of ground truth should appear."

**Concern:** The paper introduces “silence‑manufacture” as a theoretical construct but provides no empirical grounding—no case studies, data, or systematic survey of FS AI RMF implementations that demonstrate the pattern. The definition itself becomes a rhetorical artifact that stands in for the missing evidence the diagnostic is meant to uncover, reproducing the very silence it condemns.

**Suggested fix:** Include a concise empirical illustration (e.g., a documented instance where a bank’s post‑hoc explanation was used as the sole audit artifact) to show the pattern in action, or explicitly acknowledge the lack of systematic evidence and frame the definition as a hypothesis.

### `PER-SE-004` — self_examiner @ Verification Regimes as Taxonomic Move

**Paper claim:**

> "The categoricals divide AI applications in regulated decision contexts into two structurally different categories, distinguished not by risk magnitude but by whether a verification regime is available for the application's outputs."

**Concern:** This binary taxonomic move forecloses a spectrum of hybrid verification regimes (e.g., semi‑automated human‑in‑the‑loop with real‑time evidence capture) and ignores ongoing industry experiments that blend structural and post‑hoc methods. By presenting the dichotomy as exhaustive, the paper manufactures a silence around alternative designs that could mitigate the identified failures.

**Suggested fix:** Add a paragraph acknowledging the existence of hybrid or emerging verification approaches and explain why the binary taxonomy is a simplifying abstraction rather than a claim of completeness.

### `PER-SR-002` — sympathetic_regulator @ Section 3, subsection 'What the categoricals foreclose, and what they do not'

**Paper claim:**

> The categoricals foreclose architectures that rely on post-hoc explanation as a verification regime in adversarial contexts. They do not foreclose AI in lending. They foreclose specific architectural patterns: Underwriting models whose decisions are communicated via adverse action notices generated by post-hoc explanation methods, with human signatures attesting to review of the notice rather than verification of the reasoning.

**Concern:** The paper forecloses a specific architectural pattern but does not draft the Control Objective that would enact the foreclosure in the framework. A regulator reading this section knows what to prohibit but not how to write the prohibition in CO language. The FS AI RMF's 230 COs are structured as risk-name-plus-objective pairs (e.g., 'Insufficient Compliance Validation' → objective text). Without a draft CO—specifying the NIST Function, Category, the risk name, and the objective language—this categorical remains a position paper claim rather than a revision input.

**Suggested fix:** Draft at least one CO-style entry for the foreclosure. Example under MS-2 (Evaluating AI Systems): Risk name 'Post-Hoc Explanation as Sole Verification Regime'; objective: 'Where AI-generated decisions are subject to adversarial regulatory review, the institution shall not rely solely on post-hoc explanation methods (including feature attribution, counterfactual generation, or natural-language summarization) as the verification regime for the reasoning underlying the decision.' This gives the revision cycle language to work with.

### `PER-SR-003` — sympathetic_regulator @ Section 7, Conclusion

**Paper claim:**

> The architectural primitives that empty-chair representation requires (tamper-evident temporal capture, evidence binding, three-dimensional confidence characterization, structural drift typology, diagnostic techniques applied to the attested record) are sketched in this paper at the property level and left to follow-on work for implementation specification.

**Concern:** The four primitives are argued at the property level but are not mapped to the framework's axis structure. A revision requires knowing: which NIST Function does each primitive belong to? Which Category? Does each primitive require a new Sub-Category, or does it modify an existing CO? The framework currently distributes its 230 COs across Govern (81), Map (47), Measure (59), and Manage (43). Without axis placement, the primitives float free of the structure the revision must work within. The paper's own Section 4.5 says 'a primitive is valuable in proportion to its support of design-time diagnostic discipline against silence-manufacture'—this is a justification, not a placement.

**Suggested fix:** Provide a mapping table: each primitive → proposed NIST Function → proposed Category → whether new Sub-Category or modification of existing CO. For example, tamper-evident temporal capture likely maps to GV-1 or MS-2; evidence binding to MP-4 or MS-3; three-dimensional confidence characterization to MS-1; structural drift typology to MS-3 or MG-4. Even a draft mapping with acknowledged uncertainty gives the revision cycle a concrete proposal to evaluate.

### `PER-SR-004` — sympathetic_regulator @ Section 2, subsection 'Two kinds of absence'

**Paper claim:**

> The diagnostic move on produced absence is what is the architecture doing that creates this silence, and what is it inferring from the silence it created? … The distinction matters because produced absence is invisible to the empty-chair frame as initially stated. Make the absent party audible is the wrong operation when the architecture is producing the silence.

**Concern:** The structural/produced distinction is load-bearing—it determines whether the diagnostic move is 'make audible' or 'identify the suppression mechanism.' But the paper provides no operational test for distinguishing the two in examination practice. An examiner encountering a silence (e.g., low appeal rate on false-positive AML flags) cannot determine from the silence alone whether it is structural (customers chose not to appeal) or produced (appeal was prohibitively expensive). The paper acknowledges 'hybrid cases' but offers no decision procedure. Two examiners applying the frame to the same silence could classify it differently, with no reconciliation mechanism. For a framework revision, a distinction without a test is a distinction that produces inconsistent examination findings.

**Suggested fix:** Provide a minimum decision procedure or heuristic for the structural/produced classification. One candidate: a silence is classified as produced if the architecture imposes costs on challenge that the affected party did not consent to and cannot negotiate. This shifts the question from 'why is the party silent?' (inaccessible) to 'does the architecture impose challenge costs the party cannot negotiate?' (inspectable). Draft this as an examiner decision rule with at least one worked example.

### `PER-SR-005` — sympathetic_regulator @ Section 6, subsection 'Uncertainties about the frame'

**Paper claim:**

> Two examiners using the frame on the same institution may disagree about which chairs the institution is failing to represent.

**Concern:** The paper honestly names this uncertainty but does not resolve it, and for regulatory purposes the openness is a coordination problem. If the frame enters examination practice without a minimum enumeration, examiners at different agencies will develop different chair-lists, producing inconsistent supervisory expectations. The FS AI RMF's current structure avoids this problem by specifying 230 COs that are the same for every examiner. The empty-chair frame replaces that uniformity with an interpretive discipline that, without a floor, produces the very inconsistency the framework was designed to prevent.

**Suggested fix:** Provide a minimum mandatory enumeration of empty chairs for each major regulatory context (lending, BSA/AML, pricing), with the explicit statement that the enumeration is a floor, not a ceiling. The BSA/AML section's six chairs could serve as the minimum for that context. This preserves the frame's openness while giving examiners a common starting point that prevents the most damaging inconsistencies.

### `PER-SR-007` — sympathetic_regulator @ Section 4, subsection 'Examination as consequence'

**Paper claim:**

> The implication: the techniques' regulatory effect depends on adoption at the architectural level, not just at the examination level. An examiner who applies the techniques to a system designed without them produces findings of inadequacy, but the inadequacy is structural: it cannot be remediated by additional examination, only by re-architecture.

**Concern:** This passage acknowledges that the techniques require architectural adoption to produce regulatory effect, but does not analyze the coordination problem across the bodies that would need to align: Treasury (framework owner), FBIIC and AIEOG (developers), CRI (host), and downstream supervisory agencies (Fed, OCC, FDIC) that conduct examinations. If the FS AI RMF revision incorporates empty-chair language but supervisory agencies do not update examination procedures to ask the diagnostic questions, institutions have no incentive to architect for them. The paper's prescriptions exceed any single agency's authority: requiring contemporaneous capture rather than post-hoc documentation, requiring evidence binding rather than logging, requiring three-dimensional confidence rather than single-score reporting. Each of these touches supervisory guidance, examination manuals, and potentially call-report data elements. The paper does not identify which coordination points are necessary or which prescriptions fall within a single agency's authority.

**Suggested fix:** Add a coordination analysis: which prescriptions require only FS AI RMF revision (Treasury/FBIIC/AIEOG/CRI authority), which require updated supervisory guidance (Fed/OCC/FDIC authority), and which require both? At minimum, identify which of the four primitives could be encoded as voluntary framework COs (single-body action) versus which would require supervisory guidance changes (multi-body coordination). This lets the revision cycle sequence the work: framework language first where possible, inter-agency coordination where necessary.

### `PER-TR-001` — technical_reviewer @ Opening Movement, Position 1 paragraph

**Paper claim:**

> post-hoc explanation methods can be manipulated slack2020, that chain-of-thought reasoning often does not reflect the model's actual reasoning lanham2023,turpin2023

**Concern:** The paper cites Lanham et al. and Turpin et al. for the claim that chain-of-thought reasoning 'often does not reflect the model's actual reasoning.' Both papers do show that CoT traces can be perturbed without changing outputs and vice versa. However, the paper then uses this finding to argue that post-hoc explanation is 'structurally inadequate' for verification in adversarial contexts (Position 2). The leap from 'CoT is not faithful to computation' to 'all post-hoc explanation methods are structurally inadequate' is not supported by the cited work. Lanham and Turpin study LLM-specific CoT faithfulness; they do not establish claims about LIME, Shapley values, or attention-based explanations for non-LLM systems. The paper conflates a specific finding about one explanation method on one model class with a universal structural claim.

**Suggested fix:** Narrow the claim to: 'Chain-of-thought reasoning in LLMs often does not reflect the model's actual reasoning (Lanham 2023, Turpin 2023), and similar faithfulness gaps have been documented in other post-hoc explanation methods (cite specific methods and papers).' Then distinguish which explanation methods the structural inadequacy claim applies to, or acknowledge that the universality of the claim exceeds the cited evidence.

### `PER-TR-002` — technical_reviewer @ Opening Movement, Position 1 paragraph

**Paper claim:**

> bordt2022 sharpen the claim with a contextual distinction directly relevant here: post-hoc explanation methods fail specifically in adversarial contexts, where the explanation's recipient cannot assume cooperative intent from the system being explained.

**Concern:** The paper attributes to Bordt et al. (2022) a claim about post-hoc explanation failure 'specifically in adversarial contexts.' Bordt et al. do discuss post-hoc explanation reliability and adversarial settings, but the paper does not quote or precisely specify what Bordt et al. actually argue about the adversarial-context distinction. The paper then applies this to bank examination as 'structurally adversarial,' but Bordt et al.'s work does not establish that bank examination is the kind of adversarial context they analyze. The paper is using Bordt et al. to support a regulatory claim (about examination dynamics) that the cited work does not address. This is citation overreach.

**Suggested fix:** Quote the specific passage from Bordt et al. that supports the adversarial-context claim. Then separately argue (with or without citation) why bank examination should be characterized as adversarial in the sense Bordt et al. mean. Or acknowledge that Bordt et al. do not directly address regulatory examination contexts and that the application is an inference the paper is making, not a claim the cited work establishes.

### `PER-TR-003` — technical_reviewer @ Opening Movement, framework description (implicit in reference block)

**Paper claim:**

> The framework specifies 230 Control Objectives, organized along four orthogonal axes... Axis 3 — AI Trustworthy Principles (cross-cutting tag, 7 values; with structural distribution): Accountable & Transparent: 179 COs (77.8%)

**Concern:** The paper uses the 78%/22% skew (179 of 230 COs tagged 'Accountable & Transparent' vs. 51 tagged with other principles) as evidence that the framework is 'nominally pluralist' but structurally dominated by one principle. However, the paper does not establish the null model against which this skew is surprising. If the framework's authors intentionally weighted Accountable & Transparent more heavily because it is foundational to financial regulation, the skew is not evidence of imbalance—it is evidence of intentional design. The paper treats the numerical distribution as diagnostic of a problem without establishing what distribution would be expected or justified. This is a statistical inference without a defensible baseline.

**Suggested fix:** Either: (a) establish a principled null model (e.g., 'if the seven principles were equally important, we would expect ~33 COs per principle') and then argue why that null is the right one, or (b) acknowledge that the distribution reflects the framework authors' intentional weighting and argue separately (on regulatory or policy grounds) that the weighting is misaligned with what the framework should protect, rather than treating the distribution as evidence of hidden imbalance.

### `PER-TR-004` — technical_reviewer @ Section 2: The Frame as Method, opening

**Paper claim:**

> The empty-chair frame's value depends on its generativity... This section demonstrates the latter through a worked example in BSA/AML transaction monitoring... The frame applied to lending tends to confirm what readers already believe, which is a poor test of whether the frame is doing work or merely renaming work that was already being done.

**Concern:** The paper argues that BSA/AML is a harder test of the frame than lending because 'the empty chairs are plural and conflicting.' However, the paper then applies the frame to BSA/AML and produces six enumerated chairs (next victim, false-positive customer, marginalized customer, institution's future self, financial system, criminal). The enumeration is presented as if it is the frame's output, but the paper does not establish that this enumeration is what the frame *generates* versus what the paper's author *chose to enumerate*. The paper does not show the frame being applied by a second analyst to the same domain and producing a different enumeration, which would demonstrate whether the frame is generative or whether it is a vocabulary that different users fill with their own prior commitments. The claim that the frame 'produces clarity' in BSA/AML is not falsifiable from the evidence presented.

**Suggested fix:** Either: (a) apply the frame to the same BSA/AML domain with a second analyst and show that the frame produces convergent or productively divergent enumerations, or (b) acknowledge that the paper demonstrates the frame can be applied to BSA/AML and produces a coherent analysis, but does not demonstrate that the frame is generative (produces outputs that differ from the analyst's prior commitments) versus merely a vocabulary for organizing prior commitments.

### `PER-TR-005` — technical_reviewer @ Section 3: Verification Regimes as Taxonomic Move, 'The taxonomic move' subsection

**Paper claim:**

> The categoricals divide AI applications in lending into two categories... Applications where verification is structurally available... Applications where verification is not structurally available. Decision generation by an underwriting model whose output is communicated to the applicant via an adverse action notice extracted by a post-hoc explanation method.

**Concern:** The paper claims that post-hoc explanation methods (Shapley values, LIME) produce explanations that 'do not bind to the underlying reasoning of the model' and therefore cannot serve as a verification regime. However, the paper does not distinguish between: (a) explanations that are unfaithful to the model's computation (the Lanham/Turpin finding about CoT), and (b) explanations that are faithful to the model's computation but do not capture the model's *reasoning* in a philosophical sense. A Shapley value is a mathematically well-defined attribution; it is not faithful to the model's internal computation in the sense Lanham/Turpin show, but it is a faithful answer to the question 'which features contributed most to this output.' The paper conflates these two senses of faithfulness and uses the conflation to argue that explanation methods cannot work, when the actual claim is narrower: certain explanation methods do not capture what the model 'actually did' at the computational level. This is a real problem but not the same as saying explanation cannot work for verification.

**Suggested fix:** Distinguish between computational faithfulness (does the explanation trace the model's actual computation) and feature-importance faithfulness (does the explanation correctly identify which features mattered for the output). Acknowledge that Shapley values and LIME may be faithful in the second sense while unfaithful in the first. Then argue specifically why computational faithfulness is required for the verification regime the adverse action notice is meant to provide, rather than treating feature-importance explanations as automatically inadequate.

### `PER-TR-007` — technical_reviewer @ Section 4: Diagnostic Techniques, 'Silence-manufacture as the underlying structural pattern' subsection

**Paper claim:**

> Silence-manufacture is the dual of Goodhart's law goodhart1984problems, not strictly its inverse... Goodhart's law describes optimization pressure on a metric corrupting the metric... Silence-manufacture describes suppression pressure on disconfirming evidence sustaining the metric's apparent validity.

**Concern:** The paper claims that silence-manufacture is a 'dual' of Goodhart's law and distinguishes them by saying Goodhart is about metric corruption while silence-manufacture is about suppression of disconfirming evidence. However, Goodhart's law is often understood to include exactly the suppression mechanism the paper describes: when a measure becomes a target, people optimize for the measure rather than the underlying construct, which means they suppress or ignore evidence that contradicts the measure's validity. The paper's distinction between 'metric corruption' and 'suppression of disconfirming evidence' is not as sharp as it claims. Moreover, the paper does not cite any work that uses the term 'silence-manufacture' prior to this paper, so the claim that it is a known pattern with a known name is unsupported. The paper appears to be introducing a new term and then claiming it is the 'dual' of an existing concept, which is confusing and potentially misleading.

**Suggested fix:** Either: (a) acknowledge that silence-manufacture is a new term the paper is introducing, and explain how it relates to Goodhart's law without claiming it is a 'dual,' or (b) cite prior work that uses the term 'silence-manufacture' or a closely related concept, and establish the distinction more carefully. The current framing suggests the term has prior standing when it does not.

### `PER-TR-008` — technical_reviewer @ Section 4: Diagnostic Techniques, 'What silence-manufacture predicts' subsection

**Paper claim:**

> The three predictions are not independent claims; they are three consequences of one structural pattern, applied to three sites: regulatory reform, analytical inquiry, and political discourse... The de-banking discourse exemplifies this prediction: political-debanking framing fills a silence the BSA/AML regime legally produces under 31 USC 5318(g)(2).

**Concern:** The paper claims that the de-banking discourse is an example of silence-manufacture producing mis-attributing public discourse, and cites 31 USC 5318(g)(2) as the legal provision that 'produces' the silence. However, 31 USC 5318(g)(2) is the safe harbor provision that protects banks from liability for account closures made in good faith to comply with BSA/AML. The paper does not explain how this provision 'legally produces' silence about the causes of account closures. The paper then cites anthony2026 as reporting that 'political or religious motivations' account for only 35 of 8,361 complaints, but does not establish that the absence of political motivation in the data is evidence of silence-manufacture rather than evidence that political debanking is not the primary driver. The paper is using the de-banking case to support a prediction about silence-manufacture, but the causal chain from the legal provision to the silence to the mis-attribution is not clearly established.

**Suggested fix:** Explain precisely how 31 USC 5318(g)(2) produces silence about account-closure causes (e.g., does it prevent disclosure, create liability for disclosure, or something else?). Then establish that the absence of political-motivation complaints in the anthony2026 data is evidence of suppression rather than evidence that political debanking is rare. Or acknowledge that the de-banking case is suggestive but not conclusive evidence for the silence-manufacture prediction, and that the causal chain requires more detailed analysis than the paper provides.

### `PER-TR-009` — technical_reviewer @ Section 5: Architectural Primitive Categories, 'What the four primitives compound to' subsection

**Paper claim:**

> The primitives are not exhaustive. Section [ref] names tamper-evident temporal capture, evidence binding, three-dimensional confidence characterization, and structural drift typology as the primitives the diagnostic techniques require. We have argued that these four are necessary; we have not argued that they are sufficient.

**Concern:** The paper claims the four primitives are necessary but not sufficient, and acknowledges that 'implementation work in Paper 2 will reveal whether additional primitives are required.' This is an honest uncertainty, but it undermines the paper's structural claim that the four primitives are what 'empty-chair representation requires.' If the paper does not know whether the four are sufficient, then the paper has not established what empty-chair representation requires. The paper is presenting a partial list as if it is a complete structural specification. This is not fatal to the paper's argument (position papers can propose partial solutions), but it should be marked more clearly in the main text rather than relegated to the uncertainties section.

**Suggested fix:** In Section 5's introduction, state explicitly: 'The four primitives below are the categories the diagnostic techniques require; implementation work will likely reveal additional primitives necessary for complete empty-chair representation. This section specifies the structural minimum we can argue for from the frame's commitments alone.' This moves the uncertainty into the main argument rather than treating it as a caveat.

### `PER-TR-010` — technical_reviewer @ Section 6: Honest Uncertainties, 'The meta-uncertainty: theory of effect' subsection

**Paper claim:**

> The paper's primary intended effect is at the architectural level: shaping what gets built so that built systems are diagnosable in the ways the frame requires... If the primary effect fails — if architects do not adopt the frame and continue building systems without the diagnostic primitives — the secondary effects also degrade.

**Concern:** The paper acknowledges that its effect depends on architects adopting the frame, but the paper provides no evidence or argument for why architects would adopt it. The paper is addressed to a policy/regulatory audience (position paper on the FS AI RMF), not to architects. The paper does not specify how the frame would be communicated to architects, what incentives would motivate adoption, or how adoption would be monitored. The paper's theory of effect is incomplete: it identifies the mechanism (architects adopt the frame) but does not establish the pathway from the paper's publication to that adoption. This is a fundamental gap in the paper's practical claim.

**Suggested fix:** Either: (a) add a section on dissemination and adoption strategy (how the frame reaches architects, what regulatory or market incentives drive adoption), or (b) reframe the paper's primary effect as regulatory/examination-level rather than architectural, and acknowledge that architectural adoption is a secondary effect that depends on regulatory uptake first. The current framing claims architectural primacy without establishing the pathway to it.

### `PER-VN-002` — vendor @ Opening Movement

**Paper claim:**

> human oversight of AI recommendations is not a verification regime when the human reviews explanations rather than reasoning... The signature attests to the human's review of the explanation. The decision was made by the AI. The reasoning was never verified.

**Concern:** The paper assumes the human reviewer has no independent reasoning capacity and no ability to develop domain expertise over time. The strongest vendor position is that human reviewers, especially domain experts (loan officers, compliance analysts, fraud investigators), develop calibrated judgment through repeated exposure to cases and outcomes. A loan officer who reviews 100 AI recommendations with explanations, observes outcomes, and adjusts their mental model is not merely signing explanations; they are developing a verification regime through experiential learning. The paper treats human oversight as a static artifact (signature on explanation) rather than as a dynamic process (expert judgment calibrated through feedback). This is a weakened version of human oversight that the paper attacks.

**Suggested fix:** Section 3 should distinguish between static human oversight (signature on explanation, no feedback loop) and dynamic human oversight (expert judgment calibrated through repeated cases and outcome observation). The paper's categorical applies to the static case; the dynamic case requires engagement with the human-learning literature and with the question of whether repeated exposure to AI recommendations with explanations and outcome feedback constitutes a verification regime. If the answer is yes, the categorical is narrower than stated; if no, the paper should explain why domain expertise and feedback loops do not constitute verification.

### `PER-VN-003` — vendor @ Opening Movement

**Paper claim:**

> any architecture that relies on explanation-of-output as its verification regime in an adversarial context has built a Potemkin form of accountability... The empty chair — the party who depends on the verification regime to represent their interest — is not represented by an explanation that does not bind to the underlying reasoning.

**Concern:** The paper's definition of 'verification regime' is narrower than the strongest vendor position. The paper requires that verification bind to 'underlying reasoning'—the model's actual computational process. The strongest vendor position is that verification can bind to decision-relevant features without binding to computational process: a verification regime that establishes which features the model weighted, in what direction, and with what confidence, enables an examiner to assess whether the decision was reasonable given the features, even if the explanation does not capture the model's internal state. This is verification of decision-reasonableness, not verification of reasoning-faithfulness. The paper forecloses this category without engaging it.

**Suggested fix:** Section 3 should explicitly distinguish between verification of reasoning (does the explanation capture what the model actually computed?) and verification of decision-reasonableness (given the features the model weighted, was the decision reasonable?). The paper's categorical applies to the first; the second is a different verification regime that the paper should either engage or explicitly exclude from scope.

### `PER-VN-004` — vendor @ Opening Movement

**Paper claim:**

> The framework specifies 230 Control Objectives... nearly every control objective can be understood as protecting an interest of a party who is not in the room when an AI system makes or supports a financial decision.

**Concern:** The paper's characterization of the FS AI RMF's structure is incomplete. The reference block shows that 179 of 230 COs (77.8%) are tagged 'Accountable & Transparent,' with the other six principles (Explainable & Interpretable, Valid & Reliable, Fair, Secure & Resilient, Privacy-Enhanced, Safe) accounting for only 51 COs combined. The framework's own structure is heavily weighted toward accountability and transparency, not toward the seven-principle pluralism the paper's opening suggests. The paper's empty-chair framing is compatible with this weighting, but the paper should acknowledge that the framework itself has already made a structural choice about which principles matter most, and that choice is not neutral across the empty chairs the paper names. Some empty chairs (the institution's future self, the examiner) are well-served by accountability-and-transparency controls; others (the marginalized customer, the next victim) may require the other six principles more heavily.

**Suggested fix:** Section 1 should acknowledge the FS AI RMF's actual principle distribution and discuss whether the framework's 78%-accountability weighting aligns with the empty-chair enumeration the paper proposes. If the paper believes the weighting is misaligned, it should argue for reweighting; if aligned, it should explain why accountability-and-transparency controls serve all the empty chairs adequately.

### `PER-VN-005` — vendor @ Opening Movement

**Paper claim:**

> The dishonest middle is not merely a failure of representation. It is an active production of silence, interpreted as endorsement... A system in which AI generates a recommendation, a human reviews the explanation, and the human signs the decision satisfies an org-chart picture of accountability without satisfying the verification requirement the org-chart was meant to encode.

**Concern:** The paper does not engage the strongest vendor argument: that the org-chart picture of accountability is itself the verification regime in many regulatory contexts. Bank examination does not require that every decision be individually verifiable; it requires that the institution have a documented governance structure, that the structure be followed, and that the structure include human oversight. The paper treats this as theater; the regulatory regime treats it as adequate. The paper's position requires that the regulatory regime itself be wrong about what constitutes verification, which is a claim about regulatory authority the paper does not establish. The vendor position is that if the regulatory regime accepts org-chart accountability as sufficient, then an architecture that satisfies the org-chart is compliant, even if the paper's frame would reject it as theater.

**Suggested fix:** Section 3 should engage the question of regulatory authority: does the paper argue that the FS AI RMF should be interpreted as requiring verification-of-reasoning (the paper's position), or does it argue that the current regulatory regime is inadequate and should be changed? If the former, the paper should show where in the FS AI RMF text the requirement for reasoning-verification appears; if the latter, the paper should acknowledge that it is arguing for regulatory change, not interpretation of existing regulation.

### `PER-VN-006` — vendor @ Section 3: Verification Regimes as Taxonomic Move

**Paper claim:**

> The categoricals divide AI applications in lending into two categories... Applications where verification is not structurally available. Decision generation by an underwriting model whose output is communicated to the applicant via an adverse action notice extracted by a post-hoc explanation method.

**Concern:** The paper does not address the strongest vendor counter: that interpretable-by-design models (linear models, tree-based models, rule-based systems, attention-based models with interpretable attention) provide verification regimes that post-hoc explanation does not require. The paper cites Rudin 2019 on interpretable models but does not engage the position that interpretable-by-design models solve the verification problem the paper identifies. The categorical forecloses post-hoc explanation but does not foreclose AI in lending if the AI is built interpretably. The paper should either acknowledge this category or explain why interpretable-by-design models do not constitute a verification regime.

**Suggested fix:** Section 3 should explicitly enumerate the architectural categories that do provide verification regimes: (1) interpretable-by-design models where the model's reasoning is structurally available, (2) decision-support tools where AI surfaces material for human reasoning, (3) architectures with tensor-channel observation that bind explanations to underlying computation. The paper should then clarify whether the categorical against post-hoc explanation applies only to black-box models or more broadly.

## MINOR findings (13)

### `PER-CR-005` — civil_rights_attorney @ Section 7: Conclusion

**Paper claim:**

> The empty chairs are plural and they do not always agree. But the architectural function of regulatory governance is to give them voice in the institutional mechanism, not merely in the institutional documentation.

**Concern:** The paper repeatedly invokes 'giving voice' to absent parties but cites zero civil rights organizations, fair lending advocates, or community banking consumer groups. The only external references are academic/technical literature and a Cato policy analysis. This erases the decades of litigation, advocacy, and regulatory comment that established ECOA, UDAAP, and FHA enforcement, treating affected parties as abstract architectural variables rather than organized litigants with discovery rights and class-action standing.

**Suggested fix:** Integrate citations to NCRC, NCLC, CFPB fair lending reports, and community advocacy litigation to ground the 'empty chair' in actual affected-party advocacy. Clarify that 'voice' in civil rights law requires standing, discovery access, and class certification pathways, not just architectural attestation.

### `PER-CO-005` — compliance_officer @ Section 2: The Frame as Method, opening paragraph

**Paper claim:**

> The empty-chair frame's value depends on its generativity. If naming absent-party representation as the organizing principle behind the FS AI RMF produces only a more sympathetic vocabulary for compliance theater, the frame has earned nothing.

**Concern:** The paper's generativity claim is abstract. It does not acknowledge that community banks already use frameworks as compliance shopping lists. If the empty-chair frame is not immediately translatable into a checklist, it will be ignored. The paper needs to show how the 230 COs map to empty chairs, not just assert that the mapping exists.

**Suggested fix:** Add a table in an appendix that maps the 230 FS AI RMF Control Objectives to empty chairs (e.g., GV-1.1.1 → 'future compliance officer,' MP-2.3.4 → 'marginalized customer'). Include a column for 'evidence artifact' that lists what I should collect to demonstrate representation.

### `PER-CO-006` — compliance_officer @ Section 2: The Frame as Method, Two kinds of absence

**Paper claim:**

> The frame's diagnostic move on structural absence is how does the architecture make this party audible to the parties who are present?

**Concern:** The paper treats 'audible' as a binary: either the party is audible or they are not. In practice, audibility is a spectrum. A loan applicant might be 'audible' via an adverse action notice but 'inaudible' on pricing decisions. The paper needs to define degrees of audibility and provide a rubric for assessing them.

**Suggested fix:** Add a subsection titled 'Audibility Spectrum' that defines three levels (e.g., 'documented,' 'verifiable,' 'contestable') and provides examples of artifacts that satisfy each level. Include a column in the CO mapping table that specifies the required audibility level for each empty chair.

### `PER-CO-007` — compliance_officer @ Section 5: Architectural Primitive Categories, Primitive 2: Evidence binding

**Paper claim:**

> The honest formulation of the primitive requires that the bound evidence be the underlying reasoning the decision was based on, not a post-hoc reconstruction.

**Concern:** The paper's categorical rejection of post-hoc explanation is too absolute. In practice, some post-hoc explanations (e.g., Shapley values for linear models) are more faithful than others (e.g., LIME for deep neural networks). The paper should provide a decision tree for assessing when a post-hoc explanation is 'good enough' for community-bank risk tolerance.

**Suggested fix:** Add a subsection titled 'Post-Hoc Explanation Triage' that provides (1) a decision tree for assessing explanation faithfulness (e.g., model type, decision stakes, adversarial context), (2) a list of 'red flag' explanation methods (e.g., attention visualization for transformer models), and (3) a template vendor questionnaire for assessing explanation fidelity.

### `PER-EX-006` — examiner @ Section 3: Verification Regimes as Taxonomic Move (A turn: pricing as produced-absence canonical case)

**Paper claim:**

> Statistical validation against outcomes verifies that the model performs as intended in aggregate... (sr11_7,sr26_2)

**Concern:** The citation 'sr11_7,sr26_2' references supervisory guidance on model risk management. SR 26-2 explicitly excludes generative AI and agentic AI. Without noting this exclusion, the citation could imply that the guidance applies to the AI underwriting models discussed, when in fact it may not cover certain AI systems. This is a precision issue that an examiner would flag for accuracy.

**Suggested fix:** Add a brief note that SR 26-2 excludes generative AI and agentic AI, and clarify whether the models under discussion fall within its scope. If not, rely on the FS AI RMF or other relevant references.

### `PER-EX-007` — examiner @ Section 1: Opening Movement

**Paper claim:**

> what commensurate compliance means

**Concern:** The term 'commensurate compliance' is not defined in the paper and is not a term used in the FS AI RMF or in SR 26-2. It introduces ambiguity about what standard is being applied. An examiner would ask for clarification: compliance with what, and commensurate to what? This lack of precision could confuse readers about regulatory expectations.

**Suggested fix:** Define the term explicitly or replace it with language that reflects the FS AI RMF's own framing (e.g., 'proportionate implementation' or 'risk-based adoption'). If referring to a concept from SR 26-2, cite the specific language.

### `PER-FS-005` — frame_skeptic @ Diagnostic Techniques

**Paper claim:**

> We claim three techniques because they emerge cleanly from the frame's structural commitments and produce design constraints directly applicable to AI governance system construction.

**Concern:** Technique 1 enumerates absent parties; Technique 2 renders attestation patterns interpretable by documenting what is deliberately omitted; Technique 3 asks what an interface produces and what it infers from the resulting silence. These read as staged applications of a single operation—making implicit absences explicit and interrogating inferences drawn from them—rather than three independent methods. The paper presents them as three for expository clarity, but the separability claim is not demonstrated by distinct formal properties or non-overlapping diagnostic outputs.

**Suggested fix:** The subsection 'The techniques as compounding design constraints' could specify a formal criterion (for example, distinct input domains or non-substitutable outputs) that would render the three techniques non-reducible to one another.

### `PER-SE-005` — self_examiner @ Opening Movement – Categorical Position 1

**Paper claim:**

> "rudin2019 made it forcefully, and subsequent work has demonstrated that explanation methods can be manipulated slack2020, that chain‑of‑thought reasoning often does not reflect the model's actual reasoning lanham2023,turpin2023"

**Concern:** The citation pattern treats these works as anchor citations that substantiate the claim, yet it does not engage with any literature that challenges the impossibility of verification (e.g., work on provable interpretability or tensor‑channel observation). This selective anchoring subtly manufactures authority by silencing dissenting perspectives.

**Suggested fix:** Cite at least one counter‑point (e.g., a study on provable model interpretability) and briefly discuss why the paper’s frame still regards those approaches as insufficient, thereby making the citation landscape more balanced.

### `PER-SE-006` — self_examiner @ Conclusion

**Paper claim:**

> "The three positions, taken together, name a single structural failure mode the paper has called silence‑manufacture"

**Concern:** The paper’s analytical vocabulary labels the absence of evidence as “silence‑manufacture,” which itself is a name for an absence. By naming the absence without providing a concrete metric or observable indicator, the paper substitutes a rhetorical label for the empirical evidence it claims to lack, reproducing the silence‑manufacture pattern at the meta‑level.

**Suggested fix:** Propose a concrete proxy (e.g., frequency of post‑hoc explanations used as primary audit artifacts) that could be measured in future work to operationalize the “silence‑manufacture” label.

### `PER-SR-006` — sympathetic_regulator @ Section 1, Opening Movement

**Paper claim:**

> Community banks under the threshold for primary applicability still face the question of what commensurate compliance means, and the document itself does not answer it.

**Concern:** The FS AI RMF has no applicability threshold—it is 'designed for all financial institutions, regardless of size, type, complexity, or criticality.' The 'primary applicability threshold' language belongs to SR 26-2/OCC Bulletin 2026-13, which applies to organizations with over $30 billion in total assets and explicitly excludes generative and agentic AI. Conflating the two documents undermines the paper's credibility with regulators who know the framework's scope, and it obscures the paper's actual contribution: the FS AI RMF is the framework that does address AI specifically and does so without a size threshold, which is precisely why community banks need the interpretive help the paper offers.

**Suggested fix:** Correct the threshold reference: the FS AI RMF applies to all institutions regardless of size; the $30B threshold belongs to SR 26-2, which is revised model-risk guidance that excludes generative and agentic AI. Reframe the community-bank challenge as the 230-CO surface being operationally daunting for resource-constrained institutions without an interpretive frame, which is the paper's actual argument and does not depend on a threshold claim.

### `PER-TR-006` — technical_reviewer @ Section 3: Verification Regimes as Taxonomic Move, 'A turn: pricing as produced-absence canonical case'

**Paper claim:**

> The Truth in Lending Act requires disclosure of a rate's mathematical structure (APR, finance charges, payment schedule); it does not require disclosure of why this particular rate was offered to this particular applicant regZ1026.

**Concern:** The paper cites regZ1026 (Regulation Z, 12 CFR 1026) for the claim that TILA does not require disclosure of rate-setting rationale. This is correct as a narrow legal claim, but the paper does not acknowledge that Regulation B (Equal Credit Opportunity Act) does require creditors to provide pricing-related information in some contexts (e.g., when a customer requests it, or when pricing is based on credit score). The paper's framing of pricing as completely undisclosed is partially correct but incomplete. This is a minor point because the paper's argument about produced absence in pricing still holds even if some disclosure is required; but the citation should be more precise about what TILA does and does not require.

**Suggested fix:** Clarify: 'TILA requires disclosure of the rate's mathematical structure but not the substantive rationale for the rate offered to a particular applicant. Regulation B requires some pricing-related disclosures in specific contexts, but does not generally require disclosure of the model's reasoning for the rate offered.' This is more precise and does not weaken the paper's argument about produced absence.

### `PER-VN-007` — vendor @ Section 3: Verification Regimes as Taxonomic Move (pricing turn)

**Paper claim:**

> The Truth in Lending Act requires disclosure of a rate's mathematical structure (APR, finance charges, payment schedule); it does not require disclosure of why this particular rate was offered to this particular applicant... The customer accepts because they need credit and has no basis for negotiation.

**Concern:** The paper's characterization of pricing-decision architecture as producing silence is accurate but incomplete. The strongest vendor position is that pricing models are subject to fair-lending compliance regimes (disparate-impact analysis, monitoring for discrimination) that do constitute a verification regime, even if not at the individual-customer level. The paper acknowledges this ('Statistical validation against outcomes verifies that the model performs as intended in aggregate') but dismisses it as not addressing the individual empty chair. The paper should engage the question of whether aggregate verification is sufficient for regulatory purposes, or whether individual verification is a regulatory requirement the paper believes should exist but does not currently.

**Suggested fix:** Section 3's pricing turn should clarify whether the paper is arguing that (1) current regulatory regimes are inadequate because they do not require individual verification, or (2) individual verification is a structural requirement that current regimes fail to recognize. The distinction matters for regulatory uptake: if (1), the paper is arguing for regulatory change; if (2), the paper is arguing for interpretation of existing regulation.

### `PER-VN-008` — vendor @ Section 4: Diagnostic Techniques

**Paper claim:**

> An architect who applies them builds systems that are diagnosable; an examiner who applies them to an undiagnosable system can only document that diagnosis is unavailable... The architectural moment is where empty-chair representation is structurally determined, and the diagnostic techniques are most valuable as design-time discipline.

**Concern:** The paper assumes that architects will adopt the diagnostic techniques at design time, but provides no mechanism for ensuring adoption or for incentivizing it. The strongest vendor position is that adoption depends on regulatory mandate or competitive advantage. If neither exists, architects will continue building systems without the techniques because the techniques impose costs (implementation complexity, operational overhead, examination exposure) without immediate benefits. The paper does not address the adoption problem or the incentive structure that would drive adoption.

**Suggested fix:** Section 4 or the Conclusion should address the adoption question: what would cause architects to adopt these techniques? Regulatory mandate? Competitive differentiation? Liability exposure? The paper should either argue that adoption will occur through one of these mechanisms or acknowledge that the techniques' value is aspirational rather than predictive of actual practice.

## Persona overall assessments

### civil_rights_attorney (`qwen/qwen3.6-plus`)

[Civil Rights Attorney] This paper offers a sophisticated architectural critique of compliance theater, but it systematically sidelines the statutory hooks that give civil rights practitioners actual leverage. Before citing it in advocacy or litigation, I would add explicit mappings between its "empty-chair" and "silence-manufacture" concepts and existing ECOA/UDAAP/FHA liability standards, clarifying that architectural transparency cannot substitute for disparate-impact analysis, proxy-discrimination doctrine, or private rights of action. Without those additions, the framework risks becoming a voluntary parallel regime that institutions cite to deflect statutory fair-lending claims.

### compliance_officer (`mistralai/mistral-large-2512`)

[Compliance Officer: Community Bank] Overall assessment: I would forward this paper to peer compliance officers, but with a strong caveat: the frame is intellectually compelling, but the paper’s architectural focus is a poor fit for community banks that are buyers, not builders. The most useful parts are the diagnostic techniques (empty-chair enumeration, pages-missing, produced-silence question pair), but only if they are reframed as vendor due-diligence tools rather than design-time disciplines. The paper’s silence-manufacture critique is spot-on, but it needs a "Monday morning" translation for banks that cannot re-architect their systems.

### examiner (`deepseek/deepseek-v4-pro`)

[Examiner: Bank Supervisor] **Overall Assessment (Senior Examiner):**  
This paper contains fatal regulatory conflations—treating a voluntary industry framework as a regulation and misattributing a size threshold that belongs to separate supervisory guidance. These errors would mislead banks and examiners about the nature and applicability of the FS AI RMF. While the conceptual frame may offer interpretive value, the paper cannot be relied upon in its current form for supervisory conversation. I recommend substantial revision to clearly distinguish the FS AI RMF from binding regulations and supervisory guidance, and to accurately represent examiner practice.

### frame_skeptic (`x-ai/grok-4.3`)

[Frame Skeptic: Internal Coherence] The central frame does not fully earn its weight: silence-manufacture is presented as a single structural pattern unifying model-level, accountability-level, and institutional-level failures, yet the instances rely on distinct suppression mechanisms without a demonstrated isomorphism, and the empty-chair metaphor functions primarily as an organizing label rather than a derivation from the FS AI RMF's actual four-axis architecture. The single most important conceptual move in revision is to specify whether silence-manufacture is intended as a formal structural identity across domains or as an analogical family-resemblance concept, and to clarify whether the verification-regime normativity is immanent to the framework or an external standard the paper brings to it.

### self_examiner (`openai/gpt-oss-120b`)

[Self-Examiner: Reflexive Diagnostic] **Overall assessment:**  
By applying its own diagnostic, the paper largely succeeds in exposing structural silences in the FS AI RMF but fails to turn the diagnostic onto itself. The most critical shortcoming is the failure to acknowledge its own verification regime (Finding PER‑SE‑003), which constitutes a fatal exemption that undermines the paper’s central claim that all architectures that hide ground truth should be exposed. Addressing this meta‑silence would bring the paper into full compliance with the standard it sets.

### sympathetic_regulator (`z-ai/glm-5.1`)

[Sympathetic Regulator: Generative Critic] **Overall assessment:** I would carry the empty-chair frame and the structural/produced absence distinction into the next revision cycle—they provide genuine interpretive leverage on the 230-CO surface and could shape Sub-Category language under existing Categories (particularly GV-1, MS-1, MS-2, and MG-4). Before doing so, I would ask the author for three things: (1) draft CO-style language for at least the post-hoc-explanation foreclosure and the contemporaneous-capture requirement, so the revision has text to work with rather than positions to translate; (2) a minimum mandatory empty-chair enumeration for lending and BSA/AML, so examiners start from a common floor; and (3) an examination-detectable indicator for silence-manufacture at the institutional level, without which the paper's unifying concept remains analytically powerful but supervisially inert. The silence-manufacture unification is the paper's strongest intellectual contribution and its largest operational gap—closing that gap is the difference between a framework revision that absorbs the vocabulary and one that acts on the structure.

### technical_reviewer (`anthropic/claude-haiku-4.5`)

[Technical Reviewer: ML/AI Researcher] ---

## Overall Assessment

This position paper makes bold structural claims about AI governance, empty-chair representation, and silence-manufacture. The core argument is intellectually coherent and addresses a real gap in how the FS AI RMF is understood. However, the paper has significant citation-fidelity and empirical-grounding problems that weaken its technical standing:

1. **Citation overreach** (PER-TR-001, PER-TR-002): The paper cites Lanham, Turpin, and Bordt for claims those papers do not fully support. Specifically, findings about LLM chain-of-thought faithfulness are generalized to all post-hoc explanation methods, and Bordt et al.'s work on adversarial contexts is applied to bank examination without establishing that connection.

2. **Statistical inference without baseline** (PER-TR-003): The 78%/22% skew in framework principles is presented as evidence of imbalance, but no null model or justification for what distribution would be expected is provided.

3. **Unfalsifiability and circularity** (PER-TR-004, PER-TR-008): The frame's generativity is asserted but not demonstrated. The silence-manufacture prediction about de-banking is presented as evidence but the causal chain is not clearly established.

4. **Incomplete structural argument** (PER-TR-009, PER-TR-010): The paper claims the four primitives are necessary for empty-chair representation but acknowledges they may not be sufficient, which undermines the claim that the paper has identified what representation requires. The theory of effect (how the frame reaches architects and motivates adoption) is absent.

**Recommendation: Revise and resubmit.** The paper's core insights about empty-chair representation and silence-manufacture are valuable and worth developing. However, the technical claims must be tightened to match the evidence cited, the statistical inferences must be grounded in defensible baselines, and the practical pathway from structural argument to architectural adoption must be specified. The paper would benefit from a more modest framing of what it establishes (structural diagnosis of silence-manufacture) versus what it leaves open (empirical validation, regulatory uptake, architectural adoption).

### vendor (`anthropic/claude-haiku-4.5`)

[Vendor: Articulate Advocate] ---

## Overall Assessment

This paper has changed my understanding of what my tools are for, but not in the direction the paper intends.

The paper's strongest contribution is the **silence-manufacture frame** (Section 4), which unifies three separate critiques into a coherent structural pattern. That unification is genuinely powerful: it explains why compliance theater persists across reform cycles, why analytical literatures partition around certain phenomena, and why Goodhart-shaped fixes fail. If the frame is right, my industry has been building sophisticated substitutes for the ground truth we claim to expose, and reading the absence of challenge as evidence of adequacy.

But the paper does not actually refute the position I represent. It refutes a *weaker* version of it.

The paper's categoricals (post-hoc explanation is inadequate, human oversight of explanations is not verification) are structurally sound *if* you accept the paper's definition of verification: binding to underlying reasoning. But the strongest vendor position is not that post-hoc explanations are faithful. It is that they narrow the search space for interrogation, and that domain experts calibrated through repeated exposure to cases and outcomes develop judgment that constitutes a verification regime even without reasoning-faithfulness. The paper does not engage this search-space-narrowing argument. It attacks the faithfulness claim, which is not the strongest version of the position.

Similarly, the paper does not address interpretable-by-design models, which solve the verification problem the paper identifies without requiring the architectural primitives the paper proposes. The paper cites Rudin but does not engage the position that interpretable models are the answer to the verification gap. This is a significant omission.

**What has changed:** I now see that my industry's strongest case is not "explanations are faithful" but "explanations narrow search space and domain experts develop judgment." That is a much more defensible position than what the paper attacks. And I see that the silence-manufacture frame is a useful diagnostic for distinguishing between systems that genuinely narrow search space and systems that produce substitute artifacts while suppressing ground truth.

**What has not changed:** I still believe that human-on-the-loop explanation tooling, when applied to interpretable-by-design models or to decision-support systems where AI surfaces material for human reasoning, provides real verification regimes. The paper's architectural primitives are valuable, but they are not the only path to honest empty-chair representation.

The paper would be stronger if it engaged the search-space-narrowing argument, addressed interpretable-by-design models explicitly, and clarified whether it is arguing for regulatory change or regulatory interpretation. As written, it has changed how I think about silence-manufacture, but it has not changed what I believe my tools are for.
