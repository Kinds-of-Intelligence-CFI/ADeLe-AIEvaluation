# ProgramBench: task texts and outcomes (fetched 2026-10-01)

Benchmark slug: `programbench`. 200 tasks. Each task gives the agent a compiled, execute-only
binary of an open-source CLI program plus whatever documentation is left in its workspace.
The agent must write a new codebase from scratch whose `./compile.sh` builds a behaviourally
identical `./executable`. Hidden pytest suites (LM-generated, median ~755 scored tests per
task) grade it. Paper: arXiv 2605.03546 (Yang, Lieret, ... Press; Meta), CC-BY-4.0.

## Sources

| What | Where | Pinned revision | Licence |
|---|---|---|---|
| Task list, `task.yaml` (repo, commit, language, difficulty), `tests.json` (test branches, ignored tests) | https://github.com/facebookresearch/ProgramBench | tag `v1.2.5` = `27f02157c785f8da3647aa6dbbe6b9137f99f10e` (2026-09-29) | MIT |
| Agent prompt | https://github.com/SWE-agent/mini-swe-agent `src/minisweagent/config/benchmarks/programbench.yaml` | tag `v2.4.5` = `e187bcb2ff5825d85761a6f9c1f98c9fa6cfbc79` | MIT |
| Agent workspace (docs) | Docker Hub `programbench/<owner>_1776_<repo>.<sha>:task_cleanroom_v6`, last layer only | image + layer digests per task in `meta_programbench.csv` | third-party, per task (MIT 105, Apache 37, GPL/LGPL/MPL/AGPL ~32, ...) |
| Leaderboard registry (per-test pass/fail, cost, calls, tokens, manifests) | https://github.com/ProgramBench/submissions | `c19e570f64719c8326ccdcc7af803447cb89d1a6` (2026-09-30) | MIT |
| Per-run forks (light `eval.json`, `traj.json`) | https://github.com/ProgramBench/<run_id>, commit in `pointer.yaml` | per run, in `leaderboard.csv` | not stated |
| Same runs, heavy eval logs + submissions | HF datasets `programbench/<run_id>` (25), test suites `programbench/ProgramBench-Tests` (MIT) | not downloaded | |

The HF run datasets hold ~55 GB of `eval.log.json` (pipeline logs). They are not needed: the
registry's `_stats/score.json` already has per-test pass/fail. Error codes and agent exit
status come from HTTP range reads of the fork files (~50 KB per run x task). Nothing was gated;
no login was used.

Downloads cached under `data/downloads/programbench/` (gitignored), 2.4 GB in total:
`layers/` 1.8 GB (200 last-layer blobs, sha256-checked), `registry/` 0.55 GB,
`programbench-tests-json/` 41 MB, `fork_extracts/` 2 MB.

## What the agent sees, and what `prompt` contains

