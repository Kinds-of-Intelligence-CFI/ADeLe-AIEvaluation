# plp-o-relabel — PLp relabelled with the adopted text O

Owner: Pablo. Same judge, prompt and tasks as `pl-relabel-v2`; only the PLp text changes (O, adopted 2026-10-01).

| | |
|---|---|
| design, predictions | `PREREGISTRATION.md` |
| runs | `labels/o-swe`, `labels/o-tau2`, `labels/o-tb4` (+ `../plp-b2/labels/o-swe-gate`) |
| analysis | `analysis/analyse.py` → `results/relabel_o.json` |
| what happened | `RUNLOG.md` |

```
python experiments/benchmarks/plp-o-relabel/make_prompts.py
# judging: relays judge-dispatcher-v2-low -> adele-judge-v2-low, model opus
python experiments/benchmarks/plp-o-relabel/writers.py --run o-swe --transcripts <judging session>/subagents
python experiments/benchmarks/plp-o-relabel/collect.py --run o-swe
uv run --extra annotate --with scipy --with statsmodels python experiments/benchmarks/plp-o-relabel/analysis/analyse.py
```
