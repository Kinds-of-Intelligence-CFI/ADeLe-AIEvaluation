# `PLs` × `MCu`: a measured overlap that cannot be fixed from the v2 side

> The `labs/rubric-qa/...` paths cited below are on the `rubrics/v2-lab-record` branch, not in this PR. See `docs/lab-record.md`.


*For discussion. Nothing in this note proposes a change to `data_v1`; it asks the v1 owners a
question that only they can answer.*

## The claim, and why we tested it

The pre-PR audit flagged `PLs` (situational and environmental understanding) against `MCu`
(calibrating knowns and unknowns) at HIGH severity: four of `MCu`'s own L4/L5 examples —
differential diagnosis, a dataset with unknown sampling bias, poker after the flop, crisis
investing — score high *because the relevant world state is hidden*, which is what `PLs`
scores. The audit's verdict was that the residual correlation is **structural**: both are
driven by hiddenness.

That was an argument from reading the two rubrics. Round 33 measured it, with items built to
separate the pair in each direction.

## What we found: the overlap is real, and it is one-directional

```
  item                                                          PLs   MCu
  complete record of 1000 coin tosses; nothing hidden.
  state how confident anyone could be about the next toss         0     3
  a published dataset with its full sampling protocol; say
  which conclusions it supports and how sure one can be           0     4

  find the fire exit in an unfamiliar building while staff
  close corridors as you move                                     4     4
  operate a valve network whose settings are not displayed
  and change when other operators act                             5     4
```

`MCu` separates cleanly: where the world is fully observable and the question is about the
reliability of one's own judgement, `MCu` fires and `PLs` is silent. That direction is fine.

`PLs` **cannot** separate. On tasks that are pure exploration of hidden, shifting state, with
no calibration asked for at all, `MCu` still scores 4. It is riding on hiddenness.

## Why we cannot fix it here

`PLs` is not the dimension misbehaving — it scores those items correctly. No clause we can
write in `PLs` prevents `MCu` from firing. The fix, if there is one, has to be a scoping
clause on `MCu`'s side, and `data_v1` is out of scope for this branch by the standing rule
that naming a dimension as the owner of a demand is not the same as editing that dimension.

## What it costs in practice

The asymmetry bounds the damage. Demand profiles for agentic tasks will **over-report
metacognitive calibration** — any task with hidden or changing world state carries an `MCu`
score it may not have earned. The reverse does not happen: `PLs` does not inflate on
calibration-heavy tasks.

## Three ways to close it, and what each needs

1. **Leave both, state the limitation.** Defensible on the taxonomy artifact's own position:
   collinearity is not itself a defect, and two correlated demands can each add predictive
   resolution — the psychometric tradition deliberately keeps correlated narrow abilities for
   exactly that reason. Costs nothing; the over-report stays.
2. **Scope `MCu` on the v1 side.** One clause distinguishing *uncertainty about the world*
   (→ `PLs`) from *uncertainty about the reliability of one's own judgement* (→ `MCu`). This
   is the real fix and it is the v1 owners' call. It would need measuring afterwards — this
   lab has now had two carve-outs that were correct in substance and still failed to bind.
3. **Merge them.** The artifact is explicit that this is only justified if dropping the
   distinction does not degrade the demand-based assessor's instance-level prediction. **We
   cannot run that test** — it needs solver outcomes joined to demand labels, which the
   current data does not supply.

## Recommendation

Option 1 for the PR, with the numbers above stated plainly, and option 2 raised with the v1
owners as a separate question. Option 3 should not be decided until criterion data exists,
because the artifact's own decision rule makes prediction the arbiter and we have no way to
consult it.

One caveat on our own evidence: `MCu` was tested against `PLs` only. The audit lists nine v1
dimensions as clean against all four of ours and eleven as untested. `MCu` is the pair we had
most reason to worry about, and the worry was justified — which is some reason to think the
remaining eleven deserve the same treatment rather than the benefit of the doubt.

Data: `labs/rubric-qa/r33/`.
