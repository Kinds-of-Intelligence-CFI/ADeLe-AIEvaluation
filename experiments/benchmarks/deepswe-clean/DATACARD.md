---
license: mit
pretty_name: ADeLe — DeepSWE v1.1 with demand labels
tags:
  - ai-evaluation
  - deepswe
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

# ADeLe — DeepSWE v1.1 with demand labels

All {n_tasks} tasks of DeepSWE v1.1, with per-task solve rates, external defect flags, and ADeLe demand labels on the
{n_clean} clean tasks. {n_labels} labels ({label_counts}). Built at commit `{commit}` of
[ADeLe-AIEvaluation](https://github.com/Kinds-of-Intelligence-CFI/ADeLe-AIEvaluation) (branch `agentic-v2`,
`experiments/benchmarks/deepswe-clean/`).

## What is in it

| file | one row per | what |
|---|---|---|
| `labels_wide.csv` (default) | task | outcomes, defect flags, `keep`, one column per rubric (empty for dropped tasks) |
| `labels.csv` | task × rubric | the level, with the judge, prompt and answer hashes and the run that made it |
| `tasks.csv` | task (all {n_tasks}) | the same outcomes and flags, without labels |
| `rubrics.csv` | rubric | code, name, generation, file and sha256 of the exact text used |

Task text is not included (the DeepSWE site carries a no-training canary). Join on `instance_id` with
[`datacurve-ai/deep-swe`](https://github.com/datacurve-ai/deep-swe), commit `3cda4081` (no v1.1 tag),
`tasks/<instance_id>/instruction.md`.

## Tasks and flags

- **Clean set (`keep`).** All tasks except the 23 that Epoch AI's review (2026-09-07, CC BY 4.0) names as defective
  (`epoch_defect_type`, `epoch_mechanism`). Every task is solved at least once, so nothing else is dropped.
- **`community_issue`** (flag, not exclusion): an open issue or PR on the benchmark's GitHub claims an ambiguous
  instruction or a verifier that rejects correct work, unfixed in v1.1 (`community_refs`). These are third-party claims.

**Solve rate** is the share of scored trials resolved across Datacurve's 70 configurations (28 models × reasoning
effort, mini-swe-agent, up to 4 trials per task; site data of 2026-09-22). Trials Datacurve excludes from its score are
missing, not failures. `solve_rate_pre_timeout` drops the 8 configurations run after the agent timeout was raised on
2026-08-26; `solve_rate_no_astra` drops GPT-6 Astra's OpenAI-run configurations.

## How the labels were made

- **Rubrics.** ADeLe v2: PLp (Planning), PLe (Action control and execution), PLs (Simulating), MSm (Mind modelling and
  social cognition), MSc (Communication and social interaction); each a 0–5 scale. `rubrics.csv` pins the exact text.
  PLs is the text adopted on 2026-10-04.
- **Judge.** Claude Opus 5.5 at effort low, run as a Claude Code subagent, one call per task and rubric. Only answers
  written by that model are kept.
- **Prompt.** ADeLe's v2 annotation prompt: the rubric and the task instruction (verbatim, as the agent sees it), a
  short written assessment, then the level. The judge never sees tests, solutions or agent attempts.
- **Missing labels:** none.

## What the labels show

PLp falls with solve rate on the clean set: ρ = {rho_plp}. PLs falls too: ρ = -0.22 (p = 0.033, n = 90). PLe shows
nothing (ρ ≈ 0). MSm and MSc are 0 on every task: DeepSWE involves no other party. Full results:
[deepswe-clean/RESULTS.md](https://github.com/Kinds-of-Intelligence-CFI/ADeLe-AIEvaluation/blob/agentic-v2/experiments/benchmarks/deepswe-clean/RESULTS.md).

## Limits

- Epoch's review is partial. Its main error mode (agent tests collide with hidden tests) can hit any task, so solve
  rates are probably biased down, more for models that write tests.
- Datacurve states no terms for its trial data (deep-swe issue #94, open). Only per-task aggregates are included.
- Task text is public; this is not a contamination-free set.
- One judge, one sample per cell.

## License and citation

Labels and metadata: MIT, like the ADeLe code. DeepSWE task specs: Apache-2.0. Epoch AI's defect labels: CC BY 4.0.
Cite the ADeLe paper ([arXiv:2503.06378](https://arxiv.org/abs/2503.06378)), DeepSWE (Datacurve) and Epoch AI's review.
