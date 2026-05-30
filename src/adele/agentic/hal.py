"""Whole-task ingest for the simplest agentic methodology.

Rung 1 of the ladder annotates the **whole task** an agent is given — the public
benchmark prompt, not the encrypted rollout trace — so no HAL decryption or Weave
is needed here. This module turns a set of HAL tasks into the
``prompt``/``custom_id`` frame the annotator consumes, emits a blank sheet for the
human annotator to fill, and runs the LLM judge over the active v2 rubric set.

The task source (which HAL benchmark, where its inputs are fetched) is an open
decision; ``load_tasks`` reads a simple CSV/JSONL so it is agnostic to that, and
``adele.data.load_benchmark`` can feed a HuggingFace-hosted benchmark in later.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import pandas as pd


@dataclass(frozen=True)
class HalTask:
    """One whole agent task: the prompt given to the agent, plus its outcome."""
    custom_id: str
    prompt: str
    benchmark: str = ""
    final_success: Optional[bool] = None


def load_tasks(path: str) -> pd.DataFrame:
    """Load whole tasks from a ``.csv`` or ``.jsonl`` file.

    Requires ``custom_id`` and ``prompt`` columns/keys; ``benchmark`` and
    ``final_success`` are carried through if present.
    """
    p = Path(path)
    if p.suffix == ".jsonl":
        frame = pd.read_json(p, lines=True)
    else:
        frame = pd.read_csv(p)
    for col in ("custom_id", "prompt"):
        if col not in frame.columns:
            raise ValueError(f"Task file {path} must have a '{col}' column.")
    return frame


def human_label_template(tasks: pd.DataFrame, demands: List[str]) -> pd.DataFrame:
    """Blank annotation sheet: ``custom_id`` + ``prompt`` + one column per demand.

    The human annotator fills the demand columns with 0–5 levels; the result is
    a wide frame ready for ``adele.agentic.validation.rubric_agreement``.
    """
    for col in ("custom_id", "prompt"):
        if col not in tasks.columns:
            raise ValueError(f"tasks must have a '{col}' column.")
    sheet = tasks[["custom_id", "prompt"]].copy()
    for demand in demands:
        sheet[demand] = pd.NA
    return sheet


def run_judge(tasks: pd.DataFrame, *, model: str = "gpt-4o", **annotate_kwargs) -> pd.DataFrame:
    """Annotate whole tasks on the **active v2 rubric set** with an LLM judge.

    Thin wrapper over ``adele.annotation.annotate`` that injects the composed
    active catalog and demand list. Returns a wide frame (``custom_id`` + one
    column per demand) aligned with ``human_label_template``'s schema.

    Cost note: this calls the judge once per task × demand — estimate tokens/$
    and dry-run on a handful before scaling.
    """
    from adele.annotation import annotate
    from adele.agentic import active_demands, load_active_catalog

    return annotate(
        data=tasks,
        catalog=load_active_catalog(),
        demands=active_demands(),
        model=model,
        format="wide",
        **annotate_kwargs,
    )
