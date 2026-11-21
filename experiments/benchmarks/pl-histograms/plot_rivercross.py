"""Level histograms of PLp, PLe and PLs on the river-crossing puzzle states of rivercross-v2 (run rc-state: 43 states,
Opus 5.5 low, v2 prompt). These labels use the rubric texts of 2026-09-30: before PLp text O (2026-10-01) and before the
examples review (2026-10-04). Writes rivercross_levels.csv and rivercross_levels.png.

    python experiments/benchmarks/pl-histograms/plot_rivercross.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
RUN = HERE.parent / "rivercross-v2/labels/rc-state/labels_long.csv"
MODEL = "claude-opus-5-5"
DIMS = ["PLp", "PLe", "PLs"]
LEVELS = np.arange(6)


def main() -> None:
    lab = pd.read_csv(RUN)
    lab = lab[lab["valid"].astype(bool) & lab["writer_model"].astype(str).str.startswith(MODEL)]
    rows = []
    for d in DIMS:
        s = lab[lab["demand"] == d]["level"].astype(int)
        rows += [{"rubric": d, "level": int(k), "tasks": int((s == k).sum()), "n": len(s)} for k in LEVELS]
    t = pd.DataFrame(rows)
    t.to_csv(HERE / "rivercross_levels.csv", index=False)

    fig, axes = plt.subplots(1, len(DIMS), figsize=(10, 3.2), sharey=True)
    for j, d in enumerate(DIMS):
        ax, h = axes[j], t[t["rubric"] == d]
        n = h["n"].iloc[0]
        ax.bar(h["level"], h["tasks"] / n, color=f"C{j}")
        for k, c in zip(h["level"], h["tasks"]):
            if c:
                ax.text(k, c / n + 0.03, str(c), ha="center", fontsize=7)
        ax.set_title(f"{d} (n = {n})")
        ax.set_xticks(list(LEVELS))
        ax.set_xlabel("level")
        ax.set_ylim(0, 1.15)
    axes[0].set_ylabel("share of puzzle states")
    fig.suptitle("River-crossing puzzle states: PL levels (rubric texts of 2026-09-30; counts on bars)", fontsize=10)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(HERE / "rivercross_levels.png", dpi=150)
    print(t.pivot_table(index="rubric", columns="level", values="tasks").to_string())


if __name__ == "__main__":
    main()
