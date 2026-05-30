"""
Ability profiling and visualization.

Computes per-model ability scores by fitting a statistical model of
correctness ~ demand_profile for each demand dimension, then
visualises the results as radar/polar plots.

The ability model is **pluggable**. The default is
``LogisticAbilityModel`` (per-dimension weighted logistic regression).
To implement an alternative (e.g. Bayesian joint model), subclass
``AbilityModel`` and pass it to ``compute_ability_scores(model_class=...)``.

Ported from ``scc_and_ability_profiles.ipynb``.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Type

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import scienceplots  # noqa: F401  (registers the 'science' style)
from scipy.stats import spearmanr
from sklearn.linear_model import LogisticRegression


def _use_science_style() -> None:
    """Apply the 'science' plot style.

    Called inside the plotting functions rather than at import time, so that
    importing this module for the numeric API does not require a TeX install.
    The 'science' style renders text with LaTeX; if the TeX toolchain
    (``latex``/``dvipng``) is not on PATH we keep the style but disable
    ``text.usetex`` so plots still render (without TeX fonts).
    """
    import shutil

    plt.style.use("science")
    if not (shutil.which("latex") and shutil.which("dvipng")):
        plt.rcParams["text.usetex"] = False

# NumPy 2.0 renamed trapz → trapezoid
_trapz = getattr(np, "trapezoid", None) or np.trapz

logger = logging.getLogger(__name__)

# Import canonical ordering
from adele.analysis.constants import DEMAND_ORDER


# ============================================================================
# AbilityModel protocol — extend this to add new models (e.g. Bayesian)
# ============================================================================

class AbilityModel(ABC):
    """Abstract base class for ability scoring models.

    An ``AbilityModel`` receives the **full demand profile matrix** (all
    dimensions for all instances) together with per-instance binary
    correctness, and produces an ability score per demand dimension.

    **Current approach** (``LogisticAbilityModel``):
        Fits an independent logistic regression per demand dimension.
        The success probability of an instance depends only on its
        demand level in the dimension being scored.

    **Future approach** (e.g. ``BayesianAbilityModel``):
        Fits a joint model over all dimensions simultaneously.
        The success probability depends on the instance's *full* demand
        profile, capturing interactions between demands. For example,
        an instance that is Level 5 in Reasoning *and* Level 4 in
        Knowledge may be harder than either dimension alone predicts.

    To implement a new model:

    1. Subclass ``AbilityModel``.
    2. Implement ``fit(demand_profiles, correctness, demands)``
       and the ``ability_scores`` property.
    3. Pass your class to ``compute_ability_scores(model_class=...)``.

    Example::

        class BayesianAbilityModel(AbilityModel):
            def fit(self, demand_profiles, correctness, demands, **kw):
                # demand_profiles: DataFrame with N rows × D demand columns
                # correctness: 1-D array of 0/1
                # Model P(correct | full profile) jointly
                ...

            @property
            def ability_scores(self) -> Dict[str, float]:
                # Return marginal ability per dimension from posterior
                ...
    """

    @abstractmethod
    def fit(
        self,
        demand_profiles: pd.DataFrame,
        correctness: np.ndarray,
        demands: List[str],
        **kwargs,
    ) -> None:
        """Fit the model on instances with their full demand profiles.

        Args:
            demand_profiles: DataFrame where each row is an instance and
                each column is a demand dimension (values 0–5).
                Shape: (n_instances, n_demands).
            correctness: 1-D array of binary correctness (0 or 1),
                same length as demand_profiles.
            demands: List of demand column names (defines ordering).
            **kwargs: Model-specific parameters (e.g. dup_threshold,
                grid_min, grid_max for LogisticAbilityModel).
        """
        ...

    @property
    @abstractmethod
    def ability_scores(self) -> Dict[str, float]:
        """Return ability scores per demand dimension.

        Returns:
            Dictionary mapping demand acronym → ability score in [0, 1].
            Higher values indicate higher ability (the model maintains
            performance even at high demand levels).
        """
        ...

    def predict_success_probability(
        self, demand_profiles: pd.DataFrame
    ) -> np.ndarray:
        """Predict P(correct) for instances given their full demand profiles.

        Optional — used for prediction and diagnostics. The default
        implementation returns zeros.

        Args:
            demand_profiles: DataFrame of shape (n_instances, n_demands).

        Returns:
            1-D array of predicted success probabilities.
        """
        return np.zeros(len(demand_profiles), dtype=float)


# ============================================================================
# Default implementation: Weighted Logistic Regression (from the notebook)
# ============================================================================

class LogisticAbilityModel(AbilityModel):
    """Ability model using per-dimension weighted logistic regression.

    This is the default model, ported from the ADeLe paper's notebook.
    It fits each demand dimension **independently**: for each demand, a
    logistic regression predicts P(correct) ~ demand_level. The ability
    score is the area under that logistic curve, normalised to [0, 1].

    Note on scale: the notebook reports the *un-normalised* integral
    ``trapz(p, x)`` over the [0, 100] grid (a ~0–8 scale). This model divides
    by the grid width (``grid_max - grid_min``) to put scores on [0, 1]. The
    transform is monotonic, so rankings and profile shapes are identical, but
    the absolute numbers differ from the notebook's CSVs/figures by that factor.

    This approach assumes that the success probability depends only on
    the single demand with the highest level. A future Bayesian model
    would relax this by modelling the joint profile.
    """

    def __init__(self):
        self._scores: Dict[str, float] = {}
        self._models: Dict[str, LogisticRegression] = {}

    def fit(
        self,
        demand_profiles: pd.DataFrame,
        correctness: np.ndarray,
        demands: List[str],
        *,
        level_diff: int = 0,
        dup_threshold: int = 100,
        grid_min: float = 0,
        grid_max: float = 100,
        n_grid: int = 10001,
        **kwargs,
    ) -> None:
        x_values = np.linspace(grid_min, grid_max, n_grid)

        for demand in demands:
            if demand not in demand_profiles.columns:
                continue

            other_demands = [d for d in demands if d != demand]

            # Filter: isolate instances where this demand dominates
            if other_demands and level_diff is not None:
                other_max = demand_profiles[other_demands].max(axis=1)
                mask = other_max <= (demand_profiles[demand] + level_diff)
                filtered_profiles = demand_profiles[mask]
                filtered_correct = correctness[mask.values]
            else:
                filtered_profiles = demand_profiles
                filtered_correct = correctness

            if len(filtered_profiles) == 0:
                # No instances where this demand is the binding constraint, so
                # there is no SCC to fit and no area to integrate. Record NaN
                # ("not estimable"), as the notebook does — NOT 0.0, which would
                # claim the model fails at every demand level in this dimension.
                self._scores[demand] = float("nan")
                continue

            X_feature = filtered_profiles[[demand]].values
            y_feature = filtered_correct.astype(float)

            X_train, y_train, weights = _compute_sample_weights_with_anchor(
                X_feature, y_feature, dup_threshold
            )

            try:
                lr = LogisticRegression(random_state=42, max_iter=10000)
                lr.fit(X_train, y_train, sample_weight=weights)
                predictions = lr.predict_proba(x_values.reshape(-1, 1))[:, 1]
                auc = float(_trapz(predictions, x_values) / (grid_max - grid_min))
                self._scores[demand] = auc
                self._models[demand] = lr
            except Exception as exc:
                logger.warning(
                    "Failed to compute ability for %s: %s", demand, exc
                )
                # Degenerate single-class fit (e.g. a model that is wrong on
                # every instance — the y=0 anchor leaves only one class). That
                # is a real ~zero ability, not "no data", so keep 0.0 (not NaN).
                self._scores[demand] = 0.0

    @property
    def ability_scores(self) -> Dict[str, float]:
        return dict(self._scores)

    def predict_success_probability(
        self, demand_profiles: pd.DataFrame
    ) -> np.ndarray:
        """Predict using the max-demand heuristic (highest level dominates)."""
        if not self._models:
            return np.zeros(len(demand_profiles), dtype=float)
        # Average predictions across fitted dimensions
        preds = []
        for demand, lr in self._models.items():
            if demand in demand_profiles.columns:
                p = lr.predict_proba(demand_profiles[[demand]].values)[:, 1]
                preds.append(p)
        if preds:
            return np.mean(preds, axis=0)
        return np.zeros(len(demand_profiles), dtype=float)


# ============================================================================
# Sample weighting (shared helper)
# ============================================================================

def _compute_sample_weights_with_anchor(
    X_feature: np.ndarray,
    y_feature: np.ndarray,
    dup_threshold: int = 100,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Compute sample weights with a synthetic anchor point.

    For each demand level bin (1-5), computes weights to balance
    representation. Adds a synthetic anchor at level 20 with label 0
    to regularise the logistic regression.

    Ported from the notebook's ``compute_sample_weights_with_anchor``.
    """
    if X_feature.ndim == 1:
        X_feature = X_feature.reshape(-1, 1)

    levels = [1, 2, 3, 4, 5]
    counts = {lv: int(np.sum(X_feature.flatten() == lv)) for lv in levels}
    total_original = sum(counts.values())

    if total_original == 0:
        return X_feature, y_feature, np.ones(len(y_feature))

    # Determine eligible bins
    eligible = [lv for lv in levels if counts[lv] >= dup_threshold]
    majority_count = (
        max(counts[lv] for lv in eligible) if eligible
        else max(counts.values())
    )

    # Set targets for eligible bins
    targets = {}
    for lv in levels:
        if counts[lv] >= dup_threshold:
            targets[lv] = float(majority_count)
        else:
            targets[lv] = None

    # Proportional targets for ineligible bins
    ineligible = [lv for lv in levels if targets[lv] is None]
    E = sum(targets[lv] for lv in levels if targets[lv] is not None)
    sum_ineligible = sum(counts[lv] for lv in ineligible)

    if sum_ineligible > 0 and total_original > sum_ineligible:
        T = E / (1 - (sum_ineligible / total_original))
    else:
        T = E if E > 0 else 1.0

    for lv in ineligible:
        targets[lv] = (counts[lv] / total_original) * T if total_original > 0 else 0

    # Compute per-sample weights
    sample_weights = np.zeros(X_feature.shape[0], dtype=float)
    for lv in levels:
        mask = X_feature.flatten() == lv
        if counts[lv] > 0:
            sample_weights[mask] = targets[lv] / counts[lv]

    # Synthetic anchor point
    total_target = sum(targets[lv] for lv in levels)
    X_anchor = np.full((1, 1), 20)
    y_anchor = np.zeros(1)
    anchor_weight = max(total_target, 1.0)

    X_train = np.vstack([X_feature, X_anchor])
    y_train = np.concatenate([y_feature, y_anchor])
    combined_weights = np.concatenate([sample_weights, [anchor_weight]])

    return X_train, y_train, combined_weights


