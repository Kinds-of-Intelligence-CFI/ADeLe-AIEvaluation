"""Level histograms of PLp, PLe and PLs on the seven agentic benchmarks (clean sets). Writes pl_levels.csv and
pl_levels.png.

Labels: each study's release/labels_wide.csv (Opus 5.5 low, v2 prompt); rows with `keep` false are dropped where the
file has that column, and missing labels are skipped.

    python experiments/benchmarks/pl-histograms/plot.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).resolve().parent
BENCH = HERE.parent
DIMS = ["PLp", "PLe", "PLs"]
LEVELS = range(6)
SETS = {"swebench-clean": "SWE-bench Verified", "programbench-pl": "ProgramBench", "deepswe-clean": "DeepSWE",
        "frontierswe-pl": "FrontierSWE", "tb4-clean": "Terminal-Bench 4.0", "tbsci-pl": "TB-Science",
        "tau2-clean": "tau2"}


def main() -> None:
    rows = []
    for study, name in SETS.items():
        w = pd.read_csv(BENCH / study / "release/labels_wide.csv")
        if "keep" in w:
            w = w[w["keep"].astype(bool)]
        for d in DIMS:
            s = w[f"v2/{d}"].dropna().astype(int)
            rows += [{"benchmark": name, "rubric": d, "level": k, "tasks": int((s == k).sum()), "n": len(s)}
                     for k in LEVELS]
    t = pd.DataFrame(rows)
    t.to_csv(HERE / "pl_levels.csv", index=False)

    fig, axes = plt.subplots(len(SETS), len(DIMS), figsize=(9, 12), sharex=True, sharey=True)
    for i, name in enumerate(SETS.values()):
        for j, d in enumerate(DIMS):
            ax = axes[i, j]
            h = t[(t["benchmark"] == name) & (t["rubric"] == d)]
            n = h["n"].iloc[0]
            ax.bar(h["level"], h["tasks"] / n, color=f"C{j}")
            for k, c in zip(h["level"], h["tasks"]):
                if c:
                    ax.text(k, c / n + 0.03, str(c), ha="center", fontsize=7)
            ax.set_ylim(0, 1.15)
            ax.set_xticks(list(LEVELS))
            if i == 0:
                ax.set_title(d)
            if j == 0:
                ax.set_ylabel(f"{name}\n(n = {n})", fontsize=8)
            if i == len(SETS) - 1:
                ax.set_xlabel("level")
    fig.suptitle("Share of clean tasks at each level (counts on bars)", fontsize=10)
    fig.tight_layout()
    fig.savefig(HERE / "pl_levels.png", dpi=150)


if __name__ == "__main__":
    main()
