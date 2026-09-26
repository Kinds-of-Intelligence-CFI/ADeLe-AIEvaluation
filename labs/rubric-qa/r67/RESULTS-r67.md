# Round 67 — the genre-free repair, relabel, and a corrected criterion (2026-08-26)

Seal: `sealed_predictions_r67.md`. Same 25 ForecastBench items as r66, relabelled by opus against
meta-stripped PLs v19. Plus a correction to the criterion itself, found while re-checking the join.

## First: r66's Brier join was buggy, and that is mine

ForecastBench dataset questions resolve at **five horizons each**, and each superforecaster
forecast carries the horizon it targets. r66's join pooled all of a question's forecasts against
its *first* resolution only. Corrected (forecast matched to its own horizon's outcome), the Briers
move by up to 0.36 per question — and the picture changes:

| criterion, corrected join | v16-era labels | v19 labels |
|---|---|---|
| raw supers Brier | **+0.304** | +0.101 |
| supers minus naive baseline | **+0.434** | **+0.456** |

So r66's headline of "+0.124, ambiguous" was the product of a naive criterion *and* a join bug.
With both fixed, even the suspect old labels clear the pre-registered 0.30 bar against
excess-Brier. This is recorded as a measurement error of mine, not a property of any rubric.

## The v19 relabel: the misroute is fixed, and the distribution collapsed

| | v16-era | v19 |
|---|---|---|
| distribution | 1:2, 2:4, 3:2, 4:5, **5:12** | **2:21**, 3:1, 4:2, 5:1 |

19 of 25 items moved, mean shift −1.5 levels. Everything the r66 diagnosis flagged moved correctly:
stocks, SOFR, the treasury rate, the Andorra spike and Belichick all came off 5, each citing the
new standing-rate clause or the new Note. The two items still at 4 (the Seine cancellation, the
21–25 storm band) are the two worst-forecast items in the sample (mean Brier 0.400), which is the
first time the labels and the outcomes have pointed the same way at the top.

Seal rules: (1) ≤5 at L5 — pass, one. (2) the inversion — dissolved, though with n=1 at L5 no
claim is made. (3) rho vs excess ≥ +0.20 — pass at +0.456, but fragile: with 21 ties it rests on
four points.

## The honest reading: the corpus, not the rubric, is now the binding constraint

Twenty-one items at Level 2 is not over-correction by the clause — spot-checking the reasoning,
each application is consistent with Pablo's own rulings. The weather items fell to 2 by the
executability route (published forecasts are a model that is theirs to run), which is exactly the
swe-0461 logic. The Bolivia and Andorra items fell because a base rate answers a 30-day count
comparison as well as anything can, which is how superforecasters themselves attack them.

The conclusion that follows is about the corpus: **standard forecasting-benchmark questions mostly
make low simulating demands under the severity doctrine**, because base rates and published
models are the simplest adequate strategy for most of them. The r58 finding that "forecasting
populates the top band" was an artefact of designed items plus the over-firing clause. Real items
that genuinely need mechanism-modelling (the Seine, the storm band) exist but are a minority.

Two consequences:

1. **PLs criterion validity cannot be settled on this slice alone**, because PLs barely varies on
   it. A valid test needs items where the demand varies: the full 162 will contain some, but a
   physical-simulation-heavy corpus would be better.
2. **The old labels' +0.43 is not validity evidence either.** The over-firing clause routed
   contested items to 5, contested items are exactly the high-Brier ones, so the correlation was
   partly outcome-entropy leaking into the labels.

## Known residual issues, for the full run

- Dataset questions are **horizon-ambiguous as written** (five resolution dates per question), and
  the right demand label can differ by horizon: climatology is optimal at a year, a runnable model
  wins at a week. The full run should label per (question, horizon).
- One judged inconsistency: the 21–25 storm band scored 4 while >25 storms scored 2. Defensible
  (a band needs the season carried finely, a tail needs only the rate) but worth a second judge.
- Pablo's question — is another dimension driving the result — is now an empirical design item:
  the full run should label QL and KN alongside PLs, so whatever predicts accuracy can be
  attributed rather than assumed.
