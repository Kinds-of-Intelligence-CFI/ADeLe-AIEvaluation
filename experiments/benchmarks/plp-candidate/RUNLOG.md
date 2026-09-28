# plp-candidate — run log

## 2026-09-28 — pinned runs `cand-tb`, `ctrl-tb`, `cand-swe`, `cand-tau2`

`make_prompts.py` wrote 360 prompts. Prompts built with the current text reproduced every original
prompt hash (`tb4pl-r1`, `tau2pl-r1`, `swepl-gate-low`, `swepl-r1-low`). So only the Level 3
sentence differs between the arms. The analysis script was tested on synthetic labels, which were
not kept.

## 2026-09-28 — all four runs complete

Seven `judge-dispatcher-low` relays, 08:35–09:02 UTC, plus one retry.
- **Coverage.** 360/360 cells answered and parsed.
- **Writers.** `uefi-bootkit` in `ctrl-tb` was written by `claude-opus-4-8` on both attempts, so it
  has no label. Every other answer was written by `claude-opus-5-5`.
- **Protocol check** over all 361 judge transcripts: exact message, effort `low`, no CLAUDE.md,
  own files only. The one flag is a Write cut off by the classifier stop on `uefi-bootkit`, which
  wrote nothing.
- **Cost.** Mean final-request context 7.2k–7.7k tokens, 16–20 s per call.