# ============================================================================
# Main API
# ============================================================================

def compute_ability_scores(
    model_data: pd.DataFrame,
    annotations: pd.DataFrame,
    *,
    demands: Optional[List[str]] = None,
    model_class: Type[AbilityModel] = LogisticAbilityModel,
    ug_threshold: float = 75,
    **model_kwargs,
) -> Dict[str, float]:
    """Compute ability scores for a single model.

    Instantiates an ``AbilityModel``, fits it on the full demand profile
    matrix and per-instance correctness, and returns scores per dimension.

    The default ``LogisticAbilityModel`` fits each dimension independently
    (P(correct) ~ demand_level). A future ``BayesianAbilityModel`` would
    model P(correct | full_profile) jointly, capturing inter-demand
    interactions.

    Args:
        model_data:    DataFrame with ``custom_id`` and ``correct`` columns
                       (per-instance model correctness, 0 or 1).
        annotations:   Wide-format annotation DataFrame with ``custom_id``
                       and demand columns + optionally ``UG`` column.
        demands:       List of demand dimensions. None = auto-detect.
        model_class:   AbilityModel subclass to use. Defaults to
                       ``LogisticAbilityModel``. Pass a custom class
                       (e.g. ``BayesianAbilityModel``) to use a different
                       statistical model.
        ug_threshold:  Minimum UnGuessability score for inclusion.
        **model_kwargs: Additional keyword arguments passed to
                       ``model.fit()`` (e.g. ``dup_threshold``,
                       ``grid_min``, ``grid_max``, ``n_grid``,
                       ``level_diff``).

    Returns:
        Dictionary mapping demand acronym → ability score.
    """
    if demands is None:
        demands = [d for d in DEMAND_ORDER if d in annotations.columns]

    # Merge model results with annotations
    merged = annotations.merge(model_data, on="custom_id", how="inner")
    available_demands = [d for d in demands if d in merged.columns]

    # Drop rows with any NaN feature BEFORE filtering/fitting, as the notebook
    # does (``nan_rows = X.isna().any(axis=1)`` over UG + the demand columns).
    # Otherwise a failed annotation (NaN level) would silently shift the fitted
    # curves — or be passed straight into LogisticRegression.
    feat_cols = (["UG"] if "UG" in merged.columns else []) + available_demands
    merged[feat_cols] = merged[feat_cols].apply(pd.to_numeric, errors="coerce")
    merged["correct"] = pd.to_numeric(merged["correct"], errors="coerce")
    before = len(merged)
    merged = merged[~(merged[feat_cols].isna().any(axis=1) | merged["correct"].isna())]
    if len(merged) < before:
        logger.info("Dropped %d/%d rows with NaN features/correctness",
                    before - len(merged), before)

    if "UG" in merged.columns:
        merged = merged[merged["UG"] >= ug_threshold].copy()

    # Extract the demand profile matrix and correctness vector
    demand_profiles = merged[available_demands].copy()
    correctness = merged["correct"].values.astype(float)

    # Fit the ability model on the full profile
    ability_model = model_class()
    try:
        ability_model.fit(
            demand_profiles=demand_profiles,
            correctness=correctness,
            demands=available_demands,
            **model_kwargs,
        )
        return ability_model.ability_scores
    except Exception:
        # Log the full traceback so an all-zero result is debuggable rather than
        # silently passed off as a real (flat) ability profile.
        logger.error("AbilityModel.fit() failed; returning zero scores", exc_info=True)
        return {d: 0.0 for d in available_demands}


