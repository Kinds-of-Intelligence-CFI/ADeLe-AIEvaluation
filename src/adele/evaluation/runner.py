"""
Model evaluation via Inspect AI.

Converts ADeLe benchmark data into Inspect AI Task objects and runs
model evaluations, extracting per-instance correctness for ability
profiling.

Two paths:

* **Battery** (data has an ``answer_format`` column, e.g. from
  :func:`adele.data.load_battery`): scored faithfully to the ADeLe v1.0
  verification conventions via a per-sample dispatching scorer — MC by
  option-letter match, Open-ended by a model-graded judge. The 18 demand
  levels ride through into the Inspect log via ``Sample.metadata``. The
  registered ``adele_battery`` task runs this directly:

      inspect eval adele/adele_battery --model openai/gpt-4o -T answer_format=MC

* **Generic benchmark** (no ``answer_format``): legacy whole-dataset scoring
  (``choice``/``match``), used for ad-hoc benchmarks.

Usage:
    from adele.evaluation import evaluate_model
    from adele.data import load_battery

    results = evaluate_model(
        model="openai/gpt-4o",
        data=load_battery(answer_format="MC", max_samples=50),
    )
"""

import logging
from typing import List, Optional, Union

import pandas as pd

from inspect_ai import Task, eval as inspect_eval, task
from inspect_ai.dataset import MemoryDataset, Sample
from inspect_ai.model import Model
from inspect_ai.scorer import CORRECT, choice, match
from inspect_ai.solver import Solver, generate, multiple_choice

from adele.data.battery import DEMAND_COLS
from adele.evaluation.scoring import adele_scorer
from adele.evaluation.version import result_version, version_hash

logger = logging.getLogger(__name__)

# Battery columns carried through into Sample.metadata (for post-hoc profiling).
_META_COLS = DEMAND_COLS + ["UG", "answer_format", "benchmark", "source", "task", "verification_final"]


def _model_name(model: Optional[Union[str, Model]]) -> Optional[str]:
    """Stable string name for a model spec (for the version key)."""
    if model is None:
        return None
    return model if isinstance(model, str) else getattr(model, "name", str(model))


