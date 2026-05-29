"""
Benchmark data loader — load any HuggingFace dataset for ADeLe.

Core function is ``load_benchmark()`` which returns a pandas DataFrame
with at minimum ``prompt`` and ``custom_id`` columns, ready for
demand-level annotation.

Usage:
    from adele.data import load_benchmark

    # Known benchmark (uses registry)
    df = load_benchmark("mmlu-pro")

    # Any HuggingFace dataset with column mapping
    df = load_benchmark(
        "bigcode/humanevalpack",
        prompt_column="prompt",
        id_column="task_id",
    )

    # With a custom prompt template
    df = load_benchmark(
        "cais/mmlu",
        hf_subset="anatomy",
        prompt_template="{question}\\nA. {A}\\nB. {B}\\nC. {C}\\nD. {D}",
    )
"""

import logging
import os
from typing import Optional

import pandas as pd

from adele.data.registry import (
    get_benchmark,
)

logger = logging.getLogger(__name__)


def load_benchmark(
    name_or_hf_id: str,
    *,
    hf_subset: Optional[str] = None,
    split: Optional[str] = None,
    prompt_column: Optional[str] = None,
    id_column: Optional[str] = None,
    target_column: Optional[str] = None,
    choices_column: Optional[str] = None,
    prompt_template: Optional[str] = None,
    max_samples: Optional[int] = None,
    hf_token: Optional[str] = None,
) -> pd.DataFrame:
    """Load a benchmark dataset and format it for ADeLe annotation."""
    # 1. Try the registry first
    cfg = get_benchmark(name_or_hf_id)

    if cfg is not None:
        hf_id = cfg.hf_dataset_id
        hf_subset = hf_subset or cfg.hf_subset
        split = split or cfg.split
        prompt_column = prompt_column or cfg.prompt_column
        id_column = id_column or cfg.id_column
        target_column = target_column or cfg.target_column
        choices_column = choices_column or cfg.choices_column
        prompt_template = prompt_template or cfg.prompt_template
        logger.info(
            "Using registered benchmark '%s' → %s", cfg.name, hf_id
        )
        if not cfg.verified:
            logger.warning(
                "Benchmark '%s' is UNVERIFIED (%s). Confirm/override the "
                "HF id, split, and columns before relying on results.",
                cfg.name, cfg.description,
            )
    else:
        hf_id = name_or_hf_id
        split = split or "test"
        prompt_column = prompt_column or "question"
        logger.info(
            "No registry entry for '%s'; loading as raw HF dataset", hf_id
        )

    # 2. Load from HuggingFace
    from datasets import load_dataset  # lazy import

    logger.info("Loading dataset '%s' (subset=%s, split=%s)", hf_id, hf_subset, split)

    ds = load_dataset(
        hf_id,
        name=hf_subset,
        split=split,
        token=hf_token or os.environ.get("HF_TOKEN"),  # gated datasets via env
    )

    if max_samples is not None:
        ds = ds.select(range(min(max_samples, len(ds))))

    df = ds.to_pandas()
    logger.info("Loaded %d rows, columns: %s", len(df), list(df.columns))

    # 3. Build the output DataFrame
    result = _build_output(
        df,
        prompt_column=prompt_column,
        id_column=id_column,
        target_column=target_column,
        choices_column=choices_column,
        prompt_template=prompt_template,
        benchmark_name=cfg.name if cfg else hf_id,
    )

    logger.info("Prepared %d instances for annotation", len(result))
    return result


def load_from_file(
    path: str,
    *,
    prompt_column: str = "prompt",
    id_column: Optional[str] = "custom_id",
    target_column: Optional[str] = None,
    choices_column: Optional[str] = None,
) -> pd.DataFrame:
    """Load benchmark data from a local CSV, JSONL, or Parquet file."""
    path_lower = str(path).lower()
    if path_lower.endswith(".csv"):
        df = pd.read_csv(path)
    elif path_lower.endswith(".jsonl"):
        df = pd.read_json(path, lines=True)
    elif path_lower.endswith(".parquet"):
        df = pd.read_parquet(path)
    else:
        raise ValueError(f"Unsupported file type: {path}")

    return _build_output(
        df,
        prompt_column=prompt_column,
        id_column=id_column,
        target_column=target_column,
        choices_column=choices_column,
        benchmark_name="local",
    )


# ============================================================================
# Internal helpers
# ============================================================================

def _build_output(
    df: pd.DataFrame,
    *,
    prompt_column: str,
    id_column: Optional[str],
    target_column: Optional[str],
    choices_column: Optional[str] = None,
    prompt_template: Optional[str] = None,
    benchmark_name: str = "benchmark",
) -> pd.DataFrame:
    """Build a standardised output DataFrame from raw data."""
    result = pd.DataFrame()

    # -- Prompt --
    if prompt_template:
        result["prompt"] = df.apply(
            lambda row: _format_template(prompt_template, row), axis=1
        )
    elif prompt_column in df.columns:
        # Some datasets store the prompt as a list (e.g. LiveBench's `turns`);
        # join those into plain text rather than stringifying the list.
        result["prompt"] = df[prompt_column].map(_prompt_to_text)
    else:
        available = ", ".join(df.columns[:10])
        raise ValueError(
            f"Column '{prompt_column}' not found in dataset. "
            f"Available columns: {available}..."
        )

    # -- Custom ID --
    if id_column and id_column in df.columns:
        result["custom_id"] = df[id_column].astype(str)
    else:
        result["custom_id"] = [
            f"{benchmark_name}-{i}" for i in range(len(df))
        ]

    # -- Target --
    if target_column and target_column in df.columns:
        result["target"] = df[target_column].astype(str)

    # -- Choices --
    if choices_column and choices_column in df.columns:
        result["choices"] = df[choices_column]

    return result.reset_index(drop=True)


def _prompt_to_text(value) -> str:
    """Coerce a prompt cell to text, joining list/array values with newlines."""
    if isinstance(value, (list, tuple)):
        return "\n".join(str(v) for v in value)
    if hasattr(value, "tolist") and not isinstance(value, (str, bytes)):
        return "\n".join(str(v) for v in value.tolist())
    return str(value)


def _format_template(template: str, row: pd.Series) -> str:
    """Format a prompt template using values from a DataFrame row.

    Supports ``{column_name}`` placeholders. If a column contains a list
    (e.g. multiple-choice options), it's joined with newlines.
    """
    values = {}
    for col in row.index:
        val = row[col]
        if isinstance(val, (list, tuple)):
            # Format lists as newline-separated (e.g. MC options)
            formatted = "\n".join(
                f"{chr(65 + i)}. {v}" for i, v in enumerate(val)
            )
            values[col] = formatted
        else:
            values[col] = str(val)
    try:
        return template.format(**values)
    except KeyError as e:
        logger.warning("Template key %s not found in row columns", e)
        return template
