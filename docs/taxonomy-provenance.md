# Provenance: the four agentic rubrics against the cognitive-ability taxonomy

Audited against *Taxonomies of Cognitive Abilities — State of the Art & ADeLe*, §9–§12.
This closes desideratum 1, which until now had no evidence of any kind.

## What the artifact asks of a dimension

It is explicit that **dissociation is a hypothesis generator, not the verdict**: the task-level
echo of a lesion crossover is only an observational separability check, and "two demands can
be correlated yet each add predictive resolution." A collinear pair has three readings, and
only the first warrants a merge:

1. genuinely one ability → merge;
2. battery-sampling gap → keep, and build the separating task;
3. **suboptimal demand-level definitions that make distinct abilities co-vary → rewrite the
   rubric, don't merge.**

Reading 3 is the one this branch has been executing, mostly without knowing the artifact
named it.

## Its verdict on our stream, and what we did

§10 assesses "Stream B — Paolo_Pablo" and finds one structural problem:

> `PLp`, `PLe` and `MSe` are all keyed to the same difficulty drivers — temporal horizon,
> number of agents, open-endedness, environment dynamics […] The factors, not the abilities,
> are doing the work.

with two prescriptions. Both are now done, and measured:

| artifact prescription | what we did | evidence |
|---|---|---|
| "`PLp` vs `PLe` only dissociate if you re-key them to different factors (plan-search vs execution/feedback)" | `PLp` is keyed to plan-search — depth, branching, sparsity of successful paths. `PLe` is keyed to execution — **since r38–r39, specifically to the availability and difficulty of progress and correctness checking; irreversibility and impact of failure were removed as placement keys** (see the correction note below) | battery-v1: `PLp`>>`PLe` [3,3,4,3] and `PLe`>>`PLp` [4,5,4,5]; re-measured r42: diagonal 3/3 both ways, r44 regression 11/11 exact |
| "`MSe` is really an environment-complexity descriptor mis-filed under MS / social cognition — re-file it" | renamed `MSe` → **`PLs`**, moved into the planning/environment group, construct restated as the world's task-relevant state | battery-v1: `PLs`>>`MSc` [4,4,5,4], `MSc`>>`PLs` [4,5,4,4] |
| "the single highest-leverage fix: factor out the shared agentic difficulty drivers into the extraneous block alongside AT/VO/UG" | **added this commit** — every one of the four now states in its boundaries paragraph that horizon, agent count, environment change and open-endedness are difficulty factors in their own right and do not raise it by themselves | pending re-measurement |
| §11 KEEP: "mind-modelling MS→MSm" | done (`c5130dc`) | — |
| §11 KEEP: `MSc` "keep only the active-strategic residue not already in CEe/MSm" | exactly the construct: `MSc` routes expression to CEe and inference to MSm and scores only the steering | r31: `MSc` scores 0 on every inference-only item; r30 C-set 4/4 against its own drivers |
| §11 RECLASSIFY: `ECc` self-control → propensity | not in the active set, and `MSc` states that mastering one's own impulses "is not scored here, or anywhere in this set: it is a disposition of the solver" | — |

§9 also records that the v2 social split is endorsed on the literature: *"MS ✓ strong — ToM
dissociates (autism, TPJ). v2 split (MSm/MSe/MSc) is well-motivated."*

## What the artifact flags that we have NOT tested

