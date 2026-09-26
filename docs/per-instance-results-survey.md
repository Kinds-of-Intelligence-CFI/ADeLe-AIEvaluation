# Where per-instance results exist for frontier and near-frontier models (survey, 2026-09-14)

**Purpose.** ADeLe v2's agentic rubrics (PLp, PLe, PLs, MSc, MSm) have never been joined to a
solver outcome (desideratum 9, criterion validity). The join needs, per benchmark instance:
the task text (to annotate demand), and for each model a **flag** (solved / not solved, or a
reward) or, better, a **trace** (the full trajectory). This note records which public sources
carry that, for which model generation, and how to get it. Everything marked *verified* was
checked directly on 2026-09-14 (listing the bucket, downloading a file, parsing it); everything
marked *not opened* was located but its contents were not inspected.

**Generations used below** (by release date, not by score):

| tier | models |
|---|---|
| **G0 — frontier (Jun–Sep 2026)** | Claude Fable 5 / 5.1, Claude Opus 5, GPT-5.6 (-sol), GPT-6 Astra, Kimi K3, DeepSeek V4 (-Flash), Gemini 3.5 Flash, Qwen3.8 Max, Muse Spark 1.1, Inkling, Grok 4.5 |
| **G1 — one step behind (Jan–May 2026)** | Claude Opus 4.6 / 4.7 / 4.8, Sonnet 4.6, GPT-5.3-Codex / 5.4 / 5.5, Gemini 3.1 Pro, GLM-5 / 5.1 / 5.2, Kimi K2.5 / 2.6, MiniMax M2.5–M3, Qwen3.5 / 3.6 / 3.7, DeepSeek V3.2, Grok 4.2 |
| **G2 — late 2025** | Claude Opus 4.5, Sonnet 4.5, Haiku 4.5, GPT-5 / 5.1 / 5.2, Gemini 3 Pro / Flash, Kimi K2, GLM-4.6 / 4.7 |
| **G3 — mid 2025 and earlier** | Opus 4 / 4.1, Sonnet 4, Claude 3.7, o3, o4-mini, GPT-4.1, Gemini 2.5, DeepSeek R1 / V3 |

