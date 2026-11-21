"""Build the Terminal-Bench 4.0.0 clean set (README.md): the rule Pablo set for SWE-bench Verified, applied here.

Keep every Terminal-Bench 4.0.0 task except:
  epoch_defect   listed by Epoch AI's review of Terminal-Bench 4.0.0 (2026-09-04) as a false positive (accepts
                 wrong solutions) or a false negative (rejects correct ones); recorded in the task metadata
  never_solved   no trial of any configuration in the panel's Terminal-Bench results solves it

Solve rates come from the committed results panel (panel/tasks.csv: Harbor Hub leaderboard, 27 current-generation
configurations, 5 trials per task). Writes tasks.csv: every one of the 66 tasks with its solve counts, expert-hour
estimate, exclusion reasons and `keep`.

    python experiments/benchmarks/tb4-clean/make_set.py
"""

from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def main() -> None:
    panel = pd.read_csv(HERE.parent / "panel/tasks.csv")
    panel = panel[panel["benchmark"] == "terminal-bench-4.0.0"].set_index("instance_id")
    meta = pd.read_csv(ROOT / "data/instances/meta_terminal-bench-4.0.0.csv").set_index("instance_id")
    assert len(panel) == 66 and set(panel.index) == set(meta.index)
    df = panel[["n_configs", "n_trials", "solved_trials", "solve_rate"]].join(
        meta[["category", "expert_time_estimate_hours", "epoch_defect"]])
    # The panel's own broken flag must agree with the metadata.
    assert (panel["known_broken"].fillna("").ne("") == df["epoch_defect"].notna()).all()
    rows = []
    for iid, r in df.sort_index().iterrows():
        reasons = [x for x, hit in (("epoch_defect", pd.notna(r["epoch_defect"])),
                                    ("never_solved", r["solved_trials"] == 0)) if hit]
        rows.append({"instance_id": iid, "category": r["category"], "expert_hours": r["expert_time_estimate_hours"],
                     "n_configs": int(r["n_configs"]), "n_trials": int(r["n_trials"]),
                     "solved_trials": int(r["solved_trials"]), "solve_rate": round(float(r["solve_rate"]), 4),
                     "epoch_defect_type": r["epoch_defect"] if pd.notna(r["epoch_defect"]) else "",
                     "excluded_by": ";".join(reasons), "keep": not reasons})
    out = pd.DataFrame(rows)
    out.to_csv(HERE / "tasks.csv", index=False)
    ex = out[~out["keep"]]["excluded_by"].str.split(";").explode().value_counts().to_dict()
    print(f"kept {int(out['keep'].sum())} of 66; exclusions by reason: {ex}")


if __name__ == "__main__":
    main()
