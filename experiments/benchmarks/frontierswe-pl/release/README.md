---
license: mit
pretty_name: ADeLe — FrontierSWE v2 with demand labels
tags:
  - ai-evaluation
  - frontierswe
  - demand-annotation
  - adele
configs:
  - config_name: default
    data_files: labels_wide.csv
  - config_name: labels
    data_files: labels.csv
  - config_name: tasks
    data_files: tasks.csv
  - config_name: rubrics
    data_files: rubrics.csv
---

# ADeLe — FrontierSWE v2 with demand labels

All 34 tasks of FrontierSWE v2, with per-task outcomes, flags and ADeLe demand labels on the 19 clean
tasks. 95 labels (PLp 19, PLe 19, PLs 19, MSm 19, MSc 19). Built at commit `b528ffa` of
[ADeLe-AIEvaluation](https://github.com/Kinds-of-Intelligence-CFI/ADeLe-AIEvaluation) (branch `agentic-v2`,
`experiments/benchmarks/frontierswe-pl/`).

## What is in it

| file | one row per | what |
|---|---|---|
| `labels_wide.csv` (default) | task | outcomes, flags, `keep`, one column per rubric (empty for dropped tasks) |
| `labels.csv` | task × rubric | the level, with the judge, prompt and answer hashes and the run that made it |
| `tasks.csv` | task (all 34) | the same outcomes and flags, without labels |
| `rubrics.csv` | rubric text | code, name, generation, file, sha256 of the exact text, and the runs that used it |

Task text is not included (the task repository has no licence). Join on `instance_id` with
[`Proximal-Labs/frontier-swe-v2`](https://github.com/Proximal-Labs/frontier-swe-v2), tag `v2.0.0` (commit `da83f84`).

## Tasks, outcomes and flags

**Outcomes** come from the frontierswe.com aggregates (site of 2026-09-30): 18 models, each with mean and best reward
over its runs (usually 5), all with the `proximus` harness at maximum effort. Rewards are continuous in [0, 1].
Per-run rewards are not public. A (task, model) cell is solved when the model's mean reward is ≥ 0.9.
`solve_rate_<t>` is the share of the 18 models solved at threshold t (0.9 primary; 0.75, 0.5);
`best_solve_rate_0.9` uses each model's best run; `mean_reward` is run-weighted over all models; `best_any` is the
best run of any model.

- **Clean set (`keep`).** Tasks some model's best run brings to 0.9: 19. The other 15 are never
  solved at that threshold. No external defect review exists, so nothing else is dropped.
- **`github_issue`** (flag): an open issue on the task repository names the task (`github_issues`).
- **`version_suffix`** (flag): the task.toml name has a -patched/-hardened/-qemu/-impl suffix the site lacks, so the
  site's results may predate a task fix.

## How the labels were made

- **Rubrics.** ADeLe v2: PLp (Planning), PLe (Action control and execution), PLs (Simulating), MSm (Mind modelling and
  social cognition), MSc (Communication and social interaction); each a 0–5 scale. `rubrics.csv` pins the exact text.
- **Runs.** All labels come from relabel-v2, made after the examples review of 2026-10-04 (`d4ec2ec`). PLp cells at
  Levels 3–5 were then re-judged in relabel-v3, after the synthesis example moved to Level 4 (`d6cc9ca`); the new
  label replaces the old one. Every clean task was at PLp 3–5 in relabel-v2, so every PLp label here comes from
  relabel-v3. Each row of `labels.csv` names its run. The merge is one-sided: only cells at 3–5 were re-judged, so PLp leans slightly down
  ([relabel-v3/RESULTS.md](https://github.com/Kinds-of-Intelligence-CFI/ADeLe-AIEvaluation/blob/agentic-v2/experiments/benchmarks/relabel-v3/RESULTS.md)).
- **Judge.** Claude Opus 5.5 at effort low, run as a Claude Code subagent, one call per task and rubric. Only answers
  written by that model are kept.
- **Prompt.** ADeLe's v2 annotation prompt: the rubric and what the agent sees (`instruction.md`, plus the README it
  cites), a short written assessment, then the level. The judge never sees tests, solutions or agent attempts.
- **Missing labels:** none on the clean tasks. The 15 dropped tasks have no labels here. Their PLp was labelled
  with an earlier text (amendment 1 of the study, in RESULTS.md); those labels were not relabelled and are not
  released.

## What the labels show

PLp on the 19 clean tasks: Level 3 on 19 of 19. With so little spread, PLp cannot be tested against solve rate
here (one level: not testable). MSm is 0 on 18 of the 19 clean tasks and MSc on all 19: FrontierSWE involves no other
party. Full results:
[frontierswe-pl/RESULTS.md](https://github.com/Kinds-of-Intelligence-CFI/ADeLe-AIEvaluation/blob/agentic-v2/experiments/benchmarks/frontierswe-pl/RESULTS.md).

## Limits

- Small: 34 tasks, 18 models, outcomes from aggregates only.
- Trials the site's QA panel flagged for cheating are scored 0 and cannot be told apart from honest zeros.
- The task repository has no licence and the site states no terms; redistributing task text needs permission.
- One judge, one sample per cell.

## License and citation

Labels and metadata: MIT, like the ADeLe code. Cite the ADeLe paper
([arXiv:2503.06378](https://arxiv.org/abs/2503.06378)) and FrontierSWE (Proximal Labs).
