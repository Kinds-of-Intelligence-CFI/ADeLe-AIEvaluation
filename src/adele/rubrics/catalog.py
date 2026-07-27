"""
Rubrics management for demand-level annotation.

Provides the RubricsCatalog class for loading, listing, and accessing
demand-level rubrics. Ships with the 18 DeLeAn v1.0 demand rubrics. (A 19th
file, UG_choice_num.txt, is an answer-format classifier rather than a 0–5
demand rubric, so it does not pass validation and is not loaded as a demand;
see adele.annotation.unguessability_from_choices for the UG score.)

Usage:
    from adele.rubrics.catalog import RubricsCatalog

    catalog = RubricsCatalog()            # loads bundled rubrics
    catalog = RubricsCatalog("./my_rubrics/")  # loads custom rubrics

    rubric = catalog.get("AS")
    print(rubric.full_name)   # "Attention and Scan"
    print(rubric.content)     # full rubric text
"""

import re
import logging
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# ============================================================================
# Built-in acronym → full name mapping. 18 are 0–5 demand rubrics; UG_choice_num
# is the answer-format/unguessability classifier (not loaded as a demand rubric).
# The bundled rubrics now carry a '# Name' header (parsed as the full name); this
# mapping remains as a fallback for headerless or custom rubric files.
# ============================================================================
BUILTIN_RUBRIC_NAMES: Dict[str, str] = {
    "AS":  "Attention and Scan",
    "AT":  "Atypicality",
    "CEc": "Verbal Comprehension",
    "CEe": "Verbal Expression",
    "CL":  "Conceptualisation, Learning and Abstraction",
    "KNa": "Knowledge of Applied Sciences",
    "KNc": "Customary Everyday Knowledge",
    "KNf": "Knowledge of Formal Sciences",
    "KNn": "Knowledge of Natural Sciences",
    "KNs": "Knowledge of Social Sciences",
    "MCr": "Identifying Relevant Information",
    "MCt": "Critical Thinking Processes",
    "MCu": "Calibrating Knowns and Unknowns",
    "MSm": "Mind Modelling and Social Cognition",
    "QLl": "Logical Reasoning",
    "QLq": "Quantitative Reasoning",
    "SNs": "Spatio-physical Reasoning",
    "UG_choice_num": "Unguessability",
    "VO":  "Volume",
}


def default_rubrics_dir() -> Path:
    """Single source of truth for the v1.0 rubric ``.txt`` files: the package
    copy at ``adele/rubrics/data_v1`` (shipped in the wheel and used in source
    checkouts alike)."""
    return Path(__file__).resolve().parent / "data_v1"


@dataclass
class Rubric:
    """A single demand-level rubric.

    Attributes:
        acronym:   Short identifier (e.g. "AS", "MCr").
        full_name: Human-readable name (e.g. "Attention and Scan").
        content:   Full rubric text with level descriptions and examples.
        file_path: Absolute path to the source .txt file.
        version:   Rubric set the file declares (e.g. "v1.0", "v2-draft"),
                   read from an optional ``#!`` metadata line. Defaults to
                   "v1.0" when the file carries no such line, so a loaded
                   rubric always says which set it belongs to.
    """
    acronym: str
    full_name: str
    content: str
    file_path: str
    version: str = "v1.0"


class RubricsCatalog:
    """Manages a catalog of demand-level rubrics.

    Loads rubric files from a folder (defaulting to the bundled rubrics
    shipped with this package) and provides methods for listing, filtering,
    and accessing them.

    Rubric files are plain-text .txt files. Two formats are accepted:

    Format A (ADeLe-AIEvaluation — no header):
        The entire file is rubric content. The full name is resolved
        from the built-in BUILTIN_RUBRIC_NAMES mapping.

    Format B (delean-batch-manager — with header):
        First line is ``# Full Rubric Name``; remaining lines are content.
    """

    def __init__(self, rubrics_folder: Optional[str] = None):
        """Initialise the catalog.

        Args:
            rubrics_folder: Path to a folder containing .txt rubric files.
                If None, uses the bundled rubrics shipped with this package.
        """
        if rubrics_folder is None:
            self._folder = default_rubrics_dir()
        else:
            self._folder = Path(rubrics_folder)

        self._cache: Dict[str, Rubric] = {}
        self._load()

    @classmethod
    def from_paths(cls, paths: "Iterable[str | Path]",
                   mixed_versions_ok: bool = False) -> "RubricsCatalog":
        """Build a catalog from an explicit list of rubric ``.txt`` files.

        Unlike the folder constructor, this composes a catalog from files that
        may live in different directories — e.g. selecting, per dimension, which
        of several rubric source versions to use. Each file is parsed and
        validated exactly as in the folder loader.

        Set ``mixed_versions_ok`` when the composition deliberately spans rubric
        versions, so :func:`warn_if_mixed_versions` stays quiet. The v2 agentic
        set does this: ``MSm`` is v1's mind-modelling rubric, unchanged.
        """
        self = cls.__new__(cls)
        self._folder = None
        self._cache = {}
        self._mixed_versions_ok = mixed_versions_ok
        for p in paths:
            self._add_file(Path(p))
        return self

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get(self, acronym: str) -> Optional[Rubric]:
        """Get a rubric by acronym, or None if not found."""
        return self._cache.get(acronym)

    def __getitem__(self, acronym: str) -> Rubric:
        """Get a rubric by acronym; raises KeyError if not found."""
        if acronym not in self._cache:
            raise KeyError(
                f"Rubric '{acronym}' not found. "
                f"Available: {', '.join(sorted(self._cache))}"
            )
        return self._cache[acronym]

    def __contains__(self, acronym: str) -> bool:
        return acronym in self._cache

    def __len__(self) -> int:
        return len(self._cache)

    def __iter__(self):
        return iter(sorted(self._cache.values(), key=lambda r: r.acronym))

    def list(self) -> List[Dict[str, str]]:
        """List all rubrics as a list of dicts (acronym, full_name)."""
        return [
            {"acronym": r.acronym, "full_name": r.full_name}
            for r in self
        ]

    @property
    def acronyms(self) -> List[str]:
        """All loaded acronyms, sorted alphabetically."""
        return sorted(self._cache.keys())

    @property
    def versions(self) -> set:
        """The distinct rubric versions present in this catalog.

        A catalog should normally hold a single version; more than one means
        v1.0 and draft v2 rubrics have been composed together (see
        :func:`warn_if_mixed_versions`).
        """
        return {r.version for r in self._cache.values()}

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _load(self):
        """Load all .txt rubric files from self._folder."""
        if not self._folder.exists():
            logger.error("Rubrics folder does not exist: %s", self._folder)
            return
        if not self._folder.is_dir():
            logger.error("Rubrics path is not a directory: %s", self._folder)
            return

        count = sum(self._add_file(fp) for fp in sorted(self._folder.glob("*.txt")))
        logger.info("Loaded %d rubrics from %s", count, self._folder)

    def _add_file(self, fp: Path) -> bool:
        """Parse, validate and cache one rubric file. Returns True if added."""
        try:
            acronym, full_name, content, version = _parse_rubric_file(fp)
            is_valid, msg = validate_rubric(content)
            if not is_valid:
                logger.warning("Skipping invalid rubric %s: %s", fp.name, msg)
                return False
            self._cache[acronym] = Rubric(
                acronym=acronym,
                full_name=full_name,
                content=content,
                file_path=str(fp.resolve()),
                version=version,
            )
            return True
        except Exception as exc:
            logger.warning("Error loading rubric %s: %s", fp.name, exc)
            return False


