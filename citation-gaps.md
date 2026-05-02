# Citation-Gap Punch List
*Generated 2026-05-02. Inline citation pass completed 2026-05-02.*

## Status

**14 of 20 gaps resolved.** Tony added 9 new bib entries (`treasuryFSAIRMFRelease2026`, `ffiecBSAAMLManual`, `treasuryDeRisking2023`, `regB1002_9`, `cfpbCircular2022_03`, `regZ1026`, `sr11_7`, `sr26_2`, `usc31_5318g2`) plus `goodhart1984problems`; inline `\parencite` calls added at the corresponding sites. Paper builds clean at 33 pages, no undefined references.

**6 gaps remain open** — all require sourcing new material before prose can cite. Listed below.

---

## Open gaps

### section1.tex:18 — *commentary attribution*
> "Recent commentary on the FS~AI~RMF describes it as a \emph{systems blueprint} rather than a checklist..."

The CRI Guidebook PDFs in `references/` (CRI FS AI RMF Guidebook, Initial Stage and Full versions) are likely candidates if CRI is the source of the "systems blueprint" framing. Otherwise: a Sullcrom or comparable law-firm memo distinct from `sullcrom2026`.

### section2.tex:70 — *operational decision-making qualifier*
> "...there is extensive evidence from cognitive psychology that retrospective justifications often diverge from the reasoning that actually produced a decision, especially under time pressure and high case volume \parencite{nisbett1977}."

Nisbett & Wilson covers introspection limits but not the time-pressure qualifier. Candidates: Kahneman & Klein 2009 ("Conditions for intuitive expertise"); Klein 1998 (*Sources of Power*); or operational decision-making literature.

### section3.tex:92 — *fair-lending / pricing-discrimination cluster*
> "The dishonest middle in pricing is more diffuse than in denial because there is no regulatory artifact equivalent to the adverse action notice..."

Bartlett, Morse, Stanton & Wallace 2022 ("Consumer-lending discrimination in the FinTech era," *J. Financial Economics*); CFPB indirect-auto-pricing actions could supplement.

### section4.tex:24 — *optional / aspirational*
> "An architect who applies them builds systems that are diagnosable; an examiner who applies them to an undiagnosable system can only document that diagnosis is unavailable."

Brooks 1975 (*Mythical Man-Month*, conceptual integrity) or Wing 2006 ("Computational thinking") as design-methodology anchor. Skippable if the structural argument stands without an authority anchor.

### section4.tex:54 — *Goodhart-on-safety-evals literature*
> "...benchmark gaming, eval-set contamination, and the Goodhart-on-safety-evals pattern: metrics survive while the underlying construct degrades..."

Manheim & Garrabrant 2018 (arXiv:1803.04585, "Categorizing Variants of Goodhart's Law") is a tractable canonical anchor. Recht et al. on benchmark contamination is an alternative.

### section5.tex:95 — *interpretability-research anchor*
> "By \emph{tensor-channel observation} we mean direct observation of model internal state --- activations, attention patterns, intermediate representations..."

Anthropic interpretability anchor: Olah et al. circuits work; Bricken et al. 2023 (dictionary learning / monosemanticity); or Elhage et al. "Toy Models of Superposition." The paper's argument leans on internal-state observation as the alternative to text-channel verification, so this anchor matters more than `rudin2019` (which is for ante-hoc interpretability, a different category).

---

## Resolved (for reference)

| Site | Cite added | Bib key |
|---|---|---|
| section1.tex:16 | FS AI RMF release | `treasuryFSAIRMFRelease2026` |
| section2.tex:33 | FFIEC BSA/AML Manual | `ffiecBSAAMLManual` |
| section2.tex:39 | Treasury 2023 De-risking | `treasuryDeRisking2023` |
| section3.tex:37 | Reg B AAN provisions | `regB1002_9` |
| section3.tex:37 | FCRA AAN provisions | `fcraAdverseAction` |
| section3.tex:41 | CFPB Circular 2022-03 | `cfpbCircular2022_03` |
| section3.tex:47 | CFPB Circular 2022-03 | `cfpbCircular2022_03` |
| section3.tex:90 | TILA / Reg Z | `regZ1026` |
| section3.tex:102 | SR 11-7 + SR 26-2 | `sr11_7,sr26_2` |
| section4.tex:39 | Goodhart 1984 | `goodhart1984problems` (Tony) |
| section4.tex:52 | Sycophancy + RLHF | `sharma2023,perez2022` |
| section4.tex:67 | 31 USC §5318(g)(2) | `usc31_5318g2` |
| section6.tex:48 | April 2026 model-risk | `sullcrom2026` |
| section6.tex:50 | Goodhart 1984 | `goodhart1984problems` (Tony) |
| section7.tex:20 | FS AI RMF release | `treasuryFSAIRMFRelease2026` |
| section7.tex:34 | Goodhart 1984 | `goodhart1984problems` (already there) |

---

## Other notes

- Section 3 (lending) had the densest concentration of gaps; the regulatory-anchor cluster (ECOA/Reg B, FCRA, TILA/Reg Z, SR 11-7, CFPB circular) is now anchored.
- The drafter tracked needs in section-top `%` comments rather than `\needcite` inline. If future drafting wants unfilled spots visible in the rendered PDF, switch to inline `\needcite` markers.
- Biber still emits a "legacy month field" warning for `bordt2022` (`month={June}` should be `month=jun` or numeric). Cosmetic.
