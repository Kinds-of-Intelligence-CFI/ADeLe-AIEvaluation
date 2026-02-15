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

    # Annotate demand levels for a benchmark
    annotations = adele.annotate(benchmark="mmlu", api_key="sk-...")

    # Full evaluation pipeline
    results = adele.evaluate(model="openai/gpt-4o", benchmark="mmlu")
"""

__version__ = "0.1.0"
__author__ = "Kinds of Intelligence Team at CFI"
