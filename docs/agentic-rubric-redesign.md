# Re-keying the ADeLe v2 agentic demand dimensions

**Status:** draft for team review · branch `rubrics/v2-improved` · all rubrics validated, none merged to `agentic`

---

## 1. Summary

The v2 agentic rubrics (Paolo_Pablo stream) were measurably collinear: on our own
3-judge HAL labels, **PLp and PLe never separated** — no task scored high on one and
low on the other, for any judge, in any label set — and they differed by a
near-constant offset of +0.9 to +1.1. That is the signature of two scales keyed on the
same underlying quantity with different intercepts, not of two abilities.

The cause was structural. Each rubric declared five to seven difficulty drivers, and
neighbouring rubrics declared *overlapping* ones — temporal horizon, number of agents,
open-endedness, environment dynamics. A long, multi-agent, dynamic task therefore
scored high on every agentic dimension at once. The drivers were doing the work, not
the abilities.

We re-keyed four dimensions so that each is scored on **exactly one driver**, and every
other difficulty feature is explicitly routed to the dimension that owns it. One
dimension was re-filed from the social family to the planning family and renamed; one
was removed from the demand set entirely.

| code | name | status |
|---|---|---|
| **PLp** | Planning | re-keyed |
| **PLe** | Action control and execution | re-keyed |
| **PLs** | Situational and environmental understanding | re-keyed, re-filed from `MSe`, renamed |
| **MSc** | Communication and social interaction | re-keyed |
| ~~ECc~~ | ~~Behavioural inhibition and self-control~~ | **removed** — propensity, not ability |

All four keep the exact v1.0 rubric shape: title, one preamble paragraph, Levels 0–5
with a prose definition and concrete examples. No new dimension codes, no structural
additions, no changes to `data_v1`.

---

## 2. The four drivers

Each dimension now moves on one quantity, and each level is characterised in its own
text by where that quantity stands. Read the verb spines below as the whole design.

### PLp — Planning
**Driver: how much of a workable plan already exists, and how strongly its choices interact.**

> given (0) → retrieved (1) → assembled (2) → searched for (3) → constructed (4) → invented (5)

The demand is set by the *hardest plan-finding the task requires*, whether at the outset
or when execution shows the plan failing. Deliberately **not** drivers: how long execution
takes (→ VO), whether other agents are present (→ MS), whether the environment changes
(→ PLs), whether feedback is sparse (→ PLe). Those raise PLp only insofar as they make a
workable plan harder to find — so a long, dynamic, multi-agent task whose plan is obvious
stays low, and a static, fully observable, single-agent task can reach the top.

### PLe — Action control and execution
**Driver: how the task lets execution errors be detected and recovered.**

> checked at every step (1) → checked at checkpoints (2) → self-checked (3) → safeguarded against propagation (4) → safeguarded before every commitment (5)

Also covers the executive residue: noticing that a plan is no longer working (devising the
replacement is PLp), deciding what to advance next, and choosing the matching branch of a
conditional plan. Two definitions do the heavy lifting:

- **An action** is the carrying-out of one plan step — the finest unit that could be
  *separately instructed*, *done wrong*, and *redone*. Tokens fail both tests; a trace's
  tool calls pass, so task-level and trace-level annotation agree by construction.
- **Feedback** is information that establishes, *without further work*, that a step
  succeeded — the task's success signal, not mere observation of the new state, and not an
  interlocutor's acknowledgement.

An answer that deliberation can produce whole is executed by mere *transcription*, however
hard it was to find; a deliverable whose earlier parts are used by later ones is
*constructed*, and counts as many actions as it has redoable steps.

### PLs — Situational and environmental understanding
**Driver: how the task-relevant state of the world comes to be known.**

> given (0) → read off (1) → gathered (2) → inferred (3) → tracked (4) → anticipated (5)

Hiddenness first, then change; the top rung is state that changes *unsignalled* and must be
projected from a model. Demand rises with how hidden the state is and whether it changes —
**not with how much of it there is**. Deducing what known facts imply is *not* situational
understanding, which is why a Sudoku grid and a chess position are Level 0.

*Why it moved to the PL family:* the agentic loop is know the situation (PLs) → find the
plan (PLp) → execute it (PLe). Filed under MS, its ladder escalated on the number and nature
of other agents — MS's own driver — making the two collinear by construction. With PLs moved
out, the MS family is purely social.

### MSc — Communication and social interaction
**Driver: how far the other party's stance must be moved, how much it resists, and how much the moves must adapt to what they do in return.**

> no stance to move (0) → no steering needed (1) → steering a cooperative exchange (2) → moving an open stance (3) → overcoming resistance (4) → reconciling conflicting stances (5)

This is the *active-strategic residue* left once Mind Modelling takes the reading of minds
and Verbal Expression takes the crafting of messages — including fitting an explanation to
its audience, which v1 CEe already owns. Two consequences are deliberate and will look
counterintuitive:

- **Stakes do not raise the demand.** A grave diagnosis delivered by an established protocol
  to a listener who is not opposing you is a 3, not a 4. The old rubric made it a 4 by
  definition ("health, jobs, finances or safety") — grading the consequences of failure
  rather than the communicative work.
