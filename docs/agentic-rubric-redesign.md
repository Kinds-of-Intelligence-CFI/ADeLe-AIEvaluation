# Re-keying the ADeLe v2 agentic demand rubrics

**Status:** complete and validated, not merged · branch `rubrics/v2-improved` (34 commits off `agentic`)

---

## 0. Orientation — for a reader with no prior context

**What a demand rubric is.** ADeLe scores every *task* on a set of cognitive **demand
dimensions**, each on a 0–5 scale. A rubric is a short document — one paragraph defining the
dimension, then one paragraph per level plus concrete examples — that an LLM judge reads in
order to assign a level to a task. Demand is a property of the **task**, never of the solver:
"this task requires level 4 planning", not "this model plans at level 4". Ability is measured
separately, by seeing which demand levels a system succeeds at.

**The v1 and v2 sets.** ADeLe v1 (`src/adele/rubrics/data_v1/`) is the established, published
set — Verbal Expression (CEe), Volume (VO), Mind Modelling (MS), Knowledge (KN*), Metacognition
(MC*), and others. It is **frozen and untouched by this work**. ADeLe v2 adds an *agentic* set
for tasks where a system acts over time: two authoring streams live under
`src/adele/rubrics/data_v2/`, `Paolo_Pablo/` (planning, execution, environment, communication)
and `Marko/` (a memory triad, also untouched here).

**What this branch did, in one paragraph.** The Paolo_Pablo agentic rubrics were found to be
*collinear* — different dimensions were scoring the same underlying thing, so they moved
together and carried no independent information. We re-keyed four of them so each is scored on
exactly one driver, removed one that was measuring a personality trait rather than a task
demand, and re-filed one from the social family to the planning family. Every change was tested
against LLM judges before being kept, across twenty evaluation rounds and roughly 800
annotations, including a controlled testbed with an exact solver as ground truth.

**Reading order.** This document is the whole account. `labs/rubric-qa/README.md` is the
round-by-round lab notebook with the data. `docs/agentic-open-questions.md` specifies the two
experiments that would settle what is still open. The commit messages on the branch record each
decision, the alternatives rejected, and its verification.

---

## 1. The problem

On our own three-judge labels of HAL agent traces, **PLp (Planning) and PLe (Action Control)
never separated**: no task scored high on one and low on the other, for any judge, in any label
set. The two differed by a near-constant offset of +0.9 to +1.1 with a standard deviation of
only 0.28. That is the signature of two scales measuring one quantity with different intercepts
— not of two abilities.

The cause was structural, and visible in the rubric text without any data. Each rubric declared
five to seven difficulty drivers, and neighbouring rubrics declared **overlapping** ones:
temporal horizon, number of agents, open-endedness, environment dynamics. A task that was long,
multi-agent and dynamic therefore scored high on every agentic dimension simultaneously. The
drivers were doing the work; the dimensions were passengers.

A separate diagnosis applied to two more dimensions: `MSe` (Environmental and Situational
Understanding) was filed under the *social* family but describes a world-model, and its upper
levels escalated on the number and nature of other agents — Mind Modelling's driver — making the
two collinear by construction. And `ECc` (Behavioural Inhibition and Self-Control) conditioned
its levels on the *solver's* state rather than the task's content.

---

## 2. What we changed

### 2.1 The method

Every rubric was rebuilt to the same rules, which emerged from the failures rather than being
imposed up front:

1. **One driver per dimension.** Every other difficulty feature is explicitly *routed* in the
   preamble to the dimension that owns it, and may raise this dimension only through its own
   driver.
2. **A verb spine.** Each level's own text names where the driver stands — "this demand level is
   characterized by the plan being *assembled*" — so a judge classifies rather than impressions.
3. **Categorical gates readable from the task statement.** Boundaries are yes/no questions, not
   magnitudes to estimate.
4. **Quantify only what a judge can count.** PLe's feedback ratio is manifest and gets numeric
   bands; PLp's search sparsity is latent — estimating it means solving the task — so it gets
   none. The asymmetry is deliberate. (§6 records where this rule costs us.)
5. **Anti-inflation floors.** Every level that could swallow its neighbour carries an explicit
   "Critically, …" clause saying what does *not* qualify.
6. **Designed traps, built in from the start.** Each rubric ships with anchors at the boundaries
   where judges historically confuse it with a neighbour.
7. **A distinction stated only in the preamble is not enforced.** Learned the hard way, three
   times. Every load-bearing rule now appears inside the level that uses it (§4.4).

All four keep the exact v1.0 format — title, one preamble paragraph, Levels 0–5 with prose and
examples — so they drop into the existing pipeline unchanged.

