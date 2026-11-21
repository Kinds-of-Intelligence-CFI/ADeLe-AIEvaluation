"""Pre-registered analysis of goal-visible: the five released rubrics on the coding and terminal sets, with the goal
written into the input. Writes results/analysis.json and results/agreement.csv.

Three label sources, each over the 787 released tasks (only valid answers written by claude-opus-5-5 count):
  new       runs goal-visible and goal-visible-long
  control   same rubric texts, judge and bare-digit prompt on the old input: noreason-pl and noreason-long (PL),
            relabel-v4-ms and relabel-v4-ms-long (MS)
  released  label set `current`
Reported (PREREGISTRATION.md): new against control and against released, per set and rubric (exact, within one, mean
shift, level counts); Spearman of each source with each set's primary outcome, as ms-benchmarks (swebench-pl's `rho`:
two-sided p, Fisher-z 95% CI), predicted negative; and the sealed predictions.

    uv run python experiments/benchmarks/goal-visible/analysis/analyse.py
"""

import importlib.util
import json
import sys
from pathlib import Path

import pandas as pd

from adele.mass.labelset import labels as labelset_labels
from adele.mass.labelset import load_labelset

HERE = Path(__file__).resolve().parents[1]
BENCH = HERE.parent
RUNS = BENCH / "mass-annotation/runs"
MODEL = "claude-opus-5-5"
DIMS = ["PLp", "PLe", "PLs", "MSm", "MSc"]
PL, MS = DIMS[:3], DIMS[3:]
SETS = {"swe-bench-verified": ("swebench-clean", "solve_rate"), "deepswe-v1.1": ("deepswe-clean", "solve_rate"),
        "frontierswe-v2": ("frontierswe-pl", "solve_rate_0.9"), "programbench": ("programbench-pl", "solve_rate_0.9"),
        "terminal-bench-4.0.0": ("tb4-clean", "solve_rate"), "terminal-bench-science-0.1": ("tbsci-pl", "solve_rate")}


def load(name: str, path: Path):
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


rho = load("swepl_analyse", BENCH / "swebench-pl/analysis/analyse.py").rho


def run_labels(runs: list, dims: list) -> pd.DataFrame:
    lab = pd.concat([pd.read_csv(RUNS / r / "labels.csv", dtype={"instance_id": str}) for r in runs])
    lab = lab[lab["valid"].astype(bool) & (lab["writer_model"].astype(str) == MODEL)]
    lab = lab.assign(demand=lab["rubric_ref"].str.removeprefix("v2/"))
    lab = lab[lab["demand"].isin(dims) & lab["benchmark"].isin(SETS)]
    return lab.drop_duplicates(["benchmark", "instance_id", "demand"], keep="last")[
        ["benchmark", "instance_id", "demand", "level"]]


def sources() -> dict:
    rel = labelset_labels(load_labelset(RUNS.parent / "labelsets/current.toml"), benchmarks=list(SETS))
    rel = rel.assign(demand=rel["rubric"].str.removeprefix("v2/"))[["benchmark", "instance_id", "demand", "level"]]
    return {"new": run_labels(["goal-visible", "goal-visible-long"], DIMS),
            "control": pd.concat([run_labels(["noreason-pl", "noreason-long"], PL),
                                  run_labels(["relabel-v4-ms", "relabel-v4-ms-long"], MS)]),
            "released": rel}


def outcomes() -> pd.DataFrame:
    parts = []
    for bench, (study, col) in SETS.items():
        t = pd.read_csv(BENCH / study / "tasks.csv", dtype={"instance_id": str})
        t = t[t["keep"].astype(bool)] if "keep" in t else t
        parts.append(pd.DataFrame({"benchmark": bench, "instance_id": t["instance_id"], "outcome": t[col]}))
    return pd.concat(parts, ignore_index=True)


def counts(s: pd.Series) -> str:
    return " ".join(f"{int(k)}:{v}" for k, v in s.value_counts().sort_index().items())


