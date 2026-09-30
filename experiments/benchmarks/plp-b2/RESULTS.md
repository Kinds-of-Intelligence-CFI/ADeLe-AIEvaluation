# plp-b2 — results

**Question.** Does candidate B2 make the PLp judges follow search rather than solution length? B2
says only choices that could go wrong add to planning demand, and adds one contrasting pair of
examples.

**Answer.** No. On the same 54 river-crossing states, B2's labels still follow length (+0.37,
p = 0.0002) and not search (+0.13, p = 0.22). That is essentially what the current text gave (+0.33 and
+0.10). The judges read and use the new examples: 154 of 162 answers cite them. But they use them as a
type label. Any river-crossing state with an interacting constraint is matched to the Level 3
sliding-block example, whatever the amount of search.

**Status.** B2: complete (2026-09-30). All three pre-registered tests failed. Candidate S, the structural
change (amendment 1), passed the exit criterion narrowly on the same 54 states: search bits +0.23
(p = 0.002) against length +0.21 (p = 0.004). It still fails E3. On the SWE-bench gate tasks (amendment 2), S's labels track solve rate more
strongly than the current text's: ρ = −0.73 against −0.55 on 37 tasks. All three sanity checks hold. Next
comes the lab regression, in a fresh session. Nothing changes in `src/` yet.

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

## Amendment 1: candidate S, the structural change

Pre-registered before any of its labels (`f22cf47`). S is B2 plus a placement rule: the level is the higher
of the kind of planning and the size of the search. It adds a small, moderate or large search at Levels 2,
3 and 4, a Level 4 example of a large pure search, and a Level 5 note that search size alone does not
reach 5. From `results/s_search.json` (`analysis/analyse.py --run s-search --out s_search.json`). All 162
answers were written by `claude-opus-5-5` and parsed; the protocol check was clean.

| test | S | B2 | current text | holds (S) |
|---|---|---|---|---|
| E1 (exit). bits > 0, p < 0.05, and above ctg | bits +0.23 (p = 0.002), ctg +0.21 (p = 0.004) | +0.13 / +0.37 | +0.10 / +0.33 | **yes** |
| E2. ctg coefficient below 0.328 | 0.213 | 0.366 | — | yes |
| E3. Spearman with Opus 5.5's non-optimal share ≥ 0.3 | 0.05 | 0.19 | −0.02 | no |

Pre-registered probabilities: E1 0.45, E2 0.55, E3 0.35.

**Reading, as fixed in advance: E1 holds, so the SWE-bench gate sanity check and the lab regression come
next.** The pass is narrow. The search coefficient only just exceeds the length coefficient, and both
remain significant.

**Mean PLp by cell under S** (current text in brackets):

| crossings left | bits low | bits mid | bits high |
|---|---|---|---|
| 2–3 | 1.50 (1.50) | 2.00 (2.33) | 2.33 (2.33) |
| 4–6 | 2.00 (2.33) | 2.33 (2.50) | 2.17 (2.67) |
| 7+ | 2.17 (3.00) | 2.50 (2.67) | 2.83 (2.83) |

Exploratory:
- **Where the gain comes from.** S mostly brings long, easy states down: 7+ crossings with low bits
  fall from 3.00 to 2.17. It does not lift short, trappy states: 2–3 crossings with high bits stay at
  2.33. So the length effect shrinks, but S does not yet see the states strong solvers find hardest
  (E3 fails).
- **Labels compress to 2.** S gives 38 states at 2, 14 at 3, 1 at 1 and 1 at 0. The current text gives
  20, 30, 3 and 1. The mean shift is −0.26, and S matches the current text on 63% of states. No state
  reaches 4.
- **Repeats agree much more.** All three repeats agreed on 83% of states under S, against 59% under
  the current text. The rule seems to make judgements more consistent.
- **The judges use the rule sparingly.** 33 of 162 answers cite the size of the search. A typical
  answer places a small puzzle at 3 because "the plan still has to be found by a small search that
  looks a few steps ahead". It keeps it below 4 because "the state space is tiny, only a few choices
  could go wrong".

Caveats:
- The pass is narrow on 54 states, with one judge.
- Compressing labels to 2 could reduce the benchmark correlations. The SWE-bench sanity check exists
  to test that.

## Amendment 2: SWE-bench sanity check for S

Pre-registered before any of its labels (`e60bfc8`). The run covers PLp on the 44 SWE-bench Verified
gate tasks, one Opus-low call each, with the v2 prompt. The baseline is the current text with the same
builder and judge (`natural-prompt`, `npb-gate-opuslow`); prompts were hash-checked. All 44 answers
were written by `claude-opus-5-5` and parsed; the protocol check was clean. From
`results/s_swe_gate.json` (`analysis/swe_gate.py`).

| test | result | prediction (p) | holds |
|---|---|---|---|
| G1. S vs solve rate < 0, p < 0.05 (37 solvable tasks) | ρ = −0.73, p = 2 × 10⁻⁷ | 0.75 | yes |
| G2. at most 0.15 weaker than the current text (−0.55) | 0.18 stronger | 0.6 | yes |
| G3. most common level at most 85% | 68% (30 of 44 at 2) | 0.75 | yes |

**Reading, as fixed in advance: all three hold, so the lab regression comes next,** in a fresh session
and pre-registered first.

Exploratory:
- **Levels.** S gives 13 tasks at 1, 30 at 2 and 1 at 3. The current text gives 18 at 1 and 26 at 2. S
  matches the current text on 77% of tasks, with a mean shift of +0.14. So on SWE-bench, S moves a few
  bug fixes from 1 to 2 and sharpens the ordering. Unlike on the puzzles, it does not compress labels
  to 2.
- **The gain may partly be noise.** It rests on one call per task and 37 tasks. The 95% intervals of
  the two correlations overlap widely. The safe conclusion is that S does not weaken the benchmark
  link, and it may strengthen it.

## Deviations and caveats

- No deviations.
- The test uses one judge and one testbed, with small puzzles. On real tasks, kinds of planning may
  vary more than on these puzzles.

## Reproduce

```
python experiments/benchmarks/plp-b2/analysis/analyse.py
```
