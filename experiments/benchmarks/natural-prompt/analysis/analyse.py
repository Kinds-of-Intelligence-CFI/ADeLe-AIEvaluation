"""Pre-registered analysis of natural-prompt (PREREGISTRATION.md). Writes results/natural_prompt.json.

A. Safeguards. Sonnet 5.5 high with the natural prompt on the 44 PLp gate cells (np-plp-s55h). The groups
   come from judge-sonnet55: the 23 cells its safeguards blocked twice under the old prompt, and the 21 it
   answered.
B. Method. Opus low with the natural prompt (np-gate-opuslow) against Opus low with the old prompt
   (swebench-pl/labels/swepl-gate-low), on the 132 gate cells.

    python experiments/benchmarks/natural-prompt/analysis/analyse.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parents[1]
BENCH = HERE.parent
JUDGE_IO = HERE.parents[3] / "judge-io"
DIMS = ["PLp", "PLe", "PLs"]
NEW = "opus-low-natural"


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


def counted(path: Path, model: str) -> pd.DataFrame:
    lab = pd.read_csv(path, dtype={"instance_id": str})
    return lab[lab["valid"] & lab["writer_model"].astype(str).str.startswith(model)]


def mean_chars(folder: Path) -> float | None:
    files = list(folder.glob("*.txt"))
    return round(float(np.mean([len(f.read_text(encoding="utf-8")) for f in files])), 1) if files else None


def main() -> None:
    out = {}

    # A. Safeguards on the PLp cells.
    idx = pd.read_csv(HERE / "labels/np-plp-s55h/prompts_index.csv", dtype={"instance_id": str})
    before = pd.read_csv(BENCH / "judge-sonnet55/labels/s55h-gate/labels_long.csv", dtype={"instance_id": str})
    answered_before = set(before.loc[before["demand"] == "PLp", "instance_id"])
    blocked = set(idx["instance_id"]) - answered_before
    control = set(idx["instance_id"]) & answered_before
    a = counted(HERE / "labels/np-plp-s55h/labels_long.csv", "claude-sonnet-5-5")
    answered = set(a["instance_id"])
    calls = pd.read_csv(HERE / "labels/np-plp-s55h/calls.csv")
    out["A"] = {"blocked_twice_under_old_prompt": len(blocked), "blocked_answered_now": len(blocked & answered),
                "control_cells": len(control), "control_answered_now": len(control & answered),
                "calls": int(calls["calls"].sum()), "calls_stopped_by_a_safeguard": int(calls["safeguard_stops"].sum()),
                "passes": len(blocked - answered) <= 2}

    # B. Opus low, natural prompt against old prompt.
    expected = len(pd.read_csv(HERE / "labels/np-gate-opuslow/prompts_index.csv"))
    new = counted(HERE / "labels/np-gate-opuslow/labels_long.csv", "claude-opus-5-5").assign(judge=NEW)
    old = pd.read_csv(BENCH / "swebench-pl/labels/swepl-gate-low/labels_long.csv", dtype={"instance_id": str})
    med = pd.read_csv(BENCH / "swebench-pl/labels/swepl-gate/labels_long.csv", dtype={"instance_id": str})
    wide = pd.concat([new, old, med]).pivot_table(index=["instance_id", "demand"], columns="judge", values="level")
    nvo = {"all": pair(wide, NEW, "opus-low"), **{d: pair(wide.xs(d, level="demand"), NEW, "opus-low") for d in DIMS}}
    checks = {"1_exact_ge_0.83": nvo["all"]["exact"] >= 0.83,
              "2_within1_ge_0.98": nvo["all"]["within1"] >= 0.98,
              "3_shift_within_0.10_each": all(abs(nvo[d]["mean_shift"]) <= 0.10 for d in DIMS),
              "4_counted_ge_0.95": len(new) >= 0.95 * expected}
    out["B"] = {"cells": expected, "counted": len(new), "natural_vs_old": nvo,
                "natural_vs_opus_medium": pair(wide, NEW, "opus-medium"),
                "old_vs_opus_medium": pair(wide.dropna(subset=[NEW]), "opus-low", "opus-medium"),
                "mean_answer_chars": {"natural": mean_chars(JUDGE_IO / "np-gate-opuslow/responses/opus-low"),
                                      "old": mean_chars(JUDGE_IO / "swepl-gate-low/responses/opus-low")},
                "checks": checks, "passes": all(checks.values())}

    out["verdict"] = {(True, True): "the natural prompt fixes the flags and keeps the labels",
                      (True, False): "fixes the flags, but changes the labels",
                      (False, True): "keeps the labels, but does not fix the flags",
                      (False, False): "neither"}[(out["A"]["passes"], out["B"]["passes"])]
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results/natural_prompt.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({"A": out["A"], "B": {k: out["B"][k] for k in ("counted", "natural_vs_old", "checks", "passes")},
                      "verdict": out["verdict"]}, indent=1))


if __name__ == "__main__":
    main()
