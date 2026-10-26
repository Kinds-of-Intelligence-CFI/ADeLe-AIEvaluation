# tau2-nogoal — the full task without the grading (pre-registration)

Pablo, 2026-10-26: "Pre-register and pin a tau2 run with the full task minus part 3 (grading), same tasks, rubrics
and judge, so we can tell a truer reading from a leak of difficulty cues."

**Why.** In `tau2-full` every rubric tracked solve rate more strongly once the judge saw the full task (PLp −0.28 →
−0.48, MSc +0.10 → −0.32), and MSc matched Pablo on 14 of 15. But part 3 shows the grader's expected actions, outcome
checks and known task issues. A judge that reads "five write actions expected" learns how hard the task is without
reading its demands. If the gains come from parts 1 and 2 (policy, tools, records, script), they should survive
without part 3. If they come from the grader, they should shrink back toward the released labels.

## Input

The judged `tau2-full` text (`data/instances-tau2-full-v2/`), cut before "## 3. The goal", with the opening line
changed from "The agent never sees parts 2 or 3. All three parts together are the task you annotate." to "The agent
never sees part 2. Both parts together are the task you annotate." Parts 1 and 2 are byte-identical to what
`tau2-full` judged (`build.py` checks this). Part 3 had a median of 905 chars (airline), 736 (retail), 1,687 (banking).

**A leak this does not remove.** Part 1's records were picked with ids taken from the grader (the worksheet code),
so the judge still sees which orders or reservations the task touches. It does not see what should be done to them.

## Design

Same 242 tasks, five rubrics (PLp, PLe, PLs, MSm, MSc), judge (Opus 5.5, effort low, subagents), bare-digit prompt
and retries as `tau2-full`. Runs `tau2-nogoal` (227 tasks, 1,135 cells) and `tau2-nogoal-long` (15 banking tasks,
75 cells, chunked judge; same 50,000-char / 1,500-line rule). Planner estimate: about 6 weekly points.

## Reported

1. Per domain and rubric: no-grading labels against `tau2-full` and against the released labels (exact, within one,
   level counts).
2. Criterion signals per rubric (within domain, as `tau2-full`), for released, `tau2-full` and no-grading labels.
3. MSc against Pablo's 15 labels.

## Decision rule (fixed now)

For PLp and MSc, the share of the signal gain that survives without grading:
`kept = (ρ_nogoal − ρ_released) / (ρ_full − ρ_released)`, with ρ the within-domain Spearman with solve rate.
- `kept ≥ 2/3`: the gain is mostly a truer reading. Keep the full task with grading, or drop part 3 at no cost.
- `kept ≤ 1/3`: the gain is mostly the grader's cues. Use the input without part 3.
- In between: mixed. Report it and leave the choice to Pablo.
Noise: with n = 242 each Spearman has a 95% interval of about ±0.12, and there is no rerun estimate for this input.
The two runs share tasks, so their difference is less noisy than that, but its size is unknown. Read `kept` as a
rough share, not a test. Reported for all five rubrics, decided on PLp and MSc.

## Sealed predictions

| prediction | probability |
|---|---|
| PLp: kept ≥ 2/3 | 0.55 |
| MSc: kept ≥ 2/3 | 0.5 |
| MSc matches Pablo exactly on at least 12 of 15 without grading | 0.6 |
| Pooled exact agreement with `tau2-full` (all five rubrics) at least 80% | 0.6 |

## Then

The result goes to Pablo with the decision rule's reading. The label set and the release do not change before his OK.

## Superseded (2026-10-26), never run

Pablo stopped this check before any label: the judge should see the goal. He chose instead to keep the goal and drop
only the grader's expected-action list (`../tau2-goal`). The runs `tau2-nogoal` and `tau2-nogoal-long` stay pinned
with no labels; four relays were recorded and released without launching.