### 2.2 The four dimensions

| code | name | driver | spine |
|---|---|---|---|
| **PLp** | Planning | how much of a workable plan already exists, and how strongly its choices interact | given → retrieved → assembled → searched → constructed → invented |
| **PLe** | Action control and execution | how the task lets execution errors be detected and recovered | checked every step → checked at checkpoints → self-checked → safeguarded against propagation → safeguarded before every commitment |
| **PLs** | Situational and environmental understanding | how the task-relevant state of the world comes to be known | given → read off → gathered → inferred → tracked → anticipated |
| **MSc** | Communication and social interaction | how far a stance must be moved, how much it resists, how much moves must adapt | no stance → no steering → steering a cooperative exchange → moving an open stance → overcoming resistance → reconciling conflicting stances |

Three definitions do disproportionate work:

- **An action** (PLe) is the carrying-out of *one plan step* — the finest unit that could be
  separately instructed, done wrong, and redone. Tokens fail both tests; a trace's tool calls
  pass, so task-level and trace-level annotation agree by construction.
- **Feedback** (PLe) is information that establishes, *without further work*, that a step
  succeeded — the task's success signal. Not observation of the new state, not an
  acknowledgement, and **not a check that an action was legal**: a rule that rejects invalid
  moves tells the agent it may proceed, never that it is succeeding.
- **Transcription vs construction** (PLe): an answer deliberation can produce whole is executed
  by transcription however hard it was to find; a deliverable whose earlier parts are used by
  later ones is executed through all of them, even when handed over at once.

Two consequences are deliberate and look wrong at first glance. In MSc, **stakes do not raise
demand** — a grave diagnosis delivered by protocol to a listener who is not opposing you is a 3,
not a 4 — and **one-shot persuasive composition is minimal**, however hard, because there is no
exchange to steer (that difficulty is Verbal Expression plus Mind Modelling).

### 2.3 Removed, renamed, and one pipeline change

- **`ECc` removed.** It scores a propensity, not a capability: the same situation appeared at
  three levels separated only by asserted willpower, which breaks the task-not-solver invariant.
  The executive-function literature does not support inhibition as a separable ability factor.
  Its capability-flavoured content — noticing a tempting action is wrong — is already PLe's.
- **`MSe` → `PLs`**, re-filed from the MS family to the PL family. The agentic loop is *know the
  situation (PLs) → find the plan (PLp) → execute it (PLe)*. With PLs moved out, the MS family
  is purely social. Historical label CSVs keep the `MSe` code.
- **`src/adele/annotation/prompts.py` (+3 lines).** Two dimension-neutral judging rules — *demand
  is a property of the task* and *when in doubt assign the lower level* — moved out of rubric
  text into the shared prompt. **This affects v1 annotation too and needs sign-off.** It is
  coupled: dropping it means restoring two sentences to each of the four rubrics.
- **`.gitattributes` (+4 lines).** `*.csv` is LFS-tracked in this repo and the CFI LFS budget is
  exhausted, so the small human-readable QA label files are exempted from LFS.

---

## 3. Evidence

Twenty rounds, roughly 800 annotations, judges **haiku / sonnet / opus** only, always through
the repo's own `build_annotation_prompt`, always writing reasoning before any score. Data in
`labs/rubric-qa/`.

### 3.1 Paired old-vs-new, same tasks, same judges, same seeds

PLp on 8 pilot tasks (5 USACO divisions, 2 τ-bench, 1 AssistantBench), 3 judges × 3 seeds per
arm, 144 annotations:

| metric | old rubric | new rubric |
|---|---|---|
| Krippendorff α (ordinal) | 0.611 | **0.861** |
| levels actually used | 1–3 | **1–4** |
| per-judge SD | 0.40–0.69 | **0.85–1.15** |
| USACO medians Bronze→Platinum | 3, 2, 2, 2, 3 (**non-monotone**) | **3, 3, 4, 4, 4** |
| Spearman vs contest division | 0.15 | **0.66** |
| Platinum vs a τ-bench flight change | **same score** | 2 levels apart |

Under the old rubric Bronze was rated *harder* than two Platinums, and judges' stated reasons
cited the borrowed drivers verbatim: *"no multi-agent coordination → below Level 3"*.

### 3.2 The collinearity itself

Re-annotating the 12 HAL frames that produced the original finding:

| judge | arm | mean(PLe−PLp) | SD of that difference | independent frames |
|---|---|---|---|---|
| sonnet | old | +0.92 | 0.28 | 0 / 12 |
| opus | old | +1.08 | 0.28 | 0 / 12 |
| sonnet | new | **+0.17** | **0.69** | 5 / 12 |
| opus | new | **+0.42** | **0.64** | 5 / 12 |

