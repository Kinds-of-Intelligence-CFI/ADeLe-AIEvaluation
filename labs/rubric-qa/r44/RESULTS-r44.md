# Round 44 — PLe compression regression, and closing PLp (2026-08-22)

Seal: `sealed_predictions_r44.md`. Raw: `results_r44.csv`. Judges h/s/o, 3 seeds, never Fable.

## Verdict: compression ADOPTED — 11/11 items reproduced exactly

| item | r39 | r44 | Δ |
|---|---|---|---|
| probe-L2forced | 2 | 2 | 0 |
| probe-L3elected | 3 | 3 | 0 |
| probe-L4a / L4b | 4 / 4 | 4 / 4 | 0 |
| probe-L0a / L0b | 0 / 0 | 0 / 0 | 0 |
| probe-filing | 2 | 2 | 0 |
| probe-cave | 5 | 5 | 0 |
| probe-kill | 1 | 1 | 0 |
| swe-0090 / usaco-0002 | 3 / 3 | 3 / 3 | 0 |

All five pre-registered rules pass. Every judge's deciding phrase still quotes a surviving
clause — the L2 forced clause, the L3 elected clause including "nor that the task names one",
L4's symptoms-far-from-cause, L5's "none can be constructed", and the stakes exclusion on
probe-filing. Nothing was bought with behaviour.

Shape after compression, against desideratum 7 (v1 range 66–217 w, PLp reference 73 w):

| | r39 | r44 |
|---|---|---|
| preamble | 151 w | **117 w** |
| does-not-cover | 168 w | **139 w** |
| L3 / L4 / L5 | 140 / 86 / 135 w | **111 / 76 / 114 w** |

PLe is now inside the v1 range on every element and roughly 20% shorter overall. It remains
longer than PLp; that residue is the cost of clauses each round measured into existence, and
I am not proposing to cut further — the next cut would have to take a tested clause.
**Desideratum 7: met.** Examples untouched throughout, so the r39 placement result stands.

## PLp — closed with no text change

PLp's body is unchanged since 2026-08-16. What closed it was r42/r43: the diagonal held on
all three PLp items, the drafted lookahead exclusion moved no score and was withdrawn under
the stopping rule, and the double dissociation against PLs was measured in both directions.
Only the meta line changes, to record that evidence (`PLp_r43_final.txt`).

**One residual accepted rather than fixed:** PLp's L3/L4 boundary is judge-capability-relative
(a weaker judge reads a plan-search as harder than a stronger one does), absorbed by
median-of-3. This has been known since the July freeze note. It is a property of judging, not
of the text, and no text edit has ever been shown to move it — recording it as an accepted
limitation is the honest close.

## Where the PL family now stands

| desideratum | PLp | PLe | PLs |
|---|---|---|---|
| 1 taxonomy fit | met | **entry stale — open** | **none — open** |
| 2 disentangles (measured) | met (r42/r43) | met (r42) | met (r42) |
| 3 single driver | met | met | met, fused (r40) |
| 4 intuitive | met | met | met |
| 5 usability | met, residual accepted | met (α 0.97) | met, one boundary open |
| 6 examples disentangle | met (r42) | met (r42) | met (r42) |
| 7 v1 shape | met | **met (r44)** | 147 w — open |
| 8 thoughtful | met | met | met |
| 9 empirical grounding | open | open | open |

**PLp and PLe are finished** on everything this workstream can close. What remains for both
is desideratum 1 (provenance entries — writing, not measurement) and desideratum 9
(criterion validity — solver outcomes joined to demand labels, a data-pipeline job that no
internal round can substitute for).

PLs still needs: the six-item coupling-vs-chain boundary round, a compression pass of its
own, a provenance entry, and — the one that matters — **Pablo's labels, which it has never
had.**