- **`MMp` (procedural memory) overlaps `PLe` (execution)** — §10 watch-out. Never measured, and
  it was not on the pre-PR audit's list either. A routing clause was added to `PLe` this
  commit ("a routine run off by rote, with no monitoring because none is needed, is Procedural
  Memory") but the clause is unmeasured, which by this lab's own repeated finding means it may
  not bind.
- **`MMs` overlaps `AS`**, and **`MMe` vs the `KN*` knowledge dimensions** — both in the memory
  stream, not ours, but they belong in the same conversation.
- **A causal / intuitive-physics dimension** is proposed as an addition. Out of scope here.

## The gap the artifact names that we still cannot close

Its decisive test is not dissociation but **incremental prediction**: merge only if "dropping
the distinction does not degrade the demand-based assessor's instance-level prediction," and
"this makes ADeLe's own predictive goal, not a borrowed lesion criterion, the final arbiter."

Every measurement in 35 rounds is internal — does the rubric do what its text says, and do the
dimensions separate on designed items. **None of it is criterion validity.** That needs solver
outcomes joined to demand labels, which the current data cannot supply (recorded since round
23.1). It is the single largest outstanding claim, and it is a data problem rather than a
rubric problem.


---

# Correction notice (2026-08-22)

Two entries above describe dimensions that have since changed underneath them. The rows are
annotated rather than rewritten, so the record of what was claimed when stays legible.

- **`PLe`** is no longer keyed to "feedback density, silent propagation, irreversibility."
  Rounds 38–39 re-anchored it to *the availability and difficulty of progress and correctness
  checking*, and explicitly removed impact of failure and irreversibility as placement keys:
  a step whose correctness is easy to establish makes a low demand however consequential it
  is. The change was forced by measurement — an unamendable-but-checklist-easy regulatory
  filing scored 5 under the old text and 2 under the new, against a human anchor of 2.
- **`PLs`** above refers to the deleted `MSe`→`PLs` dimension, not to the current one.

# `PLs` "Simulating" — provenance (2026-08-20, entered 2026-08-22)

This dimension post-dates the artifact audited above, so it carries no §9–§12 verdict. Its
grounding is stated here on its own terms.

## The ability it is drawn from

`PLs` is keyed to the capacity mammals evolved for running a situation forward internally —
prospection: taking a represented state of affairs and playing it out under its own dynamics
to find out what would happen, without acting. It is among the better-attested capacities in
comparative cognition, and the reason it is a plausible dimension rather than a task feature
is that it appears as a *mechanism* across otherwise unrelated behaviours — anticipating a
physical outcome, projecting how a scene will develop, evaluating a course before taking it —
and is studied under names that all describe the same operation: prospection, episodic future
thinking, forward models in motor control, cognitive maps and the forward sweeps observed at
choice points in rodent navigation.

Two consequences of that grounding are written into the rubric, and both are load-bearing:

1. **What is simulated is what the world does, not what to do about it.** Prospection is
   recruited by planning but is not planning: choosing among one's own actions is search, and
   a candidate action enters this dimension only as a stipulated change whose consequences must
   be traced. This is a one-directional dependence — planning may run on an externally supplied
   world model (the rules of chess are given; no one simulates them into existence) while
   simulating requires no planning at all.
2. **The demand scales with how much interacting change must be tracked, at the precision the
   answer requires** — not with how specialised the governing regularities are, nor with how
   hard the current state is to perceive. Those belong to knowledge and perception dimensions
   respectively.

## Relation to what the artifact proposed

§10 of the artifact proposes "a causal / intuitive-physics dimension" as an addition and marks
it out of scope. `PLs` arguably answers that proposal, though in a broader form: the rubric is
explicitly modality-general (physical, biological, mechanical, social or economic situations
all propagate alike), where an intuitive-physics dimension would have been narrower. Whether
that generality is right is an empirical question this project has not settled.

## Scope: what `PLs` measures, and what its zeros mean

The demand is scored on what a task asks for. Where a situation must be run forward only in
order to settle what to do, that running belongs with the choice it serves, and the task
scores low here however much foreseeing its solver would in fact do. This was not a design
decision taken up front; it was measured in **r47**, which held three systems fixed and asked
each of them two ways. A matplotlib limit-conditioning path scored 1 asked as "fix it" and 3
asked as "what happens"; a pairing process scored 0 asked as "compute the maximum matching"
and 4 asked as "how many remain unpaired at the fixed point". The clause was then written
into the rubric and re-measured in r51, where the do-arm stayed at 0 and the predict-arm at 4.

**Consequence for reading `PLs` numbers.** On the agentic pilot the dimension scores 0 on 12
of 20 instances and never exceeds 1 (**r46**), because SWE-bench, AssistantBench, USACO and
τ-bench ask an agent to fix code, look something up, devise an algorithm or serve a customer.
None asks what a situation will do. Those zeros are a statement about instance coverage, not
about the world models of the systems being evaluated, and they should never be quoted as the
latter. Instances whose deliverable is a prediction reach 3 and 4 immediately.

Whether the narrow scope is the right one is a construct decision the team has not taken. If
instrumental simulation should be scored, the scope clause is the thing to revisit, and the
cost is a re-key of the driver plus full re-validation rather than a patch.

## Evidence, and its limits

- **r51** (19 items, current v7.2 wording): 19/19 exact against sealed predictions, α 0.992.
  All three fusion falsifiers held, the precision contrast separated by three levels on one
  situation, the coupling-versus-chain boundary separated, and the planning, mind-modelling
  and execution carves held. **r52**: family diagonal 8/9 with no off-diagonal leak. Note that
  the chess co-load reported in r42 disappeared once the scope clause was explicit, moving 4
  to 0, which is a behaviour change worth the team's attention rather than a tidy-up.
- **r40** (the first battery run, superseded wording): the fused driver survived all three of
  its designed falsifiers. Precision does not act as an independent axis — exact-answer items with
  no interaction stayed at 2 — and the precision contrast separated by three levels on one and
  the same situation (coarse question 2, fine question 5). Routing carves against planning,
  mind-modelling and execution all held. α 0.971.
- **r41**: the L0 absent-referent clause binds in both directions; one pre-registered rule
  failed on a mis-built probe, so the L2/L3 coupling boundary is open.
- **r42** (family discrimination): `PLs`-loaded items score ≤1 on `PLp` and `PLe`; the single
  co-load, a chess plan, is a property of chess.
- **Not established:** no human has ever labelled a `PLs` item. Every anchor in r40–r42 is
  construction-side. This is the dimension's weakest evidential point and is not closed by any
  round above.
- **Desideratum 9** is open for `PLs` exactly as for the rest of the stream: no criterion
  validity, for the same data reason recorded at the end of this document.
