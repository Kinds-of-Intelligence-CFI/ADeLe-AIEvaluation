# Round 71 — the full-162 criterion run (2026-08-26)

Seal: `sealed_predictions_r71.md`. All 162 resolved questions of ForecastBench 2024-07-21,
batch-labelled by opus for PLs v19 and QLq (v1, unmodified); outcomes are horizon-matched
superforecaster Brier, clipped public-crowd Brier, and naive baselines. Data:
`labelled_162.json`.

## The batch gate FAILED, narrowly, so everything below is exploratory

The rule required >= 20/25 exact against the r67 single-call labels with none two off. Measured:
**19/25 exact, two items two off.** All six disagreements are at the top of the scale, every one
lower in batch than alone (Seine 4->3, Russia 5->3, storms 4->2, Belichick 3->2, Myanmar 2->3,
Olympics-AI 2->1). Batch labelling compresses the top band — consistent with r68's finding that the
upper levels are the under-determined part of the text. Per the seal these results are reported as
exploratory, not confirmatory.

## Findings

**1. PLs is flat on this corpus, now at full scale.** 146 of 162 questions at Level 2; eight 1s,
six 3s, one 4, one 5. rho against excess-over-naive Brier: **+0.09**. H1 confirmed: ForecastBench
cannot validate PLs, because standard forecasting questions barely exercise it — the full-scale
version of r67's conclusion.

**2. QLq varies, and predicts raw accuracy — but mostly through outcome entropy.** Distribution
0-3 across all 162. rho against raw supers Brier **+0.43**, public Brier +0.39 — but against
excess-over-naive, **-0.06** overall. High-QLq questions (drift-and-volatility estimation) are
intrinsically near coin flips, so the label predicts how uncertain the outcome is more than how far
solvers fall short.

**3. The one genuine desideratum-9 signal: QLq on dataset questions, rho +0.36 against
excess-over-naive** (n = 105). Where the questions are mechanical time-series items, higher
quantitative demand goes with superforecasters beating the naive baseline by less. That is the
demand-predicts-shortfall shape, on real instances with real outcomes, for the first time in the
project — exploratory pending the gate, and for a v1 rubric rather than a v2 one.

**4. The tier test is null.** The public-minus-supers gap sits near +0.10 at every QLq level and
does not widen with demand (rho +0.00). Two adjacent human tiers give little power; the
demand x ability interaction needs a weaker tier — the models — which requires the forecast
tarballs the sandbox cannot reach.

## What this closes and what it does not

The "full-162 criterion run" is done in the only form the available data supports: two dimensions,
one judge, batch labels below the gate, no model tier. It establishes the corpus conclusion for PLs
beyond doubt and surfaces one real, exploratory validity signal for QLq. Confirmatory desideratum-9
work needs (a) single-call or multi-judge labels at least for the top band, and (b) the model
forecast sets, which Pablo can fetch with:

    curl -L -o forecast_sets.tar.gz https://www.forecastbench.org/assets/data/forecast-sets/forecast_sets.tar.gz
    curl -L -o processed_forecast_sets.tar.gz https://www.forecastbench.org/assets/data/processed-forecast-sets/processed_forecast_sets.tar.gz

dropped anywhere in the connected repo folder.
