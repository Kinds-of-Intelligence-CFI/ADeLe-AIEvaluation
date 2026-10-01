"""Analysis of deepswe-clean: PL labels of the 90 clean DeepSWE v1.1 tasks against solve rate. Writes
results/analysis.json.

Labels: mass run deepswe-clean (Opus 5.5 low, v2 prompt); only valid answers written by claude-opus-5-5 count. Spearman
rho (swebench-pl's `rho`: two-sided p, Fisher-z 95% CI) of PLp, PLe and PLs with each outcome, all predicted negative:
  solve_rate              share of scored trials resolved, all 70 configurations (primary)
  solve_rate_pre_timeout  without the 8 configurations run after the agent timeout rose to 10,800 s (sensitivity)
  solve_rate_no_astra     without GPT-6 Astra's OpenAI-run configurations (sensitivity)
on three task sets (make_set.py):
  clean                     the 90 kept tasks (primary)
  clean_no_community_issue  without the tasks an open community issue flags
  all                       the 113 tasks; skipped while the excluded tasks have no labels
DeepSWE publishes no human difficulty or time estimate, so there is no positive-direction test.

    python experiments/benchmarks/deepswe-clean/analysis/analyse.py
"""

import importlib.util
import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parents[1]
BENCH = HERE.parent
DIMS = ["PLp", "PLe", "PLs"]
MODEL = "claude-opus-5-5"
RUN = BENCH / "mass-annotation/runs/deepswe-clean/labels.csv"
OUT = HERE / "results/analysis.json"
OUTCOMES = {"solve_rate": "negative", "solve_rate_pre_timeout": "negative", "solve_rate_no_astra": "negative"}

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
    clean = df[df["keep"]]
    sets = {"clean": clean, "clean_no_community_issue": clean[~clean["community_issue"]], "all": df}
    out = {"n": {k: int(len(g)) for k, g in sets.items()},
           "unlabelled_clean": {d: sorted(clean.index[clean[d].isna()]) for d in DIMS},
           "levels": {k: {d: {int(v): int(c) for v, c in g[d].value_counts().sort_index().items()} for d in DIMS}
                      for k, g in sets.items()},
           "human_estimate": "none: DeepSWE publishes no difficulty or time estimate",
           "spearman": {}}
    for k, g in sets.items():
        if k == "all" and df.loc[~df["keep"], DIMS].isna().all(axis=None):
            out["spearman"][k] = {"note": "skipped: the excluded tasks have no labels"}
            continue
        out["spearman"][k] = {}
        for d in DIMS:
            for y, direction in OUTCOMES.items():
                h = g.dropna(subset=[d, y])
                out["spearman"][k][f"{d}_vs_{y}"] = (
                    rho(h[d], h[y], direction) if h[d].nunique() > 1 and h[y].nunique() > 1
                    else {"n": int(len(h)), "note": "constant: not testable"})
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
