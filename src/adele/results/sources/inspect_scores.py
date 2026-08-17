"""Per-sample scores from Inspect ``.eval`` logs — ours or a partner's.

Two entry points:

- :func:`from_logs` reads local Inspect logs (needs inspect-ai, the [eval]
  extra) — used for evaluations we run ourselves.
- :func:`from_csv` ingests the tiny CSV produced by
  ``scripts/extract_scores_standalone.py``. That script is what we send to
  partners who hold logs they cannot share in full (Epoch AI, Scale/Transluce):
  it extracts ONLY (task, model, sample_id, epoch, score) — no prompts, no
  completions, no metadata — so the whole hand-back is a few hundred KB and
  auditable in one screen. This module is the receiving end.

Both produce schema-valid instance-level rows.
"""

import logging
from pathlib import Path
from typing import Iterable, Optional

import pandas as pd

from adele.results.schema import merge_trials, normalize

logger = logging.getLogger(__name__)

CSV_COLUMNS = ["benchmark", "model", "sample_id", "epoch", "score"]

# Inspect score values → success in [0,1]
_VALUE_MAP = {"C": 1.0, "I": 0.0, "P": 0.5, "N": None}


def _to_success(value) -> Optional[float]:
    if isinstance(value, str):
        key = value.strip().upper()
        if key in _VALUE_MAP:
            return _VALUE_MAP[key]
        value = key  # numeric string ("0.5") falls through to float()
    try:
        v = float(value)
    except (TypeError, ValueError):
        return None
    return min(max(v, 0.0), 1.0)


def from_csv(
    csv_path: str | Path,
    *,
    scaffold: str = "none",
    source: str = "partner-extract",
) -> pd.DataFrame:
    """Ingest an extractor CSV (columns: benchmark, model, sample_id, epoch, score)."""
    raw = pd.read_csv(csv_path)
    missing = set(CSV_COLUMNS) - set(raw.columns)
    if missing:
        raise ValueError(f"{csv_path}: missing columns {sorted(missing)} "
                         f"(expected {CSV_COLUMNS})")
    df = pd.DataFrame({
        "benchmark": raw["benchmark"].astype(str),
        "instance_id": raw["sample_id"].astype(str),
        "model": raw["model"].astype(str),
        "scaffold": scaffold,
        "success": raw["score"].map(_to_success),
        "n_trials": 1,
    })
    n_unscored = int(df["success"].isna().sum())
    if n_unscored:
        logger.info("%s: dropping %d NOANSWER/unparseable rows", csv_path, n_unscored)
        df = df.dropna(subset=["success"])
    df = normalize(df, source=source, trial_level=True)
    return merge_trials(df)  # epochs of one sample → success rate


def from_logs(
    log_paths: Iterable[str | Path],
    *,
    scaffold: str = "none",
    source: str = "inspect-logs",
    scorer: Optional[str] = None,
) -> pd.DataFrame:
    """Read local Inspect .eval logs into the results schema (needs [eval])."""
    try:
        from inspect_ai.log import read_eval_log
    except ImportError as exc:
        raise ImportError("reading .eval logs needs inspect-ai: "
                          'pip install "adele[eval]"') from exc
    rows = []
    for p in log_paths:
        log = read_eval_log(str(p))
        task = getattr(log.eval, "task", "unknown")
        model = str(getattr(log.eval, "model", "unknown"))
        for s in log.samples or []:
            scores = s.scores or {}
            sc = scores.get(scorer) if scorer else next(iter(scores.values()), None)
            if sc is None:
                continue
            success = _to_success(getattr(sc, "value", None))
            if success is None:
                continue
            rows.append({
                "benchmark": task,
                "instance_id": str(s.id),
                "model": model,
                "scaffold": scaffold,
                "success": success,
                "n_trials": 1,
            })
    df = pd.DataFrame(rows)
    if len(df) == 0:
        return df
    return merge_trials(normalize(df, source=source, trial_level=True))
