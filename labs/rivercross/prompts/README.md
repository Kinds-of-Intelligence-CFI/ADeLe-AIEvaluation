# Rivercross prompt templates

Prompts are generated from three separate inputs:

1. a rubric file, which defines one dimension and its 0-5 levels;
2. a template, which defines the annotation protocol;
3. a frame CSV, which defines the task information shown to the judge.

The generated prompts under `generated/` are reproducible artifacts. Edit the
rubric or template, then rerun `build_prompt.py`; do not hand-edit generated
prompts.

## Method 1b

Use `templates/demand_to_go_annotation.txt` for residual demand-to-go annotation:
the judge scores what remains to be done from the presented state, not the
original whole task.

