# pl-relabel-v2 — run log

## 2026-09-29 — pinned runs `v2-swe`, `v2-tau2`, `v2-tb4`

`make_prompts.py` wrote 1,194, 696 and 198 prompts. Every rebuilt old prompt matched its old run's
hash, and the 132 SWE-bench gate prompts equal `natural-prompt`'s variant B, whose labels are reused.
The analysis script was tested on synthetic labels (copies of the old labels), which were not kept.

## 2026-09-30 — runs `v2-swe` and `v2-tau2`: complete

- **Judging.** From `~/Developer/ADELE`, `judge-dispatcher-v2-low` relays (model opus) of about 100
  cells, 4 at a time: `v2-swe` 08:01–08:42 UTC (12 relays and one of 2 cells), `v2-tau2` 08:39–09:04 UTC (7 relays).
- **Relay slips.** Two SWE-bench cells were never sent: each was the last cell of its relay
  (django-13794@PLs, django-9296@PLs). They were sent in a separate relay once the gap was found. One
  cell, pytest-5809@PLs, was sent twice (by the relay before its own); the first completed answer is
  the label.
- **Coverage.** `v2-swe` 1,194/1,194 and `v2-tau2` 696/696 answered and parsed, every answer written
  by `claude-opus-5-5` (`writers.py`); no classifier stop.
- **Protocol check** over all judge transcripts: exact two-line message, effort low, working
  directory `~/Developer/ADELE`, no CLAUDE.md, own files only. Mean final context 7.5k tokens
  (SWE-bench) and 7.2k (tau2), 13–14 s per call.
- **Meters.** Before (08:01 UTC): 5-hour 3%, weekly 4%. After tau2 (09:04 UTC): 5-hour 74%, weekly
  13%. `v2-tb4` waits for the 5-hour reset at 11:30 UTC to keep a margin.

## 2026-09-30 — run `v2-tb4`: complete; analysis

- **Judging.** Two relays of 99 cells, 11:32–11:45 UTC, after the 5-hour reset.
- **`uefi-bootkit`.** A safety classifier stopped `claude-opus-5-5` on all three cells, and Claude Code
  finished them with `claude-opus-4-8` (as in `tau2-tb4-pl`). The relay's first three calls for this
  task ended at once without an answer, one with a truncated message ("Response file: /"), so it
  resent them; those are the answers written by Opus 4.8. They were moved to
  `judge-io/v2-tb4/responses_fallback/opus-low/`, and the cells were judged once more. Opus 4.8 wrote
  all three again (moved there as `*.retry.txt`), so the cells have no label. After the classifier
  stop, two of these judges also tried to Read the folder `~/Developer/ADELE`, which returned nothing.
- **Coverage.** 195/198 answered, parsed and written by `claude-opus-5-5`. One judge wrote its answer
  through the path `prompts/../responses/...`, which resolves to the right file.
- **Meters.** 5-hour 0% → 11%, weekly 14% → 15%.
- **Analysis.** `analysis/analyse.py`, run with `uv run --extra annotate --with scipy --with statsmodels`.
  The first run showed n = 330 tau2 rows per rubric in the agreement table. tau2 task ids repeat across
  domains, so the merge now keys on the benchmark as well (deviation 1 in `RESULTS.md`). No
  correlation depends on that table.
