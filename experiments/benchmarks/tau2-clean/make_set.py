"""Build the tau2 clean set: Pablo's rule of 2026-10-01, applied to tau2.

Domains: airline, retail, banking_knowledge. Telecom is left out: 2,280 of its 2,285 instances share one text, so all
its panel tasks are text-collapsed. Keep every task with results on the frozen text (panel rule 1) except:
  never_solved   no scored trial of any configuration solves it

Banking grading changed in tau2 v1.0.1 (2026-07-15). For tau2-banking_knowledge only the runs made after it count
(panel `date` >= 2026-07), for the keep rule and for the solve rates. The rates over every banking run (the mixed
grading tau2-tb4-pl used) are kept in the *_mixed columns, for comparison only.

Solve rates use tau2-tb4-pl's own `outcomes()`: `solve_rate` over the configurations that ran every kept task of the
domain with scored trials ("common configurations"), `solve_rate_all` over every configuration. The kept airline and
retail rates must equal tau2-tb4-pl's sample.csv.

Writes tasks.csv (all 257 non-telecom tau2 tasks with frozen-text results) and new_tasks.csv (kept tasks without PL
labels in tau2-tb4-pl's sample; the subset of specs/tau2-clean-new-pl.toml).

    python experiments/benchmarks/panel/build.py            # data/results/panel.parquet
    python experiments/benchmarks/tau2-clean/make_set.py
"""

import importlib.util
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BENCH = HERE.parent
DOMAINS = ["airline", "retail", "banking_knowledge"]
BANKING = "tau2-banking_knowledge"
GRADING_CHANGE = "2026-07"  # tau2 v1.0.1, 2026-07-15: banking_knowledge grading changed


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> None:
    t2 = load("t2_make_prompts", BENCH / "tau2-tb4-pl/make_prompts.py")
    tasks = pd.read_csv(BENCH / "panel/tasks.csv", dtype={"instance_id": str})
    panel = pd.read_parquet(ROOT / "data/results/panel.parquet")
    sample = pd.read_csv(BENCH / "tau2-tb4-pl/sample.csv", dtype={"instance_id": str})
    frames = []
    for bench in [f"tau2-{d}" for d in DOMAINS]:
        t = tasks[tasks["benchmark"] == bench].set_index("instance_id")
        assert not t["text_collapsed"].any()
        ids = sorted(t.index)
        p = panel[panel["benchmark"] == bench]
        if bench == BANKING:
            p = p[p["date"] >= GRADING_CHANGE]
        # Keep rule: some scored trial on the frozen text solves the task (over the runs that count).
        use = p[p["text_matches_frozen"] & (p["n_trials"] > 0)]
        g = use.assign(solved=use["success"] * use["n_trials"]).groupby("instance_id")
        counts = pd.DataFrame({"solved_trials_all": g["solved"].sum(), "n_trials_all": g["n_trials"].sum()})
        assert set(counts.index) == set(ids), f"{bench}: tasks without results in the runs that count"
        counts = counts.loc[ids]
        keep = sorted(counts.index[counts["solved_trials_all"] > 0])
        s = t2.outcomes(p, bench, ids, keep).loc[ids]
        s = s.join(counts.astype(int))
        if bench == BANKING:
            s = s.join(t2.outcomes(panel[panel["benchmark"] == bench], bench, ids, keep).loc[ids].add_suffix("_mixed"))
            s["runs_counted"] = f"date >= {GRADING_CHANGE} (post v1.0.1 grading)"
        else:
            s["runs_counted"] = "all"
        s.insert(0, "benchmark", bench)
        s.insert(1, "file_id", f"{bench.removeprefix('tau2-')}-" + s.index)
        s["excluded_by"] = ["" if i in keep else "never_solved" for i in ids]
        s["keep"] = s.index.isin(keep)
        frames.append(s.rename_axis("instance_id").reset_index())
    out = pd.concat(frames, ignore_index=True)
    cols = ["benchmark", "instance_id", "file_id", "runs_counted", "solved_trials_all", "n_trials_all",
            "solve_rate", "n_configs", "solve_rate_all", "n_configs_all",
            "solve_rate_mixed", "n_configs_mixed", "solve_rate_all_mixed", "n_configs_all_mixed", "excluded_by", "keep"]
    out = out[cols].astype({"n_configs_mixed": "Int64", "n_configs_all_mixed": "Int64"})
    assert len(out) == 257

    # Same rates as tau2-tb4-pl for kept airline and retail tasks (no grading change there).
    kept = out[out["keep"]].set_index(["benchmark", "instance_id"])
    ref = sample.set_index(["benchmark", "instance_id"])
    nb = kept[kept.index.get_level_values(0) != BANKING]
    assert nb.index.isin(ref.index).all()
    for c in ("solve_rate", "n_configs", "solve_rate_all", "n_configs_all"):
        assert (nb[c] - ref.loc[nb.index, c]).abs().max() < 1e-3, f"{c} differs from tau2-tb4-pl sample.csv"
    # Banking over every run reproduces tau2-tb4-pl's (mixed-grading) rates on its 69 banking tasks.
    b = ref.loc[[i for i in ref.index if i[0] == BANKING]]
    for c in ("solve_rate", "solve_rate_all"):
        assert (kept.loc[b.index, f"{c}_mixed"] - b[c]).abs().max() < 1e-3, f"banking {c}_mixed differs"

    labelled = set(ref.index[ref.index.get_level_values(0).str.startswith("tau2-")])
    new = kept[~kept.index.isin(labelled)].reset_index()
    assert labelled <= set(kept.index), "a task labelled in tau2-tb4-pl is not in the clean set"
    out.to_csv(HERE / "tasks.csv", index=False)
    # The runner's subset joins on (benchmark, instance_id): tau2 ids repeat across domains ('0' is airline and retail).
    new[["benchmark", "instance_id", "file_id"]].to_csv(HERE / "new_tasks.csv", index=False)

    print(out.groupby("benchmark").agg(tasks=("instance_id", "size"), kept=("keep", "sum"),
                                       configs=("n_configs", "min"), configs_all=("n_configs_all", "max")))
    print(f"kept {int(out['keep'].sum())} of {len(out)}; already labelled {len(labelled)}; new {len(new)}: "
          f"{new.groupby('benchmark').size().to_dict()}")


if __name__ == "__main__":
    main()
