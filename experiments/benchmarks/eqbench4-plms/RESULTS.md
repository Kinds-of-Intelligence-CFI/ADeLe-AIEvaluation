# eqbench4-plms — results

**Question.** On EQ-Bench 4, a benchmark of 8-turn support conversations with a simulated person who hides a core
issue, do the social rubrics (MSm, MSc) and the planning rubrics (PLp, PLe, PLs) track how often frontier models get
the person to disclose it?

**Answer.** No. The new outcome works, but the rubrics do not track it. Disclosure varies a lot across scenarios
(from 0 to all 10 models), the outcome judge agrees with itself on 93% of repeats, and models with a higher EQ-Bench
Elo get more disclosures (ρ = +0.85, n = 10). But MSm is 4 on 119 of 120 scenarios, so it cannot rank them, and MSc
(3 or 4) does not fall with disclosure within either source type (−0.08). PLp, PLe and PLs show nothing within
source type.

**Status.** Complete (2026-10-03). Labels: 600 cells (120 scenarios × 5 rubrics), all by Opus 5.5 at effort low, check
OK. Outcome: 1,260 judge calls (1,200 + 60 repeats), all valid, all written by Opus 5.5, no classifier stops. Four of
eight sealed predictions held.

## Design

See `PREREGISTRATION.md`, pushed before any label (`c279564`). 120 scenarios (60 generated, 60 hand-authored). Labels:
what the tested model sees plus the persona's hidden brief. Outcome: per transcript, did the person openly acknowledge
the hidden core issue (CORE yes / partly / no), for 10 models; scenario `disclosure_rate` = share of models with yes.
Primary test: MSm and MSc against disclosure rate within source type, combined by Fisher z.

## Pre-registered results

From `results/analysis.json` (`analysis/analyse.py`).

**Levels (120).** MSm 4/5 = 119/1. MSc 3/4 = 75/45 (generated: all 3; hand-authored: 15/45). PLp 2/3 = 87/33. PLe 3 on
119. PLs 3 on 114.

**Outcome.** Across 1,200 transcripts, CORE yes 268, partly 662, no 270. Scenario disclosure rate: mean 0.22, median
0, range 0–1. Generated 0.30, hand-authored 0.14.

| test | ρ | p | note |
|---|---|---|---|
| MSm against disclosure rate, within source (primary) | +0.18 | 0.19 | hand-authored only (generated: MSm constant) |
| MSc against disclosure rate, within source (primary) | −0.08 | 0.53 | hand-authored only (generated: MSc constant) |
| PLp, within source | −0.12 | 0.20 | |
| PLe / PLs, within source | +0.13 / −0.04 | ns | |
| MSc / PLp against disclosure, all 120 pooled | −0.22 / −0.20 | 0.017 / 0.03 | between-source difference |
| MSc against items voiced, within source | −0.25 | 0.06 | |

**Checks.** Outcome repeatability: CORE exact agreement 0.93, κ 0.87; items exact 0.97 (60 repeats). Model-level
disclosure rate against EQ-Bench 4 Elo: ρ = +0.85, p = 0.002 (n = 10; Opus 5 highest at 0.33, Gemini 3.1 Pro lowest at
0.13).

**Sealed predictions.**

| prediction | p | outcome |
|---|---|---|
| median MSm at least 3 | 0.85 | held (4) |
| median MSc at least 3 | 0.8 | held (3) |
| MSm takes at least two levels with 15 or more scenarios each | 0.6 | failed (119 at 4) |
| MSm against disclosure, within source, negative, p < 0.05 | 0.3 | failed (+0.18) |
| MSc against disclosure, within source, negative, p < 0.05 | 0.3 | failed (−0.08) |
| PLp against disclosure, within source, negative, p < 0.05 | 0.15 | failed (−0.12) |
| outcome repeatability at least 0.8 | 0.7 | held (0.93) |
| model-level disclosure against Elo positive, p < 0.05 | 0.5 | held (+0.85) |

## Exploratory

Disclosure differs strongly by scenario type and persona brief, which the rubrics do not see as different:
hand-authored power-imbalance scenarios 0.00, ego-threat 0.08, reality distortions 0.11, social exclusion 0.38.
Among generated personas, externalizing or minimizing defences sit near 0.1, counter-attacking near 0.6.

## Reading

- **The outcome is sound.** It is reliable and it orders models the way EQ-Bench's own pairwise Elo does. So the null
  is in the rubrics, not the outcome.
- **MSm saturates.** Every persona hides a core issue and has defences, so every scenario needs a model of hidden
  beliefs: MSm gives 4 throughout. What makes disclosure hard here (power imbalance, a defensive stance, a hostile
  framing) is not a different level of MSm as the rubric is written.
- **MSc separates the two scenario sources** (generated all 3, most hand-authored 4), and pooled it does fall with
  disclosure (−0.22), but within a source it does not. The pooled result mixes two sets with different outcomes.
- **The judge sees the hidden brief.** The rubric judge rates demand from the persona's instructions, as for tau2. A
  rating from what the tested model sees alone might differ; not tested.

## Deviations and caveats

- No deviations.
- Same-family judging: the outcome judge is Claude, and Claude Opus 5 is the top model on disclosure as on Elo.
- One transcript per (scenario, model); the persona is played by one model (Gemini 3.1 Pro).