- **One-shot composition is minimal here**, however persuasive it must be, because there is
  no exchange to steer. A newspaper column arguing for a carbon tax is a 1.

---

## 3. Empirical results

Sixteen evaluation rounds, ~700 annotations, judges **haiku / sonnet / opus** only, always
using the repo's own `build_annotation_prompt` format with reasoning written before any
score. Labels are in `labs/rubric-qa/`.

### 3.1 The headline: old vs new, same tasks, same judges, same seeds

PLp on 8 pilot tasks (5 USACO divisions + 2 tau-bench + 1 AssistantBench), 3 judges × 3 seeds
per arm, 144 annotations:

| metric | old rubric | new rubric |
|---|---|---|
| Krippendorff α (ordinal) | 0.611 | **0.861** |
| levels actually used | 1–3 only | **1–4** |
| per-judge SD | 0.40–0.69 | **0.85–1.15** |
| USACO medians, Bronze→Platinum | 3, 2, 2, 2, 3 (**non-monotone**) | **3, 3, 4, 4, 4** (monotone) |
| Spearman vs contest division | 0.15 | **0.66** |
| Platinum vs a tau-bench flight change | **same score (2)** | 2 levels apart |

Under the old rubric, Bronze was rated *harder* than two Platinums, and a Platinum problem
got the same planning demand as changing a flight booking. The judges' own reasoning cited
the borrowed drivers verbatim: *"no multi-agent coordination → below Level 3"*, *"roughly
4–10 steps → Level 2"*.

### 3.2 Did the measured collinearity actually go away?

Re-annotating the 12 mid-trajectory HAL frames that produced the original finding:

| judge | arm | separation | ρ | mean(PLe−PLp) | SD of that difference |
|---|---|---|---|---|---|
| sonnet | old | 0.00 | +0.82 | +0.92 | 0.28 |
| opus | old | 0.00 | +0.84 | +1.08 | 0.28 |
| sonnet | new | 0.08 | +0.75 | **+0.17** | **0.69** |
| opus | new | 0.00 | +0.71 | **+0.42** | **0.64** |

**The constant-offset signature is gone.** The PLp−PLe difference is now task-dependent
(its variance more than doubled) instead of a fixed intercept, and the two dimensions move
independently on 5 of 12 frames versus 0 of 12 before. Residual ρ ≈ 0.7 with a varying
difference is what two genuinely distinct but correlated demands look like.

Separation itself stays near zero *on this set*, and that is the battery, not the rubric:
all 12 frames are SWE-bench bug-fix checkpoints, a family where plan-finding and execution
difficulty genuinely rise together. On heterogeneous batteries the same rubrics separate in
both directions (§3.3).

### 3.3 Do the dimensions come apart when the tasks differ?

Median profiles, designed and real tasks:

| task | PLp | PLe | PLs | MSc |
|---|---|---|---|---|
| Find the winning line in a chess position | 3 | **1** | **0** | 0 |
| USACO Platinum problem (real, pilot) | **4** | 3 | **0** | 0 |
| Year-end ledger reconciliation by hand | low | **4** | 1 | 0 |
| Live database migration, no rollback | low | **5** | 2 | 0 |
| Intermittent radio interference, unsignalled | 2 | 2 | **5** | 0 |
| Broker water rights among three farms | 3 | 2 | 2 | **5** |
| tau-bench retail conversation (real, pilot) | 2 | 1 | 2 | **2** |

High-on-one, low-on-another appears in **both** directions for every pair. The old rubric
set could not produce a single such cell.

### 3.4 Do the traps hold? (designed adversarial items)

Each rubric was given items built to pull it toward a neighbouring dimension.

| trap | designed | result |
|---|---|---|
| PLp: 200-step protocol executed as written (length is VO) | 0 | held |
| PLe: chess line — plan-hard, execution-trivial | ≤1 | **failed 9/9, then fixed**, now 15/15 |
| PLs: Sudoku / chess / fully specified statement (deduction ≠ observation) | 0 | 27/27 exact |
| MSc: read a poker opponent, never interact (that is MS) | ≤1 | held |
| MSc: persuasive newspaper column (that is CEe) | ≤1 | **failed 3/3, then fixed**, now 1/1/1 |
| MSc: grave veterinary diagnosis to a trusting family (stakes ≠ resistance) | 3 | held |

The two failures were the most valuable results in the project; both are described in §4.

### 3.5 Do the judges annotate the way we would?

Three real pilot tasks, one per benchmark family, all four dimensions, with our expected
labels **written down before any judge ran** (`labs/rubric-qa/prereg_expected.json`):

- **9 of 12 cells exact, 12 of 12 within ±1.**
- 92% of judge *pairs* within ±1; haiku sits +0.25 above the cell median on average.
- On the hardest pilot task (USACO Platinum, §3.3) the profile matched pre-registration on
  **all four** dimensions.
- In two cells the judges were arguably right and *we* were wrong — e.g. tau-bench PLe,
  where sonnet and opus scored 1 because every tool call returns an immediate success
  signal, which follows the rubric more exactly than our own expectation did.

