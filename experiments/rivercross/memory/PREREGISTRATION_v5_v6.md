# Pre-registration: MMs protocols v5 (real-1b rollouts) and v6 (widened contrast)

Committed BEFORE any v5/v6 label collection; the commit order in git is the
audit trail. The frozen v3/v4 artifacts and results are unchanged by this
document. Deviations from this plan must be reported as deviations, not
silently absorbed.

## Judge panel (fixed for v5 and v6)

- claude-sonnet-5, claude-opus-4-8, gpt-5 (the panel that passed v3 gates and
  the v4 verbosity control, spanning two model families).
- Claude Haiku 4.5 is excluded a priori: v3 judge-independence failure
  (delta tracked history_length rho=0.583 and cost_to_go rho=0.722) and v4
  batch-framing instability (same traces labeled 2-4 in v3, 1 in v4).
- Any judge added later must first pass a state-reconstruction screen:
  given held-out history-only prompts, reconstruct the exact current
  configuration for >= 90% of items. Gate performance on this protocol may
  not be used to select judges.
- Annotation settings: one completion per prompt via
  memory/run_prompt_annotation.py; max-tokens 16384 for Claude judges,
  32768 for GPT-5.

## Shared prompt

Template `prompts/templates/memory_state_tracking_annotation_v5.txt` - the
frozen v3 template with the contrast-set-specific sentence generalized
("Multiple tasks may share the same number of history steps."); decision
rule, focus list, and level anchors are unchanged. MMs rubric version:
`src/adele/rubrics/data_v2/Marko/MMs.txt` as in v3.

## Protocol v5 - MMs on real method-1b rollout states

Frames: the existing `frames/1b_state_visible.csv` and
`frames/1b_history_only.csv` (43 paired states from real method-1b traces;
the same states carry PLp/PLe v11 labels). Pair metadata:
`frames/ground_truth/1b_memory_pairs.csv` (cost_to_go 1-7, history_length
1-4, object_location_updates 2-8).

Gates, per judge (analysis: `analyze_multi_judge_mms.py --pairs
frames/ground_truth/1b_memory_pairs.csv --history-frame
frames/1b_history_only.csv`):

1. Baseline floor: mean state-visible MMs <= 0.25.
2. Signal: paired delta > 0 (one-sided Wilcoxon p < 0.01) and
   Spearman(delta, object_location_updates) >= 0.5.
3. Difficulty independence (newly testable here because cost_to_go spans
   1-7): in the standardized regression
   delta ~ object_location_updates + history_length + cost_to_go,
   beta(object_location_updates) > |beta(cost_to_go)|, and
   Spearman(delta, cost_to_go) < Spearman(delta, object_location_updates).

Cross-judge: pairwise within-1 >= 0.9 and QWK >= 0.5 across the panel.

Caveat recorded in advance: on real traces the features are naturally
correlated (updates grows with history length); raw correlations are
reported but the regression is the primary evidence for gate 3.

Exploratory (no gate): correlate MMs delta with the PLp/PLe v11 labels on
the shared custom_ids - the expectation is that MMs delta tracks update
complexity rather than planning demand.

## Protocol v6 - widened contrast set

Purpose: close the three v3 design gaps - (a) controls without variance,
(b) untested level 4-5 anchors, (c) updates/reversals collinearity.

Construction (`frames/build_wide_contrast.py`, seeded random-walk sampling
because exhaustive enumeration is infeasible at length 10):

- history_length in {3, 7, 10}; 2 replicates per cell as in v3.
- Within each history_length: low / medium / high object-memory complexity
  cells, with the high cells at length 10 targeting the level 4-5 range.
- Decoupling cells at matched update counts: (many updates, zero reversals)
  vs (matched updates, many reversals).
- cost_to_go varied across cells (target: spread over at least 1-5) instead
  of being pinned.

Gates, per judge:

1. Baseline floor: mean state-visible MMs <= 0.25.
2. Within each history_length bucket, cell-mean delta increases
   monotonically from low to high complexity (cell-level analysis primary,
   as in the post-review v3 reporting).
3. Difficulty independence, as v5 gate 3.
4. Anchor coverage (diagnostic, not pass/fail): the top length-10 cells
   elicit labels >= 4 from at least two judges; if not, the level-4/5
   anchors remain untested and must be flagged.
5. Reversal effect (directional, exploratory): at matched updates, the
   reversal cell's delta >= the no-reversal cell's delta.

Cross-judge: as v5.

## Human annotation

Before any external claim from v5/v6: the v3 spot-check is completed for
all 18 pairs and a human pass over the v5 pairs is collected, using
templates with explicit annotator/date fields; a second annotator for a
human-human ceiling remains an open team task (todo.md).
