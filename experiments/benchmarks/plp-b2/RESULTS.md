# plp-b2 — results

**Question.** Does candidate B2 make the PLp judges follow search rather than solution length? B2
says only choices that could go wrong add to planning demand, and adds one contrasting pair of
examples.

**Answer.** No. On the same 54 river-crossing states, B2's labels still follow length (+0.37,
p = 0.0002) and not search (+0.13, p = 0.22). That is essentially what the current text gave (+0.33 and
+0.10). The judges read and use the new examples: 154 of 162 answers cite them. But they use them as a
type label. Any river-crossing state with an interacting constraint is matched to the Level 3
sliding-block example, whatever the amount of search.

**Status.** Complete (2026-09-30). All three pre-registered tests failed. Following the pre-registration,
the lab regression was not run, and nothing changes in `src/`.

## Design

See `PREREGISTRATION.md`, pushed before any label (`d207da2`). The 54 states, prompt builder and judge
are those of `rivercross-v2` amendment 2 (run `rc-search`). Only the rubric text differs. Opus low
judged each state three times, and the label is the median. All 162 answers were written by
`claude-opus-5-5` and parsed; the protocol check was clean.

## Pre-registered results

From `results/b2_search.json` (`analysis/analyse.py`).

| test | B2 | current text | holds |
|---|---|---|---|
| E1 (exit). PLp ~ bits + ctg: bits > 0, p < 0.05, and above ctg | bits +0.13 (p = 0.22), ctg +0.37 (p = 0.0002) | bits +0.10, ctg +0.33 | no |
| E2. ctg coefficient below the current text's | 0.366 | 0.328 | no |
| E3. Spearman with Opus 5.5's non-optimal share ≥ 0.3 | 0.19 | −0.02 | no |

Pre-registered probabilities: E1 0.35, E2 0.6, E3 0.3.

**Reading, as fixed in advance: both E1 and E2 fail, so the wording does not change behaviour.** The
choice is now between a structural change to the levels and accepting that PLp, as judged, is a
length-weighted difficulty measure.

## Exploratory results

- **Why it failed.** 154 of 162 answers cite the new examples, and 17 quote the new sentence. A typical
  answer, for a state 8 crossings from the goal with high search bits, says no ready-made routine "like
  the Hanoi recursion" fixes the moves, so it matches the sliding-block example at Level 3. The judges
  sort puzzles by kind: routine (Hanoi) against constrained search (sliding block). Within the kind
  "search", nothing in the levels grades how much search there is. So nearly every state lands at 3,
  and the few below 3 are the shortest.
- **Levels.** B2 gives 35 states at 3, 14 at 2, 3 at 1 and 2 at 0. The current text gives 30, 20, 3
  and 1. So B2 lifts labels slightly (mean +0.06) and matches the current text on 80% of states.
- **The short, trappy cell** (2–3 crossings, high bits) rises from 2.33 to 2.50, and the short, easy
  cell falls from 1.50 to 1.17. This is the intended direction, but small. The correlation with Opus
  5.5's non-optimal share rises from −0.02 to 0.19.
- All three repeats agreed on 67% of states under B2, and on 59% under the current text.

## What this implies

PLp's levels are kinds of planning: given, retrieved, assembled, searched, constructed and invented.
They are not amounts. Every river-crossing state is the same kind, "searched", so the rubric has no
place to put more or less search. The judges fall back on how long the solution looks. A sentence or
an example cannot fix this, because the scale itself lacks the axis. The options:
1. **Structural:** grade Levels 2–4 partly by how much search is needed, meaning how many choices can
   go wrong and how far ahead they must be looked at, not only by the kind of planning.
2. **Accept:** keep PLp as a kind-of-planning scale that predicts difficulty well on benchmarks, and
   state openly that it does not measure the amount of search within a kind. Leave amount-of-search
   to a separate measure.

This is a methodology decision for Pablo and the team.

## Deviations and caveats

- No deviations.
- The test uses one judge and one testbed, with small puzzles. On real tasks, kinds of planning may
  vary more than on these puzzles.

## Reproduce

```
python experiments/benchmarks/plp-b2/analysis/analyse.py
```
