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

## Amendment 1: variant B (added 2026-09-29, after the first run, before any label of B)

**Why.** In the first run, the plain prompt moved 19 labels, all upward. Reading the 19 answers
against the rubric text: on the 12 PLe cells the plain prompt follows the rubric (checking is
elected, which is Level 3, and r59 measured such tasks at 3). On 4 PLp cells it called a standard
debugging routine "assembled" (Level 2), and on 2 PLs cells it ignored a Level 1 example that
matches the task. So the aim is to keep the PLe gain and undo the other upgrades.

**Variant B** (`prompt.py`, `TEMPLATE_B`) adds three sentences to the assessment paragraph: "Compare
the task with the rubric's examples at the levels you consider. Base the level on the conditions
the rubric states, not on how long or easy the work looks. If the task genuinely fits two adjacent
levels, choose the lower one." The old lower-of-two sentence is dropped, so the rule is stated once.

**Runs.** `npb-gate-opuslow` (Opus low, the 132 gate cells) and `npb-plp-s55h` (Sonnet 5.5 high, the
44 PLp cells), with the same agents, relays and retry rule as before.

**Checks** (`analysis/analyse_b.py`). Pablo chose not to add blind labels, so the targets come from
my reading of the rubric, which is not independent of the judges.
- T1: at least 10 of the 12 PLe cells stay at 3.
- T2: at least 5 of the 6 upgraded PLp and PLs cells (astropy-7671, django-11433, scikit-learn-14894,
  sympy-20916 on PLp; django-15629, django-15916 on PLs) go back to their old label.
- T3: on the other 113 cells, exact agreement with the old labels 0.85 or more, and each rubric's
  mean shift within ±0.10.
- A: at most 2 of the 44 PLp cells without a Sonnet 5.5 answer after one retry.
- P: at least 95% of the 132 Opus cells labelled by `claude-opus-5-5`.
- The 3 contested PLp cells (django-11451 and django-12143 at 0 to 1, django-15629 at 2 to 3) are
  reported, not scored.

B passes if every check holds.

**Predictions (sealed).** T1 0.75; T2 0.55; T3 0.7; A 0.85; B passes 0.35.

**Cost.** 176 calls, plus retries; about 1.5 weekly points.

## Deviations

None yet.
