# Rivercross prompt templates

Prompts are generated from three separate inputs:

1. a rubric file, which defines one dimension and its 0-5 levels;
2. a template, which defines the annotation protocol;
3. a frame CSV, which defines the task information shown to the judge.

The generated prompts under generated/ are reproducible artifacts. Edit the rubric or template, then rerun build_prompt.py; do not hand-edit generated prompts.

## Method 1b PLp/PLe

Use templates/demand_to_go_annotation.txt for residual demand-to-go annotation: the judge scores what remains to be done from the presented state, not the original whole task.

Current generated prompts:

- generated/prompt_PLp_1b_state_visible.txt
- generated/prompt_PLe_1b_state_visible.txt

## MMs history-only pilot

Use templates/memory_state_tracking_annotation.txt with Marko's MMs rubric. The pilot needs both conditions so the analysis can compute paired delta:

- generated/prompt_MMs_1b_state_visible.txt
- generated/prompt_MMs_1b_history_only.txt

Regenerate with:

python experiments/rivercross/prompts/build_prompt.py --rubric MMs --template memory_state_tracking_annotation --frame experiments/rivercross/frames/1b_state_visible.csv
python experiments/rivercross/prompts/build_prompt.py --rubric MMs --template memory_state_tracking_annotation --frame experiments/rivercross/frames/1b_history_only.csv
