---
license: mit
pretty_name: ADeLe — ProgramBench with demand labels
tags:
  - ai-evaluation
  - programbench
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

# ADeLe — ProgramBench with demand labels

All 200 tasks of ProgramBench v1.2.5, with per-task outcomes, flags, and ADeLe demand labels on the 130
clean tasks. 644 labels (PLp 128, PLe 129, PLs 129, MSm 129, MSc 129). Built at commit `fd88cd4` of
[ADeLe-AIEvaluation](https://github.com/Kinds-of-Intelligence-CFI/ADeLe-AIEvaluation) (branch `agentic-v2`,
`experiments/benchmarks/programbench-pl/`).

## What is in it

| file | one row per | what |
|---|---|---|
| `labels_wide.csv` (default) | task | outcomes, prompt size, flags, `keep`, one column per rubric (empty for dropped tasks) |
| `labels.csv` | task × rubric | the level, with the judge, prompt and answer hashes and the run that made it |
| `tasks.csv` | task (all 200) | the same outcomes and flags, without labels |
| `rubrics.csv` | rubric | code, name, generation, file and sha256 of the exact text used |

Task text is not included: the documentation the agent sees comes from third-party programs under many licences. Join
on `instance_id` with [`facebookresearch/ProgramBench`](https://github.com/facebookresearch/ProgramBench), tag
`v1.2.5` (commit `27f0215`).

## Tasks, outcomes and flags

**Outcomes** come from the MIT-licensed [ProgramBench/submissions](https://github.com/ProgramBench/submissions)
registry (commit `c19e570`, 2026-09-30): 25 runs, 20 models, mini-SWE-agent, one attempt per task. Score = passed /
scored tests. A (run, task) cell is solved when score ≥ 0.9. `solve_rate_<t>` is the share of the task's attempted runs
at threshold t (0.9 primary; 0.75, 0.5); runs that did not submit the task are missing. `mean_score` is over attempted
runs. `difficulty` is ProgramBench's own label.

- **Clean set (`keep`).** Tasks some run brings to 0.9: 130. No external defect list names tasks as broken, so
  nothing else is dropped.
- **`docs_damaged`** (flag): the benchmark's cleaning script deleted documentation (issue #7), or the workspace has
  under 2,000 chars of docs.
- **`knowledge_gated`** (flag): on the skip-list of a third-party audit (kimjune01/program-bench-audit, cited in issue
  #50): tests need exact hashes, byte-exact renders or an undiscoverable entry point. Ids only; the audit is
  share-alike.
- **`evaluator_issue`** (flag): an open evaluator-bug issue names the task and v1.2.5 does not fix it
  (`evaluator_refs`).

## How the labels were made

- **Rubrics.** ADeLe v2: PLp (Planning), PLe (Action control and execution), PLs (Simulating), MSm (Mind modelling and
  social cognition), MSc (Communication and social interaction); each a 0–5 scale. `rubrics.csv` pins the exact text.
- **Judge.** Claude Opus 5.5 at effort low, run as a Claude Code subagent, one call per task and rubric. Only answers
  written by that model are kept. Prompts too long for one read (13 tasks) were read in 200-line parts by the same
  model, and a check required every line to come back.
- **Prompt.** ADeLe's v2 annotation prompt: the rubric and what the agent sees (the agent instruction, the workspace
  file listing and the full documentation), a short written assessment, then the level. The judge never sees tests,
  solutions or agent attempts.
- **Missing labels:** `agourlay__zip-password-finder.704700d` (all rubrics); `filosottile__age.706dfc1` (PLp). For zip-password-finder a safety classifier handed every attempt to another model;
  for age (PLp) the judge twice stopped reading one line short of the end, which the check rejected.

## What the labels show

PLp falls with solve rate on the clean set: ρ = -0.48 (p = 1e-08, n = 128). This holds without flagged tasks, at every threshold, and
after controlling for prompt length. PLe and PLs are weak or null. MSm and MSc are 0 on every labelled task:
ProgramBench involves no other party. Full results:
[programbench-pl/RESULTS.md](https://github.com/Kinds-of-Intelligence-CFI/ADeLe-AIEvaluation/blob/agentic-v2/experiments/benchmarks/programbench-pl/RESULTS.md).

## Limits

- Floor-heavy outcome: many clean tasks are solved by one or two runs.
- Test branches that errored are absent from the score, as on the leaderboard.
- Task programs and their docs are public; this is not a contamination-free set.
- One judge, one sample per cell.

## License and citation

Labels and metadata: MIT, like the ADeLe code. ProgramBench and its submissions registry: MIT. Cite the ADeLe paper
([arXiv:2503.06378](https://arxiv.org/abs/2503.06378)) and ProgramBench (arXiv:2605.03546).
