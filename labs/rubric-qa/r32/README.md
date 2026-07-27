# Round 32 — measuring three PLe audit claims instead of applying them

The pre-PR audit left three PLe findings. All three were **arguments from reading the
text**, never measured. The audit's own preamble reports that about a third of that
pass's confident claims were false against data already held, and round 30 is this
session's own case of a plausible fix that failed and backfired. So the claims were
tested before anything was changed. Pre-registered in `prereg_r32.json`.

| claim | verdict |
|---|---|
| **3.1** L5 makes irreversibility a third conjunct, so irreversible-but-instant tasks score low | **CONFIRMED**, and worse than stated |
| **3.5b** no brake at the top of the scale, so hard tasks drift to 5 | **REFUTED** |
| **3.3** action/feedback defined only in the preamble while three levels count in those units | **REFUTED** |

## 3.1 — confirmed, and the audit under-stated it

Three items that are irreversible, instantly confirmed, and non-propagating (book a
non-refundable flight; send an unrecallable all-company message; execute an irreversible
payment) scored **[0, 5, 5]**. Not a wrong answer — a *five-level disagreement on the
same item*, decided by whether a judge reads "in addition to" as the conjunction it
literally is. The reversible twin (I04) is 0 for all three judges, so it is
irreversibility producing the split and not item difficulty.

The audit predicted a wrong answer. What is actually there is an unstable one, which is
worse: it will not show up as a consistent bias in any aggregate.

## 3.5b and 3.3 — refuted, and 3.3 is worth keeping

**3.5b.** Two fully reversible items built to provoke upward drift — a 40-file refactor
with silent propagation, a six-week filing with counsel review — scored [4,4,4] and
[2,2,2]. Neither drifted. No brake was needed for the reason the audit gave.

**3.3.** All three probes landed on their pre-registered levels, unanimously: sixty
immediately-checked ledger entries stayed at L1 (so the "however many steps" clause held
and the count did not drive it), four thousand words were not counted as actions, and
hours of deliberation were not counted as actions.

So **preamble definitions bind where preamble carve-outs do not**, and the mechanism is
visible. A level that says "roughly once every two to ten actions" *forces* the judge to
resolve "action". A level that never mentions an exception never sends the judge looking
for one. That is why round 20's finding, and PLe's L1 and MSm's L4 carve-outs, are all
about carve-outs — and it is why PLe's preamble can stay at 257 words holding two
definitions three levels depend on. 3.3's proposed fix would have triplicated text to
solve a problem that does not exist.

## The fix, in two passes

**Pass 1** made irreversibility sufficient at L5 and added the matching carve-out at L0
(a single irreversible action reads as "one atomic action, succeeds or fails at once",
which is where the judge scoring 0 was getting it). The target items went to [5,5,5] —
and T06, sending a death notification, went **[0,0,0] -> [0,5,5]**. Sending cannot be
undone either. Prereg agreement fell 52 -> 49/72.

**Pass 2** added the missing condition: the step must be one that *could be carried out
wrongly*. A booking can be the wrong flight; a message either sends or it does not, and
its risk lies in what it carries, which belongs to whichever dimension owns the content.

```
  I01-I03  [0,5,5] -> [5,5,5]     the defect, fixed, no spread left
  T06      [0,5,5] -> [0,0,5]     mostly recovered; one judge still says 5
  battery  52/72 -> 49/72 -> 53/72
```

So the brake the audit wanted at the top of the scale **is** needed — not for the drift
it predicted, which does not happen, but for drift this fix created.

## Residuals, stated rather than buried

- **T06 still has one judge at 5.** Whether sending a notification "could be carried out
  wrongly" is genuinely arguable — wrong family, wrong details. Two of three now read it
  as content risk. Left as-is rather than tuned further on a single item.
- **T07 wobbles independently of anything done here.** [0,0,3] in r30, [0,0,3] in r31's
  tightening-only arm, [0,3,3] here. It is an unstable item, not a regression.
- **Overfitting risk is real and should be said plainly.** This is the fourth round scored
  on the same 24 items. Net +1 cell is not evidence of much; the decisive result here is
  the audit items going from a five-level spread to none. The battery needs refreshing
  before its totals carry weight again.
