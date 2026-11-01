"""Rubric validation: judge-vs-human agreement on demand levels.

The simplest agentic methodology (see ``AGENTIC_METHODOLOGY.md``) annotates
whole HAL tasks on the v2 agentic dimensions with an LLM judge, then checks the
judge against a human annotator. This module is the agreement core: given the
judge's per-instance levels and the human's, it reports, per dimension, the
metrics §4 of the plan calls for — quadratic-weighted κ, Spearman ρ, exact and
adjacent (±1) agreement, mean absolute error, and a per-level confusion matrix.

Both inputs are **wide**-format frames (``custom_id`` + one 0–5 column per
demand, the schema ``adele.data.load_battery`` and ``annotate(format="wide")``
produce). With a single human annotator there is no human–human ceiling, so
these numbers locate ambiguous anchors rather than certify the rubric; pass a
list of human frames once ≥2 annotators exist to also get that ceiling.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import cohen_kappa_score

LEVELS = list(range(6))  # 0..5 ordinal demand levels


@dataclass(frozen=True)
class DimensionAgreement:
    """Agreement between two annotators on one demand dimension."""
    demand: str
    n: int                    # instances both annotators scored (non-NaN)
    quadratic_kappa: float    # quadratic-weighted Cohen's κ
    spearman: float           # Spearman rank correlation
    exact: float              # fraction with identical level
    adjacent: float           # fraction within ±1 level
    mae: float                # mean absolute level difference
    confusion: pd.DataFrame   # rows = annotator A level, cols = B level, 0..5


@dataclass(frozen=True)
class AgreementReport:
    """Per-dimension agreement plus a tabular summary."""
    dimensions: Dict[str, DimensionAgreement]

    def to_frame(self) -> pd.DataFrame:
        """One row per demand with the scalar metrics (confusion omitted)."""
        return pd.DataFrame(
            [
                {
                    "demand": d.demand, "n": d.n,
                    "quadratic_kappa": d.quadratic_kappa, "spearman": d.spearman,
                    "exact": d.exact, "adjacent": d.adjacent, "mae": d.mae,
                }
                for d in self.dimensions.values()
            ]
        )

    def __str__(self) -> str:
        frame = self.to_frame()
        if frame.empty:
            return "AgreementReport(empty)"
        return frame.round(3).to_string(index=False)


def _pair_agreement(demand: str, a: np.ndarray, b: np.ndarray) -> DimensionAgreement:
    """Agreement metrics for two aligned, NaN-free integer level vectors."""
    n = len(a)
    diff = np.abs(a - b)
    confusion = pd.crosstab(
        pd.Categorical(a, categories=LEVELS),
        pd.Categorical(b, categories=LEVELS),
        dropna=False,
    ).reindex(index=LEVELS, columns=LEVELS, fill_value=0)

    # κ and ρ are undefined when an annotator never varies (single class /
    # zero variance). Report NaN rather than a misleading 0 or a warning.
    constant = len(set(a)) < 2 or len(set(b)) < 2
    kappa = float("nan") if constant else cohen_kappa_score(a, b, weights="quadratic", labels=LEVELS)
    rho = float("nan") if constant else float(spearmanr(a, b).statistic)

    return DimensionAgreement(
        demand=demand,
        n=n,
        quadratic_kappa=float(kappa),
        spearman=rho,
        exact=float(np.mean(diff == 0)),
        adjacent=float(np.mean(diff <= 1)),
        mae=float(np.mean(diff)),
        confusion=confusion,
    )


def rubric_agreement(
    judge: pd.DataFrame,
    human: pd.DataFrame,
    demands: Optional[List[str]] = None,
) -> AgreementReport:
    """Compute judge-vs-human agreement per demand dimension.

    Args:
        judge:   Wide frame: ``custom_id`` + one 0–5 column per demand.
        human:   Wide frame in the same schema (the human annotator's labels).
        demands: Dimensions to score. None → every non-``custom_id`` column
                 present in both frames.

    Returns:
        An ``AgreementReport``. Dimensions with no overlapping non-NaN
        instances are skipped (a logged-free, explicit omission).
    """
    if "custom_id" not in judge.columns or "custom_id" not in human.columns:
        raise ValueError("Both frames must have a 'custom_id' column.")

    if demands is None:
        shared = set(judge.columns) & set(human.columns)
        demands = [c for c in judge.columns if c in shared and c != "custom_id"]

    merged = judge.merge(human, on="custom_id", suffixes=("_judge", "_human"))

    results: Dict[str, DimensionAgreement] = {}
    for demand in demands:
        ja, ha = f"{demand}_judge", f"{demand}_human"
        if ja not in merged.columns or ha not in merged.columns:
            continue
        pair = merged[[ja, ha]].apply(pd.to_numeric, errors="coerce").dropna()
        if pair.empty:
            continue
        results[demand] = _pair_agreement(
            demand,
            pair[ja].to_numpy(dtype=int),
            pair[ha].to_numpy(dtype=int),
        )

    return AgreementReport(dimensions=results)
