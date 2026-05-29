"""
Predictive power analysis using a Random Forest "assessor".

Trains a Random Forest to predict per-instance correctness from demand
annotations, and measures how well it generalises. This is the evidence that
the demand profile is *informative* about model performance.

Faithful to ``predictive_power_stats_rf-assessor.ipynb``:

* The assessor is ``RandomForestClassifier(n_estimators=100,
  min_samples_split=50, criterion="entropy")``.
* Three evaluation modes, all via 10-fold ``KFold``:
    - in-distribution (``group_by=None``): folds over instances;
    - OOD by benchmark (``group_by="benchmark"``): folds over the *unique
      benchmark labels*, so no benchmark in the test fold is seen in training;
    - OOD by task (``group_by="task"``): same, over the unique task labels.
* Out-of-fold predictions are pooled across all folds (every instance is held
  out exactly once), and AUROC / accuracy / ECE / Brier are computed once on
  the pooled arrays, then averaged over the random seeds.
"""

import logging
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import KFold
from sklearn.metrics import roc_auc_score, accuracy_score, brier_score_loss

logger = logging.getLogger(__name__)

# Seeds from the notebook's production (multi-seed) run.
DEFAULT_SEEDS: Tuple[int, ...] = (1, 2, 3, 4, 5, 42, 123, 456, 789, 1000)


# ============================================================================
# Helpers
# ============================================================================

def _feature_columns(
    annotations: pd.DataFrame,
    demands: Optional[List[str]],
    include_ug: bool,
) -> List[str]:
    """Feature columns: UG (if present) prepended to the demand dimensions."""
    from adele.analysis.constants import DEMAND_ORDER

    if demands is None:
        demands = [d for d in DEMAND_ORDER if d in annotations.columns]
    cols = []
    if include_ug and "UG" in annotations.columns:
        cols.append("UG")
    cols.extend(d for d in demands if d in annotations.columns)
    return cols


def _build_xy(
    model_data: pd.DataFrame,
    annotations: pd.DataFrame,
    demands: Optional[List[str]],
    include_ug: bool,
) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame]:
    """Merge on ``custom_id`` and build the (numeric, NaN-dropped) feature frame.

    Returns ``(X, y, merged)`` where the three are row-aligned (same index).
    Rows with any NaN feature are dropped (faithful to the notebook).
    """
    merged = annotations.merge(model_data, on="custom_id", how="inner")
    feat_cols = _feature_columns(merged, demands, include_ug)
    if not feat_cols:
        raise ValueError("No feature columns found (need UG and/or demand columns).")

    X = merged[feat_cols].apply(pd.to_numeric, errors="coerce")
    y = pd.to_numeric(merged["correct"], errors="coerce")

    keep = ~(X.isna().any(axis=1) | y.isna())
    X = X[keep].reset_index(drop=True)
    y = y[keep].astype(int).reset_index(drop=True)
    merged = merged[keep].reset_index(drop=True)
    return X, y, merged


def _calculate_ece(y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10) -> float:
    """Expected Calibration Error: 10 equal-width bins, weighted by bin mass.

    Reproduces the notebook's ``calculate_ece`` exactly.
    """
    y_true = np.asarray(y_true)
    y_prob = np.asarray(y_prob)
    bin_edges = np.linspace(0, 1, n_bins + 1)
    bin_indices = np.minimum(np.digitize(y_prob, bin_edges) - 1, n_bins - 1)

    ece = 0.0
    total = len(y_true)
    for i in range(n_bins):
        mask = bin_indices == i
        n = int(np.sum(mask))
        if n > 0:
            acc = float(np.mean(y_true[mask]))
            conf = float(np.mean(y_prob[mask]))
            ece += (n / total) * abs(acc - conf)
    return ece


def _positive_proba(clf: RandomForestClassifier, X: np.ndarray) -> np.ndarray:
    """P(correct) for each row, robust to a training fold with no positives."""
    classes = list(clf.classes_)
    if 1 in classes:
        return clf.predict_proba(X)[:, classes.index(1)]
    return np.zeros(len(X), dtype=float)


