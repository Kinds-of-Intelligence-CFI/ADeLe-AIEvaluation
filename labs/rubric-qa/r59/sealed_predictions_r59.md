# r59 sealed predictions — the two worrying checks, plus the PLs mid-band (2026-08-25)

Texts under test: `/home/user/plfix/PLe.txt`, `PLp.txt`, `PLs.txt` (PLs at v13).
Judges h/s/o, one item per call, median of three, never Fable. Judges are told to score from the
rubric below the `#!` line only, after r58's leak.

## Part A — does PLe suffer the executability collapse that flattened PLs?

The worry: the mechanism that took PLs to 0-2 on the agentic pilot is that tools carry the work.
PLe Level 1 is "the environment checks at every step". A harness that returns output after every
tool call may satisfy that, in which case PLe flattens the same way and we lose a second dimension
to the same argument.

The reason it might not: PLe defines a check as "information that establishes, without further
work, whether an action or subtask has done what it was for", and adds that "an observation from
which success must still be worked out is not a check". A shell returning a stack trace is an
observation, not a check. If that definition holds, PLe is safe and the two dimensions come apart
for a principled reason.

| id | item | dim | predicted |
|---|---|---|---|
| A1 | fix a failing test in a repository, with a shell and the suite, every command returning its output | PLe | **3** |
| A2 | change a customer's order through tools that report the success or failure of each call | PLe | **2** |
| A3 | the same repository task, but an automatic validator runs after every action and says pass or fail | PLe | **1** |
| A4 | extend a large codebase that has no test suite | PLe | **4** |

A2 carries Pablo's own label: he put tau-bench items at 2 on PLe. A3 is the ceiling case that shows
Level 1 is reachable at all. **The collapse signal is A1 or A4 coming back at 1 or 2.**

## Part B — has the PLp/PLs co-load returned?

r52 reported the co-load fixed: the chess plan went to PLs 0 because of the scope clause then in
force. Pablo reversed that scope, so simulating done in order to act is scored again. No family
diagonal has been run since, so the fix may have quietly undone itself.

| id | item | dim | predicted |
|---|---|---|---|
| B1 | find a strong plan in a club-level chess middlegame | PLp | **3** |
| B2 | the same chess item | PLs | **3** |
| B3 | seat 60 guests across 8 tables under stated conflicts and preferences | PLp | **3** |
| B4 | the same seating item | PLs | **0** |

**B2 is the whole point.** I predict 3, not 0: tracing a move's consequences is exactly what the
reversed scope says to score, so the co-load should be back. If B2 comes in at 3 or above while B1
is also 3, PLp and PLs are double-counting chess-shaped tasks and r52's "the leak is gone" is
superseded. B3/B4 are the control: a planning task with nothing changing over the course must stay
at PLs 0, or the reversal has broken the carve rather than merely restored the co-load.

## Part C — Pablo's item types for the PLs middle

r58 left PLs bimodal on forecasting, 2 or 5. Pablo named the two families that should fill in.

| id | item | dim | predicted |
|---|---|---|---|
| C1 | from three seconds of positions and speeds at a junction, where is the cyclist in two seconds | PLs | **2** |
| C2 | given a 2-point policy-rate rise, stated elasticities and the mortgage reset schedule, do housing starts fall more than 15 per cent within eight quarters | PLs | **4** |

C2 is the test of Pablo's reading that the bimodality was an artefact of my item set: an economic
question with an agreed model and a threshold answer should land at 4, not 5, under the second Note.

## Pre-registered decision rules

1. **PLe does not collapse**: A1 >= 3 and A4 >= 4. Failure means PLe has the same defect as PLs and
   is a construct question for Pablo, not a wording fix.
2. **PLe Level 1 is reachable**: A3 <= 1.
3. **PLe human anchor holds**: A2 = 2.
4. **The co-load question is answered either way**: report B1 and B2 as measured. If both >= 3, the
   co-load is back and r52's finding is superseded in the record.
5. **The planning carve survives the reversal**: B4 <= 1.
6. **The PLs middle fills**: C1 <= 3 and C2 = 4. If C2 comes back 5, the bimodality is a property of
   the text rather than of my item set, and Level 4 needs a positive characterisation for
   forecasting-shaped tasks.
7. Overall >= 8 of 10 within 1.

Nothing here licenses a text change on its own. Rules 1, 4 and 6 are construct questions and go to
Pablo whatever they measure.