The headline: **no public source gives agentic per-instance results for G0 except one** (tau2
`banking_knowledge`, 97 tasks, on Sierra's public S3 bucket). G1 is covered well for
Terminal-Bench 2.0, OSWorld 2.0, METR's task suites and ARC-AGI; G2 is covered well for
SWE-bench Verified, tau2 (all domains), HAL's nine benchmarks, Toolathlon and Exgentic.

---

## 1. Summary table

"Flags" = per-instance success or reward. "Traces" = full trajectories. "Text" = whether the
task text needed for demand annotation is public and joins on the same id.

| # | source | benchmark(s) | what | newest generation | text | access |
|---|---|---|---|---|---|---|
| 1 | Sierra tau2 public S3 bucket | tau2 airline / retail / telecom / banking_knowledge (+ voice, "terminal") | **traces + flags**, 4 trials | **G0** (banking_knowledge only); G2 for the other domains | yes, frozen in `data/instances/` | open, `sierra-tau-bench-public` S3 (verified) |
| 2 | SWE-bench/experiments (GitHub) | SWE-bench Verified (+ lite, test, multimodal, multilingual) | **flags** for 135 entries; traces for some entries | G2 (Opus 4.5, Gemini 3 Pro, GPT-5); a few G1 (GPT-5.2-Codex, Kimi K2.5, Gemini 3.5 Flash) | yes, HF `princeton-nlp/SWE-bench_Verified` | open (verified) |
| 3 | Terminal-Bench 2.0 leaderboard (HF) | Terminal-Bench 2.0, 89 tasks | **flags**, 5 trials × 76 submissions; traces only in the web viewer | **G1** (Opus 4.7, GPT-5.5, Gemini 3.1 Pro, GLM-5, Kimi K2.5, MiniMax M2.7, DeepSeek V3.2) | yes, HF `harborframework/terminal-bench-2.0` (canary strings) | open (verified) |
| 4 | OSWorld 2.0 / OSWorld-Verified trajectories (HF) | OSWorld 2.0 (long-horizon computer use), OSWorld-Verified (369 tasks) | **traces** (zips per run) | **G0/G1** (GPT-5.6-sol, GPT-5.5, Opus 4.7, Sonnet 4.6, MiniMax M3, GLM-V5, Qwen3.7) | yes, HF `xlangai/osworld_v2_tasks` | open (located, not opened) |
| 5 | METR eval-analysis-public (GitHub) | HCAST, SWAA, RE-Bench (228 tasks) | **flags** + human baseline minutes, 24k runs | **G1** (Opus 4.6, GPT-5.3-Codex, GPT-5.2, Gemini 3 Pro) | mostly **no** (HCAST tasks private) | open (verified) |
| 6 | HAL (Princeton) | SWE-bench Verified Mini, tau-bench airline, USACO, GAIA, AssistantBench, CORE-bench, SciCode, ScienceAgentBench, ColBench, browser-use, SeeAct | **traces + flags**, encrypted | G2 (Sonnet 4.5, Haiku 4.5, GPT-5, Opus 4.1; Opus 4.5 on CORE-bench only) | yes (per benchmark) | open, HF `agent-evals/hal_traces`, decrypt with `hal-decrypt` (verified listing) |
| 7 | Toolathlon trajectories (HF) | Toolathlon, 108 tasks | **traces**, 3 runs | G2 (GPT-5, Opus 4.5, Sonnet 4.5, DeepSeek 3.2, Kimi K2, GLM-4.6) | yes (repo) | open (verified listing) |
| 8 | Exgentic agent-llm-traces-v2 (HF) | AppWorld, SWE-bench, BrowseComp-Plus, tau2 ×3 | **traces + per-session score/success**, 10,057 sessions, 4 harnesses | G2/G1 (Opus 4.5, Gemini 3 Pro, GPT-5.2, DeepSeek V3.2, Kimi K2.5) | yes | open; local copy in `data/downloads/exgentic` (verified README) |
| 9 | ARC Prize per-task dumps | ARC-AGI-1/2 | **flags** (attempts per task) | **G0/G1** (Opus 5, Fable 5, GPT-5.6, Kimi K3 via scraper; Opus 4.8, GPT-5.4, Gemini 3.1 Pro, GLM-5 in local dump) | yes (grids) | open; local `data/downloads/arc_dump` + `adele results fetch-arcprize` |
| 10 | MathArena outputs (HF) | AIME 2025 / 2026 | **flags**, ~97 configs | G1/G0 | yes | open; `adele results fetch-matharena` |
| 11 | HELM Capabilities v1.15.0 (GCS) | GPQA, MMLU-Pro, Omni-MATH, IFEval, WildBench | **per-instance predictions**, 68 models | G2 (Gemini 3 Pro, GPT-5.1, Sonnet 4.5) | yes | open, `crfm-helm-public` bucket (verified) |
| 12 | ForecastBench processed sets | forecasting questions, rounds 2024-07 → 2026-08 | per-question forecasts + resolutions | **G0** (Fable 5, Opus 4.8) | yes | open; local tarball `processed_forecast_sets.tar.gz` (verified) |
| 13 | BrowseComp-Plus runs (HF) | BrowseComp-Plus | **traces** (o3, GPT-5) | G2 | yes (encrypted answers) | open; local `data/downloads/bcp_runs` |
| 14 | Epoch AI Benchmarking Hub | GPQA, SWE-bench Verified, SimpleQA Verified, MirrorCode, OTIS Mock AIME, FrontierMath | per-sample in a bot-protected log viewer only | **G0** | yes | **gated**: partner ask drafted in `docs/partner-data-request.md` (branch `benchmark-results`) |
| 15 | Scale SWE-bench Pro public | SWE-bench Pro | traces viewable in Docent dashboards; no bulk download | **G0/G1** (Muse Spark 1.1, GPT-5.4, 25 models) | yes | **gated**: partner ask |
| 16 | Gaia2 / ARE (Meta) | Gaia2, 800 scenarios | leaderboard reads a **private** HF results dataset; traces only if a submitter publishes them | unknown | yes | **not usable** today (verified 401) |
| 17 | SWE-rebench (Nebius) | monthly fresh SWE tasks | leaderboard aggregates; per-instance results not in the HF README | G1 (Opus 4.6, GLM-5.1) | yes | **to check** on swe-rebench.com |
| 18 | LiveBench (HF) | LiveBench | HF `model_answer` / `model_judgment` now hold only the leaderboard parquet | — | — | aggregate only (verified) |
| 19 | HLE, BrowseComp, SWE-Lancer, PaperBench, Vending-Bench, Artificial Analysis, Vals | — | no public per-instance record | — | — | none |

---

## 2. The sources that matter for the agentic rubrics

### 2.1 Sierra's tau2 bucket — the only G0 agentic flags (verified)

The repo's `src/adele/results/sources/tau2.py` says tau2 is "aggregate only, trajectories are
maintainer-gated". **That is wrong today.** The bucket `sierra-tau-bench-public` is publicly
listable (64,157 keys) and holds 12,355 trajectory JSON files under
`submissions/<model>_<org>_<date>/trajectories/`. Each per-domain file has `tasks[]` (the task
definitions, including the user scenario) and `simulations[]`, one per (task, trial), each with
`task_id`, `trial`, `reward_info.reward`, `termination_reason`, cost, and the full `messages`.

Coverage by domain (airline 50 tasks, retail 114, telecom 2,285 in the frozen set,
banking_knowledge 97):

| batch | user simulator | models | domains |
|---|---|---|---|
| Aug 2026 (`*_sierra_2026-08-04`) | gpt-5.2 | **claude-fable-5, claude-opus-5, claude-opus-4-8, gpt-5-6-sol, kimi-k3, grok-4-5, glm-5-2, qwen3-8-max, muse-spark-1-1, inkling** | banking_knowledge only |
| May 2026 | gpt-5.2 | claude-opus-4-6, claude-opus-4-7, gpt-5-5, gpt-5-4, gemini-3-1-pro, grok-4-1-fast / 4-2 / 4-fast, gemini-2-5-pro | banking_knowledge only |
| Feb–Mar 2026 | gpt-5.2 | claude-opus-4-5, claude-sonnet-4-5, gpt-5.2 (high and no-reasoning), glm-5, qwen3.5-397b, gemini-3-pro, gemini-3-flash | airline, retail, telecom, banking_knowledge (gemini: airline/retail/telecom + a "terminal" domain) |
| 2025 | gpt-4.1 | gpt-5, gpt-4.1, gpt-4.1-mini, o4-mini, claude-3-7-sonnet, qwen3-max, toolorchestra | airline, retail, telecom |
| voice track | various | ~20 realtime/voice submissions (281–379 files each) | telecom_regular etc. |

Verified today: 22 files (11 models × airline + retail) parsed into
`tau2_pertask_rewards.parquet` in the session scratchpad (200 sims per model on airline, 456 on
retail; pass@1 ranges 0.50–0.84). The Fable 5 banking file (172 MB) parses: 97 tasks × 4 trials.
The banking_knowledge prompts are already frozen in `data/instances/instances_tau2-banking_knowledge.csv`.

Caveats. (i) The frozen telecom set collapses 2,285 tasks to ~5 prompt texts; the variation is
hidden environment state that task-text annotation cannot see. (ii) Cross-batch comparisons mix
user simulators (gpt-4.1 vs gpt-5.2). (iii) `banking_knowledge` prompts are long narratives
(median 3.3k chars), a different shape from airline/retail.

### 2.1a Snapshot drift in tau2 — verified 2026-09-14

The same tau2 task id can carry different task text in different sources. Airline task 7 reads
"upgrade to economy first" in the HuggingFace mirror `HuggingFaceH4/tau2-bench-data` (which the
2026-07 pilot used) and "upgrade to business ... (Using the CC ending in 2135)", plus an added
"You are sick.", in the sierra-research repo that `data/instances/` was frozen from.

Checked directly: **the Sierra reward files carry the frozen text, not the mirror's.** So
`data/instances/` joins the outcome data correctly. Two consequences: historical tau anchors
(r38/r39/r53/r76) are attached to the mirror text and must be re-verified by prompt hash before
reuse as ground truth; and the results-side fetchers should record a prompt hash alongside
`instance_id`, because `instances.check_join` can only see that ids match, not that the text
behind an id has changed.

### 2.2 SWE-bench Verified — dense G2 flags, text public (verified)

`SWE-bench/experiments`, split `verified`: 135 entries with `results/results.json` (resolved
ids); union universe 471 of the 500 instances. Top entries: Opus 4.5 under three scaffolds
(0.84), Gemini 3 Pro (0.82), GPT-5 under OpenHands / Prometheus (0.76–0.79), Kimi K2, GLM-4.6.
Newest: 2026-02 mini-swe-agent runs of GPT-5.2-Codex, Gemini 3 Pro, Kimi K2.5, MiniMax 2.5, and a
2026-09-01 Gemini 3.5 Flash entry with `per_instance_details.json`. **No Opus 5, Fable 5 or
GPT-5.6** anywhere in the repo; those live only in Epoch's gated viewer (source 14). Some
entries ship `trajs/` and `logs/`; the Opus 4.5 entries checked today ship results only.
Per-instance solve rate over all 135 entries is spread across the whole range (36 instances
solved by fewer than 5% of entries, 92 by more than 85%), which is what a criterion-validity
test needs.

### 2.3 Terminal-Bench 2.0 leaderboard — G1 flags, closed since May (verified)

HF `harborframework/terminal-bench-2-leaderboard`, `submissions/terminal-bench/2.0/<agent>__<model>/`,
76 submissions, each a job folder `tbench-2.1-k5-v01/<task>__<trial>/result.json` (verifier
rewards), plus `config.json`, `exception.txt`, `metadata.yaml` (model name, provider). 89 tasks × 5
trials. Models: Opus 4.7 (4 agents), Opus 4.6 (~15 agents), Sonnet 4.6, GPT-5.5 (4), GPT-5.4,
GPT-5.3-Codex (~12), Gemini 3.1 Pro (5), Gemini 3 Flash, GLM-5 / 4.7, Kimi K2.5, MiniMax M2.5 /
M2.7, DeepSeek V3.2, Qwen3.5-9B / 3.6-35B, Qwen3-Coder-480B, Grok 4.20. Trajectories are not in
the repo (the tbench.ai viewer has them). Submissions closed 2026-05-14 pending a new process, so
G0 will not appear here soon. The runbook's note that "TB 2.1 per-trial results live in Harbor
Hub's JS app" is outdated: they are in this HF repo. Task text: `harborframework/terminal-bench-2.0`
`<task>/instruction.md` (89 tasks, median 716 chars); carries no-training canaries, so it stays
out of the public repo (already gitignored under `data/`).

### 2.4 OSWorld 2.0 — G0/G1 traces for computer use (located, not opened)

HF `xlangai/osworld2.0-trajectory` holds run zips named `results_v2_gpt56sol.zip`,
`results_gpt5.5_500steps.zip`, `results_opus4.7_500steps.zip`, `claude-opus-47_300steps_run{1,2}`,
`results_sonnet4.6_500steps*.zip`, `results_minimax_m3_500steps.zip`, `result_glm-v5-turbo_500steps.zip`,
`qwen37-plus_*steps` (plus 173k files of a website demo). `xlangai/ubuntu_osworld_verified_trajs`
holds OSWorld-Verified runs for Sonnet 4.5 / 4 / 3.7 at 15/50/100 steps, UI-TARS, AutoGLM, Doubao,
EvoCUA, Holo3, CoAct, and an "intelligence-indeed" Sonnet 4.6 + Opus 4.7 run, with `all_result.json`.
This is the only source with a G0 model (GPT-5.6-sol) on a long-horizon agentic benchmark, but it
is multimodal (screenshots), so demand annotation would need SPv and the deferred multimodal set,
and the zip contents still have to be checked for per-task rewards.

### 2.5 METR time-horizon runs — G1 flags without task text (verified)

`METR/eval-analysis-public`, `reports/time-horizon-1-1/data/raw/runs.jsonl`: 24,008 runs over 228
tasks (HCAST 15,176 runs, SWAA 8,287, RE-Bench 545), with `score_binarized`, `score_cont`,
`human_minutes` (the human baseline), scaffold, tokens and cost. 21 aliases including Claude Opus
4.6, Opus 4.5, 4.1, GPT-5.3-Codex, GPT-5.2, GPT-5.1-Codex-Max, GPT-5, Gemini 3 Pro, o3, and
`human`. This is the richest per-task record of G1 agentic performance, and the human-minutes
column is a Volume anchor. The blocker is task text: HCAST tasks are private; RE-Bench (7 tasks)
and SWAA (short atomic actions) are published. Worth a targeted ask to METR for task statements
under NDA, since the outcome side is already public.

### 2.6 HAL — G2 traces on nine benchmarks (listing verified)

HF `agent-evals/hal_traces`: 381 encrypted zips, decryptable with the HAL `hal-decrypt`
script. Counts: CORE-bench 66, tau-bench airline 47, SWE-bench Verified Mini 45, SciCode 38,
GAIA 37, ColBench 36, AssistantBench 34, ScienceAgentBench 25, browser-use 19, SeeAct 18, USACO
15. Models reach Sonnet 4.5, Haiku 4.5, GPT-5 (2025-08-07), Opus 4.1, o3, o4-mini, GPT-4.1,
DeepSeek R1 / V3 / V3.1, Gemini 2.0 Flash, Gemini 2.5 Pro; Opus 4.5 appears only on CORE-bench.
Nothing from 2026. The `agentic` branch of this repo already frames HAL SWE-bench traces
(`labs/hal-traces/`, LFS), so the decrypt path exists.

### 2.7 Third-party trace corpora (G2/G1)

- **Toolathlon** (`hkust-nlp/Toolathlon-Trajectories`): 17 models × 3 runs × 108 tasks, JSONL
  trajectories; includes Opus 4.5, Sonnet 4.5, GPT-5 (high), o3, DeepSeek 3.2 thinking, Kimi K2,
  GLM-4.6, Grok 4. Official runs by the benchmark authors.
- **Exgentic agent-llm-traces-v2**: 10,057 sessions with per-session `score` and `success`
  across AppWorld (1,500), SWE-bench (1,959), BrowseComp-Plus (1,948), tau2 airline / retail /
  telecom (957 / 1,848 / 1,844), for Opus 4.5, Gemini 3 Pro, GPT-5.2, DeepSeek V3.2, Kimi K2.5
  under four harnesses (claude_code, openai_solo, smolagents_code, tool_calling). Third-party runs
  in OpenTelemetry span format; useful for per-step work because the harness is held fixed
  across models. Already downloaded under `data/downloads/exgentic`.
- **BrowseComp-Plus runs** (`Tevatron/browsecomp-plus-runs`): o3 and GPT-5 with two retrievers;
  per-query traces with encrypted answers. Already under `data/downloads/bcp_runs`.

### 2.8 Static per-instance flags (controls and discriminant validity)

- **ARC Prize dumps** (`data/downloads/arc_dump`, 72 configs): per-task attempt JSONs for Opus
  4.8 (four efforts), Opus 4.6 / 4.5, Sonnet 4.5, Haiku 4.5, GPT-5.4 (+mini/nano), GPT-5.2 (+pro),
  GPT-5.1, Gemini 3.1 Pro, Gemini 3 Deep Think / Flash, GLM-5, DeepSeek V3.2, Grok 4.20, Qwen3.
  The runbook's scraper adds Opus 5, Fable 5, GPT-5.6, Kimi K3, Inkling, DeepSeek V4 Flash. G0
  covered; puzzles, so PLp/PLs should read low and SPv high — a useful null for the agentic set.
- **MathArena AIME 2025 / 2026**: per-problem correctness, ~97 configs; the runbook uses it as
  the discriminant-validity control (agentic demands should floor).
- **HELM Capabilities v1.15.0**: per-instance predictions for 68 models × GPQA, MMLU-Pro,
  Omni-MATH, IFEval, WildBench, in the `crfm-helm-public` GCS bucket
  (`capabilities/benchmark_output/runs/v1.15.0/<run>/`). Newest models Gemini 3 Pro, GPT-5.1,
  Sonnet 4.5, Haiku 4.5, Grok 4, Kimi K2, DeepSeek R1-0528. Joins the v1 cognitive dimensions.
- **ForecastBench**: the tarball in this folder holds question sets from 2024-07-21 to
  2026-08-02 with per-question forecasts for many model configs; the newest round includes
  Claude Fable 5, Opus 4.8 / 4.7 and Haiku 4.5. Outcomes resolve continuously. Rounds r66 / r67
  found the corpus low on PLs under the current doctrine and the criterion (Brier) contaminated
  by irreducible outcome entropy, so this is a secondary source.

### 2.9 Gated or absent

- **Epoch AI hub**: the only G0 per-sample record for GPQA, SWE-bench Verified, SimpleQA
  Verified, MirrorCode, OTIS Mock AIME and FrontierMath (Fable 5, GPT-5.6, Kimi K3), behind a
  bot-protected log viewer. The partner protocol and extractor script are on branch
  `benchmark-results` (`docs/partner-data-request.md`, `scripts/extract_scores_standalone.py`).
- **Scale SWE-bench Pro public**: 25 models led by Muse Spark 1.1 and GPT-5.4; trajectories
  are visible per model in Docent dashboards (docent.transluce.org) but there is no bulk
  download. Ask Scale / Transluce for `(instance_id, model, resolved)`.
- **Gaia2**: the leaderboard space reads `meta-agents-research-environments/leaderboard_results`,
  which returns 401 (private). Submitters may publish their own trace datasets; none found for
  frontier models.
- **SWE-rebench** (Nebius): monthly fresh tasks with Opus 4.6 / GLM-5.1 on top; per-instance
  results are not documented on the HF dataset; the leaderboard site needs a check.
- **HLE, BrowseComp**: no per-instance data at any generation (runbook, unchanged).
- **LiveBench**: the HF `model_answer` / `model_judgment` repos now contain only the leaderboard
  parquet; per-question answers are no longer published there.

---

## 3. Coverage by generation

| benchmark (source) | G0 | G1 | G2 | text public |
|---|---|---|---|---|
| tau2 banking_knowledge (Sierra S3) | **traces** | traces | traces | yes (frozen) |
| tau2 airline / retail / telecom (Sierra S3) | — | — | traces | yes (frozen) |
| Terminal-Bench 2.0 (HF leaderboard) | — | **flags** | flags | yes (canary) |
| OSWorld 2.0 (HF) | traces (GPT-5.6-sol) | traces | — | yes |
| METR HCAST / SWAA / RE-Bench | — | **flags** | flags | mostly no |
| SWE-bench Verified (experiments) | — | a few | **flags** (135 entries) | yes |
| HAL nine benchmarks | — | — | traces | yes |
| Toolathlon, Exgentic, BrowseComp-Plus | — | some | traces | yes |
| ARC-AGI (Prize dumps) | flags | flags | flags | yes |
| AIME (MathArena) | flags | flags | flags | yes |
| HELM Capabilities | — | — | flags | yes |
| ForecastBench | forecasts | forecasts | forecasts | yes |
| GPQA / SWE-V / FrontierMath (Epoch) | gated | gated | gated | yes |
| SWE-bench Pro (Scale) | gated | gated | — | yes |

---

## 4. What this implies for the plan

1. **Pilot order.** SWE-bench Verified (G2 flags, dense, text public) → tau2 airline / retail
   (G2 traces, 11 models, prompts frozen) → Terminal-Bench 2.0 (G1 flags, 76 submissions,
   held-out benchmark family). This matches the order proposed in the session, and all three
   are downloadable today without a partner.
2. **The G0 story runs through tau2 banking_knowledge, ARC and the Epoch ask.** If the goal is
   an envelope that extrapolates to the current generation, banking_knowledge (97 tasks, Fable 5,
   Opus 5, GPT-5.6-sol, Kimi K3) is the only agentic set where that can be tested now; ARC gives
   a static G0 anchor; Epoch is the ask that would add SWE-bench Verified and GPQA for G0.
3. **Two repo corrections.** `tau2.py` should become an instance-level fetcher reading the S3
   bucket (schema above); the runbook's Terminal-Bench note should point at the HF leaderboard
   repo. Both belong on `benchmark-results`.
4. **Per-step work has more data than the plan assumed.** Sierra (all messages), Toolathlon,
   Exgentic (span-level, harness fixed) and OSWorld give unencrypted trajectories without HAL's
   decrypt step, and Exgentic's fixed-harness design is the cleanest for comparing models on the
   same transitions.
5. **METR is worth an ask.** Public outcomes plus human baselines for 228 tasks and G1 models,
   missing only the task text.

---

## 5. Verification log (2026-09-14)

All artefacts are in the session scratchpad, not in the repo:
`swe-experiments/` (sparse clone, 4.1 MB, 135 verified entries) → `swebench_verified_results.parquet`
(63,585 rows) and `swebench_verified_solverate.csv`; `swebench_verified_instances.parquet` (HF, 500
rows); `tau_s3_keys.txt` (64,157 keys) → `tau2_pertask_rewards.parquet` (11 models × airline +
retail); `tau_fable5_banking.json` (172 MB, 388 simulations); `tb2_tasks/` (89 instruction.md);
`tb2_leaderboard/` (per-trial result.json for 14 submissions, download in progress);
`metr_runs.jsonl` (24,008 runs); `helm_cap_runspecs.json` (340 run specs). HF listings for
`agent-evals/hal_traces`, `xlangai/osworld2.0-trajectory`, `xlangai/ubuntu_osworld_verified_trajs`,
`hkust-nlp/Toolathlon-Trajectories`, `Exgentic/agent-llm-traces-v2`, `Tevatron/browsecomp-plus-runs`,
`livebench/*`, `nebius/SWE-rebench*` were read but not downloaded.

---

## 6. Quality audits, and which audited benchmarks have per-task data (added 2026-09-26)

This adds a quality filter the survey above does not apply. Epoch's Benchmark Reviews (rubric
v1) label a benchmark *Flawed* when at least 20% of an inspected sample has scoring errors, or
when version drift, crippled elicitation or setup bias corrupt the results. BenchJack (arXiv
2605.12673, 2026) tests whether an agent could reward-hack a benchmark's harness. Everything
below was checked on 2026-09-26 by reading the cited pages (and, for SWE-rebench, the page
source); no data was downloaded.

