# PLs examples review (draft for Pablo, 2026-10-04)

Every example bullet of the current `PLs.txt` (28, including the three added today), checked against the rubric's
own clauses. Nothing here has been judged yet. Confidence is how sure I am that the problem is real.

## The bar, from v1

The v1 examples (e.g. `data_v1/SNs.txt`, `QLq.txt`, `MCt.txt`) are realistic tasks. Someone could actually be set
them: a vase knocked off a table, compound interest, a recipe scaled up. They are not puzzles built to sit on a
boundary. v1's precision is loose, but no v1 example contradicts its own level text. So the bar here is:
1. **Correct under the rubric's own clauses.** In particular, the coupling must change the answer at Level 3; a loose
   run must flip it at Level 4; at Level 5 a direct-effects model must point the wrong way. And nothing may be settled
   by a stated rule or a standing rate.
2. **Natural.** It reads as a question someone would ask, with the quantities that decide it (v1's flat rate of
   concrete detail), and with no clauses added only to steer the judge.

## Verdicts

| level | example (short) | verdict | why | confidence |
|---|---|---|---|---|
| 0 | finished chess game, who won | keep | the result is read off the move list | — |
| 0 | completed Sudoku, valid? | keep | static check | — |
| 0 | fixed string, max (j−i)(k−j) | keep | fixed configuration; contest-style, like v1's real items | — |
| 1 | wine glass onto tiles | keep | one familiar step | — |
| 1 | short-tempered driver cut up | keep | one step of a described tendency | — |
| 1 | coffee at 70° in an 18° room | keep | direction only, rough model | — |
| 1 | one failing test, repo and shell at hand | keep | your ruling (swe-0461) | — |
| 1 | attached protocol missing | keep | encodes the v14 ruling; odd-looking but deliberate | — |
| 2 | tap into a bath | keep | rate × time | — |
| 2 | three kettles on their own hobs | keep | independent processes | — |
| 2 | forty dominoes | keep | a chain with no return, per the Level 3 note | — |
| 2 | deposit compounding monthly | keep | closed form | — |
| 2 | customer-service refund | keep | stated rules settle each change | — |
| 3 | ring road lane closure | **fix the question** | journey times rise even with no diversion, so the coupling does not change the answer | 0.7 |
| 3 | foxes reach 900 rabbits | keep | without the coupling, rabbits keep increasing; with it, they do not | — |
| 3 | two shops undercutting | **fix** | "undercuts within a day of any change" plus "four points per cut" is a stated rule; the month's margin is arithmetic (Level 2) | 0.6 |
| 3 | cue ball into the pack, any ball pocketed? | **fix the question** | a loose run does not settle it; the best answer is a base rate, which the standing-rate clause keeps low | 0.6 |
| 3 | NEW: retries against a slowing database | **replace** | "do failures rise?" is yes even without the feedback loop | 0.85 |
| 4 | fox–rabbit trough below forty | keep | coupled, and the trough depth needs accuracy | — |
| 4 | drought, four crops, one channel | keep | coupled, and the fine answer needs accuracy | — |
| 4 | two queues, join the shorter, served alternately | **replace** | the stated rules bound the gap between the queues. Arrivals always join the shorter one, so they never widen the gap beyond one, and alternate service never widens it beyond two. So "second queue empty while the first holds three" can never happen. That is an invariant, settled by the rules (Level 2 at most), not by an accurate run | 0.85 |
| 4 | fine billiards shot | keep | precision, per your ruling | — |
| 4 | storm and two valleys | keep | agreed model, precision, per the Level 5 note | — |
| 4 | NEW: LRU cache and batch job | **replace** | LRU is a stated rule. Between two reads of a hot key, about 1,200 other keys are read, against 1,000 slots, so the hit rate is about zero: arithmetic (Level 2), and not a near thing. The judge put it at 3, 3, 4 | 0.9 |
| 5 | profession licensing juniors | **fix** | every stated effect points to "below", so a direct-effects model already gives the answer; nothing stated pulls the other way | 0.7 |
| 5 | two states, mobile launchers | keep | feedback on each side's estimate; no model to trust | — |
| 5 | bank run contagion | keep | the textbook case | — |
| 5 | rail line, rents and tenants | keep | displacement can reverse the direct effect | — |
| 5 | NEW: 300 services, retry policy | **replace** | the direct effect is never stated, so nothing shows the direct-effects model pointing the wrong way; and it repeats the retry mechanism | 0.6 |

