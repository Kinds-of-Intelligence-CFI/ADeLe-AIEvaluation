"""Pre-registered analysis of s-swe-gate (PREREGISTRATION.md, amendment 2). Writes results/s_swe_gate.json.

PLp under candidate S (this run) and under the current text (natural-prompt run npb-gate-opuslow), both Opus low
with the v2 prompt, one call per task; only answers by claude-opus-5-5 count. Solve rates and the solvable flag
come from swebench-pl/sample.csv.
  G1  Spearman of S's PLp with solve rate over the solvable gate tasks < 0, one-sided p < 0.05
  G2  S's Spearman is at most 0.15 weaker (closer to zero) than the current text's on the same tasks
  G3  no collapse: the most common level holds at most 85% of the 44 tasks

    python experiments/benchmarks/plp-b2/analysis/swe_gate.py
    python experiments/benchmarks/plp-b2/analysis/swe_gate.py --run sq-swe-gate --out sq_swe_gate.json  # amendment 4
"""

import argparse
import json
from pathlib import Path

import pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parents[1]
BENCH = HERE.parent
JUDGE = "claude-opus-5-5"


def levels(path: Path) -> pd.Series:
    lab = pd.read_csv(path)
    lab = lab[lab["valid"] & (lab["writer_model"] == JUDGE) & (lab["demand"] == "PLp")]
    return lab.set_index("instance_id")["level"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default="s-swe-gate")
    ap.add_argument("--out", default="s_swe_gate.json")
    args = ap.parse_args()
    s = levels(HERE / f"labels/{args.run}/labels_long.csv")
    cur = levels(BENCH / "natural-prompt/labels/npb-gate-opuslow/labels_long.csv")
    sample = pd.read_csv(BENCH / "swebench-pl/sample.csv").set_index("instance_id")
    df = pd.DataFrame({"S": s, "current": cur}).join(sample[["solve_rate", "solvable"]])
    sol = df[df["solvable"]].dropna(subset=["S", "current"])
    r_s, p_s = spearmanr(sol["S"], sol["solve_rate"])
    r_c, p_c = spearmanr(sol["current"], sol["solve_rate"])
    modal = float(df["S"].value_counts(normalize=True).max())
    checks = {"G1_S_negative_p_lt_0.05": bool(r_s < 0 and p_s / 2 < 0.05),
              "G2_at_most_0.15_weaker": bool(r_s - r_c <= 0.15),
              "G3_modal_share_le_0.85": bool(modal <= 0.85)}
    out = {"n_tasks": int(df["S"].notna().sum()), "n_solvable": int(len(sol)),
           "S_vs_solve_rate": {"rho": round(float(r_s), 3), "p_one_sided": float(f"{p_s / 2:.3g}")},
           "current_vs_solve_rate": {"rho": round(float(r_c), 3), "p_one_sided": float(f"{p_c / 2:.3g}")},
           "S_modal_share": round(modal, 3), "checks": checks,
           "descriptive": {"S_levels": {int(k): int(v) for k, v in df["S"].value_counts().sort_index().items()},
                           "current_levels": {int(k): int(v) for k, v in df["current"].value_counts().sort_index().items()},
                           "exact_S_vs_current": round(float((df["S"] == df["current"]).mean()), 3),
                           "mean_shift_S_minus_current": round(float((df["S"] - df["current"]).mean()), 3)}}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / args.out).write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
