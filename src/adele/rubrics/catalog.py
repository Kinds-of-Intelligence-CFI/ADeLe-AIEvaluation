"""
Rubrics management for demand-level annotation.

Provides the RubricsCatalog class for loading, listing, and accessing
demand-level rubrics. Ships with the 19 bundled DeLeAn v1.0 rubrics.

Usage:
    from adele.rubrics.catalog import RubricsCatalog

    catalog = RubricsCatalog()            # loads bundled rubrics
    catalog = RubricsCatalog("./my_rubrics/")  # loads custom rubrics

    rubric = catalog.get("AS")
    print(rubric.full_name)   # "Attention and Search"
    print(rubric.content)     # full rubric text
"""

import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# ============================================================================
# Built-in acronym → full name mapping for the 19 DeLeAn v1.0 rubrics.
# The bundled rubrics in ADeLe-AIEvaluation don't contain a '# Name' header,
# so we provide this mapping explicitly.
# ============================================================================
BUILTIN_RUBRIC_NAMES: Dict[str, str] = {
    "AS":  "Attention and Search",
    "AT":  "Anticipation and Time Horizons",
    "CEc": "Causal and Effect — comprehension",
    "CEe": "Causal and Effect — execution",
    "CL":  "Compositionality and Levels of Abstraction",
    "KNa": "Knowledge — academic",
    "KNc": "Knowledge — common sense",
    "KNf": "Knowledge — factual / encyclopaedic",
    "KNn": "Knowledge — numerical / quantitative",
    "KNs": "Knowledge — specialised / professional",
    "MCr": "Metacognition — reflection",
    "MCt": "Metacognition — theory of mind",
    "MCu": "Metacognition — uncertainty",
    "MS":  "Memory and State Tracking",
    "QLl": "Quantitative and Logical Reasoning — logical",
    "QLq": "Quantitative and Logical Reasoning — quantitative",
    "SNs": "Sensorimotor — spatial",
    "UG_choice_num": "Understanding Instructions / Goals — choice and number",
    "VO":  "Vocabulary and Language",
}


@dataclass
class Rubric:
    """A single demand-level rubric.

    Attributes:
        acronym:   Short identifier (e.g. "AS", "MCr").
        full_name: Human-readable name (e.g. "Attention and Search").
        content:   Full rubric text with level descriptions and examples.
        file_path: Absolute path to the source .txt file.
    """
    acronym: str
    full_name: str
    content: str
    file_path: str


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
            self._folder = Path(__file__).parent / "data"
        else:
            self._folder = Path(rubrics_folder)

        self._cache: Dict[str, Rubric] = {}
        self._load()

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

    def get_content_dict(self) -> Dict[str, str]:
        """Return {acronym: content} for all loaded rubrics."""
        return {a: r.content for a, r in self._cache.items()}

    def get_rubrics_dict(self) -> Dict[str, dict]:
        """Return {acronym: {full_name, content}} for all rubrics."""
        return {
            a: {"full_name": r.full_name, "content": r.content}
            for a, r in self._cache.items()
        }

    def reload(self):
        """Re-load all rubrics from the folder."""
        self._cache.clear()
        self._load()

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

        count = 0
        for fp in sorted(self._folder.glob("*.txt")):
            try:
                acronym, full_name, content = _parse_rubric_file(fp)
                is_valid, msg = validate_rubric(content)
                if not is_valid:
                    logger.warning("Skipping invalid rubric %s: %s", fp.name, msg)
                    continue
                self._cache[acronym] = Rubric(
                    acronym=acronym,
                    full_name=full_name,
                    content=content,
                    file_path=str(fp.resolve()),
                )
                count += 1
            except Exception as exc:
                logger.warning("Error loading rubric %s: %s", fp.name, exc)

        logger.info("Loaded %d rubrics from %s", count, self._folder)


# ============================================================================
# Module-level helpers
# ============================================================================

def _parse_rubric_file(file_path: Path) -> Tuple[str, str, str]:
    """Parse a rubric .txt file, supporting both ADeLe and delean formats.

    Returns:
        (acronym, full_name, content)
    """
    acronym = file_path.stem
    text = file_path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)

    if not lines:
        raise ValueError("Empty rubric file")

    first_line = lines[0].strip()

    # Format B: header line starts with '#'
    if first_line.startswith("#"):
        full_name = first_line.lstrip("#").strip()
        content = "".join(lines[1:]).strip()
    else:
        # Format A: no header — use built-in mapping
        full_name = BUILTIN_RUBRIC_NAMES.get(acronym, acronym)
        content = text.strip()

    return acronym, full_name, content


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
