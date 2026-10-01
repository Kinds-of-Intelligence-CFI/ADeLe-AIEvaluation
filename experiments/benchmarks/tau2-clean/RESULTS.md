# tau2-clean — results

**Question.** Do the PL results on tau2 hold on a clean task set, with banking solve rates from one grading version?

**Answer.** Yes for PLp: on the 242 clean tasks, PLp falls with solve rate within domain at ρ = −0.30 (p < 0.001),
close to the earlier −0.35. Banking alone weakens with the consistent grading (−0.17, not significant, against −0.29
with mixed grading). PLs also falls with solve rate (−0.19); PLe does not (−0.07).

**Status.** Complete (2026-10-01). 30 new cells (10 banking tasks × PLp, PLe, PLs), all labelled by Opus 5.5 at effort
low, protocol clean. Three of five sealed predictions held.

## Design

See `PREREGISTRATION.md`, pushed before any label (`a2340ec`). tau2 airline, retail and banking_knowledge tasks with
results on the frozen text, minus never-solved tasks; telecom excluded (5 shared texts). Banking uses only the 10
configurations run after tau2 v1.0.1 (2026-07-15), which changed its grading. 242 tasks: airline 49, retail 114,
banking 79. 232 reuse labels from `plp-o-relabel` and `pl-relabel-v2` (prompts hash-checked); 10 were labelled here by
run `tau2-clean-new-pl` of `adele mass`.

## Pre-registered results

From `results/clean.json` (`analysis/analyse.py`). Within-domain Spearman against solve rate on common configurations,
combined across domains; Fisher-z 95% intervals.

| | combined | airline (49) | retail (114) | banking (79) |
|---|---|---|---|---|
| PLp | −0.30 [−0.41, −0.18], p < 0.001 | −0.54 | −0.29 | −0.17 (ns) |
| PLe | −0.07 (ns; airline and banking only) | −0.21 (ns) | one level | +0.01 (ns) |
| PLs | −0.19 [−0.32, −0.07], p 0.003 | −0.36 | −0.24 | −0.03 (ns) |

**Banking grading.** Post-change and mixed solve rates agree in rank (ρ = 0.92), but mixed rates are lower by 0.15 on
average. PLp against banking solve rate: −0.17 [−0.38, +0.05] post-change, −0.29 [−0.48, −0.07] mixed.

**Levels.** PLp mostly 2 (airline 1/2 = 13/36; retail 1/2 = 7/107; banking 1/2/3 = 4/69/6).

**Sealed predictions.**

| prediction | p | outcome |
|---|---|---|
| PLp within-domain combined negative, p < 0.05 | 0.9 | held (−0.30) |
| within ±0.10 of −0.35 | 0.75 | held |
| banking PLp more negative with post-change than with mixed rates | 0.5 | failed (−0.17 against −0.29) |
| PLe within domain negative, p < 0.05 | 0.5 | failed (−0.07) |
| PLs within domain negative, p < 0.05 | 0.5 | held (−0.19) |

## Reading

The tau2 PLp result survives cleaning. The banking signal shrinks once all runs use the same grading. Part of the old
banking correlation may have come from older, weaker models scored under the stricter grading: the pre-change
configurations are mostly earlier model generations, so grading and model generation cannot be separated here.

## Deviations and caveats

- No deviations.
- Banking post-change rates rest on 10 configurations.
- The 232 reused labels and their outcomes were analysed before; only the 10 new labels and the banking re-grading are
  new.