def _group_folds(
    labels: np.ndarray, n_folds: int, seed: int
) -> List[Tuple[np.ndarray, np.ndarray]]:
    """Shuffle the unique group labels (seeded) and KFold over them."""
    unique = np.array(pd.unique(labels))
    rng = np.random.RandomState(seed)
    rng.shuffle(unique)
    n_splits = min(n_folds, len(unique))
    if n_splits < 2:
        raise ValueError(
            f"Need >=2 distinct groups to split; got {len(unique)}."
        )
    if n_splits < n_folds:
        logger.warning(
            "Only %d distinct groups; reducing folds %d -> %d",
            len(unique), n_folds, n_splits,
        )
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=seed)
    return [(unique[tr], unique[te]) for tr, te in kf.split(unique)]


def _pooled_oof(
    X: pd.DataFrame,
    y: pd.Series,
    *,
    groups: Optional[pd.Series],
    n_folds: int,
    seed: int,
    rf_kwargs: dict,
) -> Tuple[np.ndarray, np.ndarray]:
    """Out-of-fold pooled (y_true, y_prob) for one seed.

    ``groups=None`` folds over instances (ID); otherwise folds over the unique
    group labels (OOD), so a test group is never seen in training.
    """
    Xv = X.values
    yv = y.values
    true_parts: List[np.ndarray] = []
    prob_parts: List[np.ndarray] = []

    if groups is None:
        kf = KFold(n_splits=n_folds, shuffle=True, random_state=seed)
        splits = kf.split(Xv)
        for train_idx, test_idx in splits:
            clf = RandomForestClassifier(random_state=seed, **rf_kwargs)
            clf.fit(Xv[train_idx], yv[train_idx])
            true_parts.append(yv[test_idx])
            prob_parts.append(_positive_proba(clf, Xv[test_idx]))
    else:
        gv = groups.values
        for train_vals, test_vals in _group_folds(gv, n_folds, seed):
            test_mask = np.isin(gv, test_vals)
            train_mask = np.isin(gv, train_vals)
            if train_mask.sum() == 0 or test_mask.sum() == 0:
                continue
            clf = RandomForestClassifier(random_state=seed, **rf_kwargs)
            clf.fit(Xv[train_mask], yv[train_mask])
            true_parts.append(yv[test_mask])
            prob_parts.append(_positive_proba(clf, Xv[test_mask]))

    return np.concatenate(true_parts), np.concatenate(prob_parts)


# ============================================================================
# Public API
# ============================================================================

def compute_predictive_power(
    model_data: pd.DataFrame,
    annotations: pd.DataFrame,
    *,
    demands: Optional[List[str]] = None,
    group_by: Optional[str] = None,
    include_ug: bool = True,
    n_folds: int = 10,
    seeds: Sequence[int] = DEFAULT_SEEDS,
    n_estimators: int = 100,
    min_samples_split: int = 50,
    criterion: str = "entropy",
) -> Dict[str, object]:
    """Assess how well demand levels predict model correctness.

    Defaults reproduce ``predictive_power_stats_rf-assessor.ipynb``. Out-of-fold
    predictions are pooled across folds and scored once per seed; metrics are
    then averaged over ``seeds``.

    Args:
        model_data:   DataFrame with ``custom_id`` and ``correct`` (0/1).
        annotations:  Wide annotations / battery with ``custom_id``, the demand
                      columns, optionally ``UG``, and (for OOD) the ``group_by``
                      column.
        demands:      Demand feature columns. None = auto-detect from DEMAND_ORDER.
        group_by:     None for in-distribution (fold over instances), or
                      ``"benchmark"`` / ``"task"`` for OOD (fold over the unique
                      values of that column).
        include_ug:   Prepend the ``UG`` column to the features if present.
        n_folds:      Number of folds (over instances, or over group labels).
        seeds:        Random seeds to average over.
        n_estimators, min_samples_split, criterion: Random Forest params
                      (notebook: 100 / 50 / "entropy").

    Returns:
        Dict with ``group_by``, ``n_instances``, ``n_seeds`` and the mean (and
        ``*_std``) of ``roc_auc``, ``accuracy``, ``ece``, ``brier`` over seeds,
        plus a ``per_seed`` dict of the raw per-seed values.
    """
    X, y, merged = _build_xy(model_data, annotations, demands, include_ug)

    if group_by is not None and group_by not in merged.columns:
        raise ValueError(
            f"group_by={group_by!r} not found. Available: {list(merged.columns)}"
        )

    groups = merged[group_by] if group_by is not None else None
    rf_kwargs = dict(
        n_estimators=n_estimators,
        min_samples_split=min_samples_split,
        criterion=criterion,
        n_jobs=-1,
    )

    label = group_by or "instance"
    metrics = {"roc_auc": [], "accuracy": [], "ece": [], "brier": []}

    if y.nunique() < 2:
        logger.warning("Only one class in 'correct'; predictive power is undefined.")
        return {
            "group_by": label, "n_instances": int(len(y)), "n_seeds": 0,
            "roc_auc": float("nan"), "roc_auc_std": float("nan"),
            # majority-class accuracy (a constant predictor's score)
            "accuracy": float(max(y.mean(), 1 - y.mean())), "accuracy_std": 0.0,
            "ece": float("nan"), "ece_std": float("nan"),
            "brier": float("nan"), "brier_std": float("nan"),
            "per_seed": {k: [] for k in metrics},
        }

    for seed in seeds:
        y_true, y_prob = _pooled_oof(
            X, y, groups=groups, n_folds=n_folds, seed=seed, rf_kwargs=rf_kwargs
        )
        y_pred = (y_prob > 0.5).astype(int)
        try:
            auc = float(roc_auc_score(y_true, y_prob))
        except ValueError:
            auc = float("nan")
        metrics["roc_auc"].append(auc)
        metrics["accuracy"].append(float(accuracy_score(y_true, y_pred)))
        metrics["ece"].append(_calculate_ece(y_true, y_prob))
        metrics["brier"].append(float(brier_score_loss(y_true, y_prob)))

    result: Dict[str, object] = {
        "group_by": label,
        "n_instances": int(len(y)),
        "n_seeds": len(seeds),
        "per_seed": metrics,
    }
    for key, vals in metrics.items():
        result[key] = float(np.nanmean(vals))
        result[f"{key}_std"] = float(np.nanstd(vals))

    logger.info(
        "Predictive power (%s): AUROC=%.3f, ECE=%.3f, acc=%.3f over %d seeds",
        label, result["roc_auc"], result["ece"], result["accuracy"], len(seeds),
    )
    return result


