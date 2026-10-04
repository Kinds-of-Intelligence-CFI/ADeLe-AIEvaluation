---
license: mit
pretty_name: ADeLe — tau2 clean set with demand labels
tags:
  - ai-evaluation
  - tau2-bench
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

# ADeLe — tau2 clean set with demand labels

The tau2 tasks of three domains (airline, retail, banking_knowledge) that some agent has solved, with ADeLe demand
labels for every task. 242 tasks, 726 labels. Built at commit `cd608bf` of
[ADeLe-AIEvaluation](https://github.com/Kinds-of-Intelligence-CFI/ADeLe-AIEvaluation) (branch `agentic-v2`,
`experiments/benchmarks/tau2-clean/`).

## What is in it

| file | one row per | what |
|---|---|---|
| `labels_wide.csv` (default) | clean task | solve rates, the hash of the task text, one column per rubric |
| `labels.csv` | clean task × rubric | the level, with the judge, prompt and answer hashes and the run that made it |
| `tasks.csv` | tau2 task with results (257) | solve counts and rates, the reason a task was excluded, and `keep` |
| `rubrics.csv` | rubric | code, name, generation, file and sha256 of the exact text used |

A task is `(benchmark, instance_id)`: ids repeat across domains (`0` is an airline and a retail task). Task text is
not included. It is the user scenario of `data/tau2/domains/<domain>/tasks.json` in
[`sierra-research/tau2-bench`](https://github.com/sierra-research/tau2-bench), rendered by ADeLe's tau2 loader;
`prompt_sha12` pins the exact text, since tau2 revised some tasks between versions.

## How the set was built

- **Domains.** Airline, retail and banking_knowledge. Telecom is left out: 2,280 of its 2,285 tasks share one text, so
  a label could not tell them apart.
- **Results.** Per-task rewards from Sierra's public results, only for runs on the same task text as the frozen one.
- **Banking grading.** tau2 v1.0.1 (2026-07-15) changed how banking_knowledge is graded. For banking, only the 10
  configurations run after it (August 2026) count, for the rule below and for the solve rates. The rates over every
  banking run, old and new grading mixed, are in the `*_mixed` columns for comparison only.
- **Rule.** Keep a task if at least one scored trial solves it. With no pass ever recorded, a broken task cannot be
  told apart from a hard one.

| domain | tasks with results | never solved | kept |
|---|---|---|---|
| airline | 50 | 1 | 49 |
| retail | 114 | 0 | 114 |
| banking_knowledge | 93 | 14 | 79 |

**Solve rate** (`solve_rate`) is the share of scored trials with reward 1, over the configurations that ran every kept
task of the domain (airline 7, retail 8, banking 10). `solve_rate_all` uses every configuration that ran the task
(airline and retail 16, banking 10).

## How the labels were made

- **Rubrics.** ADeLe v2 planning family: PLp (Planning), PLe (Action control and execution), PLs (Simulating). Each
  is a 0–5 scale; `rubrics.csv` pins the exact text by sha256. PLp is the text adopted on 2026-10-01, PLs the one
  adopted on 2026-10-04.
- **Judge.** Claude Opus 5.5 at effort low, run as a Claude Code subagent, one call per task and rubric. Only answers
  written by that model are kept.
- **Prompt.** ADeLe's v2 annotation prompt (`build_annotation_prompt_v2`): the rubric and the task, a short written
  assessment, then the level. The judge sees only the user scenario, never the expected actions or any agent's attempt.
- **Runs.** PLp and PLe of 10 banking tasks were labelled in run `tau2-clean-new-pl` (ADeLe's mass-annotation
  runner); the rest come from the earlier runs `o-tau2` (PLp) and `v2-tau2` (PLe). The prompts are byte-identical across
  these runs for the same task and rubric. Every PLs label comes from run `pls-relabel`.

## What the labels show

PLp against solve rate, within domain: ρ = -0.30 (p = 4.2e-06; Spearman per domain, combined by Fisher z).
Details:
[`results/clean.json`](https://github.com/Kinds-of-Intelligence-CFI/ADeLe-AIEvaluation/blob/agentic-v2/experiments/benchmarks/tau2-clean/results/clean.json).

## Limits

- **Few configurations.** 7 to 10 configurations per domain. Rates are noisy, most of all for banking.
- **Outcome-based rule.** Dropping never-solved tasks uses the outcome itself. No external audit of tau2 tasks is used.
- **Little spread.** Most tasks sit at PLp 2; PLe barely varies outside banking.
- **Contamination.** tau2 tasks are public. Some passes may rest on memory.
- **One judge, one sample per cell.**

## License and citation

Labels and metadata: MIT, like the ADeLe code and tau2-bench. Cite the ADeLe paper
([arXiv:2503.06378](https://arxiv.org/abs/2503.06378)) and tau2-bench.
