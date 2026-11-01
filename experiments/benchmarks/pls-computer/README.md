# pls-computer — do computer-world examples help PLs?

Owner: Pablo. Three example bullets are added to PLs at Levels 3, 4 and 5: computer worlds that cannot be run first
(`PLs_candidate.txt`). The check is that they place where intended and change nothing else. Judge: Opus 5.5 at
effort low, v2 prompt.

**Status.** Complete (2026-10-04): the candidate passes, and all three examples are kept. They lower PLs on DeepSWE. See `RESULTS.md`.

| | |
|---|---|
| design, decision rule, predictions | `PREREGISTRATION.md` |
| items, with the 4-gram check | `items.csv` (built by `make_prompts.py`; pairs in `pairs.csv`) |
| runs | `labels/plsc-1/` (pass 1), `labels/plsc-2/` (pass 2, if needed) |
| analysis | `analysis/analyse.py` → `results/analysis.json` |
| what happened | `RUNLOG.md` |

## Reproduce

```
python experiments/benchmarks/pls-computer/make_prompts.py
# judging: relays judge-dispatcher-v2-low -> adele-judge-v2-low, model opus (see RUNLOG.md)
python experiments/benchmarks/pls-computer/writers.py --run plsc-1 --transcripts <judging session>/subagents
python experiments/benchmarks/pls-computer/collect.py --run plsc-1
python experiments/benchmarks/pls-computer/analysis/analyse.py
```
