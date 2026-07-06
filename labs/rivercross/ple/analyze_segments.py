"""Cross-model agreement + oracle correlation for the segment (method 2) labels.

Reads labels/seg_multilen/{haiku,sonnet,opus}_{PLp,PLe}.csv and
oracle_PLe_seg_multilen.csv, prints per-model label distributions, pairwise
agreement (exact, within-1, quadratic-weighted kappa) and Spearman correlation
of each model's levels against the solver oracle columns.

No scipy needed: QWK and Spearman are implemented with numpy only.
"""

from __future__ import annotations

import sys
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
STRATEGY = sys.argv[1] if len(sys.argv) > 1 else "multilen"
LABELS = HERE / "labels" / f"seg_{STRATEGY}"
MODELS = ["haiku", "sonnet", "opus"]
DIMS = ["PLp", "PLe"]
ORACLE_COLS = [
    "d_phi", "length", "cost_to_go_start", "min_phi_dip",
    "n_illegal", "n_nonoptimal",
]


def qwk(a: np.ndarray, b: np.ndarray, n_cat: int = 6) -> float:
    """Quadratic-weighted Cohen's kappa on integer labels 0..n_cat-1."""
    obs = np.zeros((n_cat, n_cat))
    for x, y in zip(a, b):
        obs[x, y] += 1
    obs /= obs.sum()
    pa, pb = obs.sum(1), obs.sum(0)
    exp = np.outer(pa, pb)
    w = np.subtract.outer(np.arange(n_cat), np.arange(n_cat)) ** 2 / (n_cat - 1) ** 2
    denom = (w * exp).sum()
    if denom == 0:
        return float("nan")
    return 1 - (w * obs).sum() / denom


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    ra = pd.Series(a).rank().to_numpy()
    rb = pd.Series(b).rank().to_numpy()
    if ra.std() == 0 or rb.std() == 0:
        return float("nan")
    return float(np.corrcoef(ra, rb)[0, 1])


def main() -> None:
    oracle = pd.read_csv(HERE / f"oracle_PLe_seg_{STRATEGY}.csv").set_index("custom_id")
    oracle["n_nonoptimal"] = (
        oracle.n_lateral + oracle.n_backward + oracle.n_fatal + oracle.n_recovering
    )
    for dim in DIMS:
        frames = {}
        for m in MODELS:
            p = LABELS / f"{m}_{dim}.csv"
            if p.exists():
                frames[m] = pd.read_csv(p).set_index("custom_id")["level"]
        if not frames:
            print(f"[{dim}] no label files under {LABELS}")
            continue
        df = pd.DataFrame(frames).join(oracle, how="inner")
        n = len(df)
        print(f"\n=== {dim} (seg_{STRATEGY}, n={n}) ===")
        print("label distributions:")
        for m in frames:
            dist = df[m].value_counts().sort_index().to_dict()
            print(f"  {m:7s} {dist}")
        print("pairwise agreement:")
        for m1, m2 in combinations(frames, 2):
            a, b = df[m1].to_numpy(int), df[m2].to_numpy(int)
            exact = (a == b).mean()
            within1 = (np.abs(a - b) <= 1).mean()
            print(
                f"  {m1}-{m2:7s} exact={exact:.2f} within-1={within1:.2f} "
                f"QWK={qwk(a, b):.2f}"
            )
        if len(frames) == 3:
            all3 = (df[MODELS].nunique(axis=1) == 1).mean()
            print(f"  all-3 exact agreement: {all3:.2f}")
        print("Spearman vs oracle:")
        for col in ORACLE_COLS:
            row = "  " + f"{col:17s}"
            for m in frames:
                row += f" {m}={spearman(df[m].to_numpy(), df[col].to_numpy()):+.2f}"
            print(row)


if __name__ == "__main__":
    main()
