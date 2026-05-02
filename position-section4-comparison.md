# Section 4 Pressure Test: Examiner-Primary vs. Architect-Primary

*Status: comparison artifact. Both Section 4 drafts arrive at the same three diagnostic techniques (empty-chair enumeration, pages missing from the ledger, produced-silence question pair) but frame them as either examiner moves or architect moves. This document examines what each framing accomplishes that the other doesn't.*

## What each version is trying to do

Both versions develop the same three techniques as the section's load-bearing diagnostic content. Both treat produced-silence as the most contestable of the three. Both transition into Section 5 by arguing that primitive categories are determined by what the techniques require.

The difference is in *who is the primary diagnostic agent*, which determines what the techniques mean and how they constrain action.

Examiner-primary frames the techniques as moves an examiner brings to an existing system, producing assessment leverage during regulatory review. The audience is regulators thinking about how to examine.

Architect-primary frames the techniques as design-time questions an architect asks while building, with examination-time application falling out as consequence. The audience is builders thinking about how to build, with regulators as the inheritors of buildings designed under the discipline.

These produce different sections in subtle but consequential ways.

## Where each is stronger

**Examiner-primary is stronger at:**

- Direct alignment with the paper's stated audience. The paper is researcher-to-regulator, the FS AI RMF is an examination framework, and examiners are the most direct empty-chair frame consumers. Framing diagnosis from their perspective lands in the conversation the paper is already part of.

- Connecting to existing examination practice. Examiners have established methodology for reviewing institutions; the techniques described as additions to that methodology slot into existing practice. The reader can imagine using them next week without rebuilding their conception of their job.

- Concrete operational claim. The techniques produce findings during examination; the findings have regulatory weight; the institution responds to the findings. The chain from technique to consequence is short and well-understood.

- Acknowledgment of the coordination problem from Section 1. The examiner-primary version explicitly notes that the techniques' value depends on examination resources and expertise, which honors the caveat from the opening. The architect-primary version partially elides this.

**Architect-primary is stronger at:**

- Deeper structural claim. The architect-primary framing argues that examination-time diagnosis is inadequate as a primary intervention point, because a system designed without the techniques may be unable to answer the diagnostic questions regardless of examiner skill. This is a sharper claim than examiner-primary makes.

- Coherence with the paper's overall position. The paper argues that AI governance must be architectural rather than documentational. Diagnosis-as-design-discipline is structurally consistent with that position; diagnosis-as-examination-technique is partly orthogonal to it. The architect-primary version's section reinforces the paper's architectural claim throughout; the examiner-primary version's section pivots to a different agent and partly leaves the architectural argument.

- Setting up Section 5 more directly. Section 5 develops architectural primitive categories. If diagnosis is framed as architect-primary, the primitives are tools the architect uses for design-time discipline, which is the natural framing. If diagnosis is framed as examiner-primary, the primitives are tools that support examination, which is a step further from architectural design and requires more transition work.

- Producing a normative claim Section 6 (honest uncertainties) can interrogate. The architect-primary section makes an explicit claim that AI governance systems should be architected to be diagnosable; this is contestable and a position paper should make contestable claims it can defend. The examiner-primary section's claims are largely about what examiners can do, which is less contestable but also less load-bearing for the paper's overall argument.

## Where each is weaker

**Examiner-primary weakness:** The framing partly accepts existing systems as the diagnostic target rather than challenging the systems' structural inadequacy. An examiner using the techniques on a system designed without them can produce findings of inadequacy, but the section as drafted doesn't strongly argue that this is the wrong intervention point. The reader could leave the section thinking "great, more sophisticated examination techniques" rather than "examination-time intervention is inadequate; the techniques' real work is at architectural design time."

**Examiner-primary weakness:** The audience-coherence argument cuts both ways. Yes, examiners are the most direct frame consumers. But the paper is a *position paper*, which means it's not just describing what examiners should do — it's making a structural argument about AI governance. Framing the techniques as examination methodology subtly relegates the frame to a methodology-of-examination rather than an architecture-of-governance, which is a softer position than the paper's overall argument.

**Architect-primary weakness:** Audience indirection. The paper's audience is regulators; the architect-primary framing addresses architects with regulators as inheritors. This requires the regulator-reader to translate "what the architect should do" into "what we should require architects to do," which is a step they may or may not take. The examiner-primary framing speaks directly to its audience.

