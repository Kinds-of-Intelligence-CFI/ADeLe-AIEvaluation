# rivercross-v2 — results

**Question.** On river-crossing puzzles, where an exact solver knows the true remaining work, do the
current planning rubrics behave as they should?

**Answer.** PLp does not follow search. In the main runs it tracks the solver's cost-to-go at
Spearman ρ = 0.85. The length-versus-search contrast (amendment 1) shows that this is mostly
distance to the goal:
- two extra decision points at the same length moved the label on only 2 of 9 pairs;
- more crossings left, at the same decision points, raised it on 13 of 21 pairs, and lowered it on
  none.

The effect is a step, not a slope. States 2 crossings from the goal get PLp 0–1, states 4 away get
2, and states 5 or more away get 3. The PLp rubric says length should not raise the demand. PLs stays
low, as its rubric says. PLe splits into 0 for a single crossing and 3 for a written multi-step
answer, which follows its rubric. On agent play with a referee, PLe is 1.

**Status.** Complete (2026-09-30). The main runs have 178 cells, all labelled by Opus 5.5 at effort
low; five of the six sealed tests held, and T3 failed. Amendment 1 judged 59 more states three times
each: L1 (length effect) held and S1 (search effect) failed.

## Design

See `PREREGISTRATION.md`, pushed before any label (`decdc58`).

- **Frames.** Read from `experiments/rivercross/` without change:
  - `rc-state`: 43 puzzle states partway through, with the state shown. Judged for PLp, PLe and PLs.
  - `rc-play`: 49 states of captured agent play, with the referee's replies. Judged for PLe.
- **Ground truth.** The solver's cost-to-go is the number of crossings left on the shortest
  solution. The judge never sees it.
- **Judging.** Opus low, v2 prompt, current rubrics, one state per call.

## Pre-registered results

From `results/rivercross.json` (`analysis/analyse.py`).

| test | result | prediction (p) | holds |
|---|---|---|---|
| T1. PLp against cost-to-go | ρ = 0.85 [0.73, 0.92], p < 10⁻¹² | at least 0.6 (0.6) | yes |
| T2. cost-to-go-1 states at PLp 0 or 1 | 12 of 12 (all at 0) | at least 80% (0.75) | yes |
| T3. `rc-state` PLe at its most common level | 58% (25 of 43 at 3) | at least 80% (0.55) | no |
| T4a. `rc-state` PLs at 2 or below | 43 of 43 | at least 80% (0.7) | yes |
| T4b. PLs against cost-to-go, below PLp's | ρ = 0.56, below 0.85 | below (0.75) | yes |
| T5. `rc-play` PLe at its most common level | 96% (47 of 49 at 1) | at least 80% (0.65) | yes |

**Labels by cost-to-go (`rc-state`, number of states).**

| cost-to-go | states | PLp 0 / 1 / 2 / 3 | PLe 0 / 1 / 2 / 3 | PLs 1 / 2 |
|---|---|---|---|---|
| 1 | 12 | 12 / 0 / 0 / 0 | 12 / 0 / 0 / 0 | 7 / 5 |
| 2 | 22 | 4 / 14 / 4 / 0 | 0 / 4 / 1 / 17 | 1 / 21 |
| 3–4 | 6 | 0 / 1 / 4 / 1 | 0 / 0 / 1 / 5 | 0 / 6 |
| 5–7 | 3 | 0 / 0 / 0 / 3 | 0 / 0 / 0 / 3 | 0 / 3 |

Mean PLp by cost-to-go: 0.0 (1), 1.0 (2), 2.0 (3 and 4), 3.0 (5 and 7).

## Exploratory results

- **PLp follows the rubric's own anchors.**
  - Every state one crossing from the goal is at 0. That matches Level 0's "a task scored partway
    through whose remaining work is a single forced action".
  - The deepest states reach Level 3, where decisions interact and options must be compared by
    looking ahead.
  - No state reaches 4. That is right for small puzzles with a known kind of solution.
- **Why PLe is not flat (T3).** The `rc-state` frames ask for a written sequence of crossings, with
  no environment to confirm each one.
  - A single crossing is one atomic action, so it is Level 0.
  - Any longer answer is judged Level 3: checks are easy, and the solver elects to make them, by
    writing out the banks after each crossing.
  - So PLe's correlation with cost-to-go (ρ = 0.78) comes from one crossing against several, not
    from length. Among the 31 states with two or more crossings left, 25 are at 3.
  - My prediction assumed a flat PLe and missed the single-action case. The labels follow the
    rubric.
- **PLe on agent play is 1, as the rubric says.** The referee accepts or rejects every move, so the
  environment checks each action (Level 1). The older rivercross labels, made with an earlier PLe
  text, were mostly 2. Only 4% match, with a mean shift of −0.65.
