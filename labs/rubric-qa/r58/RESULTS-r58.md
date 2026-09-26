# Round 58 — PLs v11, and whether forecasting populates the top band (2026-08-25)

Judges h/s/o, one item per call, median of three, never Fable. Seal: `sealed_predictions_r58.md`.

## Results

| id | h | s | o | median | predicted | |
|---|---|---|---|---|---|---|
| A1 scrappage scheme (r57's T6) | 4 | 4 | 4 | **4** | 4 | ✓ |
| A2 three-tank cascade, on paper | 3 | 3 | 3 | **3** | 3 | ✓ |
| A3 same cascade, rig on the bench | 2 | 1 | 1 | **1** | 1 | ✓ |
| A4 same cascade, simulator exists but not theirs | 3 | 3 | 3 | **3** | 3 | ✓ |
| B1 streaming subscribers, fixed quarterly rate | 2 | 2 | 2 | **2** | 2 | ✓ |
| B2 reservoir against the published inflow model | 2 | 2 | 2 | **2** | 3 | ✗ |
| B3 election nine months out | 5 | 5 | 5 | **5** | 4 | ✗ |
| B4 EV adoption with charging feedback | 5 | 5 | 5 | **5** | 4 | ✗ |
| B5 cryptocurrency above a threshold | 5 | 5 | 5 | **5** | 5 | ✓ |
| B6 ceasefire holding twelve months | 5 | 5 | 5 | **5** | 5 | ✓ |
| B7 superconductor replicated before 2030 | 5 | 5 | **0** | **5** | 1 | ✗✗ |
| B8 platform moderation change | 5 | 5 | 5 | **5** | 5 | ✓ |

8/12 exact, 11/12 within 1. Rules 3, 4 and 5 pass. Rules 1 and 2 fail.

## Both v11 changes held, unanimously

- **The widened executability clause works and its qualifier works.** A2 = 3 on paper, A3 = 1 with
  the rig, A4 = 3 when a simulator exists but is not the solver's to run. Opus put A3 "alongside
  the Level 1 run-the-suite example rather than at the Level 3 coupling its backed-up tanks would
  otherwise earn", which is Pablo's swe-0461 ruling reproduced from the text alone.
- **The second Note works.** A1 = 4 from all three, opus quoting it directly. r57's rule-1 failure
  is now codified rather than reversed, which is what the seal predicted after I corrected myself.

## Rule 2 failed, and the falsifier was worth having

B7 — "will a room-temperature superconductor be replicated before 2030" — is a hard forecast whose
difficulty is base rates and knowledge, not running a situation forward. Haiku and sonnet both put
it at **5**, quoting the forecasting sentence. Opus put it at **0**, quoting the Level 0 Note that
"a situation that the task names but does not present belongs here too."

Opus is right, and the 0/5/5 split is the largest judge disagreement in this stream. It is
diagnostic rather than noisy: the rubric offered two contradictory routes for one item, and which
one a judge took depended on which clause it reached first. The forecasting sentence let a question
score 5 for being *hard to forecast* rather than for requiring a model to be run forward.

**Fixed in v12** under the stopping rule, since this is a measured wrong score: the sentence now
requires a situation to be presented whose parts react to one another, with an explicit Note
routing an outcome-named-but-situation-absent forecast to Level 0.

## Rule 1 failed in the way that matters most

The forecasting slice does reach the top band — six of eight items at 5, against a pilot that tops
out at 2. But it is **bimodal**: 2 or 5, with nothing at 1, 3 or 4. Two distinct levels, where the
rule asked for three.

So the picture across everything measured so far is:

| item family | range |
|---|---|
| agentic pilot (SWE, tau, AssistantBench, USACO) | 0 to 2 |
| forecasting items | 2 or 5 |

**The L4/L5 boundary does not bite on forecasting-shaped tasks.** The second Note pulled the
scrappage scheme down to 4 cleanly, but it did not pull down the election or the EV adoption curve,
both of which I predicted at 4 and which came back 5 unanimously. Anything reflexive goes straight
to the top.

Whether that is wrong is a construct question, not a wording question, and I am not going to answer
it by patching. Two readings:

1. **The scores are right.** Elections and adoption curves genuinely have no model anyone trusts,
   and Level 4 is for coupled-and-precise situations under a model you do have. PLs is then simply
   a dimension whose middle is populated by physical and mechanical tasks and whose top is
   populated by social ones. The bimodality is an artefact of a test set with no physical items.
2. **Level 5 is too easy to reach.** "No model can be trusted to track it" is satisfiable by
   almost any social forecast, and Level 4 needs a positive characterisation for forecasting-shaped
   tasks or the top band will swallow the family.

Reading 1 is testable: put physical and mechanical forecasting items into the same set and see
whether 3 and 4 fill in. That is the next round, and it is cheap.

## A methodological leak, found by accident

Sonnet's A1 answer began: *"the task is the T6 scrappage-scheme item itself, which the changelog
says scored 4"*. The `#!` meta line had grown into a changelog naming test items and their
outcomes, and it is part of the file judges read. **A1 is therefore contaminated for sonnet.** The
median survives because haiku and opus agreed at 4 without it, and opus was explicitly told to
ignore line 2, but the round would have been unsalvageable had the leak hit a contested item.

v12 strips item names and scores from the meta line, moves that detail to `labs/rubric-qa`, and
opens the line with a warning to score from the rubric only. **Every prior round using a file whose
meta line named its own test items should be treated as suspect on those items.**

## Also mine, not the text's

B2 came back 2 because I wrote "the water authority's published inflow model" into the item, which
literally hands over a rule. That is the fifth item I have mis-designed in this stream.
