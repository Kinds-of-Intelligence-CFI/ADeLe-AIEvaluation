# pls-computer — run log

## 2026-10-04 — setup

`make_prompts.py` wrote 209 prompts (run `plsc-1`). Every R candidate prompt is its released prompt with the
rubric text swapped (the released prompt contains the current text exactly once; checked). Every prompt file's
SHA-256 matches the index. The 4-gram check voided M3a ("and there is no", shared with the new Level 3 bullet);
M3a and M3b were reworded in parallel and the check rerun: no item shares a 4-gram. `analysis/analyse.py` was
tested on synthetic labels, which were not kept.
