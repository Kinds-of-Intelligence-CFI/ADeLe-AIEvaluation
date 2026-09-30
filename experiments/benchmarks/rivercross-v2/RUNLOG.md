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

## 2026-09-30 — pinned run `rc-contrast` (amendment 1)

`make_contrast.py` solved 50 puzzles and drew 9 search pairs and 21 length pairs: 59 distinct states,
59 PLp prompts, each to be judged three times. It reproduces the existing frame wording exactly (checked
on `chain-3-boat-1#s2`). The library gives missionaries-cannibals with boat 2 and boat 3 the same name,
so the script renames them by boat size. No prompt contains a solver value. `analysis/contrast.py` was
tested on random synthetic labels, which were not kept.

## 2026-09-30 — run `rc-contrast`: complete

- **Judging.** Three `judge-dispatcher-v2-low` relays (model opus) of 59 cells, one per repeat folder,
  12:28–12:39 UTC.
- **Coverage.** 3 × 59 answered and parsed, all by `claude-opus-5-5`, with no classifier stop.
  `writers.py` counts each cell as called three times, because the repeats share file names.
- **Transcript gap.** One answer (`missionaries-cannibals-4-boat-3--R-C2.C3.M1.M3`, `opus-low-r1`) has
  no matching Write call in its transcript. The assistant record holding it is missing, but the
  harness confirmation of the created file is there, and every record is from Opus 5.5. `writers.py`
  now falls back to that confirmation and records an `evidence` column (deviation in `RESULTS.md`).
  The `rc-state` and `rc-play` writers files were regenerated and gain only that column.
- **Protocol check.** Clean.
- **Analysis.** `analysis/contrast.py`: L1 holds, S1 fails.
