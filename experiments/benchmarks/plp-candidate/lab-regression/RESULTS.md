# plp-candidate / lab-regression — results

**Question.** Does candidate C change PLp's behaviour on the lab's standing tests?

**Answer.** No. C passes the pre-registered regression: nothing that holds under the current text
breaks under C.
- Placement: all 20 examples got the same level under both texts.
- Minimal pairs: all 5 items got the same level, and all four pair checks hold under both.
- Family diagonal: the 9 rebuilt items pass under both texts. One battery check broke in pass 1:
  M01, a pure MSc item, rose from 2 to 3 on PLp under C. Pass 2 gave it 2 under both texts, so the
  loss was noise.
- Disentanglement: no loss. C removed one leak among the foreign examples.
- No item moved by two levels. 86 of 99 items got the same median under both texts. The 13 moves
  were one level each, 6 up and 7 down.
- **Candidate D** (C's first clause only, "Knowing the established method is knowledge rather than
  planning.") fails its rule by one confirmed two-level move. It also lowers labels more broadly
  than C. See the section on D below.

**Status.** Complete (2026-09-28). C: 600 judge calls, verdict "pass". D: 315 judge calls, verdict
"fail". `PLp.txt` is unchanged; which sentence to adopt is Pablo's decision.

## Design

See `PREREGISTRATION.md`, pushed before any label (`86de254`).

- **Texts.** The current `PLp.txt`, and C: the same text plus one sentence at the end of the
  "What this dimension does not cover" paragraph.
- **Judges.** haiku, sonnet and opus through `adele-judge-low`, one item per call, median of three.
  The rubric was shown as production loads it, examples kept. Set P is the exception: its items
  are the examples, so the examples were stripped.
- **Items.** 99 items, each judged under both texts:
  - P, placement (r25): PLp's 20 examples;
  - F, examples disentangle (r34): 32 PLe, PLs and MSc examples at Levels 3 to 5;
  - M, minimal pairs (r36): 5 items, rebuilt from descriptions;
  - D, family diagonal (r42/r43): 9 items, rebuilt from descriptions;
  - B, battery-v1: 33 of 36 items. The 4-gram check voided E03, P03 and X01.
- **Rule.** A loss is a check that holds under the current text and fails under C. Items behind a
  loss are judged again (pass 2). C passes if no loss and no two-level move is confirmed.

## Pre-registered results

From `results/regression.json` (`analysis/analyse.py`).

| check | holds, current text | holds, C | loss in pass 1 | confirmed |
|---|---|---|---|---|
| Placement (P) | 13 of 20 | the same 13 | none | — |
| Minimal pairs (M) | 4 of 4 | 4 of 4 | none | — |
| Family diagonal, rebuilt items (D) | 9 of 9 | 9 of 9 | none | — |
| Family diagonal, battery's pure items | 12 of 14 | 11 of 14 | M01 above 2 | no |
| Disentanglement, examples (F) | 22 of 32 clean | 23 of 32 clean | none | — |
| Disentanglement, battery (separation, co-occurrence, anchors, mid-band) | 18 of 22 | 18 of 22 | none | — |
| All checks | 78 of 101 | 78 of 101 | 1 | 0 |

- **Pass 2.** M01 is "a colleague has refused to swap shifts; bring him to swap". In pass 1 it had
  haiku 3, sonnet 2, opus 2 under the current text (median 2), and 3, 3, 2 under C (median 3). In
  pass 2 both texts got 3, 2, 2 (median 2). The loss is not confirmed.
- **Moves.** No item moved by two levels or more.
- **Verdict: pass.**

The checks that fail under the current text fail under C too. They are listed in the exploratory
section below.

**Also reported.**
- Per set, medians equal under both texts: P 20 of 20, M 5 of 5, D 8 of 9, F 25 of 32, B 28 of 33.
- Sign test over single-judge labels: 27 lower under C, 21 higher, p = 0.47. No shift.
- C's judges quoted the new sentence in 5 of 297 answers. One of them is on a moved item
  (F-PLs-L4-4, 2 to 1).

**Sealed predictions.**

| prediction | p | outcome |
|---|---|---|
| C passes | 0.5 | happened |
| no confirmed loss: placement / pairs / diagonal / disentanglement | 0.75 / 0.9 / 0.8 / 0.9 | all held |
| no confirmed two-level move | 0.95 | held |
| if C loses anything, it is a downward move | 0.9 | moot: no confirmed loss. The one pass-1 loss was upward. |
| the listed at-risk items move | — | none moved: contest programming (P-L3-3, D-PLp4), route and picking (P01, P04), timetabling, packing and meal plan all stay at 3 |
| more single-judge labels lower under C than higher | 0.75 | held (27 against 21) |
| that shift is significant | 0.3 | did not happen (p = 0.47) |
| C removes at least one leak in F | 0.35 | happened: F-PLs-L5-4 (rail line), 3 to 2 |
| the new sentence is quoted in 10 to 40 per cent of C's answers | 0.6 | failed: 1.7 per cent |
| the current text matches the stored lab medians on 80 per cent or more | 0.6 | failed narrowly: 37 of 47 (79 per cent) |

## Exploratory results

Not pre-registered. From `results/exploratory.json` (`analysis/exploratory.py`).

- **The carve rarely fires on designed items.** Sonnet quoted it four times and haiku once. Opus
  never did. The word "knowledge" appears in 16 per cent of C's answers and 8 per cent of the
  current text's. So this regression shows C is safe on the lab's items. It does not show C does
  much there. Its intended effect is on real tasks, where it moved `html-js-filter`.
- **Placement under the current text: 7 of 20 examples miss their level**, with examples stripped.
  Both texts give the same answer, so this is about `PLp.txt` as it stands, not about C.
  - Top band, as in r25: ML-paper replication 4 → 3, synthesis route 5 → 4, research programme 5 → 4.
  - Level 0 real-time translation → 3. Its gloss ("the difficulty is linguistic") was removed in the
    2026-08-25 example pass. Without it, and without the other examples, judges read the task as
    planning.
  - Level 0 temperature conversion → 1, Level 1 covering letter → 2, Level 2 one-day city plan → 3.
  - In production the examples are shown, so the examples themselves are safe. The misses say
    what the level statements alone do not carry.
- **Leaks under the current text: 10 of 32 foreign examples score PLp 3 or more.** Six are MSc
  examples at Levels 3 to 5; r34 accepted that negotiation co-loads plan search. The others are
  PLe's patent claims (Level 3), untested codebase (Level 4) and Mars landing (Level 5), and PLs's
  rail line (Level 5). r34 ended with 4 leaks into PLp, all MSc. The examples and judges have
  changed since, so this is a pointer for desideratum 6, not a measured regression.
- **Battery checks that fail under both texts.** MSc>>PLp and PLs>>PLp do not separate at gap 3
  (as in the lab's July runs for MSc). X02 (flooded cave) scores PLp 3, not 4. D08 scores 3
  against a registered 1, as in July.
- **Current text against the stored lab medians.** 37 of 47 match. The 10 others differ by one
  level, 7 up and 3 down (mean +0.09).
- **Judges.** Single-judge labels equal between texts: opus 89 per cent, sonnet 89 per cent, haiku
  74 per cent. Haiku reads higher (mean level 2.2, against 1.7 for opus and 1.8 for sonnet).
- **Cost.** Mean final context and time per call: opus 6.5k tokens and 14 s, sonnet 8.3k and
  32 s, haiku 9.4k and 51 s. The weekly limit went from 88 to 93 per cent during the run, other
  sessions included.

## Candidate D: the first clause only

Pre-registered as an amendment before any label of D (`f53e9cb`). D alone was judged (`labreg-d1`,
297 calls), against the current-text labels of `labreg-r1`. Pass 2 (`labreg-d2`, 18 calls) re-ran
three items under both texts. From `results/regression_d.json` (`analysis/analyse.py --candidate d`).

**Verdict: fail.** One two-level move repeated in pass 2. No loss repeated.

| item | pass 1: current → D | pass 2: current → D | outcome |
|---|---|---|---|
| F-MSc-L3-4, haggling with a market trader | 3 → 1 | 2 → 1 | the two-level move repeats in the same direction: confirmed |
| M-A1, loading ten identical boxes | 1 → 0 (so A1 to A3 "rises") | 1 → 1 | loss not repeated |
| F-PLs-L4-3, two queues at one counter | 2 → 3 (a new leak) | 3 → 2 | loss not repeated |

- The confirmed move goes toward a cleaner label. A foreign example stops leaking into PLp.
- **D lowers labels more broadly than C.** Single-judge labels: 30 lower under D, 15 higher
  (p = 0.036). All three judges lean lower: opus 8 against 3, sonnet 7 against 4, haiku 15 against
  8. Under C only haiku leaned lower. The lean is on the battery (10 lower, 2 higher) and on
  placement (5 lower, 0 higher).
- **The planning checks hold.** All four minimal-pair checks, all nine family-diagonal items and
  all placement checks hold under D once pass 2 is counted. One placement check improves: the
  covering letter reaches Level 1 (from 2).
- **Medians equal between texts:** 83 of 99 (C: 86). D quoted in 4 of 297 answers.

**Sealed predictions for D.**

| prediction | p | outcome |
|---|---|---|
| D passes | 0.45 | failed: one confirmed two-level move |
| if D loses anything, it is a downward move | 0.9 | moot: no confirmed loss. The confirmed move was downward. |
| D is quoted in 10 per cent or more of answers | 0.5 | failed: 1.3 per cent |
| more single-judge labels lower under D | 0.8 | held (30 against 15) |
| that shift is significant | 0.4 | happened (p = 0.036) |

**Reading.** The shorter sentence is broader, as expected. It lowers PLp by one level on many items,
mostly items with little planning, and it does not break the planning checks. By the pre-registered
rule it is not "unchanged", so it is not the tested option. C is.

## Deviations and caveats

- **Haiku ran without an effort setting.** The pre-registration says effort low for all three.
  The harness applies no effort to Haiku 4.5, and its transcripts record none. Opus and sonnet ran
  at low.
- **No noise control.** There is no current-against-current run. Pass 2 guards the checks only. 13
  of 99 medians moved between texts, and the sign test finds no direction, which fits judge noise.
- **Rebuilt items.** M and D are new texts written from the rounds' descriptions. They measure the
  designs, not the original items.
- **Void items.** The 4-gram rule removed P03, the battery's only Level 5 PLp item, and X01, a
  co-occurrence item.
- **Placement design.** One example per call, with all examples stripped. r25 put the whole pool
  in one call.
- **Classifier stops.** Six opus calls were stopped by a safety classifier (five in pass 1, one in
  pass 2). Opus 5.5 still wrote five of those answers. The sixth, the Mars-landing example under the
  current text, wrote nothing and was judged once more, as pre-registered. Every answer was written
  by its registered model.
- **Protocol.** Every judge got the exact two-line message, ran from `~/Developer/ADELE`, had no
  CLAUDE.md attached, and touched only its own two files. One Write cut off by a classifier stop
  targeted a folder and wrote nothing.

## Reproduce

```
python experiments/benchmarks/plp-candidate/lab-regression/analysis/analyse.py
python experiments/benchmarks/plp-candidate/lab-regression/analysis/exploratory.py
```

The numbers above are those committed with this file. Prompts and the judges' reasoning stay out of
the repo (`data/annotations/labreg-r1/`, `labreg-r2/`). The exploratory carve counts need them.
