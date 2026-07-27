"""Agentic evaluation: v2 rubric library + whole-task validation.

This package extends ADeLe from static tasks toward agent rollouts. The first
step is the **v2 agentic rubric library** and a harness to **validate** it
against human judgement (see ``AGENTIC_METHODOLOGY.md``).

The v2 rubrics are drafted across **two source documents** ("Paolo_Pablo" and "Marko";
see ``MANIFEST.tsv``). Faithful per-source conversions live under
``rubrics/data_v2/{Paolo_Pablo,Marko}/``; ``MANIFEST.tsv`` records provenance and the
single **active selection** used for annotation. ``load_active_catalog()``
composes that active set into a ``RubricsCatalog``.
"""

import csv
import hashlib
from dataclasses import dataclass, fields
from pathlib import Path
from typing import List

from adele.rubrics.catalog import RubricsCatalog, _parse_rubric_file

DATA_V2_DIR = Path(__file__).resolve().parent.parent / "rubrics" / "data_v2"
MANIFEST_PATH = DATA_V2_DIR / "MANIFEST.tsv"


@dataclass(frozen=True)
class ManifestEntry:
    """One active v2 dimension and where it came from.

    ``sha256`` fingerprints the rubric file's bytes, so a silent edit to a
    source rubric is detectable (see ``adele.agentic.verify_manifest``).
    """
    code: str
    full_name: str
    source: str          # "Paolo_Pablo" | "Marko"
    rel_path: str        # path relative to DATA_V2_DIR, e.g. "Paolo_Pablo/PLp.txt"
    source_doc_id: str   # Google Doc id the rubric was converted from
    source_heading: str  # heading as written in that Doc
    version_date: str    # rubric version date if any, else "unknown"
    sha256: str

    @property
    def path(self) -> Path:
        return DATA_V2_DIR / self.rel_path


def read_manifest() -> List[ManifestEntry]:
    """Parse ``MANIFEST.tsv`` into ``ManifestEntry`` rows (manifest order)."""
    with open(MANIFEST_PATH, newline="", encoding="utf-8") as f:
        return [ManifestEntry(**row) for row in csv.DictReader(f, delimiter="\t")]


def active_demands() -> List[str]:
    """The dimension codes in the active v2 set, in manifest order."""
    return [e.code for e in read_manifest()]


def load_active_catalog() -> RubricsCatalog:
    """Compose the active v2 rubric set (per the manifest) into a catalog."""
    return RubricsCatalog.from_paths(e.path for e in read_manifest())


# Source-document provenance, keyed by source tag. The per-dimension active
# selection (which source each code is taken from) lives in _ACTIVE below.
_DOCS = {
    "Paolo_Pablo":   {"doc_id": "1xBrJVip8f-b3pLsE1xO1kijSbBvBRgGsUIRXlHDuerk", "version_date": "2025-07-26"},
    "Marko": {"doc_id": "1tyaEcWqyn8N5TDbgNYnsC7ZiLTtynHCGoNps8Ag_8y0", "version_date": "unknown"},
    # MSm is v1's MS rubric carried into v2 under the new code; its judged text is
    # unchanged (see tests/test_agentic.py::test_MSm_text_is_v1_MS_unchanged). v1 itself
    # is untouched: data_v1/MS.txt and the published MS label column both stay as they are.
    "v1": {"doc_id": "arXiv:2503.06378 §10", "version_date": "1.0"},
}

# (code, source, source_heading-as-written-in-the-source, rel_path), in active-set order.
# Non-memory dims come from "Paolo_Pablo"; memory dims from "Marko"; MSm is carried from v1.
# ECc was removed from the agentic set (propensity, not ability) and MSe was renamed PLs.
#
# The active set is the text/tool-relevant agentic dimensions — the ones HAL
# benchmarks actually exercise. The four sensory/motor rubrics (Dexterity SNp,
# Kinesthetic SNk, Auditory SPa, Visual SPv) stay in the library under
# rubrics/data_v2/Paolo_Pablo/ but are NOT active: text-based agent tasks would score
# them all 0, so they add cost without signal. Re-activate them here for
# embodied/multimodal work.
_DEFERRED_MULTIMODAL = ("SNp", "SNk", "SPa", "SPv")

_ACTIVE = [
    ("PLp", "Paolo_Pablo", "Planning", "Paolo_Pablo/PLp.txt"),
    ("PLe", "Paolo_Pablo", "Action control and execution", "Paolo_Pablo/PLe.txt"),
    ("PLs", "Paolo_Pablo", "Environmental and situational understanding", "Paolo_Pablo/PLs.txt"),
    ("MSm", "v1", "Mind Modelling and Social Cognition", "v1/MSm.txt"),
    ("MSc", "Paolo_Pablo", "Communication and social interaction", "Paolo_Pablo/MSc.txt"),
    ("MMe", "Marko", "Episodic Memory", "Marko/MMe.txt"),
    ("MMp", "Marko", "Procedural Memory", "Marko/MMp.txt"),
    ("MMs", "Marko", "Working Memory", "Marko/MMs.txt"),
]


def build_manifest() -> None:
    """(Re)generate ``MANIFEST.tsv`` from the source files + ``_ACTIVE`` table.

    Run after editing a rubric file so the recorded ``sha256`` stays current::

        python -c "from adele.agentic import build_manifest; build_manifest()"
    """
    rows = []
    for code, source, heading, rel_path in _ACTIVE:
        _, full_name, _, _ = _parse_rubric_file(DATA_V2_DIR / rel_path)
        rows.append(ManifestEntry(
            code=code, full_name=full_name, source=source, rel_path=rel_path,
            source_doc_id=_DOCS[source]["doc_id"], source_heading=heading,
            version_date=_DOCS[source]["version_date"],
            sha256=_sha256(DATA_V2_DIR / rel_path),
        ))
    cols = [f.name for f in fields(ManifestEntry)]
    with open(MANIFEST_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, delimiter="\t")
        w.writeheader()
        for r in rows:
            w.writerow({c: getattr(r, c) for c in cols})


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_manifest() -> List[str]:
    """Return a list of drift problems (empty == manifest matches the files).

    Catches a missing file or a rubric whose bytes no longer match the
    ``sha256`` the manifest recorded.
    """
    problems = []
    for e in read_manifest():
        if not e.path.is_file():
            problems.append(f"{e.code}: missing file {e.rel_path}")
        elif _sha256(e.path) != e.sha256:
            problems.append(f"{e.code}: sha256 mismatch for {e.rel_path}")
    return problems
