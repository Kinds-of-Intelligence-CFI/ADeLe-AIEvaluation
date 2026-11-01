# jev-v1 — results

**Question.** On the v1 battery with the 18 v1 rubrics, does Jev's agreement with LLM judges depend on whether the
rubric can be read off the task (Pablo's hypothesis: rubrics that need partial solving defeat a classifier)?

**Answer.** Not against GPT-4o: the solve-to-judge rubrics agree at least as well as the read-off ones. Mean κ is
0.56 for solve-to-judge (QLq, QLl and MCt all 0.70) and 0.43 for read-off. Read-off rubrics are mixed: KNn 0.92, but
AS, CEe, KNc and MCu about 0.15, where Jev sits up to two levels below GPT-4o. Jev's expected level ranks items much as
GPT-4o does (Spearman 0.6 to 0.9 on most rubrics): its weakness is the level scale more than the ordering.

**Status.** Jev and GPT-4o complete (2026-10-04; 1,000 items, 23.6M input tokens, about $1). The Opus core (60 items
× 18 rubrics, 1,080 calls) awaits Pablo's go; until then the hypothesis is tested against GPT-4o only.

## Results (Jev against GPT-4o, 1,000 items)

| group | mean κ | mean exact | mean within one | Jev labels at 0 or 5 |
|---|---|---|---|---|
| read-off (12 rubrics) | 0.43 | 0.57 | 0.78 | 51% |
| solve-to-judge (6 rubrics) | 0.56 | 0.56 | 0.82 | 47% |

Per rubric: `results/analysis.json`. Highest κ: KNn 0.92, QLq, QLl and MCt 0.70, KNa 0.68. Lowest: AS 0.15, CEe,
KNc and MCu 0.17.

## Predictions (sealed)

| prediction | p | outcome so far |
|---|---|---|
| mean κ(Jev, GPT-4o) higher on R than on S | 0.7 | **no** (0.43 against 0.56) |
| on R, κ(Jev, Opus) within 0.1 of κ(GPT-4o, Opus) | 0.5 | needs the Opus core |
| on S, more than 0.1 below | 0.6 | needs the Opus core |
| κ(Jev, GPT-4o) below 0.5 on QLq and QLl | 0.6 | **no** (0.70 and 0.70) |
| Jev piles at 0 or 5 more on S than on R | 0.6 | no (47% against 51%) |
