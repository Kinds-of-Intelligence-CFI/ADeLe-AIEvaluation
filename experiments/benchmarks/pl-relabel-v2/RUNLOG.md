# pl-relabel-v2 — run log

## 2026-09-29 — pinned runs `v2-swe`, `v2-tau2`, `v2-tb4`

`make_prompts.py` wrote 1,194, 696 and 198 prompts. Every rebuilt old prompt matched its old run's
hash, and the 132 SWE-bench gate prompts equal `natural-prompt`'s variant B, whose labels are reused.
The analysis script was tested on synthetic labels (copies of the old labels), which were not kept.
