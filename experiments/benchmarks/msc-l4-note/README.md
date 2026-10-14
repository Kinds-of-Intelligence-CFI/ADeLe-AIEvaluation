# msc-l4-note — does a sustained-opposition note fix MSc Level 4?

Owner: Pablo. Tests one candidate change to MSc: two sentences in Level 4's Note that place a lone objection,
answered once and dropped, below Level 4. Current text and candidate are judged side by side on the MS lab
regression's MSc items, eight minimal pairs and fifteen real tau2 tasks, ten of them labelled blind by Pablo.
The rubric in `src/` does not change here.

| | |
|---|---|
| design, rules, predictions | `PREREGISTRATION.md` |
| candidate text | `MSc_candidate.txt` |
| items | `items.csv` (tau2 texts blanked), `pairs.csv`, `human_items.csv` (ids only) |
| Pablo's labels | `human_labels.csv` |
| runs | `labels/msc-l4-1/`, `labels/msc-l4-2/` (pass 2, if needed) |
| analysis | `analysis/analyse.py` → `results/results.json` |

## Reproduce

```
uv run --extra annotate python experiments/benchmarks/msc-l4-note/make_prompts.py
# judging: the 18 relay files in $ADELE_JUDGE_IO/msc-l4-1/relays/ go to judge-dispatcher-v2-low
uv run --extra annotate python experiments/benchmarks/msc-l4-note/writers.py --run msc-l4-1 --transcripts <session>/subagents --set-aside
uv run --extra annotate python experiments/benchmarks/msc-l4-note/collect.py --run msc-l4-1
uv run --extra annotate python experiments/benchmarks/msc-l4-note/analysis/analyse.py
```
