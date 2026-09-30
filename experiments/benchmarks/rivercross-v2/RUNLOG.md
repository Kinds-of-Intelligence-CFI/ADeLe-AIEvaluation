# rivercross-v2 — run log

## 2026-09-30 — pinned runs `rc-state` and `rc-play`

`make_prompts.py` wrote 129 and 49 prompts from the rivercross frames. No prompt contains a solver
field (`dist_to_goal`, `cost_to_go`). The analysis script was tested on random synthetic labels,
which were not kept.

## 2026-09-30 — runs `rc-state` and `rc-play`: complete

- **Judging.** Three `judge-dispatcher-v2-low` relays (model opus) of 66, 63 and 49 cells,
  12:10–12:18 UTC.
- **Coverage.** 129/129 and 49/49 answered and parsed, all written by `claude-opus-5-5`
  (`writers.py`), with no classifier stop and no cell sent twice.
- **Protocol check.** Exact two-line message, effort low, working directory `~/Developer/ADELE`, no
  CLAUDE.md, own files only. Mean final context 7.0–7.1k tokens, 13–15 s per call.
- **Meters.** 5-hour 11% → 21%, weekly 15% → 16%.
- **Analysis.** `analysis/analyse.py`, run with `uv run --with scipy`. T3 fails; the other five
  tests hold.
