# pl-relabel-v2 — results

**Question.** Do the pre-registered PL results of `swebench-pl` and `tau2-tb4-pl` hold when the labels
are made with the v2 prompt?

**Answer.** The PLp results hold. PLp against solve rate is −0.58 on SWE-bench Verified (was −0.57)
and −0.38 within tau2 domains (was −0.33). PLe weakens on SWE-bench (−0.29, was −0.46), because the
v2 prompt puts almost every SWE-bench task at PLe 3. Terminal-Bench still shows no significant link
for any rubric. Its PLp estimate moved from −0.06 to +0.25 (p = 0.15).

**Status.** Complete (2026-09-30). 2,085 of 2,088 cells labelled by Opus 5.5 at effort low. The three
`uefi-bootkit` cells have no label: a safety classifier stopped Opus 5.5 on both attempts. Of the
seven sealed predictions, five held and two failed.

## Design

See `PREREGISTRATION.md`, pushed before any label (`af5f147`).

- Opus low relabelled PLp, PLe and PLs with `build_annotation_prompt_v2`. The 1,194 SWE-bench cells
  come from `swepl-r1-low`, and the 132 gate cells are reused from `natural-prompt`. tau2 has 696
  cells and Terminal-Bench 4.0.0 has 198.
- Every old prompt was rebuilt from the same rubric and task text and matched its stored hash, so
  only the prompt differs.
- The analysis reruns each study's own pre-registered functions on the new labels. The old
  Opus-low results sit beside them.

## Pre-registered results

From `results/relabel.json` (`analysis/analyse.py`). The rho values are Spearman, with Fisher-z 95%
confidence intervals.

**SWE-bench Verified, 435 solvable tasks** (`swebench-pl` questions)

| | v2 prompt | old prompt |
|---|---|---|
| PLp against solve rate | −0.58 [−0.64, −0.50] | −0.57 |
| PLe against solve rate | −0.29 [−0.38, −0.20] | −0.46 |
| PLs against solve rate | −0.18 [−0.27, −0.08] | −0.14 |
| PLp against time to fix | +0.48 [+0.40, +0.55] | +0.45 |

All four keep the predicted sign, with p < 0.001.

**tau2, 232 tasks** (`tau2-tb4-pl` Q1, within domain, combined over domains)

| | v2 prompt | old prompt |
|---|---|---|
| PLp | −0.38 [−0.49, −0.26] | −0.33 |
| PLe (airline and banking only) | −0.11 [−0.29, +0.07] | −0.24 |

- PLp stays negative in each domain: airline −0.57, banking −0.41, retail −0.28.
- PLe is no longer significant within domain.
- Pooled over domains (a robustness check), PLe is still −0.46 (was −0.53).

**Terminal-Bench 4.0.0, 33–34 tasks with results** (`tau2-tb4-pl` Q1 and Q2)

| | v2 prompt | old prompt |
|---|---|---|
| PLp against solve rate | +0.25 [−0.10, +0.55] | −0.06 |
| PLe against solve rate | −0.23 [−0.53, +0.13] | not tested (too little variation) |
| PLs against solve rate | +0.11 [−0.24, +0.44] | −0.08 |
| PLp against expert hours | +0.21 [−0.15, +0.52] | +0.19 |

None is significant, as before.

**Agreement, new against old labels**

| | exact | within one level | mean shift |
|---|---|---|---|
| SWE-bench PLp (442 tasks) | 0.81 | 1.00 | +0.07 |
| SWE-bench PLe | 0.82 | 1.00 | +0.18 |
| SWE-bench PLs | 0.94 | 1.00 | +0.03 |
| tau2 PLp (232) | 0.91 | 1.00 | −0.05 |
| tau2 PLe | 0.85 | 1.00 | −0.07 |
| tau2 PLs | 0.94 | 1.00 | +0.03 |
| Terminal-Bench PLp (65) | 0.89 | 1.00 | +0.02 |
| Terminal-Bench PLe | 0.82 | 1.00 | −0.06 |
| Terminal-Bench PLs | 0.72 | 1.00 | 0.00 |