def compute_spearman_correlations(
    model_data: pd.DataFrame,
    annotations: pd.DataFrame,
    *,
    demands: Optional[List[str]] = None,
) -> Dict[str, float]:
    """Compute Spearman rank correlations between demand levels and correctness.

    For each demand dimension, computes the Spearman correlation between
    the demand level and the model's correctness (0/1).

    Args:
        model_data:  DataFrame with ``custom_id`` and ``correct``.
        annotations: Wide-format annotations with demand columns.
        demands:     List of demand dimensions.

    Returns:
        Dictionary mapping demand → Spearman correlation coefficient.
    """
    if demands is None:
        demands = [d for d in DEMAND_ORDER if d in annotations.columns]

    merged = annotations.merge(model_data, on="custom_id", how="inner")
    merged["correct"] = pd.to_numeric(merged["correct"], errors="coerce")
    correlations = {}

    for demand in demands:
        if demand not in merged.columns:
            continue
        valid = merged[[demand, "correct"]].dropna()
        if len(valid) < 10:
            correlations[demand] = 0.0
            continue
        rho, _ = spearmanr(valid[demand], valid["correct"])
        correlations[demand] = float(rho) if not np.isnan(rho) else 0.0

    return correlations


# ============================================================================
# Visualization
# ============================================================================

