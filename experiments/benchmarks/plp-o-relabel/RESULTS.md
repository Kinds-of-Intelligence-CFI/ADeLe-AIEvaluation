# plp-o-relabel — results

**Question.** With the adopted PLp text O, does PLp keep its links to difficulty on real tasks?

**Answer.** Yes, and almost unchanged. O and the previous text give the same benchmark results within noise.
SWE-bench Verified: ρ = −0.573 with solve rate (previous −0.576). tau2 within domain: −0.35 (previous −0.38).
Terminal-Bench: still no significant link (+0.15, previous +0.25). O agrees exactly with the previous labels on 79%
of SWE tasks, 91% of tau2 and 89% of Terminal-Bench, and always within one level.

**Status.** Complete (2026-10-01). 695 of 696 new cells labelled by Opus 5.5 at effort low, plus the 44 SWE gate
labels of `plp-b2`'s `o-swe-gate`. `uefi-bootkit` has no label: a safety classifier stopped Opus 5.5 on both attempts
and Opus 4.8 wrote both answers (set aside, as pre-registered; the same happened in `pl-relabel-v2`).

## Design

See `PREREGISTRATION.md`, pushed before any label (`e2e3c37`). Same judge, prompt and task texts as `pl-relabel-v2`;
every previous prompt was rebuilt and matched its stored hash, so only the PLp text differs. PLe and PLs labels come
from `pl-relabel-v2` (their rubrics did not change). The studies' own analysis functions were rerun.

## Pre-registered results

From `results/relabel_o.json` (`analysis/analyse.py`). Spearman, Fisher-z 95% intervals.

| | O | previous text |
|---|---|---|
| SWE, PLp vs solve rate (435 solvable) | −0.573 [−0.64, −0.50] | −0.576 |
| SWE, PLp vs time to fix | +0.454 [+0.37, +0.53] | +0.478 |
| tau2, PLp within domain (232) | −0.346 | −0.378 |
| — airline / banking / retail | −0.54 / −0.31 / −0.29 | −0.57 / −0.41 / −0.28 |
| tau2, pooled over domains (robustness) | −0.378 | −0.303 |
| Terminal-Bench, PLp vs solve rate (33) | +0.15 (p = 0.42) | +0.25 (p = 0.15) |
| Terminal-Bench, PLp vs expert hours | +0.18 (p = 0.31) | +0.21 (p = 0.24) |

**Agreement and levels.**

| | exact | within one | mean shift (O − previous) | PLp levels under O | previous |
|---|---|---|---|---|---|
| SWE (442) | 79% | 100% | +0.10 | 0:16 1:170 2:244 3:5 | 0:19 1:209 2:200 3:7 |
| tau2 (232) | 91% | 100% | +0.04 | 1:24 2:203 3:5 | 1:34 2:192 3:6 |
| Terminal-Bench (65) | 89% | 100% | −0.08 | 2:13 3:49 4:3 | 2:9 3:52 4:4 |

O moves some SWE tasks from 1 to 2 and nothing else of note. It does not spread the scale on real tasks: SWE and tau2
sit at Levels 1–2, Terminal-Bench at 3.

**Sealed predictions.**

| prediction | p | outcome |
|---|---|---|
| SWE PLp negative, p < 0.05 | 0.97 | held |
| SWE more negative than −0.58 | 0.55 | failed (−0.573) |
| SWE within ±0.10 of −0.58 | 0.7 | held |
| SWE time to fix positive, p < 0.05 | 0.95 | held |
| tau2 within domain negative, p < 0.05 | 0.85 | held |
| tau2 more negative than −0.38 | 0.45 | failed (−0.346) |
| Terminal-Bench not significant | 0.75 | held |
| Terminal-Bench negative | 0.4 | failed (+0.15) |
| exact agreement: SWE ≥ 0.75 / tau2 ≥ 0.7 | 0.6 / 0.55 | held / held |
| SWE mean shift within ±0.15 | 0.7 | held (+0.10) |
| more Terminal-Bench tasks at 4+ under O | 0.5 | failed (3 against 4) |

## Reading

O changed what PLp means (one driver, search after knowledge, odds anchors) without changing what it predicts on these
benchmarks. That is reassuring for adoption: nothing was lost. It also says the benchmark links were never about the
length-versus-search question that motivated O. On SWE-bench and tau2, almost every task is Level 1 or 2 under both
texts, and the correlation comes from that 1/2 split. The SWE gate's −0.71 for O (37 tasks) was small-sample noise:
on all 435 tasks it is −0.57. Terminal-Bench, where tasks reach Level 3–4, still shows no link, as before.

The open question is the same as before O: does PLp add predictive power over the other rubrics (desideratum 9)?

## Deviations and caveats

- `uefi-bootkit` unlabelled (both attempts written by Opus 4.8 after classifier stops). One of its calls also tried
  to Read the working folder before its prompt.
- Protocol check over 697 judge transcripts: exact two-line message, working directory `~/Developer/ADELE`, no
  CLAUDE.md, Read then Write, apart from the call above.
