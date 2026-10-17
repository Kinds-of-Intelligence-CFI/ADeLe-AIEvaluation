# pls-computer — run log

## 2026-10-04 — setup

`make_prompts.py` wrote 209 prompts (run `plsc-1`). Every R candidate prompt is its released prompt with the
rubric text swapped (the released prompt contains the current text exactly once; checked). Every prompt file's
SHA-256 matches the index. The 4-gram check voided M3a ("and there is no", shared with the new Level 3 bullet);
M3a and M3b were reworded in parallel and the check rerun: no item shares a 4-gram. `analysis/analyse.py` was
tested on synthetic labels, which were not kept.

## 2026-10-04 — pass 1 (`plsc-1`) and pass 2 (`plsc-2`): complete

Pass 1: four `judge-dispatcher-v2-low` relays of 51 to 53 cells, about 5 minutes each, run concurrently.
209/209 answered and parsed, all written by `claude-opus-5-5`, no classifier stop, no cell called twice. One relay
reported 51 sent for 52 cells; all 52 answers exist and each matches a Write call. One item needed pass 2 (B-D02,
a two-level move): one relay of 6 cells, 6/6 parsed, all Opus 5.5. The move did not repeat. Verdict: pass.
