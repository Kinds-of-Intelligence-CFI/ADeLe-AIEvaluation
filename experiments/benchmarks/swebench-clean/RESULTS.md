# swebench-clean — results

**Question.** Do the PL results on SWE-bench Verified hold on a cleaner task set, which drops the tasks known or
likely to be broken and keeps the hard tasks that some agent has solved?

**Answer.** Yes. On the 443 clean tasks, PLp falls with solve rate at ρ = −0.58 and rises with SWE-bench's human
time-to-fix estimate at ρ = +0.47. These match the earlier 435-task values (−0.57, +0.45). The 35 hard tasks that only
1 to 6 of 135 agents solve read higher on PLp (mean 2.0 against 1.54). PLe (−0.30) and PLs (−0.18) also fall with
solve rate, but they barely vary: 423 of 443 tasks are PLe 3, and 416 are PLs 1.

**Status.** Complete (2026-10-01). 90 new cells (30 tasks × PLp, PLe, PLs), all answered and parsed by Opus 5.5 at
effort low, protocol clean. All six sealed predictions held.

## Design

See `PREREGISTRATION.md`, pushed before any label (`4b0fc41`). The clean set is SWE-bench Verified minus the 29 tasks no
agent of 135 has solved, minus the 3 tasks OpenAI's 2026 audit names as defective, minus the 26 tasks whose tests
UTBoost showed accept wrong patches (one overlap): 443 of 500 (`tasks.csv`, with each exclusion's reason). Labels:
Opus 5.5 low, v2 prompt, PLp text O; 413 tasks reuse existing labels (prompts hash-checked), 30 were labelled here.

## Pre-registered results

From `results/clean.json` (`analysis/analyse.py`, which applies `swebench-pl`'s own `questions()`). Spearman, Fisher-z
95% intervals.

| | clean set (443) | clean, solve rate ≥ 0.05 (408) |
|---|---|---|
| PLp against solve rate | −0.581 [−0.644, −0.511] | −0.570 [−0.637, −0.495] |
| PLe against solve rate | −0.297 [−0.382, −0.208] | −0.303 [−0.391, −0.210] |
| PLs against solve rate | −0.179 [−0.268, −0.086] | −0.164 [−0.257, −0.067] |
| PLp against time to fix | +0.468 [+0.388, +0.542] | +0.458 [+0.374, +0.535] |

All p < 0.001.

**Levels.** PLp 0/1/2/3 = 16/163/256/8. PLe 1/2/3 = 1/19/423. PLs 0/1/2 = 1/416/26. The 35 rarely solved tasks: PLp
1/2/3 = 3/29/3.

**Sealed predictions.**

| prediction | p | outcome |
|---|---|---|
| PLp against solve rate negative, p < 0.05 | 0.97 | held (−0.581) |
| more negative on the 443 than on the 408 | 0.7 | held, by a hair (−0.581 against −0.570) |
| between −0.65 and −0.50 on the 443 | 0.65 | held |
| PLp against time to fix positive, p < 0.05 | 0.95 | held (+0.468) |
| PLe against solve rate negative, p < 0.05 | 0.85 | held (−0.297) |
| PLs has three or more levels and is tested | 0.3 | happened (0, 1, 2), though 416 of 443 are at 1 |
| the 35 rarely solved tasks have higher mean PLp | 0.85 | held (2.0 against 1.54) |
| at least one of them at PLp 3 | 0.6 | held (3) |

## Reading

Removing the known-defective tasks and adding the hard solved tail changes nothing material. The PLp result does not
rest on broken tasks. The hard tail sits higher on PLp, as it should, but almost entirely at Level 2: real SWE-bench
tasks rarely reach PLp 3 or above. PLe and PLs carry little information on this benchmark, since almost every task is at
one level.

## Deviations and caveats

- No deviations.
- Contamination is not addressed (OpenAI 2026): some passes, and some judge labels, may rest on recall.
- The never-solved rule selects on outcome; the OpenAI and UTBoost exclusions do not. OpenAI's full list of audited
  tasks is not public, so other defective tasks may remain among the hard ones.
- Solve rates pool 135 entries from 2023–2026.

## Reproduce

```
python experiments/benchmarks/swebench-clean/make_set.py
uv run --extra annotate --with scipy python experiments/benchmarks/swebench-clean/analysis/analyse.py
```
