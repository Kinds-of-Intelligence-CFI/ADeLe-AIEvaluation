# CooperBench: tasks, what the agents see, outcomes (fetched 2026-10-03)

Benchmark slug: `cooperbench`. Data only: no judge calls, no labels.
Paper: "CooperBench: Why Coding Agents Cannot be Your Teammates Yet", arXiv 2601.13295 (v2, 2026-01-26).

12 repositories, 30 task pools (one real PR each), 199 features, 652 feature pairs
(all pairs within a pool). Pool sizes run from 1 pair (huggingface_datasets/7309) to 66
(pallets_click/2068). Languages by pair: Python 560, Rust 45, TypeScript 25, Go 22.
(The paper text says "34 pools" and "52 task sets" in places; the data have 30 pools.)

## Sources

| What | Where | Pinned revision | Licence |
|---|---|---|---|
| Feature texts as the runs saw them, gold patches, subsets | github.com/cooperbench/CooperBench `dataset/` | `6da33519` (2026-02-01) | MIT (pyproject, README; no LICENSE file, GitHub shows none) |
| Spec audit, gold conflict report, later fixes | same repo | `63b9d44d` (2026-09-14, HEAD) | same |
| Paper runs: logs, patches, merge reports, test results | HF `CooperBench/trajectories` | `906bc2f6` (2026-01-28) | MIT |
| Leaderboard per-pair coop results and totals | github.com/cooperbench/website (serves cooperbench.com) `public/static/data/{coop,coop_git}/index.json`, `src/pages/leaderboard.astro` | `97dbb0ab` (2026-03-26); live site files identical on 2026-10-03 | **none stated** |
| GPT-5.5 (codex) runs: solo, coop+git, team | HF `CooperBench/team-trajectories` | `dd371629` (2026-05-23) | Apache-2.0 |
| Same team runs reshaped (not used) | HF `CooperBench/team-coop` | `7348f4ba` | MIT |
| Task dataset mirror (not used; post-audit texts) | HF `CooperBench/cooperbench-dataset` | `b612b1a3` (2026-09-05) | MIT |
| Gemini 3 Flash mini-swe-agent solo run (not used) | HF `CooperBench/cooperbench-trajectories` | `51ad52c5` | none; pass rate 35.9%, matches no leaderboard row |

robots.txt of cooperbench.com has no directives (only Cloudflare content-signal comments).
arXiv HTML fetched once (allowed). No login, no gated data. About 0.5 GB cached under
`data/downloads/cooperbench/` (merge reports and test results 336 MB, team tarballs 107 MB).

## Conditions and what each agent sees

The paper harness (OpenHands v0.54, CodeAct agent; runs Oct-Dec 2025) has **two phases**.
Phase 1 is planning: a custom tool loop with read-only tools that ends when the agent calls
`agreement_reached(plan=...)`. Phase 2 is implementation in OpenHands, with that plan pasted
into the user message. The paper does not describe the planning phase; the logs show it.

Template source. The text below is copied from the agents' own logs in
`CooperBench/trajectories@906bc2f` (pair pallets_click/2068 f1-f2, Claude). `fetch_tasks.py`
re-downloads those logs and asserts every template piece matches (whitespace-normalised).
The public harness repo at `328e7e0` (2026-01-27) has close but different templates:
`execution/templates/task_prompt.j2` matches; `execution/templates/coop_prompt.j2` puts the
SCENARIO and COORDINATION text in the user message, while the runs had it in the system
prompt; `planning/templates/coop.j2` has an older workflow text. Paper App. D quotes a merged
version. The logs are the ground truth. Feature texts in the logs match the repo at
`6da33519`, not HEAD (HEAD has audit edits; see defects).

