"""
Tests for the rubrics module.
"""

import pytest
from adele.rubrics.catalog import RubricsCatalog, Rubric, validate_rubric, warn_if_mixed_versions


class TestRubricsCatalog:
    """Tests for RubricsCatalog loading and access."""

    def test_loads_bundled_rubrics(self):
        catalog = RubricsCatalog()
        assert len(catalog) == 18

    def test_acronyms_sorted(self):
        catalog = RubricsCatalog()
        acronyms = catalog.acronyms
        assert acronyms == sorted(acronyms)
        assert "AS" in acronyms
        assert "VO" in acronyms

    def test_get_returns_rubric(self):
        catalog = RubricsCatalog()
        rubric = catalog.get("AS")
        assert rubric is not None
        assert isinstance(rubric, Rubric)
        assert rubric.acronym == "AS"
        assert rubric.full_name == "Attention and Scan"
        assert len(rubric.content) > 100

    def test_get_missing_returns_none(self):
        catalog = RubricsCatalog()
        assert catalog.get("NONEXISTENT") is None

    def test_getitem_raises_keyerror(self):
        catalog = RubricsCatalog()
        with pytest.raises(KeyError, match="NONEXISTENT"):
            _ = catalog["NONEXISTENT"]

    def test_contains(self):
        catalog = RubricsCatalog()
        assert "AS" in catalog
        assert "NONEXISTENT" not in catalog

    def test_iter_yields_rubrics(self):
        catalog = RubricsCatalog()
        rubrics = list(catalog)
        assert len(rubrics) == 18
        assert all(isinstance(r, Rubric) for r in rubrics)

    def test_list_returns_dicts(self):
        catalog = RubricsCatalog()
        items = catalog.list()
        assert len(items) == 18
        assert all("acronym" in item and "full_name" in item for item in items)

    def test_custom_folder_nonexistent(self):
        catalog = RubricsCatalog("/nonexistent/path")
        assert len(catalog) == 0

    def test_skips_ug_choice_num(self):
        """UG_choice_num.txt is not a demand rubric and should be skipped."""
        catalog = RubricsCatalog()
        assert "UG_choice_num" not in catalog


class TestValidateRubric:
    """Tests for rubric validation."""

    def test_empty_content(self):
        valid, msg = validate_rubric("")
        assert not valid

    def test_short_content(self):
        valid, msg = validate_rubric("too short")
        assert not valid

    def test_valid_rubric_from_catalog(self):
        catalog = RubricsCatalog()
        rubric = catalog.get("AS")
        valid, msg = validate_rubric(rubric.content)
        assert valid


_VALID = (
    "Intro paragraph long enough to pass the rubric length check comfortably here.\n"
    "Level 0: none. Examples: x\nLevel 1: low. Examples: x\nLevel 2: mid. Examples: x\n"
    "Level 3: hi. Examples: x\nLevel 4: vhi. Examples: x\nLevel 5: max. Examples: x\n"
)


class TestRubricVersions:
    """Version flags: v1.0 vs v2-draft, parsed from an optional '#!' line."""

    def test_bundled_v1_rubrics_are_version_v1(self):
        c = RubricsCatalog()
        assert c.versions == {"v1.0"}
        assert c.get("QLl").full_name == "Logical Reasoning"  # from the '# Title' header

    def test_meta_line_sets_version_and_is_stripped(self, tmp_path):
        f = tmp_path / "XX.txt"
        f.write_text("# Demo\n#! version: v2-draft\n" + _VALID)
        r = RubricsCatalog.from_paths([f]).get("XX")
        assert r.version == "v2-draft"
        assert r.full_name == "Demo"
        assert "#!" not in r.content and "# Demo" not in r.content

    def test_warn_if_mixed_versions(self, tmp_path):
        a = tmp_path / "AA.txt"; a.write_text("# A\n" + _VALID)
        b = tmp_path / "BB.txt"; b.write_text("# B\n#! version: v2-draft\n" + _VALID)
        mixed = RubricsCatalog.from_paths([a, b])
        assert mixed.versions == {"v1.0", "v2-draft"}
        assert warn_if_mixed_versions(mixed) is not None
        assert warn_if_mixed_versions(RubricsCatalog.from_paths([a])) is None
