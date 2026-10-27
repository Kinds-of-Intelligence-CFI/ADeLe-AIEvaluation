# cooperbench-plms

Planning (PLp, PLe, PLs) and social (MSm, MSc) labels on 120 CooperBench feature pairs, each as a solo task and as a
two-agent cooperation task, tested against each pair's drop in success from solo to coop. See `PREREGISTRATION.md`.
Data and sources: `../cooperbench-data/` (`NOTES.md`). Set and sample: `make_set.py` → `tasks.csv`, `subset.csv`.
Labels via `adele mass` (spec `../mass-annotation/specs/cooperbench-plms.toml`). Analysis: `analysis/analyse.py` →
`results/analysis.json`. Log: `RUNLOG.md`.
