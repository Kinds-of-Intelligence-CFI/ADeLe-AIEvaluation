"""Pre-registered analysis of swebench-pl (PREREGISTRATION.md, section Analysis).

Analysis set: the 435 tasks with solve rate >= 0.05, pooling the gate run's solvable tasks and
swepl-r1. Reports the level distribution of each PL rubric; Q1, Spearman rho between each PL
rubric and solve rate (PLe and PLs only if they take at least three values); Q2, Spearman rho
between PLp and SWE-bench's human time-to-fix bucket; both without the 37 step-1 tasks; and,
once results/audit_flags.csv exists, both without the tasks the test-validity audit flags.
As in the power statement: two-sided alpha = 0.05 and a Fisher-z 95% CI (Bonett-Wright standard
error for Spearman's rho); a prediction is supported when p < 0.05 with the predicted sign.
`n_off_mode` counts tasks away from a rubric's most common level: when it is tiny, rho rests on
those few tasks.

Needs the committed labels and sample.csv, plus the time-to-fix buckets from the Hugging Face
dataset at the pinned revision. Writes results/analysis.json and results/pl_levels.csv.

    python experiments/benchmarks/swebench-pl/analysis/analyse.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parents[1]
DIMS = ["PLp", "PLe", "PLs"]
RUNS = ["swepl-gate", "swepl-r1"]
HF_REVISION = "c104f840cc67f8b6eec6f759ebc8b2693d585d4a"
BUCKETS = {"<15 min fix": 0, "15 min - 1 hour": 1, "1-4 hours": 2, ">4 hours": 3}


def rho(x: pd.Series, y: pd.Series, direction: str) -> dict:
    """Spearman rho of rubric x with y, two-sided p, Fisher-z 95% CI, and the verdict."""
    r, p = spearmanr(x, y)
    n = len(x)
    se = np.sqrt((1 + r**2 / 2) / (n - 3))
    lo, hi = np.tanh(np.arctanh(r) + np.array([-1.96, 1.96]) * se)
    sign_ok = r < 0 if direction == "negative" else r > 0
    return {"n": n, "n_off_mode": int((x != x.mode()[0]).sum()), "rho": round(float(r), 3),
            "p_two_sided": float(f"{p:.3g}"), "ci95": [round(float(lo), 3), round(float(hi), 3)],
            "predicted": direction, "supported": bool(sign_ok and p < 0.05)}


def questions(df: pd.DataFrame, dims: list[str]) -> dict:
    out = {f"Q1_{d}_vs_solve_rate": rho(df[d], df["solve_rate"], "negative") for d in dims}
    out["Q2_PLp_vs_time_to_fix"] = rho(df["PLp"], df["time_to_fix"], "positive")
    return out


def main() -> None:
    from datasets import load_dataset

    labels = pd.concat(pd.read_csv(HERE / f"labels/{r}/labels_long.csv") for r in RUNS)
    assert labels["valid"].all() and (labels["judge"] == "opus-medium").all()
    wide = labels.pivot(index="instance_id", columns="demand", values="level")[DIMS]
    sample = pd.read_csv(HERE / "sample.csv").set_index("instance_id")
    meta = load_dataset("princeton-nlp/SWE-bench_Verified", split="test",
                        revision=HF_REVISION).to_pandas().set_index("instance_id")
    df = wide.join(sample).join(meta["difficulty"])
    df["time_to_fix"] = df["difficulty"].map(BUCKETS)
    df = df[df["solvable"]]
    assert len(df) == 435 and df[DIMS + ["solve_rate", "time_to_fix"]].notna().all().all()

    levels = pd.DataFrame({d: df[d].value_counts().reindex(range(6), fill_value=0) for d in DIMS})
    levels.index.name = "level"
    varied = [d for d in DIMS if df[d].nunique() >= 3]
    step1 = df["run"] == "swepl-gate"

    out = {
        "analysis_set": {"n": len(df), "from_step1": int(step1.sum()), "from_step2": int((~step1).sum())},
        "levels": {d: {int(k): int(v) for k, v in levels[d].items()} for d in DIMS},
        "rubrics_tested_in_Q1": varied,
        "main": questions(df, varied),
        "robustness_without_step1": questions(df[~step1], varied),
    }
    flags = HERE / "results/audit_flags.csv"
    if flags.exists():
        flagged = set(pd.read_csv(flags).query("flagged")["instance_id"])
        kept = df[~df.index.isin(flagged)]
        out["robustness_without_audit_flags"] = {"n_flagged": len(flagged & set(df.index)),
                                                 **questions(kept, varied)}
    else:
        out["robustness_without_audit_flags"] = "pending: the test-validity audit has not run"

    (HERE / "results").mkdir(exist_ok=True)
    levels.to_csv(HERE / "results/pl_levels.csv")
    (HERE / "results/analysis.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
