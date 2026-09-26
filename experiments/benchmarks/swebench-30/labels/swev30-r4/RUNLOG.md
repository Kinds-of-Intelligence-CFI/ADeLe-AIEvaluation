# swev30-r4 run log

## 2026-09-26 — dry run: 6 calls, no retries

Task `django__django-15382` × {PLp, PLe, VO} × {sonnet, opus}, judged by `adele-judge` with the
pinned r4 inputs (`475a5a9`): prompts read from, and answers written to, `judge-io/swev30-r4/`,
two levels above the repo. The 792 judge-side prompt copies were hash-checked against
`prompts_index.csv` before the calls.

| judge | PLp | PLe | VO |
|---|---|---|---|
| sonnet | 3 | 3 | 3 |
| opus | 2 | 3 | 3 |

The same levels as in the discarded r2 dry run.

- All six answers parse and end with the prescribed sentence; 3,768 words in total. No safeguard
  flags.
- **Judge context.** None of the six transcripts has a CLAUDE.md of any kind: no `instructions`
  attachment and no nested `ADELE_v2/CLAUDE.md`. Besides the agent's system prompt and the prompt
  file, what remains is harness boilerplate: environment (working folders), date, model, the
  account's e-mail line, one MCP-server note, and for Sonnet a permission-mode flag.
- Effort `max` on every request; the aliases resolved to `claude-sonnet-5` and `claude-opus-5-5`.
- Tools: Opus called Read, Write, hand-back. In two of three calls Sonnet also read its own
  response file before writing it, as in r2. No other file was opened or written. One Sonnet
  hand-back was a summary instead of the bare `DONE 3`; only the saved answer is used.
- **Cost.** Final-request context per call: Sonnet 16.8k–30.7k tokens (mean 22.2k), Opus
  10.8k–15.8k (mean 13.5k), against r2 means of 36.1k and 28.3k. Most of it is the answer turn,
  thinking plus answer: Sonnet 10.4k–21.6k, Opus 5.6k–9.5k. The first request is about 3.2k
  (Opus) to 3.7k (Sonnet). Wall time: Sonnet 128–263 s (mean 177 s), Opus 55–94 s (mean 76 s),
  six in parallel.
- **Projection.** The remaining 1,578 calls: about 28M tokens on this metric (51M projected after
  r2, 110M after r1) and about 55 agent-hours, i.e. about 2 h for Opus and 5 h for Sonnet at 8
  concurrent calls.

Status: labels kept, as the protocol is unchanged. The full run awaits Pablo's approval.
