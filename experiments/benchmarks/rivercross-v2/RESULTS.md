# rivercross-v2 — results

**Question.** On river-crossing puzzles, where an exact solver knows the true remaining work, do the
current planning rubrics behave as they should?

**Answer.** PLp does not follow search, and search is what makes these puzzles hard for strong
models. In the main runs PLp tracks the solver's cost-to-go at Spearman ρ = 0.85, but three follow-ups
show that this is the length of the remaining solution:
- **Amendments 1 and 2, the labels.** On matched pairs and on a grid balanced between search bits
  (depth × width, with forced steps counting zero) and length, PLp rises with length (+0.33,
  p = 0.0001) and not with search (+0.10, p = 0.26).
- **Amendment 3, strong solvers.** Sonnet 5.5 and Opus 5.5 almost always solve the states: Opus 98.5%,
  Sonnet 91.5%. When they miss the shortest solution, it is on states with more search bits (Opus
  +0.071, p = 0.004; Sonnet +0.087, p = 0.016), not on longer ones. The trappiest short states are the
  hardest: Opus misses the optimum on 37% of attempts at 2–3 crossings with high bits, against 0% at
  2–3 crossings with low bits. PLp, which puts short states low, does not track this (ρ = −0.02 with
  Opus, 0.10 with Sonnet).

Only Haiku's and Sonnet's outright failures rise with length, and those are state-tracking slips. PLs
stays low, as its rubric says. PLe splits into 0 for a single crossing and 3 for a written multi-step
answer, which follows its rubric; on agent play with a referee it is 1.

**Status.** Complete (2026-09-30). The main runs have 178 cells, all labelled by Opus 5.5 at effort
low; five of the six sealed tests held, and T3 failed. Amendment 1 judged 59 more states three times
each: L1 (length effect) held and S1 (search effect) failed. Amendment 2 judged 54 balanced states
three times for PLp and once for VO, with 270 Haiku solver attempts: H2 and C2 (length) held;
H1, H3, C1 and C3 failed. Amendment 3 repeated the solver criterion with Sonnet 5.5 and Opus 5.5
(270 attempts each): O1 (search predicts non-optimal answers) held for both, O2 and P1 failed for both,
F2 held for Sonnet, and Opus's failure tests hit the ceiling.

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
  cost-to-go that the rivercross arm found (Spearman 0.83–0.89) survives both the rubric re-key and
  the move to one state per call with the v2 prompt. Amendment 1 shows that the link is mostly
  distance to the goal, not search.
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

## Amendment 2: search as depth × width, apart from execution length

Pre-registered before any of its labels (`415d459`). The sample is 54 states from 37 puzzles, 6 per
cell of a 3 × 3 grid of crossings left (2–3, 4–6, 7+) by search bits (up to 4.5, 5–8, 8.5+). The
pool includes puzzles with "free" items that conflict with nothing. The sample Spearman of crossings
left against bits is 0.14.
- **PLp:** three Opus-low repeats; the label is the median.
- **VO:** v1 rubric, once per state.
- **Solver:** five Haiku 4.5 attempts per state. The pre-registered pilot on 12 other states gave a
  success share of 0.77, so the rule chose Haiku. The attempts were replayed with the puzzle rules.

From `results/search.json` (`analysis/search.py`). Coefficients are standardised; standard errors
are HC3.

| test | model | result | prediction (p) | holds |
|---|---|---|---|---|
| H1 | PLp ~ bits + ctg | bits +0.10, p = 0.26 | > 0, p < 0.05 (0.4) | no |
| H2 | same | ctg +0.33, p = 0.0001 | > 0, p < 0.05 (0.8) | yes |
| H3 | same | bits below ctg | bits > ctg (0.25) | no |
| C1 | failure ~ bits + ctg | bits +0.04, p = 0.27 | > 0, p < 0.05 (0.6) | no |
| C2 | same | ctg +0.12, p = 0.0002 | > 0, p < 0.05 (0.5) | yes |
| C3 | — | Spearman of PLp with failure 0.20 | at least 0.3 (0.5) | no |

**Reading, as fixed in advance: H2 without H1, so PLp follows forced length, which is Volume's
ground.** The solver criterion agrees that length, not search bits, is what makes these states
harder for Haiku (C2 without C1).

**Mean PLp by cell:**

| crossings left | bits low | bits mid | bits high |
|---|---|---|---|
| 2–3 | 1.50 | 2.33 | 2.33 |
| 4–6 | 2.33 | 2.50 | 2.67 |
| 7+ | 3.00 | 2.67 | 2.83 |

**Solver failure share by cell:**

| crossings left | bits low | bits mid | bits high |
|---|---|---|---|
| 2–3 | 0.17 | 0.17 | 0.17 |
| 4–6 | 0.10 | 0.40 | 0.23 |
| 7+ | 0.43 | 0.50 | 0.47 |

Exploratory:
- **How the solver fails.** Of 270 attempts, 191 succeeded (71%), 71 made an illegal move (26%),
  5 gave no parsable answer, and only 3 were legal but did not reach the goal. Illegal moves rise
  with length: 14% at 2–3 crossings, 20% at 4–6, and 44% at 7+. So Haiku rarely fails to find a
  plan. It fails to keep the banks straight over a long sequence. That is a state-tracking demand
  (working memory, execution), not a planning one, so this criterion cannot vindicate PLp following
  length.
