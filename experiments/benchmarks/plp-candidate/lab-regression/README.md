# plp-candidate / lab-regression — does candidate C pass the lab's regression?

Owner: Pablo. Candidate C adds one knowledge carve to PLp's scope paragraph. Before adoption, it is
run through the rubric lab's standing tests: example placement (r25), examples disentangle (r34),
minimal pairs (r36), family diagonal (r42/r43) and battery-v1. Three judges (haiku, sonnet, opus
at low effort) score every item under the current text and under C.

**Status.** Complete (2026-09-28): C passes. Nothing that holds under the current text breaks
under C. See `RESULTS.md`. Candidate D (C's first clause only) fails its rule by one confirmed
two-level move, and lowers labels more broadly than C.

| | |
|---|---|
| design, decision rule, predictions | `PREREGISTRATION.md` |
| items, with the 4-gram check | `items.csv` (built by `make_prompts.py`; rebuilt items in `reconstructed_items.csv`) |
| runs | `labels/labreg-r1/` (pass 1), `labels/labreg-r2/` (pass 2, if needed) |
| analysis | `analysis/analyse.py` → `results/regression.json`; `analysis/exploratory.py` → `results/exploratory.json` |
| what happened | `RUNLOG.md` |
| write-up | `RESULTS.md` |

## Reproduce

```
python experiments/benchmarks/plp-candidate/lab-regression/make_prompts.py
# judging: relays judge-dispatcher-low -> adele-judge-low, models haiku, sonnet and opus
python experiments/benchmarks/plp-candidate/lab-regression/writers.py --run labreg-r1 --transcripts <judging session>/subagents
python experiments/benchmarks/plp-candidate/lab-regression/collect.py --run labreg-r1
python experiments/benchmarks/plp-candidate/lab-regression/analysis/analyse.py
```
