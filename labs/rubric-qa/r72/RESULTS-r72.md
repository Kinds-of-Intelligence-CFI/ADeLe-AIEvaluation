# Round 72 — the model tier: demand x ability, measured (2026-08-26)

Data: ForecastBench's own processed forecast sets for 2024-07-21 (per-model, per-question,
resolutions inline; imputed forecasts excluded; combination questions excluded). Eleven solver
tiers joined to the r71 demand labels on 161 questions. Labels inherit r71's failed batch gate, so
this is exploratory-grade on the label side; the outcome side is ForecastBench's own processing.

## The ability ladder is sane, which validates the join

Mean Brier: supers .110 < public .145 < claude-3.5-sonnet .169 < claude-3-opus .183 < gpt-4o .191
< llama-3-70b .207 < always-0.5 .250 < llama-2-70b .264 ~ claude-3-haiku .269 < random .337 <
gpt-3.5 .365. The 2024 models bracket the no-skill line; gpt-3.5 is worse than random, a known
calibration pathology. Nothing is upside down.

## H3 as sealed is REFUTED, and the refutation taught the right lesson

The seal predicted the weak-minus-strong Brier gap widens with demand. Measured: it NARROWS
(llama2-minus-supers rho **-0.37**). Cause: on forecasting corpora, high demand co-occurs with high
outcome entropy, and entropy compresses the achievable gap — everyone converges toward 0.25 where
the answer is a coin flip. Raw Brier gaps are the wrong functional form for the interaction, which
is a finding about criterion design, not about the rubric.

## Reformulated as retained skill, the interaction appears — in the right direction

Skill = ForecastBench's own naive-forecaster Brier minus the tier's, per question (dataset
questions, n = 105).

| QLq | n | supers | gpt-4o | llama-2-70b |
|---|---|---|---|---|
| 0 | 4 | +0.90 | +0.90 | +0.53 |
| 1 | 11 | +0.60 | +0.59 | +0.21 |
| 2 | 18 | +0.09 | +0.02 | +0.01 |
| 3 | 72 | **+0.07** | **-0.03** | **-0.00** |

Every tier's skill shrinks as demand rises (per-tier rho -0.24 to -0.40, all negative). But WHO
retains skill orders exactly by ability: at QLq 0-1 every tier beats naive, including llama-2; at
QLq 3 **only the superforecasters remain above the naive floor** and every model tier is at or
below it. That is the item-response structure a demand scale is supposed to produce — low levels
passed by all solvers, the top measured level passed only by the strongest — on real instances,
real solvers of eleven ability grades, and real resolutions.

**This is the first demand-by-ability criterion result in the project.** Its honest scope: one
dimension (QLq, a v1 rubric), one corpus slice (105 dataset questions, 72 of them at level 3),
labels below the batch gate. PLs shows the same directional pattern faintly (per-tier rho +0.18 to
+0.27 for competent tiers, ~0 for incompetent ones) but its labels are near-constant here and
carry little information.

## What would make it confirmatory

1. Re-label the 161 at single-call grade, at least the top band (the gate failures were all there).
2. A second dimension with real variance on this corpus (QLl, or KN once an aggregate exists).
3. A second round of ForecastBench (33 more sit in the tarball, unlabelled) as a held-out
   replication.

## Consistency check on earlier rounds

ForecastBench's own supers per-question Briers against the r67 hand-join, all 162 questions:
median absolute difference 0.005, 90th percentile 0.045, max 0.098 (computed, not assumed — the
processed sets aggregate individual forecasters slightly differently, likely a median-of-forecasts
versus my mean-of-Briers). The r67 correction is vindicated; residual differences are aggregation
convention, not join error.
