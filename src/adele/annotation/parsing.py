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
        # The model stated its score explicitly — treat it as authoritative.
        # Don't fall through on an out-of-range value, or we might grab a
        # different, unrelated in-range number from the text and fabricate a
        # valid-looking score (e.g. "...criterion 3... the level is: 7").
        level = float(structured[-1])
        return (level, True) if 0 <= level <= 5 else (float("nan"), False)

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


def unguessability_from_choices(value) -> float:
    """Convert an answer-format classification into the battery's UG score.

    The ``UG_choice_num`` rubric classifies a question's answer format as the
    number of choices (an integer ``n``) or ``"open"`` for open-ended. The
    ADeLe battery's ``UG`` column is an unguessability score on 0–100; the
    analysis modules filter on ``ug_threshold=75``. This maps one to the other:

        n choices  -> (1 - 1/n) * 100   (e.g. 4 choices -> 75, 2 -> 50)
        "open"     -> 100               (nothing to guess from)
        n <= 1     -> 0

    NOTE: the formula is inferred from the threshold convention (75 ≈ 4
    choices); confirm against the paper if exact battery values are required.
    Returns NaN for unparseable input.
    """
    if value is None:
        return float("nan")
    if isinstance(value, str):
        v = value.strip().lower()
        if v in ("open", "open-ended", "openended"):
            return 100.0
        try:
            n = float(v)
        except ValueError:
            return float("nan")
    else:
        try:
            n = float(value)
        except (TypeError, ValueError):
            return float("nan")
    if n != n:  # NaN
        return float("nan")
    if n <= 1:
        return 0.0
    return (1.0 - 1.0 / n) * 100.0


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
        for line_no, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError as exc:
                # Skip a single malformed line rather than dropping the whole file.
                logger.warning("Skipping malformed line %d in %s: %s",
                               line_no, output_file.name, exc)
                continue
            raw_id = item["custom_id"]

            # Parse composite ID: instance_id__demand_acronym
            if "__" in raw_id:
                instance_id, demand = raw_id.rsplit("__", 1)
            else:
                instance_id = raw_id
                # Fall back to the demand encoded in the filename (output_<acr>.jsonl).
                demand = output_file.stem.split("_", 1)[-1]

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
    # dropna=False keeps a demand column even if every value failed extraction
    # (all-NaN), so the output has a stable, predictable set of demand columns
    # instead of silently dropping a whole dimension.
    wide = df.pivot_table(
        index="custom_id",
        columns="demand",
        values="level",
        aggfunc="first",
        dropna=False,
    ).reset_index()
    wide.columns.name = None
    return wide
