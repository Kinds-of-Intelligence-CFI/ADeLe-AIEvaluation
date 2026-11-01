# examples-regression — pre-registration

Committed and pushed before any label of this study. Pablo approved the regression and the full relabel on 2026-10-04.

**Question.** The examples review (`../examples-review`, commit `d4ec2ec`) reworded 33 bullets, replaced 9 and dropped
2. Each new bullet places where intended. Do the changes also shift how the judge labels other tasks?

## Design

- **Texts.** Per rubric (PLp, PLe, PLs, MSm, MSc), `old` = the file at `d4ec2ec~1`, `new` = at `d4ec2ec` (the active
  text). The memory rubrics have no benchmark labels and are not included.
- **Judge.** Opus 5.5 at effort low, `adele-judge-v2-low` via `judge-dispatcher-v2-low`, v2 prompt. One item per
  call; only answers written by `claude-opus-5-5` count. Opaque ids; all sets and texts shuffled (run `exreg-1`).
- **Sets** (`make_prompts.py`, `items.csv`):
  - B: the lab's 36 standing battery items (`7159671`), both texts, one label each. 4-gram check against the new
    bullets: B-D03 void for MSc; B-D08, B-E02 and B-L01 void for PLp (as numbered in `items.csv`, indices 7, 12, 24 and
    30). 352 calls.
  - R: 60 real tasks, 10 each from SWE-bench Verified, DeepSWE, Terminal-Bench 4.0, tau2 retail, EQ-Bench 4 and
    CooperBench coop prompts (seed 20261006), new text once; reference is the current Opus label (old text). 300 calls.
  - N: 20 of the R tasks under the old text again, to measure judge noise. 100 calls.
- **Pass 2** (`exreg-2`): every cell with a move of two levels or more, judged again under both texts, three repeats
  each. If more than 15 cells need it, I stop and report first.

## Decision rule (`analysis/analyse.py`)

Per rubric: a move is new minus old (B) or new minus the current label (R). A move of 2+ is confirmed if pass 2 moves
the item the same way. Drift: B and R pooled, more moves one way than the other, sign test p < 0.05, and a larger share
moving that way than in N. **A rubric passes** if it has no confirmed move of 2+ and no drift. A passing rubric goes to
the full relabel unchanged; a failing one is reported with the items behind it, and its relabel waits for Pablo.

## Predictions (sealed)

- All five rubrics pass: 0.55. Per rubric: PLp 0.85, PLe 0.75, PLs 0.75, MSm 0.95, MSc 0.85.
- If a rubric drifts, it is downward: 0.6 (the review removed glosses that pulled some items up).
- Per rubric, at least 70 per cent of B items unchanged: 0.7.
- The noise subset changes at least 15 per cent of its labels: 0.6.
- More than 15 cells need pass 2: 0.15.

## Cost

752 calls in pass 1, plus up to about 90 in pass 2. About 3.5 weekly points (now 60 per cent).

## The full relabel (pre-registered separately, after this study)

PLp, PLe, PLs, MSm and MSc on the seven agentic clean sets and the three social sets, about 7,065 calls. It runs in a
new session after the weekly reset (2026-10-06, 20:00 UTC), for each rubric that passes here.
