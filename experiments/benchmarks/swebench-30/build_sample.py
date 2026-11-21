"""Draw the SWE-bench Verified sample for the swebench-30 run.

Pool: the 500 official instances minus the 14 already labelled in the
3-benchmark pilot, which are re-judged separately as test-retest anchors.
Strata: terciles of the leaderboard solve rate (mean resolved over the 135
entries of SWE-bench/experiments), 10 tasks each, seeded. Tasks solved by
fewer than 5% of entries are flagged `suspect`: OpenAI's 2026 audit found most
rarely-solved tasks have tests that reject correct fixes. They are kept and
analysed with and without.

Inputs (gitignored, see PREREGISTRATION.md for their provenance):
    data/instances/instances_swe-bench-verified.parquet   adele instances prepare -b swebench
    data/results/swebench.parquet                          adele results fetch-swebench --instance-ids ...
Output: sample.csv next to this script, ids and metadata only (no task text).

    python experiments/benchmarks/swebench-30/build_sample.py
"""

from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SEED = 20260926
PER_STRATUM = 10
SUSPECT_BELOW = 0.05
HF_REVISION = "c104f840cc67f8b6eec6f759ebc8b2693d585d4a"


def main() -> None:
    from datasets import load_dataset

    inst = pd.read_parquet(ROOT / "data/instances/instances_swe-bench-verified.parquet")
    flags = pd.read_parquet(ROOT / "data/results/swebench.parquet")
    solve = flags.groupby("instance_id")["success"].mean().rename("solve_rate")
    meta = load_dataset("princeton-nlp/SWE-bench_Verified", split="test",
                        revision=HF_REVISION).to_pandas()[["instance_id", "repo", "difficulty"]]
    pilot = pd.read_csv(HERE.parent / "pilot-3bench" / "medians.csv")
    anchors = set(pilot.loc[pilot["benchmark"] == "swe-bench-verified", "custom_id"]
                  .str.removeprefix("swe-"))

    df = (inst[["instance_id", "prompt", "prompt_sha12"]]
          .merge(meta, on="instance_id", how="left")
          .merge(solve, on="instance_id", how="left"))
    assert len(df) == 500 and df["solve_rate"].notna().all() and df["repo"].notna().all()
    assert anchors <= set(df["instance_id"]) and len(anchors) == 14
    df["prompt_chars"] = df["prompt"].str.len()
    df["suspect"] = df["solve_rate"] < SUSPECT_BELOW

    pool = df[~df["instance_id"].isin(anchors)].copy()
    pool["stratum"] = pd.qcut(pool["solve_rate"].rank(method="first"), 3,
                              labels=["low", "mid", "high"]).astype(str)
    new = pd.concat([pool[pool["stratum"] == s].sample(PER_STRATUM, random_state=SEED)
                     for s in ("low", "mid", "high")])
    new["role"] = "new"
    anc = df[df["instance_id"].isin(anchors)].assign(role="anchor", stratum="")

    cols = ["instance_id", "role", "stratum", "repo", "difficulty",
            "solve_rate", "suspect", "prompt_chars", "prompt_sha12"]
    out = pd.concat([new, anc])[cols].round({"solve_rate": 4})
    out.to_csv(HERE / "sample.csv", index=False)

    bounds = pool.groupby("stratum")["solve_rate"].agg(["min", "max", "size"])
    print(bounds.loc[["low", "mid", "high"]].round(3).to_string())
    print(out.groupby("role")[["suspect"]].sum().to_string())
    print(f"wrote {len(out)} rows → {HERE / 'sample.csv'}")


if __name__ == "__main__":
    main()
