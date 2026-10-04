# relabel-v2 — run log

## 2026-10-04 — setup and first rounds

Specs written from the pls-relabel and social-study specs (refs: all five rubrics; relays of 100, deviation 2).
`old_labels.csv` frozen (7,052 rows) before any label. `relabel-v2` pinned at 13:27 UTC (5,080 cells). Three rounds of
four `judge-dispatcher-v2-low` relays of 100 cells, about 10 minutes each: 1,195 labels, all protocol checks passed,
5 cells rejected once and queued for retry by the runner. Weekly usage 62 to 66 per cent (about 1 point per 400
calls). Stopped with no relay in flight, to continue in a new session (orchestrator context; about 15 rounds remain).

Not yet pinned: `relabel-v2-long`, `relabel-v2-eqbench4`, `relabel-v2-cooperbench`, `relabel-v2-gamearena`.
