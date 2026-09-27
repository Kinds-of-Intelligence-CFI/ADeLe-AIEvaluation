"""Effort gate of swebench-pl (PREREGISTRATION.md, step 1): Opus at medium against Opus and
Sonnet at max, on the PL cells of swebench-30. Step 1b runs the same comparison for Opus at low,
also against Opus-medium.

Needs current labels: swebench-30/collect.py --run swev30-r4, then collect.py --run <gate run>.
Prints the pairwise agreements and the four conditions; writes results/gate.json (step 1) or
results/gate-<run>.json.

    python experiments/benchmarks/swebench-pl/gate.py
    python experiments/benchmarks/swebench-pl/gate.py --run swepl-gate-low --judge opus-low   # step 1b
"""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
S30 = HERE.parent / "swebench-30"
DIMS = ["PLp", "PLe", "PLs"]
MED, MAX, SON = "opus-medium", "opus", "sonnet"


def qwk(a: pd.Series, b: pd.Series, k: int = 6) -> float:
    """Quadratic-weighted Cohen's kappa on levels 0..k-1 (nan when there is no spread)."""
    o = np.zeros((k, k))
    for x, y in zip(a.astype(int), b.astype(int)):
        o[x, y] += 1
    w = np.subtract.outer(np.arange(k), np.arange(k)) ** 2
    e = np.outer(o.sum(1), o.sum(0)) / o.sum()
    return float(1 - (w * o).sum() / (w * e).sum()) if (w * e).sum() else float("nan")


def pair(df: pd.DataFrame, x: str, y: str) -> dict:
    d = df[[x, y]].dropna()
    diff = d[x] - d[y]
    return {"n": len(d), "exact": round(float((diff == 0).mean()), 3),
            "within1": round(float((diff.abs() <= 1).mean()), 3),
            "mean_shift": round(float(diff.mean()), 3), "qwk": round(qwk(d[x], d[y]), 3)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default="swepl-gate")
    ap.add_argument("--judge", default=MED)
    run, j = ap.parse_args().run, ap.parse_args().judge
    tag = j.removeprefix("opus-")                       # "medium" or "low", as in the output keys
    r4 = pd.read_csv(S30 / "labels/swev30-r4/labels_long.csv", dtype={"instance_id": str})
    gate = pd.read_csv(HERE / f"labels/{run}/labels_long.csv", dtype={"instance_id": str})
    expected = len(pd.read_csv(HERE / f"labels/{run}/prompts_index.csv"))
    frames = [r4[r4["demand"].isin(DIMS)], gate]
    if j != MED:
        frames.append(pd.read_csv(HERE / "labels/swepl-gate/labels_long.csv", dtype={"instance_id": str}))
    wide = pd.concat(frames).pivot_table(index=["instance_id", "demand"], columns="judge", values="level")

    with_son = wide.dropna(subset=[SON])
    out = {
        "parse_rate": round(float(gate["valid"].sum()) / expected, 3),
        f"{tag}_vs_max": pair(wide, j, MAX),
        f"{tag}_vs_max_by_rubric": {d: pair(wide.xs(d, level="demand"), j, MAX) for d in DIMS},
        "on_sonnet_cells": {f"{tag}_vs_max": pair(with_son, j, MAX),
                            "sonnet_vs_max": pair(with_son, SON, MAX),
                            f"{tag}_vs_sonnet": pair(with_son, j, SON)},
    }
    if j != MED:
        out[f"{tag}_vs_medium"] = pair(wide, j, MED)
        out[f"{tag}_vs_medium_by_rubric"] = {d: pair(wide.xs(d, level="demand"), j, MED) for d in DIMS}
    checks = {
        "1_within1_ge_0.90": out[f"{tag}_vs_max"]["within1"] >= 0.90,
        f"2_exact_{tag}_ge_sonnet": out["on_sonnet_cells"][f"{tag}_vs_max"]["exact"]
                                    >= out["on_sonnet_cells"]["sonnet_vs_max"]["exact"],
        "3_shift_within_0.25": all(abs(out[f"{tag}_vs_max_by_rubric"][d]["mean_shift"]) <= 0.25 for d in DIMS),
        "4_parse_ge_0.98": out["parse_rate"] >= 0.98,
    }
    out["checks"] = checks
    out["gate_passes"] = all(checks.values())
    (HERE / "results").mkdir(exist_ok=True)
    name = "gate.json" if run == "swepl-gate" else f"gate-{run}.json"
    (HERE / "results" / name).write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
