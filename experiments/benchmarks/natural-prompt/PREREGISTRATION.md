# natural-prompt — pre-registration

Committed and pushed before any label of this study. Pablo asked for it on 2026-09-29 and chose the
wording (option 1).

**Question.** Can a plain annotation prompt stop Sonnet 5.5's safeguards from blocking our requests,
without changing the labels of our judge (Opus low)?

**Why.** Our shared prompt dates from the v1 pipeline (2024-era models). It asks, in capitals, for
"CHAIN-OF-THOUGHTS REASONING STEPS". In `judge-sonnet55`, Sonnet 5.5 blocked 23 of 44 PLp prompts
twice, under the `reasoning_extraction` category. Anthropic's guidance describes this category as
prompts that ask the model to reproduce its internal reasoning in the response text, and advises
removing such instructions.

## The natural prompt (`prompt.py`)

It keeps the method and changes only the wording:
- it states the research purpose in one sentence;
- it wraps the rubric and the task in `<rubric>` and `<task>` tags;
- "Rate the task's demand for {demand} according to the rubric, not any particular solver's attempt
  at it";
- the rule to choose the lower of two adjacent levels unless the higher one is clearly met;
- "Before giving a level, write a short assessment of the task against the rubric: what the task
  requires, which level's conditions it meets, and what keeps it below the next level. Give the
  level that this assessment supports";
- it ends with "The level of {demand} demanded by this task is: N", which the existing parser reads.

The judge agents get neutral instructions too (`adele-judge-v2-low`, `adele-judge-v2-high`: "Answer
as the instructions ask"). The old agents said "a step-by-step written assessment".

`make_runs.py` rebuilds every old prompt from the same rubric and task text and checks it against the
stored hash of `swepl-gate`. So the inputs are identical, and only the prompt's wording differs.

## Tests

**A. Safeguards** (run `np-plp-s55h`). Sonnet 5.5 at high effort on the 44 PLp gate cells: the 23 it
blocked twice under the old prompt, and the 21 it answered. A cell whose call is blocked is judged
once more, as before.
- **A passes** if at most 2 of the 23 are still without an answer.

**B. Method** (run `np-gate-opuslow`). Opus low with the natural prompt on the 132 gate cells (PLp,
PLe, PLs × 44 tasks), against Opus low's stored labels under the old prompt (`swepl-gate-low`).
Opus low's repeat agreement is about 88% exact (Terminal-Bench PLp; the lab regression).
- **B passes** if all four hold:
  1. exact agreement 0.83 or more (about two standard errors below 88% at n = 132);
  2. within one level 0.98 or more;
  3. mean shift within ±0.10 for each rubric;
  4. at least 95% of cells labelled by `claude-opus-5-5` and parsed.

**Verdict** (`analysis/analyse.py`): A and B each pass or fail.
- If both pass, the natural prompt fixes the flags and keeps the labels. I then propose moving it into
  `src/adele/annotation/prompts.py` as a new builder, next to the old one. That needs Pablo's OK.

**Also reported:** agreement with Opus medium under both prompts, calls stopped by a safeguard, and
the mean answer length under both prompts.

**Cost.** About 44 to 88 Sonnet calls and 132 Opus-low calls, roughly 1 to 1.5 weekly points. Judging
starts after the weekly reset (2026-09-29 20:00 UTC).

## Predictions (sealed)

- A passes: 0.65. At least 20 of the 21 control cells answered: 0.85.
- B: exact 0.83 or more, 0.65; within one level 0.98 or more, 0.9; every shift within ±0.10, 0.55.
  B passes: 0.45.
- Both pass: 0.3.
- Answers are shorter under the natural prompt: 0.75.

## Deviations

None yet.
