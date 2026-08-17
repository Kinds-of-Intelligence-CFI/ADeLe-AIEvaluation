"""tau2/tau3-bench leaderboard → per-DOMAIN aggregates (NOT instance-level).

The public leaderboard submissions
(``web/leaderboard/public/submissions/*/submission.json`` in
https://github.com/sierra-research/tau2-bench) carry pass@1..4 per domain;
per-task trajectories are uploaded to the maintainers' S3 after review and are
not publicly indexed. This fetcher therefore returns an AGGREGATE frame — kept
deliberately outside the instance-level schema so it cannot be joined by
mistake. Ask Sierra for trajectory files if instance-level tau2 is needed.

Schema verified against the repo (65 submissions incl. claude-fable-5, 2026-08).
"""

import json
import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


def fetch_aggregates(tau2_repo: str | Path) -> pd.DataFrame:
    """One row per (submission, domain) with pass@k and metadata."""
    sub_dir = Path(tau2_repo) / "web" / "leaderboard" / "public" / "submissions"
    if not sub_dir.is_dir():
        raise FileNotFoundError(
            f"{sub_dir} not found — pass a checkout of sierra-research/tau2-bench"
        )
    rows = []
    for f in sorted(sub_dir.glob("*/submission.json")):
        entry = f.parent.name
        if entry.startswith("A_EXAMPLE"):
            continue
        try:
            d = json.loads(f.read_text())
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("skipping %s: %s", entry, exc)
            continue
        for domain, res in (d.get("results") or {}).items():
            if not res:
                continue
            rows.append({
                "benchmark": f"tau2-{domain}",
                "model": d.get("model_name", entry),
                "scaffold": "tau2-agent",
                "submitting_org": d.get("submitting_organization"),
                "submission_date": d.get("submission_date"),
                "reasoning_effort": d.get("reasoning_effort"),
                "user_simulator": (d.get("methodology") or {}).get("user_simulator"),
                **{k: res.get(k) for k in ("pass_1", "pass_2", "pass_3", "pass_4", "cost")},
                "trajectories_available": bool(d.get("trajectories_available")),
                "entry": entry,
                "source": "tau2-leaderboard",
            })
    df = pd.DataFrame(rows)
    logger.info("tau2 leaderboard: %d (submission, domain) aggregate rows — "
                "NO instance-level data; trajectories are maintainer-gated", len(df))
    return df
