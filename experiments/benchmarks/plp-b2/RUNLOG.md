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

## 2026-09-30 — run `s-search`: complete

Three relays, 21:19–21:27 UTC. 162/162 answered and parsed, all by `claude-opus-5-5`. Protocol check
clean. E1 and E2 hold, and E3 fails.

## 2026-09-30 — pinned run `s-swe-gate` (amendment 2)

`make_s_swe.py` rebuilt the 44 current-text gate prompts and matched every stored hash, then wrote the
S prompts. `analysis/swe_gate.py` was tested on synthetic labels, which were not kept. That test printed
the baseline Spearman from existing labels (−0.554), which is recorded in the amendment.

## 2026-09-30 — run `s-swe-gate`: complete

One relay of 44 cells. 44/44 answered and parsed, all by `claude-opus-5-5`. Protocol check clean.
G1–G3 hold.

## 2026-10-01 — lab regression for S (amendment 3): fail, narrowly

See `../plp-candidate/lab-regression/RESULTS.md`, section "Candidate S". One confirmed loss: the covering-letter
example (Level 1) reads 2 under S, on a one-vote margin in pass 2. Nothing else broke.

## 2026-10-01 — pinned S-q runs (amendment 4)

`make_sq.py` built `PLp_Sq.txt` (S with four sentences replaced, checked) and wrote `sq-search` (54 × 3) and
`sq-swe-gate` (44; every S prompt reproduced its stored hash). `make_prompts_s.py --candidate sq` wrote
`labreg-sq1` (102 prompts, same items as S). No new 4-gram is shared with the frames or the lab items. The
analysis scripts gained `--run`/`--candidate` options; their defaults reproduce the stored S results (results
files unchanged).
