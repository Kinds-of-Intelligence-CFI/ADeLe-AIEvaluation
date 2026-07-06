# Rivercross annotation frames

Frames are the task materials shown to demand-level annotators. They must stay
separate from solver-derived analysis targets.

## Files

- `1b_state_visible.csv` is the method-1b residual-demand frame with the current
  river-crossing state visible in each prompt. It is appropriate for PLp/PLe
  demand-to-go annotation.
- `ground_truth/1b_state_visible_cost_to_go.csv` contains solver cost-to-go for
  the same `custom_id`s. This file is analysis-only and must never be included in
  annotation prompts.

## Leak-free rule

Annotation frames may contain only information the judge is allowed to use. They
must not contain solver oracle fields such as `dist_to_goal`, `cost_to_go`,
`solver_depth`, `optimal_steps`, or optimal traces. Run `validate_frames.py`
after regenerating frames.

