# benchmarks — demand annotation on real agent benchmarks

Owner: Pablo.

The external-validity arm: annotate real benchmark instances on the active
agentic dimensions, join those demand vectors to per-instance success/failure for
many models, and test whether demand predicts success well enough to extrapolate
to a model not in the fit.

## Where things are

| | |
|---|---|
| procedure, step by step | `docs/runbook-benchmarks.md` |
| success-matrix loaders | `src/adele/results/` (SWE-bench, MathArena, ARC Prize, tau2, Harbor Hub for Terminal-Bench 4.0, Inspect) |
| instance freezing | `src/adele/instances.py`, CLI `adele instances prepare` |
| judge | CLI `adele agentic judge` |
| partner data requests | `docs/partner-data-request.md` |
| pilot sample (4 benchmarks × 5 tasks) | `pilot/`, regenerate with `adele agentic pilot --seed 0` |
| results of every study, and the run registry | `RESULTS.md`, `runs.csv` |
| every benchmark's per-task results under one set of rules (coverage, verifiably solvable tasks, model registry) | `panel/` |
| first real-benchmark run (SWE-bench Verified, 30 tasks × 25 rubrics) | `swebench-30/` |
| planning rubrics on all solvable SWE-bench Verified tasks (Opus, medium effort) | `swebench-pl/` |
| planning rubrics on tau2 and Terminal-Bench 4.0 (Opus, low effort) | `tau2-tb4-pl/` |
| a candidate Level 3 sentence for PLp, tested on real tasks | `plp-candidate/` |

## Runtime data is not in the repo

Everything the pipeline downloads or produces at runtime lives under a gitignored
`data/` tree: `data/downloads/` raw dumps, `data/instances/` frozen annotation
inputs, `data/results/` success-flag parquets, `data/annotations/` judge output.

This is not only a size decision. Some benchmarks (Terminal-Bench among them)
carry no-training-corpora canary strings in their task text, which must never land
in a public repository.

`ADeLe_battery_data/` at the repo root is a different thing: the *published*
battery release, tracked and LFS-backed.

## Results

`RESULTS.md` indexes every study's results and `runs.csv` lists every pinned run;
`python experiments/benchmarks/report.py` rebuilds both from committed files.

Every study folder has the same files: `README.md` (what, why, how to reproduce,
one status line), `PREREGISTRATION.md` (question, design, predictions, deviations),
a run log, `labels/<run>/` (`run.json` with the pinned hashes, `prompts_index.csv`,
`labels_long.csv`), `analysis/` scripts writing frozen outputs to `results/`, and
`RESULTS.md`, the write-up to share. `RESULTS.md` keeps a fixed layout, which
`report.py` reads:

1. `**Question.**`, `**Answer.**` (answer first) and `**Status.**` paragraphs;
2. `## Design`;
3. `## Pre-registered results`, every check and prediction with its outcome,
   failures included;
4. `## Exploratory results`, if any, labelled as not pre-registered;
5. `## Deviations and caveats`;
6. `## Reproduce`, with the commit holding the numbers.

Closing a run: collect the labels, run the analysis, write or update `RESULTS.md`,
run `report.py`, commit, then push after scanning the diff for secrets, canary
strings and benchmark text. Only committed numbers go into a write-up; a study's
`RESULTS.md` is written only after its predictions are locked. Judges' reasoning
and task text stay in the gitignored `data/` tree.
