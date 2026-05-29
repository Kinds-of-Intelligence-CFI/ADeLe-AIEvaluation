"""
Demand-level annotation engine.

Handles the full annotation lifecycle: prompt construction, batch job
management via OpenAI Batch API, and result parsing.
"""

from adele.annotation.annotator import annotate
from adele.annotation.prompts import build_annotation_prompt, build_batch_request
from adele.annotation.parsing import (
    extract_demand_level,
    parse_batch_output,
    parse_multiple_outputs,
    to_wide_format,
    unguessability_from_choices,
)

__all__ = [
    "annotate",
    "build_annotation_prompt",
    "build_batch_request",
    "extract_demand_level",
    "parse_batch_output",
    "parse_multiple_outputs",
    "to_wide_format",
    "unguessability_from_choices",
]
