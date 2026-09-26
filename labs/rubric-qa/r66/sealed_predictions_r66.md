# r66 sealed — criterion validity pilot: does PLs demand predict forecaster accuracy? (2026-08-26)

**The first test of desideratum 9 in this project.** Every previous round asked whether the text
does what it says. This asks whether the labels predict anything.

## Data, all real and pre-existing

- ForecastBench 2024-07-21 round. 189 questions, 40 superforecasters, 7,693 individual forecasts,
  each with the forecaster's probability, reasoning and the searches they ran.
- Joined to the published resolution set: **162 questions have both forecasts and a resolution.**
- Per-question outcome = mean Brier score across the ~40 superforecasters. Range 0.000 to 0.892,
  median 0.100, so there is real variance to predict.
- Pilot sample: **25 questions**, stratified by source (3 from each of the seven larger sources,
  2 from each of the two smaller), seeded, drawn before any labelling.

Labels are PLs levels from opus, one question per call, scored against a meta-stripped rubric.
Single-judge for the pilot; a positive result triggers the full 162 with three judges.

## Hypothesis

Superforecaster Brier rises with PLs demand. Questions that need a more complex or more accurate
model of a situation are forecast less well.

## Pre-registered decision rule

- **Signal**: Spearman rho >= 0.30 between PLs label and mean Brier. Proceed to the full 162.
- **No signal**: rho <= 0.10. Report that PLs demand does not predict superforecaster accuracy on
  this set, and say so in the provenance record rather than looking for a friendlier cut.
- **Ambiguous**: between. Run the full 162 before concluding anything.

## The confound I must control, named before seeing the numbers

Market questions (manifold, metaculus, polymarket, infer) are **selected because they are
contested**, so their resolutions cluster near 0.5 and their Brier scores are mechanically higher
than dataset questions whose answers are often near-certain. If PLs also scores market questions
higher, a positive rho could be pure selection rather than anything about simulating.

Three checks, all pre-registered:

1. **Within-stratum rho**, computed separately for market and dataset questions. If the effect only
   exists between strata and vanishes within them, it is selection.
2. **Partial correlation controlling for forecaster uncertainty**, using the mean forecast's
   distance from 0.5 as the proxy. A question the crowd finds a coin-flip is hard whatever its
   demand.
3. **Report the market/dataset split of the labels themselves**, so any confounding is visible
   rather than inferred.

A positive rho that survives (1) and (2) is worth the full run. One that does not survive them is
reported as a selection artefact.

## What this cannot show

Superforecaster accuracy is not model accuracy. This tests whether the demand scale orders *human
expert* performance. Pablo has located the per-model forecast tarballs on the ForecastBench site,
which the sandbox cannot reach; once those are pulled the same pipeline runs against models, and
the 2024-07-21 round then carries expert, crowd and model forecasts on identical items.
