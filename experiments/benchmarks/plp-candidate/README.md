# plp-candidate — does a new Level 3 sentence help PLp?

Owner: Pablo. One candidate change to PLp's Level 3 is tested on real benchmark tasks. It replaces
one sentence (`PLp_candidate.txt`, and `PREREGISTRATION.md` for the exact wording). The judge is
Opus at low effort, as in the main studies.

**Status.** Complete (2026-09-28): no candidate passed. A had no effect. B (an explicit rule) and C
(a knowledge carve) each moved one of Pablo's three Level-2 tasks. See `RESULTS.md`. C then passed
the lab regression (`lab-regression/`); D, its first clause alone, did not.

| | |
|---|---|
| design, decision rule, predictions | `PREREGISTRATION.md` |
| what happened | `RUNLOG.md` |
| tasks and outcome data | `sample.csv` |
| runs | `labels/cand-tb/`, `labels/ctrl-tb/`, `labels/cand-swe/`, `labels/cand-tau2/` |
| analysis | `analysis/compare.py` → `results/compare.json` |
| write-up | `RESULTS.md` |

## Reproduce

```
python experiments/benchmarks/plp-candidate/make_prompts.py
# judging: relays judge-dispatcher-low → adele-judge-low, one per run (see RUNLOG.md)
python experiments/benchmarks/plp-candidate/writers.py --run <run> --transcripts <judging session>/subagents
python experiments/benchmarks/plp-candidate/collect.py --run <run>
python experiments/benchmarks/plp-candidate/analysis/compare.py
```
