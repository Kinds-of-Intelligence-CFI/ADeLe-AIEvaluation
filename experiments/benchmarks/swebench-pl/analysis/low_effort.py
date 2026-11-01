"""Step 1c (exploratory; PREREGISTRATION.md): Opus at low effort against Opus at medium on every
solvable task, and Q1/Q2 recomputed on the low labels with the pre-registered analysis's own
functions. Low labels: runs swepl-gate-low and swepl-r1-low; medium: swepl-gate and swepl-r1.
Writes results/low_effort.json.

    python experiments/benchmarks/swebench-pl/analysis/low_effort.py
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE / "analysis"))
from analyse import BUCKETS, DIMS, HF_REVISION, questions  # noqa: E402


def qwk(a: pd.Series, b: pd.Series, k: int = 6) -> float:
    o = np.zeros((k, k))
    for x, y in zip(a.astype(int), b.astype(int)):
        o[x, y] += 1
    w = np.subtract.outer(np.arange(k), np.arange(k)) ** 2
    e = np.outer(o.sum(1), o.sum(0)) / o.sum()
    return float(1 - (w * o).sum() / (w * e).sum()) if (w * e).sum() else float("nan")


def agreement(low: pd.Series, med: pd.Series) -> dict:
    d = low - med
    return {"n": len(d), "exact": round(float((d == 0).mean()), 3),
            "within1": round(float((d.abs() <= 1).mean()), 3),
            "qwk": round(qwk(low, med), 3), "mean_shift_low_minus_medium": round(float(d.mean()), 3)}


def labels(runs: list[str]) -> pd.DataFrame:
    lab = pd.concat(pd.read_csv(HERE / f"labels/{r}/labels_long.csv") for r in runs)
    assert lab["valid"].all()
    return lab.pivot(index="instance_id", columns="demand", values="level")[DIMS]


def main() -> None:
    from datasets import load_dataset

    low, med = labels(["swepl-gate-low", "swepl-r1-low"]), labels(["swepl-gate", "swepl-r1"])
    sample = pd.read_csv(HERE / "sample.csv").set_index("instance_id")
    solvable = sample.index[sample["solvable"]]
    low, med = low.loc[solvable], med.loc[solvable]
    assert len(low) == len(med) == 435

    out = {"n_tasks": len(low),
           "agreement_all": agreement(low.stack(), med.stack()),
           "agreement_by_rubric": {d: agreement(low[d], med[d]) for d in DIMS},
           "levels_low": {d: {int(k): int(v) for k, v in low[d].value_counts().sort_index().items()} for d in DIMS}}
    meta = load_dataset("princeton-nlp/SWE-bench_Verified", split="test",
                        revision=HF_REVISION).to_pandas().set_index("instance_id")
    df = low.join(sample).join(meta["difficulty"])
    df["time_to_fix"] = df["difficulty"].map(BUCKETS)
    varied = [d for d in DIMS if df[d].nunique() >= 3]
    out["questions_on_low_labels"] = questions(df, varied)
    (HERE / "results/low_effort.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
