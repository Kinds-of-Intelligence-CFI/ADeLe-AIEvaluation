# programbench-pl

PL labels (PLp, PLe, PLs) on a clean set of ProgramBench (v1.2.5), joined to per-run test pass rates of the 25
leaderboard runs. See `PREREGISTRATION.md`. Set: `make_set.py` → `tasks.csv` (all 200 tasks; `keep` marks the 130
clean ones). Labels via `adele mass` (spec `../mass-annotation/specs/programbench-pl.toml`). Analysis:
`analysis/analyse.py` → `results/analysis.json`. Log: `RUNLOG.md`. Data sources and fetchers: `../programbench-data/`
(`NOTES.md`).

**Data terms.** Per-run scores come from the ProgramBench/submissions registry (MIT) and are tracked as a plain CSV,
`../panel/sources/programbench/runs.csv` (5,000 rows, 1.2 MB: ids, numbers, short metadata). Task text, workspace
documentation and prompts stay in `data/instances/` (gitignored); the documentation is third-party, under each
project's own licence. The audit behind `knowledge_gated` is share-alike: only task ids are used here.

```
python experiments/benchmarks/programbench-pl/make_set.py
adele mass plan experiments/benchmarks/mass-annotation/specs/programbench-pl.toml
python experiments/benchmarks/programbench-pl/analysis/analyse.py
```
