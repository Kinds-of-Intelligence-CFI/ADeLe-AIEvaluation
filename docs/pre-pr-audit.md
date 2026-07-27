# Pre-PR audit of the four agentic rubrics

Run after round 26, before opening the PR. Two independent passes with no memory of the
26 rounds: a **construct-overlap audit** of all four v2 rubrics against all 18 v1 rubrics
(72 pairs), and an **adversarial read** of the four rubrics on their own terms.

Findings are triaged by what they cost and, where we already have data, checked against it.
That check matters: about a third of the adversarial pass's confident claims are **false
against measurements we already hold**, which is the clearest argument yet for the
measure-don't-assume discipline.

---

## 1. Blocking — must be resolved before the PR

### 1.1 `MSm` does not exist

> **RESOLVED 2026-07-27.** Decided by Pablo: change `MS` to `MSm`. `MSm` now exists as an
> active v2 dimension — `rubrics/data_v2/v1/MSm.txt`, carrying v1 `MS`'s text unchanged — so
> the routing resolves and the pipeline has a rubric under the code. v1 is untouched:
> `data_v1/MS.txt`, `DEMAND_ORDER` and the published `MS` label column all stay as they are.
> See `docs/proposal-MS-to-MSm.md` for the two sub-decisions deliberately left open.
> The finding as originally written follows.

