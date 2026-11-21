# API vs subagent solvers (2026-11-20)

Does `api_solve.py` (default harness mode) give the same results as the Claude Code subagent runs?
The same 54 states and 5 tries per model. The bar was set before the runs: success within 0.08 and optimal within
0.10 of the subagent run.

| model | runs (subagent → API) | n API | success | optimal | bar |
|---|---|---|---|---|---|
| Opus 5.5, effort low | rc-solve-opus → rc-solve-api-opus | 268 | 0.985 → 0.993 | 0.907 → 0.884 | passes |
| Sonnet 5.5, effort low | rc-solve-sonnet → rc-solve-api-sonnet | 264 | 0.915 → 0.932 | 0.730 → 0.742 | passes |
| Haiku 4.5, thinking budget 31,999 | rc-solve → rc-solve-api-haiku | 269 | 0.707 → 0.219 | 0.559 → 0.186 | **fails** |

A few cells have no answer: 2 Sonnet refusals and some connection errors. Rerunning the same command fills them.

**Opus and Sonnet:** API runs compare with the published subagent runs.

**Haiku: do not compare API runs with `rc-solve`.** The likely cause is how Haiku reasons:
- As a subagent, Haiku wrote its reasoning as visible text before the answer. Median time per call was 62 s.
- Through the API with a thinking budget, it thinks briefly and answers. Median time per call was 9 s, with about
  1,000 output tokens.
- Untested fix: run Haiku without thinking, so it reasons in visible text as it did in Claude Code.

The plain-prompt Haiku arm (`--plain`) stopped on a connection error before writing `usage.csv`. Its answers are on
disk but were not scored.

Tokens and seconds per call are in `labels/<run>/usage.csv`. Median output tokens (including thinking): Opus 484,
Sonnet 861, Haiku 1,051. Median seconds: Opus 5.5, Sonnet 7.4, Haiku 9.4.
