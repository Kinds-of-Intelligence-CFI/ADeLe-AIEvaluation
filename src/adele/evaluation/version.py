"""Composite result versioning for ADeLe-on-Inspect evaluations.

A result is only meaningful relative to four moving parts: the rubric set, the
demand-annotation battery, the grader, and the underlying benchmark. We record
all of them and derive a short hash so results are pooled/compared only when
these match. Change any component and the version bumps.

The rubric set and scorer suite are versioned by **content hash**, not a
hand-maintained string: editing a bundled rubric ``.txt`` or the scoring logic
changes the fingerprint (and therefore the composite hash) automatically, so an
edit can't silently slip through unversioned. Each keeps a human-readable
semantic label (e.g. ``v1.0``) with the content fingerprint appended:
``v1.0+ab12cd34``.
"""

import hashlib
from functools import lru_cache
from pathlib import Path
from typing import Dict, Iterable, Optional

# Human-readable semantic labels (the paper's v1.0 artifacts). A content
# fingerprint is appended to the rubric/scorer labels below.
RUBRICS_LABEL = "v1.0"        # DeLeAn rubric set + 0-5 scheme (paper section 10)
BATTERY_VERSION = "v1dot0"    # HF dataset ADeLe_battery_v1dot0
SCORER_LABEL = "0.1.0"        # scoring-suite semantic version

# Content sources for the fingerprints (resolve in both editable and installed
# layouts: the rubric .txt files and scoring.py both ship inside the package).
_RUBRICS_DATA_DIR = Path(__file__).resolve().parent.parent / "rubrics" / "data"
_SCORING_MODULE = Path(__file__).resolve().parent / "scoring.py"


def _fingerprint(paths: Iterable[Path]) -> str:
    """Short stable hash of the given files' names + contents (sorted by name)."""
    h = hashlib.sha256()
    for p in sorted(paths, key=lambda x: x.name):
        h.update(p.name.encode())
        h.update(b"\0")
        h.update(p.read_bytes())
        h.update(b"\0")
    return h.hexdigest()[:8]


@lru_cache(maxsize=1)
def rubrics_version() -> str:
    """``RUBRICS_LABEL`` + a fingerprint of the bundled rubric ``.txt`` files."""
    if not _RUBRICS_DATA_DIR.is_dir():
        return RUBRICS_LABEL
    return f"{RUBRICS_LABEL}+{_fingerprint(_RUBRICS_DATA_DIR.glob('*.txt'))}"


@lru_cache(maxsize=1)
def scorer_suite_version() -> str:
    """``SCORER_LABEL`` + a fingerprint of the scoring-logic source."""
    if not _SCORING_MODULE.is_file():
        return SCORER_LABEL
    return f"{SCORER_LABEL}+{_fingerprint([_SCORING_MODULE])}"


def result_version(judge_model: Optional[str] = None) -> Dict[str, Optional[str]]:
    """The composite version key recorded on every run.

    ``grader`` splits by task type: MC scoring is judge-free (judge=None);
    Open-ended scoring is graded by ``judge_model``. ``benchmark`` is per-sample
    (carried in Sample.metadata), so it is not repeated here. ``rubrics`` and
    ``scorer_suite`` carry content fingerprints (see module docstring).
    """
    return {
        "rubrics": rubrics_version(),
        "battery": BATTERY_VERSION,
        "scorer_suite": scorer_suite_version(),
        "judge": judge_model,
    }


def version_hash(judge_model: Optional[str] = None) -> str:
    """Short stable hash of the composite version, for grouping/comparison."""
    v = result_version(judge_model)
    payload = "|".join(f"{k}={v[k]}" for k in sorted(v))
    return hashlib.sha256(payload.encode()).hexdigest()[:12]
