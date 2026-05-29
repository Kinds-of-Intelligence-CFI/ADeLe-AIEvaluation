"""
Analysis and profiling sub-package.

Provides demand profiling, ability profiling, and predictive
power analysis tools.

Heavy dependencies (scikit-learn, matplotlib, ...) are imported lazily so that
``import adele`` and the lightweight ``adele[eval]`` install stay cheap. The
public names below resolve on first access (PEP 562) — e.g.
``from adele.analysis import LogisticAbilityModel`` works unchanged but only
imports sklearn at that point. Install with ``pip install adele[analysis]``.
"""

import importlib

# Light, dependency-free — safe to import eagerly.
from adele.constants import DEMAND_ORDER

# name -> submodule it lives in (imported lazily on first access).
_LAZY = {
    "compute_demand_profile": "adele.analysis.demand",
    "plot_demand_profile": "adele.analysis.demand",
    "plot_from_csv": "adele.analysis.demand",
    "AbilityModel": "adele.analysis.ability",
    "LogisticAbilityModel": "adele.analysis.ability",
    "compute_ability_scores": "adele.analysis.ability",
    "compute_spearman_correlations": "adele.analysis.ability",
    "plot_ability_profile": "adele.analysis.ability",
    "plot_multi_model_ability": "adele.analysis.ability",
}

__all__ = ["DEMAND_ORDER", *_LAZY]


def __getattr__(name: str):
    if name in _LAZY:
        module = importlib.import_module(_LAZY[name])
        return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return sorted(__all__)
