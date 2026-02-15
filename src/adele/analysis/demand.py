"""
Demand profiling and visualization.

Computes demand profiles from annotation matrices and produces
polar heatmap visualizations equivalent to the R ``demand_profiles.R``.
"""

import logging
from pathlib import Path
from typing import Optional, List

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import Rectangle

logger = logging.getLogger(__name__)

# Import canonical ordering
from adele.analysis.constants import DEMAND_ORDER


def compute_demand_profile(
    annotations: pd.DataFrame,
    *,
    demands: Optional[List[str]] = None,
) -> pd.DataFrame:
    """Compute a demand profile from wide-format annotations.

    A demand profile is a frequency table counting how many instances
    fall at each level (0–5) for each demand dimension.

    Args:
        annotations: Wide-format DataFrame with ``custom_id`` and demand
                     columns (e.g. ``AS``, ``CEc``, ...).
        demands:     Ordered list of demand column names. None = auto-detect
                     from ``DEMAND_ORDER``.

    Returns:
        DataFrame with columns: ``demand``, ``level``, ``count``.
    """
    if demands is None:
        # Auto-detect: use DEMAND_ORDER columns that are present
        demands = [d for d in DEMAND_ORDER if d in annotations.columns]
        # Add any extra demand columns not in the canonical order
        extra = [c for c in annotations.columns
                 if c not in demands and c != "custom_id"]
        demands.extend(sorted(extra))

    rows = []
    for demand in demands:
        if demand not in annotations.columns:
            continue
        vals = annotations[demand].dropna().astype(int).clip(0, 5)
        counts = vals.value_counts().reindex(range(6), fill_value=0)
        for level in range(6):
            rows.append({
                "demand": demand,
                "level": level,
                "count": counts[level],
            })

    return pd.DataFrame(rows)


def plot_demand_profile(
    profile_or_annotations: pd.DataFrame,
    *,
    title: Optional[str] = None,
    base_color: str = "#30638e",
    figsize: tuple = (10, 10),
    dpi: int = 150,
    save_path: Optional[str] = None,
) -> plt.Figure:
    """Create a polar heatmap of a demand profile.

    This produces the characteristic ADeLe "sunburst" chart showing
    the distribution of demand levels across dimensions.

    Args:
        profile_or_annotations: Either a long-format profile DataFrame
            (with ``demand``, ``level``, ``count`` columns) or a
            wide-format annotations DataFrame (with demand columns).
        title:      Plot title.
        base_color: Base color for the gradient (default: ADeLe blue).
        figsize:    Figure size in inches.
        dpi:        Resolution.
        save_path:  If provided, save the figure to this path.

    Returns:
        The matplotlib Figure object.
    """
    # Determine input format
    if "count" in profile_or_annotations.columns:
        profile = profile_or_annotations
    else:
        profile = compute_demand_profile(profile_or_annotations)

    # Get unique demands in order
    demands = profile["demand"].unique().tolist()
    n_demands = len(demands)

    # Build count matrix: (demands × levels)
    count_matrix = np.zeros((n_demands, 6))
    for i, demand in enumerate(demands):
        mask = profile["demand"] == demand
        for _, row in profile[mask].iterrows():
            level = int(row["level"])
            count_matrix[i, level] = row["count"]

    # Create the polar figure
    fig = plt.figure(figsize=figsize, dpi=dpi)
    ax = fig.add_subplot(111, polar=True)

    # Create color map: white → base_color
    cmap = mcolors.LinearSegmentedColormap.from_list(
        "adele", ["white", base_color]
    )
    max_count = count_matrix.max()
    if max_count == 0:
        max_count = 1

    # Angular positions
    angles = np.linspace(0, 2 * np.pi, n_demands, endpoint=False)
    bar_width = 2 * np.pi / n_demands * 0.92  # slight gap

    # Draw tiles: for each demand × level
    for i in range(n_demands):
        for level in range(6):
            color = cmap(count_matrix[i, level] / max_count)
            ax.bar(
                angles[i], height=1, width=bar_width,
                bottom=level, color=color,
                edgecolor="white", linewidth=0.8,
            )

    # Style the plot
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    # Demand labels
    ax.set_xticks(angles)
    ax.set_xticklabels(demands, fontsize=11, fontweight="bold")

    # Radial (level) labels
    ax.set_yticks(np.arange(0, 6) + 0.5)
    ax.set_yticklabels([str(i) for i in range(6)], fontsize=9,
                       fontweight="bold", color="#333")
    ax.set_ylim(0, 6)

    # Remove grid
    ax.grid(False)
    ax.spines["polar"].set_visible(False)

    # Title
    if title:
        ax.set_title(title, fontsize=16, fontweight="bold", pad=30)

    # Colorbar
    sm = plt.cm.ScalarMappable(
        cmap=cmap,
        norm=mcolors.Normalize(vmin=0, vmax=max_count),
    )
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, fraction=0.03, pad=0.12)
    cbar.ax.set_ylabel("Frequency", fontsize=10)

    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=dpi, bbox_inches="tight")
        logger.info("Saved demand profile plot to %s", save_path)
        plt.close(fig)

    return fig


def plot_from_csv(
    csv_path: str,
    *,
    title: Optional[str] = None,
    base_color: str = "#30638e",
    save_path: Optional[str] = None,
) -> plt.Figure:
    """Load an annotation CSV and produce a demand profile plot.

    Convenience function that reads a CSV with ``custom_id`` and demand
    columns, computes the profile, and plots it.

    Args:
        csv_path:   Path to the annotation CSV.
        title:      Optional plot title. If None, inferred from filename.
        base_color: Base color for the gradient.
        save_path:  If provided, save the figure (default: same name as CSV
                    with ``.png`` extension).

    Returns:
        The matplotlib Figure.
    """
    df = pd.read_csv(csv_path)

    if title is None:
        title = Path(csv_path).stem.replace("_", " ").title()

    if save_path is None:
        save_path = str(Path(csv_path).with_suffix(".png"))

    return plot_demand_profile(
        df,
        title=title,
        base_color=base_color,
        save_path=save_path,
    )