**Architect-primary weakness:** The examination-as-consequence framing in the architect-primary version is genuinely true but rhetorically risky. The reader who is skeptical of the architectural claim arrives at examination-as-consequence and sees the section's primary value happening in a different conversation than the one they're in. Examiner-primary keeps the audience in their conversation throughout.

**Architect-primary weakness:** Implementability claims. Architect-primary asks more of architects than examiner-primary asks of examiners. Architects already build under cost and deadline pressure; adding three diagnostic techniques as design discipline is a substantial demand and the section as drafted doesn't fully engage with whether the demand is realistic. Examiner-primary asks examiners to add to their repertoire; architect-primary asks architects to change their methodology.

## What the comparison reveals about the section's role

The section's role in the paper is to operationalize the frame. The question is: operationalize *for whom*?

If the paper's primary intervention point is examination practice — making examiners better at reading existing systems — examiner-primary is the right framing. The section produces tools regulators can use, and the architectural claim is implicit (good architecture supports good examination).

If the paper's primary intervention point is architectural design — making the systems built under FS AI RMF be designed for empty-chair representation from the start — architect-primary is the right framing. The section produces design discipline architects can adopt, and the examination claim falls out as consequence.

These are different theories of how a position paper produces effect. The first says: improve the regulatory review process and institutions will respond by building better systems. The second says: improve the architectural design process and the regulatory review process will benefit as a consequence. Both are coherent. The position paper has to choose one as primary; the choice is partly about audience and partly about which intervention point the paper believes is more leveraged.

## What I notice about my own preference

The architect-primary version is structurally tighter. It coheres better with the paper's overall claim, sets up Section 5 more directly, and makes a sharper normative argument. I drafted it second and felt it produce more of the section's needed work in less space.

The examiner-primary version is rhetorically tighter. It speaks directly to the audience the paper is addressing. It connects to existing practice in ways the reader can act on without rebuilding their conception of their role.

If I had to choose without further input, I would lean architect-primary, because the structural argument is the paper's load-bearing claim and the section should reinforce it. But the lean is real, not strong. The examiner-primary version is genuinely good and may be the right choice for audience-coherence reasons that outweigh the structural-coherence reasons.

## Recommendation

A hybrid that keeps architect-primary as the dominant framing while including an explicit examination-time application section. Specifically: develop the three techniques as design-time discipline (architect-primary), then include a section explicitly demonstrating how examiners apply the same techniques to existing systems, with the asymmetry from the architect-primary draft preserved (a system designed without the techniques may be undiagnosable regardless of examiner skill).

The hybrid achieves several things. It makes the structural claim — diagnosis is architectural discipline first, examination methodology second — load-bearing rather than implicit. It speaks to the regulator audience by including their application of the techniques, but does so within a framing that argues for architectural intervention as the primary leverage point. It avoids the audience-indirection weakness of pure architect-primary while preserving the structural coherence the architect framing produces.

Estimated section length: similar to either standalone version, perhaps slightly longer because the architect-primary content plus the examination-application turn is more material than either alone. ~3000 words. Long but justifiable for a section developing three techniques and demonstrating their application across two agents.

## Alternative I rejected

Pure examiner-primary, which I argued for instinctively before drafting. Rejected because the architect-primary version's structural argument is sharper and the paper's overall claim benefits more from architect-primary framing. The instinct toward examiner-primary was audience-driven rather than substance-driven.

Pure architect-primary, without the examination turn. Rejected because the audience-indirection weakness is real and the regulator-reader needs to see their own application of the techniques explicitly rather than translating from the architect framing.

## What I'm uncertain about

The hybrid recommendation is my call after drafting both. Tony may read both and conclude differently. The architect-primary framing is more ambitious and may be the wrong move for a paper that benefits from being read in regulatory venues. The examiner-primary framing is more accessible and may underclaim what the paper is actually arguing.

The implementability concern about architect-primary is real and not fully addressed in the draft. Architects build under constraints; design discipline that adds substantial work without producing visible value to the institution may not survive contact with project deadlines. The position paper can argue for the discipline without solving the adoption problem, but Section 6 (honest uncertainties) probably needs to acknowledge it.

The conservative-balancing principle from Section 3 (canonical example after Section 2's unusual one) doesn't have a clear analogue here. Both framings are defensible regulatory positions; neither is obviously the unusual choice. The hybrid recommendation is conservative-by-comparison in the sense that it preserves both framings rather than committing fully to architect-primary, but the comparison is to "pure architect-primary" rather than to "the canonical position." Worth flagging that the alternation principle from Section 3 doesn't straightforwardly apply.
