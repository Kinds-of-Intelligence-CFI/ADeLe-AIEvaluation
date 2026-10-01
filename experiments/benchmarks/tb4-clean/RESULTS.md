# tb4-clean — results

**Question.** Do the PL rubrics track difficulty on a clean Terminal-Bench 4.0.0 set, without Epoch AI's 30 defective
tasks and the tasks no agent solves?

**Answer.** No. On the 34 fully labelled clean tasks, no planning rubric tracks solve rate or the expert-hour estimate:
PLp +0.12, PLe −0.17, PLs +0.05 against solve rate, none significant. Most tasks sit at PLp 3.

**Status.** Complete (2026-10-01). Descriptive, not a new pre-registered test: these labels and outcomes were already
analysed on all 66 tasks (`tau2-tb4-pl`, `pl-relabel-v2`, `plp-o-relabel`). `uefi-bootkit` has no labels (a safety
classifier handed the judge's calls to another model).

## Design

Terminal-Bench 4.0.0 (66 tasks) minus the 30 tasks Epoch AI's review names as defective and the 7 no trial solves (6
overlap): 35 tasks (`make_set.py` → `tasks.csv`). Solve rate: share of solved trials across 27 Harbor Hub leaderboard
configurations × 5 trials. Labels: PLp text O (`plp-o-relabel` run `o-tb4`), PLe and PLs (`pl-relabel-v2` run `v2-tb4`),
Opus 5.5 low, v2 prompt.

## Results

From `results/clean.json` (`export.py`). Spearman, n = 34.

| | against solve rate | against expert hours |
|---|---|---|
| PLp | +0.12 (p 0.49) | +0.17 (p 0.35) |
| PLe | −0.17 (p 0.35) | +0.16 (p 0.36) |
| PLs | +0.05 (p 0.77) | +0.28 (p 0.11) |

**Levels.** PLp 2/3/4 = 7/25/2. PLe 2/3/4 = 1/16/17. PLs 0/1/2 = 9/9/16.

## Reading

As on the full benchmark, the planning rubrics do not track Terminal-Bench difficulty. Removing the defective tasks
does not change that. Difficulty here seems to come from domain knowledge and strict tests, which these rubrics leave
out by design.

## Caveats

- Small: 34 tasks. Epoch's review was partial, so defective tasks may remain.
- Shareable package with data card: `release/`.
