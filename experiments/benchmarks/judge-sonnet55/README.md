# judge-sonnet55 — can Sonnet 5.5 replace Opus 5.5 as the judge?

Owner: Pablo. Sonnet 5.5 at high effort labels PLp and PLe on the 44 gate tasks of `swebench-pl`,
with the gate's prompts byte for byte. Its labels are compared with the stored Opus labels (medium,
low and max), and its cost per call is read from the plan's usage meters.

**Status.** Pre-registered (2026-09-29). Judging not started.

| | |
|---|---|
| design, checks, predictions | `PREREGISTRATION.md` |
| judge and relay agents | `adele-judge-high.md`, `judge-dispatcher-high.md` (installed in `~/Developer/ADELE/.claude/agents/`) |
| run | `labels/s55h-gate/` (`make_run.py`) |
| analysis | `analysis/analyse.py` → `results/agreement.json` |

## Reproduce

```
python experiments/benchmarks/judge-sonnet55/make_run.py
# judging: relays judge-dispatcher-high -> adele-judge-high, model alias sonnet
python experiments/benchmarks/judge-sonnet55/writers.py --run s55h-gate --transcripts <judging session>/subagents
python experiments/benchmarks/judge-sonnet55/collect.py --run s55h-gate
python experiments/benchmarks/judge-sonnet55/analysis/analyse.py
```
