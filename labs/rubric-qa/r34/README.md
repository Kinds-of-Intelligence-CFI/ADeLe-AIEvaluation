# Round 34 — do the examples themselves disentangle? (desideratum 6)

Round 25 tested **placement**: does an example return to the level it illustrates, within its
own rubric. It never asked what desideratum 6 actually poses — is an example illustrating
`PLe` L4 **low** on `PLp`, `PLs` and `MSc`? This does.

All 77 examples from the four rubrics pooled into one blind set, level cross-references
rewritten, opaque shuffled ids, and the pool scored by each of the four rubrics — so every
example gets one own-dimension score and three foreign ones. A foreign score of 3+ at level
3-5 is a leak.

## Result

| | before | after |
|---|---|---|
| placement within 1 on own dimension | 77/77 | **77/77** |
| foreign scorings clean (levels 3-5) | 81/111 = **73%** | 106/111 = **95%** |

### What the first run found

30 leaks, and 27 of them were *inside the PL triad* — `PLp`↔`PLe` 12, `PLe`↔`PLs` 8,
`PLp`↔`PLs` 7. `MSc` was already clean as a receiver: not one `PLp`/`PLe`/`PLs` example
scored 3+ on it.

That is the taxonomy artifact's §10 diagnosis showing up at the level of examples rather than
levels. The re-key fixed the *rubrics* — battery-v1 separates 10/12 — but the examples still
described whole realistic tasks, and a realistic hard planning task also involves execution.

### The fix

An isolating example has to say what it does **not** demand, the way battery-v1's pure items
do ("every distance is given in a table, the roads never change, and nothing is hidden").
Fourteen examples got one short neutralising clause each:

```
  PLp L3 multi-city trip      + "Nothing is reserved: the deliverable is the itinerary."
  PLp L4 first ascent         + "The deliverable is the route plan; the climb is not attempted here."
  PLp L5 synthesis route      + "The route is designed on paper; nothing is run at the bench."
  PLe L4 ledger reconciliation+ "The reconciliation procedure is given step by step."
  PLe L4 legal translation    + "The glossary and translation brief are supplied."
  PLs L5 dead reckoning       + "Holding a heading is trivial; the whole difficulty is knowing where you are."
  PLs L5 building fire        + "What is scored here is knowing where the fire has reached, not putting it out."
  MSc L5 hostage negotiation  + "The tactical plan is settled and not yours to make."
  ... and six more
```

Every leak inside the PL triad is gone. Five remain: four `MSc` examples scoring `PLp` 3 —
multi-party negotiation genuinely involves search over concession sequences, and the taxonomy
is explicit that co-loading is not itself a defect — and one `PLe`→`PLs`.

Placement did not move: still 77/77. Battery-v1 separation did not move: still 10/12.

## A note on the tension inside desideratum 6

"Representative" and "strengthens disentanglement" pull against each other. A representative
example of hard planning is a realistic composite; an example that isolates the construct is
artificial. The resolution used here is to isolate at the levels where confusion was actually
measured — the PL triad at 3-5 — and leave the rest representative.

## Method note, kept because it cost a round

The first attempt keyed items as `PLe-L4-02`. The id names the dimension and the level, and it
necessarily reaches the judge because the answer is returned as keyed JSON. Judges read it off:
one returned a perfect diagonal across all four rubrics. Blinding is not only about which arm
a judge sees — anything carried alongside the item can carry the answer. Rounds 26-33 used ids
that encode nothing and are unaffected.
