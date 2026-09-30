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

## 2026-09-30 — pinned amendment 2 runs (`rc-search`, `rc-search-vo`, `rc-solve-pilot`, `rc-solve`)

`make_search.py` solved 93 puzzles (3,942 states 2 or more crossings from the goal) and drew 54 states
(6 per cell) and 12 pilot states. The first band choice (mid 5.5–7.5) left only 5 puzzles in one cell,
so the mid band was widened to 5–8 before any label. New agents `rc-solver` and `rc-solver-dispatcher`
(copies in this folder) were installed in `~/Developer/ADELE/.claude/agents/`; the harness loads them
from the next user message. `score_solve.py` was checked on library-generated solutions, and
`analysis/search.py` on random synthetic labels (not kept). No prompt contains a solver value.

## 2026-09-30 — amendment 2 runs: complete

- **PLp and VO.** Three `judge-dispatcher-v2-low` relays for `rc-search` (54 × 3) and one for
  `rc-search-vo` (54). All answers were written by `claude-opus-5-5` and parsed. Protocol checks
  clean.
- **Solver pilot.** Five `rc-solver-dispatcher` relays (model haiku) launched at once alongside the
  PLp relays hit the concurrent-subagent limit: t2 sent nothing and was relaunched after the others
  finished. 60/60 attempts, all by `claude-haiku-4-5-20251001`, success 0.767 → the solver is Haiku
  (rule: Sonnet only at 0.15 or less).
- **Solver main run.** Five relays, three at a time. One t1 cell failed with a transient harness
  error before answering and was sent once more. 270/270 attempts, all by Haiku 4.5, no classifier
  stop.
- **Analysis.** `analysis/search.py --solver-model claude-haiku-4-5-20251001`: H2 and C2 hold; H1,
  H3, C1 and C3 fail.

## 2026-09-30 — pinned amendment 3 runs (`rc-solve-sonnet`, `rc-solve-opus`)

`make_strong.py` copied the 54 `rc-solve` prompts (hashes checked) into two runs. `analysis/strong.py`
was tested on synthetic outcomes, which were not kept.

## 2026-09-30 — amendment 3 runs: complete

- **Judging.** From 16:32 UTC, after the 5-hour reset, `rc-solver-dispatcher` relays with at most
  four running at a time: Sonnet 5.5 and Opus 5.5, attempts t1–t5.
- **Stalls.** Opus t3 (13 answers), Opus t4 (9) and Sonnet t3 (1) stopped on the harness stream
  watchdog. The missing cells (41, 45, 53) were sent again in new relays; the attempt folders hold
  no duplicate answers.
- **Coverage.** 270/270 attempts per model, all by the intended model (`claude-sonnet-5-5`,
  `claude-opus-5-5`), with no classifier stop.
- **Analysis.** `analysis/strong.py`: O1 holds for both models, O2 and P1 fail for both, F2 holds
  for Sonnet, and Opus's failure tests are at the ceiling.
