# panel — every benchmark's results on equal footing

Owner: Pablo. One table of the public per-task results the benchmark studies use: SWE-bench
Verified, tau2 (airline, retail, telecom, banking_knowledge) and Terminal-Bench 4.0.0, built under
the same rules so that the benchmarks can be analysed together.

- `COVERAGE.md` (generated): tasks, configurations and models per benchmark and generation, and
  the models that link benchmarks.
- `tasks.csv` (generated): every task with results: frozen-text hash, configurations, trials,
  solve rate, flags, and the benchmark's own difficulty data (SWE-bench's human time-to-fix
  bucket, Terminal-Bench's expert time estimate and category).
- `models.csv` (hand-kept): one id per model, with provider and release month.
- `data/results/panel.parquet` (gitignored, rebuilt below): one row per (benchmark, task,
  configuration).

## Rules

1. **One row per (benchmark, task, configuration).** A configuration is one run of one system:
   a SWE-bench leaderboard entry, a tau2 results file, a Terminal-Bench leaderboard row.
   `success` is the share of the configuration's scored trials with reward 1, and `n_trials`
   counts the scored trials. A trial that ended without a score (an error before grading) is
   missing, not a failure.
2. **One name per model.** `models.csv` maps each source's model names to one id, with its
   release month; the generation follows from it: G0 June–September 2026, G1 January–May 2026,
   G2 July–December 2025, G3 earlier. Multi-model systems, and SWE-bench entries whose metadata
   names no single model, are `system` rows: they count towards a task's difficulty, not towards
   any model's ability. A name missing from `models.csv` is listed in `unmapped_models.csv`,
   which must stay empty.
3. **One text per task.** Every task is its frozen instance (`data/instances/`, hash
   `prompt_sha12`), the text the judges annotate. tau2 revised some tasks between versions; the
   fetcher rebuilds the text each run used and compares hashes. Results on another version of the
   text stay in the panel, flagged `text_matches_frozen = False`, and are left out of solve rates.
4. **Verifiably solvable.** A task qualifies when its scored trials on the frozen text, over all
   configurations, pass at least 5% of the time and no audit names it as broken. The 5% cut is
   `swebench-pl`'s pre-registered rule; on SWE-bench and on Terminal-Bench 4.0 it means about 7 of
   135 trials. Named as broken: the three SWE-bench Verified tasks OpenAI's 2026 audit names (its
   full list is not public; a test-validity audit is pending) and the 30 Terminal-Bench 4.0.0
   tasks in Epoch's review. Tasks that share one text (`text_collapsed`: tau2 telecom has 2,285
   tasks over 5 texts) cannot be told apart by annotating text.
5. **A solve rate depends on who attempted the task.** It averages over the configurations that
   ran the task, and those differ by benchmark: mostly 2024–2025 systems on SWE-bench, mostly
   current models on Terminal-Bench 4.0, late 2025 to mid 2026 on tau2. Compare solve rates across
   benchmarks within one generation, or through the models that ran on several benchmarks
   (`COVERAGE.md`).

The same rules apply to annotation: every benchmark is judged on its verifiably solvable tasks,
with the same judge, rubric files and prompt builder.

## Rebuild

```
# SWE-bench: results and entry metadata from SWE-bench/experiments at 40f164d
git -C data/downloads/swe-experiments sparse-checkout add '/evaluation/verified/*/metadata.yaml'
adele results fetch-swebench data/downloads/swe-experiments --instance-ids data/instances/instances_swe-bench-verified.parquet
# tau2: per-task rewards from Sierra's public bucket (streams about 6 GB; caches parsed rows)
adele results fetch-tau2
# frozen instances (tau2 needs a checkout of sierra-research/tau2-bench in TAU2_REPO)
adele instances prepare -b swebench,taubench,terminalbench4
# the panel; Terminal-Bench 4.0 results come from the committed export in sources/
python experiments/benchmarks/panel/build.py
```

`sources/terminal-bench-4/` holds the per-task trial counts exported from the public Harbor Hub
leaderboard pages on 2026-09-27 (how: `src/adele/results/sources/harbor_hub.py`). They
reproduce the leaderboard's accuracy for 26 of 27 rows; for Opus 5 at max effort the export has
173 solved trials where the leaderboard implies 171, probably a later re-grade.
