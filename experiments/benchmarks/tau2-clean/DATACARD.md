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
labels for every task. {n_kept} tasks, {n_labels} labels. Built at commit `{commit}` of
[ADeLe-AIEvaluation](https://github.com/Kinds-of-Intelligence-CFI/ADeLe-AIEvaluation) (branch `agentic-v2`,
`experiments/benchmarks/tau2-clean/`).

## What is in it

| file | one row per | what |
|---|---|---|
| `labels_wide.csv` (default) | clean task | solve rates, the hash of the task text, one column per rubric |
| `labels.csv` | clean task × rubric | the level, with the judge, prompt and answer hashes and the run that made it |
| `tasks.csv` | tau2 task with results (257) | solve counts and rates, the reason a task was excluded, and `keep` |
| `rubrics.csv` | rubric text | code, name, generation, file, sha256 of the exact text, and the runs that used it |

A task is `(benchmark, instance_id)`: ids repeat across domains (`0` is an airline and a retail task). Task text is
not included. The task is defined by `data/tau2/domains/<domain>/` in
[`sierra-research/tau2-bench`](https://github.com/sierra-research/tau2-bench); `prompt_sha12` pins the user scenario
(the simulated customer's script, rendered by ADeLe's tau2 loader), since tau2 revised some tasks between versions.

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
  is a 0–5 scale; `rubrics.csv` pins the exact text by sha256.
- **Runs.** All labels come from tau2-goal (2026-10-26), one run over every clean task and rubric
  ([tau2-goal/RESULTS.md](https://github.com/Kinds-of-Intelligence-CFI/ADeLe-AIEvaluation/blob/agentic-v2/experiments/benchmarks/tau2-goal/RESULTS.md)).
- **Judge.** Claude Opus 5.5 at effort low, run as a Claude Code subagent, one call per task and rubric. Only answers
  written by that model are kept.
- **What the judge reads.** The full task from the agent's side: the domain policy, the agent's tools, the database
  records the task touches, the simulated customer's script and standing rules, and the goal (what the agent must
  tell the customer, the outcome checks, what the reward is based on). It does not see the grader's list of expected
  actions or any agent's attempt. Until 2026-10-26 the judge read only the customer's script; on that input MSc and
  the PL rubrics tracked solve rate less well
  ([tau2-full/RESULTS.md](https://github.com/Kinds-of-Intelligence-CFI/ADeLe-AIEvaluation/blob/agentic-v2/experiments/benchmarks/tau2-full/RESULTS.md)).
  Built by `experiments/benchmarks/tau2-goal/build.py`.
- **Prompt.** ADeLe's v2 annotation prompt without the written assessment (`build_annotation_prompt_v2_noreason`): the
  rubric and the task, then the level as a bare digit.

## What the labels show

PLp against solve rate, within domain: ρ = {rho_plp} (p = {p_plp}; Spearman per domain, combined by Fisher z).
The study's results, on earlier labels:
[`RESULTS.md`](https://github.com/Kinds-of-Intelligence-CFI/ADeLe-AIEvaluation/blob/agentic-v2/experiments/benchmarks/tau2-clean/RESULTS.md).

## Limits

- **Few configurations.** 7 to 10 configurations per domain. Rates are noisy, most of all for banking.
- **Outcome-based rule.** Dropping never-solved tasks uses the outcome itself. No external audit of tau2 tasks is used.
- **Little spread.** Most tasks sit at PLp 2; PLe barely varies outside banking.
- **Contamination.** tau2 tasks are public. Some passes may rest on memory.
- **One judge, one sample per cell.**

## License and citation

Labels and metadata: MIT, like the ADeLe code and tau2-bench. Cite the ADeLe paper
([arXiv:2503.06378](https://arxiv.org/abs/2503.06378)) and tau2-bench.
