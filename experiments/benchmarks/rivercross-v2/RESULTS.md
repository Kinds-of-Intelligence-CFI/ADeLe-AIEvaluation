# rivercross-v2 — results

**Question.** On river-crossing puzzles, where an exact solver knows the true remaining work, do the
current planning rubrics behave as they should?

**Answer.** PLp does. It tracks the solver's cost-to-go at Spearman ρ = 0.85, rising one level at a
time from 0 (one crossing left) to 3 (five or more). PLs stays low, as its rubric says it should on
rule-governed puzzles. PLe is not flat, contrary to my prediction. It splits into 0 for a single
crossing and 3 for a written multi-step answer, which is what its rubric says. On the agent-play
states, where a referee checks every move, PLe is 1 on 47 of 49.

**Status.** Complete (2026-09-30). All 178 cells were labelled by Opus 5.5 at effort low. Five of
the six sealed tests held; T3 failed.

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

## Deviations and caveats

- No deviations from the pre-registration.
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
