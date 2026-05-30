"""
Demand-level annotation engine.

Handles the full annotation lifecycle: prompt construction, batch job
management via OpenAI Batch API, and result parsing.

Prompt construction and result parsing depend only on the core deps, so they
import eagerly. ``annotate`` pulls in the heavy ``[annotate]`` extra (openai,
litellm, tenacity), so it resolves lazily (PEP 562) — importing this package, or
the light helpers from it, no longer requires those packages installed.
"""

import importlib

from adele.annotation.prompts import build_annotation_prompt, build_batch_request
from adele.annotation.parsing import (
    extract_demand_level,
    parse_batch_output,
    parse_multiple_outputs,
    to_wide_format,
    unguessability_from_choices,
)

# name -> submodule it lives in (imported lazily on first access).
_LAZY = {"annotate": "adele.annotation.annotator"}

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


def __getattr__(name: str):
    if name in _LAZY:
        return getattr(importlib.import_module(_LAZY[name]), name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return sorted(__all__)
