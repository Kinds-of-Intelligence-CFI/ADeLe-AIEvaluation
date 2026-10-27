"""Analysis of programbench-pl: PL labels of the 130 clean ProgramBench tasks against outcomes. Writes
results/analysis.json.

Labels: mass runs programbench-pl and programbench-pl-long (the 13 tasks read in parts; route.py), Opus 5.5 low, v2
prompt; only valid answers written by claude-opus-5-5 count. Spearman
rho (swebench-pl's `rho`: two-sided p, Fisher-z 95% CI) of PLp, PLe and PLs with each outcome of make_set.py:
  solve_rate_0.9     primary, predicted negative: share of attempted runs with score >= 0.9
  solve_rate_0.75, solve_rate_0.5, mean_score     sensitivity, predicted negative
  difficulty         ProgramBench's own label (easy 1, medium 2, hard 3; 9 clean tasks have none), predicted positive
on task sets:
  clean                     keep == True (some run reaches 0.9; primary)
  clean_unflagged           and none of docs_damaged, knowledge_gated, evaluator_issue
  clean_no_docs_damaged     and not docs_damaged
  clean_no_knowledge_gated  and not knowledge_gated

    python experiments/benchmarks/programbench-pl/analysis/analyse.py [labels.csv[,labels.csv] [out.json]]
"""

import importlib.util
import json
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parents[1]
BENCH = HERE.parent
DIMS = ["PLp", "PLe", "PLs"]
MODEL = "claude-opus-5-5"
RUNS = [BENCH / f"mass-annotation/runs/{r}/labels.csv" for r in ("programbench-pl", "programbench-pl-long")]
OUT = HERE / "results/analysis.json"
PRIMARY = "solve_rate_0.9"
OUTCOMES = {PRIMARY: "negative", "solve_rate_0.75": "negative", "solve_rate_0.5": "negative",
            "mean_score": "negative", "difficulty_ord": "positive"}
DIFFICULTY = {"easy": 1, "medium": 2, "hard": 3}

_spec = importlib.util.spec_from_file_location("swepl_analyse", BENCH / "swebench-pl/analysis/analyse.py")
_swepl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_swepl)
rho = _swepl.rho


def main(runs: list = RUNS, out_path: Path = OUT) -> None:
    tasks = pd.read_csv(HERE / "tasks.csv").set_index("instance_id")
    tasks["difficulty_ord"] = tasks["difficulty"].map(DIFFICULTY)
    lab = pd.concat([pd.read_csv(r, dtype={"instance_id": str}) for r in runs if Path(r).exists()])
    lab = lab[lab["valid"].astype(bool) & lab["writer_model"].astype(str).str.startswith(MODEL)
              & lab["rubric_ref"].isin([f"v2/{d}" for d in DIMS])]
    wide = lab.assign(demand=lab["rubric_ref"].str.removeprefix("v2/")).pivot(
        index="instance_id", columns="demand", values="level").reindex(columns=DIMS)
    df = tasks[tasks["keep"]].join(wide)
    sets = {"clean": df, "clean_unflagged": df[~df["any_flag"]],
            "clean_no_docs_damaged": df[~df["docs_damaged"]],
            "clean_no_knowledge_gated": df[~df["knowledge_gated"]]}
    out = {"primary": f"{{dim}}_vs_{PRIMARY} on clean",
           "n": {k: int(len(g)) for k, g in sets.items()},
           "unlabelled": {d: sorted(df.index[df[d].isna()]) for d in DIMS},
           "levels": {k: {d: {int(v): int(c) for v, c in g[d].value_counts().sort_index().items()} for d in DIMS}
                      for k, g in sets.items()},
           "spearman": {}}
    for k, g in sets.items():
        out["spearman"][k] = {}
        for d in DIMS:
            for y, direction in OUTCOMES.items():
                h = g.dropna(subset=[d, y])
                out["spearman"][k][f"{d}_vs_{y.removesuffix('_ord')}"] = (
                    rho(h[d], h[y], direction) if h[d].nunique() > 1 and h[y].nunique() > 1
                    else {"n": int(len(h)), "note": "constant: not testable"})
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    args = sys.argv[1:3]
    main(*([[Path(x) for x in args[0].split(",")]] if args else []), *map(Path, args[1:]))
