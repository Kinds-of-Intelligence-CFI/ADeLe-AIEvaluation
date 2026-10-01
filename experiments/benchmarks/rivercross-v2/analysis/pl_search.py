"""Pre-registered analysis of amendment 4 (PREREGISTRATION.md): PLe and PLs on the 54 grid states. Writes
results/pl_search.json.

Labels: PLe, PLs from the mass run rivercross-search-pl (one Opus-low call each); PLp = median of plp-b2's three
o-search repeats (text O). Only valid answers written by claude-opus-5-5 count. Outcomes per state from amendments 2
and 3: ctg (execution length), bits (search), and the Opus and Sonnet failure and non-optimal shares (states with at
least three attempts by the intended model). Spearman of each rubric with each.

    python experiments/benchmarks/rivercross-v2/analysis/pl_search.py
"""

import json
from pathlib import Path

import pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parents[1]
BENCH = HERE.parent
MODEL = "claude-opus-5-5"
SOLVERS = {"opus": ("rc-solve-opus", "claude-opus-5-5"), "sonnet": ("rc-solve-sonnet", "claude-sonnet-5-5")}


def main() -> None:
    df = pd.read_csv(HERE / "frames/search_truth.csv").set_index("custom_id")
    lab = pd.read_csv(BENCH / "mass-annotation/runs/rivercross-search-pl/labels.csv")
    lab = lab[lab["valid"].astype(bool) & lab["writer_model"].astype(str).str.startswith(MODEL)]
    df = df.join(lab.assign(r=lab["rubric_ref"].str.removeprefix("v2/")).pivot(
        index="instance_id", columns="r", values="level"))
    o = pd.read_csv(BENCH / "plp-b2/labels/o-search/labels_long.csv")
    o = o[o["valid"] & (o["writer_model"] == MODEL)]
    df["PLp"] = o.groupby("instance_id")["level"].median()
    for name, (run, model) in SOLVERS.items():
        sv = pd.read_csv(HERE / f"labels/{run}/solve_long.csv")
        sv = sv[sv["writer_model"] == model]
        per = sv.groupby("custom_id")
        keep = per.size()[per.size() >= 3].index
        df[f"{name}_failure"] = (1 - per["success"].mean()).loc[keep]
        df[f"{name}_non_optimal"] = (1 - per["optimal"].mean()).loc[keep]
    outcomes = ["ctg", "bits", "opus_failure", "opus_non_optimal", "sonnet_failure", "sonnet_non_optimal"]
    out = {"n": int(len(df)), "unlabelled": {d: sorted(df.index[df[d].isna()]) for d in ("PLe", "PLs", "PLp")},
           "levels": {d: {str(k): int(v) for k, v in df[d].value_counts().sort_index().items()}
                      for d in ("PLe", "PLs", "PLp")}, "spearman": {}}
    for d in ("PLe", "PLs", "PLp"):
        for y in outcomes:
            g = df[[d, y]].dropna()
            r, p = spearmanr(g[d], g[y])
            out["spearman"][f"{d}_vs_{y}"] = {"n": int(len(g)), "rho": round(float(r), 3), "p": float(f"{p:.3g}")}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results/pl_search.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