# ============================================================================
# Module-level helpers
# ============================================================================

def _parse_meta_line(line: str) -> Dict[str, str]:
    """Parse a ``#! key: value | key: value`` metadata line into a dict.

    Segments are ``|``-separated; only ``key: value`` segments are kept, so a
    free-text lead like ``#! ADeLe v2 — DRAFT | version: v2-draft`` is fine
    (the lead has no colon and is ignored). Keys are lower-cased.
    """
    raw = line.lstrip()[2:]  # drop the leading '#!'
    out: Dict[str, str] = {}
    for part in raw.split("|"):
        if ":" in part:
            key, value = part.split(":", 1)
            out[key.strip().lower()] = value.strip()
    return out


def _parse_rubric_file(file_path: Path) -> Tuple[str, str, str, str]:
    """Parse a rubric .txt file, supporting both ADeLe and delean formats.

    An optional ``#!`` line (anywhere in the body) is treated as **metadata**:
    it is stripped from the returned content — so it never reaches the LLM
    judge — and its ``version`` key, if present, sets the rubric version. When
    no ``#!`` line declares a version, the version defaults to ``"v1.0"``.

    Returns:
        (acronym, full_name, content, version)
    """
    acronym = file_path.stem
    text = file_path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)

    if not lines:
        raise ValueError("Empty rubric file")

    first_line = lines[0].strip()

    # Format B: a '# Full Name' title line ('#!' is metadata, not a title).
    if first_line.startswith("#") and not first_line.startswith("#!"):
        full_name = first_line.lstrip("#").strip()
        body_lines = lines[1:]
    else:
        # Format A: no title — use built-in mapping
        full_name = BUILTIN_RUBRIC_NAMES.get(acronym, acronym)
        body_lines = lines

    # Pull out any '#!' metadata line(s) and strip them from the content, so
    # the flag is visible in the file but never sent to the judge.
    version = "v1.0"
    kept_lines = []
    for ln in body_lines:
        if ln.lstrip().startswith("#!"):
            version = _parse_meta_line(ln).get("version", version)
        else:
            kept_lines.append(ln)
    content = "".join(kept_lines).strip()

    return acronym, full_name, content, version


def warn_if_mixed_versions(catalog: "RubricsCatalog") -> Optional[str]:
    """Warn (and return the message) if a catalog mixes rubric versions.

    Composing canonical v1.0 rubrics with draft v2 rubrics in one annotation
    run is almost always a mistake — the sets use different dimensions and the
    v2 set is unvalidated. Returns ``None`` when the catalog is single-version.
    """
    if getattr(catalog, "_mixed_versions_ok", False):
        return None
    versions = catalog.versions
    if len(versions) > 1:
        msg = (
            f"Catalog mixes rubric versions {sorted(versions)}. v1.0 and draft "
            "v2 rubrics should not be annotated together; state which set you mean."
        )
        logger.warning(msg)
        return msg
    return None


def validate_rubric(content: str) -> Tuple[bool, str]:
    """Validate that rubric content follows the expected format.

    Checks for:
    - Non-empty content (≥100 characters)
    - Level descriptions 0 through 5
    - At least some examples

    Returns:
        (is_valid, message)
    """
    if not content or not content.strip():
        return False, "Empty rubric content"

    if len(content.strip()) < 100:
        return False, "Rubric content seems too short (< 100 chars)"

    levels_found = re.findall(r"[Ll]evel\s*[0-5]", content)
    if len(levels_found) < 6:
        return False, (
            f"Expected at least 6 level descriptions (0–5), found {len(levels_found)}"
        )

    examples = re.findall(r"[Ee]xamples?", content, re.IGNORECASE)
    if len(examples) < 6:
        return False, (
            f"Expected at least 6 example sections, found {len(examples)}"
        )

    return True, "Valid rubric"
