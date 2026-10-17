# swev30-r2 run log

## 2026-09-26 — dry run: 6 calls, no retries

Task `django__django-15382` × {PLp, PLe, VO} × {sonnet, opus}, judged by the `adele-judge`
subagent with the per-call message template in `run.json` (inputs pinned at `85e127c`). The
prompt, rubric, builder, agent and instruction hashes were re-checked before the calls; all match.

| judge | PLp | PLe | VO |
|---|---|---|---|
| sonnet | 3 | 3 | 3 |
| opus | 2 | 3 | 3 |

- All six answers parse and end with the prescribed sentence; 530–770 words each. No safeguard
  flags (0 of 6).
- Opus called Read, Write, hand-back. Sonnet also read its own response file, which did not
  exist yet, before writing it (all three calls): one extra request, no other file touched.
- The aliases resolved to `claude-sonnet-5` and `claude-opus-5-5` (subagent transcripts), as in r1.
- **Reasoning effort** was `max` for every judge request, inherited from the orchestrating
  session: `adele-judge.md` sets no `effort`, so a session at another level would change it.
  r1's judges also ran at `max`.
- **Injected context.** Besides its system prompt and the prompt file, each judge's context holds
  what the harness attaches to every subagent: the user-level `~/.claude/CLAUDE.md` with its
  imported profile and the workspace `CLAUDE.md`; the `ADELE_v2/CLAUDE.md` working guide,
  attached once the judge reads a file below it; and environment, date and MCP boilerplate. None
  of it gives rubric levels, expected levels or pilot results. r1's transcripts show the same
  attachments.
- **Cost.** 25.8k–39.9k tokens per call as the Agent tool reports them (the final request's full
  context, the metric used for r1): Sonnet mean 36.1k, Opus 28.3k, against about 69k in r1. The
  largest part is the judge's own answer turn, thinking plus answer: 13.8k–21.2k tokens for
  Sonnet, 9.5k–13.3k for Opus. Harness and injected context take about 12k, the prompt about 3k.
  Across its 4–5 requests a call also re-reads cached context: about 79k tokens per Sonnet call,
  53k per Opus call. Wall time 88–237 s (Sonnet mean 202 s, Opus 108 s), six in parallel.
- **Projection.** The remaining 1,578 calls: about 51M tokens on r1's metric (r1 projected 110M
  for the whole design) and about 68 agent-hours, i.e. 4–9 hours at 16–8 concurrent calls.
  Orchestrating them from one conversation would add about 0.8M tokens to its context (about
  0.5k per call). Workflow scripts avoid that: at most 1,000 agents each, 8 concurrent on this
  machine, e.g. one workflow per judge.
- No plan-usage reading was taken before the run, so its share of the subscription's usage
  limits is not measured.

Status: superseded by deviation 2 (run `swev30-r3`). The six labels are discarded: kept aside
under `data/`, never analysed.
