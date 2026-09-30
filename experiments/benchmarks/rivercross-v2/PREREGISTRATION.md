# rivercross-v2 — pre-registration

Committed and pushed before any label of this study. Pablo asked on 2026-09-30 for the rivercross
puzzles to be judged again with the current rubrics and the adopted v2 prompt, and for PLs to be
tried on them for the first time.

**Question.** On river-crossing puzzles, where an exact solver knows the true remaining work, do the
current planning rubrics behave as they should?
- Does PLp follow the solver's cost-to-go?
- Do PLe and PLs stay low and flat, as their rubrics say they should on small, fully visible,
  rule-governed puzzles?

## Why

The benchmark studies have no ground truth, only solve rates. The rivercross arm has one, but its
PLp and PLe results were made against rubric text that no longer exists, with many states per call
(`experiments/rivercross/README.md`). This study reruns the arm with what the benchmark studies now
use, so the two arms can be compared.

## Design

- **Frames**, read from `experiments/rivercross/` without change:
  - `rc-state`: 43 puzzle states partway through a puzzle, with the current state shown
    (`frames/1b_state_visible.csv`). Judged for PLp, PLe and PLs, which makes 129 cells.
  - `rc-play`: 49 states from captured agent play, with the move history and the referee's replies
    (`ple/frame_PLe_1b.csv`). Judged for PLe, which makes 49 cells.
- **Ground truth.** For each `rc-state` state, the solver's cost-to-go is the number of crossings
  left on the shortest solution (`frames/ground_truth/1b_state_visible_cost_to_go.csv`). The judge
  never sees it. Its range is narrow: 12 states at 1, 22 at 2, and 9 from 3 to 7.
- **Judge.** Opus low through `adele-judge-v2-low`, relayed by `judge-dispatcher-v2-low`, one state
  per call. The prompt is `build_annotation_prompt_v2`, with the rubrics of the active catalog.
- **Model check.** Only answers written by `claude-opus-5-5` count. Other answers are set aside, and
  the cell is judged once more. If that attempt fails too, the cell has no label.
- **Analysis.** `analysis/analyse.py` runs the tests below. There is no overall pass mark: each test
  is reported on its own.

## Tests and predictions (sealed)

The rubric reasoning behind each prediction:
- PLp: level 0 covers "a task scored partway through whose remaining work is a single forced action",
  and level 3 is where "decisions interact" and options must be compared by looking ahead.
- PLs: where options "follow from stated rules", running them forward "makes no more demand than any
  other rule-governed step".
- PLe: it depends on what checks the task provides. The `rc-play` frames show a referee that rejects
  illegal moves at every step.

| test | measure | prediction | p |
|---|---|---|---|
| T1 | Spearman of PLp with cost-to-go, `rc-state` | at least 0.6, with p < 0.05 | 0.6 |
| T2 | share of the 12 cost-to-go-1 states at PLp 0 or 1 | at least 0.8 | 0.75 |
| T3 | share of `rc-state` PLe labels at the most common level | at least 0.8 | 0.55 |
| T4a | share of `rc-state` PLs labels at 2 or below | at least 0.8 | 0.7 |
| T4b | Spearman of PLs with cost-to-go, against T1 | below PLp's | 0.75 |
| T5 | share of `rc-play` PLe labels at the most common level | at least 0.8 | 0.65 |

What would matter:
- **T1 and T2 fail:** the current PLp rubric, or this protocol, has lost the link to true remaining
  search that the older rivercross work found.
- **T4 fails:** PLs is picking up search size, which belongs to PLp.

**Exploratory, not tested:**
- PLs against the number of items, forbidden pairs and boat size.
- PLe against cost-to-go.
- Mean PLp at each cost-to-go.
- The new labels against the older Opus labels for the same states (`method1b/labels_v11/opus_PLp.csv`
  and `ple/labels/1b/opus_PLe.csv`). Those labels came from an older rubric and protocol, so this
  comparison describes the change rather than testing it.

## Cost

178 Opus-low calls in two relays: about 1 weekly point.

## Caveats known in advance

- **One judge.** The earlier rivercross work compared three.
- **Narrow ground truth.** 34 of the 43 states are 1 or 2 crossings from the goal.
- **Small numbers.** With 43 states, a rank correlation of 0.6 has a 95% interval of roughly
  0.36 to 0.77.
- **Different framing.** The frames ask for a sequence of crossings from a given state. That is the
  "demand-to-go" framing of the rivercross arm, not the whole-task framing of the benchmark studies.

## Deviations

None. See `RESULTS.md`.

## Amendment 1 — length or search? (2026-09-30, before any `rc-contrast` label)

**Why.** In the main runs, PLp rose one level per step of cost-to-go (ρ = 0.85, `RESULTS.md`). On these
puzzles cost-to-go mixes two things: how long the remaining solution is, and how much search it takes to
find. The PLp rubric scores only the second: "Nor is the demand raised by how long or laborious the
execution is". So the main result cannot tell whether the judge follows search or counts crossings.