> **A note on Krippendorff α.** On the real-pilot cells α is 0.393, far below the 0.86–0.99
> of the designed batteries. This is a prevalence artefact, not a regression: 18 of 28 labels
> were exactly 2, so chance agreement is already high and α over-penalises any deviation
> (raw agreement was 92% within ±1). **Always report α with the level distribution beside
> it.** Evidence that the ladders do resolve where real tasks live: PLp over 8 pilot tasks
> spans levels 1–4 with SD 0.85–1.15.

---

## 4. The two failures worth reading

**PLe: what counts as an "action"?** A task reading *"find the winning line in this chess
position and write it down"* was designed to score ≤1 — all difficulty is in finding the
plan. Every judge scored 4, and they were faithful to the text: calculating chess variations
is a chain of dependent internal steps where an early error invalidates the rest, which is
exactly what the Level 4 anchor described. But if internal reasoning counts as execution,
every hard reasoning task scores high on *both* PLp and PLe — and the collinearity we were
removing returns through the side door. Defining an action *intentionally* (one plan step:
separately instructable, wrongable, redoable) rather than physically fixed it: the trap has
held 15/15 since, and an unrelated seed-instability on USACO disappeared at the same time.

**MSc: naming a boundary is not enforcing it.** The preamble said this dimension is about
"steering an interaction, not composing its messages" — but no *level* required an exchange,
so a one-shot persuasive column slid into Level 3, whose text ("brought there by argument,
framing or compromise") describes an op-ed exactly. Making interactivity a gate fixed it, and
a **held-out** case never mentioned in the rubric (writing a eulogy) also scored 1 — so the
judges applied the gate rather than matching an anchor.

The generalisable lesson: *a distinguishing property stated only in the preamble is not
enforced.* Every load-bearing distinction now appears as a "Critically, …" clause inside the
level that needs it, and every level that could absorb its neighbour has an explicit floor.

---

## 5. Why ECc was removed

Two independent reasons. First, it scores a **propensity, not a capability**: its levels
conditioned on the solver's state — the same situation ("ignore a notification while
working") appeared at three different levels, separated only by asserted willpower — which
breaks the task-not-solver invariant the whole taxonomy rests on. Second, the executive-
function literature does not support inhibition as a separable ability factor.

Its capability-flavoured content — noticing that a tempting action is the wrong one and not
taking it — is already covered by PLe, whose driver is detecting deviations and recovering.
Any propensity description the team wants should live outside the demand taxonomy and not be
scored on the same 0–5 scale. The file remains in git history.

---

## 6. Also changed: judging protocol moved out of the rubrics

Two sentences that apply identically to every dimension — *demand is a property of the task,
not of any particular solver's behaviour*, and *when in doubt between two adjacent levels,
assign the lower unless the higher level's requirement is clearly met* — now live once in
`build_annotation_prompt` instead of being repeated in rubric text. The tie-break rule
measurably converts weak-judge boundary noise into a deterministic choice.

**This touches the prompt used by all dimensions, including v1, and needs sign-off.** Both
sentences are dimension-neutral and should only sharpen v1 annotation, but it is a
shared-pipeline change.

---

## 7. Limitations and open questions

1. **Separation on real traces is still unproven** — the HAL set is one benchmark family. The
   decisive test is a mixed-family trace run (SWE + tau frames together); the tau traces are
   already in `labs/hal-traces/tau`.
2. **No human anchor yet.** The two-phase worksheet in `labs/hal-traces/worksheet/` exists;
   ~15 items would tell us whether judges track the intended construct or merely agree with
   each other.
3. **Real benchmark tasks cluster in levels 1–3.** The top of every scale is currently
   evidenced by designed items plus USACO Platinum. If the battery is meant to discriminate
   at the top, it needs harder instances.
4. **Known judge offsets.** haiku ceilings at PLp 3 on contest problems where sonnet/opus
   reach 4 — the L3/L4 gate is partly judge-capability-relative (whether the judge can sketch
   the plan). The 3-judge median absorbs it exactly on every task tested.
5. **Open routing decisions for the team:** goal open-endedness with no requester (self-set
   success criteria) is owned by nobody; prospective memory ("act at the right moment")
   sits between PLe and Marko's memory triad; PLe's preamble is 375 words against v1's
   66–217 range, the cost of four definitions no other rubric needs.
6. **Not validated:** the memory triad (MMe/MMp/MMs) is untouched by this work. An earlier
   draft of our audit wrongly claimed those were collinear on the basis of shared example
   text; that claim was retracted — shared Level 0 anchors are the null case, and their
   matched-content contrasts are good design.

---

## 8. Where things are

- Rubrics: `src/adele/rubrics/data_v2/Paolo_Pablo/{PLp,PLe,PLs,MSc}.txt`
- Labels and full round-by-round record: `labs/rubric-qa/`
- Design rationale: the commit messages on `rubrics/v2-improved` are written to be read —
  each records the failure that motivated the change, the alternatives rejected, and the
  verification.

Nothing is merged to `agentic`. Suggested next step: a draft PR so the diff can be reviewed
per dimension, plus a decision on the two open routings in §7.5.
