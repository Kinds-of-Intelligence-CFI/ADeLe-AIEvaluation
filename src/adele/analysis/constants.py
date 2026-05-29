"""
Shared constants for the analysis sub-package.

Re-exported from :mod:`adele.constants` (the single source of truth) so existing
imports (``from adele.analysis.constants import DEMAND_ORDER``) keep working.
"""

from adele.constants import DEMAND_ORDER

__all__ = ["DEMAND_ORDER"]
