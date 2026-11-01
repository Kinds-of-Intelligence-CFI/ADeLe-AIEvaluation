"""Pre-registered analysis of jev-v1. Writes results/analysis.json.

Per v1 rubric: quadratic weighted kappa, exact and within-one agreement and mean difference between Jev's most
probable level and the paper's GPT-4o label (1,000 items); Spearman of Jev's expected level with the GPT-4o label; the
share of labels at 0 or 5 for each judge. Group means for the read-off (R) and solve-to-judge (S) rubrics fixed in
PREREGISTRATION.md. If labels/opus_labels.csv exists (the 60-item core), the same against Opus.

    python experiments/benchmarks/jev-v1/analysis/analyse.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parents[1]
R = ["KNa", "KNc", "KNf", "KNn", "KNs", "CEc", "CEe", "AT", "VO", "MS", "AS", "MCu"]
S = ["QLq", "QLl", "MCt", "MCr", "SNs", "CL"]


def qwk(a: pd.Series, b: pd.Series, k: int = 6) -> float:
    o = np.zeros((k, k))
    for x, y in zip(a.astype(int), b.astype(int)):
        o[x, y] += 1
    w = np.array([[(i - j) ** 2 for j in range(k)] for i in range(k)]) / (k - 1) ** 2
    e = np.outer(o.sum(1), o.sum(0)) / o.sum()
    return round(float(1 - (w * o).sum() / (w * e).sum()), 3)


def compare(m: pd.DataFrame, ref: str) -> pd.DataFrame:
    rows = []
    for d, g in m.groupby("rubric"):
        rows.append({"rubric": d, "group": "R" if d in R else "S", "n": len(g), "qwk": qwk(g["level"], g[ref]),
                     "spearman_expected": round(float(g["expected"].corr(g[ref], method="spearman")), 3),
                     "exact": round(float((g["level"] == g[ref]).mean()), 3),
                     "within_one": round(float(((g["level"] - g[ref]).abs() <= 1).mean()), 3),
                     "mean_diff": round(float((g["level"] - g[ref]).mean()), 3),
                     "jev_at_0_or_5": round(float(g["level"].isin([0, 5]).mean()), 3),
                     "ref_at_0_or_5": round(float(g[ref].isin([0, 5]).mean()), 3)})
    return pd.DataFrame(rows).sort_values(["group", "qwk"])


def main() -> None:
    jev = pd.read_csv(HERE / "labels/jev_labels.csv")
    jev = jev[jev["status"] == "ok"]
    s = pd.read_csv(HERE / "sample.csv")
    g4 = s.melt(id_vars=["benchmark", "instance_id", "core"], var_name="rubric", value_name="gpt4o")
    out = {}
    t = compare(jev.merge(g4, on=["benchmark", "instance_id", "core", "rubric"]), "gpt4o")
    out["jev_vs_gpt4o"] = t.to_dict("records")
    out["jev_vs_gpt4o_group_means"] = t.groupby("group")[["qwk", "exact", "within_one", "jev_at_0_or_5"]].mean().round(3).to_dict()
    op = HERE / "labels/opus_labels.csv"
    if op.exists():
        opus = pd.read_csv(op)
        m = jev.merge(opus, on=["instance_id", "rubric"]).merge(g4[["instance_id", "rubric", "gpt4o"]], on=["instance_id", "rubric"])
        out["jev_vs_opus"] = compare(m, "opus").to_dict("records")
        out["gpt4o_vs_opus"] = {d: qwk(g["gpt4o"], g["opus"]) for d, g in m.groupby("rubric")}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results/analysis.json").write_text(json.dumps(out, indent=2) + "\n")
    print(t.to_string(index=False))
    print(json.dumps(out["jev_vs_gpt4o_group_means"], indent=1))


if __name__ == "__main__":
    main()
