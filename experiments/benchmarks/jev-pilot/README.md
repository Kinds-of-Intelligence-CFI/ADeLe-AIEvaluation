# jev-pilot — can a System One classifier reproduce our demand labels?

Owner: Pablo. TypeSafe's Jev (`jev-1.13.0`) labels the seven agentic clean sets and the three social sets on PLp, PLe,
PLs, MSm and MSc. The labels are compared with the Opus 5.5 (low) labels and with each set's outcome.

**Status.** Pre-registered 2026-10-04; running.

| | |
|---|---|
| design, predictions | `PREREGISTRATION.md` |
| runner | `run_jev.py` → `labels/jev_labels.csv` (responses kept locally in `judge-io/jev-pilot/`) |
| analysis | `analysis/analyse.py` → `results/analysis.json` |