def plot_ability_profile(
    ability_scores: Dict[str, float],
    *,
    title: Optional[str] = None,
    color: str = "#30638e",
    figsize: tuple = (8, 8),
    dpi: int = 150,
    save_path: Optional[str] = None,
) -> plt.Figure:
    """Plot an ability profile as a radar/polar chart.

    Args:
        ability_scores: Dict mapping demand → ability score (0–1).
        title:         Plot title.
        color:         Line/fill color.
        figsize:       Figure size.
        dpi:           Resolution.
        save_path:     If provided, save the plot.

    Returns:
        matplotlib Figure.
    """
    _use_science_style()
    # Order demands
    demands = [d for d in DEMAND_ORDER if d in ability_scores]
    if not demands:
        demands = sorted(ability_scores.keys())

    values = [ability_scores.get(d, 0) for d in demands]
    n = len(demands)

    # Close the radar polygon
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
    values = values + [values[0]]
    angles = angles + [angles[0]]

    fig = plt.figure(figsize=figsize, dpi=dpi)
    ax = fig.add_subplot(111, polar=True)

    ax.plot(angles, values, "o-", linewidth=2, color=color)
    ax.fill(angles, values, alpha=0.25, color=color)

    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_xticks(np.linspace(0, 2 * np.pi, n, endpoint=False))
    ax.set_xticklabels(demands, fontsize=11, fontweight="bold")
    ax.set_ylim(0, 1)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8])
    ax.set_yticklabels(["0.2", "0.4", "0.6", "0.8"], fontsize=8, color="#666")
    ax.grid(True, alpha=0.3)

    if title:
        ax.set_title(title, fontsize=14, fontweight="bold", pad=25)

    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=dpi, bbox_inches="tight")
        logger.info("Saved ability profile to %s", save_path)
        plt.close(fig)

    return fig


