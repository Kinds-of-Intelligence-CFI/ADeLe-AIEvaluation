"""Terminal-Bench-Science 0.1 per-trial outcomes from the public Harbor Hub leaderboard.

No browser needed. The Hub is a Next.js app; its leaderboard pages load data through
React server actions, which accept anonymous POSTs (header ``Next-Action: <id>``, body a
JSON argument list) and answer in the RSC wire format, where line ``1:`` is the JSON
result. Two actions are used:

  fetchLeaderboardWithRows(leaderboardId)                -> leaderboard + rows + metrics
  fetchLeaderboardRowTrials({leaderboardId, rowIds, page}) -> 100 trials per page

The action ids are build hashes from the Hub's JS bundles (chunks 0-ht8u3ozefl_.js and
2-f26jsvkqgb3.js on 2026-10-01); they change when the Hub is redeployed. To refresh them,
fetch a row page and grep its chunks for ``createServerReference)("<id>",...,"<name>"``.

Writes, to experiments/benchmarks/panel/sources/terminal-bench-science-0.1/:
  harbor_hub_trials_0-1.json  per-task digit strings, the format of
                               adele.results.sources.harbor_hub.from_export
  leaderboard_0-1.tsv          one line per leaderboard row (incl. rows without public trials)
  trials_0-1.csv.gz            one line per trial: task, reward, tokens, cost, exception

Run: python experiments/benchmarks/tbsci-data/fetch_outcomes.py
"""

import csv
import gzip
import json
import urllib.request
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

HUB = "https://hub.harborframework.com"
DATASET_PATH = "/datasets/terminal-bench-science/terminal-bench-science/latest"
LEADERBOARD_ID = "9a545a14-78d0-44b4-9003-afe062522a47"  # "v0-1-eval", 3 trials per task
ACTION_ROWS = "403053b301d17dc8145029701e9b2615f4c6c0d0be"    # fetchLeaderboardWithRows
ACTION_TRIALS = "40b5777b78718418f0a08402d13908a9c3b109231b"  # fetchLeaderboardRowTrials
OUT = Path(__file__).resolve().parents[1] / "panel" / "sources" / "terminal-bench-science-0.1"
PREFIX = "terminal-bench-science/"


def action(path: str, action_id: str, arg) -> dict:
    req = urllib.request.Request(
        HUB + path, data=json.dumps([arg]).encode(), method="POST",
        headers={"Next-Action": action_id, "Accept": "text/x-component",
                 "Content-Type": "text/plain;charset=UTF-8", "User-Agent": "adele-data/0.1"})
    body = urllib.request.urlopen(req, timeout=60).read().decode()
    line = next(l for l in body.split("\n") if l.startswith("1:"))
    return json.loads(line[2:])


def row_trials(row_id: str) -> list:
    path = f"{DATASET_PATH}/leaderboards/v0-1-eval/rows/{row_id}"
    items, page = [], 1
    while True:
        res = action(path, ACTION_TRIALS, {"leaderboardId": LEADERBOARD_ID, "rowIds": [row_id], "page": page})
        items += res["items"]
        if page >= res["total_pages"]:
            break
        page += 1
    assert len(items) == len({t["id"] for t in items}) == res["total"], row_id
    return items


def main() -> None:
    board = action(DATASET_PATH + "?tab=leaderboard", ACTION_ROWS, LEADERBOARD_ID)
    rows = sorted(board["rows"], key=lambda r: r["rank"])
    trials = {r["id"]: row_trials(r["id"]) if r["n_trials"] else [] for r in rows}
    tasks = sorted({t["task_name"].removeprefix(PREFIX) for ts in trials.values() for t in ts})

    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "leaderboard_0-1.tsv", "w", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["row_id", "rank", "agent", "model", "effort", "accuracy", "accuracy_stderr", "passes",
                    "n_trials_board", "n_trials_public", "total_tokens", "total_cost_usd", "model_release_date",
                    "row_created"])
        for r in rows:
            m, x = r["metadata"], r["metrics"]
            w.writerow([r["id"], r["rank"], m["agent_display"]["label"], m["model_display"]["label"],
                        m["reasoning_effort"], round(x["accuracy"], 2), round(x["accuracy_stderr"], 2),
                        x["passes"], x["tasks"], len(trials[r["id"]]), x["total_tokens"],
                        round(x["total_cost_usd"], 2), m["model_release_date"], r["created_at"][:10]])

    export_rows = []
    for r in rows:
        ts = trials[r["id"]]
        if not ts:
            continue
        by_task = defaultdict(list)
        for t in ts:
            by_task[t["task_name"].removeprefix(PREFIX)].append(t)
        count = lambda pred: "".join(str(sum(pred(t) for t in by_task[k])) for k in tasks)
        export_rows.append({
            # most common slug: the Kimi K3 row mixes "kimi-k3" and "regwise" trials
            "id": r["id"], "model": Counter(t["model_name"] for t in ts).most_common(1)[0][0],
            "agent": ts[0]["agent_name"],
            "solved": count(lambda t: t["reward"] == 1),
            "rewarded": count(lambda t: t["reward"] is not None),
            "exceptions": count(lambda t: t["error_type"] is not None),
            "exc": dict(Counter(t["error_type"] for t in ts if t["error_type"])),
        })
        solved = sum(t["reward"] == 1 for t in ts)
        assert solved == r["metrics"]["passes"], (r["id"], solved, r["metrics"]["passes"])
    (OUT / "harbor_hub_trials_0-1.json").write_text(json.dumps({
        "exported": date.today().isoformat(),
        "source": f"{HUB} leaderboard v0-1-eval ({LEADERBOARD_ID}) via fetchLeaderboardRowTrials (public)",
        "tasks": tasks, "rows": export_rows}))

    cols = ["row_id", "task", "trial", "job_name", "agent_name", "agent_version", "model_provider", "model_name",
            "reward", "error_type", "input_tokens", "output_tokens", "cache_tokens", "cost_usd",
            "started_at", "finished_at", "status", "attempt", "n_attempts", "is_scored"]
    with gzip.open(OUT / "trials_0-1.csv.gz", "wt", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for rid, ts in trials.items():
            for t in sorted(ts, key=lambda t: (t["task_name"], t["job_name"] or "")):
                w.writerow([rid, t["task_name"].removeprefix(PREFIX), t["name"]] + [t.get(c) for c in cols[3:]])
    print(f"{len(rows)} rows ({len(export_rows)} with public trials) x {len(tasks)} tasks -> {OUT}")


if __name__ == "__main__":
    main()
