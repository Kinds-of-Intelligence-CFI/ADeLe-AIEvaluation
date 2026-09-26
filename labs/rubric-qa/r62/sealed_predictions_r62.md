# r62 sealed predictions — the rule-governed-options clause (2026-08-25)

Text under test: PLs v15. Judges h/s/o, one item per call, median of three, never Fable.

## Why this round exists

Pablo labelled the club-level chess plan at **PLs 2**. All three judges put it at **3** in r59, and
their reasoning was unanimous on the cause: each read *alternating turns* as parts acting on one
another. haiku, "how your moves and opponent's responses influence each other"; sonnet, "interact
and feed back on each other"; opus, "the opponent's reciprocal responses".

That is a measured wrong score against a human label, which licenses a wording fix. Pablo chose the
narrowest of the three candidates: the exclusions already say other agents enter as parts of the
model *whose described tendencies are run forward*, and in chess there are no tendencies, only legal
moves. v15 adds: *where their options follow from stated rules rather than from described
tendencies, the rules supply the model, and running those options forward makes no more demand than
any other rule-governed step, however many turns are taken.*

**The risk is over-firing.** Two of the four items exist only to catch it.

## Item-independence check, mechanical

Each item diffed against PLs's twenty-six example bullets. The chess item is not an example in PLs
(it is one in PLp, a different file, which is the accepted co-load). The two coupling controls were
written fresh rather than reusing the two-shops and foxes-and-rabbits examples, precisely so that a
judge cannot match them by name. No chess example has been added to PLs; if this round passes, one
goes in afterwards, so that this round is not scored against an example of its own conclusion.

| id | item | tests | predicted |
|---|---|---|---|
| T1 | find a strong plan in a club-level chess middlegame position | the fix, on the item that produced the miss | **2** |
| T2 | two hospitals each raise nurse pay when the other does, and each finds recruitment harder as the other's pay rises; is either fully staffed at year end | **over-firing guard**: described tendencies, feedback | **3** |
| T3 | a draughts position at move 12; does the player to move have a forced capture sequence that wins a piece | the fix again, many turns, no plan to find | **2** |
| T4 | in a pay negotiation each concession lowers what the other side believes it must settle for; do they agree before the deadline | **over-firing guard**: parties, but tendencies rather than rules | **3** |

## Pre-registered decision rules

1. **The fix works**: T1 = 2 and T3 = 2.
2. **It does not over-fire**: T2 = 3 and T4 = 3.
3. No item more than 1 from prediction.

Failure of rule 1 means the clause is too weak and Pablo's label is still unmet. Failure of rule 2
means it is too strong and must be narrowed or withdrawn, since dragging genuine coupling down to 2
would be a worse defect than the one being fixed. **Rule 2 failing is the outcome to prefer
catching**: T1 was always likely to move once a clause pointed at it, and the honest test of this
change is whether anything else moved with it.
