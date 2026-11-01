# relabel-v4-ms — results

**Question.** With the social rubrics adopted on 2026-10-25 (`b05ddf3`: MSc v4b, the MSm candidate), how do the
released MSm and MSc labels change?

**Answer.** Most labels stay the same: 94.5% of MSc cells and 91.5% of MSm cells. The changes sit in a few places,
and nearly all go down.
- **tau2, MSc.** The old Level 4 labels mostly go: 24 → 3. Level 1 grows from 2 to 29. This is the refusal fix the
  new text was written for. MSc now falls with solve rate (ρ −0.14, p 0.04); before it did not (+0.10).
- **tau2, MSm.** Level 3 drops from 24 to 4. The weak negative signal (−0.12, p 0.07) is gone (+0.11, ns).
- **CooperBench, MSm.** About half the Level 3 labels move to 2 (111 → 57 at Level 3).
- **Everything else** barely moves. The coding and terminal sets stay at 0. EQ-Bench 4 MSm is unchanged (119 of 120 at 4).
- **Against Pablo (tau2 MSc).** The new labels match his 15 labels 10 times (13 within one); the released labels
  matched 5 times. This is below ms-candidate's 15 of 15, and the input explains it: production keeps tau2's frozen
  script text, and ms-candidate found that v4b on the script matches only 9 of 15. On the full task it matched 15 of 15.

**Status.** Complete (2026-10-26). 2,826 cells in five runs; 2,824 labels, all written by Opus 5.5 at effort low.
The label set and the releases are unchanged; that waits for Pablo's OK.

## Design

See `PREREGISTRATION.md` (`dc0e04a`). Bare-digit prompt (`v2-noreason`), one repeat, the mass runner's retries.
Old labels: `old_labels.csv`, the MSm and MSc labels of label set `current` at `dc0e04a` (2,823 cells; it was written
after the run had started, from the unchanged `labelsets/current.toml`). No pass/fail rules; this is production.

## Run

| run | cells | labels | rejected attempts |
|---|---|---|---|
| relabel-v4-ms | 2,032 | 2,030 | 4 classifier swaps, 1 double write |
| relabel-v4-ms-long | 26 | 26 | 2 (judge answered before reading the whole prompt) |
| relabel-v4-ms-eqbench4 | 240 | 240 | 0 |
| relabel-v4-ms-cooperbench | 480 | 480 | 0 |
| relabel-v4-ms-gamearena | 48 | 48 | 0 |

- Every rejected cell was re-sent. All but two got a label on the retry.
- The two cells with no label are ProgramBench `zip-password-finder` (MSm and MSc). The safety classifier stopped
  Opus 5.5 on both attempts, and Opus 4.8 wrote the answers (set aside). These two cells had no released label either.
- TB-Science `protein-active-learning` MSc had no released label; it now has one (0).
- `mass check` passes on all five runs.
- One orchestrator slip: a shell `cd` moved the session's working directory for a few seconds during round 1. It
  was moved back at once. `check` verifies every judge's working directory and passed, so no judge ran in the wrong place.
- Weekly usage 11% → 19% (about 8 points; the estimate was 13).

## Results

New against released labels, by set and rubric. Level counts are old → new.

| set | rubric | n | exact | within 1 | mean shift | levels old | levels new |
|---|---|---|---|---|---|---|---|
| tau2-airline | MSc | 49 | 65% | 73% | | 2:27 3:6 4:16 | 1:7 2:36 3:4 4:2 |
| tau2-airline | MSm | 49 | 88% | 100% | | 1:2 2:44 3:3 | 1:1 2:48 |
| tau2-banking | MSc | 79 | 72% | 94% | | 1:2 2:65 3:6 4:6 | 1:19 2:52 3:7 4:1 |
| tau2-banking | MSm | 79 | 63% | 100% | | 1:20 2:53 3:6 | 1:28 2:48 3:3 |
| tau2-retail | MSc | 114 | 96% | 98% | | 2:111 3:1 4:2 | 1:3 2:111 |
| tau2-retail | MSm | 114 | 85% | 100% | | 1:2 2:97 3:15 | 1:1 2:112 3:1 |
| tau2 (all) | MSc | 242 | 82% | 92% | −0.29 | 1:2 2:203 3:13 4:24 | 1:29 2:199 3:11 4:3 |
| tau2 (all) | MSm | 242 | 79% | 100% | −0.11 | 1:24 2:194 3:24 | 1:30 2:208 3:4 |
| CooperBench | MSc | 240 | 93% | 100% | −0.07 | 0:110 1:10 2:120 | 0:120 1:7 2:113 |
| CooperBench | MSm | 240 | 75% | 100% | −0.23 | 0:120 2:9 3:111 | 0:120 2:63 3:57 |
| EQ-Bench 4 | MSc | 120 | 88% | 100% | −0.02 | 3:77 4:43 | 3:79 4:41 |
| EQ-Bench 4 | MSm | 120 | 100% | 100% | 0.00 | 4:119 5:1 | 4:119 5:1 |
| GameArena | MSc | 24 | 96% | 100% | −0.04 | 0:15 1:5 4:3 5:1 | 0:15 1:5 4:4 |
| GameArena | MSm | 24 | 71% | 100% | −0.04 | 0:5 1:6 2:5 3:7 4:1 | 0:4 1:8 2:5 3:6 4:1 |
| TB-Science | MSc | 69 | 100% | 100% | 0.00 | 0:69 | 0:70 |
| TB-Science | MSm | 70 | 99% | 100% | −0.01 | 0:69 2:1 | 0:69 1:1 |
| Terminal-Bench 4.0 | MSc | 35 | 97% | 100% | +0.03 | 0:35 | 0:34 1:1 |
| Terminal-Bench 4.0 | MSm | 35 | 100% | 100% | 0.00 | 0:34 1:1 | 0:34 1:1 |
| FrontierSWE | MSc, MSm | 19 | 100% | 100% | 0.00 | MSm 0:18 2:1, MSc all 0 | same |
| SWE-bench Verified | MSc, MSm | 443 | 100% | 100% | 0.00 | all 0 | all 0 |
| ProgramBench | MSc, MSm | 129 | 100% | 100% | 0.00 | all 0 | all 0 |
| DeepSWE | MSc, MSm | 90 | 100% | 100% | 0.00 | all 0 | all 0 |

