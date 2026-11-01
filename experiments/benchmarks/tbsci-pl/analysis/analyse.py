"""Analysis of tbsci-pl: PL labels of the 70 Terminal-Bench Science 0.1 tasks against outcomes. Writes
results/analysis.json.

Labels: mass run tbsci-pl (Opus 5.5 low, v2 prompt); only valid answers written by claude-opus-5-5 count. Spearman rho
(swebench-pl's `rho`: two-sided p, Fisher-z 95% CI) of PLp, PLe and PLs with solve_rate (predicted negative) and
expert_hours (predicted positive), on three task sets:
  all                        the 70 tasks
  solved_any                 tasks some trial solves
  solved_any_no_open_issue   and with no open score-relevant [TASK FIX] issue (make_set.py)

    python experiments/benchmarks/tbsci-pl/analysis/analyse.py
"""

import importlib.util
import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parents[1]
BENCH = HERE.parent
DIMS = ["PLp", "PLe", "PLs"]
MODEL = "claude-opus-5-5"
RUN = BENCH / "mass-annotation/runs/tbsci-pl/labels.csv"
OUTCOMES = {"solve_rate": "negative", "expert_hours": "positive"}

_spec = importlib.util.spec_from_file_location("swepl_analyse", BENCH / "swebench-pl/analysis/analyse.py")
_swepl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_swepl)
rho = _swepl.rho


def main() -> None:
    tasks = pd.read_csv(HERE / "tasks.csv").set_index("instance_id")
    lab = pd.read_csv(RUN, dtype={"instance_id": str})
    lab = lab[lab["valid"].astype(bool) & lab["writer_model"].astype(str).str.startswith(MODEL)
              & lab["rubric_ref"].isin([f"v2/{d}" for d in DIMS])]
    wide = lab.assign(demand=lab["rubric_ref"].str.removeprefix("v2/")).pivot(
        index="instance_id", columns="demand", values="level").reindex(columns=DIMS)
    df = tasks.join(wide)
    sets = {"all": df, "solved_any": df[df["solved_any"]],
            "solved_any_no_open_issue": df[df["solved_any"] & ~df["open_issue"]]}
    out = {"n": {k: int(len(g)) for k, g in sets.items()},
           "unlabelled": {d: sorted(df.index[df[d].isna()]) for d in DIMS},
           "levels": {k: {d: {int(v): int(c) for v, c in g[d].value_counts().sort_index().items()} for d in DIMS}
                      for k, g in sets.items()},
           "spearman": {}}
    for k, g in sets.items():
        out["spearman"][k] = {}
        for d in DIMS:
            for y, direction in OUTCOMES.items():
                h = g.dropna(subset=[d, y])
                out["spearman"][k][f"{d}_vs_{y}"] = (
                    rho(h[d], h[y], direction) if h[d].nunique() > 1 and h[y].nunique() > 1
                    else {"n": int(len(h)), "note": "constant: not testable"})
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results/analysis.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
