# Mass annotation — plan (draft, 2026-10-01, not pushed)

**Goal.** Full demand profiles for the benchmarks we can join to per-task results: the v1 rubrics, the adopted
v2 planning family, and the memory rubrics. Then the analyses that need them: demand profiles, SCCs and ability
profiles, and above all incremental prediction (desideratum 9), which no v2 rubric has yet.

## 1. What gets annotated

**Benchmarks (tier 1).** The three with current-generation per-task results in `data/results/panel.parquet`, on the
same task sets as the PL labels, so every rubric covers the same tasks:

| benchmark | tasks | note |
|---|---|---|
| SWE-bench Verified | 442 (the PL set) | 434 verifiably solvable; one prompt > 24k chars (truncation rule needed) |
| tau2 airline / retail / banking | 232 (the PL set) | frozen texts; telecom skipped: 2,280 of 2,285 instances share one text |
| Terminal-Bench 4.0.0 | 66 | 30 tasks with Epoch-listed defects are annotated but flagged |
| **total** | **740** | |

Tier 2 (later, separate plan): HAL's benchmarks (USACO, AppWorld, CORE-bench, GAIA, SciCode…), which have per-task
results for several models but need ingest work. Tier 3: Epoch-Verified benchmarks without per-task agent data
(demand profiles only, no SCCs).

**Rubrics per task.**

| set | codes | judged per task | status |
|---|---|---|---|
| v1 (DeLeAn 1.0) | AS AT CEc CEe CL KNa KNc KNf KNn KNs MCr MCt MCu QLl QLq SNs VO | 17 | published, canonical |
| MSm | v2 MSm (= v1 MSm + one L4/L5 carve-out) replaces v1 MSm | 1 | lab-validated |
| MSc | v2 | 1 | lab-validated (v2-draft) |
| memory | MMe MMp MMs (Marko) | 3 | **never lab-tested**: gate in §3 |
| PL | PLp (O), PLe, PLs | 0 | already labelled (`plp-o-relabel`, `pl-relabel-v2`) |
| UG | computed from answer format | 0 | all these tasks are open-ended → 100 |

**22 judged rubrics × 740 tasks = 16,280 calls.**

## 2. Protocol (unchanged from the PL runs)

One call per (task, rubric); Opus 5.5 at effort low via `adele-judge-v2-low`; the v2 prompt; rubric as the catalog
serves it, examples kept; frozen task texts with hashes; writers check (other-model answers set aside, one retry, then
no label); protocol check per run; coverage diffed against the index after every relay (relays drop cells). Labels
carry the rubric generation (`v1/AT`, `v2/MSm`) so v1 and v2 codes never collide.

## 3. Gates before the bulk run (each pre-registered)

1. **Dry run** (~50 calls): 2 tasks per benchmark × all 22 rubrics. Checks parsing, prompt sizes, cost per rubric.
2. **v1 bridge** (~1,100 calls): 60 v1-battery instances (stratified over its 20 benchmarks) × 18 v1 rubrics,
   compared with the published GPT-4o labels. Per dimension: exact, within one, mean shift. Bar: within one ≥ 0.85
   and |shift| ≤ 0.3. Dimensions that miss are still annotated, but marked "not comparable to the v1 battery".
   Without this, our v1 labels (new judge, new prompt) cannot be merged with the paper's.
3. **Memory rubrics, lab-lite** (~360 calls): their own examples placed with examples stripped (three repeats), plus
   ~30 neighbouring examples (PLe, AS, MCr, CEc) checked for leaks. Bar: ≥ 65% of examples at their own level, none two
   levels off (PLp itself scores 65–85% here). If it fails, memory is run as exploratory or deferred (your call; Marko
   should see the result either way).
4. **Noise floor** (~500 calls, run inside the bulk): 3% stratified re-judge, per rubric. Plus a fixed 60-cell anchor
   set re-judged at the start of each week, to catch judge drift (Opus 5.5 cannot be pinned to a snapshot).

## 4. Analyses (pre-registered before any bulk label)

- Demand profiles per benchmark and domain, all 25 rubrics.
- Per rubric: Spearman with solve rate within benchmark/domain (descriptive). VO against SWE time to fix and
  Terminal-Bench expert hours (a direct criterion check for VO).
- **Incremental prediction (desideratum 9)**: predict per-(task, model) success from the demand vector plus model,
  grouped CV by task, nested sets: v1 → v1 + PL → v1 + PL + MS → + memory. Metric: AUC and Brier, with task-bootstrap
  CIs. This is the result the team needs.
- SCCs and ability profiles for the bridging models in the panel.

## 5. Cost and schedule

Calibration from the last runs: an Opus-low call costs about 0.005 weekly points and 0.04% of a 5-hour window,
orchestration included.

| | calls | weekly points | 5-hour windows |
|---|---|---|---|
| gates 1–3 | ~1,500 | ~8 | ~0.6 |
| bulk | 16,280 | ~90 | ~6.5 |
| noise + anchors | ~700 | ~4 | ~0.3 |
| **total** | **~18,500** | **~100** | **~7.5** |

That is one full week of the Max plan. **Route A (subscription):** spread over ~2 weeks at ≤ 55%/week, so your own
work keeps room; ~2,000 calls per window, run at window resets. **Route B (Anthropic Message Batches API):** about
$0.02–0.03 per call at batch prices → roughly $350–550 in total, done in a day, needs an API key and a ~200-call
bridge check (API judge vs subagent judge), plus a small Anthropic batch backend in `adele.annotation` (OpenAI's
exists).

## 6. Engineering

One reusable runner instead of per-study scripts (`experiments/benchmarks/mass-annotation/`): build prompts for any
(benchmark × rubric) grid with hash manifest; shard into relay batches; a state file of done / missing / fallback cells
so any fresh session can resume ("launch next 4 relays"); generic writers, collect and protocol checks. Tests on a toy
grid. Promote into `src/adele` later, with your OK.

## 7. Risks

Budget contention with your live sessions (stop at 85% weekly); judge drift (anchor set); safety-classifier stops on
cyber-flavoured tasks (expect a few unlabelled cells); memory rubrics unvalidated; SWE-bench contamination and
Terminal-Bench defects (flag, analyse with and without); orchestrator context (rotate sessions every ~40 relays).

## Decisions (Pablo, 2026-10-01)

1. **Scope:** tier-1 benchmarks that Epoch approves, plus rivercross; WeirdML if it can be scored. Note: no tier-1
   benchmark is Epoch-Verified (SWE-bench Verified and Terminal-Bench 4.0.0 are Flawed; tau2 is not reviewed). Epoch's
   Verified four are ExploitBench, SimpleQA Verified, PostTrainBench and WeirdML v2; only 6 of WeirdML v2's 19 tasks are
   public. Final choice with the team.
2. **Budget:** subscription plus $250 of cloud-session credits; the judge may change (e.g. OpenAI). **Nothing is run
   now: build the runner, judge-agnostic and easy to launch** (see `ARCHITECTURE.md`).
3. **MSm:** v2 MSm only.
4. **Memory rubrics:** wait for the team. The runner must make adding them a one-line spec change.
