# relabel-v2 — results

**Question.** How do the PLp, PLe, PLs, MSm and MSc labels of the seven agentic clean sets and the three social sets
change under the reviewed examples (`d4ec2ec`), and do the rubrics' signals hold?

**Answer.** Few labels change, and about as many as judge noise alone would change. The signals hold, except on
DeepSWE.
- Labels unchanged, pooled over all ten sets: PLp 86%, PLe 92%, PLs 88%, MSm 94%, MSc 97%. Rerunning the same judge on
  the same text kept 80%, 95%, 80%, 85% and 100% in the examples regression. So the new examples move labels no more
  than a second draw does.
- No set moves by more than 0.15 of a level on average on any rubric.
- The strong signals hold: PLp on SWE-bench Verified (ρ −0.58 → −0.55), ProgramBench (−0.48 → −0.51) and tau2 (−0.30
  → −0.29); PLs on tau2 (−0.20 → −0.15, p 0.027).
- DeepSWE loses both of its weak signals: PLs (−0.22 → −0.13, p 0.22) and PLp (−0.22 → −0.12, p 0.25). Both were near
  p 0.04 before, on 90 tasks. They were fragile, and a redraw at noise level removes them.
- MS still separates social from single-agent tasks: mean MSc is 0.0 on every single-agent set, 2.00 on CooperBench
  coop prompts and 3.36 on EQ-Bench 4.

So the relabel does not show the new examples to be better or worse. It shows they are safe: they keep the labels and
the signals within noise.

**Status.** Complete (2026-10-04). 7,065 calls in five runs, all written by Opus 5.5 at effort low; 7,056 labels.
Nine cells have no label: all five rubrics of ProgramBench `zip-password-finder` and TB-Science
`protein-active-learning`, minus one cell, where the safety classifier swapped the judge on every attempt (these two
tasks had no old labels either). Weekly usage 62% → 84%. Sealed predictions: 10 of 11 held; the one that failed
(DeepSWE PLs stays significant) was set at 0.4.

## Design

See `PREREGISTRATION.md`, pushed before any label (deviations 1 and 2: started before the weekly reset at Pablo's
request; relays of 100). Old labels are `old_labels.csv`, frozen before any new label. The run log is `RUNLOG.md`.

## Predictions

| prediction | sealed | result |
|---|---|---|
| pooled unchanged ≥ 80%: PLp | 0.55 | held (86%) |
| pooled unchanged ≥ 80%: PLe | 0.75 | held (92%) |
| pooled unchanged ≥ 80%: PLs | 0.7 | held (88%) |
| pooled unchanged ≥ 80%: MSm | 0.8 | held (94%) |
| pooled unchanged ≥ 80%: MSc | 0.95 | held (97%) |
| no set's mean shift beyond ±0.3 | 0.7 | held (largest −0.15, EQ-Bench 4 PLs) |
| SWE-bench Verified PLp ρ ≤ −0.5 | 0.8 | held (−0.55) |
| ProgramBench PLp significant and negative | 0.85 | held (−0.51, p < 0.001) |
| tau2 PLs significant and negative within domain | 0.55 | held (−0.15, p 0.027) |
| DeepSWE PLs stays significant | 0.4 | failed (−0.13, p 0.22) |
| MS separation (MSc ≤ 1 single-agent; ≥ 2 EQ-Bench 4 and CooperBench coop) | 0.95 | held (0.0; 3.36 and 2.00) |

"Single-agent" is every agentic set except tau2, as in `ms-benchmarks`. CooperBench coop sits exactly at the
threshold (2.00 before and after).

## Results

ρ is Spearman with each set's primary outcome (as `ms-benchmarks`; tau2 combined within domain); "ns" means p ≥ 0.05;
"const." means one level only, so not testable. Old labels are the released ones (PLs from `pls-relabel`).

**PLp**

| set | n | unchanged | mean shift | ρ old | ρ new |
|---|---|---|---|---|---|
| SWE-bench Verified | 443 | 82% | +0.09 | −0.58 (p < 0.001) | −0.55 (p < 0.001) |
| tau2 (within domain) | 242 | 94% | −0.03 | −0.30 (p < 0.001) | −0.29 (p < 0.001) |
| DeepSWE | 90 | 84% | −0.09 | −0.22 (p 0.041) | −0.12 ns |
| ProgramBench | 129 | 91% | −0.02 | −0.48 (p < 0.001) | −0.51 (p < 0.001) |
| FrontierSWE | 19 | 95% | +0.05 | −0.20 ns | −0.03 ns |
| Terminal-Bench 4.0 | 35 | 88% | −0.06 | +0.12 ns | +0.12 ns |
| TB-Science | 69 | 96% | −0.04 | +0.24 (p 0.045) | +0.25 (p 0.040) |

**PLe**

| set | n | unchanged | mean shift | ρ old | ρ new |
|---|---|---|---|---|---|
| SWE-bench Verified | 443 | 96% | +0.01 | −0.30 (p < 0.001) | −0.26 (p < 0.001) |
| tau2 (within domain) | 242 | 87% | +0.04 | −0.07 ns | −0.14 (p 0.031) |
| DeepSWE | 90 | 93% | −0.07 | +0.00 ns | +0.04 ns |
| ProgramBench | 129 | 89% | −0.08 | −0.09 ns | −0.12 ns |
| FrontierSWE | 19 | 95% | −0.05 | +0.29 ns | +0.42 ns |
| Terminal-Bench 4.0 | 35 | 82% | −0.12 | −0.17 ns | −0.01 ns |
| TB-Science | 69 | 96% | −0.01 | +0.00 ns | −0.03 ns |