All cells pooled: MSc 94.5% exact, 98.6% within one (1,411 cells); MSm 91.5% exact, 100% within one (1,412 cells).
The largest moves: MSm 3→2 (78 cells, mostly CooperBench and tau2) and MSc 4→1 or 4→2 (19 cells, tau2).

**Criterion signals** (Spearman with solve rate, predicted negative; tau2 within domain, as `ms-benchmarks`):

| set | rubric | old | new |
|---|---|---|---|
| tau2 | MSc | +0.10 (p 0.13) | **−0.14 (p 0.04)** |
| tau2 | MSm | −0.12 (p 0.07) | +0.11 (p 0.11) |
| Terminal-Bench 4.0 | MSc | one level | −0.10 (p 0.56; one task off 0) |
| others | | one level, or one task off the mode: not testable | unchanged |

The social sets have no solve rate. Their mean levels: CooperBench MSm 1.46 → 1.24, MSc 1.04 → 0.97; EQ-Bench 4 MSm
4.01 → 4.01, MSc 3.36 → 3.34; GameArena MSm 1.71 → 1.67, MSc 0.92 → 0.88.

## MSc against Pablo's 15 tau2 labels

His labels from `ms-candidate/human_labels.csv` (with his two revisions: H-08 to 2, H-12 to 1), matched to the tasks
through `msc-l4-note/human_items.csv`.

| | exact | within 1 | mean (judge − Pablo) |
|---|---|---|---|
| released labels | 5 of 15 | 6 | +1.67 |
| new labels | **10 of 15** | 13 | +0.53 |
| new labels, against his first labels | 8 of 15 | 13 | +0.40 |

| item | task | Pablo | old | new |
|---|---|---|---|---|
| H-01 | retail 0 | 2 | 2 | 2 |
| H-02 | airline 6 | 1 | 4 | 1 |
| H-03 | airline 45 | 1 | 4 | **4** |
| H-04 | airline 38 | 1 | 3 | **3** |
| H-05 | retail 7 | 2 | 2 | 2 |
| H-06 | airline 46 | 1 | 4 | 1 |
| H-07 | airline 43 | 1 | 3 | 2 |
| H-08 | retail 11 | 2 (first 3) | 3 | 2 |
| H-09 | airline 1 | 1 | 4 | 2 |
| H-10 | retail 9 | 2 | 2 | 2 |
| H-11 | airline 27 | 1 | 3 | 2 |
| H-12 | banking task_006 | 1 (first 2) | 1 | 1 |
| H-13 | airline 0 | 1 | 4 | 1 |
| H-14 | airline 22 | 2 | 2 | 2 |
| H-15 | airline 4 | 1 | 4 | 1 |

Every miss is too high, and all five are airline tasks. H-03 and H-04 stay two or more levels above Pablo. In
ms-candidate, v4b matched 15 of 15 on the full task and 9 of 15 on the script; here, on the script, 10 of 15. So the
gap is the input, not the rubric. ms-candidate already concluded that the full task is the better input for MSc.
Whether to change the tau2 input for MSc is Pablo's call; this run kept the script, as pre-registered.

## Files

- `results/analysis.json` (`analysis/analyse.py`); `old_labels.csv`;
  `../mass-annotation/runs/relabel-v4-ms*/labels.csv` (pushed in `47c7d8d`).
