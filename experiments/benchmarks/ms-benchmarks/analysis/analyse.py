"""Pre-registered analysis of ms-benchmarks: MSm and MSc on the clean sets of the PL studies. Writes
results/analysis.json.

Labels: mass runs ms-benchmarks and ms-benchmarks-long (Opus 5.5 low, v2 prompt); only valid answers written by
claude-opus-5-5 count. Per set: the level distribution, the share of tasks at level 0 or 1, and Spearman (swebench-pl's
`rho`: two-sided p, Fisher-z 95% CI) with the set's primary outcome, predicted negative:
  swe-bench-verified           solve_rate (swebench-clean)
  tau2 (3 domains)             solve_rate, within domain, combined by Fisher z (tau2-tb4-pl's `combined`)
  terminal-bench-4.0.0         solve_rate (tb4-clean)
  terminal-bench-science-0.1   solve_rate (tbsci-pl)
  deepswe-v1.1                 solve_rate (deepswe-clean)
  frontierswe-v2               solve_rate_0.9 (frontierswe-pl)
  programbench                 solve_rate_0.9 (programbench-pl)
A rubric with one level in a set is reported as not testable there.

    python experiments/benchmarks/ms-benchmarks/analysis/analyse.py
"""

import importlib.util
import json
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parents[1]
BENCH = HERE.parent
DIMS = ["MSm", "MSc"]
MODEL = "claude-opus-5-5"
RUNS = [BENCH / f"mass-annotation/runs/{r}/labels.csv" for r in ("ms-benchmarks", "ms-benchmarks-long")]
SETS = {"swe-bench-verified": ("swebench-clean", "solve_rate"), "terminal-bench-4.0.0": ("tb4-clean", "solve_rate"),
        "terminal-bench-science-0.1": ("tbsci-pl", "solve_rate"), "deepswe-v1.1": ("deepswe-clean", "solve_rate"),
        "frontierswe-v2": ("frontierswe-pl", "solve_rate_0.9"), "programbench": ("programbench-pl", "solve_rate_0.9")}
TAU2 = ["tau2-airline", "tau2-retail", "tau2-banking_knowledge"]


def load(name: str, path: Path):
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


rho = load("swepl_analyse", BENCH / "swebench-pl/analysis/analyse.py").rho
combined = load("t2_analyse", BENCH / "tau2-tb4-pl/analysis/analyse.py").combined


def labels() -> pd.DataFrame:
    lab = pd.concat([pd.read_csv(r, dtype={"instance_id": str}) for r in RUNS if r.exists()])
    lab = lab[lab["valid"].astype(bool) & lab["writer_model"].astype(str).str.startswith(MODEL)]
    return lab.assign(demand=lab["rubric_ref"].str.removeprefix("v2/")).pivot_table(
        index=["benchmark", "instance_id"], columns="demand", values="level").reindex(columns=DIMS).reset_index()


def outcomes() -> pd.DataFrame:
    parts = []
    for bench, (study, col) in SETS.items():
        t = pd.read_csv(BENCH / study / "tasks.csv", dtype={"instance_id": str})
        t = t[t["keep"].astype(bool)] if "keep" in t else t
        parts.append(pd.DataFrame({"benchmark": bench, "instance_id": t["instance_id"], "outcome": t[col]}))
    t = pd.read_csv(BENCH / "tau2-clean/tasks.csv", dtype={"instance_id": str})
    t = t[t["keep"].astype(bool)]
    parts.append(pd.DataFrame({"benchmark": t["benchmark"], "instance_id": t["instance_id"], "outcome": t["solve_rate"]}))
    return pd.concat(parts, ignore_index=True)


def main() -> None:
    sub = pd.concat([pd.read_csv(HERE / f, dtype={"instance_id": str}) for f in ("subset.csv", "subset_long.csv")])
    df = sub[["benchmark", "instance_id"]].merge(labels(), how="left").merge(outcomes(), how="left")
    out = {"n": {}, "unlabelled": {}, "levels": {}, "share_0_or_1": {}, "spearman": {}}
    groups = {b: g for b, g in df.groupby("benchmark") if b not in TAU2} | {"tau2": df[df["benchmark"].isin(TAU2)]}
    for name, g in groups.items():
        out["n"][name] = int(len(g))
        out["unlabelled"][name] = {d: int(g[d].isna().sum()) for d in DIMS}
        out["levels"][name] = {d: {str(int(k)): int(v) for k, v in g[d].value_counts().sort_index().items()} for d in DIMS}
        out["share_0_or_1"][name] = {d: round(float((g[d].dropna() <= 1).mean()), 3) for d in DIMS}
        direction = "negative"
        for d in DIMS:
            h = g.dropna(subset=[d, "outcome"])
            if name == "tau2":
                res = combined(h, d, "outcome", direction)
            elif h[d].nunique() < 2:
                res = {"n": int(len(h)), "note": "one level: not testable"}
            else:
                res = rho(h[d], h["outcome"], direction)
            out["spearman"][f"{name}/{d}"] = res
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results/analysis.json").write_text(json.dumps(out, indent=2, default=str) + "\n")
    print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
