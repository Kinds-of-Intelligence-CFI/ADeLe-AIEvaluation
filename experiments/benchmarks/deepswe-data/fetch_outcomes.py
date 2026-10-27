"""DeepSWE v1.1 per-trial outcomes from Datacurve's public data page.

No login needed. deepswe.datacurve.ai's data page loads static JSON "artifacts" from
/artifacts/<version>/<name>.json (see the site bundle: ``/artifacts/${name}.json``). Three are used:

  trials.json            one row per rollout (31,617 on 2026-10-01; ~51 MB): task, model, config,
                         reward, outcome, error category, test counts, tokens, cost, timestamps
  leaderboard-live.json  one row per configuration (harness + model + reasoning effort)
  tasks.json             the 113 task ids with repository and language

The gated Hugging Face dataset datacurve/deep-swe-leaderboard holds a v1.0 job (2026-06-06), not
v1.1, so it is not used. The raw JSON is cached in data/downloads/deepswe-v1.1/ (gitignored);
delete it to refresh. No task text, patches or trajectories are read or written.

Datacurve's scoring rule (leaderboard-live.json "unit"): pass@1 is over scored attempts; agent
timeouts and context-window failures are scored failures; provider, verifier and network errors
are excluded (``included_in_score`` false, outcome ``excluded_error``).

Datacurve states no terms for the trial data (issue #94), so per-trial and per-(config, task) data
stay local (Pablo, 2026-10-01). Writes, to data/raw/deepswe-v1.1/ (gitignored):
  trials_v1-1.csv.gz     one line per trial (ids, outcome, numbers); ``trial`` numbers the
                         rollouts of a (config, task) pair 1..4 by start time
  trials_compact_v1-1.json  per (config, task) digit strings, the format of
                         adele.results.sources.harbor_hub.from_export
  leaderboard_full_v1-1.tsv  one line per configuration (row_id = config), with run dates, cost, tokens
  tasks_v1-1.csv         per task: models, configs, scored trials, passes, solve rate, Epoch label
and, to experiments/benchmarks/panel/sources/deepswe-v1.1/ (tracked, aggregate only):
  leaderboard_v1-1.tsv   per configuration: model, effort, metrics_source, Datacurve's scores, run dates

Run: python experiments/benchmarks/deepswe-data/fetch_outcomes.py
"""

import json
import urllib.request
from pathlib import Path

import pandas as pd

SITE = "https://deepswe.datacurve.ai/artifacts/v1.1"
ARTIFACTS = ["trials", "leaderboard-live", "tasks"]
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CACHE = ROOT / "data" / "downloads" / "deepswe-v1.1"
OUT = ROOT / "data" / "raw" / "deepswe-v1.1"
BOARD = HERE.parent / "panel" / "sources" / "deepswe-v1.1"

TRIAL_COLS = ["trial_name", "task", "config", "model", "provider", "harness", "reasoning_effort",
              "trial", "run_attempt", "reward", "passed", "outcome", "included_in_score",
              "error_category", "exception_type", "f2p_passed", "f2p_total", "p2p_passed",
              "p2p_total", "n_agent_steps", "n_input_tokens", "n_output_tokens", "cost_usd",
              "started_at", "finished_at", "agent_duration_seconds", "metrics_source",
              "epoch_named_false_negative"]


def artifact(name: str) -> dict:
    path = CACHE / f"{name}.json"
    if not path.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(f"{SITE}/{name}.json", headers={"User-Agent": "adele-data/0.1"})
        path.write_bytes(urllib.request.urlopen(req, timeout=600).read())
    return json.loads(path.read_text())


