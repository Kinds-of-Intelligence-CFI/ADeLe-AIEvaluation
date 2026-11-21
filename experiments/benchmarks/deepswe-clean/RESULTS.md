# deepswe-clean — results

**Question.** Do the PL rubrics track difficulty on DeepSWE v1.1, a long-horizon coding benchmark with current-generation
per-trial outcomes and an external defect review?

**Answer.** PLp does, weakly: on the 90 clean tasks it falls with solve rate at ρ = −0.22 (p = 0.04). Tasks at PLp 2 are
solved in 64% of trials, tasks at PLp 3 in 54%. The result holds without the configurations run after the timeout
change (−0.24) and without GPT-6 Astra (−0.23), and weakens to p = 0.08 without the 4 tasks with open community
issues. PLe and PLs show nothing (ρ ≈ 0).

**Status.** Complete (2026-10-01). 270 cells (90 tasks × PLp, PLe, PLs), all labelled by Opus 5.5 at effort low. One
answer was rejected for a protocol breach (the judge wrote twice) and relabelled on retry. Four of six sealed predictions
held.

## Design

See `PREREGISTRATION.md`, pushed before any label (`1175f15`). DeepSWE v1.1 (113 tasks) minus the 23 tasks Epoch AI's
review names as defective: 90 tasks. Every task is solved at least once. Solve rate: share of scored trials resolved
across 70 configurations (28 models × effort, up to 4 trials). Labels: run `deepswe-clean` of `adele mass`, Opus 5.5
low, v2 prompt, PLp text O.

## Pre-registered results

From `results/analysis.json` (`analysis/analyse.py`). Spearman, Fisher-z 95% intervals.

| | clean (90) | clean, no community issue (86) |
|---|---|---|
| PLp against solve rate | −0.22 [−0.41, −0.01], p 0.041 | −0.19 [−0.39, +0.03], p 0.084 |
| PLp, configurations before the timeout change | −0.24, p 0.026 | −0.21, p 0.056 |
| PLp, without GPT-6 Astra | −0.23, p 0.028 | −0.20, p 0.062 |
| PLe against solve rate | +0.00 | −0.02 |
| PLs against solve rate | −0.00 | −0.06 |

**Levels (90).** PLp 2/3 = 24/66. PLe 3/4 = 81/9. PLs 1/2 = 31/59.

**Sealed predictions.**

| prediction | p | outcome |
|---|---|---|
| PLp against solve rate negative, p < 0.05 | 0.65 | held (−0.22, p 0.041) |
| PLp ρ between −0.60 and −0.20 | 0.55 | held, at the edge (−0.216) |
| most tasks at PLp 2 or 3, Level 3 at least as common as on SWE-bench Verified | 0.7 | held (all at 2 or 3; 66 of 90 at 3) |
| PLe against solve rate negative, p < 0.05 | 0.35 | failed (+0.00) |
| PLs against solve rate negative, p < 0.05 | 0.25 | failed (−0.00) |
| PLp's ρ with each sensitivity rate within 0.05 of the primary | 0.9 | held (−0.235, −0.232) |

## Reading

DeepSWE tasks are SWE-bench-like but larger: the judge puts 73% of them at PLp 3, against 2% of SWE-bench Verified.
PLp still separates easier from harder tasks, but with only two levels in use the correlation is modest. Residual false
negatives from the verifier (Epoch's review was partial) add noise to the outcome and likely weaken it.

## Deviations and caveats

- No deviations.
- Datacurve states no terms for its trial data, so only per-task solve rates are committed (`tasks.csv`).
