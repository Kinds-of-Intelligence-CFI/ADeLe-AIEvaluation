"""
Benchmark data loading and formatting.

Provides utilities to load benchmarks from HuggingFace and prepare
them for demand-level annotation and model evaluation.
"""

from adele.data.battery import load_battery
from adele.data.loader import load_benchmark, load_from_file
from adele.data.registry import (
    BenchmarkConfig,
    get_benchmark,
    list_benchmarks,
    register_benchmark,
)

__all__ = [
    "load_benchmark",
    "load_from_file",
    "load_battery",
    "BenchmarkConfig",
    "get_benchmark",
    "list_benchmarks",
    "register_benchmark",
]
