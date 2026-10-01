# frontierswe-pl — results

**Question.** Do the PL rubrics track difficulty on FrontierSWE v2, a benchmark of long (up to 20 h) open-ended
engineering and research tasks with current-generation outcomes?

**Answer.** Not testably. The judge puts 18 of the 19 clean tasks at PLp 3 and one at PLp 4, so PLp barely varies.
Its correlation with solve rate is negative but far from significant (ρ = −0.20, p = 0.42; −0.34 against mean reward,
p = 0.15). PLe and PLs show nothing.

**Status.** Complete (2026-10-01). 57 cells (19 tasks × PLp, PLe, PLs), all labelled by Opus 5.5 at effort low,
protocol clean. All five sealed predictions came out as the higher-probability side.

## Design

See `PREREGISTRATION.md`, pushed before any label (`1175f15`). FrontierSWE v2 (34 tasks). A (task, model) cell is solved
when the model's mean reward over its runs is ≥ 0.9 (Pablo); task solve rate = share of 18 models solved. Clean set:
tasks some model's best run brings to 0.9: 19. Prompt: the instruction plus the README it cites. Labels: run
`frontierswe-pl` of `adele mass`, Opus 5.5 low, v2 prompt, PLp text O.

## Pre-registered results

From `results/analysis.json` (`analysis/analyse.py`). Spearman, Fisher-z 95% intervals; n = 19.

| | ρ | 95% CI | p |
|---|---|---|---|
| PLp against solve rate at 0.9 | −0.20 | [−0.60, +0.29] | 0.42 |
| PLp at 0.75 / 0.5 | −0.20 / −0.33 | | 0.42 / 0.17 |
| PLp against mean reward | −0.34 | [−0.70, +0.14] | 0.15 |
| PLe against solve rate at 0.9 | +0.29 | [−0.20, +0.66] | 0.23 |
| PLs against solve rate at 0.9 | −0.01 | | 0.97 |

**Levels (19).** PLp 3/4 = 18/1. PLe 3/4 = 14/5. PLs 1/2 = 9/10. On the 14 unflagged tasks PLp is constant (all 3).

**Sealed predictions.**

| prediction | p | outcome |
|---|---|---|
| PLp against solve rate at 0.9 negative, p < 0.05 | 0.2 | did not happen (p 0.42) |
| PLp ρ negative in sign | 0.55 | held (−0.20) |
| at least 15 of 19 tasks at PLp 3 or higher | 0.75 | held (19) |
| at least one task at PLp 4 or higher | 0.6 | held (1) |
| neither PLe nor PLs significant | 0.8 | held |

## Reading

FrontierSWE tasks are all large projects, and the PLp scale treats them alike: Level 3 covers almost everything. With
19 tasks and one off-mode label, this benchmark cannot test PLp. Like Terminal-Bench, it says the top of the PLp scale
is coarse for long agentic work.

## Deviations and caveats

- No deviations.
- Outcomes are model means over 5 runs from the site's aggregates; per-run rewards are not public (robots.txt).
- The 0.9 threshold leaves a coarse outcome (7 distinct solve rates; 3 kept tasks at 0).
