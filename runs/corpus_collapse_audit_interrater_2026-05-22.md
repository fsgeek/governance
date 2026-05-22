# Inter-rater codings — collapse-audit (4 raters, 2026-05-22)

Pre-reg: docs/superpowers/specs/2026-05-22-collapse-audit-interrater-preregistration-note.md (commit 8ea285e).
Raters A–D: independent, identical frozen rubric, mutually blind. pc=premature-collapse, hn=honest-null, sc=successful-collapse, snt=substrate-non-transport, ot=other.

| cycle | A | B | C | D | 5-way | collapse-unanimous |
|---|---|---|---|---|---|---|
| shap-rash | hn | hn | hn | sc | 3-1 | yes |
| i-stab | hn | hn | hn | hn | UNANIMOUS | yes |
| v1v2 | pc | pc | pc | pc | UNANIMOUS | yes (collapse) |
| refine6 | snt | hn | ot | hn | split | yes |
| within | sc | sc | sc | sc | UNANIMOUS | yes |
| shap-pric | hn | hn | hn | hn | UNANIMOUS | yes |
| dis-geo | pc | ot | pc | ot | 3-1 | NO |
| dis-rout | hn | pc | pc | pc | 3-1 | NO |
| ext-band | pc | snt | ot | snt | split | NO |
| routable | hn | hn | hn | hn | UNANIMOUS | yes |
| fm11 | snt | snt | pc | snt | 3-1 | NO |
| silence12 | sc | pc | pc | ot | split | NO |
| hmda | snt | snt | snt | snt | UNANIMOUS | yes |
| expanded14 | pc | pc | pc | pc | UNANIMOUS | yes (collapse) |
| frame13 | hn | ot | hn | hn | 3-1 | yes |
| saturation | ot | sc | sc | sc | 3-1 | yes |

## Agreement
- 5-way: pairwise exact 0.646, Fleiss κ **0.537**
- binary collapse-vs-not: pairwise 0.823, Fleiss κ **0.546**
- premature-collapse counts (of 16): A=4, B=4, C=6, D=3 — all raters: NOT modal; honest-null largest/tied (A=6,B=5,C=5,D=5)
- contested (5-way non-unanimous): shap-rash, refine6, dis-geo, dis-rout, ext-band, fm11, silence12, frame13, saturation
- scatter concentrates on MULTI-LEG experiments (dis-geo, ext-band, fm11, silence12)
