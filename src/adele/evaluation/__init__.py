"""
Model evaluation via Inspect AI.

Wraps Inspect AI to run models on benchmarks and collect
per-instance correctness data for ability profiling.

Also exposes the registered ``adele_battery`` task (run via
``inspect eval adele/adele_battery``) and the scoring/version helpers.
"""

from adele.evaluation.runner import (
    adele_battery,
    create_task,
    dataframe_to_samples,
    evaluate_model,
    results_from_log,
)
from adele.evaluation.scoring import adele_mc_scorer, adele_scorer
from adele.evaluation.version import (
    result_version,
    rubrics_version,
    scorer_suite_version,
    version_hash,
)

__all__ = [
    "evaluate_model",
    "results_from_log",
    "create_task",
    "dataframe_to_samples",
    "adele_battery",
    "adele_scorer",
    "adele_mc_scorer",
    "result_version",
    "rubrics_version",
    "scorer_suite_version",
    "version_hash",
]
