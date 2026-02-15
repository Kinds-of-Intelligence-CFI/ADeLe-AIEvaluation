"""
Model evaluation via Inspect AI.

Converts ADeLe benchmark data into Inspect AI Task objects and runs
model evaluations, extracting per-instance correctness for ability
profiling.

Usage:
    from adele.evaluation import evaluate_model

    results = evaluate_model(
        model="openai/gpt-4o",
        data=benchmark_df,    # DataFrame with prompt, custom_id, target
    )
"""

import logging
from typing import List, Optional

import pandas as pd

from inspect_ai import Task, eval as inspect_eval
from inspect_ai.dataset import Sample, MemoryDataset
from inspect_ai.solver import generate, multiple_choice
from inspect_ai.scorer import match, choice

logger = logging.getLogger(__name__)


def dataframe_to_samples(
    df: pd.DataFrame,
    *,
    task_type: str = "open-ended",
) -> List[Sample]:
    """Convert a benchmark DataFrame into Inspect AI Samples.

    Args:
        df:        DataFrame with ``prompt``, ``custom_id``, and
                   optionally ``target`` and ``choices`` columns.
        task_type: "open-ended" or "multiple-choice".

    Returns:
        List of Inspect AI Sample objects.
    """
    samples = []
    for _, row in df.iterrows():
        sample_kwargs = {
            "input": str(row["prompt"]),
            "id": str(row["custom_id"]),
        }

        if "target" in row and pd.notna(row.get("target")):
            sample_kwargs["target"] = str(row["target"])

        if "choices" in row and pd.notna(row.get("choices")):
            choices = row["choices"]
            if isinstance(choices, str):
                choices = [c.strip() for c in choices.split(",")]
            sample_kwargs["choices"] = choices

        samples.append(Sample(**sample_kwargs))

    return samples


def create_task(
    data: pd.DataFrame,
    *,
    task_type: str = "open-ended",
    name: str = "adele_eval",
) -> Task:
    """Create an Inspect AI Task from benchmark data.

    Args:
        data:      DataFrame with ``prompt``, ``custom_id``, ``target``.
        task_type: "open-ended" or "multiple-choice".
        name:      Task name for logging.

    Returns:
        An Inspect AI Task ready for evaluation.
    """
    samples = dataframe_to_samples(data, task_type=task_type)
    dataset = MemoryDataset(samples=samples, name=name)

    if task_type == "multiple-choice":
        return Task(
            dataset=dataset,
            solver=[multiple_choice()],
            scorer=choice(),
        )
    else:
        return Task(
            dataset=dataset,
            solver=[generate()],
            scorer=match(),
        )


def evaluate_model(
    model: str,
    data: pd.DataFrame,
    *,
    task_type: str = "open-ended",
    task_name: str = "adele_eval",
    max_samples: Optional[int] = None,
    log_dir: Optional[str] = None,
) -> pd.DataFrame:
    """Run a model evaluation using Inspect AI.

    Evaluates the given model on all instances in ``data`` and returns
    per-instance correctness results.

    Args:
        model:       Model identifier (e.g. "openai/gpt-4o",
                     "anthropic/claude-3-sonnet-20240229",
                     "hf/meta-llama/Llama-3-8B").
        data:        DataFrame with ``prompt``, ``custom_id``, ``target``.
        task_type:   "open-ended" or "multiple-choice".
        task_name:   Name for the evaluation task.
        max_samples: Maximum number of samples to evaluate.
        log_dir:     Directory for Inspect AI logs.

    Returns:
        DataFrame with columns:
        - ``custom_id``: Instance identifier.
        - ``correct``:   1 if the model answer was correct, 0 otherwise.
        - ``model_answer``: The model's response text.
    """
    if "target" not in data.columns:
        raise ValueError(
            "DataFrame must have a 'target' column for evaluation. "
            "Use adele.data.load_benchmark() with a target_column."
        )

    if max_samples and max_samples < len(data):
        data = data.head(max_samples)

    task = create_task(data, task_type=task_type, name=task_name)

    logger.info(
        "Evaluating %s on %d instances (task_type=%s)",
        model, len(data), task_type,
    )

    # Run evaluation
    eval_kwargs = {"model": model, "tasks": [task]}
    if log_dir:
        eval_kwargs["log_dir"] = log_dir

    results = inspect_eval(**eval_kwargs)

    # Extract per-instance results
    eval_log = results[0]
    instance_results = []

    if eval_log.samples:
        for sample in eval_log.samples:
            correct = 0
            if sample.scores:
                # Get the first scorer's value
                for scorer_name, score_obj in sample.scores.items():
                    val = score_obj.value
                    if val in ("C", "correct", 1, 1.0, True):
                        correct = 1
                    break

            # Extract model answer from the last assistant message
            model_answer = ""
            if sample.messages:
                for msg in reversed(sample.messages):
                    if msg.role == "assistant":
                        model_answer = msg.text if hasattr(msg, 'text') else str(msg.content)
                        break

            instance_results.append({
                "custom_id": sample.id,
                "correct": correct,
                "model_answer": model_answer,
            })

    result_df = pd.DataFrame(instance_results)
    n_correct = result_df["correct"].sum()
    logger.info(
        "Evaluation complete: %d/%d correct (%.1f%%)",
        n_correct, len(result_df), 100 * n_correct / max(1, len(result_df)),
    )

    return result_df
