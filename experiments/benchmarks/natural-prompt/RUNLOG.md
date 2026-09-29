# natural-prompt — run log

## 2026-09-29 — pinned runs `np-plp-s55h` and `np-gate-opuslow`

`make_runs.py` wrote 44 and 132 prompts. For every cell the old prompt, rebuilt from the same rubric
and task text, matched the stored hash of `swepl-gate`, so only the wording differs. The natural
prompt is slightly shorter (for example 10,081 against 10,166 characters). New agents
`adele-judge-v2-low`, `adele-judge-v2-high`, `judge-dispatcher-v2-low` and `judge-dispatcher-v2-high`
were installed; the harness loads them from the next user message. The analysis script was tested
on synthetic labels, which were not kept.