**Failed an audit** (per-task data exists, but the flags are suspect): SWE-bench Verified (Epoch
*Flawed*, 2026-09-03: OpenAI's audit of the 138 tasks o3 could not reliably solve found 59.4%
with tests that reject correct fixes, a floor of 16.4% of all 500; contamination; BenchJack about
100% hackable), SWE-bench Pro (*Flawed*; about 100% hackable), Terminal-Bench (4.0.0 *Flawed*:
30 of 66 tasks with public defects, listed by name in the review; about 100% hackable), and
MLE-bench (about 100% hackable). Hackable means an agent could fake success, not that published
results were faked.

**Epoch *Verified*** (4 of its 15 reviews) and their per-task data:

| benchmark | per-task data | models | limits for ADeLe |
|---|---|---|---|
| ExploitBench v0.1 (41 V8 bugs; 2026-09-12) | per-bug × model grid on exploitbench.ai, graded on a 5-tier, 16-flag ladder; transcripts captured as "audit bundles", not public | 20 configurations incl. GPT-5.5, Claude Opus 4.7, Claude Mythos Preview, Gemini 3.1 Pro, Kimi K2.6, GLM 5.1 | grid viewable, not downloadable; task framing inside the public images `ghcr.io/exploitbench/v8-r1` |
| PostTrainBench v1.1 (2026-09-09) | 1,338 trajectories with full traces and `metrics.json`, HF `aisa-group/PostTrainBench-Trajectories` (Apache-2.0) | Claude Code, Codex CLI, Gemini CLI and OpenCode configurations | 28 near-identical tasks (7 target evals × 4 base models), so little demand variance |
| WeirdML v2 (2026-08-10) | per-task results per model (WeirdML site; `htihle/weirdml-time-horizons`) | many | only 23.5% of task texts are public |
| SimpleQA Verified (2026-09-10) | no per-question agent data found | — | static QA; at most a control |

