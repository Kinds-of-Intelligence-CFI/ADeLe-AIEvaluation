# plp-o-relabel — run log

## 2026-10-01 — pinned

`make_prompts.py` wrote `o-swe` (398), `o-tau2` (232) and `o-tb4` (66). Every `pl-relabel-v2` PLp prompt was rebuilt
from the previous text and matched its stored hash; the 44 `o-swe-gate` prompts match what this script builds.
`analysis/analyse.py` was tested by feeding the current-text labels in as O: it reproduced `pl-relabel-v2`'s
results exactly. The test files were not kept.

## 2026-10-01 — judging complete

Seven `judge-dispatcher-v2-low` relays (four SWE of about 100, two tau2 of 116, one Terminal-Bench of 66), at most
four at once. 398/398, 232/232 and 65/66 answered and parsed, all by Opus 5.5. `uefi-bootkit`: classifier stop,
answer by Opus 4.8, moved to `responses_fallback/`, judged once more, same again, moved aside (`.retry.txt`): no
label. No relay dropped or repeated a cell (checked against `prompts_index.csv`). Analysis run with
`uv run --extra annotate --with scipy --with statsmodels` (uv.lock deleted).
