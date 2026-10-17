"""
Prompt construction for demand-level annotation.

Ported and simplified from delean-batch-manager's ``files.py``.
Constructs the full instruction prompt sent to the LLM judge for
each (task_instance, rubric) pair.
"""


def is_reasoning_model(model: str) -> bool:
    """True for OpenAI reasoning models (o1/o3/o4…), which only accept the
    default temperature (so callers must omit a custom temperature)."""
    return model.split("/", 1)[-1].startswith(("o1", "o3", "o4"))


def build_annotation_prompt(
    demand_name: str,
    rubric_content: str,
    task_instance: str,
) -> str:
    """Build the full prompt for annotating one demand level.

    This is the core prompt that asks an LLM judge to score a task
    instance on a specific demand dimension using chain-of-thought
    reasoning.

    Args:
        demand_name:    Human-readable name of the demand
                        (e.g. "Attention and Scan").
        rubric_content: Full rubric text with level descriptions.
        task_instance:  The benchmark question / task to annotate.

    Returns:
        The complete prompt string.
    """
    instruction = (
        "INSTRUCTION: "
        f"Score the level of *{demand_name}* demanded by the given "
        "TASK INSTANCE using a discrete value from 0 to 5. "
        "Demand is a property of the task, not of any particular solver's "
        "behaviour; when in doubt between two adjacent levels, assign the "
        "lower unless the higher level's requirement is clearly met. "
        "Use CHAIN-OF-THOUGHTS REASONING to reason step by step "
        "before assigning the score. "
        "After the CHAIN-OF-THOUGHTS REASONING STEPS, conclude your "
        "assessment with the statement: "
        f'"Thus, the level of *{demand_name}* demanded by the given '
        'TASK INSTANCE is: SCORE"'
        ", where SCORE is an integer score you have determined."
    )

    full_prompt = (
        f"The following rubric describes six distinct levels of "
        f"*{demand_name}* required by different tasks:\n"
        f"{rubric_content}\n\n"
        f'TASK INSTANCE: {task_instance}\n\n'
        f'{instruction}\n\n'
        f"CHAIN-OF-THOUGHTS REASONING STEPS to score the level of "
        f"*{demand_name}* demanded by the given TASK INSTANCE above:"
    )

    return full_prompt


PROMPT_V2 = """We are annotating AI evaluation tasks for a research study on the cognitive demands that tasks make. Below are a rubric for {demand}, with levels from 0 to 5, and a task.

<rubric>
{rubric}
</rubric>

<task>
{task}
</task>

Rate the task's demand for {demand} according to the rubric, not any particular solver's attempt at it.

Before giving a level, write a short assessment of the task against the rubric: what the task requires, which level's conditions it meets, and what keeps it below the next level. Compare the task with the rubric's examples at the levels you consider. Base the level on the conditions the rubric states, not on how long or easy the work looks. If the task genuinely fits two adjacent levels, choose the lower one. Give the level that this assessment supports. End with this sentence, with the level as a single digit:
The level of {demand} demanded by this task is: N"""


PROMPT_V2_NOREASON = PROMPT_V2.replace(
    "Before giving a level, write a short assessment of the task against the rubric: what the task requires, which "
    "level's conditions it meets, and what keeps it below the next level. Compare the task with the rubric's examples "
    "at the levels you consider. Base the level on the conditions the rubric states, not on how long or easy the work "
    "looks. If the task genuinely fits two adjacent levels, choose the lower one. Give the level that this assessment "
    "supports. End with this sentence, with the level as a single digit:",
    "Give the level directly, without any assessment, explanation or other text. Base the level on the conditions the "
    "rubric states, not on how long or easy the work looks. If the task genuinely fits two adjacent levels, choose the "
    "lower one. Answer with the level alone, as a single digit from 0 to 5, and nothing else.",
).replace("\nThe level of {demand} demanded by this task is: N", "")
assert PROMPT_V2_NOREASON != PROMPT_V2


def build_annotation_prompt_v2_noreason(
    demand_name: str,
    rubric_content: str,
    task_instance: str,
) -> str:
    """The v2 prompt without written reasoning: the judge states the level only.

    Identical to :func:`build_annotation_prompt_v2` except the final instruction, which drops the assessment and the
    comparison with the rubric's examples and asks for the bare digit (no closing sentence). Built for the
    no-reasoning ablation (``experiments/benchmarks/noreason``).
    """
    return PROMPT_V2_NOREASON.format(demand=demand_name, rubric=rubric_content, task=task_instance)


def build_annotation_prompt_v2(
    demand_name: str,
    rubric_content: str,
    task_instance: str,
) -> str:
    """Build the v2 annotation prompt (adopted 2026-09-29).

    Same inputs as :func:`build_annotation_prompt`, in plain wording. The v1
    prompt asks for written "chain-of-thought" steps, which Sonnet 5.5's
    safeguards block; this one asks for a short assessment before the level.
    It was tested as variant B in ``experiments/benchmarks/natural-prompt``.
    The answer ends with "... is: N", which :func:`extract_demand_level`
    reads. The v1 builder stays for reproducing earlier runs.
    """
    return PROMPT_V2.format(demand=demand_name, rubric=rubric_content, task=task_instance)


def build_batch_request(
    custom_id: str,
    demand_acronym: str,
    prompt: str,
    model: str = "gpt-4o",
    max_completion_tokens: int = 1000,
) -> dict:
    """Build a single OpenAI Batch API request body.

    Returns a dict matching the JSONL format expected by the
    ``/v1/chat/completions`` batch endpoint.

    Args:
        custom_id:    Unique identifier for this request (e.g. "mmlu-0").
        demand_acronym: Rubric acronym (e.g. "AS").
        prompt:       The full annotation prompt (from ``build_annotation_prompt``).
        model:        OpenAI model to use.
        max_completion_tokens: Max tokens for the response.

    Returns:
        A dict ready to be serialised as one JSONL line.
    """
    body = {
        "model": model,
        "max_completion_tokens": max_completion_tokens,
        "messages": [
            {"role": "user", "content": prompt}
        ],
    }
    # Reasoning models (o1/o3/o4…) only accept the default temperature; sending
    # temperature=0 makes the batch request fail. Set it only for other models.
    if not is_reasoning_model(model):
        body["temperature"] = 0

    return {
        "custom_id": f"{custom_id}__{demand_acronym}",
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": body,
    }
