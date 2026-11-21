# FrontierSWE v2 data (benchmark slug `frontierswe-v2`)

Fetched 2026-10-01. Scripts: `fetch_tasks.py`, `fetch_outcomes.py` (this folder).

## Sources

| What | Where | Version | License |
|---|---|---|---|
| Tasks | https://github.com/Proximal-Labs/frontier-swe-v2 | tag `v2.0.0` = commit `da83f84f8fbcec3cbf0f2b17c98ebc811355c2df` (2026-09-19) | No license file. README: "provided for evaluation purposes"; "Task content and scoring may still be updated." |
| Outcomes | https://www.frontierswe.com (home page and the 34 `/tasks/<slug>` pages) | site build `dpl_CLmJYtCU8VFY5apX1fWa3F5qB5uP`, sitemap lastmod 2026-09-30 | No terms page found (`/terms`, `/terms-of-service`, `/tos`, `/legal`, `/privacy` all 404). |
| Harness runner | https://github.com/Proximal-Labs/px-eval | not used | No license. The Proximus harness (system prompt, submit tool) is not public (issue #3). |

## Per-run outcomes: not fetched (robots.txt)

`https://www.frontierswe.com/robots.txt` has `Disallow: /traces`, `/traces/` and `/api/` for
`User-Agent: *`. It repeats this for `anthropic-ai` and `ClaudeBot`, and blocks GPTBot and CCBot
from the whole site. The per-run data (task-labelled reward of each of the ~3,050 runs, plus
traces) lives only under `/traces`. So I stopped there, as the brief requires.
Disclosure: one GET of `/traces` went out (body discarded, nothing parsed) in the same command
that first read robots.txt. No other `/traces` or `/api` request was made.
`fetch_outcomes.py` checks robots.txt before every uncached request and refuses disallowed paths.
In total about 50 requests went to the site, sent one at a time with a 2 s pause.

To get per-run rewards, one of these is needed:
(a) written permission from Proximal Labs to read `/traces`, or
(b) a data export from them (contact: the GitHub issues on frontier-swe-v2, or frontierswe.com/contribute).

## What the allowed pages give

The pages embed their data in the Next.js RSC payload. No API is called.

- **Home page**, per task × model: mean@5 and best@5 reward (the heatmap), number of runs,
  mean cost, mean hours, and mean / best model's mean. Per model: leaderboard score under best,
  mean and worst aggregation (overall and by category), cost, tokens and duration. Per model:
  the sorted list of all its run rewards pooled over tasks. This list has **no task labels**.
- **Task pages**, per model on that task: score (equal to the home mean to 4 dp), a "±" spread,
  steps, input and output tokens, average cost and average time. The "±" is the SD over runs, not
  the SE: under an SE reading, 75 cells would have an SD larger than the maximum possible for
  rewards in [0, 1].

## Files

Task text goes only into gitignored `data/`. Checked with `git check-ignore`: rule `data/` in `.gitignore`.

- `data/instances/instances_frontierswe-v2.parquet`. Columns: benchmark, instance_id, prompt,
  prompt_sha12, has_readme. 34 rows. `prompt` is `tasks/<id>/instruction.md` verbatim, the file
  Harbor gives the agent; for the 25 that cite a README, followed by a blank line, the line
  `Contents of <container path>:` and the README verbatim (Decision 1, taken 2026-10-01).
  Registered in `data/instances/INSTANCES.tsv` (sha256 `af62cb1bf63e…`, median 3,100 chars,
  max 9,824). The instruction-only version (sha256 `5e5685bcd661…`, median 992, max 2,246) was
  replaced before any label.
- `data/instances/meta_frontierswe-v2.csv`. Columns: instance_id, num, name, categories (from
  the README table), toml_name, difficulty, toml_category, oracle_reward_threshold, keywords,
  agent/verifier timeouts, verifier_environment_mode, cpus, memory_mb, storage_mb, gpus,
  gpu_types, network_mode, has_job_yaml, instruction_chars, prompt_chars (with README),
  prompt_cites_readme, readme_chars, description.
- `data/instances/readme_frontierswe-v2.parquet`. Columns: instance_id, container_path,
  source_path, text, text_sha12. This is the agent-visible README that 25 of the 34
  instructions cite as "the complete contract" (see Decision 1).
- `data/raw/frontierswe-v2/site/`: cached raw HTML (home page, `/tasks`, blog, changelog,
  harness, and 34 task pages).