def main() -> None:
    trials, board, tasks = (artifact(n) for n in ARTIFACTS)
    df = pd.DataFrame(trials["rows"]).rename(columns={"task_name": "task"})
    task_ids = {r["id"] for r in tasks["rows"]}
    assert len(df) == trials["n_trials"] and set(df.task) == task_ids and len(task_ids) == 113
    assert set(df.source) == {"deep-swe"} and df.trial_name.is_unique

    # Trial number within (config, task): run_attempt where given (GPT-6 Astra), else start order.
    df = df.sort_values(["config", "task", "run_attempt", "started_at", "trial_name"])
    df["trial"] = df.groupby(["config", "task"]).cumcount() + 1
    df["exception_type"] = df.exception.map(lambda e: e.get("exception_type") if isinstance(e, dict) else None)

    # Trials Epoch's review names as false negatives (trial ids are the part after "__").
    epoch = pd.read_csv(HERE / "epoch_defects.csv")
    named = {(t, s) for t, ids in zip(epoch.instance_id, epoch.named_trial_ids) for s in ids.split(";")}
    df["epoch_named_false_negative"] = [(t, n.split("__")[1]) in named for t, n in zip(df.task, df.trial_name)]
    assert df.epoch_named_false_negative.sum() == len(named), "an Epoch-named trial is missing"
    assert not df[df.epoch_named_false_negative].passed.any()

    # Our counts must reproduce Datacurve's leaderboard.
    lb = pd.DataFrame(board["rows"]).set_index("config")
    scored = df[df.included_in_score]
    mine = scored.groupby("config").agg(n_passed=("passed", "sum"), n_attempted=("passed", "size")).reindex(lb.index)
    assert set(lb.index) == set(df.config)
    assert (mine.n_passed == lb.n_passed).all() and (mine.n_attempted == lb.n_attempted).all()

    OUT.mkdir(parents=True, exist_ok=True)
    df.sort_values(["model", "config", "task", "trial"])[TRIAL_COLS].to_csv(
        OUT / "trials_v1-1.csv.gz", index=False, compression="gzip")

    dates = df.groupby("config").agg(metrics_source=("metrics_source", "first"),
                                     first_started=("started_at", "min"), last_finished=("finished_at", "max"),
                                     n_trials_all=("trial_name", "size"))
    assert (df.groupby("config").metrics_source.nunique() == 1).all()
    cols = ["model", "provider", "harness", "reasoning_effort", "pass_at_1", "pass_at_4", "n_passed",
            "n_attempted", "n_tasks_passed_any", "ci_half", "n_runs", "mean_cost_usd", "mean_output_tokens",
            "mean_agent_steps"]
    lbo = lb[cols].join(dates).rename(columns={"reasoning_effort": "effort"})
    lbo.insert(4, "accuracy", (100 * lbo.pass_at_1).round(1))  # percent, as in the Harbor Hub exports
    lbo["first_started"] = lbo.first_started.str[:10]
    lbo["last_finished"] = lbo.last_finished.str[:10]
    lbo.index.name = "row_id"
    lbo = lbo.sort_values("pass_at_1", ascending=False).round(4)
    lbo.to_csv(OUT / "leaderboard_full_v1-1.tsv", sep="\t")
    BOARD.mkdir(parents=True, exist_ok=True)
    lbo[["model", "provider", "harness", "effort", "metrics_source", "accuracy", "pass_at_1", "pass_at_4",
         "n_passed", "n_attempted", "n_tasks_passed_any", "ci_half", "first_started", "last_finished"]].to_csv(
        BOARD / "leaderboard_v1-1.tsv", sep="\t")

    # Compact per-(config, task) counts in the schema of adele.results.sources.harbor_hub.from_export
    # (one digit per task; at most 4 trials, so one digit suffices). "rewarded" counts scored trials,
    # "exceptions" the trials Datacurve excludes.
    tasks_sorted = sorted(task_ids)
    rows = []
    for config, d in df.groupby("config"):
        by_task = d.groupby("task")
        count = lambda s: "".join(str(int(s.get(k, 0))) for k in tasks_sorted)
        rows.append({"id": config, "model": d.model.iloc[0], "agent": d.harness.iloc[0],
                     "solved": count(by_task.apply(lambda x: (x.included_in_score & x.passed).sum())),
                     "rewarded": count(by_task.included_in_score.sum()),
                     "exceptions": count(by_task.apply(lambda x: (~x.included_in_score).sum())),
                     "exc": d[~d.included_in_score].error_category.value_counts().to_dict()})
    (OUT / "trials_compact_v1-1.json").write_text(json.dumps({
        "exported": board["generated_at"][:10],
        "source": f"{SITE}/trials.json (public), scored = included_in_score",
        "tasks": tasks_sorted, "rows": rows}))

    g = scored.groupby("task")
    summ = pd.DataFrame({
        "n_models": g.model.nunique(), "n_configs": g.config.nunique(),
        "n_trials": g.size(), "n_passed": g.passed.sum(),
        "n_excluded": df[~df.included_in_score].groupby("task").size(),
        "n_models_any_pass": scored[scored.passed].groupby("task").model.nunique(),
        "n_configs_any_pass": scored[scored.passed].groupby("task").config.nunique(),
        "n_epoch_named_fn_trials": df.groupby("task").epoch_named_false_negative.sum(),
    }).reindex(sorted(task_ids)).fillna(0).astype(int)
    summ["solve_rate"] = (summ.n_passed / summ.n_trials).round(4)
    summ["epoch_defect"] = epoch.set_index("instance_id").epoch_defect.reindex(summ.index).fillna("")
    summ.index.name = "instance_id"
    summ.to_csv(OUT / "tasks_v1-1.csv")

    print(f"{len(df)} trials ({len(scored)} scored), {df.model.nunique()} models, {df.config.nunique()} configs, "
          f"{len(task_ids)} tasks; never solved: {(summ.n_passed == 0).sum()}; "
          f"generated {board['generated_at'][:10]} -> {OUT}, {BOARD / 'leaderboard_v1-1.tsv'}")


if __name__ == "__main__":
    main()
