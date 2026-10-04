"""Level histograms of the five v2 rubrics (PLp, PLe, PLs, MSm, MSc) on every benchmark, with the current labels: the
relabel-v2 runs (Opus 5.5 low, v2 prompt, reviewed examples of d4ec2ec). Agentic sets are their clean sets; CooperBench
is split into coop and solo prompts. Writes dims_now.csv and dims_now.png.

    python experiments/benchmarks/pl-histograms/plot_dims_now.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
BENCH = HERE.parent
RUNS = ["relabel-v2", "relabel-v2-long", "relabel-v2-eqbench4", "relabel-v2-cooperbench", "relabel-v2-gamearena"]
MODEL = "claude-opus-5-5"
DIMS = ["PLp", "PLe", "PLs", "MSm", "MSc"]
LEVELS = np.arange(6)
SETS = {"swe-bench-verified": "SWE-bench Verified", "programbench": "ProgramBench", "deepswe-v1.1": "DeepSWE",
        "frontierswe-v2": "FrontierSWE", "terminal-bench-4.0.0": "Terminal-Bench 4.0",
        "terminal-bench-science-0.1": "TB-Science", "tau2": "tau2", "eqbench4": "EQ-Bench 4",
        "cooperbench@coop": "CooperBench (coop)", "cooperbench@solo": "CooperBench (solo)", "gamearena": "Game Arena"}


def labels() -> pd.DataFrame:
    parts = []
    for run in RUNS:
        lab = pd.read_csv(BENCH / "mass-annotation/runs" / run / "labels.csv", dtype={"instance_id": str})
        parts.append(lab[lab["valid"].astype(bool) & lab["writer_model"].astype(str).str.startswith(MODEL)])
    lab = pd.concat(parts)
    key = lab["benchmark"].where(~lab["benchmark"].str.startswith("tau2"), "tau2")
    coop = lab["benchmark"] == "cooperbench"
    key = key.where(~coop, "cooperbench@" + lab["instance_id"].str.split("@").str[-1])
    return lab.assign(set=key, rubric=lab["rubric_ref"].str.removeprefix("v2/"))


def main() -> None:
    lab = labels()
    rows = []
    for key, name in SETS.items():
        for d in DIMS:
            s = lab[(lab["set"] == key) & (lab["rubric"] == d)]["level"].astype(int)
            rows += [{"benchmark": name, "rubric": d, "level": int(k), "tasks": int((s == k).sum()), "n": len(s)}
                     for k in LEVELS]
    t = pd.DataFrame(rows)
    t.to_csv(HERE / "dims_now.csv", index=False)

    fig, axes = plt.subplots(len(SETS), len(DIMS), figsize=(13, 17), sharex=True, sharey=True)
    for i, name in enumerate(SETS.values()):
        for j, d in enumerate(DIMS):
            ax = axes[i, j]
            h = t[(t["benchmark"] == name) & (t["rubric"] == d)]
            n = h["n"].iloc[0]
            ax.bar(h["level"], h["tasks"] / n, color=f"C{j}")
            for k, c in zip(h["level"], h["tasks"]):
                if c:
                    ax.text(k, c / n + 0.03, str(c), ha="center", fontsize=6)
            ax.set_ylim(0, 1.2)
            ax.set_xticks(list(LEVELS))
            if i == 0:
                ax.set_title(d)
            if j == 0:
                ax.set_ylabel(f"{name}\n(n = {n})", fontsize=8)
            if i == len(SETS) - 1:
                ax.set_xlabel("level")
    fig.suptitle("Demand levels per benchmark, current labels (share of tasks; counts on bars)", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.985))
    fig.savefig(HERE / "dims_now.png", dpi=130)
    print(t.pivot_table(index=["benchmark", "rubric"], columns="level", values="tasks").to_string())


if __name__ == "__main__":
    main()
