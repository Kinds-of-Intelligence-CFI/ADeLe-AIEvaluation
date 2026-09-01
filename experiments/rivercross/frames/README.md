# Rivercross annotation frames

Frames are the task materials shown to demand-level annotators. They must stay separate from solver-derived analysis targets.

## Files

- 1b_state_visible.csv is the method-1b residual-demand frame with the current river-crossing state visible in each prompt. It is appropriate for PLp/PLe demand-to-go annotation and as the state-visible baseline for MMs.
- 1b_history_only.csv is the paired MMs pilot frame. Each row has the same underlying state as a state-visible row, but shows only rules, initial state, move history, and goal. The present configuration is not directly shown.
- 1b_memory_contrast_state_visible.csv and 1b_memory_contrast_history_only.csv are the v3 MMs contrast frames. They hold history_length fixed within buckets while varying object-location update complexity.
- ground_truth/1b_state_visible_cost_to_go.csv contains solver cost-to-go for the state-visible custom_ids.
- ground_truth/1b_memory_pairs.csv maps each state-visible row to its history-only pair and stores hidden analysis fields: true state, cost_to_go, history_length, object_location_updates, repeated moves, and related memory features.
- ground_truth/1b_memory_contrast_pairs.csv is the paired analysis table for the v3 contrast set, including contrast_level and object-memory complexity features.

## Generation

Run:

python experiments/rivercross/frames/build_frames.py
python experiments/rivercross/frames/build_memory_contrast.py

The state-visible frame is preserved from the legacy method1b frame. The history-only frame is generated structurally: the builder infers the underlying solver state, finds a legal shortest history from the initial state to that state, and formats the item from initial state plus move history. It is not produced by deleting current-state text from the state-visible prompt.

## Leak-free rule

Annotation frames may contain only information the judge is allowed to use. They must not contain solver oracle fields such as dist_to_goal, cost_to_go, solver_depth, optimal_steps, or optimal traces. History-only frames must also avoid direct current-state descriptions such as Current situation, Left bank:, Right bank:, or The boat is on.

Validate with:

python experiments/rivercross/frames/validate_frames.py
python experiments/rivercross/frames/validate_frames.py --condition history_only
python experiments/rivercross/frames/validate_frames.py --condition history_only --frame experiments/rivercross/frames/1b_memory_contrast_history_only.csv --state-visible-frame experiments/rivercross/frames/1b_memory_contrast_state_visible.csv --memory-pairs experiments/rivercross/frames/ground_truth/1b_memory_contrast_pairs.csv

The ground_truth files are analysis-only and must never be included in annotation prompts.
