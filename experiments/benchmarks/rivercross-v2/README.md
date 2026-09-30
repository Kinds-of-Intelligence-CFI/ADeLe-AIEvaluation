# rivercross-v2 — the rivercross puzzles judged with the current rubrics and the v2 prompt

Owner: Pablo. The rivercross frames and solver ground truth (`experiments/rivercross/`, Mingqian's
arm) are read without change. Opus low judges PLp, PLe and PLs, one state per call, with the v2
annotation prompt. The labels are checked against the solver's cost-to-go.

**Status.** Pre-registered (2026-09-30). Judging not started.

| | |
|---|---|
| design, predictions | `PREREGISTRATION.md` |
| runs | `labels/rc-state/`, `labels/rc-play/` (`make_prompts.py`) |
| analysis | `analysis/analyse.py` → `results/rivercross.json` |

## Reproduce

```
python experiments/benchmarks/rivercross-v2/make_prompts.py
# judging: judge-dispatcher-v2-low -> adele-judge-v2-low, model opus
python experiments/benchmarks/rivercross-v2/writers.py --run <run> --transcripts <judging session>/subagents
python experiments/benchmarks/rivercross-v2/collect.py --run <run>
python experiments/benchmarks/rivercross-v2/analysis/analyse.py
```
