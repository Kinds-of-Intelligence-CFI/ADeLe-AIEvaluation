"""Package-wide constants — the single source of truth shared by all subpackages.

Kept dependency-free (no pandas/sklearn/inspect) so any subpackage can import it
without pulling heavy dependencies.
"""

# Canonical ordering of the 18 DeLeAn v1.0 demand dimensions (as in the paper).
# Every subpackage imports this from here — do not redefine it elsewhere.
DEMAND_ORDER = [
    "AS", "CEc", "CEe", "CL", "MCr",
    "MCt", "MCu", "MSm", "QLl", "QLq",
    "SNs", "KNa", "KNc", "KNf", "KNn",
    "KNs", "AT", "VO",
]

# v1.0 published its mind-modelling dimension as ``MS``. v2 splits communication out
# as ``MSc``, which makes ``MS`` the narrower of the two, so the parent was renamed
# ``MSm``. The construct is unchanged and no rubric text was edited - only the code.
#
# Data published under the old code keeps it: the released battery CSV, the existing
# label sets, and the frozen paper-reproduction scripts (``demand_profiles.R``,
# ``scc_and_ability_profiles.ipynb``) all still say ``MS`` and all still work, because
# they read the CSV directly. The Python toolkit renames on load - see
# ``adele.data.battery.load_battery`` - so everything downstream of it sees ``MSm``.
LEGACY_DEMAND_ALIASES = {"MS": "MSm"}
