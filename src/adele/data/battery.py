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

from adele.constants import DEMAND_ORDER, LEGACY_DEMAND_ALIASES

logger = logging.getLogger(__name__)

HF_REPO = "CFI-Kinds-of-Intelligence/ADeLe_battery_v1dot0"
HF_FILE = "ADeLe_batterry_v1dot0.csv"  # upstream filename spelling

# The 18 DeLeAn v1.0 demand dimensions (annotated 0-5), from the shared taxonomy.
DEMAND_COLS = DEMAND_ORDER


_GATED_HELP = (
    "Could not download the ADeLe battery from HuggingFace ({repo}).\n"
    "The dataset is GATED: you must (1) request access at\n"
    "https://huggingface.co/datasets/{repo} with your HF account, and\n"
    "(2) provide a token for that account via hf_token= or the HF_TOKEN env var.\n"
    "Alternatively, use a local copy of the battery CSV:\n"
    "  - pass csv_path=... (Inspect: -T csv_path=...), or\n"
    "  - set the ADELE_BATTERY_CSV env var, or\n"
    "  - use the copy shipped in the repo at ADeLe_battery_data/ (run `git lfs pull` first).\n"
    "Original error: {err}"
)


def _resolve_csv_path(csv_path: Optional[str], hf_token: Optional[str]) -> str:
    """Local path > ADELE_BATTERY_CSV env > download from HuggingFace."""
    path = csv_path or os.environ.get("ADELE_BATTERY_CSV")
    if path:
        return path
    from huggingface_hub import hf_hub_download  # lazy import

    logger.info("Downloading ADeLe battery from HuggingFace (%s)", HF_REPO)
    try:
        return hf_hub_download(
            repo_id=HF_REPO,
            filename=HF_FILE,
            repo_type="dataset",
            token=hf_token or os.environ.get("HF_TOKEN"),
        )
    except Exception as err:  # gated-repo / auth / network errors alike
        raise RuntimeError(_GATED_HELP.format(repo=HF_REPO, err=err)) from err


def _check_not_lfs_pointer(path: str) -> None:
    """Fail fast (and helpfully) when ``path`` is a git-lfs pointer, not the CSV.

    The in-repo battery CSV is stored with git-lfs; without ``git lfs pull`` the
    file on disk is a 3-line pointer whose text would otherwise be parsed as a
    one-column CSV and die much later with a confusing ``KeyError``.
    """
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            head = f.read(64)
    except OSError:
        return  # let pd.read_csv raise its own, clearer file error
    if head.startswith("version https://git-lfs"):
        raise RuntimeError(
            f"{path} is a git-lfs POINTER, not the battery CSV. "
            "Run `git lfs install && git lfs pull` in the repository "
            "(or download the CSV from HuggingFace) and try again."
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
    _check_not_lfs_pointer(path)
    df = pd.read_csv(path)

    if answer_format is not None:
        df = df[df["answer_format"] == answer_format]
    if benchmark is not None:
        df = df[df["benchmark"] == benchmark]

    # Map to the toolkit's uniform schema (prompt/custom_id/target).
    df = df.rename(columns={"instance_id": "custom_id", "groundtruth": "target"})
    # The released battery predates the MS -> MSm rename; map it on load so the
    # published CSV keeps working untouched. See adele.constants.LEGACY_DEMAND_ALIASES.
    df = df.rename(columns={k: v for k, v in LEGACY_DEMAND_ALIASES.items() if k in df.columns})

    keep = [
        "custom_id", "prompt", "target", "answer_format",
        "benchmark", "source", "task", "UG", "verification_final",
    ] + [c for c in DEMAND_COLS if c in df.columns]
    df = df[[c for c in keep if c in df.columns]].reset_index(drop=True)

    if max_samples is not None and max_samples < len(df):
        df = df.head(max_samples)

    logger.info("Loaded %d battery instances from %s", len(df), path)
    return df
