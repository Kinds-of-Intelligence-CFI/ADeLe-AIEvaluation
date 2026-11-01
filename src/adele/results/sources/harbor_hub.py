"""Terminal-Bench 4.0.0 leaderboard (Harbor Hub) → per-task success.

Harbor Hub (https://hub.harborframework.com) publishes the official Terminal-Bench 4.0
leaderboard; each leaderboard row's page lists its trials (task, reward, exception) in a
public Trials table, 100 per page. The pages load their data through server-side calls, and
bulk download (``harbor job download``) needs a Hub login, so the trials were exported
from the public pages in a browser (2026-09-27): for each row, a script paged through the
Trials table and counted, per task, the trials, the trials with reward 1, the trials with a
reward at all, and the trials with an exception. The export is
``data/downloads/terminal-bench-4/harbor_hub_trials_4-0-0.json`` (one digit string per row
and count, in the order of ``tasks``) with the leaderboard columns in
``leaderboard_4-0-0.tsv`` next to it. Every row has 5 trials of each of the 66 tasks.

``success`` is the share of rewarded trials with reward 1: a trial that ended without a
reward (for example an API error before grading) is missing, not a failure.
"""

import csv
import json
from pathlib import Path

import pandas as pd

from adele.results.schema import normalize


def from_export(trials_json: str | Path, leaderboard_tsv: str | Path, *, benchmark: str = "terminal-bench-4.0.0",
                n_trials_run: int = 5, source: str = "harbor-hub-tb4-leaderboard") -> pd.DataFrame:
    """One row per (task, leaderboard row), in the results schema.

    The defaults are Terminal-Bench 4.0.0's; other Harbor Hub leaderboards exported the same way pass their own
    (e.g. ``benchmark="terminal-bench-science-0.1", n_trials_run=3``).
    """
    data = json.loads(Path(trials_json).read_text())
    board = {r["row_id"]: r for r in csv.DictReader(open(leaderboard_tsv), delimiter="\t")}
    rows = []
    for rec in data["rows"]:
        meta = board[rec["id"]]
        for i, task in enumerate(data["tasks"]):
            solved, rewarded, errors = (int(rec[k][i]) for k in ("solved", "rewarded", "exceptions"))
            rows.append({
                "benchmark": benchmark, "instance_id": task,
                "model": rec["model"], "scaffold": f"{rec['agent']}|effort={meta['effort']}",
                "success": solved / rewarded if rewarded else float("nan"),
                "n_trials": rewarded, "n_trials_run": n_trials_run, "n_exceptions": errors,
                "effort": meta["effort"], "leaderboard_accuracy": float(meta["accuracy"]),
                "leaderboard_row": rec["id"], "source": source,
            })
    df = pd.DataFrame(rows)
    return normalize(df[df["n_trials"] > 0])
