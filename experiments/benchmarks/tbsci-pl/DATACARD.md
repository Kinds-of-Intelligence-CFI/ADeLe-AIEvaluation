---
license: mit
pretty_name: ADeLe — Terminal-Bench Science 0.1 with demand labels
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
  - config_name: open_issues
    data_files: open_issues.csv
  - config_name: rubrics
    data_files: rubrics.csv
---

# ADeLe — Terminal-Bench Science 0.1 with demand labels

All {n_tasks} tasks of Terminal-Bench Science 0.1, with ADeLe demand labels and flags for tasks that may be broken.
{n_labels} labels. Built at commit `{commit}` of
[ADeLe-AIEvaluation](https://github.com/Kinds-of-Intelligence-CFI/ADeLe-AIEvaluation) (branch `agentic-v2`,
`experiments/benchmarks/tbsci-pl/`).

## What is in it

| file | one row per | what |
|---|---|---|
| `labels_wide.csv` (default) | task | domain, field, expert hours, trials and solve rate, flags, one column per rubric |
| `labels.csv` | task × rubric | the level, with the judge, prompt and answer hashes and the run that made it |
| `tasks.csv` | task (all {n_tasks}) | the same outcomes and flags, without labels |
| `open_issues.csv` | open `[TASK FIX]` issue | number, date, task, whether it counts for the flag, title, link |
| `rubrics.csv` | rubric | code, name, generation, file and sha256 of the exact text used |

Task text is not included (Terminal-Bench Science tasks carry a no-training canary). Join on `instance_id` with
[`harbor-framework/terminal-bench-science`](https://github.com/harbor-framework/terminal-bench-science), tag `v0.1.0`
(commit `f81afac`), `tasks/<domain>/<field>/<instance_id>/instruction.md`.

## Tasks and flags

Every task is kept. Two flags let users filter:

- **`solved_any`**: some trial solves the task. {n_solved_any} tasks; {n_never} are never solved. With no pass ever
  recorded, a broken task cannot be told apart from a hard one.
- **`open_issue`**: an open `[TASK FIX]` issue on the benchmark's GitHub names the task ({n_open_issue} tasks; issue
  numbers in `open_issues`; list fetched {issues_date}). Issues that only concern running on non-x86 machines do not
  count: the leaderboard runs on x86_64. An open issue is a report, not a confirmed defect.

{n_clean} tasks are solved and have no open issue.

**Solve rate** is the share of scored trials with reward 1 across the 12 leaderboard configurations with public trials
(Harbor Hub, `v0-1-eval`, 3 trials per task, exported 2026-10-01). A trial without a reward is missing, not a failure.
**Expert hours** is the task author's estimate in `task.toml`. Domain and field come from the task's path.

## How the labels were made

- **Rubrics.** ADeLe v2 planning family: PLp (Planning), PLe (Action control and execution), PLs (Simulating), each a
  0–5 scale; `rubrics.csv` pins the exact text by sha256. PLp is the text adopted on 2026-10-01.
- **Judge.** Claude Opus 5.5 at effort low, run as a Claude Code subagent, one call per task and rubric. Only answers
  written by that model are kept.
- **Prompt.** ADeLe's v2 annotation prompt: the rubric and the task instruction, a short written assessment, then the
  level. The judge never sees tests, solutions or agent attempts.
- **Missing labels:** {unlabelled}.

## What the labels show

PLp against solve rate: ρ = {rho_all_solve_rate} on all tasks; {rho_solved_any_no_open_issue_solve_rate} on the
solved tasks without an open issue. PLp against expert hours: ρ = {rho_all_expert_hours} on all tasks;
{rho_solved_any_no_open_issue_expert_hours} on the solved tasks without an open issue. Spearman, two-sided.

## Limits

- Small: {n_tasks} tasks, 12 configurations, 3 trials each. Wide confidence intervals.
- The issue flag is a snapshot of open reports, not an audit.
- Dropping never-solved tasks would use the outcome itself.
- Terminal-Bench Science tasks are public; this is not a contamination-free set.
- One judge, one sample per cell.

## License and citation

Labels and metadata: MIT, like the ADeLe code. Terminal-Bench Science is Apache-2.0. Cite the ADeLe paper
([arXiv:2503.06378](https://arxiv.org/abs/2503.06378)) and Terminal-Bench Science.
