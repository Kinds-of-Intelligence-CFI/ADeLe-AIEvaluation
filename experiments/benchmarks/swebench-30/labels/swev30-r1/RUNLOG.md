# swev30-r1 run log

## 2026-09-26 — dry run: 6 calls, 1 retry

Task `django__django-15382` × {PLp, PLe, VO} × {sonnet, opus}, protocol exactly as
pre-registered (`run.json`, commit `e26e794`).

| judge | PLp | PLe | VO |
|---|---|---|---|
| sonnet | 1 | 3 | 3 |
| opus | 2 | 3 (after the permitted retry) | 3 |

- All six answers parse and end with the prescribed sentence; 400–730 words each.
- Judges used only Read and Write (plus the hand-back); no file outside `responses/` was
  written.
- **Opus safeguard flags.** Opus's first PLe answer was stopped by a safety classifier before
  it was saved. The one permitted retry saved a complete answer, then the call was flagged
  anyway (Opus 5.5, detail `reasoning_extraction`). That is 2 of 3 attempts on this prompt,
  0 of 2 on the other Opus prompts, and 0 of 3 for Sonnet. The likely trigger is the request
  to write the full reasoning out.
- **Cost.** 62k–78k subagent tokens per call (mean about 69k), 47–162 s each. The prompt is
  about 2k tokens; the rest is the general-purpose agent's own system prompt and tool
  definitions. Projected full run as designed: 1,584 calls, about 110M tokens, roughly 3–5
  hours at 10–15 calls in parallel.

Status: full run on hold until Pablo decides the judge harness and scope.
