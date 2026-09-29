# natural-prompt — run log

## 2026-09-29 — pinned runs `np-plp-s55h` and `np-gate-opuslow`

`make_runs.py` wrote 44 and 132 prompts. For every cell the old prompt, rebuilt from the same rubric
and task text, matched the stored hash of `swepl-gate`, so only the wording differs. The natural
prompt is slightly shorter (for example 10,081 against 10,166 characters). New agents
`adele-judge-v2-low`, `adele-judge-v2-high`, `judge-dispatcher-v2-low` and `judge-dispatcher-v2-high`
were installed; the harness loads them from the next user message. The analysis script was tested
on synthetic labels, which were not kept.

## 2026-09-29 — runs `np-plp-s55h` and `np-gate-opuslow`: complete

- **Judging.** After the weekly reset: one `judge-dispatcher-v2-high` relay (44 cells, model sonnet)
  and three `judge-dispatcher-v2-low` relays (44 cells each, model opus), 20:35–20:41 UTC.
- **Coverage.** A: 44/44 answered by `claude-sonnet-5-5` at effort high, no safeguard stop, so no
  retry was needed. B: 132/132 answered by `claude-opus-5-5` at effort low. Two B calls got a
  "connection lost" notice after their answer was written; both answers are complete.
- **Protocol check** over the 176 transcripts: exact two-line message, working directory
  `~/Developer/ADELE`, no CLAUDE.md, own files only.
- **Meters.** Before (20:35 UTC): 5-hour 0%, weekly 0%. After: 5-hour 10%, weekly 2%.
- **Analysis.** A passes; B fails check 3 (shifts +0.16 PLp, +0.27 PLe, all upward). Verdict: "fixes
  the flags, but changes the labels". The answer-length path in `analyse.py` was fixed (it pointed one
  folder too high); that figure is exploratory.
