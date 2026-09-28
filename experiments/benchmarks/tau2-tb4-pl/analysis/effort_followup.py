"""Follow-up (exploratory; PREREGISTRATION.md, section Follow-up): Opus at max effort against Opus at
low effort on PLp for the 34 Terminal-Bench analysis-set tasks.

Reports agreement, mean shift, level counts and the low-by-max crosstab. Computes PLp against solve
rate and against expert time on both label sets, as Q1 and Q2 but exploratory. Compares both judges
with Pablo's blind labels and Claude's reading (human-labels/unblinded.csv), and checks the two
predictions. Only labels written by the registered judge are used (amendment 2).
Writes results/effort_followup.json.

    python experiments/benchmarks/tau2-tb4-pl/analysis/effort_followup.py
"""

import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parents[1]
TB4 = "terminal-bench-4.0.0"
_spec = importlib.util.spec_from_file_location("tb_analyse", HERE / "analysis/analyse.py")
an = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(an)


def plp(run: str) -> pd.Series:
    lab = pd.read_csv(HERE / f"labels/{run}/labels_long.csv", dtype={"instance_id": str})
    lab = lab[(lab["demand"] == "PLp") & lab["valid"] & (lab["writer_model"] == an.JUDGE_MODEL)]
    return lab.set_index("instance_id")["level"].astype(int)


def qwk(a: pd.Series, b: pd.Series, k: int = 6) -> float:
    o = np.zeros((k, k))
    for x, y in zip(a, b):
        o[x, y] += 1
    w = np.subtract.outer(np.arange(k), np.arange(k)) ** 2
    e = np.outer(o.sum(1), o.sum(0)) / o.sum()
    return float(1 - (w * o).sum() / (w * e).sum())


def counts(s: pd.Series) -> dict:
    return {int(k): int(v) for k, v in s.value_counts().reindex(range(6), fill_value=0).items()}


def main() -> None:
    sample = pd.read_csv(HERE / "sample.csv", dtype={"instance_id": str})
    tb = sample[(sample["benchmark"] == TB4) & sample["analysis_set"]].set_index("instance_id")
    low, mx = plp("tb4pl-r1").reindex(tb.index).dropna().astype(int), plp("tb4pl-max").reindex(tb.index).dropna().astype(int)
    both = low.index.intersection(mx.index)
    d = mx[both] - low[both]
    human = pd.read_csv(HERE / "human-labels/unblinded.csv", dtype={"pablo_level": "Int64", "claude_level": "Int64"})
    human = human.set_index("instance_id")
    human["max_level"] = human.index.map(mx)
    labelled = human.dropna(subset=["pablo_level"])

    out = {
        "n": {"low": len(low), "max": len(mx), "both": len(both)},
        "levels": {"low": counts(low), "max": counts(mx)},
        "agreement_max_vs_low": {"exact": round(float((d == 0).mean()), 3),
                                 "within1": round(float((d.abs() <= 1).mean()), 3),
                                 "qwk": round(qwk(mx[both], low[both]), 3),
                                 "mean_shift_max_minus_low": round(float(d.mean()), 3),
                                 "lower": int((d < 0).sum()), "higher": int((d > 0).sum())},
        "crosstab_low_rows_max_cols": pd.crosstab(low[both], mx[both]).to_dict(),
        "exploratory_Q1_Q2": {
            name: {"PLp_vs_solve_rate": an.corr(df, "PLp", "solve_rate", "negative"),
                   "PLp_vs_expert_hours": an.corr(df, "PLp", "expert_hours", "positive")}
            for name, df in (("low", tb.assign(PLp=low)), ("max", tb.assign(PLp=mx)))},
        "human_check": {
            "tasks": {i: {"pablo": None if pd.isna(r.pablo_level) else int(r.pablo_level),
                          "low": int(r.judge_level),
                          "max": None if pd.isna(r.max_level) else int(r.max_level),
                          "claude": None if pd.isna(r.claude_level) else int(r.claude_level)}
                      for i, r in human.iterrows()},
            "exact_with_pablo": {"low": int((labelled["pablo_level"] == labelled["judge_level"]).sum()),
                                 "max": int((labelled["pablo_level"] == labelled["max_level"]).sum()),
                                 "of": len(labelled)},
        },
    }
    out["predictions"] = {
        "1_shift_below_zero_and_more_level_2_than_low": bool(d.mean() < 0 and (mx == 2).sum() > (low == 2).sum()),
        "2_max_exact_with_pablo_at_least_4_of_6": bool(out["human_check"]["exact_with_pablo"]["max"] >= 4),
    }
    (HERE / "results/effort_followup.json").write_text(json.dumps(out, indent=2, default=str) + "\n")
    print(json.dumps(out, indent=2, default=str))


if __name__ == "__main__":
    main()