- **Search bits predict neither labels nor failures on these puzzles.** Tree bits (depth × width,
  counting choices that all work) do no better. They give +0.03 on PLp (p = 0.62) and +0.06 on
  failure (p = 0.09). The puzzles may simply be small enough that search is not the bottleneck for a
  language model.
- **PLp also rises with search bits at short lengths.** At 2–3 crossings, low bits give a mean of 1.5
  and mid or high bits 2.33, and the judges' answers cite interacting choices. Overall the effect is
  small next to length.
- **VO** is 1 on 9 states and 2 on 45. It rises weakly with crossings left (ρ = 0.42) and with bits
  (0.35), as expected for a rubric that counts thinking time in coarse log-time bins.
- **Repeats.** All three PLp repeats agreed on 59% of states. PLp was 3 on 30 states, 2 on 20, 1 on
  3 and 0 on 1.
- **Judge reasoning.** Some answers misread the puzzle. One, for a chain puzzle with free items,
  says taking the free items early "can lead to a forbidden pair later", though free items conflict
  with nothing.

Caveats:
- One judge and one solver model.
- Search bits count all legal non-undoing sequences as equally likely, which no real solver does.
- 54 states.
- The solver criterion mixes planning with state tracking. A referee-checked, move-by-move solver
  would isolate search better, since illegal moves would be rejected rather than counted as failures.

## Amendment 3: strong solvers

Pre-registered before any of its answers (`3b71501`). The same 54 prompts go to Sonnet 5.5 and Opus 5.5
(`rc-solver`, effort low), five attempts each, scored as in amendment 2 plus optimality: success with
the minimum number of crossings. From `results/strong.json` (`analysis/strong.py`).

| | Sonnet 5.5 | Opus 5.5 |
|---|---|---|
| success | 247 of 270 (91.5%) | 266 of 270 (98.5%) |
| failures | 17 illegal moves, 6 legal but short of the goal | 4 illegal moves |
| non-optimal share | 27% | 9.3% |

| test | Sonnet 5.5 | holds | Opus 5.5 | holds |
|---|---|---|---|---|
| F1. failure ~ bits | −0.009, p = 0.67 | no | ceiling (1.5% failures) | uninformative |
| F2. failure ~ ctg | +0.057, p = 0.008 | yes | ceiling | uninformative |
| O1. non-optimal ~ bits | +0.087, p = 0.016 | **yes** | +0.071, p = 0.004 | **yes** |
| O2. non-optimal ~ ctg | −0.050, p = 0.21 | no | −0.048, p = 0.044 (negative) | no |
| P1. PLp vs non-optimal ≥ 0.3 | ρ = 0.10 | no | ρ = −0.02 | no |

Pre-registered probabilities: O1 0.45 for each model, O2 0.45 and 0.4, P1 0.35 for each, F2 0.4 for
Sonnet.

**Reading, as fixed in advance: O1 without O2 for both strong solvers. Search makes these states
hard for strong models, and PLp, which follows length, misses it.**

**Opus's non-optimal share by cell:**

| crossings left | bits low | bits mid | bits high |
|---|---|---|---|
| 2–3 | 0.00 | 0.07 | 0.37 |
| 4–6 | 0.03 | 0.10 | 0.17 |
| 7+ | 0.00 | 0.07 | 0.03 |

For comparison, mean PLp at 2–3 crossings is 1.5 (low bits) and 2.33 (high bits), against 2.7–3.0 at
7+.

Exploratory:
- **The hardest states for strong models are short and trappy.** Near the goal, a high-bits state has
  few working continuations among many legal ones, so a detour looks natural. Long states often have
  more slack. Non-optimal answers even fall slightly with length once bits are held fixed (Opus
  −0.048).
- **Two kinds of difficulty, two rubrics.** Sonnet's outright failures still rise with length
  (+0.057, p = 0.008), and they are mostly illegal moves. So length does raise a demand, but it is
  state tracking. That is working memory or execution, not planning. On these puzzles PLp follows
  that demand rather than its own.
- PLp against failure: ρ = 0.27 for Sonnet and −0.01 for Opus.

Caveats:
- Non-optimality counts any longer route as a miss, including a correct but roundabout answer. The
  prompt asked for "a sequence" that works, not the shortest one, so non-optimality measures search
  quality without having been demanded.
- Effort was low. Higher effort would probably lower both shares.
- 54 states and one prompt format.

## Deviations and caveats

- **Amendment 1, transcript gap.** For one of the 177 contrast answers
  (`missionaries-cannibals-4-boat-3--R-C2.C3.M1.M3`, repeat 1), the judge transcript lacks the
  assistant record that holds the Write call. The harness's "File created successfully" reply for
  that file is present, and every record in that transcript is from `claude-opus-5-5`. `writers.py`
  now accepts that confirmation when no Write call matches, and marks such cells
  `evidence = harness_confirmation` in `writers.csv`. It is the only such cell.

- **Amendment 2, relay scheduling.** Launching eight relays at once hit the harness's concurrent-subagent
  limit. One pilot relay (t2) sent nothing and was relaunched later. One main-run cell (t1,
  `star-3+free2-boat-1--L-farmer.item2.item3.item5`) failed with a transient harness error before any
  answer and was sent once more. No cell has two answers in one attempt folder.
- **Amendment 3, stalled relays.** Three relays (Opus t3 and t4, Sonnet t3) stopped on a harness
  watchdog, with 10 minutes without progress, while usage was low. Only the cells with no answer
  were sent again: 41, 45 and 53. No cell has two answers in one attempt folder.
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
