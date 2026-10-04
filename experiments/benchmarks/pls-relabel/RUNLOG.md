# pls-relabel — run log

## 2026-10-04 — setup

Specs written from `ms-benchmarks.toml` and `ms-benchmarks-long.toml` with the rubric and names changed. `adele mass
plan`: 1,016 and 13 cells, about 5 weekly points. `analysis/analyse.py` was tested on synthetic new labels (not kept);
on the released labels it reproduces the old Spearman values in `SUMMARY.md` (SWE-bench −0.18, ProgramBench −0.14,
DeepSWE 0.00, FrontierSWE −0.01, TB 4.0 +0.05, TB-Science +0.09). Not pinned yet: pinning records the agent and
rubric hashes at launch.