def compute_feature_importances(
    model_data: pd.DataFrame,
    annotations: pd.DataFrame,
    *,
    demands: Optional[List[str]] = None,
    include_ug: bool = True,
    n_folds: int = 10,
    seed: int = 42,
    n_estimators: int = 100,
    min_samples_split: int = 50,
) -> Dict[str, float]:
    """Mean impurity-based feature importance, averaged over KFold folds.

    Reproduces the notebook's ``calculate_feature_importance``: a forest with
    the default (gini) criterion, importances averaged across the 10 folds.

    Returns:
        Dict mapping feature name (UG + demand dims) → mean importance.
    """
    X, y, _ = _build_xy(model_data, annotations, demands, include_ug)
    if y.nunique() < 2:
        logger.warning("Only one class in 'correct'; importances are undefined.")
        return {c: 0.0 for c in X.columns}

    kf = KFold(n_splits=n_folds, shuffle=True, random_state=seed)
    per_fold = []
    for train_idx, _test_idx in kf.split(X.values):
        clf = RandomForestClassifier(
            n_estimators=n_estimators,
            min_samples_split=min_samples_split,
            random_state=seed,
            n_jobs=-1,
        )
        clf.fit(X.values[train_idx], y.values[train_idx])
        per_fold.append(clf.feature_importances_)

    mean_imp = np.mean(per_fold, axis=0)
    return dict(zip(X.columns, mean_imp.tolist()))


def plot_feature_importances(
    importances: Dict[str, float],
    *,
    title: str = "Demand Feature Importances",
    color: str = "#30638e",
    figsize: tuple = (10, 6),
    dpi: int = 150,
    save_path: Optional[str] = None,
) -> "plt.Figure":
    """Plot feature importances as a horizontal bar chart.

    Args:
        importances: Dict mapping demand → importance.
        title:       Plot title.
        color:       Bar color.
        figsize:     Figure size.
        dpi:         Resolution.
        save_path:   If provided, save the plot.

    Returns:
        matplotlib Figure.
    """
    import matplotlib.pyplot as plt

    from adele.analysis.ability import _use_science_style

    _use_science_style()

    sorted_items = sorted(importances.items(), key=lambda x: x[1], reverse=True)
    demands = [x[0] for x in sorted_items]
    values = [x[1] for x in sorted_items]

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    ax.barh(demands, values, color=color, edgecolor="white")
    ax.set_xlabel("Importance", fontsize=12)
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.invert_yaxis()
    ax.grid(axis="x", alpha=0.3)

    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=dpi, bbox_inches="tight")
        logger.info("Saved feature importance plot to %s", save_path)
        plt.close(fig)

    return fig