- `experiments/benchmarks/panel/sources/frontierswe-v2/` (trackable; ids and numbers only):
  - `task_model.csv`: 612 rows (34 × 18). Columns: instance_id, site_slug, model_key, model,
    vendor, harness, n_runs, mean_reward, best_reward, mean_reward_home,
    mean_frac_of_top_model, page_score, page_pm (SD), steps, tokens_in, tokens_out,
    avg_cost_usd, avg_hours, traces_url.
  - `models.csv`: 18 rows. Leaderboard overall, implementation, performance and research
    scores under best, mean and worst aggregation; cost, tokens, duration, run counts and
    date added.
  - `task_summary.csv`: 34 rows. n_models, n_runs, run-weighted mean reward, max model mean,
    best run reward and its run id, count of models with mean (or best) at 0, and the share of
    models with mean (or best) reward ≥ 0.1, 0.5, 0.9 and 0.99. These are shares of **models**,
    not of runs. Shares of runs per task need `/traces`.
  - `model_reward_pools.json`: per model, the sorted run rewards pooled over tasks (no task
    labels), plus the best run per task, sorted.

Site slugs differ from repo directory names. The scripts join them on the display name, and
the mapping is 1:1 over all 34 tasks. `instance_id` is the repo directory name.

## Counts

- 34 tasks, 18 models, **3,051 runs** (the brief expected ~3,041). The harness is `proximus`
  for every model, each at its maximum reasoning effort, with a 20 h budget (15 h for
  reconnaissance-blind-chess-recovery).
- 5 trials per task × model, except 4 cells:
  - GPT-6 Astra on cranelift-codegen-opt: 4 runs.
  - Kimi K3 on meg-speech-decoding: 1 run.
  - Kimi K3 on postgresql-18-on-sqlite: 4 runs.
  - DeepSeek V4 Flash Vision Exp on meg-speech-decoding: 2 runs.

  So the per-model totals are 169 (GPT-6 Astra), 165 (Kimi K3), 167 (DeepSeek) and 170 for
  the rest. No reason is given anywhere.
- Rewards are continuous in [0, 1]. Pooled over 3,051 runs:
  - mean 0.351, median 0.231 (quartiles 0.013 and 0.646);
  - 19.5% of runs score exactly 0, 3.0% score ≥ 0.99, and 1.5% score exactly 1.
- Per-task run-weighted mean: from 0.022 (sglang-inference-system-optimization) to 0.710
  (verilog-simulator-in-swift).
- No task has every model at 0 or every model at 1. Every task has at least one run above 0.17.

## Models (leaderboard overall mean@5, %; date added from frontierswe.com/changelog)

| Model (site key) | Mean | Added | Flag |
|---|---|---|---|
| GPT-6 Astra (`gpt6-astra`) | 65.5 | 2026-09-11 | **Sept release**. $1,030 per trial |
| Claude Opus 5.5 (`wafer`) | 62.3 | 2026-09-22 | **Sept release** |
| Claude Sonnet 5.5 (`beignet`) | 61.9 | 2026-09-28 | **Sept release** |
| Claude Fable 5.1 (`fable51`) | 56.3 | launch (blog 2026-09-02) | **Sept release** |
| Gemini 4 Argon (`barium`) | 55.0 | 2026-09-30 | **Sept release**. Site cost caveat: "non-production setting" |
| Claude Opus 5 | 52.0 | 2026-09-08 | |
| Claude Fable 5 | 47.0 | 2026-09-08 | |
| GPT-5.6 (the blog calls it "GPT-5.6 Sol") | 32.2 | launch | |
| GLM-5.3 | 30.2 | launch | |
| Grok 4.7 | 29.5 | 2026-09-21 | |
| Kimi K3 | 25.9 | launch | 165 runs |
| Grok 4.6 | 25.3 | launch | |
| Gemini 3.7 Flash | 20.3 | launch | |
| Gemini 3.8 Flash | 19.6 | 2026-09-08 | |
| Qwen3.8-Max | 15.8 | launch | |
| DeepSeek V4 Flash Vision Exp | 14.8 | launch | 167 runs |
| Muse Spark 1.2 | 12.0 | launch | |
| Inkling | 4.1 | launch | |

**GPT-6.1 Sol is not on the site.** It appears in no cached page. Muse Spark 1.3 was requested
in issue #15 (2026-10-01) and is also absent.

## Reward and "solved"

The blog says: "every task now reports a score between 0 and 1". The score is task-specific:

- Implementation tasks: share of the test suite passed, with structural test mutation.
- Performance tasks: a cost-model proxy, for example weighted instruction counts.
- ML and science tasks: a metric on hidden data.
- Multipliers and gates apply on top, for example runtime multipliers and zeroing on safeguard
  violations.

