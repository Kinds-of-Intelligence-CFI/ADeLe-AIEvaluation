# relabel-v3 — results

**Question.** After moving the PLp synthesis example from Level 5 to Level 4 and shortening the MSm Level 5 seller
example, do the labels near those levels change, and do the rubrics' signals hold?

**Answer.** No change beyond judge noise, and the signals hold.
- Re-judged cells unchanged: PLp 86% (333 cells), MSm 97% (123 cells). Rerunning the judge changes about as many.
- PLp at Levels 4–5: 10 tasks before, 11 after (none at 5). MSm on EQ-Bench 4: 119 of 120 still at 4.
- PLp keeps its signals: SWE-bench Verified −0.55 (unchanged), ProgramBench −0.49 (was −0.51), tau2 −0.28 (was −0.29).
- One caveat on the merged labels. Only cells at PLp 3–5 were re-judged, so noise could move cells down out of
  Level 3 (39 did) but could not move Level 2 cells up (in relabel-v2 about 4% of them rose to 3, which would be about
  35 here). The merged PLp labels therefore lean slightly downward by selection, not because of the text: re-judged
  cells shift −0.11 on average, EQ-Bench 4 −0.11 and FrontierSWE −0.11 overall.

**Status.** Complete (2026-10-04). 456 cells in seven runs, all labelled and written by Opus 5.5 at effort low; weekly
usage 85% → about 86%. Every protocol check passes except one stray transcript in `relabel-v3-plp-long`: a relay was
sent one mistyped cell id (an orchestrator transcription error), whose judge found no prompt and wrote nothing; the
real cell was sent again and labelled. Sealed predictions: 7 of 7 held.

## Design

See `PREREGISTRATION.md`, pushed before any label (`d6cc9ca`). Old labels: `old_labels.csv` (relabel-v2, frozen).

## Predictions

| prediction | sealed | result |
|---|---|---|
| re-judged PLp unchanged ≥ 80% | 0.7 | held (86%) |
| re-judged MSm unchanged ≥ 80% | 0.85 | held (97%) |
| no set's mean PLp shift beyond ±0.2 | 0.85 | held (largest −0.11) |
| PLp tasks at 4–5 change by at most 10 (was 10) | 0.75 | held (11) |
| SWE-bench Verified PLp ρ ≤ −0.5 | 0.95 | held (−0.55) |
| ProgramBench PLp significant and negative | 0.85 | held (−0.49, p < 0.001) |
| EQ-Bench 4 MSm at 4 on ≥ 110 of 120 | 0.8 | held (119) |

## Results

Moves on the re-judged cells: PLp 3→2 39, 3→4 4, 4→3 3; MSm 4→3 2, 4→5 1, 5→4 1. For comparison, the full
relabel-v2 (no selection) moved PLp 3→2 in 21% of Level 3 cells and 2→3 in 4% of Level 2 cells; here 3→2 is 12%.

| set (PLp, all cells) | mean shift | ρ old | ρ new |
|---|---|---|---|
| SWE-bench Verified | −0.01 | −0.55 | −0.55 |
| ProgramBench | −0.03 | −0.51 | −0.49 |
| tau2 (within domain) | 0.00 | −0.29 | −0.28 |
| DeepSWE | −0.08 | −0.12 ns | −0.08 ns |
| TB-Science | 0.00 | +0.25 (p 0.040) | +0.28 (p 0.022) |
| Terminal-Bench 4.0 | 0.00 | +0.12 ns | +0.21 ns |
| FrontierSWE | −0.11 | −0.03 ns | constant (all 3) |

**Which labels to use.** The fixes change no label beyond noise, so either set is defensible. The merged labels
(relabel-v3 where re-judged, relabel-v2 elsewhere) match the current text but carry the one-way selection described
above; the relabel-v2 labels are symmetric but were made with the earlier two bullets. Re-judging the PLp cells at
Level 2 (about 890) would remove the asymmetry. The plots in `../pl-histograms/` use the merged labels.

## Files

- `results/analysis.json` (`analysis/analyse.py`); `selected.csv`; `../mass-annotation/runs/relabel-v3-*/labels.csv`.
