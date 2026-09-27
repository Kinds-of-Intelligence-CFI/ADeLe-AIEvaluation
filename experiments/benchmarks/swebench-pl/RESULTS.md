# swebench-pl — results

**Question.** Do the v2 planning rubrics (PLp Planning, PLe Action control and execution, PLs
Simulating) track how hard SWE-bench Verified tasks are, across the 435 tasks that leaderboard
agents solve at least sometimes?

**Answer.** Yes for PLp and PLe; PLs cannot be tested on this benchmark. PLp falls with the
leaderboard solve rate (Spearman ρ = −0.63) and rises with SWE-bench's human time-to-fix
estimate (ρ = +0.45); PLe falls with solve rate (ρ = −0.53); PLs is 1 on 433 of the 435 tasks.
One judge (Opus at medium effort).

**Status.** Preliminary (2026-09-27): the pre-registered analysis is done except one robustness
check, Q1 and Q2 without the tasks a test-validity audit flags; the audit has not run.

## Design

See `PREREGISTRATION.md` (predictions locked by Pablo before any analysis).

- **Items.** The 435 SWE-bench Verified tasks (HF `princeton-nlp/SWE-bench_Verified`, revision
  `c104f840`) whose solve rate over the 135 entries of `SWE-bench/experiments` (`40f164d`) is at
  least 0.05. Task text: the problem statement only. List and solve rates in `sample.csv`.
- **Judge.** Claude Opus (`claude-opus-5-5`) through the `adele-judge-medium` subagent: effort
  medium, tools Read and Write only, no CLAUDE.md, one (task, rubric) per call.
- **Effort gate (step 1).** On the 132 PL cells of `swebench-30`, medium effort matched Opus at
  max effort exactly on 86% of cells and within one level on all of them (κ 0.91; PLe 0.16 lower
  on average). All four gate conditions passed (`results/gate.json`, `RUNLOG.md`).
- **Labels.** 1,326 cells (132 gate, 1,194 scale-up), all parsed: `labels/swepl-gate/`,
  `labels/swepl-r1/`.

## Pre-registered results

From `results/analysis.json` (`analysis/analyse.py`). Spearman ρ with a Fisher-z 95% CI;
a prediction is supported when p < 0.05 with the predicted sign.

| test | n | ρ [95% CI] | p | prediction |
|---|---|---|---|---|
| Q1: PLp vs solve rate | 435 | −0.630 [−0.688, −0.564] | 2e−49 | supported |
| Q1: PLe vs solve rate | 435 | −0.533 [−0.601, −0.457] | 3e−33 | supported |
| Q1: PLs vs solve rate | 435 | −0.089 [−0.182, 0.005] | 0.06 | not supported; only 2 tasks are off level 1, so uninformative |
| Q2: PLp vs human time-to-fix | 435 | +0.445 [0.362, 0.521] | 2e−22 | supported |
| Q1/Q2 without the 37 step-1 tasks | 398 | PLp −0.627, PLe −0.527, PLs −0.093; Q2 +0.444 | | unchanged |
| Q1/Q2 without tasks the test audit flags | | | | pending |

Level counts (`results/pl_levels.csv`):

| level | 0 | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|---|
| PLp | 23 | 264 | 144 | 4 | 0 | 0 |
| PLe | 0 | 13 | 104 | 318 | 0 | 0 |
| PLs | 1 | 433 | 1 | 0 | 0 | 0 |

## Exploratory results (not pre-registered)

From `results/exploratory.json` (`analysis/exploratory.py`), added after the pre-registered
analysis ran.

- **Mean solve rate by PLp level:** 0.92, 0.68, 0.39, 0.14 at levels 0–3 (23, 264, 144 and 4
  tasks).
- **Against the benchmark's own difficulty label:** SWE-bench's human time-to-fix bucket gives
  ρ = −0.40 with solve rate, weaker than PLp's −0.63.
- **Not a proxy for simple size measures:** PLp's partial correlation with solve rate is −0.625
  given problem-statement length, −0.550 given time-to-fix, −0.585 given the reference patch's
  size, and −0.536 given all three.
- **Within repositories:** from −0.57 (sympy, 65 tasks) to −0.75 (matplotlib, 27); django
  (204 tasks) −0.63.

## Opus at low effort (step 1c, exploratory)

Added after the pre-registered analysis, at Pablo's choice of Opus at low effort for later runs:
every solvable task was judged again at low effort (`results/low_effort.json`,
`analysis/low_effort.py`).

- **Agreement with medium effort**, 435 tasks: exact 0.88 and within one level 1.00 over 1,305
  cells (κ 0.92); PLp 0.86, PLe 0.82, PLs 0.98. Low is 0.06 of a level higher on average.
- **The main results hold, slightly weaker:** PLp against solve rate −0.57 (medium −0.63), PLe
  −0.46 (medium −0.53), PLp against human time-to-fix +0.45 (medium +0.45).

## Deviations and caveats

- **Deviations:** none. One amendment before any analysis: predictions locked, test-validity
  robustness check added.
- **One judge.** Medium effort reproduced max effort well on the gate, but every label here is
  one Opus call.
- **Contamination.** Opus may recognise SWE-bench issues and recall their fixes (OpenAI showed
  frontier models reproducing reference patches from task ids), so PLp could partly encode
  remembered solution complexity. Controlling for patch size does not rule this out; tasks newer
  than the judge (SWE-rebench, Terminal-Bench 4.0) would.
- **Broken tests.** Epoch rates SWE-bench Verified Flawed. The solve-rate cut removes most
  broken tasks but not all: `django__django-14725`, which OpenAI's audit names as broken, has a
  solve rate of 0.074. The pending audit addresses this.
- **Solve rates** come mostly from late-2025 leaderboard entries.

## Reproduce

```
python experiments/benchmarks/swebench-pl/analysis/analyse.py       # needs the HF dataset
python experiments/benchmarks/swebench-pl/analysis/exploratory.py   # also needs data/instances/
```

The numbers above are those committed in `dc7cd01`. Judges' reasoning and prompts quote task
text and stay out of the repo.