The scoring text for each task is in the cached `/tasks/<slug>` pages. Trials flagged for
cheating by the QA judge panel were **set to 0**, according to the blog. Without traces, those
cannot be told apart from honest zeros.

Candidate definitions of "solved":

1. Use the continuous reward directly (no threshold).
2. reward ≥ τ, with τ fixed across tasks (for example 0.5 or 0.9).
3. A per-task τ. Note that `oracle_reward_threshold` in task.toml is not usable as τ: it is 0
   for 12 tasks and missing for 12.

Any definition at run level needs `/traces`. At task × model level, the mean@5 and best@5 we
hold support 1, and support 2 for best@5 ("any run ≥ τ" is the same as "best ≥ τ").

## Task-level defect evidence

- **Task text is unchanged across versions.** The only commits are the initial one
  (`0df6e17`, 2026-09-02) and v2.0.0 (`da83f84`, 2026-09-19). Between them, no
  `instruction.md` changed. The 2026-09-19 changes were:
  - image digests pinned in every task.toml;
  - preflight fixes;
  - `job.yaml` runtime profiles "restored" for 5 tasks (cranelift, ffmpeg, libexpat, rbc-chess,
    sglang);
  - the multi-GPU verifier moved into `tests/`.

  The launch models ran before these pins. Whether every model saw identical images is unknown.
- **The evaluated version may differ from the published one.** task.toml names carry suffixes
  that the site slugs lack:
  - `remotion-video-gen-patched`, `optimizer-design-v2-patched` and
    `synthetic-music-diarization-patched`;
  - `gba-stepper-hardened`, `lua-native-compiler-qemu` and `frogsgame-impl`.

  These suggest internal revisions. Whether all runs used the same revision is unknown.
- **Open GitHub issues** (all filed by outside users running Harbor + Docker, not the official
  Modal setup):
  - #14 msms-denovo-generation: the verifier `rmtree`s the `/logs/verifier` bind mount, gets
    EBUSY, and writes reward 0 without evaluating.
  - #7 flight-sim-renderer-in-opengl: core dumps count toward the 16 MiB source cap, giving a
    false 0.
  - #12 flight-sim-renderer-in-opengl: file ownership in the separate verifier gives a false
    build failure and reward 0.
  - #10 and #11 reconnaissance-blind-chess-recovery: the verifier fails to start because of a
    missing `/logs/agent` mount target, stripped entropy keys and EINVAL on hidden proc mounts.
  - #6 and PR #13 fitness-recap-video-in-remotion: a root daemon `chown`s output paths chosen
    by the agent. This is a reward-hacking or isolation hole, not a scoring false-zero.
- **Closed issues** about build reproducibility only: #5 (snooker-prediction,
  reconnaissance-blind-chess-recovery), #8 (notebook-compression private corpus image), and #4.
- **Outcome patterns.** No official run is known to be hit by the issues above. All affected
  tasks have nonzero official rewards. Two tasks look suspicious:
  - msms-denovo-generation: max run 0.17, mean 0.06, two models at 0.
  - sglang-inference-system-optimization: mean 0.02, four models at 0, oracle threshold 0.9.

  Both are hard, but these are the tasks to check first if traces become available.
  optimizer-design, sglang and synthetic-music-diarization all have oracle thresholds of
  0.9–0.95 but best runs of only 0.39–0.59.
- No errored or timed-out run information is public outside `/traces`.

## Decisions for Pablo

1. **What to annotate as the prompt.** `prompt` is `instruction.md` verbatim, 0.6–2.2k chars.
   But 25 of 34 instructions say "read `/app/README.md` for the complete … contract". Those
   READMEs (1–8k chars) are in `readme_frontierswe-v2.parquet`. The other 9 send the agent to
   workspace files, tests or docs. The options are:
   - (a) instruction only;
   - (b) instruction + README;
   - (c) a fuller workspace digest.

   The Terminal-Bench precedent is (a). **Taken 2026-10-01: (b)**, what the agent sees.
2. **Outcomes route.** The options are:
   - (a) ask Proximal Labs for per-run data or permission;
   - (b) use only the task × model aggregates: mean@5, best@5, SD, 18 models × 34 tasks.

   With (b), success could be "best@5 ≥ τ", or continuous mean@5 used as the target.
3. **Which τ for "solved"** (see above), and whether to treat reward-0 runs as failures, given
   that cheating-zeroed trials are mixed in.
4. **Model set.** Keep all 18, or only the frontier? Treat missing runs (4 cells) as missing.
5. **License.** The repo has no license. Task text stays in gitignored `data/` only.
   Redistributing it, for example on HF, needs permission.
