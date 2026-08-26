"""Scorers faithful to the ADeLe v1.0 verification conventions.

The battery has two answer formats, scored by two paths that share one
answer-extractor keyed on the prompt's own convention
("Thus, the correct answer is: X"):

  * MC          -> deterministic option-letter match against the gold answer
                   (no judge, no cost).
  * Open-ended  -> model-graded against the gold answer (the judge model is a
                   versioned, cost-bearing input; see version.py).

:func:`adele_scorer` dispatches per sample on ``metadata["answer_format"]`` so a
mixed battery run scores both paths in one pass.
"""

import re
from typing import Optional, Union

from inspect_ai.model import Model
from inspect_ai.scorer import (
    CORRECT,
    INCORRECT,
    NOANSWER,
    Score,
    Target,
    accuracy,
    model_graded_qa,
    scorer,
    stderr,
)
from inspect_ai.solver import TaskState

# The v1.0 prompts instruct the model to conclude with this marker.
_MARKER = re.compile(r"correct answer is:?\s*", re.IGNORECASE)
# Leading option label, e.g. "B", "B.", "B)", "(B)".
_LETTER = re.compile(r"^\s*\(?([A-Za-z])\)?[\.\):]")


def final_segment(text: str) -> str:
    """Return the text after the last answer marker, or the whole string."""
    matches = list(_MARKER.finditer(text))
    return text[matches[-1].end():].strip() if matches else text.strip()


def choice_letter(text: str) -> Optional[str]:
    """Extract the MC option letter from an answer segment.

    Accepted, in order: an anchored "B." / "(b):" at the start of the segment
    (any case); a bare letter as the entire segment ("b"); otherwise an
    UPPERCASE standalone letter anywhere. Restricting the loose fallback to
    uppercase A-J means prose like "a good answer would be..." can no longer
    be mis-read as option "A".
    """
    segment = final_segment(text)
    m = _LETTER.match(segment)
    if m:
        return m.group(1).upper()
    m = re.fullmatch(r"\s*\(?([A-Za-z])\)?\s*", segment)
    if m:
        return m.group(1).upper()
    m = re.search(r"\b([A-J])\b", segment)
    return m.group(1) if m else None


@scorer(metrics=[accuracy(), stderr()])
def adele_mc_scorer():
    """Deterministic option-letter match for multiple-choice samples."""

    async def score(state: TaskState, target: Target) -> Score:
        pred = choice_letter(state.output.completion)
        gold = choice_letter(target.text)
        correct = pred is not None and gold is not None and pred == gold
        return Score(
            value=CORRECT if correct else INCORRECT,
            answer=pred or "",
            explanation=f"pred={pred} gold={gold}",
        )

    return score


@scorer(metrics=[accuracy(), stderr()])
def adele_scorer(judge_model: Optional[Union[str, Model]] = None):
    """Dispatch per sample: MC -> letter match, Open-ended -> model-graded.

    Args:
        judge_model: model used to grade Open-ended samples. Required to score
            them; MC needs no judge. Recorded in the result version.
    """
    mc = adele_mc_scorer()
    open_ended = model_graded_qa(model=judge_model) if judge_model else None

    async def score(state: TaskState, target: Target) -> Score:
        fmt = (state.metadata or {}).get("answer_format")
        if fmt == "MC":
            return await mc(state, target)
        if fmt == "Open-ended":
            if open_ended is None:
                return Score(
                    value=NOANSWER,
                    explanation="Open-ended sample needs judge_model (none provided).",
                )
            return await open_ended(state, target)
        return Score(value=NOANSWER, explanation=f"Unknown answer_format: {fmt!r}")

    return score
