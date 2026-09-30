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
