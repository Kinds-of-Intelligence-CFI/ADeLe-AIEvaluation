# examples-review — results

**Question.** Are the example bullets of the eight active v2 rubrics accurate under their own rubric's clauses, and do
they meet the rubric desiderata (natural, v1-like, no glosses or stock phrases, no sibling loading)?

**Answer.** Mostly, but 42 bullets needed changing, and all 42 pass a placement check. Six reviewers (one per PL and MS
rubric, one for the three memory rubrics) checked all 165 bullets against `BRIEF.md`. They reworded 33, replaced 9
and dropped 2 (44 of 165 touched), and flagged 10 for Pablo without changing them. The 42 new or reworded bullets were then judged with the bullet
itself removed from the rubric: 37 land on their level and 5 one level off; none is two or more off. All are adopted.

**Status.** Complete (2026-10-04). 126 Opus 5.5 low calls (3 repeats per bullet; 3 retried after a permission block
stopped the judges from saving), all written by Opus 5.5. Adopted into `src/` on Pablo's standing approval for
example-only changes. Benchmark labels predate these texts.

## What changed, by rubric

| rubric | kept | changed | dropped | flagged | the main problems |
|---|---|---|---|---|---|
| PLp | 12 | 6 | 0 | 5 | Level 0 translation read as building a system; Level 5 research programme put the difficulty in execution; Level 3 trip had no departure date, so the visa did not bind |
| PLe | 11 | 7 | 1 | 1 | Level 4 ledger had a ready-made monthly check; Level 2 tutorial treated "it runs" as a check; three Level 4 bullets ended in the same gloss |
| PLs | 21 | 7 | 1 | 0 | the two-queue and LRU-cache Level 4 bullets were settled by stated rules (an invariant, and arithmetic); at Level 3 the coupling often did not change the answer; at Level 5 the direct effects alone gave the answer |
| MSm | 16 | 1 | 0 | 2 | Level 5 "Leading a negotiation" is steering (MSc's territory) |
| MSc | 14 | 5 | 0 | 0 | the market trader pursues an outcome of its own, so it is Level 4, not 3; the custody example did not say the solver mediates; glosses |
| MMe, MMp, MMs | 36 | 16 | 0 | 2 | the same legal-document task at Level 5 in both MMe and MMs; MMp examples placed against MMp's own text (a five-command Git sequence at 3, a flat checklist at 4); an MMs example that was really simulation |

Flagged items (not changed; for Pablo, and for Marko on MM) are listed in each rubric's `REVIEW.md`. The most
important: PLp's Level 5 synthesis example conflicts with the Level 5 note (a known procedure, retrosynthesis, exists);
MSm's Level 5 seller example carries a gloss and is 69 words; MMp may measure knowledge of procedures rather than
procedural memory, which is a construct question for Marko.

## Placement check (`make_placement.py`, run `exrev-1`)

Each new or reworded bullet was judged against its candidate rubric with that one bullet removed (all other examples
kept). Rule, set before judging: adopt if the median of three is within one level of the bullet's level.

- Exact: 37 of 42.
- One level off: PLp Level 0 translation (reads 1), PLp Level 5 research programme (4, 4, 5), PLs Level 4 checkout
  memory spiral (reads 3), and the MMs chess and mental-multiplication pair (read 5 and 4 at Levels 4 and 5). The
  MMs pair was swapped, so both now sit at the level they read.
- The new computer-world PLs examples: Level 3 retries (3, 3, 3), Level 4 memory spiral (3, 3, 3), Level 5 congestion
  control (5, 5, 5).

## Next

- The benchmark labels were made with the earlier texts. A full relabel of PLp, PLe, PLs, MSm and MSc on the seven
  agentic and three social sets is about 7,000 Opus calls.
- The PLs Level 4 computer example reads 3. A sharper Level 4 computer example is still open.
