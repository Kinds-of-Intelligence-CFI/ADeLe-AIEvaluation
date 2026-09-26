# PLs v7.2 re-validation — rounds r51 and r52 (2026-08-22)

Judges h/s/o, 3 seeds, one item per call, never Fable. Seals: `sealed_predictions_r51.md`.
Raw: `results_r51.csv`, `../r52/results_r52.csv`. Anchors are construction-side.
**No human has labelled a PLs item. Nothing below is human validation.**

## Five further fixes made before running, so the rounds test the final text

Rereading v7.1 turned up five things, three of them substantive:

1. **The driver statement did not describe its own lower levels.** It said demand rises with
   "the amount of interacting change", but Levels 1 and 2 have no interacting change at all.
   Now: how much change must be carried forward, how much of it interacts, and how finely
   the answer discriminates.
2. **The r47 scope finding was implicit.** A reader could not tell that simulation done in
   order to act is not scored. Now stated: *the demand is scored on what the task asks for,
   and where a situation must be run forward only in order to settle what to do, that
   running belongs with the choice it serves.*
3. **Elliptical back-references.** "The same hillside" and "The same break" are unreadable to
   a judge looking at one level in isolation. Both now name their situation.
4. Twelve kettles reduced to three, which reads like a real task rather than a contrivance.
5. "Here is a completed Sudoku grid" re-voiced to match the other examples.

## r51 — falsifiers, boundary, carves, scope. PASS on all seven rules.

**19/19 exact against sealed predictions. α = 0.992.**

- **Falsifiers all held.** A7 (interaction, coarse) = 3, not the top band. A4 and A5
  (no interaction, exact answers) = 2, so precision is still not a second axis. A8 (two
  couplings, fine answer) = 4, so the fineness-not-count gate still binds.
- **Precision contrast**: A1/A2 = 2 against A3 = 5, a three-level separation on one and the
  same situation; A7 = 3 against A6 = 5.
- **Coupling boundary**: both mutual items 3, both chain items 2, no overlap. A judge quoted
  the domino gloss verbatim to place the message relay.
- **Carves**: planning 1, mind-modelling 1, execution 0.
- **L0 clause** binds both ways: absent 0, present 2.
- **The new scope clause behaves**: the maximum-matching task 0, the same process asked as a
  prediction 4. Gap of 4, and the do-arm did not rise.

## r52 — family diagonal. Diagonal 8/9, and the off-diagonal is now empty.

| item | PLp | PLe | PLs |
|---|---|---|---|
| PLp-1 seating | **3** | 1 | 0 |
| PLp-2 timetabling | **3** | 1 | 0 |
| PLp-3 chess plan | **3** | 0 | **0** ← was 4 |
| PLe-1 sealed suit | 0 | **5** | 1 |
| PLe-2 transcription | 0 | **4** | 0 |
| PLe-3 compliance report | 1 | **3** | 0 |
| PLs-1 reservoir | 1 | 0 | **3** |
| PLs-2 price war | 1 | 0 | **3** |
| PLs-3 gear train | 0 | 0 | 2 ✗ |

**The one leak r42 found is gone, and the scope clause is why.** In r42 the chess plan scored
4 on Simulating, and I reported the co-load as a property of chess rather than a text defect.
That reading is now superseded: with the scope clause explicit, judges route the chess plan to
0, reasoning that the task asks for an action and the foreseeing belongs with the choice it
serves. **This is a large behaviour change, 4 to 0, caused by one clause I wrote — not a
cosmetic edit, and it should be reviewed as a construct decision rather than accepted because
the matrix looks tidier.** If the team wants instrumental simulation scored, this clause is
the thing to revisit, and r47 laid out what that would cost.

PLs-3 (gear train) still scores 2 on its own dimension and is still excluded from the
leakage analysis. It is a sequential chain, which the rubric now correctly places at 2 — the
item was mis-designed by me, twice, and the rubric is right about it.

## Am I happy with the rubric, pending human annotation?

Yes, with three things named rather than buried.

- **The scope is narrow and now explicit.** PLs measures simulation the task asks for. On
  agentic benchmarks that yields near-zero scores (r46), which is a statement about instance
  coverage, not about agents. Anyone reading PLs numbers needs that context, which is why it
  is going into the provenance entry.
- **Every anchor is mine.** Nineteen items in r51, nine in r52, all construction-side. Across
  PLe's rounds the anchor was wrong five times and the text zero times.
- **Desideratum 9 is untouched**, as for the whole stream.