**PLs**

| set | n | unchanged | mean shift | ρ old | ρ new |
|---|---|---|---|---|---|
| SWE-bench Verified | 443 | 98% | −0.01 | −0.09 ns | −0.05 ns |
| tau2 (within domain) | 242 | 95% | −0.01 | −0.20 (p 0.002) | −0.14 (p 0.027) |
| DeepSWE | 90 | 73% | +0.00 | −0.22 (p 0.033) | −0.13 ns |
| ProgramBench | 129 | 94% | −0.02 | −0.09 ns | −0.15 ns |
| FrontierSWE | 19 | 84% | +0.05 | +0.07 ns | −0.04 ns |
| Terminal-Bench 4.0 | 35 | 89% | −0.06 | −0.01 ns | −0.09 ns |
| TB-Science | 69 | 84% | −0.06 | +0.04 ns | +0.06 ns |

**MSm**

| set | n | unchanged | mean shift | ρ old | ρ new |
|---|---|---|---|---|---|
| SWE-bench Verified | 443 | 100% | +0.00 | const. | const. |
| tau2 (within domain) | 242 | 78% | −0.04 | −0.07 ns | −0.12 ns |
| DeepSWE | 90 | 100% | +0.00 | const. | const. |
| ProgramBench | 129 | 100% | +0.00 | const. | const. |
| FrontierSWE | 19 | 100% | +0.00 | +0.02 ns | +0.02 ns |
| Terminal-Bench 4.0 | 35 | 100% | +0.00 | −0.14 ns | −0.14 ns |
| TB-Science | 70 | 100% | +0.00 | +0.01 ns | +0.01 ns |

**MSc**

| set | n | unchanged | mean shift | ρ old | ρ new |
|---|---|---|---|---|---|
| SWE-bench Verified | 443 | 100% | +0.00 | const. | const. |
| tau2 (within domain) | 242 | 97% | −0.03 | +0.09 ns | +0.10 ns |
| DeepSWE | 90 | 100% | +0.00 | const. | const. |
| ProgramBench | 129 | 100% | +0.00 | const. | const. |
| FrontierSWE | 19 | 100% | +0.00 | const. | const. |
| Terminal-Bench 4.0 | 35 | 97% | −0.03 | −0.10 ns | const. |
| TB-Science | 69 | 100% | +0.00 | const. | const. |

| social set | rubric | n | unchanged | mean shift | mean old | mean new |
|---|---|---|---|---|---|---|
| eqbench4 | PLp | 120 | 68% | -0.13 | 2.27 | 2.14 |
| eqbench4 | PLe | 120 | 99% | +0.01 | 2.99 | 3.00 |
| eqbench4 | PLs | 120 | 77% | -0.15 | 2.95 | 2.80 |
| eqbench4 | MSm | 120 | 98% | +0.00 | 4.01 | 4.01 |
| eqbench4 | MSc | 120 | 97% | -0.02 | 3.38 | 3.36 |
| cooperbench | PLp | 240 | 88% | -0.04 | 2.17 | 2.13 |
| cooperbench | PLe | 240 | 86% | +0.03 | 3.21 | 3.24 |
| cooperbench | PLs | 240 | 70% | -0.03 | 1.52 | 1.50 |
| cooperbench | MSm | 240 | 90% | +0.01 | 1.45 | 1.46 |
| cooperbench | MSc | 240 | 88% | -0.04 | 1.08 | 1.04 |
| gamearena | PLp | 24 | 75% | +0.00 | 1.67 | 1.67 |
| gamearena | PLe | 24 | 100% | +0.00 | 0.12 | 0.12 |
| gamearena | PLs | 24 | 83% | +0.08 | 1.75 | 1.83 |
| gamearena | MSm | 24 | 67% | -0.08 | 1.88 | 1.79 |
| gamearena | MSc | 24 | 92% | +0.08 | 0.83 | 0.92 |

CooperBench by prompt type, mean old → new: coop MSc 2.00 → 2.00, MSm 2.90 → 2.92; solo MSc 0.17 → 0.08, MSm 0.00 →
0.00. tau2 stays at MSc 2.27 → 2.24, MSm 2.05 → 2.00.

## Notes

- **Where labels move.** The largest changes are PLs on CooperBench (70% unchanged), PLp on EQ-Bench 4 (68%, mean
  −0.13), MSm on Game Arena (67%, 24 tasks) and PLs on DeepSWE (73%). None has a consistent direction above 0.15.
- **TB-Science PLp** correlates positively with the outcome (+0.25, p 0.04), as before (+0.24): harder-looking tasks
  are solved more often there. It is unchanged by the relabel and not a target of this study.
- **What this does not test.** Whether the new examples are better needs a criterion the old examples can fail:
  for example placement of held-out items with known levels, or agreement with human raters. This relabel only shows
  that swapping the examples costs nothing measurable.

## Files

- `results/analysis.json`: every number above (`analysis/analyse.py`).
- `../mass-annotation/runs/relabel-v2*/labels.csv`: the new labels.
