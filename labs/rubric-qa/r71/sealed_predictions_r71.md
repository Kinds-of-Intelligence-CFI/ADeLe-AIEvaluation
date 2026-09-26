# r71 sealed — the full-162 criterion run: PLs and QLq against forecaster accuracy (2026-08-26)

All 162 resolved questions of ForecastBench round 2024-07-21, labelled for two dimensions:
PLs v19 (meta-stripped, examples kept) and QLq (v1 Quantitative Reasoning, unmodified). Outcomes:
horizon-matched superforecaster Brier (r67's corrected join), clipped public-crowd Brier, naive
baselines (market freeze value; 0.5 for dataset questions).

## Design decisions, declared before labelling

1. **Batched labelling, gated by the pilot.** One call per item for 162 x 2 dimensions is not
   proportionate; items are labelled in batches of 12 by opus. The gate: the 25 r67 items sit
   inside these batches, and batch labels must agree with r67's single-call labels on >= 20 of 25
   exact with none 2 off, or the batch method is rejected and the run stops.
2. **One label per question, not per horizon.** Dataset questions resolve at five horizons and the
   true demand can differ by horizon (r67). This run accepts that blur and says so; the Brier
   averaged over horizons is matched to a label averaged over the same ambiguity.
3. **KN is not labelled.** v1 splits knowledge across five domain files with no aggregate rubric.
   QLq carries the base-rate and statistical-extrapolation reading that r66/r67 suggested drives
   these items; attribution is between PLs and QLq.

## Sealed hypotheses

- H1: **PLs varies little** (r67: most items low under the severity doctrine) and correlates
  weakly with every accuracy criterion, |rho| < 0.3.
- H2: **QLq varies more and correlates better** with excess-over-naive Brier than PLs does. This is
  Pablo's interacting-dimension conjecture made testable.
- H3: **Tier test**: the public-minus-supers gap widens with demand on whichever dimension carries
  variance — the demand x ability interaction that is the correct form of desideratum 9.

## Decision rules

1. Batch gate as above; failing it stops everything.
2. Report Spearman rho for each dimension against: matched supers Brier, supers excess over naive,
   clipped public Brier, and the public-minus-supers gap. No post-hoc slicing beyond the
   pre-registered market/dataset strata.
3. Whatever the result, it is reported as measured; a null on H3 is a finding about this corpus,
   not a license to re-edit any rubric.
