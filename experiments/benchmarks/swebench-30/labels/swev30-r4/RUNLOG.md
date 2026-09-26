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

## 2026-09-26 — full run, Opus pass

Approved by Pablo after the dry run above.

- **Workflow canary, discarded.** 40 Opus cells were first run through a Claude Code Workflow
  script. The workflow harness wraps each agent's task in two framing messages, one of them a
  verbatim relay of the operator's chat message that launched the run, so those judges did not
  receive the pre-registered two-line message. Their 40 answers are set aside under
  `data/annotations/swev30-r4/responses_discarded_canary/`, never analysed.
- **Harness used instead.** A relay subagent, `judge-dispatcher` (`judge-dispatcher.md`: Sonnet,
  low effort, no CLAUDE.md, Agent tool only), launched from the main session, sends each cell to
  `adele-judge` through the Agent tool with the exact two-line message, three at a time; four
  relays run at once. Workflow agents cannot serve as relays: the workflow harness withholds the
  Agent tool from them. In a first 6-cell test, the relay also started a general-purpose helper
  to read the six answer files. Its instructions were then tightened, and no relay started any
  agent other than `adele-judge` afterwards (checked in every relay's transcript).
- **Protocol check** over all 784 Opus judge transcripts of the pass (783 cells and one
  duplicate): exact two-line message, `claude-opus-5-5`, effort `max`, no CLAUDE.md of any kind,
  no file opened or written other than the cell's prompt and answer. The attachments are the
  dry run's.
- **One accidental duplicate.** A relay sent `django__django-15499@KNa` twice; the first call
  returned no error. The second answer overwrote the first. By a fixed rule, the first completed
  attempt is the label: it was restored from its transcript, and the second is kept under
  `judge-io/swev30-r4/responses_duplicate/`. Both gave the same level.
- **Coverage.** Opus 792/792 answered and parsed (parse rate 100%); no retries needed.
- **Cost.** Mean final-request context 14.6k tokens (5.7k–55.9k), mean 82 s per call (max
  455 s); 16 relays of 42–50 cells, 29–50 min each; the pass ran from 12:44 to 15:25.
