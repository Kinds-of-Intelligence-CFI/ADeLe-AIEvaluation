"""ARC Prize results pages → per-task pass/fail for the newest frontier models.

ARC Prize independently runs frontier models and publishes, at
``https://arcprize.org/results/<slug>`` (e.g. ``anthropic-claude-opus-5``,
``anthropic-claude-fable-5``, ``openai-gpt-5-6``, ``moonshot-kimi-k3``), full
per-task pass/fail tables for the ARC-AGI-1 (400 tasks) and ARC-AGI-2 (120)
public eval sets, per reasoning-effort configuration. The bulk HF dump
(``arcprize/arc_agi_v2_public_eval``) lags by a model generation, so these
pages are the only per-instance record for the current one.

This fetcher needs network access at call time and parses best-effort: the
page structure is not an API and may change — every run reports how many
tasks it recovered, and fails loudly rather than returning a silently short
table. Re-verify counts against the page after any site redesign.
"""

import logging
import re
from typing import Iterable, Optional

import pandas as pd

from adele.results.schema import normalize

logger = logging.getLogger(__name__)

RESULTS_URL = "https://arcprize.org/results/{slug}"
EXPECTED_TASKS = {"arc-agi-1": 400, "arc-agi-2": 120}

# Task IDs are 8-char hex (v1) or "<hex>" style slugs; pass/fail is rendered as
# a glyph/class near the ID. We parse both a JSON payload (preferred, if the
# page embeds one) and the HTML table fallback.
_TASK_ROW = re.compile(
    r'(?P<task>\b[0-9a-f]{8}\b)[^0-9a-f].{0,400}?(?P<mark>✓|✔|✗|✘|pass|fail)',
    re.IGNORECASE | re.DOTALL,
)
_JSON_BLOB = re.compile(r'"task_id"\s*:\s*"(?P<task>[^"]+)"[^}]*?"(?:passed|correct|success)"\s*:\s*(?P<val>true|false)',
                        re.IGNORECASE)


def _get(url: str) -> str:
    try:
        import requests  # lazy
        resp = requests.get(url, timeout=60,
                            headers={"User-Agent": "adele-results/0.1 (research; contact maintainer)"})
        resp.raise_for_status()
        return resp.text
    except ImportError:
        from urllib.request import Request, urlopen
        req = Request(url, headers={"User-Agent": "adele-results/0.1 (research)"})
        with urlopen(req, timeout=60) as fh:
            return fh.read().decode("utf-8", errors="replace")


def parse_page(html: str) -> pd.DataFrame:
    """Extract (instance_id, success) pairs from a results page's content."""
    rows = [
        {"instance_id": m.group("task"), "success": m.group("val").lower() == "true"}
        for m in _JSON_BLOB.finditer(html)
    ]
    if not rows:
        rows = [
            {"instance_id": m.group("task"),
             "success": m.group("mark").lower() in ("✓", "✔", "pass")}
            for m in _TASK_ROW.finditer(html)
        ]
    df = pd.DataFrame(rows)
    if len(df):
        # keep the FIRST occurrence per task (pages may repeat ids in nav/links)
        df = df.drop_duplicates(subset="instance_id", keep="first")
    return df


def fetch(
    slugs: Iterable[str],
    *,
    benchmark: str = "arc-agi-2",
    min_tasks: Optional[int] = None,
) -> pd.DataFrame:
    """Per-task results for the given ARC Prize model slugs.

    Args:
        slugs: model result-page slugs (the model column keeps the slug —
            it encodes lab + model; effort variants appear as distinct slugs).
        min_tasks: fail if fewer tasks than this are recovered per page
            (default: 80% of the benchmark's public-set size, if known).
    """
    floor = min_tasks or int(0.8 * EXPECTED_TASKS.get(benchmark, 100))
    frames = []
    for slug in slugs:
        url = RESULTS_URL.format(slug=slug)
        html = _get(url)
        page = parse_page(html)
        if len(page) < floor:
            raise RuntimeError(
                f"{url}: recovered only {len(page)} tasks (< {floor}). The page "
                "layout has likely changed — update arcprize.parse_page, or the "
                "slug/benchmark pairing is wrong."
            )
        logger.info("%s: %d tasks parsed", slug, len(page))
        page = page.assign(model=slug, scaffold="arcprize-harness",
                           success=page["success"].astype(float))
        frames.append(page)
    df = pd.concat(frames, ignore_index=True)
    return normalize(df, benchmark=benchmark, source="arcprize-results-page")