| | solo | coop | coop_wo_comm |
|---|---|---|---|
| Agents | 1, both features | 2, one feature each | 2, one feature each |
| Partner's feature text shown | n/a | no | no |
| Phase 1 system prompt | "UNIFIED implementation plan for TWO features" + both texts | "YOUR FEATURE (SEPARATE FROM THE OTHER AGENT)" + own text; "Another agent is implementing a DIFFERENT feature ... Coordinate with them"; "REACH AGREEMENT FIRST"; example `communicate_with_agent` calls | same as coop |
| Phase 1 user message | "Create a unified implementation plan for both features." | "Begin working on your feature. Collaborate with the other agent as needed." (+ partner messages appended as history) | same as coop |
| Phase 1 tools | list_files, read_file, grep_search, agreement_reached | + communicate_with_agent | same as coop |
| Phase 2 system prompt | generic OpenHands prompt (~11.5k chars) | generic + `<COLLABORATION>` block (separate branches, 2-way merge, give exact file paths and line numbers, no insertion markers, final status message) | generic only |
| Phase 2 user message | both feature texts + plan + GUIDELINES (no git, clean up test scripts) | "You are agent_N working on the following feature in parallel with another agent." + feature + plan + "YOUR TASK" (messaging via MCP tools) | own feature + plan + GUIDELINES |
| Phase 2 tools | execute_bash, str_replace_editor, execute_ipython_cell, think, task_tracker, fetch, finish, browser | same minus browser, plus openhands_comm_send, openhands_comm_get | same as solo |

Key facts:
- **coop_wo_comm is not "no communication".** Its plans are byte-identical to coop's (1,294
  of 1,294 plan files checked in 4 pools). The plans came from the joint messaging phase and
  name the partner's feature and file ownership. Only phase 2 has no messaging.
- The partner's feature text is never shown. An agent learns it only from messages (or, in
  phase 2, from its own plan's coordination notes).
- The coop phase-2 system prompt also carries a coop-only line in its generic part: print
  statements must contain "[YOYOYO]". Harness artefact; not in the prompts here.
- Plan/agent numbering is sometimes crossed in the logs (the agent_1 plan calls itself
  "Agent 2"). Cosmetic, model-written.

The Gemini configs (Feb 2026) and GPT-5.5 runs (May 2026) used the newer `cooperbench`
harness: one phase, no planning tool, messaging by shell commands (`coop-send`,
`coop-broadcast`, `coop-recv`), optional shared git remote (`_coop/prompt.py`, e.g. at
`0c6fd1c`, v0.0.15). Their prompts are **not** built here.

## Instance file

`data/instances/instances_cooperbench.parquet`: 1,956 rows = 652 pairs × {solo, coop,
coop_wo_comm}. `instance_id` = `<repo dir>-<task id>-f<a>-f<b>@<condition>`, e.g.
`pallets_click_task-2068-f1-f2@coop`. Columns benchmark, instance_id, prompt, prompt_sha12.
Not registered in INSTANCES.tsv (left to Pablo).

Prompt layout: a title; one "Context for the reader (not shown to the agents)" paragraph
(setup and success rule); then "What the agent sees" (solo) or "Agent 1 sees" / "Agent 2
sees" (coop conditions), each with Phase 1 and Phase 2: tools, system message, user message,
verbatim inside `<<<` `>>>`. Three edits to the verbatim text:
1. The model-written plan is replaced by `[PLAN: ...]`.
2. In phase 2 the feature text is replaced by `[FEATURE...: the same feature text as in
   phase 1 is repeated here verbatim]`. This saves ~2.5k chars per agent.
3. The generic OpenHands system prompt is one sentence; the coop `<COLLABORATION>` block is
   verbatim.

`data/instances/meta_cooperbench.csv`: one row per instance. Columns: pair_id, condition,
repo, language, task_id, feature_a, feature_b, pool size, titles, feature text lengths,
prompt_chars, `gold_conflict` (git merge of the two gold patches conflicts; from
`gold_conflict_report.json`), gold files touched per feature and shared (`gold_shared_files`,
list), `spec_changed_after_runs` / `tests_changed_after_runs` (features whose feature.md /
tests.patch changed between `6da33519` and HEAD), `task_infra_changed_after_runs` (Dockerfile,
runner.sh, run_tests.sh, setup.sh or combined.patch changed), `subsets` (lite, flash).

Prompt lengths (chars):

