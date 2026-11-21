"""Build the task lists of the bulk annotation (ids only, no task text). Rerun to regenerate; output is deterministic.

    python experiments/benchmarks/mass-annotation/subsets/make_subsets.py

wave1.csv   every task that already has the released PL and MS labels (the label set "current"), plus rivercross-search:
            the bulk adds the v1 rubrics to exactly these tasks, so every rubric covers the same tasks.
dryrun.csv  the first task (by id) of each wave-1 benchmark.
"""

from pathlib import Path

import pandas as pd

from adele.mass.labelset import labels, load_labelset

HERE = Path(__file__).resolve().parent
INSTANCES = HERE.parents[3] / "data" / "instances"
EXTRA = ["rivercross-search"]  # in the plan's scope (decision 1, 2026-10-01), no PL/MS labels yet


def main() -> None:
    lab = labels(load_labelset("current"))
    tasks = lab[["benchmark", "instance_id"]].drop_duplicates()
    for b in EXTRA:
        f = INSTANCES / f"instances_{b}.parquet"
        ids = pd.read_parquet(f, columns=["instance_id"])["instance_id"].astype(str)
        tasks = pd.concat([tasks, pd.DataFrame({"benchmark": b, "instance_id": ids})])
    tasks = tasks.sort_values(["benchmark", "instance_id"]).reset_index(drop=True)
    tasks.to_csv(HERE / "wave1.csv", index=False)
    tasks.groupby("benchmark").head(1).to_csv(HERE / "dryrun.csv", index=False)
    print(tasks["benchmark"].value_counts().sort_index().to_string(), f"\ntotal {len(tasks)}")


if __name__ == "__main__":
    main()
