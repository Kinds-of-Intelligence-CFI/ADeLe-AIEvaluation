# r66b — separating the criterion from the rubric (2026-08-26)

Same 25 items and labels as r66. New data: the general-public individual forecasts (fetched from
the datasets repo's LFS store, 47,679 forecasts) and the market freeze values, giving three
additional criteria beyond raw superforecaster Brier.

**Data-quality note for any future use of the public file**: 292 public forecasts lie outside
[0,1], with a maximum of 5.0e8 — raw numbers typed where probabilities were expected. Everything
below clips to [0,1]. Unclipped, the file is unusable.

## The same labels against four criteria

| criterion | rho vs PLs |
|---|---|
| raw superforecaster Brier (r66's) | +0.124 |
| superforecaster Brier minus naive baseline (market freeze value; 0.5 for dataset) | **+0.246** |
| public-crowd Brier (clipped) | +0.227 |
| public median-forecast Brier | +0.188 |
| skill gap, public minus supers | +0.094 |

Mean by level (public, clipped): 0.116 / 0.245 / 0.170 / 0.343 / 0.269.

## Reading

1. **Part of r66's weakness was the criterion.** Raw Brier bundles irreducible outcome entropy (a
   property of the question) with demand-sensitive shortfall (the only part a demand rubric could
   predict). Subtracting a naive baseline doubles the correlation. So the criterion design in the
   r66 seal was naive, and that error is mine.
2. **The L5-below-L4 inversion survives every criterion.** That points at the labels, not the
   outcome measure: the over-firing forecasting sentence routed base-rate-answerable items to 5,
   and those items are easy under any scoring.
3. **Nothing here yet passes the pre-registered signal bar (0.30).** All conclusions remain
   pilot-grade, single-judge, n=25.
