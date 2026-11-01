# jev-v1 — pre-registration

Committed and pushed before any Jev label of this study. Pablo's hypothesis (2026-10-04): judging how much planning or
simulation a task needs requires partly working out its solution, which a classifier with no reasoning cannot do; so
Jev should match an LLM judge on rubrics that can be read off the task, and fall short on rubrics that need solving.

**Question.** On the v1 battery with the 18 v1 rubrics, does Jev's agreement with LLM judges depend on whether the
rubric can be read off the task?

## Design

- **Items.** 1,000 battery items, stratified by benchmark (seed 20261004, at least 3 per benchmark); the first 3 per
  benchmark (60 items) are the core (`run_jev_v1.py`, `sample.csv`). State: the item's `question` field.
- **Judges.**
  - Jev (`jev-1.13.0`), all 1,000 items, the 18 rubrics in one request (as `../jev-pilot`).
  - GPT-4o: the paper's labels, shipped with the battery, all 1,000 items.
  - Opus 5.5 at effort low, v2 prompt with the v1 rubric texts, the 60 core items × 18 rubrics (1,080 calls). Only
    if Pablo approves the cost; otherwise the study reports Jev against GPT-4o alone.
- **Groups, fixed now.** Read-off rubrics (R): KNa, KNc, KNf, KNn, KNs, CEc, CEe, AT, VO, MS, AS, MCu. Solve-to-judge
  rubrics (S): QLq, QLl, MCt, MCr, SNs, CL. The split follows the hypothesis: S rubrics ask how much reasoning,
  abstraction or spatial work the solution takes.
- **Measures.** Per rubric: quadratic weighted κ, exact and within-one agreement, between each pair of judges.
  Group means of κ.

## Predictions (sealed)

- Mean κ(Jev, GPT-4o) is higher on R than on S: 0.7.
- On R, κ(Jev, Opus) is within 0.1 of κ(GPT-4o, Opus) on average: 0.5. On S it is more than 0.1 below: 0.6.
- κ(Jev, GPT-4o) on QLq and QLl is below 0.5: 0.6.
- Jev's labels pile up at 0 or 5 more on S than on R (share of labels at 0 or 5): 0.6.

## Cost

Jev: about 21M input tokens, under $1. Opus core: 1,080 short calls, about 4 to 5 weekly points, pending Pablo's go.
