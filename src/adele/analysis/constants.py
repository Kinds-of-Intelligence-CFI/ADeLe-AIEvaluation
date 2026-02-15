"""
Shared constants for the analysis sub-package.
"""

# Canonical demand dimension ordering (as in the ADeLe paper).
# All modules should import DEMAND_ORDER from here.
DEMAND_ORDER = [
    "AS", "CEc", "CEe", "CL", "MCr",
    "MCt", "MCu", "MS", "QLl", "QLq",
    "SNs", "KNa", "KNc", "KNf", "KNn",
    "KNs", "AT", "VO",
]
