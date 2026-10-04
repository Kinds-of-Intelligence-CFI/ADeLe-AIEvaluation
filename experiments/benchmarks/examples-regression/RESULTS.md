# examples-regression — results

**Question.** The examples review (`d4ec2ec`) reworded 33 bullets, replaced 9 and dropped 2. Do the changes shift how
the judge labels anything other than the examples themselves?

**Answer.** No. All five rubrics pass the pre-registered rule: no confirmed move of two levels and no drift.
- Battery items unchanged between texts: PLp 30 of 33, PLe 35 of 36, PLs 30 of 36, MSm 32 of 36, MSc 34 of 35.
- Real tasks unchanged against their current label: PLp 48 of 60, PLe 54 of 60, PLs 54 of 60, MSm 54 of 60,
  MSc 60 of 60. That is about the rate at which a rerun under the old text agrees with itself (PLp 16 of 20, PLs 16
  of 20, MSm 17 of 20, PLe 19 of 20, MSc 20 of 20).
- Moves are balanced: up and down are within a few of each other on every rubric (sign tests p ≥ 0.45).
- The one two-level move (battery item M03 on PLs, 1 to 3) was noise: pass 2 gave 2, 2, 2 under both texts.

**Status.** Complete (2026-10-04). 752 pass-1 calls, 6 pass-2 calls and 1 retry (an answer finished by Opus 4.8 after a
classifier stop was set aside and the cell judged again), all counted answers written by Opus 5.5 at effort low.
Verdict: **pass** on PLp, PLe, PLs, MSm and MSc. Sealed predictions: 8 of 9 on the right side.

## Design

See `PREREGISTRATION.md` (pushed before any label, `f1871f8`). Old text `d4ec2ec~1`, new text `d4ec2ec`. Sets: the
lab's 36 battery items under both texts (four voided by the 4-gram check), 60 real tasks under the new text against
their current label (SWE-bench Verified, DeepSWE, Terminal-Bench 4.0, tau2 retail, EQ-Bench 4, CooperBench coop; 10
each), and 20 of them rerun under the old text to measure noise.

## Results

| rubric | battery unchanged | real tasks unchanged | up | down | sign test p | noise rerun unchanged | verdict |
|---|---|---|---|---|---|---|---|
| PLp | 30 / 33 | 48 / 60 | 6 | 9 | 0.61 | 16 / 20 | pass |
| PLe | 35 / 36 | 54 / 60 | 2 | 5 | 0.45 | 19 / 20 | pass |
| PLs | 30 / 36 | 54 / 60 | 7 | 5 | 0.77 | 16 / 20 | pass |
| MSm | 32 / 36 | 54 / 60 | 5 | 5 | 1.00 | 17 / 20 | pass |
| MSc | 34 / 35 | 60 / 60 | 1 | 0 | 1.00 | 20 / 20 | pass |

## Predictions (sealed)

| prediction | p | outcome |
|---|---|---|
| all five pass | 0.55 | yes |
| PLp, PLe, PLs, MSm, MSc pass (0.85, 0.75, 0.75, 0.95, 0.85) | | yes, yes, yes, yes, yes |
| per rubric, ≥ 70% of battery items unchanged | 0.7 | yes (83 to 97 per cent) |
| noise subset changes ≥ 15% of its labels | 0.6 | no (12 of 100) |
| more than 15 cells need pass 2 | 0.15 | no (1) |

## What this means

The reviewed examples change the examples, not the rest of the scale. The full relabel (`../relabel-v2`) goes ahead on
all five rubrics.