The mini-SWE-agent messages are the same for every task: a system template (rules: no source,
no wrapping, no decompiling) and an instance template ("the executable is at `./executable`;
you also have access to the existing documentation; explore all documentation files; ...").
No task-specific text is in the messages. The task-specific input is `/workspace`: the binary,
README, man pages, docs/ trees, examples and test assets left after an LM-written `clean.sh`
removed source code.

`prompt` = system template + task part of the instance template (cut before the generic
"Command Execution Rules" / "Useful command examples" scaffold sections, ~5.6k chars, identical
for all tasks) + a listing of every workspace file with its size + the full text of each
documentation file. "Documentation file" = UTF-8 text, not a licence, basename with no
extension or a prose/manual extension (.md .rst .txt .adoc .org .texi .pod, man sections .1-.9),
and not under a top-level fixture directory (assets/, testdata/, tests/, data/, fonts/,
examples/ ...). Other files are listed as "(not inlined)".

How the workspace was read: the image's last build step wipes `.git`, re-inits it and commits
the cleaned workspace, so that layer's git objects contain every committed file. This avoids
the 33 GB of earlier layers. Check: in all 200 tasks the only non-committed file is
`executable`. For cmatrix the reconstructed listing matches the agent's own `ls -la` in a
published trajectory.

Prompt lengths (chars): min 5,819; median 10,216; p75 16,615; p90 60,339; max 360,931.
**36 prompts exceed 24,000 chars**, 15 exceed 100k, 4 exceed 300k (rumdl 361k, pandoc 311k:
a 299k MANUAL.txt, gomplate 309k, lazygit 301k). If every text file were inlined instead, the
median would be 12k and the max 7.1M (ov: a 6.9 MB test fixture). 70 tasks have <2,000 chars
of documentation. One task (tomnomnom__gron) has no documentation at all, only a licence and
the binary.

Prompt template check against the runs (from each trajectory's config): the system template is
identical in all 25 runs. The instance template matches v2.4.5 exactly in 4 runs; the other 21
(internal harness) differ only by two typos ("IMPORRTANT", "commit you changes"). A later
upstream commit (2026-09-03, after v2.4.5) rewrites the rules wording; no listed run uses it.

## Files written

- `data/instances/instances_programbench.parquet`: benchmark, instance_id, prompt, prompt_sha12
  (200 rows; registered, INSTANCES.tsv sha256 `b2f9789bbc82…`).
- `data/instances/meta_programbench.csv`: repository, commit, language, difficulty, test
  branches, tests listed, ignored-test counts by reason, workspace file/text/doc counts and
  chars, readme_present, image and layer digests, prompt_chars.
- `data/instances/workspace_programbench.parquet`: one row per workspace file (path, size,
  is_text, is_licence, in_prompt, text), to recompose prompts under another rule.
- `experiments/benchmarks/panel/sources/programbench/`:
  - `leaderboard.csv`: one row per run: model, provider, agent, mini-SWE-agent version, effort,
    run date, ProgramBench version used, fork + commit, n_attempted, resolved / near /
    mean score %, cost, template hashes.
  - `runs.csv` (plain CSV, 1.2 MB; tracked): 5,000 rows (25 runs x 200 tasks): attempted, n_tests, n_passed, score,
    resolved, near_resolved, score_v125 (current ignore list re-applied), cost_usd, api_calls,
    output_tokens, error_code, test_branches_run, test_branch_errors (+codes), eval_warnings,
    exit_status, traj model name. **Note: `*.gz` is gitignored in this repo**, so this file is
    not trackable as named.
  - `task_summary.csv`: per task: n_attempted, mean/max score, solve_rate, near_rate, zero-score
    and error counts, min/max scored tests across runs.

Ids, numbers and metadata only; no task text, trajectories or model outputs.

## Runs and models (25 runs, 20 distinct models, all mini-SWE-agent, single attempt)

Run dates 2026-04-29 to 2026-09-18. Paper's 9 models (Apr 29-30): Claude Opus 4.7, Opus 4.6,
Sonnet 4.6, Haiku 4.5, Gemini 3.1 Pro, Gemini 3 Flash, GPT-5.4, GPT-5.4 mini, GPT-5 mini.
Later: GPT-5.5 (default, high, xhigh), Opus 4.7 xhigh, GLM-5.2, Opus 4.8 xhigh, Gemini 3.5 /
3.6 / 3.7 Flash, GPT-5.6 Sol (default, xhigh), Claude Opus 5 xhigh, Meta Muse Spark 1.1 xhigh,
1.2 xhigh, 1.3 xhigh, 1.3 max. Newest: Muse Spark 1.3 max (2026-09-18) and 1.3 xhigh
(2026-09-10); newest Anthropic/OpenAI/Google: Opus 5 xhigh (07-31), GPT-5.6 Sol xhigh (08-02),
Gemini 3.7 Flash (08-15). Not covered (GitHub issue #65): Grok 4.6, GPT-6 Astra.

Best runs (mean score %, resolved %, near %): Opus 5 xhigh 74.7 / 4.5 / 37.0; Opus 4.8 xhigh
70.9 / 0 / 16.5; Muse Spark 1.3 max 70.8 / 2.5 / 25.0; GPT-5.6 Sol xhigh 69.9 / 1.0 / 15.5.
Worst: GPT-5 mini 16.2. Effort is a field only where the model name states it.

## Success definition

Partial. score = passed / scored tests for the task, after removing ignored test branches and
tests (ProgramBench `tests.json`) and the registry ignore map (currently empty for all tasks).
Leaderboard metrics: % resolved (score = 1), % near (score >= 0.95), mean score; tasks a run
did not submit count as 0 over a fixed denominator of 200. `score_v125` re-applies the v1.2.5
ignore list; early runs were packaged with v1.0.2, but the change is small (493 rows differ,
max 0.056; run means move <= 0.1 pt).

Distribution over 4,964 attempted run x task cells: median 0.59, IQR 0.22-0.82; 175 are 0;
22 resolved (0.44%); 348 near-resolved. 36 cells not attempted (count as 0).

## Defect evidence

- **Binary success is nearly degenerate**: 188 of 200 tasks are never resolved. Only 12 tasks
  are resolved by any run (cmatrix 8/25, hex 3/25, eureka 2/25, nine others 1/25). The paper
  itself reports 0% resolved for its 9 models and treats % tests passed as a relative measure.
  For ADeLe, binary "resolved" gives ~22 positives; thresholds (e.g. near >= 0.95, 348
  positives) or the continuous score are the realistic outcome variables.
- **Low ceiling tasks**: 14 tasks never exceed 0.5 by any run (ffmpeg max 0.10, gromacs 0.13,
  ctags 0.19, lnav 0.22, duckdb 0.27, cppcheck 0.29, pandoc 0.29, ...).
- **Missing documentation (open issue #7, #15)**: the LM-written `clean.sh` was "overzealous" in
  several tasks and deleted whole docs/ trees (maintainer comment). Here: 70 tasks have <2k
  chars of docs; gron has none; ffmpeg keeps only a README pointing to online docs.
- **Recall-only tests (open issue #50, third-party audit
  https://github.com/kimjune01/program-bench-audit, CC BY-SA-NS)**: claims 21 programs have
  graded tests needing exact hashes/codecs/binary formats no source-blind solver can derive
  (e.g. blake3, zstd, brotli, lz4, age, Parquet/BAM/ELF decoders), 3 with byte-exact renders,
  1 with an undiscoverable subcommand; 29 programs use self-captured goldens. It proposes a
  model-blind "benchable" subset of 170. Share-alike licence: list not copied here.
- **Evaluator issues (open)**: #56/#59 test-name prefix mismatch and branches that never write
  results.xml (csview); #64 pytest-rerunfailures 16.6.1 duplicates JUnit records and inflates
  scores; #60 the oracle and the build output share `./executable`, so agents can overwrite
  the reference; #37 stdout/stderr merged in the agent's observations while tests check stderr;
  #13 Windows/macOS-specific tests; #54 stale `eval_clean_hashes`. Closed: #45 readable
  executable copy in /tmp in images < v6, #43 compile.sh downloads.
- **Branch errors shrink the denominator**: 271 cells (5.5%) have >= 1 test branch error
  (255 `results_read_failed`); those branches' tests are simply absent from the score, not
  counted as failures. Scored-test counts vary across runs by >10% in 5 tasks (gittype
  103-741, tui-journal, duckdb, walk, stgit).
- **Errors and timeouts**: eval error_code `compile_failed` 137, `copy_executable_failed` 21
  (all score 0); agent exit status: Submitted 4,869, TimeExceeded 43 (6 h limit),
  RepeatedFormatError 35, API errors 16, LimitsExceeded 1.
- **Benchmark validation (paper + tests.json)**: 65,845 ignored tests: dummy_pass 35,839,
  gold_fail 31,089, outcome_dependent_presence 483, slow_or_hang 365, gold_flaky 216, other 10.
  No whole test branch is ignored.

## Decisions for Pablo

1. **What to annotate.** The shared instruction carries no task information; the docs do.
   Options: (a) current prompt (instruction + listing + docs, median 10k, 36 > 24k);
   (b) instruction + listing + README only; (c) truncate docs at a cap; (d) also give the judge
   the binary's `--help` output (the paper says agents rely on it, but getting it needs running
   200 x86 Docker images). The doc filter is a heuristic; `workspace_programbench.parquet`
   allows any other rule.
2. **Prompts > 24k chars** (36; max 361k): truncate, summarise, or accept.
3. **Outcome variable**: resolved (22 positives / 4,964), near >= 0.95, or continuous score.
4. **Task exclusions**: the audit's recall-gated set, gron (no docs), docs-stripped tasks,
   low-ceiling tasks.
5. **Run selection**: 25 runs include several efforts of one model (GPT-5.5 x3, Opus 4.7 x2,
   GPT-5.6 Sol x2, Muse Spark 1.3 x2) and two harness generations (2.2.x vs 2.4.x).
6. **Tracking** (decided 2026-10-01): the scores come from the MIT-licensed registry, so `runs.csv` is committed
   as plain CSV.

Run: `python experiments/benchmarks/programbench-data/fetch_tasks.py` (~25 min first time,
mostly Docker Hub downloads; minutes from cache), then `fetch_outcomes.py` (~30 min, ~10k range
requests to raw.githubusercontent.com; cached per run).