| condition | min | p10 | median | p90 | max | > 24k |
|---|---|---|---|---|---|---|
| solo | 4,375 | 5,962 | 7,897 | 11,393 | 16,655 | 0 |
| coop | 13,293 | 14,881 | 16,807 | 20,304 | 25,561 | 7 |
| coop_wo_comm | 10,977 | 12,565 | 14,491 | 17,988 | 23,245 | 0 |

Feature texts: median 2,122 chars (651-6,925). Gold conflicts: 499 of 652 pairs (76.5%).
Every pair's two gold patches touch at least one common file.

## Outcomes

### Definition

- **Solo**: both features' hidden tests pass on the single patch (`both_tests_passed`).
- **Coop** (and coop_wo_comm): the two patches are merged; the pair passes if both test
  suites pass after the first merge step that works: naive git merge (only if conflict-free),
  then union merge, then a small LLM resolver (Qwen3-Coder 1.5B fine-tune). Source:
  `scripts/generate_coop_index.py` in the website repo (it reads `aggregated_results_*`
  fields `feature{1,2}_{naive,union,llm}_merge_test_passed` and `has_naive_merge_conflict`);
  paper sec. 2.2 and App. E (Table 6 "LLM" column). In merge reports the same fields sit
  under `features.featureN`, with `merge_analysis.status == "clean"` for no conflict.
- Leaderboard denominator is 652; a pair with no result counts as a fail.

### Verification against the official leaderboard

- **Coop, all 8 leaderboard configs: exact.** The site's per-pair `passed` (website
  `coop/index.json`, `coop_git/index.json`) sums to the leaderboard: GPT-5 182 (27.91%;
  the leaderboard prints 27.95, the paper 27.90), Claude 169 (25.92), MiniMax 91 (13.96),
  Qwen3-Coder 87 (13.34), Qwen3 30 (4.60), Gemini Flash SDK 171 (26.23), Gemini Pro mini-swe
  133 (20.40), Gemini Flash mini-swe 80 (12.27); with git 181 (27.76), 142 (21.78), 99 (15.18).
  These match paper Table 6 "With-comm LLM" too.
- **Coop from the HF merge results (the MIT data): not exact.** Only Qwen3 matches (30/30,
  607/607 pairs agree). Per-pair agreement with the site: GPT-5 570/591, Claude 569/607,
  Qwen3-Coder 574/590, MiniMax 410/465. Most disagreements are site pass / HF fail, so the
  site likely holds a later re-evaluation. HF covers 465-607 pairs per model.
- **The site's own `missing` flag is unreliable**: 81 GPT-5, 45 Claude, 312 MiniMax, 116
  Qwen3-Coder, 45 Qwen3 pairs are flagged missing, yet 3 GPT-5 and 56 MiniMax of them pass.
- **Solo (HF only; the site has no per-pair solo data): exact only for Qwen3-30B**
  (41/652 = 6.29% vs 6.3%). Pass rate over pairs with a result vs leaderboard: GPT-5 48.2%
  (n=593) vs 48.3; Claude 46.2% (n=532) vs 47.1; Qwen3-Coder 19.1% (n=597) vs 21.6;
  MiniMax 31.4% (n=652, full coverage) vs 36.2. So MiniMax and probably Qwen3-Coder solo
  results on HF are from an earlier evaluation than the leaderboard's. Missing solo pools:
  Claude lacks tiktoken/0, typst/6554 and the 3 Pillow pools (120 pairs); GPT-5 lacks most of
  jinja/1559 and click/2800 (59 pairs).
- **coop_wo_comm (HF only) vs paper Table 6 no-comm**: Qwen3 3.40% over 500 pairs vs 3.37%;
  the others cover 456-544 pairs and fall short of the paper's totals.
- **GPT-5.5 / codex (not on the leaderboard)**: matches its own README: solo 362/652,
  coop+git 329 (645 pairs with pass/fail; README 329/650), team 390/636, team without
  protocol 403/651. summary.json and eval.json agree on every pair.
- Gemini solo per-pair results are not public (only totals on the leaderboard).

`leaderboard_check.csv` has every number above.

### Files

