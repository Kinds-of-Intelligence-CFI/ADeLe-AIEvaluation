"""
Benchmark registry — pre-configured mappings for known datasets.

Each entry maps a short benchmark name to its HuggingFace dataset ID,
relevant split/subset information, and column mappings so that the
loader can produce a uniform schema with ``prompt`` and ``custom_id``
columns ready for demand annotation.

Users can register additional benchmarks at runtime.
"""

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


@dataclass
class BenchmarkConfig:
    """Configuration for loading a specific benchmark.

    Attributes:
        name:           Short human-readable name (e.g. "mmlu").
        hf_dataset_id:  HuggingFace dataset identifier (e.g. "cais/mmlu").
        hf_subset:      Optional subset / config name (e.g. "all").
        split:          Default split to load (e.g. "test").
        prompt_column:  Column containing the task text / question.
        id_column:      Column to use as unique ID (None → auto-generate).
        target_column:  Column containing the ground-truth answer (optional).
        prompt_template: Optional Jinja2-style or f-string template that
                         formats multiple columns into a single prompt.
                         Use ``{column_name}`` placeholders.
        description:    Short description of the benchmark.
    """
    name: str
    hf_dataset_id: str
    hf_subset: Optional[str] = None
    split: str = "test"
    prompt_column: str = "question"
    id_column: Optional[str] = None
    target_column: Optional[str] = "answer"
    choices_column: Optional[str] = None
    prompt_template: Optional[str] = None
    description: str = ""


# ============================================================================
# Built-in registry of ADeLe v1.0 battery benchmarks.
# These are the 20 benchmarks evaluated in the ADeLe paper.
# ============================================================================

_REGISTRY: Dict[str, BenchmarkConfig] = {}


def _register(cfg: BenchmarkConfig):
    _REGISTRY[cfg.name.lower()] = cfg


# -- ADeLe v1.0 Battery benchmarks --

_register(BenchmarkConfig(
    name="mmlu-pro",
    hf_dataset_id="TIGER-Lab/MMLU-Pro",
    split="test",
    prompt_column="question",
    id_column="question_id",
    target_column="answer",
    choices_column="options",
    prompt_template="{question}\n\nChoices:\n{options}",
    description="Massive Multitask Language Understanding — Pro edition",
))

_register(BenchmarkConfig(
    name="gsm8k",
    hf_dataset_id="openai/gsm8k",
    hf_subset="main",
    split="test",
    prompt_column="question",
    target_column="answer",
    description="Grade School Math 8K",
))

_register(BenchmarkConfig(
    name="math",
    hf_dataset_id="lighteval/MATH",
    split="test",
    prompt_column="problem",
    target_column="solution",
    description="Competition mathematics problems",
))

_register(BenchmarkConfig(
    name="omnimath",
    hf_dataset_id="KbsdJames/Omni-MATH",
    split="test",
    prompt_column="problem",
    target_column="solution",
    description="Olympiad-level mathematics",
))

_register(BenchmarkConfig(
    name="scibench",
    hf_dataset_id="xw27/scibench",
    split="test",
    prompt_column="problem_text",
    target_column="answer_number",
    description="Science benchmark (physics, chemistry, math)",
))

_register(BenchmarkConfig(
    name="medcalcbench",
    hf_dataset_id="ncbi/MedCalc-Bench",
    split="test",
    prompt_column="Question",
    target_column="Answer",
    description="Medical calculation benchmark",
))

_register(BenchmarkConfig(
    name="chemllmbench",
    hf_dataset_id="AI4Chem/ChemLLMBench",
    split="test",
    prompt_column="input",
    target_column="output",
    description="Chemistry language model benchmark",
))

_register(BenchmarkConfig(
    name="truthquest",
    hf_dataset_id="alessandrobessi/TruthQuest",
    split="test",
    prompt_column="question",
    target_column="answer",
    description="Truthfulness and factuality benchmark",
))

# Temporal reasoning benchmarks
_register(BenchmarkConfig(
    name="mctaco",
    hf_dataset_id="domenicrosati/MC-TACO",
    split="test",
    prompt_column="sentence",
    target_column="label",
    prompt_template="{sentence}\n\nQuestion: {question}\nAnswer: {answer}",
    description="Multiple Choice Temporal common-sense QA",
))

_register(BenchmarkConfig(
    name="tempreason",
    hf_dataset_id="sxiong/TRAM",
    split="test",
    prompt_column="question",
    target_column="answer",
    description="Temporal reasoning benchmark",
))

_register(BenchmarkConfig(
    name="timeqa",
    hf_dataset_id="hotpotqa/hotpot_qa",
    hf_subset="fullwiki",
    split="validation",
    prompt_column="question",
    target_column="answer",
    description="Time-sensitive QA",
))

_register(BenchmarkConfig(
    name="timedial",
    hf_dataset_id="google/TimeDial",
    split="test",
    prompt_column="context",
    target_column="correct1",
    description="Temporal commonsense in dialogues",
))

_register(BenchmarkConfig(
    name="menatqa",
    hf_dataset_id="drt/MenatQA",
    split="test",
    prompt_column="question",
    target_column="answer",
    description="Mental arithmetic QA",
))

# Standardised test benchmarks
_register(BenchmarkConfig(
    name="sat",
    hf_dataset_id="cais/sat",
    split="test",
    prompt_column="question",
    target_column="answer",
    description="SAT exam questions",
))

_register(BenchmarkConfig(
    name="lsat",
    hf_dataset_id="cais/lsat",
    split="test",
    prompt_column="question",
    target_column="answer",
    description="LSAT exam questions",
))

_register(BenchmarkConfig(
    name="gre-gmat",
    hf_dataset_id="cais/gre_gmat",
    split="test",
    prompt_column="question",
    target_column="answer",
    description="GRE & GMAT exam questions",
))

# Specialised benchmarks
_register(BenchmarkConfig(
    name="data-analysis",
    hf_dataset_id="cais/data_analysis",
    split="test",
    prompt_column="question",
    target_column="answer",
    description="Data analysis tasks",
))

_register(BenchmarkConfig(
    name="date-arithmetic",
    hf_dataset_id="cais/date_arithmetic",
    split="test",
    prompt_column="question",
    target_column="answer",
    description="Date arithmetic tasks",
))

_register(BenchmarkConfig(
    name="reasoning",
    hf_dataset_id="cais/reasoning",
    split="test",
    prompt_column="question",
    target_column="answer",
    description="General reasoning tasks",
))

_register(BenchmarkConfig(
    name="language",
    hf_dataset_id="cais/language",
    split="test",
    prompt_column="question",
    target_column="answer",
    description="Language understanding tasks",
))

_register(BenchmarkConfig(
    name="civil-service",
    hf_dataset_id="cais/civil_service",
    split="test",
    prompt_column="question",
    target_column="answer",
    description="Civil Service Examination questions",
))


# ============================================================================
# Registry API
# ============================================================================

def get_benchmark(name: str) -> Optional[BenchmarkConfig]:
    """Look up a benchmark config by name (case-insensitive)."""
    return _REGISTRY.get(name.lower())


def list_benchmarks() -> List[BenchmarkConfig]:
    """Return all registered benchmark configs, sorted by name."""
    return sorted(_REGISTRY.values(), key=lambda b: b.name)


def register_benchmark(config: BenchmarkConfig):
    """Register a custom benchmark config."""
    _REGISTRY[config.name.lower()] = config
