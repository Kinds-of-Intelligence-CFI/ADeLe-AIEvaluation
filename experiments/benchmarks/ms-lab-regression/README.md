# ms-lab-regression — do today's judge and prompt reproduce the lab's MS results?

Owner: Pablo. MSm and MSc are judged as the catalog loads them, with the v2 prompt and Opus at low effort,
three repeats per item, on the rubric lab's standing tests: example placement, foreign examples, the sibling
split, the lab's own MS items (r30, r36, r60, r69, r75, with r70's human labels) and battery-v1. No rubric text
changes. Modelled on `../plp-candidate/lab-regression/`.

**Status.** Built, not run (2026-10-02). Prompts are in the judge-io folder; no judge has been launched.

| | |
|---|---|
| design, checks, decision rule, predictions | `PREREGISTRATION.md` |
| items, with the 4-gram check | `items.csv` (built by `make_prompts.py` from the rubrics, `lab_items.csv` and `battery_targets.csv`) |
| runs | `labels/ms-labreg1/` (pass 1), `labels/ms-labreg2/` (pass 2, if needed) |
| analysis | `analysis/analyse.py` → `results/regression.json` |
| what happened | `RUNLOG.md` |

## Reproduce

```
python experiments/benchmarks/ms-lab-regression/make_prompts.py
# judging: the twelve relay files in $ADELE_JUDGE_IO/ms-labreg1/relays/ go to judge-dispatcher-v2-low
python experiments/benchmarks/ms-lab-regression/writers.py --run ms-labreg1 --transcripts <judging session>/subagents --set-aside
python experiments/benchmarks/ms-lab-regression/collect.py --run ms-labreg1
python experiments/benchmarks/ms-lab-regression/analysis/analyse.py
# if a check fails: make_prompts.py --replicate ITEM ... (ms-labreg2), judge, writers, collect, analyse again
```
