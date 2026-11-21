"""Inter-rubric correlations, as in the paper's Figure 4 (arXiv:2503.06378, §3.1).

The paper computes the Spearman correlation of demand levels between every pair of dimensions, over all battery
items, and reads the matrix. We do the same:
1. GPT-4o, full battery (16,108 items, 18 rubrics + UG): a check that we reproduce Figure 4.
2. GPT-4o and Opus (arms A and B) on the 60 bridge items: the same matrix per judge. Summaries:
   mean ρ and mean |ρ| over pairs, the share of variance on the first eigenvector (a general factor), how alike
   the matrices are, and a bootstrap over items.
3. A spread check: Opus's levels spread less than GPT-4o's. We map GPT-4o's levels onto Opus's per-rubric level
   distribution (quantile matching, GPT-4o's item order kept) and recompute. If the summaries stay put, the lower
   spread does not explain the lower correlations.

Rubrics a judge holds constant on these items (Opus A gives CEe 0 everywhere) are dropped for every judge.

Run: .venv/bin/python experiments/benchmarks/v1-prompt-bridge/inter_rubric.py
Writes inter_rubric.json and inter_rubric.png next to this file (correlations only, no task text).
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).parent
REPO = HERE.parents[2]
RUNS = HERE.parent / "mass-annotation" / "runs"
# Paper order (Figure 4 groups by broad capability).
RUBRICS = ["AS", "CEc", "CEe", "CL", "MCr", "MCt", "MCu", "MSm", "QLl", "QLq", "SNs",
           "KNa", "KNc", "KNf", "KNn", "KNs", "AT", "VO"]
ARMS = {"Opus A (production)": "gate-v1-bridge-h", "Opus B (paper prompt)": "gate-v1-bridge-pub"}
N_BOOT = 2000


def spearman(df: pd.DataFrame) -> pd.DataFrame:
    return df.rank().corr()  # Spearman = Pearson on ranks


def off_diag(m: pd.DataFrame) -> np.ndarray:
    return m.to_numpy()[np.triu_indices(len(m), k=1)]


def summary(df: pd.DataFrame) -> dict[str, float]:
    m = spearman(df)
    v = off_diag(m)
    return {"mean_rho": np.nanmean(v), "mean_abs_rho": np.nanmean(np.abs(v)),
            "first_eigen_share": np.linalg.eigvalsh(m.fillna(0).to_numpy())[-1] / len(m)}


def quantile_match(src: pd.DataFrame, tgt: pd.DataFrame) -> pd.DataFrame:
    """src's item order per rubric, tgt's level distribution."""
    q = src.rank(method="first") / len(src)
    return pd.DataFrame({c: np.quantile(tgt[c], q[c], method="inverted_cdf") for c in src}, index=src.index)


def judge_labels(run: str) -> pd.DataFrame:
    df = pd.read_csv(RUNS / run / "labels.csv", dtype={"instance_id": str})
    df = df[df["valid"]]
    df["rubric"] = df["rubric_ref"].str.removeprefix("v1/")
    return df.pivot_table(index="instance_id", columns="rubric", values="level", aggfunc="first")[RUBRICS]


def r3(x) -> float | list[float]:
    return [round(float(v), 3) for v in x] if np.ndim(x) else round(float(x), 3)


def main() -> None:
    battery = pd.read_csv(REPO / "data" / "downloads" / "battery-v1" / "ADeLe_batterry_v1dot0.csv",
                          usecols=["instance_id", "UG", *[r if r != "MSm" else "MS" for r in RUBRICS]])
    battery = battery.rename(columns={"MS": "MSm"}).set_index("instance_id")
    full = spearman(battery[RUBRICS + ["UG"]])

    ref = pd.read_csv(REPO / "data" / "instances" / "v1_bridge_reference.csv", dtype={"instance_id": str})
    judges = {"GPT-4o": ref.set_index("instance_id")[RUBRICS]}
    judges |= {name: judge_labels(run) for name, run in ARMS.items()}
    items = sorted(set.intersection(*(set(j.dropna().index) for j in judges.values())))
    cols = [c for c in RUBRICS if all(j.loc[items, c].nunique() > 1 for j in judges.values())]
    judges = {k: v.loc[items, cols] for k, v in judges.items()}

    rng = np.random.default_rng(0)
    boots = [rng.integers(0, len(items), len(items)) for _ in range(N_BOOT)]
    boot = {k: [summary(v.iloc[b]) for b in boots] for k, v in judges.items()}
    point = {k: summary(v) for k, v in judges.items()}
    g = off_diag(spearman(judges["GPT-4o"]))

    out = {
        "n_items": len(items), "rubrics": cols,
        "battery_full": {"n_items": len(battery), **{k: r3(v) for k, v in summary(battery[RUBRICS]).items()},
                         "pairs_above_0.8": [(a, b, r3(full.loc[a, b])) for i, a in enumerate(full)
                                             for b in list(full)[i + 1:] if full.loc[a, b] > 0.8]},
        "gpt4o_60_vs_full_matrix_r": r3(np.corrcoef(g, off_diag(full.loc[cols, cols]))[0, 1]),
        "judges": {},
    }
    for name, df in judges.items():
        e = {"sd_per_rubric": {c: r3(df[c].std()) for c in cols}}
        for k, v in point[name].items():
            e[k] = r3(v)
            e[f"{k}_ci95"] = r3(np.percentile([b[k] for b in boot[name]], [2.5, 97.5]))
            if name != "GPT-4o":
                e[f"gpt4o_minus_this_{k}"] = r3(point["GPT-4o"][k] - v)
                e[f"gpt4o_minus_this_{k}_ci95"] = r3(np.percentile(
                    [a[k] - b[k] for a, b in zip(boot["GPT-4o"], boot[name])], [2.5, 97.5]))
        if name != "GPT-4o":
            o = off_diag(spearman(df))
            e["matrix_r_vs_gpt4o"] = r3(np.corrcoef(g, o)[0, 1])
            e["pairs_gpt4o_higher"] = f"{int((g > o).sum())}/{len(g)}"
            e["gpt4o_squeezed_to_this_spread"] = {
                k: r3(v) for k, v in summary(quantile_match(judges["GPT-4o"], df)).items()}
        out["judges"][name] = e
    (HERE / "inter_rubric.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k != "judges"}, indent=2))
    for name, e in out["judges"].items():
        print(name, {k: v for k, v in e.items() if k != "sd_per_rubric"})

    panels = {"GPT-4o, full battery (16,108)": full.loc[RUBRICS, RUBRICS]}
    panels |= {f"{k}, 60 items": spearman(v).reindex(index=RUBRICS, columns=RUBRICS) for k, v in judges.items()}
    fig, axes = plt.subplots(1, 4, figsize=(28, 7.5))
    for ax, (title, m) in zip(axes, panels.items()):
        im = ax.imshow(m.to_numpy(), cmap="RdBu_r", vmin=-1, vmax=1)
        ax.set_xticks(range(len(RUBRICS)), RUBRICS, rotation=90)
        ax.set_yticks(range(len(RUBRICS)), RUBRICS)
        ax.set_title(title)
    fig.colorbar(im, ax=axes, shrink=0.8, label="Spearman ρ (blank: rubric constant for a judge, dropped)")
    fig.savefig(HERE / "inter_rubric.png", dpi=110, bbox_inches="tight")


if __name__ == "__main__":
    main()