**Patched after BenchJack:** OSWorld and WebArena went from highly hackable to 0% after three
patch rounds. OSWorld-Verified trajectories are on HF (`xlangai/ubuntu_osworld_verified_trajs`,
MIT, 15+ model variants); whether the zips carry per-task scores is not yet confirmed.

**No public per-task results:** SWE-rebench (the site embeds only per-date-window aggregates and a
problem list with PR links; ask Nebius), ITBench-AA (the HF release has the 40 public SRE tasks
but no per-model results), GDPval (220 public tasks; no per-task model grades found), and Qwen's
AgentWorldBench (no success labels).

**Implication.** ExploitBench is the only benchmark found that is Epoch-*Verified*, covers the
current generation and grades every task: the strongest candidate for the demand-predicts-success
test, pending an export of its per-bug grid and a check that judges rate exploit tasks without
tripping safety flags. PostTrainBench suits trace-level work. Everything else either failed an
audit or lacks public per-task results.

---

## Appendix — a first Opus pass on 14 SWE-bench Verified items (preliminary)

Run before this survey was requested, kept here so it is not lost. One judge (Claude Opus via a
subagent, one item per call, `#!` line stripped by `catalog.py`, examples kept), rubrics as on
`rubrics/v2-improved` (PLp v2-r43, PLe v2-r45, PLs v19). Twelve items stratified by
all-entry solve rate plus the two pilot anchors (swe-0090 = django-12858, swe-0461 = sympy-17630).

