# plp-o-relabel — run log

## 2026-10-01 — pinned

`make_prompts.py` wrote `o-swe` (398), `o-tau2` (232) and `o-tb4` (66). Every `pl-relabel-v2` PLp prompt was rebuilt
from the previous text and matched its stored hash; the 44 `o-swe-gate` prompts match what this script builds.
`analysis/analyse.py` was tested by feeding the current-text labels in as O: it reproduced `pl-relabel-v2`'s
results exactly. The test files were not kept.
