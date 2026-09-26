# Round 68 — regression check on v19's standing-rate clause (2026-08-26)

Seal: `sealed_predictions_r68.md`. Judges h/s/o, median of three, scored against v19 with the meta
line and the Level 3, 4 and 5 examples stripped.

| id | item | h | s | o | median | was | |
|---|---|---|---|---|---|---|---|
| G1 | profession headcount 2041 | 3 | **2** | 5 | **3** | 5 (r59) | ✗ |
| G2 | two states, mobile launchers | 4 | 5 | 5 | **5** | 5 | ✓ |
| G3 | bank run spreading | 4 | 5 | 5 | **5** | 5 | ✓ |
| G4 | rail line, anticipatory rents | 4 | 5 | 5 | **5** | 5 | ✓ |
| G5 | fire, four-minute window | 3 | 3 | 4 | **3** | 4, **Pablo's label** | ✗ |
| G6 | fox and rabbit trough | 3 | 4 | 4 | **4** | 4 | ✓ |
| G7 | two cafés | 3 | 3 | — | **3** | 3 | ✓ |
| G8 | chess middlegame plan | — | — | 3 | **3** | 3 | ✓ |

Two failures against the seal: G1 fell two levels, and G5 broke Pablo's own label.

## The failures are real, and v19 did not cause them

**Not one of the twenty-four judgements cited the standing-rate clause or the new Level 5 Note.**
The clause that was on trial never fired on any of these items — which is precisely the selectivity
it was designed for: it fired throughout the forecasting corpus in r67 and is silent on
mechanism-carrying situations here.

What the two failing judges actually cited:

- **G1, sonnet at 2**: Level 2's *"however long the horizon and however exact the answer required"*,
  reading the halved-hiring and lagged-seniors chain as supplied rules with no genuine feedback.
  That clause predates v19 by many versions.
- **G5, haiku and sonnet at 3**: the Level 3 gloss that a coarse run still lands on the answer,
  i.e. the sensitivity boundary introduced in v16 and already measured.

So the seal's rule 4 fires, but on the wrong defendant. **v19 passes the check it was built for.**

## What did cause them: the examples carry the top band

Controls run against the *unstripped* v19:

| item | stripped | unstripped |
|---|---|---|
| G5 fire | haiku 3, sonnet 3 | haiku 3, **sonnet 4** |
| G1 profession | sonnet 2 | **sonnet 5** (and it flagged the item as the verbatim Level 5 example) |

Sonnet moves two and three levels on the same item and the same text, purely on whether the
examples are present. G1's r59 measurement used an L5-stripped variant and came back 3/5/5; the
same design now gives 3/2/5. One judge moved and the median flipped, because haiku sits low at the
top band in every round of this stream.

**The finding to keep: the level statements alone under-determine the top band.** Three of eight
items are stable without examples; the two hardest are not. Two consequences:

1. **The annotation harness must never strip examples.** Strip the `#!` line, keep everything below
   it. This is the opposite of the r64/r65 protocol change and needs to sit alongside it.
2. **Every stripped-variant measurement in this stream is a lower bound**, not a like-for-like
   reading — including r57b, r59 and r64. Where those rounds confirmed an example at its level, the
   confirmation stands. Where they were used to compare against a full-rubric number, they were not
   comparable, and r68 is the first round to notice.

## Standing

- v19's clause: **safe**, and selective in the intended direction.
- The top band: **stable with examples, fragile without**. G2, G3 and G4 hold at 5 either way.
- Pablo's fire label at 4: recovered under the unstripped rubric by the stronger judge, lost under
  the weaker one. The 3/4 boundary remains the least stable in the rubric, as r63 found.
