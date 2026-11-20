# rivercross-v2 — the rivercross puzzles judged with the current rubrics and the v2 prompt

Owner: Pablo. The rivercross frames and solver ground truth (`experiments/rivercross/`, Mingqian's
arm) are read without change. Opus low judges PLp, PLe and PLs, one state per call, with the v2
annotation prompt. The labels are checked against the solver's cost-to-go.

**Status.** Complete (2026-09-30). PLp tracks solution length, not search. Strong solvers find search, not length, hard (amendment 3). See `RESULTS.md`.

| | |
|---|---|
| design, predictions | `PREREGISTRATION.md` |
| runs | `labels/rc-state/`, `labels/rc-play/` (`make_prompts.py`) |
| analysis | `analysis/analyse.py` → `results/rivercross.json` |
| results | `RESULTS.md` |

## Run it through the API (no Claude Code needed)

Setup: `pip install -e ".[dev]"`, and `ANTHROPIC_API_KEY` in `.env` at the repository root (load it with
`set -a; . ./.env; set +a`). Answers go to `judge-io/` next to the clone, outside git.

**Solve.** The 54 puzzle states, five tries each, scored for legality, success and optimal length:
```
python experiments/benchmarks/rivercross-v2/api_solve.py --run rc-solve-api-opus --model claude-opus-5-5
python experiments/benchmarks/rivercross-v2/score_solve.py --run rc-solve-api-opus
```
Add `--limit 3 --tries 1` for a quick test. By default the request reproduces what the `rc-solver` subagent saw, so
results compare with `rc-solve`, `rc-solve-sonnet` and `rc-solve-opus`; `--plain` sends the bare prompt instead.
`labels/<run>/usage.csv` has the real tokens (output includes thinking) and seconds per call. See
`API-COMPARISON.md` for how API and subagent results compare.

**Judge.** The same states on the PL and MS rubrics, through `adele mass` with the Anthropic Batch API:
```
python experiments/benchmarks/rivercross-v2/register_search.py     # registers benchmark rivercross-search
adele mass pin experiments/benchmarks/mass-annotation/specs/rivercross-plms-api.toml
adele mass run rivercross-plms-api && adele mass collect rivercross-plms-api
```
The `subagent-v2-low` harness reproduces the subagent judge (`experiments/benchmarks/harness-emulation`). For other
providers, change `backend` (`openai-batch`, `litellm`, `inspect`) as in `mass-annotation/RUNNING.md`.

## Reproduce

```
python experiments/benchmarks/rivercross-v2/make_prompts.py
# judging: judge-dispatcher-v2-low -> adele-judge-v2-low, model opus
python experiments/benchmarks/rivercross-v2/writers.py --run <run> --transcripts <judging session>/subagents
python experiments/benchmarks/rivercross-v2/collect.py --run <run>
python experiments/benchmarks/rivercross-v2/analysis/analyse.py
```
