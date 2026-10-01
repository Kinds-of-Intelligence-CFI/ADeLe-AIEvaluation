# DeepSWE v1.1: tasks, outcomes, defects

Benchmark slug: `deepswe-v1.1`. Fetched 2026-10-01. Data only: no annotation, judges or model runs.

## Sources and revisions

| What | Source | Revision | Access |
|---|---|---|---|
| Task text and metadata | github.com/datacurve-ai/deep-swe | `3cda4081` (2026-06-14, "Updated README for V1.1") | public |
| Upstream licenses | same repo, `PROVENANCE.md` | `6db64a40` (2026-07-10) | public |
| Per-trial outcomes | deepswe.datacurve.ai `/artifacts/v1.1/trials.json` | generated 2026-09-22 (latest job 2026-09-01) | public, no login |
| Per-config leaderboard | deepswe.datacurve.ai `/artifacts/v1.1/leaderboard-live.json` | same | public |
| Defects | epoch.ai/benchmarks/deepswe/review | reviewed 2026-09-07 | public, CC BY 4.0 |
| Community defect reports | github.com/datacurve-ai/deep-swe issues and PRs | read 2026-10-01 | public |

- The repo has no v1.1 tag (only `v1.0.0`; issue #66 asks for one). `instruction.md` is
  byte-identical from the "DeepSWE V1.1" commit `8cae598` to `main` (`0b9fabb`, 2026-08-26).
  Later commits change only `task.toml`: network mode, `[[verifier.collect]]`, and the agent
  timeout (5400 s to 10800 s on 2026-08-26).
- v1.0 to v1.1 changed all 113 instructions. The main change is an appended line telling the
  agent to work on a new branch and commit when done.
- The Hugging Face datasets are **v1.0, not v1.1**. `datacurve/deep-swe` was last changed
  2026-06-02. `datacurve/deep-swe-leaderboard` holds one job, `20260606-deep-swe-leaderboard-all-4x`,
  under `submissions/deep-swe/1.0`. Neither is needed for v1.1.
- Site data for v1 (`/artifacts/v1/trials.json`) also exists. It was not used.

## Access status

- Hugging Face login: cached, user `PabloAMC`.
- Both gated datasets list files but refuse downloads (403, "not in the authorized list").
  Nothing was requested or accepted.
- To get access (only needed for v1.0 data): open
  https://huggingface.co/datasets/datacurve/deep-swe and
  https://huggingface.co/datasets/datacurve/deep-swe-leaderboard while logged in. On each page,
  tick the box "I understand DeepSWE is intended for evaluation use" and click the button that
  requests access. Gating is `auto`, so approval should be immediate.

## Licenses and terms

- Task specs, verifiers and harness: Apache-2.0 (Datacurve's own contributions only).
  Upstream code keeps its own license; all are permissive (MIT 65, Apache-2.0 23, BSD-3 11, ...).
- The site pages carry a no-training canary. Task text
  stays in gitignored `data/` only.
- Trial artifacts on the site (`trials.json`): **no license or terms stated**. Issue #94 (2026-09-18)
  asks Datacurve for terms, including redistribution of derived labels. No answer by 2026-10-01.
- HF leaderboard dataset: CC BY 4.0 (but gated and v1.0). HF task dataset: no license field.
- Epoch review: CC BY 4.0. Committing task ids and Epoch's labels with attribution is fine.
- My reading: per-task pass counts and ids are facts, like the Terminal-Bench exports already in
  `panel/sources/`. Risk of publishing them is low. But it is Pablo's call (see decisions).

## Files

Tracked (ids, numbers and labels only; nothing committed yet):

- `fetch_tasks.py`, `fetch_outcomes.py`: the fetchers. Paths are relative to the repo.
- `epoch_defects.csv`: the 23 tasks Epoch names. Columns: `instance_id`, `epoch_defect`
  (all "False Negative"), `mechanism_group` and `mechanism` (my labels, see below),
  `n_named_trials`, `named_trial_ids` (the id after `__` in the trial name),
  `named_trial_configs` (Epoch's model labels), `source_url`, `review_date`.
- `community_issues.csv`: task-specific defect claims in Datacurve's issues and PRs.
  Columns: `instance_id`, `ref` (issue/PR number), `kind`, `state`, `opened`, `claim`,
  `status_v1_1`. Claims are third-party and mostly unconfirmed by Datacurve.
- `panel/sources/deepswe-v1.1/leaderboard_v1-1.tsv`: one row per config (`row_id` = config): model,
  provider, harness, effort, `metrics_source` (`verified_openai_handoff` for GPT-6 Astra), Datacurve's
  pass@1, pass@4, counts, CI, first and last run date. Aggregate only.

Gitignored (Pablo, 2026-10-01: no terms for the trial data, so per-trial and per-(config, task) data
stay local; per-task solve rates are committed only in `../deepswe-clean/tasks.csv`):

- `data/raw/deepswe-v1.1/leaderboard_full_v1-1.tsv`: the leaderboard above plus mean cost, tokens, steps.
- `data/raw/deepswe-v1.1/tasks_v1-1.csv`: per task: `n_models`, `n_configs`, `n_trials`
  (scored), `n_passed`, `n_excluded`, `n_models_any_pass`, `n_configs_any_pass`,
  `n_epoch_named_fn_trials`, `solve_rate`, `epoch_defect`.
- `data/raw/deepswe-v1.1/trials_compact_v1-1.json`: per (config, task) digit strings in the
  schema of `adele.results.sources.harbor_hub.from_export`. Checked: `from_export(...,
  benchmark="deepswe-v1.1", n_trials_run=4)` gives 7,908 rows, 31,462 scored trials, 17,364 passes.
- `data/raw/deepswe-v1.1/trials_v1-1.csv.gz`: one row per trial.
  Columns: `trial_name, task, config, model, provider, harness, reasoning_effort, trial,
  run_attempt, reward, passed, outcome, included_in_score, error_category, exception_type,
  f2p_passed, f2p_total, p2p_passed, p2p_total, n_agent_steps, n_input_tokens, n_output_tokens,
  cost_usd, started_at, finished_at, agent_duration_seconds, metrics_source,
  epoch_named_false_negative`. `trial` is 1..4 within (config, task), by start time.
- `data/instances/instances_deepswe-v1.1.parquet`: `benchmark, instance_id, prompt, prompt_sha12`.
  `prompt` is `instruction.md` verbatim. Registered in `data/instances/INSTANCES.tsv`
  (sha256 `a91e1c2f700c...`, median 2,075 chars, max 5,484).
- `data/instances/meta_deepswe-v1.1.csv`: repository, upstream license, language (as tagged and
  corrected), category, title, base commit, f2p/p2p test counts, timeouts, resources,
  prompt length, `epoch_defect`, `epoch_mechanism_group`, `community_issues`.
- Caches: `data/downloads/deep-swe/` (sparse checkout), `data/downloads/deepswe-v1.1/` (site JSON).

## Counts

- 113 tasks, 91 repositories. Languages (corrected): Go 35, Python 34, TypeScript 34,
  JavaScript 5, Rust 5. Category: 106 feature requests, 4 bug fixes, 3 enhancements.
- No difficulty label exists. Datacurve publishes none; solve rate is the only proxy.
- 31,617 trials; 31,462 scored; 155 excluded by Datacurve's rule (provider/verifier/network
  errors). 17,364 passes. Our counts match `leaderboard-live.json` for all 70 configs.
- 28 models, 70 configs (model x reasoning effort). One harness: mini-swe-agent via Pier on Modal.
- Every model ran every task. 111 tasks have all 70 configs scored; 2 have 69.
- Up to 4 trials per (config, task); 7,766 of 7,908 pairs have 4 scored trials.
- Solve rate per task: min 2.5%, median 60.4%, max 91.7%.

## Model coverage and run dates

Run dates are from `trials.json`. Release months are from `panel/models.csv` (dash-to-dot mapping).

| Model (Datacurve id) | Configs | Run dates | Release |
|---|---|---|---|
| claude-fable-5 | 5 | 06-12 to 06-13 | 2026-06 |
| claude-opus-4-8 | 5 | 06-12 to 06-14 | 2026-05 |
| claude-sonnet-4-6 | 1 | 06-12 to 06-14 | not in models.csv |
| gpt-5-4 | 1 | 06-12 to 06-13 | 2026-03 |
| gpt-5-5 | 4 | 06-12 to 06-13 | 2026-04 |
| kimi-k2-7-code | 1 | 06-13 | not in models.csv |
| glm-5-2 | 2 | 06-20 to 06-23 | 2026-06 |
| claude-sonnet-5 | 5 | 06-30 to 07-01 | 2026-06 |
| gpt-5-6-sol | 5 | 07-06 | 2026-07 |
| gpt-5-6-luna, gpt-5-6-terra | 5 each | 07-07 | 2026-06 |
| muse-spark-1-1 | 1 | 07-12 to 07-13 | 2026-07 |
| grok-4-5 | 1 | 07-13 | 2026-07 |
| kimi-k3 | 1 | 07-16 to 07-17 | 2026-07 |
| claude-opus-5 | 5 | 07-24 to 07-25 | 2026-07 |
| qwen3-8-max | 1 | 08-03 to 08-04 | 2026-07 |
| deepseek-v4-flash | 1 | 08-05 to 08-06 | not in models.csv |
| gemini-3-7-flash | 3 | 08-06 to 08-12 | 2026-08 |
| muse-spark-1-2 | 1 | 08-06 to 08-07 | not in models.csv |
| deepseek-v4-pro | 1 | 08-12 to 08-13 | not in models.csv |
| gemini-3-1-pro-preview | 1 | 08-12 to 08-13 | 2026-02 (alias `gemini31propreview`) |
| gemini-3-5-flash | 1 | 08-12 to 08-13 | 2026-05 |
| gemini-3-6-flash | 1 | 08-12 to 08-13 | not in models.csv |
| grok-4-6 | 4 | 08-12 to 08-13 | 2026-08 |
| glm-5-3 | 1 | 08-19 to 08-20 | 2026-08 |
| glm-5-3-flash | 1 | 08-26 | not in models.csv |
| **gemini-3-8-flash** | 2 | 08-29 to 09-01 | **2026-09** |
| **gpt-6-astra** | 5 | 08-31 to 09-01 | **2026-09** |

September 2026 models: only **GPT-6 Astra** from the watch list, plus Gemini 3.8 Flash
(released 2026-09 per `models.csv`). Absent: Gemini 4 Argon, Claude Opus 5.5, Sonnet 5.5,
Fable 5.1, GPT-6.1 Sol. Datacurve stopped adding results after 2026-09-03 (changelog; issue
#103 says a new version is in progress). GPT-6.1 Sol has only OpenAI's self-reported scores (#102).

Two caveats:

- GPT-6 Astra rows have `metrics_source = verified_openai_handoff` and no public patches or
  trajectories. The changelog says it was "priced at the expected launch rate card". These look
  like OpenAI-run results that Datacurve checked, not Datacurve's own sweep.
- 73 Claude Fable 5 trials are excluded (`model_routing_404`). The v1.1 blog says access was
  suspended by a US government directive during the sweep.

## Defect evidence

**Epoch AI** (verdict Flawed, 2026-09-07). Epoch names all 23 tasks it found. All are false
negatives. Epoch stopped at 23 because that passed its Flawed threshold; it did not review other
error types or the remaining tasks. It says 18 of 23 come from an error that "could affect any
task": agents edit or add tests, and the verifier's test handling then breaks the build.
Epoch names 89 affected trials; all 89 match failed trials in `trials.json`.

My grouping (`mechanism_group`), which reproduces Epoch's 18:

- `verifier_test_collision` (18): agent tests and hidden tests define the same symbol, or the
  verifier replaces a test file whose helpers other agent tests use, or test ids shift.
- `underspecified_prompt` (4): ink-grid-box-layout, obsidian-linter-auto-table-of-contents,
  sqlfmt-create-table-ddl-formatting, testem-bail-on-test-failure.
- `stale_build_artifact` (1): eicrud-keyset-pagination-cursor.

Epoch-named tasks still have a mean solve rate of 50.7% (others 56.3%). Only obsidian is below 5%.

**Community reports** (`community_issues.csv`, 34 rows, 25 tasks). Status in v1.1:

- Fixed in v1.1, per an independent oracle audit (#52, 2026-07-08): 112 of 113 reference
  solutions pass. The v1.0 reports in #11, #17, #30 (env drift, 8 failing golds) are resolved.
- Still open: prometheus-transactional-reload-status gold fails its own verifier (#45, #52);
  Epoch also names it.
- Prompt ambiguity claims (#13): gql-incremental-graphql-delivery (solve 3.6%) and
  bandit-structured-nosec-directives (solve 6.8%). Not named by Epoch. Unconfirmed.
- Strict or host-dependent tests: quill-shared-toolbar-focus (#24, #78), csstree (#52),
  six tasks that OOM on many-core hosts (#100), eicrud on slow disks (#92). On Datacurve's own
  hosts the golds pass, so the published outcomes may be unaffected.
- Verifier hangs on looping code (#1 koota, #60 claude-code-by-agents). These cost time but do not
  fail correct code.
- 3 wrong language tags (#53); corrected in `language_corrected`.
- 4 trials are scored `pass` with `error_category = agent_timeout` (also flagged in #52).

## Never-solved tasks

None. Every task has at least 7 passes. With the panel's 5% rule, 2 tasks fall below:
obsidian-linter-auto-table-of-contents (2.5%, Epoch-named) and gql-incremental-graphql-delivery (3.6%).

Clean set under the panel rules (drop Epoch-named, drop solve rate < 5%): **89 tasks**.

## Decisions for Pablo

1. **Clean set.** Drop the 23 Epoch tasks and gql (89 left)? Also drop bandit-structured-nosec-directives
   (ambiguity claim, 6.8%) and prometheus-transactional-reload-status (already Epoch-named)?
2. **Unnamed false negatives.** Epoch's review is partial. The test-collision bug can hit any task,
   and stronger models write more tests (Datacurve's own blog). Solve rates on the 89 tasks are
   probably biased down, more for test-writing models. Accept, or wait for Datacurve's next version.
3. **Publish outcomes?** `trials.json` has no terms (#94 open). Decided 2026-10-01: commit only per-task
   solve rates (`../deepswe-clean/tasks.csv`) and the aggregate leaderboard; the rest moved to `data/raw/`.
4. **GPT-6 Astra.** Keep its OpenAI-handoff rows in the panel, or flag them?
5. **Prompt suffix.** Every `instruction.md` ends with a line asking the agent to work on a new
   branch and commit. It is what the agent sees (kept verbatim, as for Terminal-Bench). Datacurve's
   own `prompt_characters` excludes it (about 100 chars shorter). Keep it for annotation?
6. **Model ids.** 7 Datacurve names have no `panel/models.csv` entry (table above). They need
   release months before `build.py` can use this benchmark.
7. **Timeout drift.** The repo raised the agent timeout to 10800 s on 2026-08-26. Runs after that
   (glm-5-3-flash, gemini-3-8-flash, gpt-6-astra) may have had a longer budget. Datacurve does not
   say. The paper's 9000 s also differs from the repo's 5400 s (#81, unanswered).
8. **Run vs release date.** The first v1.1 runs (06-12 to 06-14) predate the V1.1 commit (06-14)
   and release (06-15) by 1 to 3 days. I assume they used the same tasks.

## Rebuild

```
python experiments/benchmarks/deepswe-data/fetch_tasks.py
adele instances register data/instances/instances_deepswe-v1.1.parquet --benchmark deepswe-v1.1
python experiments/benchmarks/deepswe-data/fetch_outcomes.py
```

`fetch_tasks.py` reads `epoch_defects.csv` and `community_issues.csv`; both were written by hand
from the sources above on 2026-10-01 (Epoch's table parsed from the review page's HTML).
