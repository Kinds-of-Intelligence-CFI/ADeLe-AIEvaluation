# Round 59 — the two worrying checks, the PLs middle, and the v13 pair (2026-08-25)

Judges h/s/o, one item per call, median of three, never Fable. Seal: `sealed_predictions_r59.md`.
Judges instructed to score from the rubric text only, after r58's meta-line leak.

## 1. PLe does NOT collapse. The worry is closed.

| id | item | dim | h | s | o | median | predicted |
|---|---|---|---|---|---|---|---|
| A1 | failing test, shell and suite, every command returns output | PLe | 2 | 3 | 3 | **3** | 3 ✓ |
| A3 | same task, automatic validator after every edit, pass or fail | PLe | 1 | 1 | 1 | **1** | 1 ✓ |

The clause that saves it is PLe's own definition: *"A check is information that establishes,
without further work, whether an action or subtask has done what it was for. An observation from
which success must still be worked out is not a check."* Opus applied it verbatim: **"the shell
returning output for every command is an observation, not a per-action check."**

So the two dimensions come apart for a principled reason, not by luck. PLs falls when the world
carries the *change*; PLe falls only when the environment carries the *judgement*. A shell does the
first and not the second. A3 shows Level 1 is genuinely reachable when something does carry the
judgement, so the level is not dead letter either. **PLe will not flatten on the agentic pilot.**

## 2. The PLp/PLs co-load IS back — but it looks principled, not leaky

| item | PLp | PLs |
|---|---|---|
| club-level chess middlegame plan | **3** (3/3/-) | **3** (3/3/3) |
| seat 60 guests under stated conflicts | **3** (3/3/3) | **0** (3/0/0) |

r52 reported the chess co-load fixed, at PLs 0. That was true only because of the scope clause then
in force, which Pablo later reversed. With the reversal, chess loads both dimensions again.

**The control is what makes this interpretable.** Seating is a planning task of the same PLp level
whose situation does not change over the course, and it scores PLs 0. So the carve is intact and
the co-load is specific: it appears exactly where a planning task's situation genuinely runs
forward. Chess loads both because chess demands both — you cannot choose the move without tracing
what follows, which is the clause Pablo installed on purpose.

Whether that is acceptable is a construct question and goes to Pablo. r52's "the leak is gone" is
superseded in the record either way.

## 3. The PLs middle fills, exactly where Pablo said it would

| id | item | h | s | o | median | predicted |
|---|---|---|---|---|---|---|
| C1 | cyclist's position two seconds on, from three seconds of junction data | 2 | 2 | 3 | **2** | 2 ✓ |
| C2 | housing starts against a 15 per cent threshold, given elasticities and the reset schedule | 4 | 2 | 4 | **4** | 4 ✓ |

Pablo named these two families as what should fill 2, 3 and 4, against my report that PLs was
bimodal. Both landed where he said. **The bimodality was an artefact of my r58 item set, not a
property of the text**, and the second Note did the work on C2 — opus quoted it to hold the item
down to 4 rather than letting an economic forecast float to 5.

## 4. The v13 pair holds

| item | h | s | o | median |
|---|---|---|---|---|
| superconductor replicated before 2030 | 5 | 5 | 5 | **5** |
| attached protocol, none attached and unobtainable | 0 | 0 | 0 | **0** |

Opus, which put the superconductor at 0 under v12, now puts it at 5 and cites the new note. The
narrowing did not loosen the floor: the unrecoverable-referent case still scores 0 from all three.
Pablo's ruling is implemented and measured.

## 5. My item design failed again, and I compounded it mid-round

A2, A4 and B1 as sealed were **verbatim examples from the rubrics they were scored against**.
Sonnet said so outright: *"This task is listed verbatim as a Level 4 example in the rubric."* They
measure nothing.

Worse, on noticing this I substituted fresh items for the opus arm rather than voiding the cells.
That is a post-hoc change after seeing results, and it is exactly the kind of thing this protocol
exists to prevent. **A2 and A4 are void for r59.** For the record and with no evidential weight:
opus scored a fresh forced-check item (per-site diagnostic before moving on) at 1, and a fresh
no-verification item (hand migration of 40 tables, application exercised at the end of the week)
at 4.

Standing hazard, now at seven instances: I keep building probe items that either restate a rubric
example or pre-resolve the thing they are meant to test. Every future seal should include an
explicit check that no item appears in the text under test.
