---
license: mit
pretty_name: ADeLe — SWE-bench Verified clean set with demand labels
tags:
  - ai-evaluation
  - swe-bench
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

# ADeLe — SWE-bench Verified clean set with demand labels

A subset of SWE-bench Verified that drops tasks known or likely to be broken, with ADeLe demand labels for every task.
443 tasks, 1329 labels. Built at commit `b528ffa` of
[ADeLe-AIEvaluation](https://github.com/Kinds-of-Intelligence-CFI/ADeLe-AIEvaluation) (branch `agentic-v2`,
`experiments/benchmarks/swebench-clean/`).

## What is in it

| file | one row per | what |
|---|---|---|
| `labels_wide.csv` (default) | clean task | solve count and rate, SWE-bench's time-to-fix estimate, one column per rubric |
| `labels.csv` | clean task × rubric | the level, with the judge, prompt and answer hashes and the run that made it |
| `tasks.csv` | Verified task (all 500) | solve count, the reasons a task was excluded, and `keep` |
| `rubrics.csv` | rubric text | code, name, generation, file, sha256 of the exact text, and the runs that used it |

Task text is not included. Join on `instance_id` with
[`princeton-nlp/SWE-bench_Verified`](https://huggingface.co/datasets/princeton-nlp/SWE-bench_Verified).

```python
from datasets import load_dataset
clean = load_dataset("<org>/<this-dataset>")            # labels_wide.csv
labels = load_dataset("<org>/<this-dataset>", "labels")  # full provenance
```

## How the set was built

All 500 SWE-bench Verified tasks, minus three groups. A task is excluded if it is in any of them.

| excluded | tasks | why | source |
|---|---|---|---|
| never solved | 29 | No agent among the 135 leaderboard entries solves it. With no fix ever accepted, a broken task cannot be told apart from a hard one. | [`SWE-bench/experiments`](https://github.com/SWE-bench/experiments) at `40f164d` |
| named defective | 3 | OpenAI's 2026 audit names them: tests reject correct fixes or check behaviour the issue never asks for. | [OpenAI, Feb 2026](https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/) |
| weak tests | 26 | UTBoost showed their tests accept wrong patches. | [UTBoost, ACL 2025](https://aclanthology.org/2025.acl-long.189.pdf), `augTest.json` at commit `47a47c2` |

One task is in two groups (`pylint-dev__pylint-4551`: named and never solved). 443 tasks remain. Of these, 35
are hard: only 1 to 6 of the 135 entries solve them. They are kept because some agent's fix passed their tests.

**Solve rate** is the share of the 135 leaderboard entries (2023–2026) that resolve the task.

## How the labels were made

- **Rubrics.** ADeLe v2 planning family: PLp (Planning), PLe (Action control and execution), PLs (Simulating). Each
  is a 0–5 scale; `rubrics.csv` pins the exact text by sha256.
- **Runs.** All labels come from relabel-v2, made after the examples review of 2026-10-04 (`d4ec2ec`). PLp cells at
  Levels 3–5 were then re-judged in relabel-v3, after the synthesis example moved to Level 4 (`d6cc9ca`); the new
  label replaces the old one. So PLp comes from two texts, and each row of `labels.csv` names its run. The merge is
  one-sided: only cells at 3–5 were re-judged, so PLp leans slightly down
  ([relabel-v3/RESULTS.md](https://github.com/Kinds-of-Intelligence-CFI/ADeLe-AIEvaluation/blob/agentic-v2/experiments/benchmarks/relabel-v3/RESULTS.md)).
- **Judge.** Claude Opus 5.5 at effort low, run as a Claude Code subagent, one call per task and rubric. Only answers
  written by that model are kept: when a safety classifier hands a call to another model, that answer is discarded.
- **Prompt.** ADeLe's v2 annotation prompt (`build_annotation_prompt_v2`): the rubric and the task, a short written
  assessment, then the level. The judge sees only the issue text, never the tests, the patch or any agent's attempt.

## What the labels show

On the 443 tasks, PLp falls with solve rate (Spearman ρ = -0.55) and rises with the human time-to-fix
estimate (ρ = +0.41). The 35 hard tasks average PLp 1.97, against 1.64 for the rest. PLe and PLs
barely vary on this benchmark: almost every task is PLe 3 and PLs 1. Details:
[`RESULTS.md`](https://github.com/Kinds-of-Intelligence-CFI/ADeLe-AIEvaluation/blob/agentic-v2/experiments/benchmarks/swebench-clean/RESULTS.md).

## Limits

- **Contamination.** SWE-bench repositories and fixes are public, and current models can recall some of them. Some
  passes, and some judge labels, may rest on memory.
- **Not a full audit.** OpenAI's full list of 138 audited tasks is not public, so defective tasks may remain,
  most likely among the hard ones.
- **Outcome-based rule.** Dropping never-solved tasks uses the outcome itself. The OpenAI and UTBoost exclusions do not.
- **One judge, one sample per cell.** Repeat judging was not run on this set. On Terminal-Bench, the same judge gave
  the same PLp level on a repeat 88% of the time.

## License and citation

Labels and metadata: MIT, like the ADeLe code and SWE-bench. Cite the ADeLe paper
([arXiv:2503.06378](https://arxiv.org/abs/2503.06378)) and SWE-bench Verified.
