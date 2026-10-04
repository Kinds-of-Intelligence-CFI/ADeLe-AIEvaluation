# relabel-v2 — all five v2 rubrics under the reviewed examples

Owner: Pablo. Relabels PLp, PLe, PLs, MSm and MSc on the seven agentic clean sets and the three social sets after the
examples review (`d4ec2ec`). Design and predictions: `PREREGISTRATION.md`. Old labels: `old_labels.csv` (frozen).

**Status.** Running: `relabel-v2` started 2026-10-04 (1,195 of 5,080 labels; see `RUNLOG.md`). To continue in a new session:

    adele mass pin experiments/benchmarks/mass-annotation/specs/relabel-v2.toml        # and -long, -eqbench4,
                                                                                         # -cooperbench, -gamearena
    /annotate relabel-v2 (then the other four runs)
    python experiments/benchmarks/relabel-v2/analysis/analyse.py

Then: switch the seven releases to these runs (`../release.py` and each `export.py`), rerun the social studies'
analyses and `../jev-pilot`, and update `SUMMARY.md`.
