"""Exploratory analyses of tau2-tb4-pl; RESULTS.md labels them as such.

- Planned in PREREGISTRATION.md, not a test: the level distributions against swebench-pl's
  Opus-low labels on its 435 solvable tasks.
- Not pre-registered (drafted while the labels were collected, before the pre-registered analysis
  ran), as swebench-pl's exploratory checks: task-text length against solve rate and PLp, the
  partial Spearman of PLp with solve rate given text length (ranks, linear residuals), and mean
  solve rate by PLp level; per tau2 domain and on Terminal-Bench's analysis set.

Registered-judge labels only. Needs data/instances/ (gitignored) for the text lengths.
Writes results/exploratory.json.

    python experiments/benchmarks/tau2-tb4-pl/analysis/exploratory.py
"""

import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[2]
SWEPL = HERE.parent / "swebench-pl"
DIMS = ["PLp", "PLe", "PLs"]
TB4 = "terminal-bench-4.0.0"
_spec = importlib.util.spec_from_file_location("make_prompts", HERE / "make_prompts.py")
_mp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mp)


def shares(df: pd.DataFrame) -> dict:
    return {d: {"n": int(df[d].notna().sum()), "mean": round(float(df[d].mean()), 2),
                "share_by_level": {int(k): round(float(v), 3)
                                   for k, v in df[d].value_counts(normalize=True).sort_index().items()}}
            for d in DIMS}


def text_checks(df: pd.DataFrame) -> dict:
    df = df.dropna(subset=["PLp"])

    def sr(a: str, b: str) -> dict:
        r, p = spearmanr(df[a], df[b])
        return {"rho": round(float(r), 3), "p": float(f"{p:.2g}")}

    ranks = df[["PLp", "solve_rate", "text_chars"]].rank()
    z = np.column_stack([np.ones(len(ranks)), ranks["text_chars"]])
    res = {v: ranks[v] - z @ np.linalg.lstsq(z, ranks[v], rcond=None)[0] for v in ["PLp", "solve_rate"]}
    return {"n": len(df),
            "text_chars_vs_solve_rate": sr("text_chars", "solve_rate"),
            "PLp_vs_text_chars": sr("PLp", "text_chars"),
            "partial_PLp_vs_solve_rate_given_text_chars": round(float(np.corrcoef(res["PLp"], res["solve_rate"])[0, 1]), 3),
            "solve_rate_by_PLp": {int(k): {"n": int(g.size), "mean": round(float(g.mean()), 3)}
                                  for k, g in df.groupby("PLp")["solve_rate"]}}


def main() -> None:
    labels = pd.concat(pd.read_csv(HERE / f"labels/{r}/labels_long.csv", dtype={"instance_id": str})
                       for r in ["tau2pl-r1", "tb4pl-r1"])
    labels = labels[labels["valid"] & (labels["writer_model"] == "claude-opus-5-5")]
    wide = labels.pivot(index=["benchmark", "instance_id"], columns="demand", values="level")[DIMS]
    sample = pd.read_csv(HERE / "sample.csv", dtype={"instance_id": str})
    df = sample.set_index(["benchmark", "instance_id"]).join(wide).reset_index()

    chars = {}
    for bench in df["benchmark"].unique():
        if bench == TB4:
            inst = pd.read_parquet(ROOT / f"data/instances/instances_{bench}.parquet")
            inst["prompt"] = inst["prompt"].map(_mp.strip_canary)
        else:
            inst = pd.read_csv(ROOT / f"data/instances/instances_{bench}.csv", dtype={"instance_id": str})
        chars |= {(bench, i): len(p) for i, p in zip(inst["instance_id"], inst["prompt"])}
    df["text_chars"] = [chars[(b, i)] for b, i in zip(df["benchmark"], df["instance_id"])]

    swe = pd.concat(pd.read_csv(SWEPL / f"labels/{r}/labels_long.csv") for r in ["swepl-gate-low", "swepl-r1-low"])
    swe = swe.pivot(index="instance_id", columns="demand", values="level")[DIMS]
    swe_sample = pd.read_csv(SWEPL / "sample.csv").set_index("instance_id")
    swe = swe.loc[swe_sample.index[swe_sample["solvable"]]]

    sets = {"swe-bench-verified (swebench-pl, Opus low, 435 solvable)": swe}
    sets |= {b: g for b, g in df[df["benchmark"].str.startswith("tau2-")].groupby("benchmark")}
    tb = df[df["benchmark"] == TB4]
    sets |= {f"{TB4} analysis set": tb[tb["analysis_set"]], f"{TB4} other 32": tb[~tb["analysis_set"]]}

    out = {
        "planned_level_distributions": {s: shares(g) for s, g in sets.items()},
        "not_preregistered_text_length": {
            **{b: text_checks(g) for b, g in df[df["benchmark"].str.startswith("tau2-")].groupby("benchmark")},
            f"{TB4} analysis set": text_checks(tb[tb["analysis_set"]])},
    }
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results/exploratory.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
