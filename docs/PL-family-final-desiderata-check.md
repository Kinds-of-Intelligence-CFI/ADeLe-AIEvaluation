# PL family — final check against the desiderata and against v1's voice (2026-08-25)

Covers PLp, PLe, PLs as they now stand in `src/adele/rubrics/data_v2/Paolo_Pablo/`.

## Style, measured against the 18 usable v1 files

`data_v1/MSm.txt` is excluded as an outlier on its opener, not as a modified file. It is authentic
v1 text; commit c5130dc was a pure rename and the old blob is byte-identical.

| | prose sentence mean | longest | examples | example mean | em-dash | semicolon | cross-refs | glosses |
|---|---|---|---|---|---|---|---|---|
| **v1 (18 files)** | 20.8 (range 11.8-31.2) | 210 | 18.6 | 25.9 | 0.2 | 0.2 | **0** | **1 in 335** |
| PLe | 17.5 | 39 | 20 | 25.6 | 0 | 0 | 0 | 0 |
| PLp | 17.7 | 37 | 20 | 25.9 | 0 | 0 | 0 | 0 |
| PLs | 15.7 | 48 | 26 | 29.3 | 0 | 0 | 0 | 0 |

All three sit inside v1's range on every measure. PLs runs slightly long on examples because the
concreteness pass put the deciding quantities in, which is the v1 pattern rather than a departure.

Judges quote clauses back verbatim and correctly across all three rubrics, which is the strongest
usability evidence available short of human annotation.

## Desiderata

| # | | PLp | PLe | PLs |
|---|---|---|---|---|
| 1 | Taxonomy fit | pass | pass | pass, provenance recorded |
| 2 | Disentangles from siblings | pass, one open | pass, newly demonstrated | pass, one open |
| 3 | Single driver | pass | pass | pass |
| 4 | Intuitive | pass | pass | pass |
| 5 | Usable by an annotator | pass | pass | pass |
| 6 | Examples disentangle | pass | pass | pass, measured |
| 7 | v1 voice | pass, measured | pass, measured | pass, measured |
| 8 | Thoughtful | pass | pass | pass |
| 9 | **Criterion validity** | **OPEN** | **OPEN** | **OPEN** |

### Desideratum 2, the two open items

- **PLp and PLs co-load on chess-shaped tasks** (r59): chess scores 3 on both, unanimously. The
  seating control scores PLp 3 and PLs 0, so the carve is intact and the co-load appears only where
  a planning task's situation genuinely runs forward. This follows from the scope Pablo installed
  deliberately, so it is a construct decision, not a defect. **Awaiting his ruling.**
- **PLe does not co-load with PLs** and the reason is now measured (r59): PLs falls when the world
  carries the change, PLe only when the environment carries the judgement.

### Desideratum 9 is the only one still failing, and it fails for all three

Criterion validity needs solver outcomes joined to demand labels. Nothing in this stream touches
it. It is not a rubric-text problem and cannot be closed by another round.

## Anchoring, stated plainly

| | best human anchor |
|---|---|
| PLp | 94 per cent exact, QWK 0.964 |
| PLe | closed at r44, alpha 0.967; Pablo's human labels sit at level 2 |
| PLs | r53, since partly invalidated by the swe-0461 reruling; five of six hold |

**No human has labelled any PL item above 3.** Every top-band placement in all three rubrics rests
on model agreement with my construction. Across this stream a prediction of mine was wrong and the
text was right eight times; the reverse has not happened once. That asymmetry is the single best
argument for getting human labels above 3 before these are used in anger.

## Outstanding, in the order I would do them

1. Pablo's ruling on the PLp/PLs chess co-load.
2. Human labels above 3, on all three. The six designed top-band pairs on the r56 sheet are the
   cheapest route.
3. The three-deep nested attribution route in MSm Level 5, still untested after r60.
4. Desideratum 9, which is an experiment rather than a round.
5. `MSc.txt` still carries the "level of cognitive demands" opener that MSm has now shed.
