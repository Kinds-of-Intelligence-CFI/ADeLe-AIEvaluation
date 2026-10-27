# relabel-v2 — run log

## 2026-10-04 — setup and first rounds

Specs written from the pls-relabel and social-study specs (refs: all five rubrics; relays of 100, deviation 2).
`old_labels.csv` frozen (7,052 rows) before any label. `relabel-v2` pinned at 13:27 UTC (5,080 cells). Three rounds of
four `judge-dispatcher-v2-low` relays of 100 cells, about 10 minutes each: 1,195 labels, all protocol checks passed,
5 cells rejected once and queued for retry by the runner. Weekly usage 62 to 66 per cent (about 1 point per 400
calls). Stopped with no relay in flight, to continue in a new session (orchestrator context; about 15 rounds remain).

## 2026-10-04 — `relabel-v2` finished; the other four runs pinned

Rounds 4 to 13 in the same way (ten rounds of four relays, the last of three). `relabel-v2` done at 16:25 UTC:
5,071 of 5,080 cells labelled, every protocol check passed, weekly usage 66 to 77 per cent. Nine cells have no label:
all five rubrics of two tasks, `programbench / agourlay__zip-password-finder.704700d` and
`terminal-bench-science-0.1 / protein-active-learning`, minus one cell that a retry labelled. On these two tasks the
safety classifier swapped the judge to a fallback model (Opus 4.8 or Opus 5) on every attempt, so the runner rejected
the answers (`fallback_writer`); four more attempts wrote the answer twice and failed the protocol check. Both tasks
are dual use (password cracking, protein design). They stay unlabelled; the analysis drops them as missing.

`relabel-v2-long` (65 cells), `relabel-v2-eqbench4` (600), `relabel-v2-cooperbench` (1,200) and
`relabel-v2-gamearena` (120) pinned at 16:15 UTC. The runner allows one open batch of relays per run, so relays of
different runs share the four slots.

## 2026-10-04 — all five runs finished

`relabel-v2-long` 65 of 65 (two judges read only part of a long prompt; the runner rejected them and the retries
passed). `relabel-v2-eqbench4` 600 of 600, `relabel-v2-gamearena` 120 of 120 (one judge wrote twice; retry passed),
`relabel-v2-cooperbench` 1,200 of 1,200. Every protocol check passed in all five runs. Total 7,056 labels of 7,065
cells. Finished 17:35 UTC at 84 per cent weekly usage (62 at the start), so the whole relabel used about 22 points.
