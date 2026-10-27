"""The pair sample and outcome table of cooperbench-plms.

Outcomes: ../cooperbench-data/outcomes.csv (HF CooperBench/trajectories, MIT; team-trajectories, Apache-2.0). Solo and
coop come from the same evaluation pipeline there, so the drop compares like with like. Three models:
  gpt5    GPT-5, OpenHands 0.54 (paper runs): solo, coop
  claude  Claude Sonnet 4.5, OpenHands 0.54 (paper runs): solo, coop
  gpt55   GPT-5.5, codex agent (May 2026): solo, coop with git
Left out: Qwen3-30B (solo 6%, coop 5%: floor), MiniMax M2 and Qwen3-Coder (solo results do not match the leaderboard;
probably an older evaluation), Gemini (no public per-pair solo results).

Frame: pairs with a solo and a coop result for all three models. Sample (seed 0), as ../cooperbench-data/NOTES.md
proposes: stratify by task pool; take min(pool size, 2) pairs from each pool, then fill to N by largest remainder in
proportion to the pairs left in each pool; draw uniformly within a pool (pools sorted, pairs sorted by pair_id).

Writes tasks.csv (every frame pair: pool, gold_conflict, flags, per-model solo/coop success, solo_rate, coop_rate,
drop = mean of solo - coop over the three models, any_flag = a feature's spec or tests changed after the
runs, sampled) and subset.csv (the sampled pairs x solo, coop, as
`adele mass` instance ids).

    python experiments/benchmarks/cooperbench-plms/make_set.py
"""

from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
N, SEED = 120, 0
CELLS = {("solo", "gpt5"): "gpt5_solo", ("coop", "gpt5"): "gpt5_coop", ("solo", "claude"): "claude_solo",
         ("coop", "claude"): "claude_coop", ("solo", "gpt55_codex_solo"): "gpt55_solo",
         ("coop_git", "gpt55_codex_coop_git"): "gpt55_coop"}
MODELS = ["gpt5", "claude", "gpt55"]


def sample(frame: pd.DataFrame) -> list[str]:
    rng = np.random.default_rng(SEED)
    pools = {p: g.sort_values("pair_id") for p, g in sorted(frame.groupby("pool"))}
    take = {p: min(len(g), 2) for p, g in pools.items()}
    left = {p: len(g) - take[p] for p, g in pools.items()}
    extra, total = N - sum(take.values()), sum(left.values())
    quota = {p: extra * left[p] / total for p in pools}
    add = {p: int(np.floor(q)) for p, q in quota.items()}
    for p in sorted(pools, key=lambda p: (-(quota[p] - add[p]), p))[:extra - sum(add.values())]:
        add[p] += 1
    out = []
    for p, g in pools.items():
        out += g.sample(n=take[p] + add[p], random_state=int(rng.integers(2**31)))["pair_id"].tolist()
    return sorted(out)


def main() -> None:
    o = pd.read_csv(HERE.parent / "cooperbench-data/outcomes.csv")
    o["success"] = o["success"].astype(str).str.lower().map({"true": 1, "false": 0})
    o["cell"] = [CELLS.get((c, f)) for c, f in zip(o["condition"], o["config"])]
    w = o.dropna(subset=["cell", "success"]).pivot_table(index="pair_id", columns="cell", values="success")
    w = w.reindex(columns=list(CELLS.values())).dropna()
    meta = pd.read_csv(ROOT / "data/instances/meta_cooperbench.csv")
    meta = meta[meta["condition"] == "coop"].set_index("pair_id")
    meta["pool"] = meta["repo"] + "/" + meta["task_id"].astype(str)
    df = meta[["pool", "repo", "language", "gold_conflict", "gold_shared_files", "spec_changed_after_runs",
               "tests_changed_after_runs", "task_infra_changed_after_runs"]].join(w, how="inner")
    df["solo_rate"] = df[[f"{m}_solo" for m in MODELS]].mean(axis=1)
    df["coop_rate"] = df[[f"{m}_coop" for m in MODELS]].mean(axis=1)
    df["drop"] = df["solo_rate"] - df["coop_rate"]
    # A feature's spec or tests changed after the runs (the columns list the changed features); infra-only changes
    # (Dockerfiles, run scripts) are kept unflagged.
    df["any_flag"] = df["spec_changed_after_runs"].notna() | df["tests_changed_after_runs"].notna()
    df = df.rename_axis("pair_id").reset_index()
    picked = sample(df)
    df["sampled"] = df["pair_id"].isin(picked)
    df.to_csv(HERE / "tasks.csv", index=False)
    sub = pd.DataFrame({"instance_id": [f"{p}@{c}" for p in picked for c in ("solo", "coop")], "keep": True})
    sub.to_csv(HERE / "subset.csv", index=False)
    s = df[df["sampled"]]
    print(f"frame {len(df)} pairs, {df['pool'].nunique()} pools; sampled {len(s)} "
          f"({s['pool'].value_counts().min()}-{s['pool'].value_counts().max()} per pool), gold conflict "
          f"{s['gold_conflict'].mean():.0%}, flagged {s['any_flag'].mean():.0%}")
    print("drop:", s["drop"].round(2).value_counts().sort_index().to_dict(), "| solo", round(s["solo_rate"].mean(), 3),
          "coop", round(s["coop_rate"].mean(), 3))


if __name__ == "__main__":
    main()
