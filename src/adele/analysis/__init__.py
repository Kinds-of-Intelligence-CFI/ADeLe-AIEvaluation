"""
Analysis and profiling sub-package.

Provides demand profiling, ability profiling, and predictive
power analysis tools.
"""

# Canonical demand dimension ordering (as in the ADeLe paper).
# All modules should import DEMAND_ORDER from adele.analysis.constants.
from adele.analysis.constants import DEMAND_ORDER

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
    "DEMAND_ORDER",
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

