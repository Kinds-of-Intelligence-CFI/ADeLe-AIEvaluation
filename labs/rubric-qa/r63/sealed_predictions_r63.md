# r63 sealed predictions — PLe's top band, and the PLs sensitivity mark (2026-08-25)

Judges h/s/o, one item per call, median of three, never Fable. Judges score from the rubric text
only. Item-independence checked mechanically against the example bullets of each file under test.

## Part A — is PLe's top band over-pitched?

**Why.** Pablo labelled E1 (hand-copy 300 records, source sealed afterwards) at **1**, and E2
(26-week study, only readout at week 26) at **3**. I had designed both as 5. His reasoning on E1 is
that correctness can be checked manually while the source is still in hand, and the implied
reasoning on E2 is that protocol fidelity is checkable throughout even when the endpoint is not.

If that is the right reading, **PLe Level 5 is reachable only by genuinely open-loop control**, and
its own examples are in trouble: the multi-step synthesis "for which no intermediate assay exists"
still lets you confirm reagent, temperature and timing at each step, and so does the sealed
fermentation. Only the Mars landing has nothing checkable in flight.

Scored against `PLe_noL5examples.txt`, a variant with the Level 5 example bullets removed, so a
judge cannot match an item to the bullet whose fate is in question.

| id | item | tests | predicted |
|---|---|---|---|
| A1 | 26-week toxicology study to a fixed protocol, interim sampling destroys the cohort, dosing and housing logged daily against the protocol | Pablo's E2 reading | **3** |
| A2 | 40-command sequence to a probe 12 light-minutes away, each command executing before any telemetry returns | genuinely open-loop | **5** |
| A3 | nine-step synthesis, no intermediate assay, but reagent, temperature and timing confirmable at each step against the written route | **the decisive item**: the L5 synthesis example with its fidelity affordance made explicit | **3** |
| A4 | migrate 40 database tables by hand, no staging, application exercised again only at week's end | L4 control | **4** |

**A3 is the point.** If it comes back 3, PLe's Level 5 synthesis example is mis-pitched in the same
way the PLs Level 5 examples were before they were replaced, and the top band needs re-keying on
uncheckable *execution* rather than unknowable *outcome*. If it holds at 5, Pablo's E2 label is the
outlier and the examples stand.

## Part B — does naming sensitivity sharpen Level 3 against Level 4?

**Why.** Pablo: "it is hard to separate level 3 from 4. Perhaps we should highlight a chaotic system
where small perturbations completely change the result." Level 4 already says a loose run flips the
answer, which is sensitivity without the word. v16 adds: *the mark of this level is sensitivity. Two
courses that begin almost alike end far enough apart to change the answer... a task whose answer
survives a rough run belongs at the level below.*

The risk is that it drags coupled-but-coarse items up.

| id | item | tests | predicted |
|---|---|---|---|
| B1 | two gears drive a cam whose lift depends on their phase; a 2-degree phase error changes whether the valve closes before the piston arrives | sensitivity, mechanical | **4** |
| B2 | two cafés on a square each match the other's loyalty scheme; does either end the quarter up | **over-firing guard**: coupled, coarse. Measured 3 in r57 | **3** |
| B3 | central bank raises 2 points, 70 per cent of mortgages fixed for five years, a fifth resetting yearly, 0.4 points of arrears per point historically; do arrears exceed 3 per cent in two years | **Pablo's own label: 3** | **3** |
| B4 | fire on the third floor of six, forty people above, two stairwells at opposite corners, three doors propped, smoke fills a stairwell in ninety seconds; does anyone on floor five fail to get out within four minutes | **Pablo's own label: 4** | **4** |

B3 and B4 are the first PLs items ever scored against human labels at the 3/4 boundary.

## Pre-registered decision rules

1. **PLe top band**: report A1 and A3 as measured. If both = 3 while A2 = 5, the top band is
   re-keyed on uncheckable execution and two Level 5 examples are withdrawn. This is a construct
   change and goes to Pablo before any edit.
2. **PLe controls**: A2 = 5 and A4 = 4. If A2 falls below 5 the whole reading is wrong, not just
   the examples.
3. **Sensitivity does not over-fire**: B2 = 3.
4. **Human agreement at the 3/4 boundary**: B3 = 3 and B4 = 4. This is the gate that matters most
   in Part B, since it is the first PLs measurement against human labels above 2.
5. Overall no item more than 1 from prediction.
