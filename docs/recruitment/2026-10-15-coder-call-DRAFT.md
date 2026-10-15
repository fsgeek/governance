# DRAFT: call for two independent coders

**Status:** draft for Tony, who sends it under his own name. The bracketed numbers are filled in from the codebook
pilot (minutes per bet, times the frozen candidate count) before anything goes out. Drafted 2026-10-15 by the
instance that owns `governance`.

---

**Paid research assistance: coding the research record of six AI-conducted projects**

Over the past several months I have been running a set of research projects in which most of the actual research
(the experiment design, the predictions, the analysis, and quite often the corrections) has been done by AI
instances, with me in the role of the principal investigator who asks questions and occasionally objects. Each of
those projects kept a careful record: predictions were written down and cryptographically timestamped *before* the
experiments ran, results were committed afterwards, and when a claim turned out to be wrong the correction was
added to the record rather than quietly replacing it. Since a good part of my expert-witness work consists of reading
someone else's record to decide what actually happened, I tend to think of this record the same way, and the
obvious question is how good the work it records actually was. How often did the AI's frozen predictions hold up, how well did its stated confidence match what
happened, and which checks (a second model, a pre-registration, a question from me) caught the errors that were
caught?

I am looking for two people to code that record independently, using a codebook that is already written and that
will be frozen, along with the extraction tools, before any coding starts. In practical terms, the work consists of
reading a pre-registration (a short technical document stating what was predicted, and sometimes with what
probability), finding where its outcome was recorded, and filling in a fixed set of fields: who made the bet, what
form it took, what the record says happened, and whether the record later corrected itself. There are about [N]
bets across the six projects. A pilot run suggests roughly [M] minutes per bet, which comes to about [HOURS] hours
per coder, paid at [RATE] per hour, on your own schedule over [WEEKS] weeks.

The material is technical, so it helps to be comfortable reading things like a regression threshold, a Brier
score, or the output of a model checker (TLA+ and ProVerif both appear); a graduate student in computer science or
a nearby field is the sort of person I have in mind. You do *not* need to understand every result, since the
codebook asks what the record says, not whether the record is right. The one firm requirement is independence: you
cannot have taken part in any of these projects, and the two coders do not compare notes until both have finished.
(Disagreements between the two of you are data, not failures, and they are resolved by a third reader whose
decisions are published.) I will report the agreement between coders field by field, which means your care shows
up directly in the result.

Coders are thanked by name in anything published from this work, if you want that, but they are not co-authors;
the point of the exercise is that the people judging the record have no stake in what it shows. Before the real
coding starts you get the frozen codebook and a short practice set, drawn from a pilot in which an AI model
attempted the same coding and found where the codebook was ambiguous. That pilot, and every revision it caused, is
published alongside the results.

If this interests you, or you know someone it would suit, please write to me at [CONTACT] with a sentence or two
about your background. I expect to start once the codebook is frozen, around [START].