- **PLs.**
  - PLs is 1 or 2 everywhere. It is 1 mainly where a single crossing remains, since Level 1 is "a
    model of a single step".
  - It does not rise with the number of forbidden pairs (ρ = 0.16) or items (0.24).
  - It falls with boat size (−0.49). A bigger boat means shorter solutions, so this is likely the
    same single-crossing effect.
  - So PLs does not pick up search size beyond the one-step case.
- **Against the older PLp labels.** 74% match the older Opus labels for the same states, with a
  mean shift of −0.07. Those came from an earlier rubric and many states per call. So the link to
  remaining search that the rivercross arm found (Spearman 0.83–0.89) survives both the rubric
  re-key and the move to one state per call with the v2 prompt.
- **Cost.** 178 calls, 12:10–12:18 UTC. The 5-hour meter went from 11% to 21% and the weekly meter
  from 15% to 16%, including my own turns.

## Amendment 1: length or search?

Pre-registered after the main results and before any of its labels (`743feec`). The states come from
50 solvable puzzles (`make_contrast.py`), in pairs from the same puzzle:
- **9 search pairs:** same cost-to-go, 2 or more extra decision points.
- **21 length pairs:** same decision points, 2 or more extra crossings left.

Each state was judged three times, and the label is the median. From `results/contrast.json`
(`analysis/contrast.py`):

| test | result | prediction (p) | holds |
|---|---|---|---|
| S1. search effect | mean +0.22; 2 pairs higher, 0 lower, 7 tied; sign test p = 0.25 | mean ≥ 0.5 and p < 0.05 (0.3) | no |
| L1. length effect | mean +1.29; 13 pairs higher, 0 lower, 8 tied; sign test p = 0.0001 | the same (0.7) | yes |

**Reading, as fixed in advance: PLp follows length, which the rubric says it should not.**

Exploratory:
- **The length effect is a step near the goal.** In the 15 length pairs whose shorter state is 2
  crossings from the goal, the mean difference is +1.73. In the 6 pairs whose shorter state is 3 or
  more away, it is +0.17.
- **PLp by crossings left**, number of states at each level:

  | crossings left | PLp 0 | PLp 1 | PLp 2 | PLp 3 |
  |---|---|---|---|---|
  | 2 | 7 | 5 | 3 | 0 |
  | 4 | 0 | 0 | 19 | 2 |
  | 6 or more | 0 | 0 | 2 | 14 |

- **The judges solve the state and grade how trivial the solution looks.** A typical answer at 2
  crossings: "The solution is two crossings ... the decisions are trivial ... Level 1". They do not
  weigh how many wrong moves are open along the way.
- **Seven two-crossing states got PLp 0.** Level 0 requires "a single forced action". Two crossings
  with a wrong option open are neither, so these look like misreadings of the rubric.
- Over all 59 states, PLp correlates with crossings left at 0.81 and with decision points at 0.50.
  The two measures correlate with each other at 0.45.
- All three repeats agreed on 66% of states.

Caveats:
- **Decision points are my proxy for search.** They count legal moves that are not optimal. Some of
  those only waste a crossing rather than lead to a dead end, so the proxy may overstate how much
  real search a state needs.
- **The search pairs sit mostly at 4 crossings,** where PLp is 2 on 19 of 21 states. Level 3 was
  within reach, so no ceiling blocked a search effect there.
- **The rubric's levels are kinds of planning, not amounts.** Arguably, more decision points need
  not change the level as long as the kind of planning is the same. But the rubric puts the 2/3
  boundary at whether decisions interact, which is what decision points approximate. So the result
  still counts against it.

## Deviations and caveats

- **Amendment 1, transcript gap.** For one of the 177 contrast answers
  (`missionaries-cannibals-4-boat-3--R-C2.C3.M1.M3`, repeat 1), the judge transcript lacks the
  assistant record that holds the Write call. The harness's "File created successfully" reply for
  that file is present, and every record in that transcript is from `claude-opus-5-5`. `writers.py`
  now accepts that confirmation when no Write call matches, and marks such cells
  `evidence = harness_confirmation` in `writers.csv`. It is the only such cell.

- No other deviations from the pre-registration.
- **One judge.** The older rivercross work compared three judges.
- **Narrow, small ground truth.** There are 43 states, and 34 of them are 1 or 2 crossings from the
  goal. Only 3 states have five or more.
- **Different framing.** These are demand-to-go frames. The benchmark studies label whole tasks.
- **Tiny puzzles.** The result shows that PLp orders small search problems correctly. It does not
  show where Levels 4 and 5 sit.

## Reproduce

```
python experiments/benchmarks/rivercross-v2/analysis/analyse.py
```

The numbers above are those committed with this file. The judges' answers stay out of the repo.