The constant-offset signature is **gone**: the difference is now task-dependent rather than a
fixed intercept.

### 3.3 Discriminant validity — median profiles

| task | PLp | PLe | PLs | MSc |
|---|---|---|---|---|
| Find the winning line in a chess position | 3 | **1** | **0** | 0 |
| USACO Platinum problem (real, from the pilot) | **4** | 3 | **0** | 0 |
| Year-end ledger reconciliation by hand | low | **4** | 1 | 0 |
| Live database migration, no rollback | low | **5** | 2 | 0 |
| Intermittent unsignalled fault | 2 | 2 | **5** | 0 |
| Broker conflicting water rights | 3 | 2 | 2 | **5** |
| τ-bench retail conversation (real, from the pilot) | 2 | 1 | 2 | **2** |

High-on-one/low-on-another appears in **both directions for every pair**. The old set could not
produce a single such cell.

### 3.4 Agreement against pre-registered expectations

Our expected labels were written to `labs/rubric-qa/prereg_*.json` **before any judge ran**:
**9 of 12 cells exact, 12 of 12 within ±1** across three benchmark families; on the hardest real
task (USACO Platinum) all four dimensions matched exactly. In two cells the judges were arguably
right and we were wrong — e.g. τ-bench PLe, where they scored 1 because every tool call returns
an immediate success signal, following the rubric more exactly than our own expectation did.

### 3.5 The solver oracle (`labs/rivercross/`)

A controlled river-crossing testbed already in the repo carries an **exact BFS solver as a value
oracle**, so every judged state has a true remaining cost-to-go. This is the strongest ground
truth available anywhere in the project, and it produced the sharpest results — including a
failure.

