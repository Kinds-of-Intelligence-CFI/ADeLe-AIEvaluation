# tbsci-pl — results

**Question.** Do the PL rubrics track difficulty on Terminal-Bench Science 0.1, a benchmark the labs report and that has
current-generation per-trial outcomes?

**Answer.** Not against solve rate. PLp rises with the expert-hour estimate (ρ = +0.41, p < 0.001), but it does not fall
with solve rate: it rises slightly (ρ = +0.24, p = 0.045), the wrong sign. Expert hours also rise with solve rate here
(ρ = +0.21, p = 0.09), so on this benchmark longer tasks are not the ones agents fail. PLe and PLs track neither, except
PLs with expert hours (+0.25). As on Terminal-Bench 4.0, most tasks sit at PLp 3.

**Status.** Complete (2026-10-01). 207 of 210 cells labelled by Opus 5.5 at effort low. `protein-active-learning` has no
label: a safety classifier handed every attempt to another model. Two of four sealed predictions held.

## Design

See `PREREGISTRATION.md`, pushed before any label (`a2340ec`). All 70 tasks of TB-Science 0.1 (tag `v0.1.0`), with two
flags: `solved_any` (65) and `open_issue` (37, a generous mapping of open `[TASK FIX]` issues, not yet reviewed by
Pablo). Outcomes: 12 public Harbor Hub configurations × 3 trials. Labels: run `tbsci-pl` of `adele mass`
(`mass-annotation/runs/tbsci-pl/`), Opus 5.5 low, v2 prompt, PLp text O.

## Pre-registered results

From `results/analysis.json` (`analysis/analyse.py`). Spearman, Fisher-z 95% intervals.

| | all (69) | solved by some trial (64) | solved, no open issue (32) |
|---|---|---|---|
| PLp against solve rate | +0.24 [+0.00, +0.46], p 0.045 | +0.16 [−0.09, +0.39] | +0.36 [+0.00, +0.64], p 0.042 |
| PLp against expert hours | +0.41 [+0.18, +0.59], p < 0.001 | +0.41 [+0.17, +0.60] | +0.48 [+0.13, +0.72] |
| PLe against solve rate | +0.00 | −0.01 | +0.01 |
| PLe against expert hours | +0.02 | −0.03 | −0.25 |
| PLs against solve rate | +0.09 | +0.10 | +0.27 |
| PLs against expert hours | +0.25 [+0.01, +0.47], p 0.036 | +0.24 | +0.36, p 0.045 |

**Levels (69).** PLp 2/3/4 = 8/52/9. PLe 2/3/4 = 1/24/44. PLs 0/1/2/3 = 29/10/25/5.

**Sealed predictions.**

| prediction | p | outcome |
|---|---|---|
| PLp against solve rate negative, p < 0.05, on all 70 | 0.25 | failed: positive (+0.24, p 0.045) |
| PLp against expert hours positive, p < 0.05 | 0.35 | held (+0.41) |
| most tasks at PLp 3 | 0.7 | held (52 of 69) |
| no rubric significant on the solved, issue-free subset | 0.75 | failed: PLp with both outcomes, PLs with hours |

## Reading

PLp reads the size of the job, as the expert-hour estimate does, but size is not what makes TB-Science tasks hard for
current agents. Solve rate here likely turns on domain knowledge and on verifier strictness (37 tasks have open fix
issues), neither of which the PL rubrics measure. The wrong-sign PLp result is weak (the interval touches zero) and
comes from 17 tasks off Level 3. This matches Terminal-Bench 4.0 and contrasts with SWE-bench and tau2, where PLp falls
with solve rate.

## Deviations and caveats

- `protein-active-learning` is unlabelled on all three rubrics. PLe and PLs used both attempts (Opus 5 wrote them).
  PLp's retry was left unrun at Pablo's OK: the first PLp answer came from another model and was also written twice,
  which `adele mass check` flags.
- The `open_issue` flag is a generous mapping, not yet reviewed. No external review of TB-Science exists.
- 12 configurations × 3 trials gives coarse solve rates (36 trials per task).
