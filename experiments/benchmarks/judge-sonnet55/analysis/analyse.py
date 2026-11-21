"""Pre-registered analysis of judge-sonnet55 (PREREGISTRATION.md).

Sonnet 5.5 at high effort against Opus 5.5 at medium effort, on the PLp and PLe cells of swebench-pl's
gate (44 SWE-bench Verified tasks). Opus low (swepl-gate-low) is the yardstick: it is the current judge
setting, and its agreement with Opus medium on the same cells is the bar. Opus max and Sonnet 5 max
(swebench-30, run swev30-r4) are reported for context. Writes results/agreement.json.

    python experiments/benchmarks/judge-sonnet55/analysis/analyse.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parents[1]
BENCH = HERE.parent
RUN = "s55h-gate"
NEW, MED, LOW, MAX, S5 = "sonnet55-high", "opus-medium", "opus-low", "opus", "sonnet"
DIMS = ["PLp", "PLe"]
MODEL = "claude-sonnet-5-5"


def qwk(a: pd.Series, b: pd.Series, k: int = 6) -> float:
    """Quadratic-weighted Cohen's kappa on levels 0..k-1 (as swebench-pl/gate.py)."""
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


def both(wide: pd.DataFrame, x: str, y: str) -> dict:
    return {"all": pair(wide, x, y), **{d: pair(wide.xs(d, level="demand"), x, y) for d in DIMS}}


def main() -> None:
    new = pd.read_csv(HERE / f"labels/{RUN}/labels_long.csv", dtype={"instance_id": str})
    expected = len(pd.read_csv(HERE / f"labels/{RUN}/prompts_index.csv"))
    ours = new["writer_model"].astype(str).str.startswith(MODEL)
    counted = new[ours & new["valid"]]
    frames = [counted.drop(columns="writer_model"),
              pd.read_csv(BENCH / "swebench-pl/labels/swepl-gate/labels_long.csv", dtype={"instance_id": str}),
              pd.read_csv(BENCH / "swebench-pl/labels/swepl-gate-low/labels_long.csv", dtype={"instance_id": str}),
              pd.read_csv(BENCH / "swebench-30/labels/swev30-r4/labels_long.csv", dtype={"instance_id": str})]
    lab = pd.concat(frames)
    lab = lab[lab["demand"].isin(DIMS)]
    wide = lab.pivot_table(index=["instance_id", "demand"], columns="judge", values="level")
    s5 = wide.dropna(subset=[S5])
    out = {
        "cells": expected, "answered": len(new), "parsed": int(new["valid"].sum()),
        "written_by_other_model": int((~ours).sum()), "counted": len(counted),
        "new_vs_medium": both(wide, NEW, MED),
        "low_vs_medium": both(wide.dropna(subset=[NEW]), LOW, MED),
        "new_vs_low": both(wide, NEW, LOW),
        "new_vs_max": both(wide, NEW, MAX),
        "on_sonnet5_cells": {"new_vs_max": pair(s5, NEW, MAX), "sonnet5_vs_max": pair(s5, S5, MAX),
                             "new_vs_sonnet5": pair(s5, NEW, S5)},
        "levels": {j: wide[j].dropna().astype(int).value_counts().sort_index().to_dict() for j in (NEW, MED, LOW)},
    }
    nm = out["new_vs_medium"]
    checks = {
        "1_exact_vs_medium_ge_0.80": nm["all"]["exact"] >= 0.80,
        "2_within1_vs_medium_ge_0.98": nm["all"]["within1"] >= 0.98,
        "3_shift_within_0.15_each": all(abs(nm[d]["mean_shift"]) <= 0.15 for d in DIMS),
        "4_parsed_and_own_model_ge_0.95": len(counted) >= 0.95 * expected,
    }
    fails = (nm["all"]["exact"] < 0.75 or nm["all"]["within1"] < 0.95
             or any(abs(nm[d]["mean_shift"]) > 0.25 for d in DIMS))
    out["checks"] = checks
    out["verdict"] = "works well" if all(checks.values()) else ("does not" if fails else "unclear")
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results/agreement.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({k: out[k] for k in ("cells", "counted", "written_by_other_model", "checks", "verdict")}, indent=1))
    print("new vs medium:", nm, "\nlow vs medium:", out["low_vs_medium"], "\nSonnet 5 cells:", out["on_sonnet5_cells"])


if __name__ == "__main__":
    main()
