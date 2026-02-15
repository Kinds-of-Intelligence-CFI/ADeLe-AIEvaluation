"""
Rubrics management.

Provides access to the bundled DeLeAn v1.0 demand-level rubrics
and utilities for loading, listing, and validating rubrics.
"""

from adele.rubrics.catalog import Rubric, RubricsCatalog, validate_rubric

__all__ = ["Rubric", "RubricsCatalog", "validate_rubric"]