- `outcomes.csv` (tracked; MIT / Apache-2.0 sources only): one row per (pair, condition,
  config) with a result. 10,948 rows. Columns: success, feature_a_pass / feature_b_pass (solo),
  naive_conflict, naive_ok, union_ok, llm_ok (coop), per_pair_file_agrees (aggregate vs the
  per-pair file, where both exist), source, data_source. Configs: gpt5, claude, minimax,
  qwen_coder, qwen (paper harness: solo, coop, coop_wo_comm); gpt55_codex_* (solo, coop_git,
  team, team_noproto).
- `data/raw/cooperbench/outcomes_site.csv` (gitignored; no licence): site per-pair results,
  652 pairs × 8 coop configs + 3 coop_git configs = 7,172 rows, with `site_missing_flag`
  and `success_hf` for comparison. **This is the official coop outcome.**

Counts with a result (pairs of 652):

| config | solo | coop (HF) | coop (site) | coop_wo_comm | other |
|---|---|---|---|---|---|
| GPT-5 | 593 | 591 | 652 | 500 | |
| Claude Sonnet 4.5 | 532 | 607 | 652 | 499 | |
| MiniMax-M2 | 652 | 465 | 652 | 544 | |
| Qwen3-Coder-30B | 597 | 590 | 652 | 456 | |
| Qwen3-30B | 607 | 607 | 652 | 500 | |
| Gemini ×3 configs | 0 | 0 | 652 each | 0 | coop_git 652 each |
| GPT-5.5 codex | 652 | | | | coop_git 645, team 636, team_noproto 651 |

Models and runs. Paper runs: GPT-5 and MiniMax-M2 via their APIs, Claude Sonnet 4.5
(`claude-sonnet-4-5-20250929`, via Bedrock in the logs; the paper says GCP), the two Qwen
models via vLLM. k=1 (one run per pair). Phase-1 logs from 2025-10-14, phase-2 logs from
2025-11-11, merge evaluations 2025-10-17 to 2025-12-16 (dates in `generated_at`). Gemini
configs: `gemini-3-{flash,pro}-preview`, openhands-sdk or mini-swe-agent, cooperbench
harness ~v0.0.3-0.0.5 (Feb 2026; exact commit unknown). GPT-5.5: `gpt-5.5-hao` (Azure), codex
agent, runs started 2026-05-21, harness ~v0.0.15.

Mean solo minus coop success per pair (pairs with both): GPT-5 0.20, Claude 0.18, MiniMax
0.18 (but its solo is stale), Qwen3-Coder 0.05, Qwen3 0.02, GPT-5.5 (solo minus coop+git) 0.05.

## Known defects and caveats

