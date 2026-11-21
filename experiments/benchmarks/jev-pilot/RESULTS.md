# jev-pilot — results

**Question.** Can TypeSafe's Jev, a fast classifier with no written reasoning, reproduce our Opus 5.5 (low) demand
labels on agentic and social tasks, and keep their criterion validity?

**Answer.** For the social rubrics, mostly yes; for the planning rubrics, no.
- MSc agrees closely with Opus (κ 0.96, 91 per cent exact). MSm agrees on the social sets (κ 0.93) but not on the
  agentic ones (κ 0.16: Jev says 0 where Opus says about 2).
- PLp, PLe and PLs agree only loosely (κ 0.44 to 0.49). PLs is the worst (12 per cent exact): Jev puts 79 per cent of
  tasks at 0 and 9 per cent at 5, where Opus mostly says 1 or 2.
- Jev's expected level keeps part of PLp's signal: −0.46 with solve rate on SWE-bench Verified (Opus −0.58), −0.26 on
  ProgramBench (Opus −0.48), −0.18 on tau2 (Opus −0.30).
- Jev is repeatable (97 per cent identical labels on repeat) and its confidence tracks agreement (ρ 0.47).

**Status.** Complete (2026-10-04). 1,513 requests, 17.4M input tokens, about $0.73. 7 long ProgramBench tasks skipped
for length. Sealed predictions: 12 of the 14 not set at 0.5 on the right side.

## Design

See `PREREGISTRATION.md` (pushed before the run, `95810a0`; amendment 1 pushed as the run finished and before any
result was looked at, `f5f61fc`). Jev `jev-1.13.0`; one request per task with five Score questions built from the
rubric texts; the Opus labels already released or collected as reference.

## Results

| rubric | n | exact | within one | κ | mean Jev − Opus | mean probability on Opus's level |
|---|---|---|---|---|---|---|
| MSc | 1,404 | 0.91 | 0.99 | 0.96 | −0.03 | 0.81 |
| MSm | 1,404 | 0.79 | 0.83 | 0.80 | −0.35 | 0.73 |
| PLe | 1,403 | 0.58 | 0.88 | 0.49 | −0.15 | 0.42 |
| PLp | 1,402 | 0.37 | 0.85 | 0.47 | −0.09 | 0.32 |
| PLs | 1,404 | 0.12 | 0.68 | 0.44 | −0.73 | 0.16 |

Per group (agentic / social) κ: PLp 0.53 / 0.16, PLe 0.42 / 0.80, PLs 0.24 / 0.50, MSm 0.16 / 0.93, MSc 0.94 / 0.95.

**MS separation.** Mean MSc on the single-agent sets: Jev 0.52, Opus 0.54. Jev: EQ-Bench 4 3.32, CooperBench coop
2.0, solo 0.0, Game Arena 0.92.

**Calibration.** Good where Jev gives a level little probability; overconfident in the middle: at 0.6 to 0.8, Opus
picks the level 42 to 54 per cent of the time.

**Criterion validity** (Spearman with each set's outcome; Jev's most probable level / its expected level / Opus):

| set | PLp | PLe | PLs |
|---|---|---|---|
| SWE-bench Verified | −0.40 / −0.46 / −0.58 | −0.24 / −0.31 / −0.30 | −0.04 / −0.05 / −0.09 |
| ProgramBench | −0.27 / −0.26 / −0.48 | one level / −0.23 / −0.12 | one level / −0.13 / +0.01 |
| tau2 (within domain) | −0.13 / −0.18 / −0.30 | −0.01 / −0.10 / −0.07 | −0.09 / −0.16 / −0.20 |
| DeepSWE | +0.02 / +0.02 / −0.22 | +0.02 / −0.17 / 0.00 | +0.10 / −0.13 / −0.22 |

**Diagnosis** (`results/diagnosis.md`, 40 disagreements, Opus's reasons read): one failure explains most of each
rubric's disagreements. Jev's top level was 0 or 5 in 30 of 40 cases. It reads level 0 off surface features (PLp: an
issue that names the bug read as "steps given"; PLe: a small fix read as one action; MSm: tool and coding tasks read as
non-social), and reads an unpredictable human as Level 5 on PLs. Opus applied the rubric correctly in most cases.

**Exploratory (not pre-registered).** Jev's expected level ranks tasks fairly well against Opus (PLp agentic Spearman
0.75), so the problem is partly the level scale. A logistic mapping from Jev's probabilities to Opus's level, fitted
leaving one benchmark out, raises exact agreement but not κ, and loses the PLp signal (SWE-bench −0.05). Not a fix.

## Predictions (sealed)

| prediction | p | outcome |
|---|---|---|
| PLp within one ≥ 85% | 0.5 | yes (85.4%) |
| PLs within one ≥ 85% | 0.45 | no (67.5%) |
| MSc within one ≥ 85% | 0.7 | yes (99%) |
| κ ≥ 0.6 on PLp | 0.35 | no (0.47) |
| κ higher on MSm and MSc than on all PL rubrics | 0.6 | yes |
| Jev's PLs above Opus on the coding sets | 0.65 | **no** (one level below) |
| MS separation holds | 0.7 | yes |
| Jev PLp on SWE-bench significant and negative | 0.6 | yes (−0.40) |
| Jev PLp ρ ≤ −0.45 on SWE-bench | 0.3 | no (−0.40) |
| Jev PLp tau2 significant and negative | 0.45 | **yes** (p = 0.049) |
| confidence goes with agreement | 0.65 | yes |
| ≥ 95% repeat labels identical | 0.7 | yes (97%) |
| < 20 tasks skipped | 0.8 | yes (7) |
| expected level ≥ most probable level on SWE-bench PLp | 0.6 | yes |
| mean probability on Opus's level ≥ 0.4 for PLp | 0.5 | no (0.32) |
| one clause explains ≥ half of PLs disagreements | 0.55 | yes (6 of 8) |

## What this means

- Jev could label MSc now, and MSm on social tasks, at about a thousandth of the cost.
- For the planning rubrics it is not a substitute. Its expected level is a usable but weaker signal. The diagnosis
  suggests asking the deciding clauses as separate yes/no questions (`results/diagnosis.md`); that is the next test.
