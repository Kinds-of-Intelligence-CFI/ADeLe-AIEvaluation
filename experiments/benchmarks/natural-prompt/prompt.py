"""The natural annotation prompt under test (option 1, chosen by Pablo on 2026-09-29).

It takes the same inputs as adele.annotation.prompts.build_annotation_prompt: the demand's name, the
rubric as the catalog loads it, and the task text. It asks for a short assessment before the level, in
plain words, with no request to write out reasoning. It ends with a sentence the existing parser reads
(the last "is: N" in the answer).
"""

TEMPLATE = """We are annotating AI evaluation tasks for a research study on the cognitive demands that tasks make. Below are a rubric for {demand}, with levels from 0 to 5, and a task.

<rubric>
{rubric}
</rubric>

<task>
{task}
</task>

Rate the task's demand for {demand} according to the rubric, not any particular solver's attempt at it. If the task sits between two adjacent levels, choose the lower one unless the higher level's requirement is clearly met.

Before giving a level, write a short assessment of the task against the rubric: what the task requires, which level's conditions it meets, and what keeps it below the next level. Give the level that this assessment supports. End with this sentence, with the level as a single digit:
The level of {demand} demanded by this task is: N"""


def build_natural_prompt(demand_name: str, rubric_content: str, task_instance: str) -> str:
    """The natural prompt for one (task, rubric) pair."""
    return TEMPLATE.format(demand=demand_name, rubric=rubric_content, task=task_instance)
