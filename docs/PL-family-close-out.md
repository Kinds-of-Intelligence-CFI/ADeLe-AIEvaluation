# PL family and MS pair — close-out (2026-08-25)

PLp, PLe, PLs, MSm, MSc. Branch `rubrics/v2-improved`. Rounds r57 to r65 in `labs/rubric-qa`.

## What is closed

**Style and shape.** All five sit inside v1's range on every measure: prose sentence length,
example count and length, and zero em-dashes, semicolons, cross-level references or rationale
glosses against v1's rate of zero cross-references and one gloss in 335 example bullets. The
"level of cognitive demands" opener, which appears in no v1 file, is gone from every v2 file that
carried it.

**Ladders and carves, measured.** Each rubric has a measured monotone ladder and working
exclusions. MSc passed 9 of 9 on its first round with all three carves binding. PLe's top band was
challenged and survived for a principled reason. PLs's Level 4 now names sensitivity as its mark,
at Pablo's suggestion, and it separates without over-firing.

**Six construct rulings by Pablo, each implemented and measured**: demand is what the task requires
rather than what the instance supplies; the absent-referent case is Level 1, not Level 0;
executability holds however coupled the situation is; running cost is not a distinction the rubric
needs; the PLp/PLs co-load is accepted rather than engineered away; Level 5 turns on whether an
adequate model can be had rather than on whether the literature has one.

**Human agreement above 2, for the first time.** PLs agrees with Pablo's label on the fire item at
4. PLe agrees at 3 and 4 on two items. PLp agrees at 3 on two items and at 4 by argument.

## What is not closed, in order of cost

1. **Criterion validity (desideratum 9), all five.** No demand label has ever been joined to a
   solver outcome. This cannot be settled by a round; it needs labels on real instances, model
   success or failure on those same instances, and a test that the first predicts the second.
   ForecastBench supplies real questions and per-question ground truth but publishes no LLM
   forecasts, so the outcomes would have to be generated.
2. **PLp has no independent human label above 3**, and MSc has none at any level.
3. **PLp's Level 5 may be unreachable by operational tasks.** Its three examples are all
   research-grade invention. If nothing operational reaches it, PLp has the empty-ceiling problem
   PLs had before the forecasting slice.
4. **The chess reading** awaits Pablo's confirmation that his label and the rubric's score answer
   different questions rather than conflicting. If he confirms, this closes with no text change.
5. **MSm's three-deep nested attribution route to Level 5** is untested; the r60 item had two.

## Two things about the evidence itself

**Judge disagreement is concentrated at the top.** Across r57 to r65, spreads of two or three
levels occurred almost exclusively at Level 3 and above. The low band has been stable throughout.
Median-of-three has now absorbed a wrong haiku answer in r58, r61, r63 and r64. **A single-judge
annotation run with a small model would have taken all four.** Use at least three judges, or a
strong one.

**Strip the `#!` line before judging.** Two rounds were contaminated by judges reading the
changelog, one of them quoting a warning that was there to prevent exactly that. Telling a judge
to ignore a line does not work. r65 was the first round scored against a stripped copy and no
judge referenced it.

## An honest tally

Across this stream a prediction or worry of mine was wrong and the text, or Pablo, was right **ten
times**; the reverse did not happen. Separately, I built probe items that restated a rubric example
or pre-resolved what they were meant to test **eight times**, including once in the very round that
introduced a check against it. Two consequences follow. The item-independence check must be a
mechanical diff at seal time rather than an assertion. And the agreement figures in these rounds
should be read knowing that some cells measured recall of an example rather than application of a
rule.