- **Tests and specs were fixed after the runs.** All leaderboard runs predate the 2026-08-14
  gradeability audit (v0.0.29) and the 2026-09-05 combined.patch pass (CHANGELOG,
  `dataset/SPEC_AUDIT.md`). At run time 24 features were not gradeable (12 runner.sh never ran
  the feature's tests, 8 dependency drift, 5 tests carrying feature 1's expectations, 2 tests
  that did not discriminate, 1 overlapping hunks). pallets_jinja/1621 f5 passed on an untouched
  tree. 19 features failed against combined.patch: dspy/8563 f2-f6 (8/15 pairs hard zeros),
  dspy/8635 f1-f6 (5/15), tiktoken/0 f3 (issue #44, param name mismatch), jinja/1559 f3,
  jinja/1465 all 10. Earlier fixes: PRs #38-#43, #46 (Mar-Apr 2026). From git diffs: 134
  pairs contain a feature whose feature.md changed later, 61 one whose tests.patch changed,
  356 pairs sit in a pool whose Dockerfile/runner/combined.patch changed; 422 pairs have any
  of these. Flags are in the meta CSV. Which fixes predate which run is not recoverable.
- **Feature texts**: the agents saw the pre-audit texts (verified for one pair). The audit
  added contracts to 23 feature.md files. Our prompts use the pre-audit texts.
- **Missing results** count as fails on the leaderboard. For per-pair analysis use only pairs
  with a result; the site's `missing` flag does not tell you which those are.
- **One run per pair (k=1)**: per-pair success is a single Bernoulli draw.
- **Asymmetric agents**: coop runs fix feature a as agent 1. The paper says cross-model and
  swapped pairs double the count; only self-play runs are public.
- **Communication ablation is confounded** (coop_wo_comm keeps the jointly negotiated plans).
- **Harness drift**: Gemini and GPT-5.5 results come from a different harness than the
  prompts we built.
- Paper says 77.3% of tasks have conflicting gold solutions; the gold report says 76.5%.
- GitHub issues: only #44 (closed) is a task defect; #81 asks about leaderboard submissions.

## Decisions for Pablo

1. **Unit and conditions.** Proposal: (pair, condition) with solo and coop for the main study.
   Add coop_wo_comm only as a small check (its plans were negotiated with messaging, so it
   is not a clean no-communication condition). Recommend: solo + coop.
2. **Context paragraph.** Each prompt has one "not shown to the agents" paragraph with the
   setup and the success rule (merge, both test suites). It helps the judge read a two-agent
   prompt, but it is not agent-visible text. Recommend keep; the alternative is to drop it.
3. **Prompt edits.** Plan replaced by a placeholder; repeated feature text deduplicated;
   generic OpenHands prompt summarised. Recommend keep. Seven coop prompts exceed 24k chars
   (max 25.6k); recommend accept.
4. **Coop outcome source.** The official per-pair coop results are on the unlicensed
   website repo (matches the leaderboard exactly). The MIT HF data disagree on 3-12% of pairs
   per model. Recommend: use the site data for analysis, keep it in `data/raw/` until you
   decide whether committing it is fine (facts, low risk, as with DeepSWE).
5. **Solo outcome source.** Only HF. Use GPT-5, Claude and Qwen3 as is; flag MiniMax and
   Qwen3-Coder solo as stale (they do not match the leaderboard). Optionally add GPT-5.5
   (solo vs coop+git, complete, but a newer harness with different prompts and git).
6. **Defective pairs.** Recommend: keep all pairs in the instance file, and in the analysis
   run a sensitivity check without the 422 flagged pairs (or at least without the 61 pairs
   with changed tests and the dspy/8563, dspy/8635, jinja/1465, jinja/1621-f5 pairs).
7. **Labelling sample** (≈1,200-1,400 judge calls at 5 rubrics):
   120 pairs × {solo, coop} = 240 prompts = 1,200 calls; optional 40 of them × coop_wo_comm
   = +200 calls. Rule (seed 0): stratify by task pool. Take min(pool size, 2) pairs from each
   of the 30 pools, then fill to 120 by largest-remainder allocation in proportion to the
   pairs left in each pool; within a pool draw uniformly
   (`DataFrame.sample(n=k, random_state=rng.integers(2**31))`, `rng = numpy.random.default_rng(0)`,
   pools in sorted order, pairs sorted by pair_id). Result: 1-9 pairs per pool, 80% gold
   conflicts (population 76.5%), Python 100, Go 7, Rust 7, TypeScript 6.
   Why: the planned test regresses each pair's solo-minus-coop drop on the coop prompt's MSc
   and MSm, holding the solo prompt's coding demands fixed (or using pool fixed effects).
   Two pairs per pool allow within-pool contrasts; proportional fill keeps the big pools
   (click/2068: 66 pairs) from dominating, unlike the uniform "lite" subset. Labelling the
   solo version of the same pairs gives the coding-demand control. Power is limited: the drop
   is binary per model and k=1; averaging GPT-5, Claude and GPT-5.5 drops gives a 0-1 drop
   in thirds for ~470 of 652 pairs. Alternative: restrict to the 463 pairs with solo results
   for all 5 paper models (loses typst, tiktoken and Pillow).
8. **Registration.** `INSTANCES.tsv` not edited.

## Reproduce

```
python experiments/benchmarks/cooperbench-data/fetch_tasks.py     # ~1 min after clone; checks templates against logs
python experiments/benchmarks/cooperbench-data/fetch_outcomes.py  # ~15-30 min first time (HF rate limits, ~9k small files)
```
Both cache under `data/downloads/cooperbench/`. HF returns 429s on anonymous bulk
downloads; huggingface_hub retries on its own.
