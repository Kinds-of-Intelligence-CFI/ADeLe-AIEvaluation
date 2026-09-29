# pl-relabel-v2 — the planning labels redone with the v2 prompt

Owner: Pablo. PLp, PLe and PLs on SWE-bench Verified, tau2 and Terminal-Bench 4.0.0, relabelled by
Opus low with the v2 annotation prompt (`build_annotation_prompt_v2`), and each study's pre-registered
analysis rerun on the new labels.

**Status.** Pre-registered (2026-09-29). Judging not started.

| | |
|---|---|
| design, predictions | `PREREGISTRATION.md` |
| runs | `labels/v2-swe/`, `labels/v2-tau2/`, `labels/v2-tb4/` (`make_prompts.py`) |
| analysis | `analysis/analyse.py` → `results/relabel.json` |

## Reproduce

```
python experiments/benchmarks/pl-relabel-v2/make_prompts.py
# judging: judge-dispatcher-v2-low -> adele-judge-v2-low, model opus
python experiments/benchmarks/pl-relabel-v2/writers.py --run <run> --transcripts <judging session>/subagents
python experiments/benchmarks/pl-relabel-v2/collect.py --run <run>
python experiments/benchmarks/pl-relabel-v2/analysis/analyse.py
```