**Measures.** Both come from the solver, over the states of 50 solvable puzzles (`make_contrast.py`):
- **Length:** cost-to-go, the number of crossings left.
- **Search:** decision points. This is the fewest steps, along any optimal route from the state, at
  which some legal crossing other than undoing the previous one is not optimal. A step with a single
  sensible crossing is forced and does not count. At the state itself, any non-optimal crossing
  counts, because the frame does not show the previous crossing.

**Run `rc-contrast`.** Pairs are drawn within one puzzle, so the rules and wording match within a pair
(seed 20260930):
- **9 search pairs.** These are all the (puzzle, cost-to-go) combinations where decision points
  differ by 2 or more. The pair has the same length and different search.
- **21 length pairs.** One per puzzle, with the widest gap in cost-to-go (2 or more) at equal decision
  points. Neither state is one crossing from the goal, since the rubric's Level 0 already covers that.
- **Scale.** 59 distinct states, PLp only. Each state is judged three times by Opus low (judge folders
  `opus-low-r1` to `r3`), and the label is the median. That makes 177 calls, about 1 weekly point.
  The frames use the same wording as `rc-state`, built by the rivercross library's `_subproblem_text`.

**Tests** (`analysis/contrast.py`). The difference in each pair is PLp(more) − PLp(less).

| test | holds if | p |
|---|---|---|
| S1. search effect | mean difference over search pairs at least 0.5, and one-sided sign test p < 0.05 | 0.3 |
| L1. length effect | the same over length pairs | 0.7 |

**Reading, fixed in advance.**
- **S1 holds and L1 fails:** PLp follows search, as the rubric intends.
- **L1 holds and S1 fails:** PLp follows length, which the rubric says it should not. The ρ = 0.85
  result would then be mainly a length effect.
- **Both hold:** PLp follows both.
- **Neither holds:** neither effect was detected.

With only 9 search pairs, S1 has little power: the sign test needs about 5 untied pairs, all in one
direction. So a failed S1 is weak evidence against a search effect, while a length effect is easier to
detect.

**Exploratory.** Spearman of PLp with cost-to-go and with decision points over all 59 states, mean PLp
at each value, and how often the three repeats agree.

## Amendment 2 — search as depth × width, apart from execution length (2026-09-30, before any of its labels)

**Why.** In amendment 1, PLp rose when forced crossings were added and barely moved when decision
points were added. Pablo's reading: search demand does grow with depth and width, but a forced step
(width 1) adds depth without adding search. So the question is whether PLp follows the size of the
search, or the forced length of the solution, which belongs to Volume.

**Measures** (`make_search.py`, per state, from the solver):
- **Execution length:** crossings left (ctg).
- **Search bits.** Take the legal crossing sequences of length ctg that never undo the previous
  crossing. Bits = −log₂ of the share of those sequences that reach the goal.
  - A forced step multiplies both counts by 1, so it adds nothing.
  - Choices that all work keep the share high, so they add little.
  - Only choices that can go wrong add bits, at any depth.
- **Tree bits** (sensitivity): log₂ of the number of those sequences. This counts depth × width,
  including choices that all work.

**Puzzles and sample.**
- **Pool.** 93 solvable puzzles: the four conflict topologies (3–7 items, boat 1–4),
  missionaries-cannibals (3–5 pairs, boat 2–3), and chain, star and cycle puzzles with 1–3 extra
  "free" items that conflict with nothing. The free items lengthen solutions with little search.
- **Grid.** States 2 or more crossings from the goal are placed on a 3 × 3 grid: crossings left
  (2–3, 4–6, 7+) by bits (up to 4.5, 5–8, 8.5+).
- **Draw.** 6 states per cell, at most one per puzzle in a cell (seed 20260930). That gives 54
  states from 37 puzzles, with a sample Spearman of crossings left against bits of 0.14.
- **Pilot.** 12 more states outside the sample, for the solver pilot.

**Runs.**
- `rc-search`: PLp on the 54 states. Three repeats by Opus low with the v2 prompt; the label is the
  median.
- `rc-search-vo`: VO on the 54 states, once. There is no Volume rubric in the v2 set, so this uses
  the published v1 rubric. It is descriptive only: VO bins by log₁₀ of human minutes and counts
  thinking time, so it is not a clean measure of execution length.
- `rc-solve-pilot`, then `rc-solve`: a solver model gets each state with an answer format, five
  independent attempts per state, through the new `rc-solver` agent (Read and Write only) and its
  relay `rc-solver-dispatcher`. `score_solve.py` replays each answer with the library's rules. An
  attempt succeeds if every crossing is legal and everything ends on the right bank. The scorer was
  checked on solver-generated solutions: 66 of 66 optimal ones succeed, and truncated ones fail.
