"""Cross-model agreement + sanity checks for the HAL SWE-bench trace pilot.

Reads results/{dim}_{model}_c*.csv and meta_hal.csv. Reports, per dimension and
frame kind (checkpoint / segment): label distributions, pairwise agreement
(exact, within-1, QWK), demand-vs-depth trend, success-vs-failure and
agent-strength contrasts.
"""

from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
MODELS = ["haiku", "sonnet", "opus"]
DIMS = ["PLp", "PLe"]


def qwk(a, b, n_cat=6):
    obs = np.zeros((n_cat, n_cat))
    for x, y in zip(a, b):
        obs[x, y] += 1
    obs /= obs.sum()
    exp = np.outer(obs.sum(1), obs.sum(0))
    w = np.subtract.outer(np.arange(n_cat), np.arange(n_cat)) ** 2 / (n_cat - 1) ** 2
    d = (w * exp).sum()
    return float("nan") if d == 0 else 1 - (w * obs).sum() / d


def spearman(a, b):
    ra, rb = pd.Series(a).rank(), pd.Series(b).rank()
    if ra.std() == 0 or rb.std() == 0:
        return float("nan")
    return float(np.corrcoef(ra, rb)[0, 1])


meta = pd.read_csv(HERE / "meta_hal.csv").set_index("custom_id")
for dim in DIMS:
    frames = {}
    for m in MODELS:
        parts = sorted((HERE / "results").glob(f"{dim}_{m}_c*.csv"))
        s = pd.concat(
            [pd.read_csv(p, header=None, names=["custom_id", "level"]) for p in parts]
        ).set_index("custom_id")["level"]
        frames[m] = s
    df = pd.DataFrame(frames).join(meta, how="inner")
    print(f"\n================ {dim} (n={len(df)}) ================")
    for kind, sub in df.groupby("kind"):
        print(f"\n-- {kind} frames (n={len(sub)}) --")
        for m in MODELS:
            print(f"  {m:7s} dist: {sub[m].value_counts().sort_index().to_dict()}")
        for m1, m2 in combinations(MODELS, 2):
            a, b = sub[m1].to_numpy(int), sub[m2].to_numpy(int)
            print(
                f"  {m1}-{m2:7s} exact={(a==b).mean():.2f} "
                f"within-1={(np.abs(a-b)<=1).mean():.2f} QWK={qwk(a,b):.2f}"
            )
        print(f"  all-3 exact: {(sub[MODELS].nunique(axis=1)==1).mean():.2f}")

    cp = df[df.kind == "cp"]
    print("\n-- demand-to-go vs depth (checkpoints; expect negative) --")
    for m in MODELS:
        print(f"  {m}: Spearman(level, depth_frac) = {spearman(cp[m], cp.depth_frac):+.2f}")
    print("\n-- mean checkpoint demand-to-go by depth --")
    print(cp.groupby(cp.depth_frac.round(1))[MODELS].mean().round(2).to_string())
    print("\n-- opus41 runs: success vs failure, mean cp demand at 50%+75% --")
    late = cp[(cp.agent == "opus41") & (cp.depth_frac >= 0.5)]
    print(late.groupby("success")[MODELS].mean().round(2).to_string())
    print("\n-- same tasks, strong vs weak agent (matched 4 tasks), mean cp demand --")
    both = cp[cp.task.isin(cp[cp.agent == "o3mini"].task.unique())]
    print(both.groupby("agent")[MODELS].mean().round(2).to_string())
