"""Cross-family (GPT-5) supplement to the PLp/PLe judge-agreement pilots.

The PLp/PLe pipelines (analyze_plp.py / analyze_ple.py), their Claude-panel
labels, and the original figures are the reference results and are NOT
touched here. This script reads the Claude label files read-only, adds the
supplementary GPT-5 labels (gpt_PLp.csv / gpt_PLe.csv stored alongside the
Claude labels, like the unused gemini-flash labels in labels_v10), and
writes its own reports and figures next to the originals under distinct
names, so the original experiment stays exactly as the Claude-panel run
produced it.

Outputs:
  method1b/plp_cross_family.txt, ple/ple_cross_family.txt  - agreement reports
  figures/plp_vs_distance_cross_family.png   - PLp scatter, GPT-5 overlaid
  figures/ple_1b_progress_cross_family.png   - PLe-1b gradient, GPT-5 overlaid

In the figures the black/blue mean lines are computed from the Claude panel
only (matching the original figures); GPT-5 is drawn as a separate series
(purple triangles) and never enters the pooled statistics.
"""

import io
import itertools
import json
from contextlib import redirect_stdout
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import spearmanr

RIVERCROSS = Path(__file__).resolve().parent
FIG = RIVERCROSS / "figures"
from adele.testbeds.rivercross import PuzzleSpec, solve  # noqa: E402

CLAUDE_MODELS = ["haiku", "sonnet", "opus"]
COLORS = {"haiku": "#e07b39", "sonnet": "#3a7d44", "opus": "#3b5bdb", "gpt": "#8e44ad"}
GPT = "gpt"
SPECS = json.load(open(RIVERCROSS / "specs.json"))


def qwk(a, b, K=6):
    a, b = np.asarray(a, int), np.asarray(b, int)
    O = np.zeros((K, K))
    for x, y in zip(a, b):
        O[x, y] += 1
    w = np.array([[(i - j) ** 2 / (K - 1) ** 2 for j in range(K)] for i in range(K)])
    E = np.outer(O.sum(1), O.sum(0)) / O.sum()
    den = (w * E).sum()
    return float("nan") if den == 0 else 1 - (w * O).sum() / den


def agreement_report(df, models, tag):
    print(f"\n=== {tag}: {len(df)} items | models: {', '.join(models)} ===")
    for m in models:
        vc = df[m].value_counts().sort_index().to_dict()
        print(f"  {m:7s} mean={df[m].mean():.2f} dist={vc}")
    for a, b in itertools.combinations(models, 2):
        exact = (df[a] == df[b]).mean() * 100
        w1 = (abs(df[a] - df[b]) <= 1).mean() * 100
        print(f"  {a:6s}-{b:6s} exact={exact:3.0f}% within1={w1:3.0f}% QWK={qwk(df[a], df[b]):.2f}")
    all_same = (df[models].nunique(axis=1) == 1).mean() * 100
    print(f"  all-{len(models)} identical: {all_same:.0f}%")


def load_plp(version="v11"):
    cols = {
        m: pd.read_csv(RIVERCROSS / "method1b" / f"labels_{version}" / f"{m}_PLp.csv")
        .set_index("custom_id")["level"].astype(int)
        for m in CLAUDE_MODELS
    }
    cols[GPT] = (
        pd.read_csv(RIVERCROSS / "method1b" / f"labels_{version}" / "gpt_PLp.csv")
        .set_index("custom_id")["level"].astype(int)
    )
    df = pd.DataFrame(cols)
    gt = pd.read_csv(RIVERCROSS / "method1b" / "ground_truth.csv").set_index("custom_id")
    df["dist"] = gt["dist_to_goal"].reindex(df.index)
    return df


def load_ple(method):
    cols = {
        m: pd.read_csv(RIVERCROSS / "ple" / "labels" / method / f"{m}_PLe.csv")
        .set_index("custom_id")["level"].astype(int)
        for m in CLAUDE_MODELS
    }
    cols[GPT] = (
        pd.read_csv(RIVERCROSS / "ple" / "labels" / method / "gpt_PLe.csv")
        .set_index("custom_id")["level"].astype(int)
    )
    return pd.DataFrame(cols)


def ple_1b_dist(ids):
    cache, dists = {}, {}
    for cid in ids:
        inst, sk = cid.split("#s")
        if inst not in cache:
            spec = PuzzleSpec.from_dict(SPECS[inst])
            data = json.load(open(RIVERCROSS / "interactive" / f"{inst}.json"))
            cache[inst] = (solve(spec), data)
        sol, data = cache[inst]
        st = data["trajectory"][int(sk)]
        dists[cid] = sol.dist[(frozenset(st["left"]), st["boat"])]
    return dists


