"""Per-source fetchers. Each returns a frame in the results schema
(:mod:`adele.results.schema`), or a clearly-named aggregate frame when the
source publishes no instance-level data.

Bulk sources (local artifacts): swebench, matharena, inspect_scores.
Scrape sources (network at call time): arcprize.
Aggregate-only: tau2 (per-domain pass@k; trajectories are maintainer-gated).
"""

from adele.results.sources import swebench, matharena, tau2, arcprize, inspect_scores  # noqa: F401

__all__ = ["swebench", "matharena", "tau2", "arcprize", "inspect_scores"]
