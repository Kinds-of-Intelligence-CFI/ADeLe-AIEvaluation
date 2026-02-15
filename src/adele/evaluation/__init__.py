"""
Model evaluation via Inspect AI.

Wraps Inspect AI to run models on benchmarks and collect
per-instance correctness data for ability profiling.
"""

from adele.evaluation.runner import evaluate_model, create_task, dataframe_to_samples

__all__ = ["evaluate_model", "create_task", "dataframe_to_samples"]
