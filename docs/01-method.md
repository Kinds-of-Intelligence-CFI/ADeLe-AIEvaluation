# 01 — Method: demand-to-go

Read this first. It explains what we annotate and why, and which alternatives we
tried and dropped.

## The problem ADeLe v1 does not solve

ADeLe scores a **task** on cognitive demand dimensions, 0–5 per dimension. Demand
is a property of the task, never of the solver: "this task requires level 4
planning", not "this model plans at level 4". Ability is measured separately, by
seeing which demand levels a system succeeds at.

That works when a task is a single static prompt. It breaks for **agentic** tasks,
where a system acts over many steps and the difficulty *changes as the rollout
progresses*. A single number for the whole episode throws that away.

## The ladder: three temporal resolutions

A rollout can be annotated at three resolutions:

| | what is scored | status |
|---|---|---|
| **1a** whole-task | the task as given, once, at the start | **dropped** |
| **1b** demand-to-go | from an intermediate state, how much difficulty remains to reach success | **the method we use** |
| **2** per-transition | the demand of one action | **dropped** |

**1b is the workhorse.** It is the only rung that carries signal on every
dimension we have tested, and it is the one that yields the demand-vs-progress
curve — the thing a whole-task score cannot express.

**Why 1a was dropped.** Coarse, and redundant with 1b's start state. Worse, the
same judge labels the same state differently depending on which framing it is
shown, so 1a and 1b are not interchangeable views of one quantity.

**Why 2 was dropped.** It is value-blind. A single action has no horizon, so the
label collapses to a near-constant. Kept as a recorded negative result in
`experiments/rivercross/ple/labels/2/`.

A third rung — a typed `task → trajectory → transition` IR, and a learned value
model over it — is deferred, not refuted. It needs trace decryption we do not
have.

## What makes a 1b annotation valid

Four rules, each of which came out of a failure rather than being imposed up
front:

1. **Frames must be leak-free.** The judge never sees the solver's numbers. On
   rivercross this is enforced by construction in `experiments/rivercross/frames/`.
2. **The prompt is dimension-agnostic.** One shared template; the rubric text is
   the only thing that varies between dimensions. Template and rubric stay
   separate files — see `experiments/rivercross/prompts/`.
3. **Levels must be a logical partition, defined operationally.** Vague
   feature-bundles are what drive judge disagreement. The PLe calibration turned
   on exactly this: the whole disagreement came down to one ambiguous word,
   *feedback*, and was fixed by defining it operationally as the environment's
   success signal — not observation, not legality.
4. **Judge quality is dimension-dependent.** Annotating a reasoning dimension's
   demand is itself a reasoning task, so capable judges converge and weak ones lag
   on states they cannot solve. Fix the judge panel and an inclusion criterion
   *before* collecting labels, never after seeing the gates.

## How agreement is judged

Raw exact-match is not enough — a judge that defaults to one level can score well
on it. We report, per dimension:

- **quadratic-weighted κ (QWK)** and within-1 agreement across judges;
- **Spearman correlation against the solver's true cost-to-go**, where a testbed
  supplies one.

The second is only available on a testbed with ground truth. That is the whole
reason `experiments/rivercross/` exists — see `03-experiments.md`.

## Where the code lives

- Prompt building and the rubric catalogue: `src/adele/agentic/`
- The solver-backed testbed: `src/adele/testbeds/rivercross/`
- Judge CLI: `adele agentic judge`
