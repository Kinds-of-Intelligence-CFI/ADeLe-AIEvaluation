# plp-b2 — run log

## 2026-09-30 — pinned run `b2-search`

`make_b2.py` built `PLp_B2.txt`. It differs from the source file by the four approved lines only, with
no word 4-gram shared with the 54 frames, and 54 prompts are to be judged three times each. The analysis
was tested on synthetic labels, which were not kept. It reproduces the amendment 2 coefficients for the
current text (0.101 and 0.328).

## 2026-09-30 — run `b2-search`: complete

Three `judge-dispatcher-v2-low` relays of 54 cells (model opus). 162/162 answered and parsed, all by
`claude-opus-5-5`, with no classifier stop. Protocol check clean. `analysis/analyse.py`: E1, E2 and E3
all fail. The lab regression was not started, as the pre-registration requires.

## 2026-09-30 — pinned run `s-search` (amendment 1)

`make_s.py` built `PLp_S.txt`: B2 plus six insertions, checked, with no 4-gram shared with the frames.
54 prompts are to be judged three times each.