def plot_multi_model_ability(
    model_scores: Dict[str, Dict[str, float]],
    *,
    title: str = "Ability Profiles",
    colors: Optional[Dict[str, str]] = None,
    figsize: tuple = (10, 10),
    dpi: int = 150,
    save_path: Optional[str] = None,
) -> plt.Figure:
    """Plot ability profiles for multiple models on the same radar chart.

    Args:
        model_scores: Dict mapping model_name → {demand → ability_score}.
        title:        Plot title.
        colors:       Optional dict mapping model_name → color.
        figsize:      Figure size.
        dpi:          Resolution.
        save_path:    If provided, save the plot.

    Returns:
        matplotlib Figure.
    """
    _use_science_style()
    # Collect all demands
    all_demands = set()
    for scores in model_scores.values():
        all_demands.update(scores.keys())
    demands = [d for d in DEMAND_ORDER if d in all_demands]
    if not demands:
        demands = sorted(all_demands)

    n = len(demands)
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
    angles_closed = angles + [angles[0]]

    default_colors = plt.cm.tab10(np.linspace(0, 1, len(model_scores)))

    fig = plt.figure(figsize=figsize, dpi=dpi)
    ax = fig.add_subplot(111, polar=True)

    for idx, (model_name, scores) in enumerate(model_scores.items()):
        values = [scores.get(d, 0) for d in demands]
        values_closed = values + [values[0]]

        color = (
            colors.get(model_name, None) if colors
            else None
        ) or matplotlib.colors.to_hex(default_colors[idx])

        ax.plot(
            angles_closed, values_closed, "o-",
            linewidth=2, color=color, label=model_name,
        )
        ax.fill(angles_closed, values_closed, alpha=0.1, color=color)

    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_xticks(angles)
    ax.set_xticklabels(demands, fontsize=11, fontweight="bold")
    ax.set_ylim(0, 1)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8])
    ax.set_yticklabels(["0.2", "0.4", "0.6", "0.8"], fontsize=8, color="#666")
    ax.grid(True, alpha=0.3)
    ax.set_title(title, fontsize=14, fontweight="bold", pad=25)
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1), fontsize=9)

    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=dpi, bbox_inches="tight")
        logger.info("Saved multi-model ability profile to %s", save_path)
        plt.close(fig)

    return fig