def plot_plp(df, version="v11"):
    rng = np.random.default_rng(0)
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    for m in CLAUDE_MODELS:
        jx = df["dist"] + rng.uniform(-0.12, 0.12, len(df))
        jy = df[m] + rng.uniform(-0.06, 0.06, len(df))
        rho, _ = spearmanr(df[m], df["dist"])
        ax.scatter(jx, jy, s=34, alpha=0.55, color=COLORS[m],
                   label=f"{m}  (rho={rho:+.2f})", edgecolors="none")
    jx = df["dist"] + rng.uniform(-0.12, 0.12, len(df))
    jy = df[GPT] + rng.uniform(-0.06, 0.06, len(df))
    rho, _ = spearmanr(df[GPT], df["dist"])
    ax.scatter(jx, jy, s=44, alpha=0.8, color=COLORS[GPT], marker="^",
               label=f"gpt-5  (rho={rho:+.2f}, supplement)", edgecolors="none")
    claude_long = df.melt(id_vars="dist", value_vars=CLAUDE_MODELS, value_name="level")
    mean_by_d = claude_long.groupby("dist")["level"].mean()
    ax.plot(mean_by_d.index, mean_by_d.values, "k-o", lw=2, ms=5,
            label="mean (Claude panel)", zorder=5)
    ax.set_xlabel("remaining crossings to goal  (solver dist_to_goal)")
    ax.set_ylabel("annotated PLp level")
    ax.set_yticks(range(0, 6))
    ax.set_title(f"PLp annotation vs remaining search depth ({version}) + GPT-5 supplement")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8, loc="upper left")
    fig.tight_layout()
    out = FIG / "plp_vs_distance_cross_family.png"
    fig.savefig(out, dpi=150)
    print(f"wrote {out.relative_to(RIVERCROSS)}")


def plot_ple_1b(df):
    dists = ple_1b_dist(list(df.index))
    d = np.array([dists[i] for i in df.index])
    xs = sorted(set(d))
    claude = df[CLAUDE_MODELS].to_numpy()
    mean = [claude[d == x].mean() for x in xs]
    sd = [claude[d == x].std() for x in xs]
    gpt_mean = [df[GPT].to_numpy()[d == x].mean() for x in xs]
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    ax.fill_between(xs, np.array(mean) - np.array(sd), np.array(mean) + np.array(sd),
                    alpha=0.18, color="#3b5bdb", label="+/- 1 SD across Claude panel")
    ax.plot(xs, mean, "-o", color="#1b2f8a", lw=2.2, ms=6, label="mean PLe-1b (Claude panel)")
    ax.plot(xs, gpt_mean, "-^", color=COLORS[GPT], lw=2.0, ms=7,
            label="mean PLe-1b (gpt-5, supplement)")
    ax.invert_xaxis()
    ax.set_xlabel("remaining moves to goal (solver cost-to-go)   start = left --> goal = right")
    ax.set_ylabel("annotated PLe level (demand-to-go)")
    ax.set_yticks(range(0, 6))
    ax.set_ylim(-0.3, 5.3)
    ax.set_title("PLe demand-to-go gradient (method 1b) + GPT-5 supplement")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=9)
    fig.tight_layout()
    out = FIG / "ple_1b_progress_cross_family.png"
    fig.savefig(out, dpi=150)
    print(f"wrote {out.relative_to(RIVERCROSS)}")


def main():
    FIG.mkdir(exist_ok=True)
    models = [*CLAUDE_MODELS, GPT]

    plp = load_plp()
    buf = io.StringIO()
    with redirect_stdout(buf):
        print("# Generated by: python experiments/rivercross/analyze_cross_family.py")
        print("# GPT-5 supplement; Claude labels read from the original pipelines, unmodified.")
        agreement_report(plp, models, "PLp v11")
        print("\nvs solver remaining horizon (dist_to_goal):")
        for m in models:
            rho, _ = spearmanr(plp[m], plp["dist"])
            print(f"  {m:7s} Spearman(level, dist) = {rho:+.2f}")
    (RIVERCROSS / "method1b" / "plp_cross_family.txt").write_text(buf.getvalue(), encoding="utf-8")
    print(buf.getvalue())

    buf = io.StringIO()
    with redirect_stdout(buf):
        print("# Generated by: python experiments/rivercross/analyze_cross_family.py")
        print("# GPT-5 supplement; Claude labels read from the original pipelines, unmodified.")
        ple_1b = load_ple("1b")
        agreement_report(ple_1b, models, "PLe method 1b")
        dists = ple_1b_dist(list(ple_1b.index))
        d = np.array([dists[i] for i in ple_1b.index])
        print("\n  1b vs solver cost-to-go:")
        for m in models:
            rho, _ = spearmanr(ple_1b[m], d)
            print(f"    {m:7s} Spearman(level, remaining-moves) = {rho:+.2f}")
        agreement_report(load_ple("2"), models, "PLe method 2")
    (RIVERCROSS / "ple" / "ple_cross_family.txt").write_text(buf.getvalue(), encoding="utf-8")
    print(buf.getvalue())

    plot_plp(plp)
    plot_ple_1b(ple_1b)


if __name__ == "__main__":
    main()