| instance | solve rate | PLp | PLe | PLs | anchor |
|---|---|---|---|---|---|
| matplotlib-26208 | 0.01 | 2 | 3 | 1 | |
| sphinx-10435 | 0.02 | 1 | 3 | 1 | |
| sympy-17630 | 0.02 | 2 | 3 | 1 | PLs 1 (v11 ruling) ✓ |
| matplotlib-25960 | 0.08 | 2 | 3 | 1 | |
| scikit-learn-25102 | 0.31 | 3 | 3 | 1 | |
| django-13568 | 0.39 | 2 | 3 | 1 | |
| sphinx-8593 | 0.44 | 2 | 3 | 1 | |
| django-16032 | 0.54 | 2 | 3 | 1 | |
| django-12858 | 0.66 | 2 | 3 | 1 | PLs 2 (r53) ✗ by 1; PLe 3 = r39 judges, Pablo 2 |
| django-13343 | 0.69 | 2 | 3 | 1 | |
| django-11451 | 0.79 | 1 | 3 | 1 | |
| sympy-13372 | 0.81 | 2 | 3 | 1 | |
| astropy-7671 | 0.84 | 1 | 3 | 1 | |
| django-13820 | 0.90 | 1 | 3 | 1 | |

Reading: on SWE-bench Verified problem statements, PLe is constant at 3 (elected self-checking:
run the tests) and PLs constant at 1 (the executability clause), so neither can carry
criterion validity on this benchmark; PLp spans 1–3 and correlates −0.42 (Spearman, n = 14) with
solve rate. That is consistent with r38 / r39 and the v11 ruling, and it is an argument for
tau2 and Terminal-Bench as the benchmarks where the agentic set has room to vary. Single judge,
14 items: indicative only.
