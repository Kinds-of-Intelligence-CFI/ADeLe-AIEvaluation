# r60 sealed predictions — PLs v14 floor, and the two MSm cases (2026-08-25)

Judges h/s/o, one item per call, median of three, never Fable. Judges score from the rubric text
only, after r58's meta-line leak.

**Item-independence check (new, after r59's failure):** every item below has been checked against
the text it is scored under. None appears there, verbatim or in paraphrase. The attached-protocol
item is the single exception and is marked as such: it *is* an example in the file, moved from
Level 0 to Level 1 in v14, so its cell measures only whether the move took, not whether the level
is right. It is reported separately and carries no evidential weight for the construct.

## Part A — PLs v14: does the floor move without dragging the static cases up?

| id | item | predicted |
|---|---|---|
| A1 | forecast the yield of the reaction in the linked notebook page (the link is dead and the page is gone) | **1** |
| A2 | how many days of snow did the town record in the decade to 2019, from the attached table | **0** |
| A3 | a completed Sudoku grid is given, is it valid | **0** |
| A4 | the attached-protocol example itself | **1** (moved-example check only, no weight) |

A1 is the real test: a fresh absent-referent item that must land at 1. A2 and A3 are the anchored
static cases that must stay at 0. **The failure mode to watch is A2 or A3 rising**, which would mean
the new Level 1 Note has loosened the floor rather than moved one case off it.

## Part B — MSm, the two cases Pablo asked to be tested

### Case 1: the stated-stance carve against an insincere stance

MSm's exclusions say a stance the other party "has stated outright, together with their reasons,
does not have to be modelled, since the inferring has already been done". That is right for a
cooperative exchange. But where a party is bluffing, negotiating or being polite, the stated stance
is itself a move and the real one still has to be inferred. The exclusion carries no sincerity
condition, so it may zero out exactly the tasks that need mind modelling most.

| id | item | predicted |
|---|---|---|
| B1 | a colleague states plainly which option they prefer and why, and the task uses that preference | **1** |
| B2 | a seller calls it a final offer while the described circumstances make plain it is not, and the task asks what they would actually accept | **4** |

**If B2 comes in at 0 or 1, the exclusion is over-firing** and needs a sincerity condition to match
the one the Level 4 statement already has.

### Case 2: the anti-count guard against the three-attribution interlock

Level 5 requires an interlock of at least three attributions that constrain one another, nested or
distributed. Level 5 also says the number of minds does not place a task there by itself, since
attributions each settleable from its own evidence demand no combination. Those two clauses can
pull against each other, and neither has been tested since the rewrite.

| id | item | predicted |
|---|---|---|
| B3 | five department heads each state their own constraint in writing, and the task is to find a slot that suits all five | **<= 2** |
| B4 | two people only, where what one wants the other to believe about what she already knows must itself be worked out | **5** |

**B3 rising to 5 means the anti-count guard has failed**; B4 falling below 5 means the nested-dyadic
route to the top band does not work, which the rewrite claimed it would.

## Pre-registered decision rules

1. **Floor moves cleanly**: A1 = 1, and A2 = A3 = 0.
2. **Stated-stance carve is not over-firing**: B2 >= 3 while B1 <= 1.
3. **Anti-count guard holds**: B3 <= 3.
4. **Nested dyadic route works**: B4 >= 4.
5. Overall >= 5 of 6 within 1 (A4 excluded from all counts).

Rules 2, 3 and 4 are construct questions as much as wording ones. Whatever they measure goes to
Pablo before any MSm text changes.
