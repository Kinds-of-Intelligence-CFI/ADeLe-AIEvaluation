"""Build the FrontierSWE v2 task table for frontierswe-pl: all 34 tasks, with outcomes, flags and the clean set.

Outcomes: panel/sources/frontierswe-v2/task_model.csv (34 tasks x 18 models; per cell the mean and best reward over the
model's runs, usually 5). Per-run rewards are not public (frontierswe.com/robots.txt disallows /traces), so every
outcome is built from these cells. Pablo's rules (2026-10-01):
  solved cell        the model's mean reward over its runs is >= 0.9
  solve_rate_<t>     share of the 18 models with mean reward >= t, for t in 0.9 (primary), 0.75 and 0.5
  best_solve_rate_0.9  share of the 18 models whose best run reaches 0.9
  mean_reward        run-weighted mean reward of the task over all models
  best_any           best run reward of any model

Clean set: drop never-solved tasks, i.e. no model's best run reaches 0.9 (excluded_by never_solved). No external defect
list exists, so nothing else is dropped. `dropped_at_0.5` marks tasks no best run brings to 0.5;
`dropped_at_0.9_only` marks those the 0.9 rule drops but a 0.5 rule would keep. Flags (not exclusions):
  github_issue    an open issue on Proximal-Labs/frontier-swe-v2 names the task (frontierswe-data/NOTES.md, 2026-10-01)
  version_suffix  the task.toml name carries a -patched/-hardened/-qemu/-impl suffix that the site slug lacks

    python experiments/benchmarks/frontierswe-pl/make_set.py
"""

import re
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BENCH = "frontierswe-v2"
TAU, SENS = 0.9, (0.75, 0.5)
# Open issues and PRs as listed in frontierswe-data/NOTES.md (13 is PR #13, attached to issue #6).
OPEN_ISSUES = {"msms-denovo-generation": "14", "flight-sim-renderer-in-opengl": "7;12",
               "reconnaissance-blind-chess-recovery": "10;11", "fitness-recap-video-in-remotion": "6;13"}
SUFFIX = re.compile(r"-(patched|hardened|qemu|impl)$")


def main() -> None:
    meta = pd.read_csv(ROOT / f"data/instances/meta_{BENCH}.csv").set_index("instance_id")
    cells = pd.read_csv(HERE.parent / f"panel/sources/{BENCH}/task_model.csv")
    assert len(meta) == 34 and set(cells["instance_id"]) == set(meta.index) and len(cells) == 34 * 18
    assert set(OPEN_ISSUES) <= set(meta.index)
    g = cells.assign(w=cells["mean_reward"] * cells["n_runs"]).groupby("instance_id")
    out = pd.DataFrame({"n_models": g["model_key"].nunique(), "n_runs": g["n_runs"].sum()})
    for t in (TAU, *SENS):
        out[f"solve_rate_{t}"] = g["mean_reward"].apply(lambda s, t=t: (s >= t).mean()).round(4)
    out[f"best_solve_rate_{TAU}"] = g["best_reward"].apply(lambda s: (s >= TAU).mean()).round(4)
    out["mean_reward"] = (g["w"].sum() / out["n_runs"]).round(4)
    out["best_any"] = g["best_reward"].max().round(4)
    slug = g["site_slug"].first()

    out = meta[["name", "categories", "difficulty", "toml_category"]].join(out)
    out["github_issues"] = pd.Series(OPEN_ISSUES).reindex(out.index).fillna("")
    out["github_issue"] = out["github_issues"] != ""
    toml = meta["toml_name"].str.removeprefix("proximal-evals/")
    suffix = toml.str.extract(SUFFIX, expand=False)
    out["version_suffix"] = [isinstance(x, str) and not s.endswith(f"-{x}")
                             for s, x in zip(slug.reindex(out.index), suffix)]
    out["dropped_at_0.5"] = out["best_any"] < 0.5
    out["dropped_at_0.9_only"] = (out["best_any"] < TAU) & ~out["dropped_at_0.5"]
    out["excluded_by"] = (out["best_any"] < TAU).map({True: "never_solved", False: ""})
    out["keep"] = out["excluded_by"] == ""
    out = out.rename_axis("instance_id").sort_index().reset_index()
    out.to_csv(HERE / "tasks.csv", index=False)

    k = out[out["keep"]]
    print(f"{len(out)} tasks; kept {len(k)}; never_solved at {TAU}: {int((~out['keep']).sum())} "
          f"(of which {int(out['dropped_at_0.5'].sum())} also at 0.5: "
          f"{', '.join(out.loc[out['dropped_at_0.5'], 'instance_id'])})")
    for f in ("github_issue", "version_suffix"):
        print(f"{f}: {int(out[f].sum())} ({int(k[f].sum())} kept): {', '.join(out.loc[out[f], 'instance_id'])}")
    print(k[[f"solve_rate_{TAU}", *(f"solve_rate_{t}" for t in SENS), f"best_solve_rate_{TAU}", "mean_reward"]]
          .describe().round(3).to_string())


if __name__ == "__main__":
    main()
