"""Load the pre-annotated ADeLe v1.0 battery.

Unlike :func:`adele.data.load_benchmark` (which loads *source* benchmarks to be
annotated), this loads the ready-to-run ADeLe battery — a single gated CSV on
HuggingFace (``CFI-Kinds-of-Intelligence/ADeLe_battery_v1dot0``) where every
instance already carries its prompt, gold answer, answer format, and the 18
DeLeAn demand levels.

The returned DataFrame uses the toolkit's uniform schema (``prompt``,
``custom_id``, ``target``) plus battery-specific columns, so it can be passed
straight to :func:`adele.evaluation.evaluate_model` and joined back to the demand
annotations (by ``custom_id``) for ability profiling.

Usage:
    from adele.data import load_battery

    df = load_battery(answer_format="MC", max_samples=50)  # needs HF_TOKEN
    df = load_battery(csv_path="ADeLe_batterry_v1dot0.csv")  # local copy
"""

import logging
import os
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)

HF_REPO = "CFI-Kinds-of-Intelligence/ADeLe_battery_v1dot0"
HF_FILE = "ADeLe_batterry_v1dot0.csv"  # upstream filename spelling

# The 18 DeLeAn v1.0 demand dimensions (annotated 0-5). Mirrors
# adele.analysis.constants.DEMAND_ORDER; kept local so the evaluation/data path
# does not pull in the analysis (sklearn/matplotlib) dependencies.
DEMAND_COLS = [
    "AS", "CEc", "CEe", "CL", "MCr", "MCt", "MCu", "MS",
    "QLl", "QLq", "SNs", "KNa", "KNc", "KNf", "KNn", "KNs", "AT", "VO",
]


def _resolve_csv_path(csv_path: Optional[str], hf_token: Optional[str]) -> str:
    """Local path > ADELE_BATTERY_CSV env > download from HuggingFace."""
    path = csv_path or os.environ.get("ADELE_BATTERY_CSV")
    if path:
        return path
    from huggingface_hub import hf_hub_download  # lazy import

    logger.info("Downloading ADeLe battery from HuggingFace (%s)", HF_REPO)
    return hf_hub_download(
        repo_id=HF_REPO,
        filename=HF_FILE,
        repo_type="dataset",
        token=hf_token or os.environ.get("HF_TOKEN"),
    )


def load_battery(
    *,
    answer_format: Optional[str] = None,
    benchmark: Optional[str] = None,
    max_samples: Optional[int] = None,
    hf_token: Optional[str] = None,
    csv_path: Optional[str] = None,
) -> pd.DataFrame:
    """Load the ADeLe v1.0 battery as a DataFrame.

    Args:
        answer_format: filter to "MC" or "Open-ended" (default: both).
        benchmark:     filter to a single source benchmark (e.g. "MMLU-Pro").
        max_samples:   cap the number of rows (use for dry runs / cost control).
        hf_token:      HuggingFace token for the gated dataset (else HF_TOKEN env).
        csv_path:      local battery CSV (else ADELE_BATTERY_CSV env, else HF download).

    Returns:
        DataFrame with columns: ``custom_id``, ``prompt``, ``target``,
        ``answer_format``, ``benchmark``, ``source``, ``task``, ``UG``,
        ``verification_final``, and the 18 demand columns.
    """
    path = _resolve_csv_path(csv_path, hf_token)
    df = pd.read_csv(path)

    if answer_format is not None:
        df = df[df["answer_format"] == answer_format]
    if benchmark is not None:
        df = df[df["benchmark"] == benchmark]

    # Map to the toolkit's uniform schema (prompt/custom_id/target).
    df = df.rename(columns={"instance_id": "custom_id", "groundtruth": "target"})

    keep = [
        "custom_id", "prompt", "target", "answer_format",
        "benchmark", "source", "task", "UG", "verification_final",
    ] + [c for c in DEMAND_COLS if c in df.columns]
    df = df[[c for c in keep if c in df.columns]].reset_index(drop=True)

    if max_samples is not None and max_samples < len(df):
        df = df.head(max_samples)

    logger.info("Loaded %d battery instances from %s", len(df), path)
    return df
