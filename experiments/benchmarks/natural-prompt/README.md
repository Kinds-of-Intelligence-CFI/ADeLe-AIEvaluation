# natural-prompt — a plain annotation prompt

Owner: Pablo. The v1 annotation prompt asks for "CHAIN-OF-THOUGHTS REASONING STEPS", and Sonnet 5.5's
safeguards block it. This study tests a plain prompt with the same method: does it stop the blocks
(Sonnet 5.5 high, 44 PLp cells), and does it keep Opus low's labels (132 gate cells)?

**Status.** Complete (2026-09-29): the plain prompt removes Sonnet 5.5's blocks (0 of 44), but it
raises Opus low's labels (+0.16 PLp, +0.27 PLe). The old prompt stays in use. See `RESULTS.md`.

| | |
|---|---|
| design, tests, predictions | `PREREGISTRATION.md` |
| the prompt | `prompt.py` |
| judge and relay agents | `adele-judge-v2-*.md`, `judge-dispatcher-v2-*.md` (installed in `~/Developer/ADELE/.claude/agents/`) |
| runs | `labels/np-plp-s55h/` (A), `labels/np-gate-opuslow/` (B), from `make_runs.py` |
| analysis | `analysis/analyse.py` → `results/natural_prompt.json` |
| what happened | `RUNLOG.md` |
| write-up | `RESULTS.md` |

## Reproduce

```
python experiments/benchmarks/natural-prompt/make_runs.py
# judging: judge-dispatcher-v2-high -> adele-judge-v2-high (model sonnet) for A;
#          judge-dispatcher-v2-low -> adele-judge-v2-low (model opus) for B
python experiments/benchmarks/natural-prompt/writers.py --run <run> --transcripts <judging session>/subagents
python experiments/benchmarks/natural-prompt/collect.py --run <run>
python experiments/benchmarks/natural-prompt/analysis/analyse.py
```
