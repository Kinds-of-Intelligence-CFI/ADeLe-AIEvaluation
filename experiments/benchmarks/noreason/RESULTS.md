# noreason — results: which judge, at what cost?

Pre-registration: `PREREGISTRATION.md` (amendments 1–4b). Run log: `RUNLOG.md`. Numbers come from
`analysis/analyse.py`, `analysis/arms.py`, `analysis/cost.py` and `analysis/tables.py` (outputs in `results/`).
State: 2026-10-07, 01:50 UTC.

## Bottom line

**Recommendation: annotate with Opus 5.5 at effort low, answering with the bare digit (NR).**
- It matches the released labels as closely as a rerun of the released judge does, on all 7,057 cells.
- Its criterion validity is as good as the released labels': ρ is never weaker in a signal cell.
- It costs 22% less per label than the reasoning prompt, and each call takes 35% less time.
- Keep the reasoning prompt (R) for rubric pilots and audits, where the written reasons are the point.

**Do not switch to Sonnet 5.5, with or without reasoning.**
- Sonnet halves the cost again, but it shifts levels systematically: PLs and MSm are rated lower.
- It weakens the ProgramBench PLp signal.
- Written reasoning makes Sonnet worse, not better: SR is the least valid arm.

Confidence that NR is the right default for the next mass annotation: about 85%. The main residual risk is that the
6-point PLp gap on the reference subset is real rather than noise, though the full-set agreement suggests it is noise.

## The arms

All arms judge the same pinned prompts at effort low. Only the judge model and the answer format change.

| arm | judge | answer | cells | labelled |
|---|---|---|---|---|
| released | Opus 5.5 | reasoning, then digit | 7,065 | (relabel-v2, with v3 overrides for PLp and MSm) |
| R′ | Opus 5.5 | reasoning, then digit | 530 (reference subset) | 530 |
| NR | Opus 5.5 | bare digit | 7,065 | 7,057 |
| SNR | Sonnet 5.5 | bare digit | 7,065 | 7,057 |
| SR | Sonnet 5.5 | reasoning, then digit | 7,065 | 4,213 so far (all PL and tau2 MS; social sets partial) |

- R′ is a same-day rerun of the released judge. Its agreement with the released labels is the yardstick: the noise
  of rerunning the same judge.
- The reference subset is 150 tasks × 3 PL rubrics and 40 tau2 tasks × 2 MS rubrics. Every arm labelled it.
- The released PLp and MSm labels partly predate the current rubric text. R′ uses the current text, like the other
  arms, so the yardstick absorbs that difference.

## Cost vs precision

Agreement is exact agreement with the released labels on the reference subset (n = 150 per PL rubric, 40 per MS
rubric). ρ is the Spearman correlation of PLp level with task outcome, on all tasks of each signal set.

| arm | $/label, harness | s/call | $/label, API batch | PLp | PLe | PLs | MSm | MSc | ρ SWE (n=443) | ρ ProgramBench (129) | ρ tau2 (242) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| released | — | — | — | target | target | target | target | target | −0.55 | −0.49 | −0.28 |
| R′ (yardstick) | 0.0409 | 11.0 | 0.0101 | 0.89 | 0.93 | 0.93 | 0.78 | 0.97 | — | — | — |
| **NR** | **0.0320** | **7.2** | **0.0087** | 0.83 | 0.94 | 0.93 | 0.75 | 0.97 | −0.56 | −0.55 | −0.34 |
| SNR | 0.0167 | 4.5 | 0.0044 | 0.81 | 0.86 | 0.81 | 0.40 | 0.93 | −0.52 | −0.39 | −0.23 |
| SR | 0.0201 | 6.8 | 0.0057 | 0.75 | 0.83 | 0.81 | 0.38 | 0.93 | −0.42 | −0.27 | −0.26 |

How cost is measured:
- **Harness** = what one Claude Code judge subagent processed, priced at API list rates (Opus 5.5: $4 in, $5 cache
  write, $0.20 cache read, $20 out per million tokens; Sonnet 5.5: $2, $2.50, $0.20, $10). Matched cells only (the
  530 reference cells), so the arms are compared on the same prompts. Output is estimated from characters ÷ 3.6.
