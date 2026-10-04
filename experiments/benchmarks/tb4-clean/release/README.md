---
license: mit
pretty_name: ADeLe — Terminal-Bench 4.0.0 clean set with demand labels
tags:
  - ai-evaluation
  - terminal-bench
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

# ADeLe — Terminal-Bench 4.0.0 clean set with demand labels

A subset of Terminal-Bench 4.0.0 that drops the tasks an external review found defective, and the tasks no current
agent solves, with ADeLe demand labels. 35 tasks, 105 labels. Built at commit `b528ffa` of
[ADeLe-AIEvaluation](https://github.com/Kinds-of-Intelligence-CFI/ADeLe-AIEvaluation) (branch `agentic-v2`,
`experiments/benchmarks/tb4-clean/`).

## What is in it

| file | one row per | what |
|---|---|---|
| `labels_wide.csv` (default) | clean task | category, expert-hour estimate, trials and solve rate, one column per rubric |
| `labels.csv` | clean task × rubric | the level, with the judge, prompt and answer hashes and the run that made it |
| `tasks.csv` | Terminal-Bench 4.0.0 task (all 66) | solve counts, Epoch's defect type, exclusion reasons, and `keep` |
| `rubrics.csv` | rubric text | code, name, generation, file, sha256 of the exact text, and the runs that used it |

Task text is not included (Terminal-Bench tasks carry a no-training canary). Join on `instance_id` with Terminal-Bench
4.0.0 (Hugging Face `harborframework/terminal-bench`, tag `v4.0.0`).

## How the set was built

All 66 tasks, minus two groups (a task is excluded if it is in either):

| excluded | tasks | why | source |
|---|---|---|---|
| defective | 30 | Epoch AI's review lists each by name: 19 accept wrong solutions (false positive), 11 reject correct ones (false negative). | [Epoch AI, Terminal-Bench 4.0.0 review, 2026-09-04](https://epoch.ai/data/benchmark-reviews-documentation/included-benchmarks) |
| never solved | 7 | No trial of any of the 27 leaderboard configurations solves it. Six are also defective. | Harbor Hub leaderboard, exported 2026-09-27 |

35 tasks remain. Epoch's review stopped once its threshold was reached, so the other tasks were not all inspected.

**Solve rate** is the share of solved trials across the 27 current-generation leaderboard configurations (5 trials
each). **Expert hours** is the task author's estimate from each task's `task.toml`.

## How the labels were made

- **Rubrics.** ADeLe v2 planning family: PLp (Planning), PLe (Action control and execution), PLs (Simulating), each a
  0–5 scale; `rubrics.csv` pins the exact text by sha256.
- **Runs.** All labels come from relabel-v2, made after the examples review of 2026-10-04 (`d4ec2ec`). PLp cells at
  Levels 3–5 were then re-judged in relabel-v3, after the synthesis example moved to Level 4 (`d6cc9ca`); the new
  label replaces the old one. So PLp comes from two texts, and each row of `labels.csv` names its run. The merge is
  one-sided: only cells at 3–5 were re-judged, so PLp leans slightly down
  ([relabel-v3/RESULTS.md](https://github.com/Kinds-of-Intelligence-CFI/ADeLe-AIEvaluation/blob/agentic-v2/experiments/benchmarks/relabel-v3/RESULTS.md)).
- **Judge.** Claude Opus 5.5 at effort low, run as a Claude Code subagent, one call per task and rubric. Only answers
  written by that model are kept.
- **Prompt.** ADeLe's v2 annotation prompt: the rubric and the task instruction, a short written assessment, then the
  level. The judge never sees tests, solutions or agent attempts.
- **Missing labels:** none. 35 of 35 tasks have all three labels.

## What the labels show (descriptive)

On the fully labelled clean tasks, PLp against solve rate: ρ = +0.21 (p = 0.22); against expert hours:
ρ = +0.16 (p = 0.36). As on the full benchmark, PLp does not track Terminal-Bench difficulty: most tasks sit
at PLp 3. PLp was already analysed on all 66 tasks with earlier labels, so this is a description, not a new test.

## Limits

- Small: 35 tasks. Wide confidence intervals.
- Epoch's review was partial, so defective tasks may remain.
- Dropping never-solved tasks uses the outcome itself; Epoch's exclusions do not.
- Terminal-Bench 4.0 tasks were public from early 2026, before most of the evaluated models' releases, so this is not
  a contamination-free set.
- One judge, one sample per cell.

## License and citation

Labels and metadata: MIT, like the ADeLe code. Terminal-Bench is Apache-2.0. Cite the ADeLe paper
([arXiv:2503.06378](https://arxiv.org/abs/2503.06378)) and Terminal-Bench.
