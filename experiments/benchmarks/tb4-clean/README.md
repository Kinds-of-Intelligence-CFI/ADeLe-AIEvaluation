# tb4-clean — Terminal-Bench 4.0.0 without defective and never-solved tasks

Owner: Pablo. The same rule as `../swebench-clean`, applied to Terminal-Bench 4.0.0 (2026-10-01): drop the 30 tasks
Epoch AI's review names as defective and the tasks no leaderboard configuration solves. **35 of 66 tasks remain**
(`tasks.csv`, with each exclusion's reason). All PL labels already exist (Opus 5.5 low, v2 prompt, PLp text O), except
`uefi-bootkit` (safety classifier on both attempts).

**Descriptive only.** These labels and outcomes were analysed on all 66 tasks in `../tau2-tb4-pl` and
`../pl-relabel-v2`, so the summary here is not a new test. On the 34 fully labelled clean tasks, PLp does not track
solve rate (ρ = +0.12, p = 0.49) or expert hours (ρ = +0.17, p = 0.35); 25 of 34 tasks are at PLp 3.

| | |
|---|---|
| set definition | `make_set.py` → `tasks.csv` |
| release (Hugging Face layout) | `release/` (data card `release/README.md`, built by `export.py` from `DATACARD.md`) |
| summary | `results/clean.json` |
| what happened | `RUNLOG.md` |

```
python experiments/benchmarks/tb4-clean/make_set.py
uv run --extra annotate --with scipy python experiments/benchmarks/tb4-clean/export.py
```

Not yet on Hugging Face: publishing needs the organisation account and an explicit go.
