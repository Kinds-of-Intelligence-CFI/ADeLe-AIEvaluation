"""Agreement stats + plots for the PLp method-1b annotation.

Reads labels_<version>/{haiku,sonnet,opus}_PLp.csv and ground_truth.csv, prints a
cross-model agreement report (pairwise exact / within-1 / quadratic-weighted kappa,
all-3 agreement, Spearman vs the solver's remaining horizon), and regenerates:
  figures/plp_vs_distance.png  - per-model annotated level vs remaining crossings
  figures/plp_progress.png     - pooled mean demand as the task progresses

Usage: python analyze_plp.py [version]   (default version: v11)
"""
import sys
import itertools
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
PILOT = HERE.parent
FIG = PILOT / "figures"
MODELS = ["haiku", "sonnet", "opus", "gpt", "gemini-flash"]
COLORS = {"haiku": "#e07b39", "sonnet": "#3a7d44", "opus": "#3b5bdb",
          "gpt": "#8e44ad", "gemini-flash": "#7f8c8d"}
GT = pd.read_csv(HERE / "ground_truth.csv").set_index("custom_id")


def load(version):
    cols = {}
    for m in MODELS:
        p = HERE / f"labels_{version}" / f"{m}_PLp.csv"
        if p.exists():
            df = pd.read_csv(p)
            cols[m] = df.set_index("custom_id")["level"].astype(int)
    if not cols:
        return None
    out = pd.DataFrame(cols)
    out["dist"] = GT["dist_to_goal"].reindex(out.index)
    return out


def qwk(a, b, K=6):
    a, b = np.asarray(a, int), np.asarray(b, int)
    O = np.zeros((K, K))
    for x, y in zip(a, b):
        O[x, y] += 1
    w = np.array([[(i - j) ** 2 / (K - 1) ** 2 for j in range(K)] for i in range(K)])
    E = np.outer(O.sum(1), O.sum(0)) / O.sum()
    denom = (w * E).sum()
    return float("nan") if denom == 0 else 1 - (w * O).sum() / denom


def report(df, tag):
    present = [m for m in MODELS if m in df.columns]
    print(f"\n=== {tag}: {len(df)} states | models: {', '.join(present)} ===")
    print("per-model level distribution:")
    for m in present:
        vc = df[m].value_counts().sort_index().to_dict()
        print(f"  {m:7s}  mean={df[m].mean():.2f}  {vc}")
    if len(present) >= 2:
        print("pairwise agreement:")
        for a, b in itertools.combinations(present, 2):
            exact = (df[a] == df[b]).mean() * 100
            w1 = (abs(df[a] - df[b]) <= 1).mean() * 100
            print(f"  {a:6s}-{b:6s}  exact={exact:3.0f}%  within1={w1:3.0f}%  QWK={qwk(df[a], df[b]):.2f}")
    if len(present) >= 3:
        all_same = (df[present].nunique(axis=1) == 1).mean() * 100
        print(f"all-{len(present)} identical: {all_same:.0f}%")
    print("vs solver remaining horizon (dist_to_goal):")
    for m in present:
        rho, _ = spearmanr(df[m], df["dist"])
        print(f"  {m:7s}  Spearman(level, dist) = {rho:+.2f}")
    return present


def plot_vs_distance(df, present, version):
    rng = np.random.default_rng(0)
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    for m in present:
        jx = df["dist"] + rng.uniform(-0.12, 0.12, len(df))
        jy = df[m] + rng.uniform(-0.06, 0.06, len(df))
        rho, _ = spearmanr(df[m], df["dist"])
        ax.scatter(jx, jy, s=34, alpha=0.55, color=COLORS[m],
                   label=f"{m}  (rho={rho:+.2f})", edgecolors="none")
    # mean level per distance across all model labels
    long = df.melt(id_vars="dist", value_vars=present, value_name="level")
    mean_by_d = long.groupby("dist")["level"].mean()
    ax.plot(mean_by_d.index, mean_by_d.values, "k-o", lw=2, ms=5,
            label="mean (all models)", zorder=5)
    ax.set_xlabel("remaining crossings to goal  (solver dist_to_goal)")
    ax.set_ylabel("annotated PLp level")
    ax.set_yticks(range(0, 6))
    ax.set_title(f"PLp annotation vs remaining search depth ({version}, revised rubric)")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8, loc="upper left")
    fig.tight_layout()
    out = FIG / "plp_vs_distance.png"
    fig.savefig(out, dpi=150)
    print(f"wrote {out}")


def plot_progress(df, present, version):
    """Pooled annotated demand as the task progresses (remaining horizon -> 0)."""
    long = df.melt(id_vars="dist", value_vars=present, value_name="level")
    g = long.groupby("dist")["level"]
    dists = sorted(long["dist"].unique())
    mean = g.mean().reindex(dists)
    sd = g.std().reindex(dists).fillna(0)
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    ax.fill_between(dists, mean - sd, mean + sd, alpha=0.18, color="#3b5bdb",
                    label="+/- 1 SD across model x state")
    ax.plot(dists, mean, "-o", color="#1b2f8a", lw=2.2, ms=6, label="mean annotated PLp")
    ax.invert_xaxis()  # high dist (start) on left, low dist (near goal) on right
    ax.set_xlabel("crossings remaining   (start = left  -->  goal = right; task progresses -->)")
    ax.set_ylabel("annotated PLp level")
    ax.set_yticks(range(0, 6))
    ax.set_ylim(-0.3, 5.3)
    ax.set_title(f"Planning demand falls as the task progresses ({version}, revised rubric)")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=9, loc="upper right")
    fig.tight_layout()
    out = FIG / "plp_progress.png"
    fig.savefig(out, dpi=150)
    print(f"wrote {out}")


def main():
    version = sys.argv[1] if len(sys.argv) > 1 else "v11"
    df = load(version)
    if df is None:
        sys.exit(f"no labels found under labels_{version}/")
    present = report(df, f"{version} (revised search-size rubric)")
    old = load("v10")
    if old is not None:
        print("\n--- comparison: v10 (previous strict-gated run, old rubric) ---")
        report(old, "v10 (old rubric)")
    plot_vs_distance(df, present, version)
    plot_progress(df, present, version)


if __name__ == "__main__":
    main()