Also, as a set: two of the three new examples were about retries, and all three hinged on "no copy". That teaches a
surface cue. The replacements below vary both the mechanism and the reason the system cannot be run first.

## Proposed wordings

New computer-world examples (replacing today's three):

- **Level 3** (file system and database; a decision that has to be made now):
  > Before a four-day weekend, an engineer must decide whether to clear space on a server whose disk is 88 per cent
  > full and fills by about 1 per cent a day. Above 90 per cent, the database on the same disk slows, its requests
  > time out, and each timeout writes an error trace many times longer than a normal log line. Will the disk fill
  > before Tuesday?

  Without the loop: 92 per cent by Tuesday, so no. With it: the traces accelerate once the disk passes 90 per cent
  (after about two days), so yes. A loose run that keeps the loop lands on yes.

- **Level 4** (a service chain near its timeouts; launch traffic cannot be reproduced):
  > A checkout request passes through three services. The middle one gives up on the last after 2 seconds and retries
  > once; the first gives up after 4.5 seconds. Tomorrow's launch traffic cannot be reproduced beforehand, and at that
  > traffic the last service is expected to answer in about 1.8 seconds, slowing further as retries reach it. Will
  > more than one checkout in a hundred fail?

  Latencies sit just under both timeouts, and retries feed back into latency. Leaving out the retry load, or running
  loosely, flips the answer. No rule gives the latency curve; it is a described tendency.

- **Level 5** (a software ecosystem; the direct effect stated, the indirect ones pulling the other way):
  > A package registry will require two-factor sign-in for every maintainer of a popular package. Account takeovers
  > should fall, but some maintainers will hand their packages to strangers or abandon them, and attackers will move
  > to abandoned packages and to look-alike names. Will installs of malicious packages be lower two years later?

  Direct effect: fewer takeovers, so lower. Indirect: transfers, abandonment and attacker substitution could
  outweigh it, and no model of the ecosystem can be trusted to settle it.

Fixes to existing examples (each changes a lab-measured item, so each needs re-measuring):

- **Level 3, ring road:** keep the text; change the question to one the diversion decides:
  > … Does traffic on the ring road fall by a third?

  Without diversion: capacity falls by a third, so yes. With drivers returning as the side streets fill: no.
- **Level 3, two shops:** make the response a tendency, and the question one the reaction decides:
  > Two bakeries on one street sell the same bread, and each has matched the other's price cuts within a day for
  > years. If one cuts its price by 10 per cent, does it end the month with more profit?

  Without the reaction: more customers, more profit. With it: the same customers at a lower margin.
- **Level 3, coarse billiards:** keep it as the coarse half of the billiards pair, with a question a loose coupled
  run settles:
  > A cue ball strikes a tightly racked pack hard and slightly off-centre. Do the balls end up spread over most of
  > the table?
- **Level 4, queues:** drop the join-the-shorter rule, so that the arrival pattern rather than a rule drives the
  gap:
  > Two checkout lanes in a shop, each with its own cashier. Shoppers pick a lane by eye, and the slower cashier
  > takes about 20 per cent longer per shopper. Over a Saturday where arrivals run just under what the two lanes
  > can clear, does the slower lane's queue ever reach twice the length of the other's?

  This still needs checking by hand before testing; see below.
- **Level 5, profession:** add the effect that pulls the other way:
  > … Output per senior rises 30 per cent, and the lower price of the work brings in clients who could not afford it
  > before. Fewer juniors now means fewer seniors in fifteen years. Is the profession's headcount in 2041 above or
  > below today's?

## Open points for you

1. **The queue fix** is the shakiest. "Picks a lane by eye" is a described tendency, so it avoids the invariant.
   But I have not convinced myself that the answer is sensitive rather than a near-certain yes. An alternative is
   to drop the queue example: Level 4 would keep four (fox trough, drought, fine billiards, storm), against v1's
   three.
2. **Scope.** This covers PLs only. The same check (stated rules, standing rates, does the coupling change the
   answer) could be run on PLp, PLe, MSm and MSc. I have not done that.
3. **Testing.** Once you have edited these: rerun the `pls-computer` design on the new text (placement, pairs,
   battery, real tasks; about 220 calls), then relabel PLs on the seven benchmarks (about 1,030 calls). Five
   of the fixes touch examples the lab measured in r57–r68, so the placement set should include them.