Opus low agrees with itself about 88% of the time under the same prompt. So on tau2 and
Terminal-Bench, the change of prompt is within repeat noise. On SWE-bench it is not, for PLp and PLe.

**Sealed predictions**

| prediction | p | outcome |
|---|---|---|
| SWE-bench PLp against solve rate negative, p < 0.05 | 0.95 | held (−0.58) |
| SWE-bench PLp within ±0.10 of −0.57 | 0.7 | held (−0.58) |
| SWE-bench PLe within ±0.10 of −0.46 | 0.6 | failed (−0.29) |
| tau2 PLp within domain within ±0.10 of −0.33 | 0.65 | held (−0.38) |
| Terminal-Bench PLp within ±0.20 of zero | 0.75 | failed (+0.25) |
| SWE-bench PLe mean shift above +0.10 | 0.7 | held (+0.18) |
| SWE-bench PLp mean shift within ±0.10 | 0.7 | held (+0.07) |

## Exploratory results

- **PLe on SWE-bench is nearly constant now.** 415 of 435 tasks are at PLe 3, 19 at 2 and 1 at 1.
  This is the reading `natural-prompt` found on the gate. Running the reproduction or the tests is
  an elected check that is easy to apply, which the rubric puts at Level 3. The old labels had 93
  tasks at PLe 2 and 339 at 3. With only 19 left at 2, the correlation falls. So PLe separates
  tasks on tau2 (pooled −0.46) but hardly on SWE-bench.
- **On tau2, the v2 prompt moves labels slightly down, not up.** On banking, PLe went from 2 to 1 on
  14 tasks, and 9 tasks moved each way between 2 and 3. PLp went from 2 to 1 on 11 tasks across the
  three domains, and up on 4. On SWE-bench the shift was upward. So the prompt does not simply
  raise labels; it changes how the rubric's conditions are applied.
- **Terminal-Bench PLp.** The sign change comes from 6 tasks off the mode among 33. It is within the
  old estimate's interval (−0.40 to +0.29), so it may be noise. Terminal-Bench remains
  uninformative for PLp, and it is not contamination-clean (`tau2-tb4-pl`).
- **Cost.** 2,088 calls plus 5 repeats. The 5-hour meter went from 3% to 74% for the first 1,890
  cells (about 0.04% per call, including relays and my own turns), then 0% to 11% for Terminal-Bench.
  The weekly meter went from 4% to 15%, about 11 points against 12 budgeted. Mean final context was
  7.2–7.5k tokens and about 14 s per call.

## Deviations and caveats

1. **Analysis bug, fixed before reading the results.** The agreement table merged old and new
   labels on task id and rubric. tau2 task ids repeat across domains ("0" is in airline and in
   retail), so the tau2 rows were cross-matched (n = 330 instead of 232). The benchmark is now part
   of the key. SWE-bench and Terminal-Bench were unaffected, and so were all correlations.
2. **Relay slips.** Two SWE-bench cells were never sent, and one was sent twice. The two were sent
   in a separate relay; for the repeat, the first answer is the label. See `RUNLOG.md`.
3. **`uefi-bootkit`.** A safety classifier stopped Opus 5.5 on all three cells, and Claude Code
   finished them with Opus 4.8, on both attempts. Per the design, these cells have no label (as in
   `tau2-tb4-pl`).
4. **Pause.** Terminal-Bench was judged after the 5-hour reset (11:32 UTC), about 2.5 hours after
   tau2, to keep a margin on the meter. Judge snapshots cannot be pinned, so drift within a day is
   possible but unlikely to matter.
5. **Environment.** The analysis ran with `uv run --extra annotate --with scipy --with statsmodels`.
   The repo's dependencies do not include `scipy`.

Caveats: the old labels were made on 2026-09-27/28, so the comparison mixes the prompt effect with
any judge drift since then (see `natural-prompt`). There is no human reference; "holds" means the
conclusions agree, not that either labelling is right.

## Reproduce

```
python experiments/benchmarks/pl-relabel-v2/analysis/analyse.py
```

The numbers above are those committed with this file. The judges' answers stay out of the repo.
