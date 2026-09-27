# swebench-pl run log

## 2026-09-26 — step 1, effort gate (run `swepl-gate`): passes

132 Opus-medium calls through four `judge-dispatcher-medium` relays (33 cells each, about 5 min
each), from the pinned inputs (`5ec6f68`). Protocol check over all 132 judge transcripts: exact
two-line message, `claude-opus-5-5`, effort `medium`, no CLAUDE.md of any kind, no file opened or
written other than the cell's prompt and answer; 0 problems. Relays: 33 judge calls each, no
duplicate, no other tool call. 132/132 answered and parsed.

Gate (`gate.py` → `results/gate.json`; references from `swebench-30` run `swev30-r4`, Sonnet at
the 27 PL cells it had answered):

| pair | n | exact | within-1 | mean shift | QWK |
|---|---|---|---|---|---|
| Opus-medium vs Opus-max | 132 | 0.856 | 1.000 | −0.068 | 0.913 |
| — PLp / PLe / PLs exact | 44 each | 0.841 / 0.750 / 0.977 | 1.000 | −0.023 / −0.159 / −0.023 | |
| Opus-medium vs Opus-max, Sonnet cells | 27 | 0.889 | 1.000 | −0.037 | 0.930 |
| Sonnet-max vs Opus-max | 27 | 0.741 | 1.000 | +0.037 | 0.837 |
| Opus-medium vs Sonnet-max | 27 | 0.852 | 1.000 | −0.074 | 0.900 |

All four conditions hold (within-1 ≥ 0.90; exact 0.889 ≥ 0.741; shifts within ±0.25; parse
1.00), so step 2 goes ahead. Cost: mean final-request context 7.9k tokens (3.2k–10.9k) against
14.6k for the same judge at max; mean 15 s per call against 82 s.

## 2026-09-27 — step 2, scale-up (run `swepl-r1`): complete

1,194 Opus-medium calls (398 tasks × PLp, PLe, PLs) through eight `judge-dispatcher-medium`
relays of 144–150 cells, four at a time, 03:56–04:40, after the 5-hour usage window reset (the
run was held back from the evening window, which the operator's other work shared).

- Relays: one judge call per cell, no duplicate, no other tool call (checked in every relay's
  transcript; their own summaries undercount).
- Protocol check over all 1,194 judge transcripts: exact two-line message, `claude-opus-5-5`,
  effort `medium`, no CLAUDE.md of any kind, no file opened or written other than the cell's
  prompt and answer; 0 problems. One transcript also carries a `deferred_tools_record`
  attachment (a harness record of available tools), otherwise the attachments are the gate's.
- Coverage: 1,194/1,194 answered and parsed; no retries needed.
- Cost: mean final-request context 8.1k tokens (6.7k–19.5k), mean 16 s per call (max 24 s).

With step 1's 37 solvable tasks, all 435 solvable tasks now have PL labels from the same judge
and effort. The analysis waits for Pablo's review of the pre-registered predictions.
