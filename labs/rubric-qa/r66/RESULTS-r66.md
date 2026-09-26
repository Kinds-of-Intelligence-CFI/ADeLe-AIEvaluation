# Round 66 — criterion validity pilot. The first test of desideratum 9. (2026-08-26)

25 real ForecastBench questions from the 2024-07-21 round, labelled for PLs by opus against a
meta-stripped rubric, joined to the mean Brier score of ~40 superforecasters per question.
Seal: `sealed_predictions_r66.md`.

## Headline: rho = +0.124. Ambiguous, and it does not survive stratification.

| | n | mean PLs | mean Brier | Spearman rho |
|---|---|---|---|---|
| **all** | 25 | 3.84 | 0.155 | **+0.124** |
| market questions | 10 | 3.80 | 0.120 | −0.166 |
| dataset questions | 15 | 3.87 | 0.175 | +0.313 |

The pre-registered rule called +0.124 ambiguous, one step above "no signal". The confound I named
before looking turned out not to be the problem: market and dataset questions got almost identical
mean demand (3.80 against 3.87), so the correlation is not selection. It is simply weak, and it
**reverses sign between strata**.

## Mean Brier by demand level, which is the more informative cut

| PLs | n | mean Brier |
|---|---|---|
| 1 | 2 | 0.002 |
| 2 | 4 | 0.088 |
| 3 | 2 | 0.003 |
| 4 | 5 | **0.367** |
| 5 | 12 | 0.136 |

**Non-monotonic, and Level 4 is forecast far worse than Level 5.** That is not noise; the cause is
visible in the items. Several Level 5 questions have near-zero Brier: Belichick coaching again
(0.000), an AI-attributed infrastructure disaster before 2025 (0.000), a tenfold protest spike in
Montenegro (0.002), a second Russian mobilisation wave (0.004). Each is about a reflexive system,
and each had an overwhelming base rate that made the answer easy.

**Demand-as-mechanism and outcome-uncertainty come apart.** PLs Level 5 keys on whether a
trustworthy model exists, which is a property of the situation. Forecast accuracy is dominated by
how lopsided the answer is, which is a property of the question. A rubric can be right about the
first and predict nothing about the second.

That is a real finding about what desideratum 9 can and cannot establish, and it was not visible
from any amount of text work.

## The pilot found something more valuable than the correlation

**The forecasting sentence over-fires on real items. 12 of 25 landed at Level 5.**

Opus routed to 5: three stock-price questions, a treasury bill rate, a high-yield credit spread,
two hurricane-count questions, whether Belichick would coach again, whether Russia would mobilise,
whether an AI cyberattack would be blamed for an infrastructure disaster, violence in Bolivia and
protests in Montenegro. Every one cited the same clause: *"Many forecasting questions belong here,
wherever a situation's parts react to one another and no model can be trusted to track it."*

"Will Belichick head coach another team" is not a Level 5 simulating demand. It turns on one man's
decision and a base rate. But almost any social or economic system has parts reacting to one
another, so the sentence as written catches nearly everything.

r58 tested this clause with a single designed falsifier and it passed at the median, though two of
three judges failed it. **On 25 real items it fails clearly.** That is a measured defect on real
data, and it is the strongest reason yet to have run against a benchmark rather than against
designed vignettes.

The Level 5 statement's actual discriminator — *the situation's indirect effects rival or outweigh
its direct ones* — is dropped by the forecasting sentence, which asks only that parts react.

## Recommendation

**Do not proceed to the full 162 yet.** The correlation was measured against a labelling that is
skewed by a clause we now know over-fires, so rerunning at six times the cost would buy a more
precise estimate of a suspect quantity. Fix the clause, re-label, then decide.

The proposed fix ties the forecasting sentence back to the indirect-effects test and adds the guard
the real items showed missing: a question that turns on one agent's decision, or that a base rate
answers, does not belong here however reflexive its setting. That is a construct-adjacent change
and goes to Pablo before it is written.

## Limits

Single judge, n=25. Superforecaster accuracy is not model accuracy. The per-model forecast tarballs
Pablo located are the next input, and the 2024-07-21 round then carries expert, crowd and model
forecasts on identical items.
