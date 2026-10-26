# tau2-full — results

**Question.** With the full task as the tau2 judge input (policy, tools, records, customer script, simulator rules,
and how the run is graded), how do the five released rubrics change on the 242 tau2 tasks?

**Answer.** The labels fall, mostly toward Level 1, and every rubric tracks solve rate more strongly.
- **MSc matches Pablo on 14 of 15** (15 within one). The script input gave 10 (relabel-v4-ms); the released labels, 5.
- **Signals (Spearman with solve rate, within domain), released → new:** PLp −0.28 → **−0.48**, PLs −0.15 → −0.34,
  PLe −0.14 → −0.20, MSm −0.12 → −0.21, MSc +0.10 → **−0.32**. All five new signals have p < 0.01.
- **Level shifts.** MSc: Level 1 goes from 2 to 91 tasks, Level 4 from 24 to 0. MSm: Level 1 from 24 to 66. PLp
  spreads out: Level 1 from 28 to 62, Level 3 from 1 to 17.
- **Sealed predictions:** 4 of 4 held.

**Caveat.** The judge now sees the grader's expected actions. Part of the stronger signal may come from that: a task
with many expected write actions is both harder to solve and plainly more demanding. This study cannot separate a
truer demand reading from a leak of difficulty cues. A run without part 3 would tell them apart.

**Status.** Complete (2026-10-26). 1,210 cells; 1,208 labels, all written by Opus 5.5 at effort low, bare digit.
Two banking cells have no label. The label set and the release are unchanged; that waits for Pablo's OK.

## Design

See `PREREGISTRATION.md` (`6ce075d`; Pablo's goal rule `a6106fe`; amendment 1 `8c7e631`). Old labels in
`old_labels.csv`: label set `current` (column `released`; the PL rubrics used the reasoning prompt) and, for MSm and
MSc, `relabel-v4-ms` (column `v4ms`: same rubric text and prompt, script input).

## Run

| run | tasks | cells | labels | note |
|---|---|---|---|---|
| tau2-full | 217 | 1,085 | 1,085 | airline and retail used (690); banking set aside (amendment 1) |
| tau2-full-long | 25 | 125 | 0 | all rejected: lines over 2,000 chars; set aside |
| tau2-full-banking | 55 | 275 | 275 | banking documents as plain text |
| tau2-full-banking-long | 24 | 120 | 118 | chunked judge |

- **Amendment 1.** The first build wrote banking documents as JSON, one line per document body (up to 6,414 chars).
  The Read tool cuts lines over 2,000 chars. The chunked-judge check caught it; the single-read check did not, so
  185 banking labels in `tau2-full` were made on cut text. All 79 banking tasks were re-judged on plain text.
  Airline and retail never had a long line.
- **No label:** banking `task_064` PLe and `task_077` PLs. On both attempts the chunked judge stopped reading at line
  800 of about 803 (the early stop seen in programbench-pl).
- `mass check` passes on all four runs. Weekly usage 19% → 27%, including the set-aside banking work.

## Results

New against released labels. Levels are counts of tasks.

| domain | rubric | n | exact | within 1 | mean shift | released | new |
|---|---|---|---|---|---|---|---|
| airline | MSc | 49 | 20% | 57% | −1.49 | 2:27 3:6 4:16 | 1:35 2:14 |
| airline | MSm | 49 | 63% | 100% | −0.37 | 1:2 2:44 3:3 | 1:17 2:32 |
| airline | PLp | 49 | 73% | 100% | −0.14 | 1:10 2:39 | 1:20 2:26 3:3 |
| airline | PLe | 49 | 88% | 100% | +0.08 | 1:47 2:2 | 1:43 2:6 |
| airline | PLs | 49 | 61% | 100% | −0.39 | 0:1 1:3 2:45 | 0:2 1:20 2:27 |
| banking | MSc | 79 | 51% | 90% | −0.66 | 1:2 2:65 3:6 4:6 | 1:40 2:35 3:4 |
| banking | MSm | 79 | 61% | 99% | −0.10 | 1:20 2:53 3:6 | 1:24 2:53 3:2 |
| banking | PLp | 79 | 76% | 100% | +0.19 | 1:8 2:70 3:1 | 1:5 2:61 3:13 |
| banking | PLe | 78 | 47% | 97% | +0.24 | 1:26 2:33 3:20 | 1:14 2:38 3:26 |
| banking | PLs | 78 | 86% | 99% | −0.10 | 0:2 1:9 2:68 | 0:3 1:15 2:60 |
| retail | MSc | 114 | 84% | 98% | −0.18 | 2:111 3:1 4:2 | 1:16 2:98 |
| retail | MSm | 114 | 63% | 100% | −0.33 | 1:2 2:97 3:15 | 1:25 2:89 |
| retail | PLp | 114 | 75% | 100% | −0.23 | 1:10 2:104 | 1:37 2:76 3:1 |
| retail | PLe | 114 | 97% | 100% | +0.01 | 1:113 2:1 | 1:112 2:2 |
| retail | PLs | 114 | 90% | 100% | −0.09 | 0:2 1:4 2:108 | 0:2 1:14 2:98 |

Against relabel-v4-ms (script input, same MS text and prompt), which isolates the input: MSc 74% exact, mean shift
−0.31; MSm 73% exact, mean shift −0.16. The input alone moves MS labels down.

**Criterion signals** (Spearman with solve rate, within domain, predicted negative; n 241–242):

| rubric | released | relabel-v4-ms | new |
|---|---|---|---|
| PLp | −0.28 (p < 0.001) | — | **−0.48** (p < 0.001) |
| PLe | −0.14 (p 0.03) | — | −0.20 (p 0.002) |
| PLs | −0.15 (p 0.03) | — | −0.34 (p < 0.001) |
| MSm | −0.12 (p 0.07) | +0.11 (p 0.11) | −0.21 (p 0.001) |
| MSc | +0.10 (p 0.13) | −0.14 (p 0.04) | **−0.32** (p < 0.001) |

## MSc against Pablo's 15 labels

| | exact | within 1 | mean (judge − Pablo) |
|---|---|---|---|
| released | 5 | 6 | +1.67 |
| relabel-v4-ms (script) | 10 | 13 | +0.53 |
| **tau2-full** | **14** | **15** | −0.07 |

The one miss: H-14 (airline 22), Pablo 2, new 1. All five airline items that the script put too high (H-03, H-04,
H-07, H-09, H-11) now match him.

## Sealed predictions

| prediction | sealed | result |
|---|---|---|
| MSc exact vs Pablo ≥ 13 of 15 | 0.75 | held (14) |
| more MSc at Level 1 than relabel-v4-ms (29) | 0.75 | held (91) |
| PLp negative signal, p < 0.05 | 0.6 | held (−0.48) |
| MSc negative signal, p < 0.05 | 0.5 | held (−0.32) |

## Files

- `results/analysis.json` (`analysis/analyse.py`); `old_labels.csv`; `build.py`;
  `../mass-annotation/runs/tau2-full*/labels.csv`.
