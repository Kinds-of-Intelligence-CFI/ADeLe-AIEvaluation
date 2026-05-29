"""
ADeLe — Annotated Demand Levels for AI Evaluation.

A unified Python toolkit that provides:
  - Benchmark loading from HuggingFace
  - Demand-level annotation via LLM judges
  - Model evaluation via Inspect AI
  - Demand & ability profile generation
  - Predictive power analysis

Quick Start:
    import adele

    # Load a benchmark and annotate its demand levels (needs an API key)
    df = adele.load_benchmark("mmlu-pro", max_samples=50)
    annotations = adele.annotate(df, model="gpt-4o")

    # Evaluate a model on the pre-annotated ADeLe battery (needs HF_TOKEN)
    battery = adele.load_battery(answer_format="MC", max_samples=50)
    results = adele.evaluate("openai/gpt-4o", battery)

The names above resolve lazily (PEP 562), so ``import adele`` stays cheap and
only pulls in heavy optional deps (litellm, inspect_ai, …) on first use.
"""

import importlib

__version__ = "0.1.0"
__author__ = "Kinds of Intelligence Team at CFI"

# Public top-level API → (submodule, attribute). ``evaluate`` aliases
# ``evaluate_model``; the rest keep their names.
_LAZY = {
    "annotate": ("adele.annotation", "annotate"),
    "load_benchmark": ("adele.data", "load_benchmark"),
    "load_battery": ("adele.data", "load_battery"),
    "evaluate": ("adele.evaluation", "evaluate_model"),
}

__all__ = ["__version__", "__author__", *_LAZY]


def __getattr__(name: str):
    if name in _LAZY:
        module, attr = _LAZY[name]
        return getattr(importlib.import_module(module), attr)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return sorted(__all__)
