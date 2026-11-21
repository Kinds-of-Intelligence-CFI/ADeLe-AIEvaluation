"""MathArena per-problem outputs → per-instance correctness.

Source: the HuggingFace datasets ``MathArena/aime_2025_outputs`` /
``MathArena/aime_2026_outputs`` (CC BY-NC-SA; per-problem model responses with
a ``correct`` bool; several judged samples per problem for some models), or a
local parquet/directory downloaded from them.

Columns observed (2026-08): problem_idx, model_name, correct, answer,
parsed_answer, gold_answer, cost, input_tokens, output_tokens, sample_idx (or
repeated rows per problem).
"""

import logging
from pathlib import Path
from typing import Optional

import pandas as pd

from adele.results.schema import merge_trials, normalize

logger = logging.getLogger(__name__)


def _load_frame(dataset: str, local_path: Optional[str]) -> pd.DataFrame:
    if local_path:
        p = Path(local_path)
        if p.is_dir():
            parts = sorted(p.rglob("*.parquet"))
            if not parts:
                raise FileNotFoundError(f"no parquet files under {p}")
            return pd.concat((pd.read_parquet(f) for f in parts), ignore_index=True)
        return pd.read_parquet(p)
    try:
        from datasets import load_dataset  # lazy; [annotate]/[agentic] extra
    except ImportError as exc:
        raise ImportError(
            "loading from the HuggingFace Hub needs the 'datasets' package "
            "(pip install \"adele[annotate]\") — or pass local_path= to a "
            "downloaded parquet"
        ) from exc
    return load_dataset(dataset, split="train").to_pandas()


def fetch(
    dataset: str = "MathArena/aime_2026_outputs",
    *,
    local_path: Optional[str] = None,
    benchmark: Optional[str] = None,
) -> pd.DataFrame:
    """Per-problem success rates per model (trials merged)."""
    raw = _load_frame(dataset, local_path)
    required = {"problem_idx", "model_name", "correct"}
    missing = required - set(raw.columns)
    if missing:
        raise ValueError(f"unexpected MathArena schema, missing {sorted(missing)}; "
                         f"columns = {list(raw.columns)}")
    bench = benchmark or dataset.rsplit("/", 1)[-1].replace("_outputs", "").replace("_", "-")
    df = pd.DataFrame({
        "instance_id": raw["problem_idx"].astype(str),
        "model": raw["model_name"].astype(str),
        "scaffold": "none",
        "success": raw["correct"].astype(float),
        "n_trials": 1,
    })
    df = normalize(df, benchmark=bench, source="matharena", trial_level=True)
    merged = merge_trials(df)
    logger.info("MathArena %s: %d problems × %d models (%d trial rows)",
                bench, merged["instance_id"].nunique(), merged["model"].nunique(), len(raw))
    return merged
