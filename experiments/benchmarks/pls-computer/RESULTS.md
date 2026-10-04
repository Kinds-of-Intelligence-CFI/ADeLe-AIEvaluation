# pls-computer — results

**Question.** Do three computer-world examples at PLs Levels 3 to 5 (systems that cannot be run first) place where
intended, and leave the rest of PLs unchanged?

**Answer.** Yes. The candidate passes the pre-registered rule, and all three examples are kept.
- Placement: under the current text, which lacks them, the Level 3 and Level 5 examples got their own level
  (3, 3, 3 and 5, 5, 5). The Level 4 example got 3, 3, 4 (median 3, within one).
- Minimal pairs: no loss. Runnable against not runnable splits as intended under both texts (M1 1 vs 3, M2 1 vs
  4). Code traced by hand stays at 2, and at 1 with an interpreter, under both texts.
- Battery: 27 of 36 items unchanged, 4 up and 5 down. One two-level move (B-D02) was noise: pass 2 gave it
  0 in all six labels, under both texts.
- Real tasks: no upward drift and no two-level move. The examples lower PLs on DeepSWE: 12 of the 13 sampled
  tasks released at Level 2 fall to 1.

**Status.** Complete (2026-10-04). 209 pass-1 calls and 6 pass-2 calls, all written by Opus 5.5 at effort low,
no classifier stops. Verdict by the pre-registered rule: **pass**. `PLs.txt` is unchanged; adoption needs
Pablo's OK. Sealed predictions: 18 of the 20 not set at 0.5 on the right side (misses: Level 5 placed exactly, at 0.4; M3 holds, at 0.6).

## Design

See `PREREGISTRATION.md`, pushed before any label (`0fc261b`). One judge (Opus 5.5 low, v2 prompt). Four sets:
the new examples under the current text (P, 3 repeats), four minimal pairs (M, both texts, 3 repeats), the lab's
36-item battery (B, both texts, 1 label), and 60 sandboxed real tasks (R, candidate once against the released
label; 20 also rerun under the current text to measure judge noise).

## Results

**Placement (P).**

| example | target | labels | verdict |
|---|---|---|---|
| web service retries, no copy to try a release on | 3 | 3, 3, 3 | exact |
| LRU cache shared by a batch job, cannot be rehearsed | 4 | 3, 3, 4 | within one, kept |
| 300 services, new retry policy, no copy at scale | 5 | 5, 5, 5 | exact |

**Minimal pairs (M).** Medians, current text / candidate.

| pair | a | b | holds |
|---|---|---|---|
| M1 queue backlog: test copy (a) vs live only (b) | 1 / 1 | 3 / 3 | yes / yes |
| M2 deadlock: replica (a) vs one live run (b) | 1 / 1 | 4 / 4 | yes / yes |
| M3 filling disk: uncoupled (a) vs feedback (b) | 2 / 2 | 2 / 2 | no / no |
| M4 Python function: by hand (a) vs interpreter (b) | 2 / 2 | 1 / 1 | yes / yes |

M3 fails under both texts, so it is not a loss. The item is flawed. The disk fills within three weeks with or
without the feedback (40 GB at 2 GB a day takes 20 days), so the coupling never changes the answer. The rubric
puts that at Level 2.

**Battery (B).** 27 of 36 unchanged, 4 up and 5 down (sign test p = 1.0). One move of two levels: B-D02 (a train
journey from a fixed timetable), 0 under the current text and 2 under the candidate in pass 1. Pass 2: 0, 0, 0
under both texts. Not confirmed.

**Real tasks (R).** Candidate against the released label.

| benchmark | n | same | up | down |
|---|---|---|---|---|
| SWE-bench Verified | 20 | 18 | 0 | 2 |
| DeepSWE | 20 | 4 | 4 | 12 |
| TB 4.0 | 20 | 16 | 2 | 2 |
| all | 60 | 38 | 6 | 16 |
| noise: current text rerun | 20 | 14 | 3 | 3 |

No move of two levels. More tasks go down than up (sign test p = 0.053), so there is no upward drift. Levels over
the 60 tasks: released 0/1/2 = 5/30/25, candidate 5/40/15.

**The DeepSWE shift (not predicted).** Of the 13 sampled DeepSWE tasks released at Level 2, 12 fall to 1. In the
noise rerun, 2 of the 7 DeepSWE tasks moved down, so part of this shift is judge noise, but most is not. The
candidate's reasons lean on "the solver can run the system and look" and on the Level 1 failing-test example,
where the released reasons often used the Level 2 rule-governed example. The new examples sharpen the line between
running a system and simulating it in one's head, which is Pablo's ruling. It also means PLs labels on runnable
code tasks would fall if the examples are adopted: DeepSWE had 59 of 90 tasks at Level 2.

**Quotes.** Candidate answers name a new example on 21 per cent of the pair items, 3 per cent of the battery items
and none of the real tasks.

## Predictions (sealed)

| prediction | p | outcome |
|---|---|---|
| candidate passes | 0.75 | yes |
| all three examples kept | 0.6 | yes |
| Level 3 exact | 0.6 | yes |
| Level 4 exact | 0.45 | no (3) |
| Level 5 exact | 0.4 | yes |
| each within one (0.9, 0.9, 0.85) | | yes, yes, yes |
| a miss is low rather than high | 0.8 | yes (Level 4 at 3) |
| M1, M2, M3, M4 hold under the current text (0.7, 0.6, 0.6, 0.75) | | yes, yes, no, yes |
| no confirmed loss | 0.85 | yes |
| at least one gain | 0.3 | no |
| battery: no confirmed two-level move | 0.9 | yes |
| battery: at least 75 per cent unchanged | 0.7 | yes (27 of 36, exactly 75 per cent) |
| real tasks: at most 10 per cent up | 0.7 | yes (6 of 60) |
| drift | 0.1 | no |
| real tasks: no confirmed two-level move | 0.9 | yes |
| noise subset changes at least 15 per cent | 0.5 | yes (6 of 20) |
| answers name a new example on 5 to 30 per cent of real tasks | 0.5 | no (0) |

I did not predict a downward shift on any benchmark.

## What this means

- The examples work. They place where intended, and the current rubric already reads computer worlds that cannot be
  run first as Levels 3 to 5 (M1b, M2b). So the rubric covered José's case; it did not show it.
- They change nothing else that the lab tests.
- They make PLs a little lower on runnable code tasks, mainly DeepSWE. If they are adopted, PLs on the seven
  benchmarks should be relabelled (1,026 calls) so that the released labels match the text.

## Files

| | |
|---|---|
| candidate | `PLs_candidate.txt` |
| items | `items.csv`, `pairs.csv` |
| labels | `labels/plsc-1/`, `labels/plsc-2/` (`labels_long.csv`, `writers.csv`, `run.json`) |
| analysis | `analysis/analyse.py` → `results/analysis.json` |