**PLp.** Our rubric initially scored Spearman **0.497** against cost-to-go, barely above the
0.374 of the wording rivercross had replaced, with 39 of 43 states collapsed onto one level. Two
causes: our bottom rung was keyed on the plan being *provided* rather than on *no search
remaining*, so states one move from the goal had no home; and our Level 1 knowledge gate ("a
standard routine covers this") swallowed the whole puzzle genre. Both fixed — after which
Spearman is **0.857**, matching the purpose-built search-size rubric on its own testbed (0.855),
with an exact Level 0 partition (all twelve states scored 0 have true remaining distance 1, and
no others do).

**PLe.** Judges put 41 of 49 states at Level 1, reasoning that "illegal moves are rejected
immediately" — reading legality as feedback. Adding the exclusion to the preamble changed
nothing, because Level 1's own text said "or invalid actions are simply not accepted". Fixed at
the level; the modal level moved to 3 with the judge's reason "no feedback until goal", and the
eight states both rubrics score 0 are the same eight. Correlation with the oracle is ≈0 for our
rubric (−0.10) *and theirs* (−0.19, −0.23) — expected, because PLe measures the error regime,
not remaining work, and horizon is routed to Volume by design.

### 3.6 Traps

| trap | designed | outcome |
|---|---|---|
| PLp: 200-step protocol executed as written (length is VO) | 0 | held |
| PLe: chess line — plan-hard, execution-trivial | ≤1 | **failed 9/9, fixed**, now 15/15 |
| PLs: Sudoku / chess / fully specified statement (deduction ≠ observation) | 0 | 27/27 exact |
| MSc: read a poker opponent, never interact (that is MS) | ≤1 | held |
| MSc: persuasive newspaper column (that is CEe) | ≤1 | **failed 3/3, fixed**, now 1/1/1 |
| MSc: grave veterinary diagnosis to a trusting family (stakes ≠ resistance) | 3 | held |
| PLe: three final submissions, none graded until close (budgets) | 5 | held |
| PLe: deadline with per-step validation (must **not** inflate) | 1 | held |

---

## 4. Four failures worth reading

These produced the most useful fixes, and are kept in the record rather than tidied away.

**4.1 What counts as an "action".** A task reading *"find the winning line and write it down"*
was designed to score ≤1. Every judge scored 4, faithfully: chess calculation is a chain of
dependent internal steps where an early error invalidates the rest — exactly what Level 4
described. But if internal reasoning counts as execution, every hard reasoning task scores high
on *both* PLp and PLe, and the collinearity returns through the side door. Defining an action
*intentionally* (one plan step) rather than physically fixed it.

**4.2 Naming a boundary is not enforcing it.** MSc's preamble said the dimension is about
"steering an interaction, not composing its messages" — but no *level* required an exchange, so
a one-shot persuasive column slid into Level 3. Making interactivity a gate fixed it, and a
**held-out** case never mentioned in the rubric (writing a eulogy) also scored 1, so the gate
generalises rather than the anchor being memorised.

**4.3 A rubric validated for one framing is not validated for another.** PLp was built and
tested for *whole-task* annotation and compressed badly when scoring the demand *still remaining*
from a mid-trajectory state — the framing used by both the rivercross lab and the HAL trace
frames. Fixed once the decision was taken that one rubric serves both.

**4.4 The same shape three times.** All three of the above were preamble-only bindings. Rather
than wait for a fourth, we audited all four rubrics mechanically for the pattern. Seven clauses
were preamble-only; the five that could change a level are now bound at the level that uses
them, each with its anti-inflation half, and each tested (5/5). Two were deliberately left,
because neither can change a level and binding them would add text without adding constraint.

---

## 5. Is the format right?

**Yes on shape, with one honest exception.** All four carry v1's structure and level names
(None / Very low / Low / Intermediate / High / Very high), 3–5 concrete anchors per level, and
v1's scale-framing sentence ("The level of cognitive demands progresses from … to …"), which was
missing from all four until late and is the cheapest orientation cue a weak judge has. Anchors
are written to v1's concreteness standard: a picturable situation at instance level, with the
distinguishing detail stated.

The exception is **length**. Preambles now run PLs 173, PLp 187, MSc 248, **PLe 406** words,
against v1's range of 66 (MS) to 217 (CEe). PLe is genuinely out of family. That is the price of
four definitions no other rubric needs — action, feedback, transcription-vs-construction, and the
budget/deadline/branch routings — each traceable to a measured failure. It has been compressed
twice and further cutting risks losing a clause we have evidence for. **This is a real
reviewability cost and the team may reasonably ask for a different treatment** (a short preamble
plus a "definitions" note, if the format could carry one).

One structural observation for a future format decision: the `Critically, …` clauses are now
load-bearing everywhere, and if the rubric format ever became machine-readable, they would
deserve to be their own field rather than prose buried in a paragraph.

---

## 6. What remains

Ranked by where we would actually expect to find defects.

1. **Weak-judge robustness on PLp.** haiku reaches 0.647 against the oracle where sonnet reaches
   0.857 and rivercross's purpose-built rubric reaches 0.826. Their advantage is real and
   understood: numeric depth/breadth anchors let a weak judge *estimate* rather than decide a
   binary that requires solving the task first. Closing this means revisiting rule 4 of §2.1 —
   a design decision, not a tweak.
2. **MSc has no external ground truth of any kind.** It is validated only against items we
   designed ourselves, which is the weakest evidence in the set. No benchmark in the pilot
   exercises it above level 2.
3. **No human anchor.** The two-phase worksheet exists in `labs/hal-traces/worksheet/`; ~15 items
   would tell us whether judges track the intended construct or merely agree with each other.
4. **Separation on real traces is unproven.** The HAL set is one benchmark family in which
   planning and execution difficulty genuinely co-rise. `docs/agentic-open-questions.md` §1
   specifies the mixed-family battery that would settle it, and why the current four families
   structurally cannot.
5. **Two demands are unowned:** open-ended goals with no requester (probably metacognition), and
   prospective memory (probably decomposes into MMe + PLe). `docs/agentic-open-questions.md` §2
   gives one minimal-pair experiment that settles both. **No v1 change is proposed for either.**
6. **Provenance risk.** The rivercross validation in §3.5 ran against `labs/rivercross` as of
   commit `2f42e9c`. A refactor of that lab is in flight on a fork
   (`mingqianzhou123:rivercross-1b-refactor`), unreviewed here; if it changes the frames, prompt
   scaffolds or ground truth, the numbers in §3.5 should be re-run — the harness is a single
   call per dimension.

---

## 7. Where things are

| path | what |
|---|---|
| `src/adele/rubrics/data_v2/Paolo_Pablo/{PLp,PLe,PLs,MSc}.txt` | the rubrics |
| `src/adele/rubrics/data_v2/MANIFEST.tsv` | provenance and sha256; all rows verify |
| `labs/rubric-qa/README.md` | round-by-round lab notebook, 20 rounds |
| `labs/rubric-qa/*.csv`, `prereg_*.json` | every label, and the pre-registrations |
| `docs/agentic-open-questions.md` | the two experiments that settle what is open |
| commit history | one decision per commit, with its failure, alternatives and verification |

`data_v1` is untouched. Marko's memory triad is untouched — an early draft of our audit wrongly
claimed it was collinear on the basis of shared example text; that claim was **retracted**, since
shared Level 0 anchors are the null case and its matched-content contrasts are good design.
