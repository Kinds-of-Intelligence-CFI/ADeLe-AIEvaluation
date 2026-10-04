# PLs examples review (2026-10-04)

Rubric: `src/adele/rubrics/data_v2/Paolo_Pablo/PLs.txt` (29 bullets, including the three computer-world bullets
added today). Candidate: `PLs_candidate.txt` here. Bar: `../BRIEF.md`. The first review
(`experiments/benchmarks/pls-computer/EXAMPLES_REVIEW.md`) was taken as input. Every verdict below is re-derived.
Nothing here has been judged.

Counts: 21 kept, 4 fixed, 3 replaced, 1 dropped, 0 changed-and-flagged (ruling examples all kept; see open questions).

## 1. Verdicts

Confidence is how sure I am that the problem is real.

| L | example | verdict | why | conf. |
|---|---|---|---|---|
| 0 | finished chess game, who won | keep | finished record; finding the final state is perception, not scored | (0.2 that replay reads as L2) |
| 0 | completed Sudoku, valid? | keep | static check | |
| 0 | fixed string, max (j−i)(k−j) | keep | fixed configuration (Pablo's zero anchor family) | |
| 1 | wine glass onto tiles | keep | one familiar step | |
| 1 | short-tempered driver cut up | keep | one step of a described tendency | |
| 1 | coffee 70° in an 18° room | keep | direction only; a rough model lands | |
| 1 | one failing test, repo and shell to hand | keep | ruling: swe-0461 at 1; run-and-look clause | |
| 1 | attached protocol missing | keep | ruling: absent referent at 1 (v14) | |
| 2 | tap into a 200 L bath | keep | rate × time | |
| 2 | three kettles, own hobs | keep | independent processes | |
| 2 | forty dominoes | keep | chain with no return (L3 note) | |
| 2 | deposit compounding monthly | keep | closed form (month 44) | |
| 2 | customer-service refund | keep | stated rules settle each change | |
| 3 | ring road lane closure | **fix** | "do journey times rise?" is yes with no diversion at all, so the coupling does not change the answer | 0.7 |
| 3 | foxes reach 900 rabbits | keep | without predation feedback rabbits keep rising; with it they do not | |
| 3 | two shops undercutting | **fix** | "undercut within a day of any change" and "four points per cut" are a stated rule, so the month is arithmetic (L2); starting margin is missing, so it is not even answerable | 0.65 |
| 3 | cue ball into the pack, any ball pocketed? | **replace** | a loose coupled run cannot settle it: the best answer is a break-pocketing base rate (standing-rate clause) or a precise run (L4) | 0.65 |
| 3 | NEW: retries, slowing database | **fix** | "do failures rise?" is yes from doubled traffic alone; the retry loop does not change it | 0.85 |
| 4 | fox–rabbit trough below forty | keep | coupled; trough depth is sensitive (r64: 4) | |
| 4 | drought, four crops, one channel | keep | water, pest and timing couple; "which fail" is fine-grained | |
| 4 | two queues, join shorter, alternate service | **drop** | invariant, settled by the rules | 0.9 |
| 4 | fine billiards | keep | ruling: precision examples at L4 | |
| 4 | storm and two valleys | keep | ruling: precision examples at L4 | |
| 4 | NEW: LRU cache and batch job | **replace** | stated rule; reuse-distance arithmetic gives a hit rate of zero, far from the threshold | 0.9 |
| 5 | profession licensing juniors | **fix** | every stated effect points to "below", so a direct-effects model already answers it; the L5 mark (direct model points the wrong way) is absent | 0.6 |
| 5 | two states, mobile launchers | keep | feedback on each side's waiting estimate; no trusted model | (0.3 base-rate risk, see Q4) |
| 5 | bank run contagion | keep | multiple equilibria; which one is unsettled | |
| 5 | rail line, rents and tenants | keep | displacement can reverse the direct effect (r57: 5) | |
| 5 | NEW: 300 services, retry/timeout policy | **replace** | direct effect never stated, so nothing shows the direct model pointing the wrong way; repeats the L3 retry mechanism | 0.6 |

### The two claims from the first review, re-derived

**Two-queue invariant: confirmed.** Let d be the gap between the queues. An arrival joins the shorter queue, so it
moves d toward 0, or from 0 to 1 on a tie. Service alternates strictly, so between two services of one queue the
other is served once. The widest gap is 2: a tie broken toward queue A, then queue B's turn to be served. The next
event (an arrival to B, or A's service turn) brings it back to 1. "Second queue empty while the first holds three"
needs d ≥ 3, so it never happens, whatever the arrival rate. A brute-force check (200,000 random runs, random tie
breaks, skip-if-empty service) found max gap 2 and no counterexample. The near-critical arrivals that v17 added
to make the example sensitive play no part. The answer is a rule-settled invariant: Level 2 at most.

**LRU claim: confirmed, with a sharper number.** Between two reads of a hot key (one second), the job reads about
900 distinct keys from its 1,200-key cycle and the web process reads its other 299 hot keys. That is a reuse
distance of 1,199 against 1,000 slots, so every hot read misses. The job's own cycle (1,200 > 1,000) also misses
every time. Simulated: hit rate 1.0 at a job rate of 600 or 690 keys a second, 0.0 at 710 and 900. So the answer
("no, about zero") is reuse-distance arithmetic and nowhere near the 90 per cent line. Moving the numbers to the
cliff would not rescue it. A deterministic eviction rule fixes the whole course, so it stays at Level 2 however
exact.

### Where I depart from the first review's proposals

- **Ring road.** Its question "does ring-road traffic fall by a third?" is mis-derived. With no diversion, nobody
  leaves the ring road, so traffic does not fall at all. I keep the scene word for word and change only the question
  to one the return flow decides.
- **Coarse billiards.** Its replacement ("do the balls spread over most of the table?") is a familiar
  one-step outcome (L1 risk), and a loose coupled billiards question is hard to find. I replace it with a mechanical
  loop instead (brake fade), which also adds a mechanical domain that Level 3 lacked.
- **Queues.** Its rewrite ("does the slower lane ever reach twice the other's length?") is a near-certain yes, since
  1 against 2 already counts. I drop the bullet. Level 4 keeps five, and the fox trough and fine billiards already
  show accuracy rather than part count.
- **Computer worlds.** Its drafts run 50 to 64 words. Its Level 3 disk item resembles M3, which failed in
  `pls-computer` because the coupling did not change the answer. Its Level 4 item adds a third retry/timeout
  mechanism. Its Level 5 registry item is good, but it is a social ecosystem more than a computer system (kept
  as a backup, Q2).

## 2. Proposed wordings

**L3 ring road (fix: question only)**
> One of three lanes closes on a ring road carrying 4,000 vehicles an hour. Drivers divert onto parallel streets built for 800, which fill and send some of them back. Once traffic settles, are the side streets any quicker than the ring road?

Without the return flow, the side streets stay quicker. With it, drivers move until neither route gains, so the
answer is no. A loose run of the loop lands there. L3.

**L3 two shops (fix: tendency, not rule)**
> Two bakeries on one street sell the same loaf, and for years each has matched the other's price cuts within a day. One cuts its price by 10 per cent. Does it end the month with more profit?

Without the rival's reaction, the cut takes customers and raises profit. With it, shares stay level at a lower
margin, so the answer is no. The matching is a described tendency, not a stated rule. L3.

**L3 coarse billiards → brake fade (replace)**
> A lorry descends a 12 km mountain pass riding its brakes. Hot brakes grip less, so the driver presses harder, which heats them more. Is it still braking normally near the bottom?

Without the loop (heat does not affect grip), yes. With it, fade feeds on itself, so no. A coarse run lands. L3.

**L3 web service (fix: question; trimmed; can't-run reason is time)**
> A web service retries each failed call three times. Its database already slows at the daily peak, and slow calls fail. A release that doubles traffic ships today, with no time to test it. Will the retries keep failures low?

Uncoupled, retries absorb independent failures (p⁴), so yes. Coupled, retries add load to a database already past
its knee, so failures snowball: no. A coarse run lands. It cannot be run first. L3.

**L4 LRU cache → garbage-collection spiral (replace; can't-run reason is the test rig)**
> A checkout service peaks at 80 per cent of its memory, and requests queued during each garbage-collection pause hold memory until served. Sale-day traffic, 15 per cent higher, is beyond what the test rig can generate. Does the service stall in back-to-back collections?

Without the queue coupling, peak memory is 92 per cent and there is no stall. With it, pauses add memory, which
brings the next collection sooner. Whether that tips into a spiral turns on how close to the limit it runs, so a
loose run can go either way. The model (heap, collector, queue) is standard. Only its accuracy is in question. L4.

**L5 profession (fix: add the upward pull; "within two years" cut to hold length)**
> A profession licenses 12,000 juniors a year. A system passes its certification exam, firms halve junior hiring, and output per senior rises 30 per cent. Cheaper work draws in new clients, but fewer juniors now means fewer seniors in fifteen years. Is the profession's headcount in 2041 above or below today's?

The direct effects say below. Demand drawn in by cheaper work could outweigh them, and no model of the profession can
be trusted to settle which. L5.

**L5 300 services → fleet-wide congestion control (replace; can't-run reason is scale)**
> A phone maker moves a billion devices to a congestion-control scheme that backs off less when packets are lost, so their downloads speed up. Every other flow on the same links now loses more packets, and rival makers can follow. Are typical downloads faster a year later?

The direct effect says faster. Losses imposed on others, rivals copying the scheme and fuller buffers feed back
round after round and could reverse it. No model of the internet at that scale can be trusted to call it. L5.

The three computer-world bullets now differ in mechanism (a retry storm, a memory and collector spiral, network
congestion control). They differ in why they cannot be run first (no time before release, a test rig too small,
the scale of the internet). They share no stock phrase ("no copy" is gone).

## 3. Style numbers

| | bullets | mean words | max words |
|---|---|---|---|
| current | 29 | 30.9 | 62 (LRU cache) |
| candidate | 28 | 30.1 | 51 (profession) |
| changed bullets only | 7 | 42 | 51 |

No semicolons or em dashes in either. Per level, the candidate has 3 / 5 / 5 / 5 / 5 / 5 bullets (current 3 / 5 / 5 / 5 / 6 / 5).
Mechanical check: the candidate's non-bullet lines equal the current file's, and the file endings match.

The changed bullets run above v1's mean of about 26 words, but within this file's L3 to L5 norm (the unchanged
bullets at those levels run 26 to 47). I did not trim the unchanged long bullets, because accuracy rests on their
quantities.

## 4. Open questions for Pablo

1. **Which retry example to keep.** Variety requires one of the two retry bullets to change mechanism. I kept the
   Level 3 one, with a one-line fix, and replaced the Level 5 one (measured 5, 5, 5 in `pls-computer`). The
   alternative is to keep the 300-services bullet with its direct effect stated ("…so that brief slowdowns stop
   causing errors") and give Level 3 a non-retry mechanism. I found no natural non-retry Level 3 computer item
   whose coupling rests on a described tendency rather than a stated rule. Rule-driven ones (least-connections
   routing, LRU) fall to Level 2.
2. **Congestion control at Level 5** is the riskiest new item. A judge may treat it as an agreed model with
   disputed numbers, which is Level 4. Backup: the first review's package-registry item (two-factor sign-in,
   abandonment and attacker substitution), trimmed to about 40 words.
3. **Re-measurement.** Five changes touch items the lab measured: the ring road (r64: 3), the three computer bullets
   (pls-computer) and the profession (r57). All seven new or changed bullets should go through the `pls-computer`
   placement design (stripped-example variant, 3 repeats) before adoption. The garbage-collection item is my
   least certain placement (3 or 4).
4. **Ruling examples, not changed.** Fine billiards and the storm valleys stay at Level 4. One note on the storm
   item: the preamble lowers a task where an approximating model is the solver's to run, and here the solver has
   only station data, so it holds. The two-states item (Level 5, kept) carries a mild base-rate risk. Arms-control
   treaties have a base rate, and the standing-rate clause would pull the item down if a judge sees no mechanism
   doing better. I judged that the use-or-lose feedback carries it. Level 0 chess is kept, with a small risk
   that replaying a move list reads as running stated rules (Level 2).
