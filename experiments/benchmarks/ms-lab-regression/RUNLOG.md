# ms-lab-regression — run log

## 2026-10-02 — built (`ms-labreg1`), not run

`make_prompts.py` wrote 170 prompts and twelve relay files (four per repeat, at most 50 cells each): 510 calls
in pass 1. Checks at build time: the r75 texts are found verbatim in the r75 seal; the r36 pair equals the PL
regression's rebuild; battery-v1's registered and stored MSc levels match the lab record (`7159671`); set-P
prompts carry no example, and every other prompt carries the full rubric. The 4-gram check voided one item
(`B-D08-on-MSc`). Rebuilding gives the same ids and prompts.

`analysis/analyse.py`, `writers.py` (with `--set-aside`), `collect.py` and the pass-2 path
(`make_prompts.py --replicate`) were tested on synthetic labels and answers in a scratch folder. Nothing
from the test was kept. No judge has been launched.

## 2026-10-02 — rebuilt with two additions, not run

At the orchestrator's request, two additions:
- r30's eight MSc minimal pairs, in set L. Texts are verbatim from `r30/cset.csv`. Targets are r33's
  `MSc_new` medians, checked against the lab record.
- The battery's four pure MSc items on MSm, in set B. Targets are read from MSm's text.

`make_prompts.py` now writes 180 prompts and twelve relays: 540 calls. The 4-gram check voids two more items,
`L-r30-S1` and `L-r30-S2` ("will hear you out"). The analysis gained the r30 contrast check and the new MSm
check. It was tested again on synthetic labels in a scratch folder, which were deleted. Rebuilding gives the
same ids and prompts.