def compare(new: pd.DataFrame, old: pd.DataFrame, name: str) -> pd.DataFrame:
    m = new.merge(old, on=["benchmark", "instance_id", "demand"], suffixes=("_new", "_old"))
    rows = []
    for (b, d), g in m.groupby(["benchmark", "demand"]):
        diff = g["level_new"] - g["level_old"]
        rows.append({"against": name, "benchmark": b, "rubric": d, "n": len(g), "exact": round((diff == 0).mean(), 3),
                     "within_1": round((diff.abs() <= 1).mean(), 3), "mean_shift": round(diff.mean(), 3),
                     "levels_old": counts(g["level_old"]), "levels_new": counts(g["level_new"])})
    for d, g in m.groupby("demand"):
        diff = g["level_new"] - g["level_old"]
        rows.append({"against": name, "benchmark": "all", "rubric": d, "n": len(g), "exact": round((diff == 0).mean(), 3),
                     "within_1": round((diff.abs() <= 1).mean(), 3), "mean_shift": round(diff.mean(), 3),
                     "levels_old": "", "levels_new": ""})
    return pd.DataFrame(rows)


def main() -> None:
    sub = pd.concat([pd.read_csv(HERE / f, dtype={"instance_id": str}) for f in ("subset.csv", "subset_long.csv")])
    src = {k: sub.merge(v) for k, v in sources().items()}
    out = {"n_cells": {k: int(len(v)) for k, v in src.items()},
           "unlabelled_new": int(len(sub) * len(DIMS) - len(src["new"])), "spearman": {}, "mean": {}}
    agree = pd.concat([compare(src["new"], src["control"], "control"), compare(src["new"], src["released"], "released")])
    oc = outcomes()
    for k, lab in src.items():
        wide = lab.pivot_table(index=["benchmark", "instance_id"], columns="demand", values="level").reset_index()
        wide = sub.merge(wide, how="left").merge(oc, how="left")
        for b, g in wide.groupby("benchmark"):
            for d in DIMS:
                h = g.dropna(subset=[d, "outcome"])
                out["mean"][f"{k}/{b}/{d}"] = round(float(g[d].mean()), 3)
                out["spearman"][f"{k}/{b}/{d}"] = ({"n": int(len(h)), "note": "one level: not testable"}
                                                   if h[d].nunique() < 2 else rho(h[d], h["outcome"], "negative"))
    sp = out["spearman"]
    new = src["new"]
    ms0 = {b: min(float((new.loc[(new["benchmark"] == b) & (new["demand"] == d), "level"] == 0).mean()) for d in MS)
           for b in SETS}
    pooled = agree.query("against == 'control' and benchmark == 'all' and rubric == 'PLp'")["exact"].iloc[0]
    gained = [f"{b}/{d}" for b in SETS for d in DIMS
              if (sp[f"new/{b}/{d}"].get("p_two_sided", 1) < 0.05 and sp[f"new/{b}/{d}"].get("rho", 0) < 0)
              and not (sp[f"control/{b}/{d}"].get("p_two_sided", 1) < 0.05 and sp[f"control/{b}/{d}"].get("rho", 0) < 0)]
    out["predictions"] = {
        "MS at Level 0 on >= 97% of tasks in every set": [all(v >= 0.97 for v in ms0.values()), ms0],
        "SWE-bench Verified PLp rho <= -0.45": [sp["new/swe-bench-verified/PLp"].get("rho", 0) <= -0.45,
                                               sp["new/swe-bench-verified/PLp"].get("rho")],
        "ProgramBench PLp rho <= -0.4": [sp["new/programbench/PLp"].get("rho", 0) <= -0.4,
                                         sp["new/programbench/PLp"].get("rho")],
        "PLp exact agreement with control below 86%": [bool(pooled < 0.86), pooled],
        "SWE-bench Verified mean PLp up >= 0.1 vs control": [
            out["mean"]["new/swe-bench-verified/PLp"] - out["mean"]["control/swe-bench-verified/PLp"] >= 0.1,
            round(out["mean"]["new/swe-bench-verified/PLp"] - out["mean"]["control/swe-bench-verified/PLp"], 3)],
        "a set x rubric gains a negative p < 0.05 signal its control lacks": [bool(gained), gained],
    }
    (HERE / "results").mkdir(exist_ok=True)
    agree.to_csv(HERE / "results/agreement.csv", index=False)
    (HERE / "results/analysis.json").write_text(json.dumps(out, indent=2, default=str) + "\n")
    print(agree.to_string(index=False))
    print(json.dumps(out["predictions"], indent=1, default=str))


if __name__ == "__main__":
    main()