All four rubrics route mind-reading demand to "Mind Modelling (MSm)". **There is no `MSm`
file anywhere in the repository.** The shipped mind rubric is v1 `MS.txt` ("Mind Modelling
and Social Cognition"); the v2 manifest contains `PLp PLe PLs MSc MMe MMp MMs` and no `MSm`.

The reference was introduced deliberately (commit `b355336`, "route to MSm, not MS") because
the taxonomy plans for `MS` to become `MSm` when `MSc` splits off. But until that file exists,
a judge reading "assessed by Mind Modelling (MSm)" cannot resolve the routing, and the
annotation pipeline has no rubric under that code. Four files, five occurrences.

**Needs a decision:** ship `MSm`, point back to `MS`, or state in the PR that these four
rubrics land together with the `MS` split and are not annotatable before it.

Related and smaller: `PLe` and `PLs` route to "the memory dimensions" — which **do** exist
(`MMe`, `MMp`, `MMs` in `Marko/`), so this reference resolves. But it is the only routing
target in the set named without a code, while every other one carries one. Name them.

---

## 2. The collinearity claim has a hole: 13 of 18 v1 dimensions were never tested

This is the most consequential finding, because eliminating measured collinearity is the
PR's headline claim. Routing was tested against `AS`, `SNs`, `MS`, `CEe` and `VO`. The other
thirteen — including the entire `MC` metacognition family — were never checked. Two of them
collide at high severity.

### 2.1 `PLp` × `MCr` (Identifying Relevant Information) — HIGH

`MCr` L4 scores *"identifying crucial unstated information **or approaches** needed for
solution while considering **multiple possible solution paths** and their implications"*;
L5 adds *"crucial information about **solution approaches** and constraints is left unstated
and must be discovered"*.

That is PLp's quantity, in `MCr`'s published text. `PLp`'s own L4 example — a contest problem
for which no standard technique applies — scores 4 on `PLp` and 4 on `MCr` **for the same
reason**: the approach is not given and the space of approaches must be searched.

`MCr`'s distractor-filtering branch is clean; only its second branch collides. A routing
clause on our side can disclaim the *information* half but not the *approach* half, because
`MCr` claims it explicitly. **This one cannot be fixed from the v2 side alone** and needs a
framework-level decision.

### 2.2 `PLs` × `MCu` (Calibrating Knowns and Unknowns) — HIGH

Four of `MCu`'s L4/L5 examples — differential diagnosis, a dataset with unknown sampling
bias, poker after the flop, crisis investing — score high *because the relevant world state
is hidden or evolves unobserved*, which is exactly and only what `PLs` scores. A routing
clause can separate the annotator's *judgment about their own certainty* from *what it takes
to establish the state*, but the residual correlation is structural: both are driven by
hiddenness.

### 2.3 Medium, and each fixable with one clause on our side

| pair | collision | fix |
|---|---|---|
| `PLp` × `AT` | both pivot on whether a known procedure exists; `PLp` L5 synthesis example is `AT` 5 by construction | clause at `PLp` L4 |
| `PLs` × `CEc` | `PLs`'s L2/L3 directness test *is* `CEc`'s explicit/implicit-meaning boundary | clause at `PLs` L3 |
| `PLs` × `AS` | the earlier `AS` test covered the *volume* axis; the **change** axis is unrouted, and `AS` L4/L5 claim "changing conditions" | clause at `PLs` L4 |
| `PLe` × `MCt` | both score self-verification with no external checker | extend the deliberation carve-out |
| `PLp` × `CL` | "find the key insight" is scored by both | clause at `PLp` L4 |
| `PLp` × `QLl` | both driven by how strongly decisions/constraints interact | clause at `PLp` L3 |
| `MSc` × `MS` | `MS`'s own L5 example is a multi-stakeholder negotiation — the same item as `MSc` L5 | restate the routing inside `MSc` L5 |

**Clean against all four (9 of 18):** `CEe`, `VO`, `QLq`, `SNs`, `KNa`, `KNc`, `KNf`, `KNn`,
`KNs`.

---

## 3. Real defects in the rubrics themselves

### 3.1 `PLe` L5 mis-routes the central agentic case — HIGH

L5 reads *"**in addition to** sparse feedback and silent propagation, some actions are
irreversible"*. Irreversibility is a third conjunct, not a sufficient condition. So:

> Book the cheapest non-refundable flight matching these constraints. Send this message to
> the whole company. Execute this payment.

Irreversible, confirmed instantly, nothing propagates. L5 excludes it (feedback is not
sparse), L4 excludes it (*"feedback is equally sparse"*), and L1 says *"an error is caught and
corrected on the spot"* — which is false, it cannot be corrected at all. The most
consequential property an agentic action can have currently scores 1.

**Fix:** make irreversibility sufficient — *"a consequential irreversible step places a task
here on its own, whether or not feedback is sparse."*

### 3.2 `PLe`'s feedback exclusion contradicts its own L1 anchor — HIGH

The preamble excludes *"not mere observation of the new state"*. L1's anchor is *"Cook from a
recipe in which each step's outcome makes success immediately apparent before moving on"* —
which is observation of the new state. Taken literally the exclusion empties L1 and L2, since
in most environments the success signal *is* the new state; ignored, judges fall back on the
folk meaning. Two judges, two scales.

**Fix:** the intent is interpretive distance, not observation. *"…not an observation from
which success still has to be worked out"* — which matches L1's anchor and mirrors `PLs`'s
directness test, which gets the same idea right.

### 3.3 `PLe`'s action and feedback definitions are preamble-only, and three levels count them

L2 is *"roughly once every two to ten actions"*, L3 is *"stretches of tens of actions"*. Both
terms are defined only in the 405-word preamble — the action definition as three conjoined
conditions, the feedback definition as a 76-word sentence built entirely from exclusions.
Neither is restated in any level that uses it. A mis-grained count moves a task two levels.
This is the highest-leverage unbound preamble clause left in the set.

### 3.4 `PLp` L1's ordering clause leaves rigid standard procedures homeless

L1 requires *"any reasonable order succeeds"*. Compute a sample standard deviation; run a
titration; do long division. One standard routine, forced order, nothing to search. L1
excludes it by that clause, L2 excludes it (*"the steps do not constrain one another"* is
false), L3 excludes it (there are no alternatives to compare). The clause presupposes there
are ordering *choices*; the condition it wants — *"a single standard routine covers the whole
task directly"* — already does the work.

### 3.5 Missing brakes and aggregation rules

`Critically…` floors are present at `PLp` L0–L4, `PLe` L1–L3, `PLs` L0/L2/L3, `MSc` L1–L4 —
and **absent at the top of every scale**, which is exactly where upward drift happens and
where round 25 measured the softest boundary. And only `PLp` states an aggregation rule
(*"the hardest plan-finding the task still requires"*); `PLe`, `PLs` and `MSc` say nothing
about a task showing features of two levels.

---

## 4. A design decision, not a defect: `MSc` is near-binary on real benchmarks

Every level ≥2 requires a live exchange, and the clause that enforces it is correctly bound
at L1. But essentially every text benchmark item is one prompt in, one response out, so
"write a message persuading your landlord…" is L1 however hard it is. The header already
concedes the limitation — `validated: rounds 12-21 (designed items only)`.

Either add a second route into L2–L5 for *represented* exchanges (the task supplies a
transcript and the solver produces the next move; or the message must pre-empt the objections
it will provoke), or ship `MSc` knowing it is close to a binary flag on current batteries.
Not a wording fix — it changes what the dimension measures.

---

## 5. Claims the adversarial pass got wrong, checked against round 25

Recorded because it calibrates how much weight to give an unmeasured read.

| claim | measured |
|---|---|
| `PLp` L2's examples enumerate their own steps, so judges will score them L0 | webpage **2/2/2**, data analysis **2/2/2** — 3/3 clean |
| `PLp` L2's day-trip has interacting choices and reads as L3 | **2/2/2** — 3/3 clean |
| `PLs` L2's codebase example is L3 by L2's own directness test | **2/2/2** — 3/3 clean |
| `PLp` L0's real-time translation example reads as L2–L4 | **0/0/0** — 3/3 clean |
| `PLe` L3's summarisation example splits 0 vs 3 | **2/3/3** — partially supported |

The logical arguments are reasonable in every case; the judges simply do not make those
errors. One claim in five survived contact with the data.

---

## 6. Accepted limitations to state in the PR rather than fix

- **House style diverges from v1 — but less than this audit first claimed.** Two of the
  numbers below were re-measured directly on 2026-07-27 and were **wrong**; they are corrected
  here in place rather than quietly edited, because they were the basis for calling the
  divergence "measurable" and they overstated it.

  | claim as first written | re-measured |
  |---|---|
  | v1 level text ~30 words average | **64** (mean of per-rubric means; `MCr` 209, `CEe` 143, `CEc` 138, `AT` 139) — so v2's 69–94 sits *inside* v1's range, not above it |
  | `Critically` appears 0 times in all of v1 | **1** — `MS.txt` L1. Round 23.2 had this right; §6 contradicted it |

  What survives, and it is the real finding: **preamble mass**. v1's preambles run 47–217
  words (median 93). Ours are `PLp` 187 and `PLs` 198 — inside that range — against `MSc` 268
  and `PLe` **432**, which is twice v1's largest. Parenthetical dimension codes appear 0 times
  in all 19 v1 files and 12 times across our 4, but those are load-bearing: they are the
  mechanism that fixes the collinearity (round 23.2), and removing them reverts the fix.

  So the compression pass, if it is run, should target `PLe`'s and `MSc`'s preambles and
  nothing else — and it must be gated on the sentinel battery reproducing, since round 10
  compressed `PLe` 481→384 with no drift and round 28 showed what an unverified "improvement"
  costs.

- **Examples are shorter than v1's**, not longer: v2 averages 19–26 words against v1's 16–57,
  with v1's closest analogues (`CL` 50, `MCr` 57, `QLl` 42) far richer. Round 25 pushed ours
  toward naming the discriminator tersely; defensible, but it is a divergence.
- **Three of four L5s are probably empty on real suites.** `PLs` L5 is the exception.
- **`PLs` ≥ 4 fires on any task with an exogenously changing world** (round 26, §26.4).

---

## 7. What this means for the PR

The four rubrics are in good shape on everything that has been measured: 23/24 on the round-26
stress battery, 92% example placement, the rivercross oracle, and the collinearity signature
eliminated *within the tested set*. What this audit exposes is not a flaw in the work done but
the **edge of it** — the routing was never tested against two-thirds of v1, and the one
dimension it collides with hardest is the one nobody thought to check.

Recommended order:

1. Decide `MSm` — blocking.
2. **Round 27: measure the seven new overlaps**, `MCr` and `MCu` first. The PR's headline
   claim depends on it, and a routing clause written without measurement is exactly the kind
   of thing this project has repeatedly found not to bind.
3. Apply §3's defects as one batch, then re-run rounds 25 and 26 as regression.
4. Put `MSc`'s binary problem to the team as a design decision.
5. Open the PR as a draft once 1 and 2 are done; 3 can land in review.
