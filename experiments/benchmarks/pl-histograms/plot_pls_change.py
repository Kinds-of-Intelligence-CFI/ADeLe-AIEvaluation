"""PLs level counts before and after the 2026-10-04 example change, per benchmark (clean sets). Writes
pls_old_new.png from ../pls-relabel/results/analysis.json (old: the released labels at cd608bf; new: the relabel).

    python experiments/benchmarks/pl-histograms/plot_pls_change.py
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
SETS = {"swe-bench-verified": "SWE-bench Verified", "programbench": "ProgramBench", "deepswe-v1.1": "DeepSWE",
        "frontierswe-v2": "FrontierSWE", "terminal-bench-4.0.0": "Terminal-Bench 4.0",
        "terminal-bench-science-0.1": "TB-Science", "tau2": "tau2"}
LEVELS = np.arange(6)


def main() -> None:
    res = json.loads((HERE.parent / "pls-relabel/results/analysis.json").read_text())
    fig, axes = plt.subplots(len(SETS), 1, figsize=(6, 12), sharex=True)
    for ax, (key, name) in zip(axes, SETS.items()):
        for k, (arm, colour) in enumerate((("old", "0.6"), ("new", "C2"))):
            counts = np.array([res["levels"][key][arm].get(str(lv), 0) for lv in LEVELS])
            n = counts.sum()
            x = LEVELS + (k - 0.5) * 0.38
            ax.bar(x, counts / n, width=0.38, color=colour, label=f"{arm} text")
            for xi, c in zip(x, counts):
                if c:
                    ax.text(xi, c / n + 0.03, str(c), ha="center", fontsize=7)
        ax.set_ylim(0, 1.2)
        ax.set_ylabel(f"{name}\n(n = {n})", fontsize=8)
        rho = {arm: res["spearman"][key][arm] for arm in ("old", "new")}
        rho = {arm: r.get("combined", r).get("rho") for arm, r in rho.items()}
        ax.set_title(f"ρ with solve rate: {rho['old']:+.2f} → {rho['new']:+.2f}", fontsize=8, loc="right")
    axes[0].legend(fontsize=8, loc="upper left")
    axes[-1].set_xticks(LEVELS)
    axes[-1].set_xlabel("PLs level")
    fig.suptitle("PLs before and after the computer-world examples (share of tasks; counts on bars)", fontsize=10)
    fig.tight_layout()
    fig.savefig(HERE / "pls_old_new.png", dpi=150)


if __name__ == "__main__":
    main()