- **API batch** = one plain Messages call per cell, prompt in and answer out, at batch prices (50% off), averaged
  over all labelled cells. This is the cost of a future run through the API instead of subscription subagents.
- The harness overhead (agent system prompt, tool calls) dominates the bare-digit arms. Through the plain API, NR
  costs 14% less than reasoning, not 22%. The prompt is the bulk of the cost.

## Agreement on all cells

Exact agreement / mean level shift against the released labels. n ≈ 1,410 per rubric.

| rubric | NR | SNR | SR | SNR vs NR | SR vs SNR |
|---|---|---|---|---|---|
| PLp | 0.88 / −0.04 | 0.84 / +0.07 | 0.79 / −0.06 | 0.79 / +0.11 | 0.82 / −0.13 |
| PLe | 0.92 / −0.02 | 0.84 / +0.04 | 0.87 / +0.04 | 0.83 / +0.06 | 0.91 / −0.05 |
| PLs | 0.90 / −0.00 | 0.75 / −0.21 | 0.78 / −0.16 | 0.76 / −0.21 | 0.82 / +0.00 |
| MSm | 0.92 / −0.04 | 0.80 / −0.18 | 0.61 / −0.39 | 0.84 / −0.14 | 0.71 / −0.02 |
| MSc | 0.98 / −0.00 | 0.97 / −0.00 | 0.89 / −0.04 | 0.97 / +0.00 | 0.92 / −0.07 |

- NR agrees with the released labels at the level of the yardstick on every rubric.
- Sonnet rates PLs and MSm lower in both formats. That is a model effect, not a format effect.
- SR's MS rows cover the tau2 sets and part of the social sets so far.

## Criterion validity

| signal cell | released | NR | SNR | SR | SNR − released, 95% CI | SR − released, 95% CI |
|---|---|---|---|---|---|---|
| SWE-bench Verified PLp (n=443) | −0.55 | −0.56 | −0.52 | −0.42 | [−0.03, +0.08] | [+0.06, +0.19] |
| ProgramBench PLp (n=129) | −0.49 | −0.55 | −0.39 | −0.27 | [−0.04, +0.25] | [+0.04, +0.41] |
| tau2 PLp (n=242) | −0.28 | −0.34 | −0.23 | −0.26 | [−0.05, +0.14] | [−0.08, +0.12] |

A positive difference means a weaker (less negative) correlation. NR's CIs against released are [−0.07, +0.04],
[−0.17, +0.05] and [−0.13, +0.02]: NR is never weaker, and its point estimates are stronger in all three cells.

## Pre-registered verdicts

| arm | rule | verdict | why |
|---|---|---|---|
| NR | reasoning matters / mixed / not needed | **mixed** | PLp gap −6 points on the reference subset (rule: every gap under 5). PLe +1, PLs 0. No signal cell weaker. |
| SNR | usable / mixed / not usable | **mixed** | Gaps −8, −7, −12 points. ProgramBench ρ weaker by 0.10. Coverage 99.9%. Cost −48% vs NR (condition met). |
| SR | usable / mixed / not usable | **not usable** | Gaps −14, −10, −12 points. SWE and ProgramBench ρ weaker by ≥ 0.10. |

**Reading the NR verdict.** "Mixed" comes from one rubric on a 150-task subset: 9 more disagreements out of 150.
- On all 1,410 PLp cells, NR agrees with released at 0.882, against the yardstick's 0.887.
- The subset gap is within the noise of a 150-item proportion (paired SE about 0.03).
- I read it as noise, not a real loss. The verdict stays "mixed" because that is what the rule says.

**The 2×2 of model × reasoning** (reference subset, PLp exact agreement with released):

| | reasoning | bare digit |
|---|---|---|
| Opus 5.5 | 0.89 (R′) | 0.83 (NR) |
| Sonnet 5.5 | 0.75 (SR) | 0.81 (SNR) |