- **Solver model, fixed by the pilot.** Haiku 4.5 (alias `haiku`) makes 5 attempts on each of the
  12 pilot states.
  - If its success share is 0.15 or less, the solver is Sonnet 5.5 (alias `sonnet`, effort low from
    the agent file), and the pilot is rerun with it for the record.
  - Otherwise the solver is Haiku.
  - Above 0.9, Haiku is still used, and C1–C3 are flagged as having little variance.
- **Model check.** As before, only answers by the intended model count. Other answers are set aside
  and retried once.

**Tests** (`analysis/search.py`). Both predictors are standardised, and OLS uses HC3 standard errors.
Failure is the share of a state's five attempts that do not succeed.

| test | model | holds if | p |
|---|---|---|---|
| H1 | PLp ~ bits + ctg | bits coefficient > 0, p < 0.05 | 0.4 |
| H2 | same | ctg coefficient > 0, p < 0.05 | 0.8 |
| H3 | same | bits coefficient > ctg coefficient | 0.25 |
| C1 | failure ~ bits + ctg | bits coefficient > 0, p < 0.05 | 0.6 |
| C2 | same | ctg coefficient > 0, p < 0.05 | 0.5 |
| C3 | — | Spearman of PLp with failure at least 0.3 | 0.5 |

**Reading, fixed in advance.**
- **H1 without H2:** PLp follows search, as intended.
- **H2 without H1:** PLp follows forced length, which is Volume's ground. The PLp rubric, or the way
  judges apply it, then needs to say that forced steps do not count.
- **Both:** PLp follows both, and H3 says which dominates.
- **C1 and C2** say which of the two actually makes a state harder for a solver. That is the
  criterion PLp should serve.

**Sensitivity.** H1–H3 and C1–C2 are rerun with tree bits in place of bits.

**Descriptive.** VO levels and their correlation with crossings left and with bits. PLp and failure
by cell of the grid. How often the three repeats agree.

**Cost.**
- 162 PLp calls and 54 VO calls by Opus low.
- 60 pilot calls and 270 solver calls by Haiku (or Sonnet).
- About 2.5 weekly points in all.

## Amendment 3 — strong solvers (2026-09-30, before any of its answers)

**Why.** Pablo does not trust Haiku as the difficulty criterion. It is too weak, and its failures in
amendment 2 were almost all illegal moves, meaning state-tracking slips. The question is how hard these
states are for frontier models. So the amendment 2 solver criterion is repeated with Sonnet 5.5 and
Opus 5.5.

**Runs** (`make_strong.py`). The 54 `rc-solve` prompts are copied unchanged, with the same SHA-256.
- `rc-solve-sonnet`: model alias `sonnet` (Sonnet 5.5), five attempts per state.
- `rc-solve-opus`: model alias `opus` (Opus 5.5), five attempts per state.

Both use the `rc-solver` agent at effort low and are scored by `score_solve.py`. At most four relays
run at a time. Only answers by the intended model count; others are set aside and retried once.

**A second criterion.** Strong models may rarely fail, so each attempt is also scored as optimal or
not: it succeeds, and it uses the solver's minimum number of crossings. A tracking slip makes an
answer illegal, while a weak search makes it longer. So non-optimality is the more search-sensitive
criterion.

**Tests, per solver** (`analysis/strong.py`). PLp is the amendment 2 label. Predictors are
standardised; OLS uses HC3 standard errors.

| test | model | holds if | p (Sonnet) | p (Opus) |
|---|---|---|---|---|
| F1 | failure ~ bits + ctg | bits > 0, p < 0.05 | 0.25 | 0.2 |
| F2 | same | ctg > 0, p < 0.05 | 0.4 | 0.35 |
| O1 | non-optimal ~ bits + ctg | bits > 0, p < 0.05 | 0.45 | 0.45 |
| O2 | same | ctg > 0, p < 0.05 | 0.45 | 0.4 |
| P1 | — | Spearman of PLp with non-optimal share at least 0.3 | 0.35 | 0.35 |

If a criterion's overall share is below 0.05, its tests are reported as uninformative (ceiling), not
as failed. My probability that failure hits that ceiling is 0.4 for Sonnet and 0.5 for Opus.

**Reading, fixed in advance.**
- **O1 without O2:** search makes these states hard for strong models, and PLp, which follows
  length, misses it. That is a clear case for the rubric note on forced steps.
- **O2 or F2 without O1:** length drives difficulty even for strong models. Then the question for
  the team is whether that belongs to PLp or to a memory or execution rubric.
- **Ceiling on both criteria:** these puzzles are too easy for frontier models, and the testbed
  cannot answer the question for them without harder puzzles.

**Cost.** 540 solver calls: about 3–5 weekly points, run after the 5-hour window resets
(16:30 UTC).
