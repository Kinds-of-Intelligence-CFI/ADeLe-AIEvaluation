"""
Benchmark registry — pre-configured mappings for known datasets.

Each entry maps a short benchmark name to its HuggingFace dataset ID,
relevant split/subset information, and column mappings so that the
loader can produce a uniform schema with ``prompt`` and ``custom_id``
columns ready for demand annotation.

Users can register additional benchmarks at runtime.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


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
        verified:       True if the HF id/subset/split/columns have been
                         confirmed against the Hub. False marks entries whose
                         source could not be confirmed (load_benchmark warns).
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
    verified: bool = True


# ============================================================================
# Built-in registry of the source benchmarks behind the ADeLe v1.0 battery.
#
# Grounded in the paper's Table 11 (arXiv:2503.06378v2). The battery draws on
# 20 benchmarks, several of which are *umbrella* sources:
#   - AGIEval [187]: SAT (SAT-En/Math), LSAT (AR/LR/RC), LogiQA-en (= China
#     civil-service exam), AQuA-RAT (= GRE & GMAT).
#   - LiveBench [179]: categories reasoning, language, data analysis (+ math).
#   - TimeBench [27]: Date Arithmetic, MCTACO, MenatQA, TempReason, TimeDial,
#     TimeQA (the temporal-reasoning cluster).
# The registry lists them at category/sub-benchmark granularity, so it has a
# few more than 20 entries.
#
# These are convenience pointers for the *annotation* path only — they are NOT
# needed to run the pre-annotated battery (use adele.data.load_battery, which
# loads the gated CSV from HuggingFace). IDs were corrected against the Hub;
# entries still marked ``verified=False`` could not be confirmed to a public
# dataset (or their exact columns/splits are unverified) and will warn on load.
# ============================================================================

_REGISTRY: Dict[str, BenchmarkConfig] = {}


def _register(cfg: BenchmarkConfig):
    _REGISTRY[cfg.name.lower()] = cfg


# -- Standalone benchmarks --

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
    hf_dataset_id="DigitalLearningGmbH/MATH-lighteval",  # lighteval/MATH was taken down
    split="test",
    prompt_column="problem",
    target_column="solution",
    description="Competition mathematics problems (MATH)",
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
    split="train",  # only a train split is published
    prompt_column="problem_text",
    target_column="answer_number",
    description="Science benchmark (physics, chemistry, math)",
))

_register(BenchmarkConfig(
    name="medcalcbench",
    hf_dataset_id="ncbi/MedCalc-Bench",
    split="test",
    prompt_column="Question",
    target_column="Ground Truth Answer",  # not "Answer"
    description="Medical calculation benchmark",
))

_register(BenchmarkConfig(
    name="chemllmbench",
    hf_dataset_id="AI4Chem/ChemLLMBench",
    split="test",
    prompt_column="input",
    target_column="output",
    description="Chemistry LLM benchmark — GitHub-only (ChemFoundationModels/"
                "ChemLLMBench); no confirmed public HF mirror at this id",
    verified=False,
))

_register(BenchmarkConfig(
    name="truthquest",
    hf_dataset_id="mainlp/TruthQuest",  # was alessandrobessi/TruthQuest (wrong)
    split="test",
    prompt_column="Problem",       # list of statements (joined by the loader)
    target_column="Solutions",     # structured (list of {name: is_knight})
    description="TruthQuest — suppositional reasoning. Gated; 12 subsets "
                "(E/I/S × n=3..6, no default config); Solutions is structured",
    verified=False,
))

# -- Temporal reasoning benchmarks --

_register(BenchmarkConfig(
    name="mctaco",
    hf_dataset_id="CogComp/mc_taco",  # was domenicrosati/MC-TACO
    split="test",
    prompt_column="sentence",
    target_column="label",
    prompt_template="{sentence}\n\nQuestion: {question}\nAnswer: {answer}",
    description="MCTACO — multiple-choice temporal commonsense QA (TimeBench)",
))

_register(BenchmarkConfig(
    name="tempreason",
    hf_dataset_id="tonytan48/TempReason",  # was sxiong/TRAM (different/nonexistent)
    split="test",
    prompt_column="question",
    target_column="text_answers",
    description="TempReason (L2/L3) — event temporal reasoning (TimeBench). "
                "Upstream load is broken (schema mismatch in train_l2.json); "
                "needs a fixed config before it will load",
    verified=False,
))

_register(BenchmarkConfig(
    name="timeqa",
    hf_dataset_id="hugosousa/TimeQA",  # was hotpotqa/hotpot_qa (wrong dataset)
    split="test",
    prompt_column="question",
    target_column="targets",
    description="TimeQA (explicit/implicit) — event temporal reasoning (TimeBench)",
))

_register(BenchmarkConfig(
    name="timedial",
    hf_dataset_id="google-research-datasets/time_dial",  # was google/TimeDial
    split="test",
    prompt_column="conversation",  # list of dialogue turns (joined by the loader)
    target_column="correct1",
    description="TimeDial — temporal commonsense in dialogues (TimeBench)",
))

_register(BenchmarkConfig(
    name="menatqa",
    hf_dataset_id="drt/MenatQA",
    split="test",
    prompt_column="question",
    target_column="answer",
    description="MenatQA (counterfactual/order/scope) — event temporal "
                "reasoning (TimeBench); GitHub-only (weiyifan1023/MenatQA)",
    verified=False,
))

# -- AGIEval exams (lighteval/agi_eval_en: question/options/label, split=train) --

_register(BenchmarkConfig(
    name="sat",
    hf_dataset_id="lighteval/agi_eval_en",
    hf_subset="sat-en",
    split="train",
    prompt_column="question",
    target_column="label",
    choices_column="options",
    description="SAT — AGIEval SAT-En (battery also uses SAT-Math)",
))

_register(BenchmarkConfig(
    name="lsat",
    hf_dataset_id="lighteval/agi_eval_en",
    hf_subset="lsat-lr",
    split="train",
    prompt_column="question",
    target_column="label",
    choices_column="options",
    description="LSAT — AGIEval LSAT-LR (battery also uses LSAT-AR, LSAT-RC)",
))

_register(BenchmarkConfig(
    name="gre-gmat",
    hf_dataset_id="lighteval/agi_eval_en",
    hf_subset="aqua_rat",
    split="train",
    prompt_column="question",
    target_column="label",
    choices_column="options",
    description="GRE & GMAT — AGIEval AQuA-RAT (Table 11)",
))

_register(BenchmarkConfig(
    name="civil-service",
    hf_dataset_id="lighteval/agi_eval_en",
    hf_subset="logiqa-en",
    split="train",
    prompt_column="question",
    target_column="label",
    choices_column="options",
    description="AGIEval LogiQA (sourced from the China civil-service exam)",
))

# -- LiveBench categories (livebench/*: prompt in `turns`, answer `ground_truth`) --

_register(BenchmarkConfig(
    name="data-analysis",
    hf_dataset_id="livebench/data_analysis",
    split="test",
    prompt_column="turns",
    target_column="ground_truth",
    description="LiveBench — data analysis category",
))

_register(BenchmarkConfig(
    name="date-arithmetic",
    hf_dataset_id="zchuz/TimeBench",  # GitHub source; no confirmed standalone HF dataset
    split="test",
    prompt_column="question",
    target_column="answer",
    description="TimeBench — Date Arithmetic (symbolic temporal reasoning, "
                "Table 11); GitHub zchuz/TimeBench, no public HF dataset",
    verified=False,
))

_register(BenchmarkConfig(
    name="reasoning",
    hf_dataset_id="livebench/reasoning",
    split="test",
    prompt_column="turns",
    target_column="ground_truth",
    description="LiveBench — reasoning category",
))

_register(BenchmarkConfig(
    name="language",
    hf_dataset_id="livebench/language",
    split="test",
    prompt_column="turns",
    target_column="ground_truth",
    description="LiveBench — language category",
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
