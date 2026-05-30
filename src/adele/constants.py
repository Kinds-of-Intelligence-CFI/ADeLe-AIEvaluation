"""Package-wide constants — the single source of truth shared by all subpackages.

Kept dependency-free (no pandas/sklearn/inspect) so any subpackage can import it
without pulling heavy dependencies.
"""

# Canonical ordering of the 18 DeLeAn v1.0 demand dimensions (as in the paper).
# Every subpackage imports this from here — do not redefine it elsewhere.
DEMAND_ORDER = [
    "AS", "CEc", "CEe", "CL", "MCr",
    "MCt", "MCu", "MS", "QLl", "QLq",
    "SNs", "KNa", "KNc", "KNf", "KNn",
    "KNs", "AT", "VO",
]
