"""PLp, PLe and PLs level counts on the seven agentic benchmarks (clean sets): the labels first shared (each study's
release/labels_wide.csv at cd608bf, before the 2026-10-04 example changes) against the current labels (mass runs
relabel-v2 and relabel-v2-long, under the reviewed examples of d4ec2ec). Writes pl_initial_vs_now.csv and
pl_initial_vs_now.png. Both arms cover the same tasks: those labelled in the initial release.

    python experiments/benchmarks/pl-histograms/plot_initial_vs_now.py
"""

import io
import subprocess
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
BENCH = HERE.parent
ROOT = BENCH.parents[1]
INITIAL = "cd608bf"
RUNS = ["relabel-v2", "relabel-v2-long"]
MODEL = "claude-opus-5-5"
DIMS = ["PLp", "PLe", "PLs"]
LEVELS = np.arange(6)
SETS = {"swebench-clean": ("SWE-bench Verified", "swe-bench-verified"),
        "programbench-pl": ("ProgramBench", "programbench"), "deepswe-clean": ("DeepSWE", "deepswe-v1.1"),
        "frontierswe-pl": ("FrontierSWE", "frontierswe-v2"), "tb4-clean": ("Terminal-Bench 4.0", "terminal-bench-4.0.0"),
        "tbsci-pl": ("TB-Science", "terminal-bench-science-0.1"), "tau2-clean": ("tau2", None)}


def initial(study: str, benchmark: str | None) -> pd.DataFrame:
    text = subprocess.run(["git", "-C", str(ROOT), "show", f"{INITIAL}:experiments/benchmarks/{study}/release/labels_wide.csv"],
                          capture_output=True, text=True, check=True).stdout
    w = pd.read_csv(io.StringIO(text), dtype={"instance_id": str})
    if "keep" in w:
        w = w[w["keep"].astype(bool)]
    if benchmark:
        w = w.assign(benchmark=benchmark)
    return w.melt(id_vars=["benchmark", "instance_id"], value_vars=[f"v2/{d}" for d in DIMS],
                  var_name="rubric_ref", value_name="initial").dropna()


def now() -> pd.DataFrame:
    parts = []
    for run in RUNS:
        lab = pd.read_csv(BENCH / "mass-annotation/runs" / run / "labels.csv", dtype={"instance_id": str})
        lab = lab[lab["valid"].astype(bool) & lab["writer_model"].astype(str).str.startswith(MODEL)]
        parts.append(lab[["benchmark", "instance_id", "rubric_ref", "level"]].rename(columns={"level": "now"}))
    return pd.concat(parts)


def main() -> None:
    new = now()
    rows, both = [], {}
    for study, (name, bench) in SETS.items():
        m = initial(study, bench).merge(new, on=["benchmark", "instance_id", "rubric_ref"], how="left")
        for d in DIMS:
            g = m[m["rubric_ref"] == f"v2/{d}"]
            both[(name, d)] = g.dropna(subset=["now"])
            for arm in ("initial", "now"):
                s = g[arm].dropna().astype(int)
                rows += [{"benchmark": name, "rubric": d, "labels": arm, "level": int(k), "tasks": int((s == k).sum()),
                          "n": len(s)} for k in LEVELS]
    t = pd.DataFrame(rows)
    t.to_csv(HERE / "pl_initial_vs_now.csv", index=False)

    fig, axes = plt.subplots(len(SETS), len(DIMS), figsize=(10, 13), sharex=True, sharey=True)
    for i, (name, _) in enumerate(SETS.values()):
        for j, d in enumerate(DIMS):
            ax = axes[i, j]
            for k, (arm, colour) in enumerate((("initial", "0.6"), ("now", f"C{j}"))):
                h = t[(t["benchmark"] == name) & (t["rubric"] == d) & (t["labels"] == arm)]
                n = h["n"].iloc[0]
                x = LEVELS + (k - 0.5) * 0.4
                ax.bar(x, h["tasks"] / n, width=0.4, color=colour, label=arm)
                for xi, c in zip(x, h["tasks"]):
                    if c:
                        ax.text(xi, c / n + 0.03, str(c), ha="center", fontsize=6)
            g = both[(name, d)]
            same = (g["initial"] == g["now"]).mean()
            ax.set_title(f"{d}: {same:.0%} unchanged" if i else f"{d}\n{same:.0%} unchanged", fontsize=8)
            ax.set_ylim(0, 1.2)
            ax.set_xticks(list(LEVELS))
            if j == 0:
                ax.set_ylabel(f"{name}\n(n = {n})", fontsize=8)
            if i == len(SETS) - 1:
                ax.set_xlabel("level")
    axes[0, 0].legend(fontsize=7, loc="upper right")
    fig.suptitle("PL levels: labels first shared (grey) and now (colour); share of clean tasks, counts on bars",
                 fontsize=10)
    fig.tight_layout()
    fig.savefig(HERE / "pl_initial_vs_now.png", dpi=150)
    print(t.pivot_table(index=["benchmark", "rubric", "labels"], columns="level", values="tasks").to_string())


if __name__ == "__main__":
    main()
