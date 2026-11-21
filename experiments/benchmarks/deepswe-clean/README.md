# deepswe-clean

PL labels (PLp, PLe, PLs) on a clean set of DeepSWE v1.1, joined to Datacurve's per-task solve rates. See
`PREREGISTRATION.md`. Set: `make_set.py` → `tasks.csv` (all 113 tasks; `keep` marks the 90 clean ones). Labels via
`adele mass` (spec `../mass-annotation/specs/deepswe-clean.toml`). Analysis: `analysis/analyse.py` →
`results/analysis.json`. Release: `export.py` → `release/`. Log: `RUNLOG.md`. Data sources and fetchers: `../deepswe-data/` (`NOTES.md`).

**Data terms.** Datacurve states no terms for its trial data (deep-swe issue #94, open). Only per-task aggregates are
tracked: `tasks.csv` here and the per-configuration leaderboard `../panel/sources/deepswe-v1.1/leaderboard_v1-1.tsv`.
Per-trial and per-(config, task) data stay in `data/raw/deepswe-v1.1/` (gitignored), so `make_set.py` needs a local run
of `../deepswe-data/fetch_outcomes.py` first. Task text stays in `data/instances/` (gitignored).

```
python experiments/benchmarks/deepswe-data/fetch_outcomes.py   # local outcome files
python experiments/benchmarks/deepswe-clean/make_set.py
adele mass plan experiments/benchmarks/mass-annotation/specs/deepswe-clean.toml
python experiments/benchmarks/deepswe-clean/analysis/analyse.py
```
