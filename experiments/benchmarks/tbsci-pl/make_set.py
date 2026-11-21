"""Build the Terminal-Bench Science 0.1 task table for tbsci-pl: all 70 tasks, with outcomes and flags.

Pablo's rule (2026-10-01): annotate all 70, flag, filter later. Two flags:
  solved_any   some scored trial of the 12 public leaderboard configurations solves the task
  open_issue   an open, score-relevant [TASK FIX] issue on harbor-framework/terminal-bench-science names the task

Outcomes: the Harbor Hub export in panel/sources/terminal-bench-science-0.1/ (12 configurations with public trials,
3 trials per task), read with adele.results.sources.harbor_hub.from_export. A trial without a reward is missing, not a
failure. Domain and field come from the task's path (tasks/<domain>/<field>/<task>); the task.toml spellings vary.

Issues: the open issues titled "[TASK FIX] ...", fetched once with curl from the GitHub search API and frozen in
open_issues.csv (delete it to refetch). An issue maps to a task when the task id appears in its title. All count as
score-relevant (they report a verifier that rejects correct work or accepts wrong work, an underspecified instruction,
or an environment fault) except those whose title names only a non-x86 platform (aarch64, amd64-only, linux-64-only,
x86_64 hardcoded): the leaderboard runs on x86_64, so those do not touch its scores.

    python experiments/benchmarks/tbsci-pl/make_set.py
"""

import json
import re
import subprocess
from datetime import date
from pathlib import Path

import pandas as pd

from adele.results.sources.harbor_hub import from_export

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BENCH = "terminal-bench-science-0.1"
SRC = HERE.parent / "panel/sources" / BENCH
REPO = "harbor-framework/terminal-bench-science"
SEARCH = f'repo:{REPO} is:issue is:open "TASK FIX" in:title'
PLATFORM_ONLY = re.compile(r"aarch64|amd64|x86_64|linux-64", re.I)


def fetch_issues(tasks: list[str]) -> pd.DataFrame:
    out = subprocess.run(["curl", "-sf", "-G", "https://api.github.com/search/issues", "--data-urlencode",
                          f"q={SEARCH}", "--data-urlencode", "per_page=100"],
                         capture_output=True, text=True, check=True).stdout
    data = json.loads(out)
    assert not data["incomplete_results"] and data["total_count"] <= 100, "paginate"
    rows = []
    for i in data["items"]:
        if not i["title"].startswith("[TASK FIX]"):
            continue
        hit = [t for t in tasks if re.search(rf"(?<![\w-]){re.escape(t)}(?![\w-])", i["title"])]
        assert len(hit) <= 1, i["title"]
        rows.append({"number": i["number"], "created_at": i["created_at"][:10], "task": hit[0] if hit else "",
                     "score_relevant": not PLATFORM_ONLY.search(i["title"]), "title": i["title"],
                     "url": i["html_url"], "fetched_on": date.today().isoformat()})
    return pd.DataFrame(rows).sort_values("number")


def main() -> None:
    meta = pd.read_csv(ROOT / f"data/instances/meta_{BENCH}.csv").set_index("instance_id")
    inst = pd.read_parquet(ROOT / f"data/instances/instances_{BENCH}.parquet")
    assert len(meta) == 70 and set(inst["instance_id"]) == set(meta.index)
    res = from_export(SRC / "harbor_hub_trials_0-1.json", SRC / "leaderboard_0-1.tsv", benchmark=BENCH, n_trials_run=3)
    assert res["leaderboard_row"].nunique() == 12 and set(res["instance_id"]) == set(meta.index)
    g = res.assign(solved=res["success"] * res["n_trials"]).groupby("instance_id")
    out = pd.DataFrame({"n_configs": g["leaderboard_row"].nunique(), "trials": g["n_trials"].sum(),
                        "solved": g["solved"].sum().round().astype(int)})
    out["solve_rate"] = (out["solved"] / out["trials"]).round(4)

    issues_file = HERE / "open_issues.csv"
    if not issues_file.exists():
        fetch_issues(sorted(meta.index)).to_csv(issues_file, index=False)
    issues = pd.read_csv(issues_file)
    rel = issues[issues["score_relevant"] & issues["task"].notna()]
    nums = rel.groupby("task")["number"].apply(lambda s: ";".join(map(str, sorted(s))))

    parts = meta["path"].str.split("/")
    out = pd.DataFrame({"domain": parts.str[1], "field": parts.str[2],
                        "expert_hours": meta["expert_time_estimate_hours"]}).join(out)
    out["solved_any"] = out["solved"] > 0
    out["open_issues"] = nums.reindex(out.index).fillna("")
    out["open_issue"] = out["open_issues"] != ""
    out = out.rename_axis("instance_id").sort_index().reset_index()
    out.to_csv(HERE / "tasks.csv", index=False)

    print(f"{len(out)} tasks; solved_any {int(out['solved_any'].sum())}; open_issue {int(out['open_issue'].sum())}; "
          f"both solved_any and no open_issue {int((out['solved_any'] & ~out['open_issue']).sum())}")
    print(f"issues fetched {issues['fetched_on'].iloc[0]}: {len(issues)} open [TASK FIX]; "
          f"{int((issues['task'].fillna('') != '').sum())} name a TB-Science 0.1 task; {len(rel)} score-relevant")
    unmapped = issues[issues["task"].fillna("") == ""]
    print("not a 0.1 task:", "; ".join(f"#{r.number} {r.title[11:60]}" for r in unmapped.itertuples()))


if __name__ == "__main__":
    main()