The model effect (0.14 + 0.02 = 0.16) is larger than the reasoning effect (0.06 + 0.06 = 0.12). Reasoning helps Opus slightly and
hurts Sonnet.

## Sealed predictions, scored

| prediction | p | outcome |
|---|---|---|
| NR verdict: matters / mixed / not needed | 0.40 / 0.35 / 0.25 | mixed |
| Yardstick PLp exact ≥ 80% | 0.6 | yes (0.89) |
| NR PLp exact ≥ 75% | 0.45 | yes (0.83) |
| NR PLe within 5 points of yardstick | 0.55 | yes (+1) |
| NR PLs within 5 points of yardstick | 0.55 | yes (0) |
| SWE PLp ρ(NR) weaker than −0.45 | 0.45 | no (−0.56) |
| ProgramBench PLp ρ(NR) weaker than −0.40 | 0.45 | no (−0.55) |
| NR tracks prompt length more than released in ≥ 5 of 9 sets | 0.6 | yes for PLp (7 of 9); no for PLe (3) and PLs (4) |
| NR PLp mean shift ≥ +0.15 | 0.4 | no (−0.04) |
| NR answers are bare ≥ 95% | 0.8 | yes (100%) |
| SNR verdict: usable / mixed / not usable | 0.25 / 0.40 / 0.35 | mixed |
| SNR PLp exact ≥ 0.80 | 0.35 | yes (0.81) |
| \|SNR PLp shift\| ≥ 0.15 | 0.5 | no (+0.05) |
| SNR SWE ρ within 0.05 of released | 0.45 | yes (−0.52 vs −0.55) |
| SNR coverage ≥ 95% | 0.75 | yes (99.9%) |
| SNR cost ≥ 30% below NR | 0.5 | yes (−48%) |
| Model effect > reasoning effect (PLp) | 0.7 | yes |
| SR verdict: usable / mixed / not usable | 0.35 / 0.40 / 0.25 | not usable |
| SR PLs gap smaller than SNR's | 0.6 | no (both −12) |
| \|SR MSm shift\| < \|SNR MSm shift\| (tau2 subset) | 0.65 | yes (0.43 vs 0.55) |
| SR coverage ≥ 95% on PL and tau2 MS | 0.7 | yes (99.9%) |
| SR cost ≥ 30% below R′ | 0.5 | yes (−51%) |
| SR cost above NR | 0.5 | no ($0.020 vs $0.032) |

Calibration note: I was too pessimistic about NR. I expected written reasoning to matter (0.40) and the bare-digit
judge to drift upward. Neither happened.

## Coverage and safeguards

- NR: 8 cells without a label (classifier swaps to Opus 4.8 that stayed swapped on retry, and 2 Game Arena cells the
  API always refuses).
- SNR: 8 cells without a label (3 PL and 3 Game Arena safeguard stops; 2 tau2 MS cells after a fallback writer).
- SR: 3 PL cells without a label (fallback writer twice), 1 Game Arena safeguard stop.
- Sonnet 5.5 has no fallback model, so a safeguard stop means no label. On these sets that cost 0.1%.

## Caveats

- The harness cost is a model of what subagents cost, not a bill. The plan meters moved about 3% of the 5-hour
  window per 400 Sonnet cells with reasoning, which is consistent with Sonnet being cheap.
- SR on the social sets (EQ-Bench 4, CooperBench, the rest of tau2 MS) is still running and does not enter any
  verdict. This file will be updated when it finishes.
- Agreement is measured against labels from the same model family (Opus). A Sonnet judge could be "different but
  equally valid". Criterion validity is the check on that, and there Sonnet is weaker on ProgramBench and SR is
  weaker on SWE and ProgramBench.
- Opus at effort high was withdrawn (amendment 4a), so this study says nothing about higher effort.

## Reproduce

```
cd experiments/benchmarks/noreason/analysis
python analyse.py
python arms.py
python cost.py --transcripts <session>/subagents
python tables.py
```
