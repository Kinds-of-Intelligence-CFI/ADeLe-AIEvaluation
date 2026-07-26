# Two open questions, and the measurements that would settle them

Companion to `docs/agentic-rubric-redesign.md`. Both questions are currently being
argued from design intuition. Both can be turned into cheap measurements.

---

## 1. A battery that can actually show separation

### Why the current one cannot

The four families in `benchmarks.py` are structurally unable to demonstrate
discriminant validity, whatever the rubrics say. Observed ranges so far:

| family | PLp | PLe | PLs | MSc |
|---|---|---|---|---|
| USACO | 3–4 | 3 | **0 always** | **0 always** |
| SWE-bench | 2–3 | 2–3 | 2–3 | **0 always** |
| AssistantBench | 1 | 1–2 | 2 | **0 always** |
| tau-bench | 2 | 1–2 | 2 | 2 |

Every family is single-agent and fully specified, so MSc is pinned near 0 and PLs
cannot exceed 3. No family reaches 5 on anything. A battery in which two dimensions
are constants cannot produce "X high while Y low, both ways" — and a battery whose
labels cluster on one value cannot produce a high Krippendorff α, because α divides
observed disagreement by the disagreement expected from the marginal distribution.

**This is a sampling problem, not a rubric problem.** The fix is to add families that
push the dimensions currently pinned.

### The cheap part

Demand annotation needs **only the task statement** — not an agent, not a rollout, not
a scoring harness. Adding a family to the *annotation* battery therefore costs a loader
that returns task text, and nothing else. Running agents on these benchmarks is a
separate, much larger decision that this validation does not require.

### Candidate families, chosen to max out one pinned dimension each

| target | candidate families | why it moves that dimension |
|---|---|---|
| **PLs 4–5** | ALFWorld, TextWorld / interactive fiction, NetHack-style roguelikes | the state is hidden and must be explored; it changes while the agent acts; roguelikes add unsignalled change → the top rung |
| **PLs 3–4 + PLe 4** | WebArena, OSWorld / computer-use suites | site or system state must be discovered, and some operations are hard to undo |
| **MSc 3–5** | SOTOPIA (goal-driven social interaction), bargaining corpora (e.g. CraigslistBargain, multi-issue deal-making), multi-party negotiation or social-deduction settings | parties hold conflicting goals and respond strategically — the only way to reach MSc 4–5 |
| **PLp 5** | research-level mathematics or open-problem sets | no established procedure; the decomposition must be invented |
| **PLe 5** | any task family with irreversible operations (destructive system actions, one-shot submissions) | errors cannot be undone, only prevented |

Availability, licensing and prompt format need checking before committing to any of
these; the point is the *shape* of the battery, not these exact names.

### Design targets, and one warning

A validation battery should be built to a specification, not sampled for convenience:

- every dimension has at least three tasks at 0–1 and at least three at 4–5;
- at least four task pairs where dimension A is high and B is low, **and** the reverse,
  for each of the six dimension pairs;
- families deliberately unbalanced across dimensions, so profiles differ in shape.

**Do not optimise α.** α rises mechanically as spread rises, so it can be inflated by
adding easy extremes without any improvement in the rubric. The primary criteria stay:
(i) **separation** — high-on-one/low-on-other, both directions; (ii) **incremental
validity** — do the labels predict solver success better together than any subset;
(iii) agreement, reported **with** the level distribution beside it.

---

## 2. Two demands that no dimension currently owns

> **Scope: no change to v1 is proposed, here or anywhere in this work.** Naming a dimension as
> the owner of a demand is not the same as editing that dimension. PLp already names Volume (VO)
> as the owner of execution length and `VO.txt` was never touched; the same applies to every v1
> code referenced below. If one of these routings turned out not to be covered by the v1 text,
> that would be a question for the v1 owners and explicitly outside this branch — it would not
> be a reason to edit v1 from here.

The team's standard for *removing* a dimension is predictive validity rather than a
double-dissociation gate. The symmetric standard should govern *additions*: **a
phenomenon earns a dimension only if labelling it improves prediction of solver success
over the existing set.** Neither phenomenon below has been tested against that bar, and
neither should get a code until it has.

Both can be settled by the same experiment, which is small.

### The experiment: minimal pairs

For each phenomenon, build ~8 task pairs that are identical except for the phenomenon —
same content, same length, same domain. Annotate every task on all existing dimensions
(v2 agentic plus the relevant v1 dimensions), 3 judges.

- If some existing dimension's labels **move** between members of a pair, the phenomenon
  is already owned by that dimension. Record where, and if the rubric text does not make
  it obvious, add one routing clause.
- If **no** dimension moves, yet reviewers agree the two tasks differ in demand, that is
  evidence of a genuine gap — and the follow-up is the incremental-validity test, not a
  new code by assertion.

### 2a. Open-ended goals with no requester

Most of this is already routed: inferring what an under-specified *request* asks for is
the requester's intent → **MSc**; success that is harder to verify once intent is fixed
→ **PLp** (sparsity) and **PLe** (absence of feedback). The residue is the case with no
requester at all — "make something beautiful" — where the solver must supply the
evaluation criteria.

*Prior:* this looks metacognitive rather than agentic. Judging one's own output against
self-set standards is what the v1 metacognition block (MCt / MCu) describes. Recommended
default: route to metacognition, do not create a code.

*Minimal pairs:* the same deliverable specified two ways — "write a 500-word summary
covering points A, B and C" versus "write something useful about this document".

*Owner:* whoever owns the MC block; not the agentic stream. Note this is the rarer case in agentic
benchmarks — every task in the current pilot has a requester — so it can reasonably be left open.

### 2b. Prospective memory

"Act at the right moment" — noticing that a stored intention has become due while
attention is elsewhere. The cognitive literature treats this as having two components,
and the taxonomy should follow that split rather than invent a third thing:

- **retrospective component** — holding the content of the intention → memory dimensions
  (MMe), Marko's stream;
- **prospective component** — noticing the cue while occupied with something else →
  **PLe**, whose Level 3 already asks which open subtask to advance next.

Both halves are covered by rubrics that already exist, so the expected outcome of the minimal-pair
test is that MMe and PLe labels move and nothing needs writing at all.

*Prior:* it decomposes; no new code needed. But the memory half is Marko's call, so the
proposal should go to him with the pair data rather than being settled here.

*Minimal pairs:* the same interaction with and without a delayed conditional obligation
— tau-bench's "after the third agent message, also ask about other flights" is exactly
this, and its counterfactual is the same task without the timed side-request.

*Owner:* Marko for the MM half; agentic stream for the PLe half.

---

## Recommended order

1. Build the annotation-only loaders for two families first — one MSc-high, one PLs-high.
   These two dimensions are the ones currently pinned, so they buy the most evidence.
2. Re-run the separation and agreement analysis on the enlarged battery, reporting α with
   the distribution.
3. Run the minimal-pair experiment for both open routings (~16 pairs total).
4. Only then decide the routings, and only then consider a PR that touches other streams.
