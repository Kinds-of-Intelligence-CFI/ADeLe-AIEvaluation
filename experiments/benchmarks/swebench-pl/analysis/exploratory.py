"""Exploratory checks on the swebench-pl result (NOT pre-registered; added 2026-09-27 after the
pre-registered analysis ran). Does PLp's relation to solve rate reduce to something simpler?

- the human time-to-fix bucket against solve rate, as a reference;
- problem-statement length and gold-patch size (added or removed lines), against both;
- partial Spearman of PLp with solve rate given each of these (ranks, linear residuals);
- mean solve rate by PLp level, and PLp against solve rate within each repository of 25+ tasks.

Needs data/instances/ (gitignored) for the statement lengths. Writes results/exploratory.json.

    python experiments/benchmarks/swebench-pl/analysis/exploratory.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[2]
HF_REVISION = "c104f840cc67f8b6eec6f759ebc8b2693d585d4a"
BUCKETS = {"<15 min fix": 0, "15 min - 1 hour": 1, "1-4 hours": 2, ">4 hours": 3}


def main() -> None:
    from datasets import load_dataset

    labels = pd.concat(pd.read_csv(HERE / f"labels/{r}/labels_long.csv") for r in ["swepl-gate", "swepl-r1"])
    df = labels.pivot(index="instance_id", columns="demand", values="level")
    inst = pd.read_parquet(ROOT / "data/instances/instances_swe-bench-verified.parquet").set_index("instance_id")
    meta = load_dataset("princeton-nlp/SWE-bench_Verified", split="test",
                        revision=HF_REVISION).to_pandas().set_index("instance_id")
    df = (df.join(pd.read_csv(HERE / "sample.csv").set_index("instance_id"))
            .join(inst["prompt"].str.len().rename("statement_chars"))
            .join(meta[["difficulty", "patch", "repo"]]))
    df = df[df["solvable"]].copy()
    df["time_to_fix"] = df["difficulty"].map(BUCKETS)
    df["patch_lines"] = df["patch"].str.count(r"\n[+-](?![+-])")

    def sr(a: str, b: str) -> dict:
        r, p = spearmanr(df[a], df[b])
        return {"rho": round(float(r), 3), "p": float(f"{p:.2g}")}

    def partial(covs: list[str]) -> float:
        ranks = df[["PLp", "solve_rate"] + covs].rank()
        z = np.column_stack([np.ones(len(ranks))] + [ranks[c] for c in covs])
        res = {v: ranks[v] - z @ np.linalg.lstsq(z, ranks[v], rcond=None)[0] for v in ["PLp", "solve_rate"]}
        return round(float(np.corrcoef(res["PLp"], res["solve_rate"])[0, 1]), 3)

    out = {
        "n": len(df),
        "spearman": {
            "time_to_fix_vs_solve_rate": sr("time_to_fix", "solve_rate"),
            "statement_chars_vs_solve_rate": sr("statement_chars", "solve_rate"),
            "patch_lines_vs_solve_rate": sr("patch_lines", "solve_rate"),
            "PLp_vs_statement_chars": sr("PLp", "statement_chars"),
            "PLp_vs_patch_lines": sr("PLp", "patch_lines"),
        },
        "partial_PLp_vs_solve_rate_given": {
            "statement_chars": partial(["statement_chars"]),
            "time_to_fix": partial(["time_to_fix"]),
            "patch_lines": partial(["patch_lines"]),
            "statement_chars+time_to_fix+patch_lines": partial(["statement_chars", "time_to_fix", "patch_lines"]),
        },
        "solve_rate_by_PLp": {int(k): {"n": int(g.size), "mean": round(float(g.mean()), 3)}
                              for k, g in df.groupby("PLp")["solve_rate"]},
        "PLp_vs_solve_rate_by_repo": {r: {"n": len(g), "rho": round(float(spearmanr(g["PLp"], g["solve_rate"])[0]), 3)}
                                      for r, g in df.groupby("repo") if len(g) >= 25},
    }
    (HERE / "results/exploratory.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
