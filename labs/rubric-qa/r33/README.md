# Round 33 — the two HIGH collinearity pairs, and the N/C head-to-head

Two jobs. Both were the audit's own recommended step 2, and the head-to-head had been
pre-registered since round 30 but never run.

---

## Part 1 — collinearity (audit §2.1, §2.2)

12 items: for each pair, two built to favour the v1 dimension, two the v2 one, plus the
audit's own collision case and two anchors. All four rubrics scored all twelve.

### `PLp` × `MCr` — real, but far narrower than stated

```
  item  built to favour   PLp  MCr   separates?
  C01   MCr                 0    2    no      <- my item is bad, see below
  C02   MCr                 1    2    no      <- same
  C03   PLp                 4    0    YES
  C04   PLp                 4    0    YES
  C05   audit's collision   4    4    both >= 4: YES
```

`PLp` fires alone, decisively, where the approach must be invented and nothing is hidden.
The audit's collision case does collide. So the overlap is **confined to tasks where the
solution approach itself must be discovered** — not, as §2.1 frames it, PLp's whole
quantity sitting inside MCr's text.

**My two MCr-favouring items are badly designed and should not be counted.** Both hand the
solver a checklist, and MCr's own text scores a supplied procedure low. They test nothing.
The MCr-alone direction is therefore still untested.

The audit's conclusion stands on the part that was tested: a routing clause on our side
cannot disclaim the approach half, because `MCr` L4/L5 claim it explicitly. This is a
framework decision — but now with a measured scope, and the scope is one item in five.

### `PLs` × `MCu` — confirmed, and structural, exactly as the audit said

```
  item  built to favour   PLs  MCu   separates?
  C06   MCu                 0    3    YES
  C07   MCu                 0    4    YES
  C08   PLs                 4    4    no
  C09   PLs                 5    4    no
```

The asymmetry is the finding. `MCu` fires alone cleanly where the world is fully
observable and the judgement is about one's own certainty. `PLs` **cannot** fire alone:
on tasks that are pure exploration of hidden, shifting state with no calibration asked
for — find the fire exit while corridors close; operate a valve network whose settings
are hidden and change — `MCu` still scores 4.

That is not `PLs` being wrong. It is `MCu` riding on hiddenness, which is what §2.2
predicted in those words. **It cannot be fixed from the v2 side**: no clause in `PLs`
stops `MCu` firing, and `data_v1` is out of scope for this branch. It belongs in the PR
as a measured limitation.

---

## Part 2 — the head-to-head

### C-set: each arm judged against its own stated drivers — the new arm wins 4/4 to 3/4

```
  contrast                       old arm                     new arm
  S1->S2  stakes rise, willing   1->4  predicts rise    OK    3->3  predicts no change  OK
  S3->S4  stakes rise, willing   1->4  predicts rise    OK    3->3  predicts no change  OK
  R1->R2  resistance rises       1->2  predicts little  OK    1->4  predicts rise       OK
  A1->A2  one party to three     1->1  predicts rise    MISS  1->1  predicts no change  OK
```

Both theories of the construct are borne out where they disagree — origin's MSc really
does climb on stakes, ours really does climb on resistance and not on stakes. Neither is
"wrong" by this test; they measure different things, deliberately.

The one miss is origin's, and it is the familiar shape: its text names the number of
agents a driver, and adding two more already-agreeing colleagues moves nothing. Another
clause that does not bind.

### N-set: cannot settle the disentanglement claim, and should not be cited as if it does

```
  MSe_old   SWE  2 2 2 2 2 2 2 2   within-family SD 0.00
            tau  3 3 3 3 3 3 3 3   within-family SD 0.00
  PLs_new   SWE  2 2 2 2 2 2 2 2   within-family SD 0.00
            tau  2 2 2 2 2 2 1 2   within-family SD 0.33
```

H1 and H3 are **not evaluable**. Both arms collapse to a near-constant 2 on the SWE
frames, so the correlation against PLp/PLe has zero variance and is undefined, and no
frame separates by 2 or more. Only 8 of the 16 frames carry PLp/PLe reference labels at
this checkpoint, which halves what little was left.

What is visible is H2's signature: `MSe_old` assigns *literally identical* scores within
each family, for all three judges, on all sixteen frames. `PLs_new` varies. Round 9's
"moves as one ladder" pattern is reproduced in the old arm and is not present in the new
one. That is suggestive and no more.

The honest conclusion is about the instrument, not the rubrics. Sixteen frames sampled
from real traces have almost no spread, and the audit's own design targets say a
validation battery must be *built to a specification* — three tasks at 0-1 and three at
4-5 per dimension — rather than sampled for convenience. This N-set does not meet that
bar. The C-set does, and the C-set is what the PR should lean on.
