"""
Analysis and profiling sub-package.

Provides demand profiling, ability profiling, and predictive
power analysis tools.
"""

from adele.analysis.demand import (
    compute_demand_profile,
    plot_demand_profile,
    plot_from_csv,
)
from adele.analysis.ability import (
    AbilityModel,
    LogisticAbilityModel,
    compute_ability_scores,
    compute_spearman_correlations,
    plot_ability_profile,
    plot_multi_model_ability,
)

__all__ = [
    "AbilityModel",
    "LogisticAbilityModel",
    "compute_demand_profile",
    "plot_demand_profile",
    "plot_from_csv",
    "compute_ability_scores",
    "compute_spearman_correlations",
    "plot_ability_profile",
    "plot_multi_model_ability",
]

