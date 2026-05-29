"""Composite result versioning for ADeLe-on-Inspect evaluations.

A result is only meaningful relative to four moving parts: the rubric set, the
demand-annotation battery, the grader, and the underlying benchmark. We record
all of them and derive a short hash so results are pooled/compared only when
these match. Change any component and the version bumps.
"""

import hashlib
from typing import Dict, Optional

RUBRICS_VERSION = "v1.0"          # DeLeAn rubric set + 0-5 scheme (paper section 10)
BATTERY_VERSION = "v1dot0"        # HF dataset ADeLe_battery_v1dot0
SCORER_SUITE_VERSION = "0.1.0"    # this module's scoring logic


def result_version(judge_model: Optional[str] = None) -> Dict[str, Optional[str]]:
    """The composite version key recorded on every run.

    ``grader`` splits by task type: MC scoring is judge-free (judge=None);
    Open-ended scoring is graded by ``judge_model``. ``benchmark`` is per-sample
    (carried in Sample.metadata), so it is not repeated here.
    """
    return {
        "rubrics": RUBRICS_VERSION,
        "battery": BATTERY_VERSION,
        "scorer_suite": SCORER_SUITE_VERSION,
        "judge": judge_model,
    }


def version_hash(judge_model: Optional[str] = None) -> str:
    """Short stable hash of the composite version, for grouping/comparison."""
    v = result_version(judge_model)
    payload = "|".join(f"{k}={v[k]}" for k in sorted(v))
    return hashlib.sha256(payload.encode()).hexdigest()[:12]
