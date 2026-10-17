"""Phase C analysis of spv-v2 (decision rule in phaseC/PREREGISTRATION_C.md): SPv against ZeroBench solve rates.

Solve rate of a question = mean over the 67 leaderboard models of (correct samples / 5), from the matrix decoded from
zerobench.github.io (data/downloads/zerobench/site/matrix.csv, gitignored). Primary set: the 77 questions solved at
least once (the project's clean-set rule). Only answers written by claude-opus-5-5 count.

    python experiments/benchmarks/spv-v2/analysis/analyse_c.py
"""

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[2]
MATRIX = ROOT / "data/downloads/zerobench/site/matrix.csv"
FIRST_RECENT = "Claude Opus 4.6"  # rows from here on are the 2026 releases on the leaderboard


def med(s: pd.Series) -> int:
    v = sorted(int(x) for x in s)
    return v[(len(v) - 1) // 2]


def partial(x: pd.Series, y: pd.Series, z: pd.DataFrame) -> float:
    """Spearman partial correlation of x and y given z (rank, regress out, correlate residuals)."""
    r = lambda s: s.rank().to_numpy(float)  # noqa: E731
    Z = np.column_stack([np.ones(len(x))] + [r(z[c]) for c in z])
    res = [a - Z @ np.linalg.lstsq(Z, a, rcond=None)[0] for a in (r(x), r(y))]
    return float(np.corrcoef(*res)[0, 1])


def boot_diff(a: pd.Series, b: pd.Series, y: pd.Series, n: int = 5000, seed: int = 0) -> tuple[float, float]:
    rng, idx, out = np.random.default_rng(seed), np.arange(len(y)), []
    for _ in range(n):
        s = rng.choice(idx, len(idx))
        out.append(spearmanr(a.iloc[s], y.iloc[s]).statistic - spearmanr(b.iloc[s], y.iloc[s]).statistic)
    return tuple(np.nanpercentile(out, [2.5, 97.5]))


def main() -> None:
    d = pd.read_csv(HERE / "labels/spv2-c/labels_long.csv", dtype={"item_id": str})
    d = d[(d.writer_model == "claude-opus-5-5") & d.valid]
    lv = d.groupby(["item_id", "arm"])["level"].agg(med).unstack()
    M = pd.read_csv(MATRIX, index_col=0)
    rate = (M / 5).mean().rename("rate")
    recent = (M.loc[M.index[list(M.index).index(FIRST_RECENT):]] / 5).mean().rename("rate_recent")
    meta = pd.read_csv(HERE / "labels/spv2-c/question_meta.csv", dtype={"question_id": str}).set_index("question_id")
    t = lv.join(rate).join(recent).join(meta)
    t.index = t.index.astype(str)
    solved = t[(M.sum() > 0).reindex(t.index).to_numpy()]

    print(f"labels: {len(d)} | questions labelled: {len(lv)} | solved at least once: {len(solved)}")
    for arm in ("cur", "cand"):
        print(f"\n[{arm}] level counts (all 100): {t[arm].value_counts().sort_index().to_dict()}")
        for name, s in (("solved 77", solved), ("all 100", t)):
            r = spearmanr(s[arm], s.rate)
            print(f"  {name}: rho {r.statistic:+.2f} (two-sided p {r.pvalue:.3f}); "
                  f"recent models rho {spearmanr(s[arm], s.rate_recent).statistic:+.2f}")
        print(f"  solved 77, partial given question length and image count: "
              f"{partial(solved[arm], solved.rate, solved[['question_chars', 'n_images']]):+.2f}")
    r = spearmanr(solved.cand, solved.rate)
    lo, hi = boot_diff(solved.cand, solved.cur, solved.rate)
    print(f"\ncand minus cur rho (solved 77), 95% bootstrap CI: [{lo:+.2f}, {hi:+.2f}]")
    rep = d.pivot_table(index=["item_id", "arm"], columns="repeat", values="level")
    print(f"repeat agreement (same level on both repeats): {(rep[1] == rep[2]).mean():.0%}")
    one_sided = r.pvalue / 2 if r.statistic < 0 else 1 - r.pvalue / 2
    ok = r.statistic <= -0.2 and one_sided < 0.05
    print(f"\nPRIMARY (cand, solved 77): rho {r.statistic:+.2f}, one-sided p {one_sided:.3f} -> "
          f"{'SUPPORTED' if ok else 'NOT SUPPORTED'}")


if __name__ == "__main__":
    main()
