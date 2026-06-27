"""PLe agreement across methods (1a/1b/2) + the 1b demand-to-go gradient.

Reads labels/<method>/{haiku,sonnet,opus}_PLe.csv. Prints per-method agreement
(exact / within-1 / quadratic-weighted kappa / all-3) and, for 1b, the solver
cost-to-go correlation; writes figures/ple_1b_progress.png.
"""
import csv
import itertools
import json
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
PILOT = HERE.parent
REPO = PILOT
while REPO != REPO.parent and not (REPO / "src" / "adele").is_dir():
    REPO = REPO.parent
FIG = PILOT / "figures"
sys.path.insert(0, str(REPO / "src"))
from adele.rivercross import PuzzleSpec, solve  # noqa: E402

MODELS = ["haiku", "sonnet", "opus"]
COLORS = {"haiku": "#e07b39", "sonnet": "#3a7d44", "opus": "#3b5bdb"}
SPECS = json.load(open(PILOT / "specs.json"))


def load(method):
    cols = {}
    for m in MODELS:
        p = HERE / "labels" / method / f"{m}_PLe.csv"
        rows = list(csv.DictReader(p.open()))
        cols[m] = {r["custom_id"]: int(r["level"]) for r in rows}
    ids = list(cols[MODELS[0]])
    return ids, cols


def qwk(a, b, K=6):
    a, b = np.asarray(a, int), np.asarray(b, int)
    O = np.zeros((K, K))
    for x, y in zip(a, b):
        O[x, y] += 1
    w = np.array([[(i - j) ** 2 / (K - 1) ** 2 for j in range(K)] for i in range(K)])
    E = np.outer(O.sum(1), O.sum(0)) / O.sum()
    den = (w * E).sum()
    return float("nan") if den == 0 else 1 - (w * O).sum() / den


def report(method):
    ids, cols = load(method)
    arr = {m: np.array([cols[m][i] for i in ids]) for m in MODELS}
    print(f"\n=== method {method}: {len(ids)} items ===")
    for m in MODELS:
        vc = {int(k): int(v) for k, v in zip(*np.unique(arr[m], return_counts=True))}
        print(f"  {m:7s} mean={arr[m].mean():.2f} dist={vc}")
    for a, b in itertools.combinations(MODELS, 2):
        exact = (arr[a] == arr[b]).mean() * 100
        w1 = (np.abs(arr[a] - arr[b]) <= 1).mean() * 100
        print(f"  {a:6s}-{b:6s} exact={exact:3.0f}% within1={w1:3.0f}% QWK={qwk(arr[a], arr[b]):.2f}")
    all3 = np.mean([len({arr[m][k] for m in MODELS}) == 1 for k in range(len(ids))]) * 100
    print(f"  all-3 identical: {all3:.0f}%")
    return ids, arr


def solver_dist_for_1b(ids):
    """cost-to-go (remaining optimal moves) for each annotated 1b state."""
    cache, dists = {}, {}
    for cid in ids:
        inst, sk = cid.split("#s")
        k = int(sk)
        if inst not in cache:
            spec = PuzzleSpec.from_dict(SPECS[inst])
            sol = solve(spec)
            data = json.load(open(PILOT / "interactive" / f"{inst}.json"))
            cache[inst] = (sol, data)
        sol, data = cache[inst]
        st = data["trajectory"][k]
        state = (frozenset(st["left"]), st["boat"])
        dists[cid] = sol.dist[state]
    return dists


def plot_1b(ids, arr):
    dists = solver_dist_for_1b(ids)
    d = np.array([dists[i] for i in ids])
    print("\n  1b vs solver cost-to-go:")
    for m in MODELS:
        rho, _ = spearmanr(arr[m], d)
        print(f"    {m:7s} Spearman(level, remaining-moves) = {rho:+.2f}")
    # pooled mean level by remaining distance
    xs = sorted(set(d))
    mean = [np.mean([arr[m][k] for m in MODELS for k in range(len(ids)) if d[k] == x]) for x in xs]
    sd = [np.std([arr[m][k] for m in MODELS for k in range(len(ids)) if d[k] == x]) for x in xs]
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    ax.fill_between(xs, np.array(mean) - np.array(sd), np.array(mean) + np.array(sd),
                    alpha=0.18, color="#3b5bdb", label="+/- 1 SD across models")
    ax.plot(xs, mean, "-o", color="#1b2f8a", lw=2.2, ms=6, label="mean PLe-1b (3 models)")
    ax.invert_xaxis()
    ax.set_xlabel("remaining moves to goal (solver cost-to-go)   start = left --> goal = right")
    ax.set_ylabel("annotated PLe level (demand-to-go)")
    ax.set_yticks(range(0, 6))
    ax.set_ylim(-0.3, 5.3)
    ax.set_title("PLe action-control demand falls as execution progresses (method 1b)")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=9)
    fig.tight_layout()
    out = FIG / "ple_1b_progress.png"
    fig.savefig(out, dpi=150)
    print(f"  wrote {out}")


def main():
    ids_1b, arr_1b = report("1b")
    report("2")
    plot_1b(ids_1b, arr_1b)


if __name__ == "__main__":
    main()
