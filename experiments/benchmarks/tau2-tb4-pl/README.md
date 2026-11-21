# tau2-tb4-pl — planning rubrics on tau2 and Terminal-Bench 4.0

Owner: Pablo. The three planning rubrics (PLp, PLe, PLs) on the verifiably solvable tasks of tau2
(airline, retail, banking_knowledge: 232 tasks) and on all 66 Terminal-Bench 4.0.0 tasks (34 in
the analysis set). The judge is Opus at low effort, with the same rubric files and prompt builder as
`swebench-pl`. It asks whether PLp tracks difficulty beyond SWE-bench Verified.

**Status.** Complete (2026-09-28): 894 cells judged. PLp tracks solve rate within tau2's domains
(ρ −0.33) but not on Terminal-Bench (−0.06); see `RESULTS.md`.

| | |
|---|---|
| design, predictions, power | `PREREGISTRATION.md` |
| what happened, run by run | `RUNLOG.md` |
| tasks, analysis set, frozen outcome data | `sample.csv` |
| pinned runs | `labels/tau2pl-r1/`, `labels/tb4pl-r1/` (`run.json`, `prompts_index.csv`, then `labels_long.csv`) |
| analysis | `analysis/analyse.py`, `analysis/exploratory.py` → `results/` |
| write-up | `RESULTS.md` |

## Reproduce

```
python experiments/benchmarks/panel/build.py                 # data/results/panel.parquet (see panel/README.md)
python experiments/benchmarks/tau2-tb4-pl/make_prompts.py    # sample.csv, prompts, run.json
# judging: relays as in swebench-pl (judge-dispatcher-low → adele-judge-low), see RUNLOG.md
python experiments/benchmarks/tau2-tb4-pl/writers.py --run tau2pl-r1 --transcripts <judging session>/subagents
python experiments/benchmarks/tau2-tb4-pl/writers.py --run tb4pl-r1 --transcripts <judging session>/subagents
python experiments/benchmarks/tau2-tb4-pl/collect.py --run tau2pl-r1
python experiments/benchmarks/tau2-tb4-pl/collect.py --run tb4pl-r1
python experiments/benchmarks/tau2-tb4-pl/analysis/analyse.py
python experiments/benchmarks/tau2-tb4-pl/analysis/exploratory.py
```

Task text, prompts and the judges' reasons stay in the gitignored `data/` tree and in
`judge-io/`. Terminal-Bench's task text carries a training-corpus canary and must never be
committed.
