# tau2-goal — the tau2 production input: full task with the goal, without the expected actions (pre-registration)

Pablo, 2026-10-26: "I think we can keep the goal and drop the expected-action list." This replaces the no-grading
check (`../tau2-nogoal`, pinned but never run).

**Why.** `tau2-full` showed the judge the whole grader, including the list of tool calls the grader expects. That
list is close to a written solution. The coding and terminal sets show their goal but not their tests or gold
patches (`goal-visible` study). This input does the same for tau2: the judge sees what must be achieved, not the
steps.

## Input

The judged `tau2-full` text (`data/instances-tau2-full-v2/`) with part 3's expected-action paragraphs removed: the
"Expected agent actions" and "Expected customer actions" headings and the tool-call bullets under them. Part 3 keeps
the designer's purpose, what the agent must tell the customer, the outcome checks, what the reward is based on
(e.g. "DB, COMMUNICATE") and known task issues. Parts 1 and 2 are byte-identical to `tau2-full` (`build.py` checks
this, and that no line exceeds 2,000 chars). Removed text: median 440 chars (airline), 602 (retail), 1,612 (banking).

As before, part 1's records were picked with ids from the grader, so the judge sees which orders or reservations a
task touches, not what to do with them.

## Design

Same 242 tasks, five rubrics (PLp, PLe, PLs, MSm, MSc), judge (Opus 5.5, effort low, subagents), bare-digit prompt
and retries as `tau2-full`. Runs `tau2-goal` (227 tasks, 1,135 cells) and `tau2-goal-long` (15 banking tasks, 75
cells, chunked judge; same 50,000-char / 1,500-line rule). Planner estimate: about 6 weekly points.

This is a production relabel, with no pass/fail rule.

## Reported

1. Per domain and rubric: new labels against `tau2-full` and against the released labels (exact, within one, level
   counts).
2. Criterion signals per rubric (within domain, as `tau2-full`), for released, `tau2-full` and new labels.
3. MSc against Pablo's 15 labels.

## Sealed predictions

| prediction | probability |
|---|---|
| MSc matches Pablo exactly on at least 12 of 15 | 0.65 |
| PLp has a negative within-domain signal with p < 0.05 | 0.8 |
| Pooled exact agreement with `tau2-full` (all five rubrics) at least 80% | 0.6 |

## Then

If Pablo agrees, label set `current` gets a `tau2-goal` layer for the three tau2 benchmarks and five rubrics, and the
tau2 release is rebuilt. `tau2-full` stays as the record of the full-grader input.
