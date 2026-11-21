# relabel-v2 — all five v2 rubrics under the reviewed examples

Owner: Pablo. Relabels PLp, PLe, PLs, MSm and MSc on the seven agentic clean sets and the three social sets after the
examples review (`d4ec2ec`). Design and predictions: `PREREGISTRATION.md`. Old labels: `old_labels.csv` (frozen).

**Status.** Labels complete (2026-10-04): 7,056 of 7,065 cells in the five runs; results in `RESULTS.md`, run log in
`RUNLOG.md`. To reproduce the numbers:

    python experiments/benchmarks/relabel-v2/analysis/analyse.py

Still to do: switch the seven releases to these runs (`../release.py` and each `export.py`), rerun the social studies'
analyses and `../jev-pilot`, and update `SUMMARY.md`.
