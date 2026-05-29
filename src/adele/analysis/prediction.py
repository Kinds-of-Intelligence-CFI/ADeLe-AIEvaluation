"""
Predictive power analysis using Random Forest.

Assesses how well demand-level annotations predict model performance,
providing evidence for the informativeness of the demand profile.
"""

import logging
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, KFold
from sklearn.metrics import roc_auc_score, accuracy_score, classification_report

logger = logging.getLogger(__name__)


def compute_predictive_power(
    model_data: pd.DataFrame,
    annotations: pd.DataFrame,
    *,
    demands: Optional[List[str]] = None,
    n_folds: int = 10,
    n_estimators: int = 100,
    min_samples_split: int = 50,
    criterion: str = "entropy",
    random_state: int = 42,
) -> Dict[str, float]:
    """Assess how well demand levels predict model correctness.

    Trains a Random Forest classifier to predict correctness from
    demand levels and reports cross-validated performance.

    Defaults reproduce the predictive-power notebook
    (``predictive_power_stats_rf-assessor.ipynb``): 10-fold ``KFold``,
    ``min_samples_split=50``, ``criterion="entropy"``. Changing these
    changes the reported numbers, so keep them to compare against the paper.

    Args:
        model_data:    DataFrame with ``custom_id`` and ``correct``.
        annotations:   Wide-format annotations with demand columns.
        demands:       List of demand dimensions to use as features.
        n_folds:       Number of cross-validation folds.
        n_estimators:  Number of trees in the Random Forest.
        min_samples_split: Min samples to split a node (notebook used 50).
        criterion:     Split criterion (notebook used "entropy").
        random_state:  Random seed.

    Returns:
        Dictionary with keys:
        - ``accuracy``: Mean CV accuracy.
        - ``roc_auc``:  Mean CV ROC-AUC.
        - ``feature_importances``: Dict of demand → importance score.
    """
    from adele.analysis.constants import DEMAND_ORDER

    if demands is None:
        demands = [d for d in DEMAND_ORDER if d in annotations.columns]

    # Merge
    merged = annotations.merge(model_data, on="custom_id", how="inner")

    # Build feature matrix
    X = merged[demands].fillna(0).values
    y = merged["correct"].values.astype(int)

    if len(np.unique(y)) < 2:
        logger.warning("Only one class in target. Cannot compute predictive power.")
        return {
            "accuracy": float(np.mean(y)),
            "roc_auc": 0.5,
            "feature_importances": {d: 0.0 for d in demands},
        }

    # Random Forest (hyperparameters match the predictive-power notebook).
    clf = RandomForestClassifier(
        n_estimators=n_estimators,
        min_samples_split=min_samples_split,
        criterion=criterion,
        random_state=random_state,
        n_jobs=-1,
    )

    # Cross-validated scores (10-fold KFold, as in the notebook).
    cv = KFold(n_splits=n_folds, shuffle=True, random_state=random_state)

    acc_scores = cross_val_score(clf, X, y, cv=cv, scoring="accuracy")
    try:
        auc_scores = cross_val_score(clf, X, y, cv=cv, scoring="roc_auc")
        mean_auc = float(np.mean(auc_scores))
    except ValueError:
        mean_auc = 0.5

    # Fit on full data for feature importances
    clf.fit(X, y)
    importances = dict(zip(demands, clf.feature_importances_.tolist()))

    result = {
        "accuracy": float(np.mean(acc_scores)),
        "roc_auc": mean_auc,
        "feature_importances": importances,
    }

    logger.info(
        "Predictive power: accuracy=%.3f, ROC-AUC=%.3f",
        result["accuracy"], result["roc_auc"],
    )

    return result


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
    import scienceplots

    plt.style.use('science')

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
