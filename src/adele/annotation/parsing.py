"""
Output parsing for demand-level annotation results.

Ported and simplified from delean-batch-manager's ``parse.py``.
Extracts demand levels (0–5) from LLM chain-of-thought responses.
"""

import re
import json
import logging
from pathlib import Path
from typing import List, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def extract_demand_level(response: str) -> tuple[float, bool]:
    """Extract the demand level (0–5) from an LLM response.

    The LLM is instructed to conclude with:
        "Thus, the level of *X* demanded by the given TASK INSTANCE is: SCORE"

    This function finds the last integer in the final paragraph.

    Args:
        response: Full LLM response text.

    Returns:
        (level, success): The extracted level (0–5) and whether extraction
        succeeded. On failure, level is ``float('nan')``.
    """
    if not response or not response.strip():
        return float("nan"), False

    # First try: look for the structured conclusion pattern
    # "the level of *X* demanded by the given TASK INSTANCE is: SCORE"
    # Match the full number (\d+) so a stray multi-digit value like "is: 12"
    # is rejected as out-of-range rather than silently truncated to "1".
    structured = re.findall(r'is:\s*(\d+)', response)
    if structured:
        level = float(structured[-1])
        if 0 <= level <= 5:
            return level, True

    # Fallback: split into paragraphs; conclusion should be in the last one
    *_, conclusion = response.split("\n\n")

    try:
        matches = re.findall(r"\d+", conclusion)
        if not matches:
            return float("nan"), False

        level = float(matches[-1])

        # Must be in valid range
        if level < 0 or level > 5:
            return float("nan"), False

        # Guard against section numbers only (e.g. "4. Conclusion: ...")
        if len(matches) == 1 and conclusion.lstrip().startswith(str(int(level))):
            return float("nan"), False

        return level, True

    except (IndexError, ValueError):
        return float("nan"), False


def parse_batch_output(
    output_file: str | Path,
    *,
    only_successful: bool = False,
) -> pd.DataFrame:
    """Parse an OpenAI Batch API output JSONL file.

    Each line in the file corresponds to one annotation request.
    The ``custom_id`` field encodes ``{instance_id}__{demand_acronym}``.

    Args:
        output_file:    Path to the output.jsonl file.
        only_successful: If True, exclude rows where level extraction failed.

    Returns:
        DataFrame with columns:
        - ``custom_id``:     Original instance ID (without demand suffix).
        - ``demand``:        Demand acronym (e.g. "AS").
        - ``level``:         Extracted level (0–5), or NaN on failure.
        - ``finish_reason``: API finish reason ("stop", "length", etc.).
        - ``response``:      Full LLM response text.
    """
    output_file = Path(output_file)
    if not output_file.exists():
        raise FileNotFoundError(f"Output file not found: {output_file}")

    results = []

    with open(output_file, "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)
            raw_id = item["custom_id"]

            # Parse composite ID: instance_id__demand_acronym
            if "__" in raw_id:
                instance_id, demand = raw_id.rsplit("__", 1)
            else:
                instance_id = raw_id
                demand = Path(output_file).parent.name.split("_")[0]

            # Extract response content
            try:
                choice = item["response"]["body"]["choices"][0]
                finish_reason = choice["finish_reason"]
                response_text = choice["message"]["content"]
            except (KeyError, IndexError):
                finish_reason = "error"
                response_text = ""

            # Extract level — try even for "length" truncated responses
            if finish_reason in ("stop", "length"):
                level, ok = extract_demand_level(response_text)
            else:
                level = float("nan")
                ok = False

            if only_successful and not ok:
                continue

            results.append({
                "custom_id": instance_id,
                "demand": demand,
                "level": level,
                "finish_reason": finish_reason,
                "response": response_text,
            })

    df = pd.DataFrame(results)
    n_success = df["level"].notna().sum()
    logger.info(
        "Parsed %d annotations from %s (%d successful, %d failed)",
        len(df), output_file.name, n_success, len(df) - n_success,
    )
    return df


def parse_multiple_outputs(
    output_files: List[str | Path],
    *,
    only_successful: bool = False,
) -> pd.DataFrame:
    """Parse multiple output JSONL files and combine results.

    Args:
        output_files:    List of paths to output.jsonl files.
        only_successful: If True, exclude failed annotations.

    Returns:
        Combined DataFrame with all annotations.
    """
    dfs = []
    for f in output_files:
        try:
            df = parse_batch_output(f, only_successful=only_successful)
            dfs.append(df)
        except Exception as exc:
            logger.error("Error parsing %s: %s", f, exc)

    if not dfs:
        return pd.DataFrame(
            columns=["custom_id", "demand", "level", "finish_reason", "response"]
        )

    return pd.concat(dfs, ignore_index=True)


def to_wide_format(df: pd.DataFrame) -> pd.DataFrame:
    """Pivot annotation results from long to wide format.

    Input has one row per (instance, demand) pair.
    Output has one row per instance, with demand levels as columns.

    Args:
        df: Long-format DataFrame from ``parse_batch_output``.

    Returns:
        Wide-format DataFrame with columns: custom_id, AS, AT, CEc, ...
    """
    return df.pivot_table(
        index="custom_id",
        columns="demand",
        values="level",
        aggfunc="first",
    ).reset_index()
