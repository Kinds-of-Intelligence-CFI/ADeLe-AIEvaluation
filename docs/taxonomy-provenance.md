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
| "`PLp` vs `PLe` only dissociate if you re-key them to different factors (plan-search vs execution/feedback)" | `PLp` is keyed to plan-search — depth, branching, sparsity of successful paths. `PLe` is keyed to execution — feedback density, silent propagation, irreversibility | battery-v1: `PLp`>>`PLe` [3,3,4,3] and `PLe`>>`PLp` [4,5,4,5] |
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
