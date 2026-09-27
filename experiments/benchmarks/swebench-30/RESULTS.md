# swebench-30 — results

**Question.** Do the ADeLe rubrics give usable, reproducible task-level demand labels on a real
agentic benchmark (SWE-bench Verified), through the judging path we would use at scale?

**Answer.** Mostly: all pre-registered checks pass, but several rubrics agree only to within a
level. Both judges parsed 100% of cells, Sonnet and Opus are within one level of each other on
at least 90% of tasks for every rubric, and each judge reproduces its own pilot labels (within
one level on 98% of anchor cells). On several rubrics that vary across tasks, however, the two
judges do not order tasks alike (quadratic κ −0.15 to 0.29 for AT, KNf, QLl and AS). All six
sealed predictions hold, including PLp falling with solve rate (ρ = −0.67, n = 30).

**Status.** Final for run `swev30-r4` (2026-09-27).

## Design

See `PREREGISTRATION.md`; the run log is `labels/swev30-r4/RUNLOG.md`.

- **Items.** 30 SWE-bench Verified tasks, 10 per tercile of leaderboard solve rate (seed
  20260926), plus the 14 tasks of the 2026-09-14 pilot as anchors, re-judged on PLp, PLe and PLs
  only (`sample.csv`). Task text: the problem statement only.
- **Rubrics.** 25: 17 from v1 and the 8 active v2 rubrics (v2's MSm replaces v1's).
- **Judges.** Claude Sonnet (`claude-sonnet-5`) and Claude Opus (`claude-opus-5-5`) through the
  `adele-judge` subagent: effort max, tools Read and Write only, no CLAUDE.md, one (task, rubric)
  per call, each sent the exact pre-registered two-line message.
- **Labels.** 792 prompts × 2 judges = 1,584 labels, all parsed (`labels/swev30-r4/`).

## Pre-registered results

From `results/analysis.json` (`analysis/analyse.py`).

| check | criterion | result |
|---|---|---|
| 1. parse rate | ≥ 98% per judge | 100% for both |
| 2. inter-judge agreement, 30 new tasks | within one level on ≥ 80% of tasks, per rubric | 25 of 25 pass (lowest: QLl, 0.90); none flagged |
| 3. test–retest, 42 anchor cells | each judge within one level of its own pilot label on ≥ 80% | Sonnet 0.98 (exact 0.86), Opus 0.98 (exact 0.81) |

Agreement by rubric on the 30 new tasks (shift = Sonnet minus Opus; κ = quadratic-weighted
Cohen's κ, blank when one judge gives every task the same level):

| rubric | family | within 1 | exact | κ | shift |
|---|---|---|---|---|---|
| AS | v1 | 1.00 | 0.43 | 0.29 | −0.57 |
| AT | v1 | 0.97 | 0.27 | −0.15 | +0.57 |
| CEc | v1 | 1.00 | 0.73 | 0.39 | −0.13 |
| CEe | v1 | 1.00 | 0.97 | | −0.03 |
| CL | v1 | 1.00 | 0.77 | 0.51 | +0.03 |
| KNa | v1 | 1.00 | 1.00 | | 0.00 |
| KNc | v1 | 1.00 | 1.00 | | 0.00 |
| KNf | v1 | 1.00 | 0.53 | 0.19 | +0.47 |
| KNn | v1 | 0.97 | 0.97 | | +0.13 |
| KNs | v1 | 1.00 | 1.00 | | 0.00 |
| MCr | v1 | 0.97 | 0.47 | 0.51 | +0.23 |
| MCt | v1 | 1.00 | 0.73 | 0.32 | +0.27 |
| MCu | v1 | 1.00 | 0.70 | 0.67 | +0.10 |
| QLl | v1 | 0.90 | 0.37 | 0.23 | −0.67 |
| QLq | v1 | 1.00 | 0.77 | 0.69 | −0.23 |
| SNs | v1 | 1.00 | 0.97 | | −0.03 |
| VO | v1 | 1.00 | 0.67 | 0.35 | +0.33 |
| MMe | v2 | 1.00 | 1.00 | | 0.00 |
| MMp | v2 | 1.00 | 0.43 | 0.42 | −0.17 |
| MMs | v2 | 0.97 | 0.63 | 0.36 | −0.07 |
| MSc | v2 | 1.00 | 1.00 | | 0.00 |
| MSm | v2 | 1.00 | 1.00 | | 0.00 |
| PLe | v2 | 0.97 | 0.93 | | +0.03 |
| PLp | v2 | 1.00 | 0.47 | 0.51 | +0.33 |
| PLs | v2 | 1.00 | 0.93 | 0.03 | −0.07 |

Sealed predictions (descriptive, not gates), on the 30 new tasks:

| | prediction | result |
|---|---|---|
| P1 | PLe = 3 on ≥ 90% of tasks, each judge | Sonnet 100%, Opus 93%: holds |
| P2 | PLs ≤ 1 on ≥ 90% | 100% and 97%: holds |
| P3 | PLp takes at least three values | 4 values for each judge: holds |
| P4 | MSm and MSc = 0 on ≥ 90% | 100% for both rubrics and judges: holds |
| P5 | Volume rises with human time-to-fix (mean of judges) | ρ = 0.40 [0.03, 0.67], p = 0.03; without the 4 suspect tasks 0.33 (p = 0.11) |
| P6 | PLp falls with solve rate (mean of judges) | ρ = −0.67 [−0.84, −0.37], p < 0.001; without suspect tasks −0.66; Sonnet alone −0.49, Opus alone −0.68 |

Level counts per judge and rubric are in `results/levels.csv`. Six rubrics are 0 on every task
for both judges (KNa, KNc, KNs, MMe, MSc, MSm), and five more put at least 27 of 30 tasks on one
level for both (CEe, KNn, PLe, PLs, SNs), so on this benchmark only about half the rubrics
separate tasks.

## Deviations and caveats

- **Deviations 1–3** changed the judge harness, not the prompts, rubrics or checks: a lean judge
  subagent, no CLAUDE.md with effort pinned, and judge files outside the repo tree. All came
  from dry runs, before any full-run label.
- **Run notes** (`labels/swev30-r4/RUNLOG.md`): one duplicate Opus call (first answer kept); on
  two pylint tasks, 21 Sonnet judges also wrote an identical copy of their answer under a
  truncated file name (set aside); four recorded retries after a usage-limit pause.
- **Within-1 is lenient** when most tasks sit on one or two levels. Read exact agreement and κ
  for the rubrics that vary: AT, KNf, QLl and AS do not rank tasks consistently across judges.
- **n = 30** makes this an annotation-quality check, not a test of criterion validity; that is
  `swebench-pl` (435 tasks).
- **SWE-bench Verified is rated Flawed by Epoch.** 4 new tasks and 3 anchors are suspect (solve
  rate below 0.05) and are kept, with P5 and P6 also reported without them.
- **Pilot anchors** were judged in another session and model version (Opus 5 then, Opus 5.5 now).

## Reproduce

```
python experiments/benchmarks/swebench-30/analysis/analyse.py
```

The numbers above are those committed in `0eaa2e0`. Judges' reasoning and prompts quote task
text and stay out of the repo.
