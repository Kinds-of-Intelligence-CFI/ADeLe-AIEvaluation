# swebench-clean — SWE-bench Verified without known-broken and never-solved tasks

Owner: Pablo. The clean set (443 of 500) is defined in `PREREGISTRATION.md` and listed, with each exclusion's reason,
in `tasks.csv`.

| | |
|---|---|
| set definition | `make_set.py` → `tasks.csv` |
| new labels | `make_prompts.py` → run `labels/clean-swe` (30 tasks × PLp, PLe, PLs) |
| analysis | `analysis/analyse.py` → `results/clean.json` |
| what happened | `RUNLOG.md` |
| **shareable release** | `release/` (Hugging Face layout; data card `release/README.md`, built by `export.py` from `DATACARD.md`) |

```
python experiments/benchmarks/swebench-clean/make_set.py
python experiments/benchmarks/swebench-clean/make_prompts.py
# judging: relay judge-dispatcher-v2-low -> adele-judge-v2-low, model opus
python experiments/benchmarks/swebench-clean/writers.py --run clean-swe --transcripts <judging session>/subagents
python experiments/benchmarks/swebench-clean/collect.py --run clean-swe
uv run --extra annotate --with scipy python experiments/benchmarks/swebench-clean/analysis/analyse.py
uv run --extra annotate python experiments/benchmarks/swebench-clean/export.py   # rebuilds release/
```

**This is the SWE-bench Verified set to use** (Pablo, 2026-10-01). Not yet on Hugging Face: publishing needs the
organisation account and an explicit go.
