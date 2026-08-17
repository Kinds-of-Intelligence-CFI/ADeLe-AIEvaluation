"""SWE-bench experiments repo → per-instance resolved flags.

Source: a local clone of https://github.com/SWE-bench/experiments (a sparse
checkout of ``evaluation/<split>/*/results`` suffices — a few MB):

    git clone --depth 1 --filter=blob:none --sparse \
        https://github.com/SWE-bench/experiments
    cd experiments && git sparse-checkout set --no-cone '/evaluation/verified/*/results'

Each leaderboard entry ``evaluation/<split>/<YYYYMMDD_scaffold_model>/`` holds
``results/results.json`` with the list of resolved instance IDs. Unresolved =
(instance universe) − resolved − no_generation. The universe defaults to the
union of IDs seen across all entries of the split (schema verified against the
repo, 134 verified-split entries, 2026-08); pass the official ID list via
``instance_ids=`` for exactness.
"""

import json
import logging
import re
from pathlib import Path
from typing import Iterable, Optional

import pandas as pd

from adele.results.schema import normalize

logger = logging.getLogger(__name__)

BENCHMARK_BY_SPLIT = {
    "verified": "swe-bench-verified",
    "lite": "swe-bench-lite",
    "test": "swe-bench",
    "multimodal": "swe-bench-multimodal",
}

# Entry dirs look like 20251215_livesweagent_claude-opus-4-5. The split between
# scaffold and model is not mechanical; we keep the raw entry name and offer a
# best-effort split on the LAST known-model match.
_MODEL_HINTS = re.compile(
    r"(claude[-_][a-z0-9.-]+|gpt[-_][a-z0-9.-]+|o[134][a-z0-9-]*|gemini[-_][a-z0-9.-]+"
    r"|qwen[a-z0-9._-]*|deepseek[a-z0-9._-]*|kimi[a-z0-9._-]*|glm[a-z0-9._-]*"
    r"|llama[a-z0-9._-]*|grok[a-z0-9._-]*)$",
    re.IGNORECASE,
)


def split_entry_name(entry: str) -> tuple[str, str]:
    """('scaffold', 'model') best-effort from an entry directory name."""
    name = re.sub(r"^\d{8}_", "", entry)
    m = _MODEL_HINTS.search(name)
    if not m:
        return name, "unknown"
    model = m.group(0).lstrip("_-")
    scaffold = name[: m.start()].rstrip("_-") or "unknown"
    return scaffold, model


def fetch(
    experiments_dir: str | Path,
    *,
    split: str = "verified",
    instance_ids: Optional[Iterable[str]] = None,
    entries: Optional[Iterable[str]] = None,
) -> pd.DataFrame:
    """Per-instance 0/1 resolution for every leaderboard entry of a split."""
    root = Path(experiments_dir) / "evaluation" / split
    if not root.is_dir():
        raise FileNotFoundError(
            f"{root} not found — pass a checkout of SWE-bench/experiments "
            "(sparse checkout of evaluation/<split>/*/results is enough)"
        )
    per_entry: dict[str, set] = {}
    skipped: list[str] = []
    for res_file in sorted(root.glob("*/results/results.json")):
        entry = res_file.parent.parent.name
        if entries is not None and entry not in set(entries):
            continue
        try:
            data = json.loads(res_file.read_text())
            resolved = data.get("resolved", [])
            # some older entries store {"resolved": {"count": n, ...}}
            if not isinstance(resolved, list):
                skipped.append(entry)
                continue
            per_entry[entry] = set(resolved)
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("skipping %s: %s", entry, exc)
            skipped.append(entry)

    universe = (
        set(map(str, instance_ids))
        if instance_ids is not None
        else set().union(*per_entry.values()) if per_entry else set()
    )
    if instance_ids is None:
        logger.info(
            "SWE-bench %s: universe = union over %d entries = %d instances "
            "(pass instance_ids= for the official list)",
            split, len(per_entry), len(universe),
        )
    if skipped:
        logger.info("skipped %d entries without a resolved id list: %s",
                    len(skipped), skipped[:5])

    # Several leaderboard entries can share a (scaffold, model) pair (re-runs
    # at different dates); disambiguate by suffixing the entry date so each
    # entry stays its own column in the matrix.
    named = {entry: split_entry_name(entry) for entry in per_entry}
    counts: dict[tuple, int] = {}
    for pair in named.values():
        counts[pair] = counts.get(pair, 0) + 1

    rows = []
    for entry, resolved in per_entry.items():
        scaffold, model = named[entry]
        if counts[(scaffold, model)] > 1:
            scaffold = f"{scaffold}#{entry[:8]}"
        for iid in sorted(universe):
            rows.append({
                "instance_id": iid,
                "model": model,
                "scaffold": scaffold,
                "entry": entry,
                "success": 1.0 if iid in resolved else 0.0,
            })
    df = pd.DataFrame(rows)
    if len(df) == 0:
        return df
    return normalize(
        df,
        benchmark=BENCHMARK_BY_SPLIT.get(split, f"swe-bench-{split}"),
        source="swebench-experiments",
    )
