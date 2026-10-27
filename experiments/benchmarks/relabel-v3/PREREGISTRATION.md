# relabel-v3 — pre-registration

Committed and pushed before any label of this study. Pablo decided two flagged items of the examples review on
2026-10-04 and asked for a relabel of the affected cells only.

**Question.** After moving the PLp synthesis example from Level 5 to Level 4 and shortening the MSm Level 5 seller
example, do the labels near those levels change, and do the rubrics' signals hold?

## Design

- **Text changes** (`src/`, example bullets only; `docs/rubric-provenance/PLp.md` and `MSm.md`):
  - PLp: the synthesis-route bullet moves verbatim from Level 5 to Level 4.
  - MSm: the Level 5 seller's "final offer" bullet goes from 69 to 47 words; the closing gloss is removed.
- **Scope (Pablo's rule).** Re-judge only the cells whose relabel-v2 label is at most one level from the changed
  example's level: PLp at 3, 4 or 5; MSm at 4 or 5. 456 cells (`selected.csv`; subsets in `subsets/`): PLp 263 on
  the agentic sets, 13 on ProgramBench's long tasks, 17 on EQ-Bench 4, 37 on CooperBench, 3 on Game Arena; MSm 120
  on EQ-Bench 4 and 3 on Game Arena. No other cell is re-judged; it keeps its relabel-v2 label.
- **Runs** (specs in `../mass-annotation/specs/relabel-v3-*.toml`): `relabel-v3-plp`, `-plp-long` (chunked judge),
  `-plp-eqbench4`, `-plp-cooperbench`, `-plp-gamearena`, `-msm-eqbench4`, `-msm-gamearena`. Opus 5.5 at effort low,
  v2 prompt, relays of up to 100, as relabel-v2.
- **Old labels.** `old_labels.csv`: the relabel-v2 labels of PLp and MSm (2,823 rows), frozen now.
- **Analysis** (`analysis/analyse.py`). As relabel-v2, on the merged labels (new where re-judged, old elsewhere), plus
  the share unchanged, mean shift and level moves on the re-judged cells alone.
- **Caveat.** The window is set by the old label, so a cell outside it cannot move. Judge noise alone changes about
  14% of PLp and 6% of MSm labels (relabel-v2), so changes of that size are not attributable to the text.

## Predictions (sealed)

- Re-judged cells unchanged at least 80%: PLp 0.7, MSm 0.85.
- No set's mean PLp shift (all cells) beyond ±0.2: 0.85.
- PLp: tasks at Level 4 or 5, pooled, change by at most 10 (now 10, none at 5): 0.75.
- SWE-bench Verified PLp keeps ρ ≤ −0.5: 0.95. ProgramBench PLp stays significant and negative: 0.85.
- EQ-Bench 4 MSm stays at 4 on at least 110 of 120 scenarios: 0.8.

## Cost

456 Opus-low calls, about 1.1 weekly points (relabel-v2 measured about 1 point per 400 calls). Weekly usage is at 85%,
the stop line; started only with Pablo's go.