def dataframe_to_samples(df: pd.DataFrame) -> List[Sample]:
    """Convert a benchmark DataFrame into Inspect AI Samples.

    Args:
        df: DataFrame with ``prompt``, ``custom_id``, optionally ``target`` and
            ``choices``. Battery DataFrames additionally carry ``answer_format``
            and the demand columns, which are passed through ``Sample.metadata``.

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

        metadata = {c: row[c] for c in _META_COLS if c in row and pd.notna(row.get(c))}
        if metadata:
            sample_kwargs["metadata"] = metadata

        samples.append(Sample(**sample_kwargs))

    return samples


def create_task(
    data: pd.DataFrame,
    *,
    task_type: str = "open-ended",
    name: str = "adele_eval",
    judge_model: Optional[Union[str, Model]] = None,
    solver: Optional[Solver] = None,
) -> Task:
    """Create an Inspect AI Task from benchmark data.

    If ``data`` has an ``answer_format`` column (the ADeLe battery), it is scored
    with the faithful per-sample dispatch scorer (``task_type`` is ignored).
    Otherwise the legacy whole-dataset ``task_type`` scoring is used.

    Args:
        data:        DataFrame with ``prompt``, ``custom_id``, ``target``.
        task_type:   "open-ended" or "multiple-choice" (generic path only).
        name:        Task name for logging.
        judge_model: model used to grade Open-ended battery samples.
        solver:      override the default ``generate()`` solver.

    Returns:
        An Inspect AI Task ready for evaluation.
    """
    samples = dataframe_to_samples(data)
    dataset = MemoryDataset(samples=samples, name=name)
    metadata = {
        "adele_version": result_version(_model_name(judge_model)),
        "adele_version_hash": version_hash(_model_name(judge_model)),
    }

    # Battery path: faithful per-sample dispatch (MC + model-graded open-ended).
    if "answer_format" in data.columns:
        return Task(
            dataset=dataset,
            solver=[solver or generate()],
            scorer=adele_scorer(judge_model),
            metadata=metadata,
        )

    # Generic benchmark path (legacy behavior).
    if task_type == "multiple-choice":
        return Task(dataset=dataset, solver=[multiple_choice()], scorer=choice(), metadata=metadata)
    return Task(dataset=dataset, solver=[solver or generate()], scorer=match(), metadata=metadata)


@task
def adele_battery(
    answer_format: Optional[str] = None,
    benchmark: Optional[str] = None,
    limit: Optional[int] = None,
    judge_model: Optional[str] = None,
    csv_path: Optional[str] = None,
) -> Task:
    """The ADeLe v1.0 battery as a runnable Inspect task.

    Examples:
        inspect eval adele/adele_battery --model openai/gpt-4o -T answer_format=MC -T limit=50
        inspect eval adele/adele_battery --model openai/gpt-4o \
            -T answer_format=Open-ended -T judge_model=openai/gpt-4o

    Args:
        answer_format: "MC" or "Open-ended" (default: both).
        benchmark:     filter to one source benchmark (e.g. "MMLU-Pro").
        limit:         cap the number of samples (dry runs / cost control).
        judge_model:   judge for Open-ended scoring (required to score them).
        csv_path:      local battery CSV (else ADELE_BATTERY_CSV env / HF download).
    """
    from adele.data.battery import load_battery

    data = load_battery(
        answer_format=answer_format,
        benchmark=benchmark,
        max_samples=limit,
        csv_path=csv_path,
    )
    return create_task(data, name="adele_battery", judge_model=judge_model)


def evaluate_model(
    model: str,
    data: pd.DataFrame,
    *,
    task_type: str = "open-ended",
    judge_model: Optional[Union[str, Model]] = None,
    task_name: str = "adele_eval",
    max_samples: Optional[int] = None,
    log_dir: Optional[str] = None,
) -> pd.DataFrame:
    """Run a model evaluation using Inspect AI.

    Args:
        model:       Model identifier (e.g. "openai/gpt-4o").
        data:        DataFrame with ``prompt``, ``custom_id``, ``target``.
        task_type:   generic-path scoring ("open-ended"/"multiple-choice");
                     ignored for battery data (scored by ``answer_format``).
        judge_model: judge for Open-ended battery scoring.
        task_name:   name for the evaluation task.
        max_samples: maximum number of samples to evaluate.
        log_dir:     directory for Inspect AI logs.

    Returns:
        DataFrame with columns ``custom_id``, ``correct`` (1/0), ``model_answer``.
        Join to the battery (by ``custom_id``) for demand-based ability profiling.
    """
    if "target" not in data.columns:
        raise ValueError(
            "DataFrame must have a 'target' column for evaluation. "
            "Use adele.data.load_benchmark()/load_battery() with a target."
        )

    if max_samples and max_samples < len(data):
        data = data.head(max_samples)

    task_obj = create_task(
        data, task_type=task_type, name=task_name, judge_model=judge_model
    )

    logger.info("Evaluating %s on %d instances", model, len(data))

    eval_kwargs = {"model": model, "tasks": [task_obj]}
    if log_dir:
        eval_kwargs["log_dir"] = log_dir

    results = inspect_eval(**eval_kwargs)
    eval_log = results[0]

    instance_results = []
    for sample in eval_log.samples or []:
        correct = 0
        if sample.scores:
            score_obj = next(iter(sample.scores.values()))
            if score_obj.value in (CORRECT, "correct", 1, 1.0, True):
                correct = 1

        model_answer = ""
        for msg in reversed(sample.messages or []):
            if msg.role == "assistant":
                model_answer = msg.text if hasattr(msg, "text") else str(msg.content)
                break

        instance_results.append(
            {"custom_id": sample.id, "correct": correct, "model_answer": model_answer}
        )

    result_df = pd.DataFrame(instance_results)
    n_correct = int(result_df["correct"].sum()) if len(result_df) else 0
    logger.info(
        "Evaluation complete: %d/%d correct (%.1f%%)",
        n_correct, len(result_df), 100 * n_correct / max(1, len(result_df)),
    )
    return result_df
