# pl-relabel-v2 — pre-registration

Committed and pushed before any label of this study. Pablo adopted the v2 prompt on 2026-09-29
(`build_annotation_prompt_v2`, tested as variant B in `natural-prompt`) and asked for the planning
labels to be redone with it, with Opus low as the judge.

**Question.** Do the pre-registered PL results of `swebench-pl` and `tau2-tb4-pl` hold when the labels
are made with the v2 prompt?

## Design

- **Judge.** Opus low through `adele-judge-v2-low`, relayed by `judge-dispatcher-v2-low`, one call per
  cell. Answers written by another model are set aside and the cell is judged once more; if that
  fails too, the cell has no label (as in `tau2-tb4-pl`, amendment 2).
- **Runs.** `v2-swe`: the 398 SWE-bench Verified tasks of `swepl-r1-low` (1,194 cells). The 44 gate
  tasks were already judged with this exact prompt (`natural-prompt`, run `npb-gate-opuslow`); their
  prompts were checked to be identical and their labels are reused. `v2-tau2`: 232 tau2 tasks (696
  cells). `v2-tb4`: 66 Terminal-Bench tasks (198 cells). In all, 2,088 new calls.
- **Inputs.** `make_prompts.py` rebuilds every old prompt from the same rubric and task text and checks
  it against the old run's hash, so only the prompt differs.
- **Analysis** (`analysis/analyse.py`). Each study's own pre-registered functions on the new labels:
  `swebench-pl`'s questions on the 435 solvable tasks, and `tau2-tb4-pl`'s analysis on tau2 and
  Terminal-Bench. The old-prompt results (Opus low) are shown beside them, with old-against-new
  agreement per benchmark and rubric.

This is a re-measurement, not a test with a pass mark: the prompt is already adopted. The results
say which conclusions of the two studies survive the change.

## Predictions (sealed)

Old Opus-low values in brackets.
- SWE-bench, PLp against solve rate stays negative with p < 0.05 (−0.57): 0.95. Within ±0.10 of it: 0.7.
- SWE-bench, PLe against solve rate within ±0.10 (−0.46): 0.6.
- tau2, PLp against solve rate within domain within ±0.10 (−0.33): 0.65.
- Terminal-Bench, PLp against solve rate stays within ±0.20 of zero (−0.06): 0.75.
- Mean shift, new minus old, on SWE-bench: PLe above +0.10, 0.7; PLp within ±0.10, 0.7.

## Cost

2,088 Opus-low calls, about 12 weekly points and 1.5 hours, in relays of about 100 cells.

## Deviations

None yet.
