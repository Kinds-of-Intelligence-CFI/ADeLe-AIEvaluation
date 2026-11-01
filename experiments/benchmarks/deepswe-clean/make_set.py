"""Build the DeepSWE v1.1 clean set for deepswe-clean (README.md): the tb4-clean rule, applied here.

Keep every DeepSWE v1.1 task except:
  epoch_defect   one of the 23 tasks Epoch AI's review (2026-09-07) names as defective (all false negatives);
                 deepswe-data/epoch_defects.csv
  never_solved   no scored trial of any configuration solves it (there are none)
Low solve rates stay (Pablo, 2026-10-01): gql-incremental-graphql-delivery (3.6%) and bandit-structured-nosec-directives
(6.8%) are kept.

One flag, not an exclusion:
  community_issue  an open issue or PR on datacurve-ai/deep-swe (deepswe-data/community_issues.csv) claims that the
                   instruction is ambiguous or that the verifier rejects correct work on Datacurve's own runs, and
                   v1.1 has not fixed it. Not flagged: claims fixed in v1.1 (env drift and v1.0 gold failures; the
                   #52 oracle audit passes 112 of 113 golds), host-dependent failures (golds pass on Datacurve's
                   hosts), verifier hangs (cost time, do not fail correct code), metadata typos and the Dockerfile
                   fallback (the prebuilt image is used).

Outcomes: Datacurve's per-trial data in data/raw/deepswe-v1.1/trials_v1-1.csv.gz (gitignored; fetch_outcomes.py),
70 configurations, up to 4 trials per task. A trial is solved when `passed`; trials Datacurve excludes from its score
(provider, verifier, network errors) are missing, not failures. Two sensitivity rates drop configurations, flagged in
the tracked leaderboard (panel/sources/deepswe-v1.1/leaderboard_v1-1.tsv):
  solve_rate_pre_timeout  without the 8 configurations first run on or after 2026-08-26, when the repo raised the
                          agent timeout from 5,400 s to 10,800 s
  solve_rate_no_astra     without GPT-6 Astra's 5 configurations (metrics_source verified_openai_handoff: OpenAI-run)
DeepSWE has no difficulty or time estimate; solve rate is the only outcome. Writes tasks.csv: all 113 tasks.

    python experiments/benchmarks/deepswe-clean/make_set.py
"""

from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DATA = HERE.parent / "deepswe-data"
BENCH = "deepswe-v1.1"
TIMEOUT_RAISED = "2026-08-26"
FLAG_CLAIMS = {"underspecified_prompt", "test_too_strict", "flaky_p2p_gold_fails", "verifier_test_collision"}


def rates(scored: pd.DataFrame, configs: set[str]) -> pd.DataFrame:
    g = scored[scored["config"].isin(configs)].groupby("task")
    return pd.DataFrame({"n_configs": g["config"].nunique(), "n_trials": g.size(),
                         "solved_trials": g["passed"].sum().astype(int)})


def main() -> None:
    meta = pd.read_csv(ROOT / f"data/instances/meta_{BENCH}.csv").set_index("instance_id")
    inst = pd.read_parquet(ROOT / f"data/instances/instances_{BENCH}.parquet")
    assert len(meta) == 113 and set(inst["instance_id"]) == set(meta.index)
    tail = "IMPORTANT: Please work on this in a new branch from main and commit everything when you are done."
    assert inst["prompt"].str.rstrip().str.endswith(tail).all(), "prompt must keep the closing branch-and-commit line"

    board = pd.read_csv(HERE.parent / f"panel/sources/{BENCH}/leaderboard_v1-1.tsv", sep="\t").set_index("row_id")
    trials = pd.read_csv(ROOT / f"data/raw/{BENCH}/trials_v1-1.csv.gz")
    assert len(board) == 70 and set(trials["config"]) == set(board.index) and set(trials["task"]) == set(meta.index)
    scored = trials[trials["included_in_score"]]
    # Our counts must reproduce Datacurve's leaderboard.
    by_cfg = scored.groupby("config")["passed"].agg(["sum", "size"]).reindex(board.index)
    assert (by_cfg["sum"] == board["n_passed"]).all() and (by_cfg["size"] == board["n_attempted"]).all()

    late = set(board.index[board["first_started"] >= TIMEOUT_RAISED])
    astra = set(board.index[board["metrics_source"] == "verified_openai_handoff"])
    assert len(late) == 8 and len(astra) == 5 and astra <= late
    out = rates(scored, set(board.index))
    out["solve_rate"] = out["solved_trials"] / out["n_trials"]
    for col, drop in (("solve_rate_pre_timeout", late), ("solve_rate_no_astra", astra)):
        r = rates(scored, set(board.index) - drop)
        out[col] = r["solved_trials"] / r["n_trials"]

    epoch = pd.read_csv(DATA / "epoch_defects.csv").set_index("instance_id")
    assert len(epoch) == 23 and set(epoch.index) <= set(meta.index)
    ci = pd.read_csv(DATA / "community_issues.csv")
    hit = ci[(ci["state"] == "open") & (ci["claim"].isin(FLAG_CLAIMS) | ((ci["claim"] == "gold_fails")
                                                                         & ci["status_v1_1"].str.startswith("v1.1 audit")))]
    refs = hit.groupby("instance_id")["ref"].apply(lambda s: ";".join(map(str, sorted(set(s)))))

    rows = []
    for iid, r in meta.sort_index().iterrows():
        o = out.loc[iid]
        reasons = [x for x, h in (("epoch_defect", iid in epoch.index), ("never_solved", o["solved_trials"] == 0)) if h]
        rows.append({"instance_id": iid, "repository": r["repository"], "language": r["language_corrected"],
                     "category": r["category"], "n_configs": int(o["n_configs"]), "n_trials": int(o["n_trials"]),
                     "solved_trials": int(o["solved_trials"]), "solve_rate": round(float(o["solve_rate"]), 4),
                     "solve_rate_pre_timeout": round(float(o["solve_rate_pre_timeout"]), 4),
                     "solve_rate_no_astra": round(float(o["solve_rate_no_astra"]), 4),
                     "epoch_defect_type": epoch["epoch_defect"].get(iid, ""),
                     "epoch_mechanism": epoch["mechanism_group"].get(iid, ""),
                     "community_issue": iid in refs.index, "community_refs": refs.get(iid, ""),
                     "excluded_by": ";".join(reasons), "keep": not reasons})
    df = pd.DataFrame(rows)
    df.to_csv(HERE / "tasks.csv", index=False)

    kept = df[df["keep"]]
    ex = df[~df["keep"]]["excluded_by"].str.split(";").explode().value_counts().to_dict()
    print(f"kept {len(kept)} of {len(df)}; exclusions by reason: {ex}")
    print(f"community_issue: {int(df['community_issue'].sum())} tasks, {int(kept['community_issue'].sum())} kept: "
          f"{', '.join(kept.loc[kept['community_issue'], 'instance_id'])}")
    print(f"late configs ({len(late)}): {', '.join(sorted(late))}")
    print("kept solve_rate:", kept["solve_rate"].describe().round(3).to_dict(),
          f"below 0.05: {', '.join(kept.loc[kept['solve_rate'] < 0.05, 'instance_id'])}")


if __name__ == "__main__":
    main()
