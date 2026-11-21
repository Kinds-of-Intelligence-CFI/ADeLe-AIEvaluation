"""The normalized per-instance results schema.

One row = one (benchmark instance, model, scaffold) cell of the public record.

Columns:
    benchmark:   canonical benchmark slug (e.g. "swe-bench-verified", "aime-2026").
    instance_id: the benchmark's own instance identifier, unchanged. Uniqueness
                 is only guaranteed within a benchmark — always key joins on
                 (benchmark, instance_id).
    model:       model identifier as the source reports it (e.g. "claude-opus-5").
    scaffold:    agent/harness the model ran under ("none" for plain inference).
                 Public results are properties of the (model, scaffold) PAIR;
                 ability profiles must never collapse this column.
    success:     fraction of trials solved, in [0, 1]. For single-trial sources
                 this is exactly the 0/1 flag.
    n_trials:    number of trials behind ``success`` (>= 1).
    source:      short provenance slug (e.g. "swebench-experiments").

Design rule: fetchers may carry extra columns (cost, date, effort) — they are
preserved by :func:`normalize` — but the seven columns above are mandatory and
validated. Aggregate-only data (no instance_id) must NOT pass through this
schema; keep it in separate aggregate frames.
"""

from typing import Iterable, Optional

import pandas as pd

RESULT_COLUMNS = [
    "benchmark",
    "instance_id",
    "model",
    "scaffold",
    "success",
    "n_trials",
    "source",
]


def normalize(
    df: pd.DataFrame,
    *,
    benchmark: Optional[str] = None,
    scaffold: Optional[str] = None,
    source: Optional[str] = None,
    trial_level: bool = False,
) -> pd.DataFrame:
    """Coerce a fetcher frame into the results schema (extra columns kept).

    Args:
        df: frame containing at least instance_id, model, success — plus any of
            the schema columns; missing benchmark/scaffold/source can be filled
            from the keyword defaults.
        trial_level: allow repeated (benchmark, instance_id, model, scaffold)
            rows — one per trial — for frames that will pass through
            :func:`merge_trials` before use.
    """
    out = df.copy()
    for col, default in (
        ("benchmark", benchmark),
        ("scaffold", scaffold or "none"),
        ("source", source),
    ):
        if col not in out.columns:
            if default is None:
                raise ValueError(f"normalize: missing column '{col}' and no default given")
            out[col] = default
    if "n_trials" not in out.columns:
        out["n_trials"] = 1
    out["success"] = out["success"].astype(float)
    out["n_trials"] = out["n_trials"].astype(int)
    out["instance_id"] = out["instance_id"].astype(str)
    ordered = RESULT_COLUMNS + [c for c in out.columns if c not in RESULT_COLUMNS]
    out = out[ordered]
    validate_results(out, allow_trial_rows=trial_level)
    return out


def validate_results(df: pd.DataFrame, *, allow_trial_rows: bool = False) -> None:
    """Raise ValueError on schema violations; return None when valid."""
    missing = [c for c in RESULT_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"results frame missing columns: {missing}")
    if len(df) == 0:
        return
    bad = df["success"].dropna()
    if len(bad) and ((bad < 0) | (bad > 1)).any():
        raise ValueError("success must lie in [0, 1] (a rate, not a percentage)")
    if (df["n_trials"] < 1).any():
        raise ValueError("n_trials must be >= 1")
    if df["instance_id"].isna().any() or (df["instance_id"] == "").any():
        raise ValueError(
            "instance_id must be non-empty — aggregate-only data does not "
            "belong in the instance-level schema"
        )
    if not allow_trial_rows:
        # The same cell from two publishers is legitimate; within one source it
        # means unmerged trials.
        key = ["benchmark", "instance_id", "model", "scaffold", "source"]
        dupes = df.duplicated(subset=key)
        if dupes.any():
            raise ValueError(
                f"{int(dupes.sum())} duplicate {tuple(key)} rows — merge trials "
                "into success/n_trials (see merge_trials) instead"
            )


def merge_trials(df: pd.DataFrame, extra_keys: Iterable[str] = ()) -> pd.DataFrame:
    """Collapse repeated trials of the same cell into success-rate rows."""
    keys = ["benchmark", "instance_id", "model", "scaffold", "source", *extra_keys]
    grouped = df.groupby(keys, as_index=False).agg(
        _wins=("success", lambda s: float((s.astype(float) * 1.0).sum())),
        _n=("n_trials", "sum"),
    )
    grouped["success"] = grouped["_wins"] / grouped["_n"]
    grouped["n_trials"] = grouped["_n"].astype(int)
    return grouped.drop(columns=["_wins", "_n"])
