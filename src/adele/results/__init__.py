"""Public per-instance results: fetchers + the model × instance success matrix.

This package turns the public record of frontier-model evaluations into one
normalized table (see :mod:`adele.results.schema`):

    benchmark · instance_id · model · scaffold · success · n_trials · source

so demand annotations (per instance) can be joined against every model at once.

Sources (each in :mod:`adele.results.sources`) come in two kinds:
- **bulk**: downloadable artifacts — SWE-bench/experiments checkout, MathArena
  parquet dumps, Inspect ``.eval`` logs or partner-extracted score CSVs;
- **scrape**: public web UIs that publish per-instance results without dumps —
  ARC Prize results pages (network access required at call time).

Aggregate-only sources (e.g. tau2 leaderboard submissions) are exposed
separately and never mixed into the instance matrix silently.
"""

from adele.results.schema import RESULT_COLUMNS, normalize, validate_results
from adele.results.join import concat_results, success_matrix

__all__ = [
    "RESULT_COLUMNS",
    "normalize",
    "validate_results",
    "concat_results",
    "success_matrix",
]
