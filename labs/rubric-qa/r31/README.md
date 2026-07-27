# Round 31 — does MSm double-count MSc, and where?

Round 30 tried to fix the suspected MSm/MSc overlap by rewriting MSm's title and
preamble. It failed its pre-registered test and made things worse: judges started
scoring chess opponents as mind modelling. Round 31 asks the question properly.

## Why r30 couldn't answer it

MSm and MSc correlated at r = 0.90 across r30's 24 items — but 16 of those items
score 0 on both, and of the 8 that load either dimension almost all are
multi-party negotiations that genuinely load both. The correlation was an
artefact of a battery built to stress PLe and MSc. So: 10 new items built to
*separate* the two.

```
A  inference is hard, nobody to move      D01-D04
B  the stance is stated outright in full, but must be moved   D05-D07
C  both                                   D08
D  neither                                D09-D10
```

## Result

| item | MSm (v1) | MSm (+carve-out) | MSc | |
|---|---|---|---|---|
| D01 novel, four mistaken beliefs | 5 | 5 | 0 | A |
| D02 predict six votes, private note | 4 | 4 | 0 | A |
| D03 explain a poker call | 4 | 4 | 0 | A |
| D04 who missed the deadline | 4 | 4 | 0 | A |
| D05 supplier states his reasons | **4** | **2** | 4 | B |
| D06 three published budgets | **5** | **3** | 5 | B |
| D07 customer states his reason | **4** | **2** | 4 | B |
| D08 co-founders, unspoken suspicion | 5 | 5 | 5 | C |
| D09/D10 sorting, arithmetic | 0 | 0 | 0 | D |

**H1 passed on v1 already.** MSc is 0 on every A item — it never fires where there
is no one to move. That direction was never broken.

**H2 failed on v1**, on all three B items: MSm scored 4, 5, 4 on tasks that hand
the solver the other party's stance *and their reasons*. Nothing is left to infer,
and MSm was scoring it anyway. That is the double-count, and it is not diffuse —
it lives at L4 and L5.

**H2 passes with the carve-out**, and H1 and H3 are untouched.

## The fix, and why r30's version of it failed

One carve-out at L4, echoed at L5. Nothing else — title, preamble and levels 0-3
are byte-identical to v1, which a test enforces.

> Critically, a stance the other party has stated outright, together with their
> reasons, does not have to be modelled: where the task hands over what they
> believe and want, the inferring has already been done, and moving them from that
> stance is assessed by Communication and Social Interaction (MSc). What places a
> task at this level is that the mental states driving behaviour must be worked
> out, not merely acted upon.

r30 put the same idea in the preamble and it did nothing. Round 20 said preamble
clauses don't bind; PLe's L1 carve-out for displayed state said it again one
commit ago. This is the third confirmation, and it is now a rule worth stating
plainly: **a carve-out binds at the level that over-fires, and nowhere else.**

## PLe attribution, settled

r30 bundled the wording tightening with the L1 carve-out and could not attribute
the churn. The tightening-only arm settles it:

```
  S04  tightening-only [1,1,1]   +carve-out [3,3,4]   the carve-out did this
  T07  tightening-only [0,0,3]   +carve-out [0,0,3]   noise, not a regression
  T04  tightening-only [4,4,4]   +carve-out [1,4,4]   one judge, cost of the fix
  T06  tightening-only [0,0,0]   +carve-out [0,0,3]   one judge, cost of the fix
```

The olympiad-proof trap was not broken by anything we did — it shows [0,0,3] in
both arms. The carve-out buys S04 outright for two ambiguous single-judge cells.
