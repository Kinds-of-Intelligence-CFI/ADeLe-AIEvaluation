"""Exploratory review of Sonnet-Opus agreement in swebench-30 (NOT pre-registered; added
2026-09-27 after the pre-registered analysis ran).

For every rubric on which both judges vary, on the 30 new tasks: the Sonnet x Opus level
crosstab, the rank agreement (Spearman), and the boundary where one judge is systematically
a level higher. Then Volume against SWE-bench's human time-to-fix bucket for each judge, as an
external referee for that rubric. Writes results/exploratory.json.

    python experiments/benchmarks/swebench-30/analysis/exploratory.py
"""

import json
from pathlib import Path

import pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parents[1]
BUCKETS = ["<15 min fix", "15 min - 1 hour", "1-4 hours", ">4 hours"]


def main() -> None:
    labels = pd.read_csv(HERE / "labels/swev30-r4/labels_long.csv")
    sample = pd.read_csv(HERE / "sample.csv").set_index("instance_id")
    new = sample[sample["role"] == "new"]
    wide = (labels[labels["instance_id"].isin(new.index)]
            .pivot_table(index=["instance_id", "demand"], columns="judge", values="level"))

    rubrics = {}
    for d in sorted(wide.index.get_level_values("demand").unique()):
        x = wide.xs(d, level="demand")
        if x["sonnet"].nunique() < 2 and x["opus"].nunique() < 2:
            continue
        ct = pd.crosstab(x["sonnet"].astype(int), x["opus"].astype(int))
        higher = (x["sonnet"] > x["opus"]).sum(), (x["opus"] > x["sonnet"]).sum()
        pairs = x.loc[x["sonnet"] != x["opus"], ["sonnet", "opus"]].astype(int).value_counts().head(1)
        rubrics[d] = {
            "spearman_sonnet_opus": round(float(spearmanr(x["sonnet"], x["opus"])[0]), 2)
            if x["sonnet"].nunique() > 1 and x["opus"].nunique() > 1 else None,
            "tasks_sonnet_higher": int(higher[0]), "tasks_opus_higher": int(higher[1]),
            "most_common_split_sonnet_opus": [int(v) for v in pairs.index[0]] if len(pairs) else None,
            "most_common_split_tasks": int(pairs.iloc[0]) if len(pairs) else 0,
            "crosstab_rows_sonnet_cols_opus": {int(s): {int(o): int(n) for o, n in row.items() if n}
                                               for s, row in ct.iterrows()},
        }

    vo = wide.xs("VO", level="demand").join(new["difficulty"])
    ttf = vo["difficulty"].map({b: i for i, b in enumerate(BUCKETS)})
    volume = {j: {"spearman_vs_time_to_fix": round(float(spearmanr(vo[j], ttf)[0]), 2),
                  "levels_by_bucket": {b: {int(k): int(v) for k, v in g[j].value_counts().sort_index().items()}
                                       for b, g in vo.groupby("difficulty")}}
              for j in ["sonnet", "opus"]}

    out = {"n_tasks": len(new), "rubrics_where_a_judge_varies": rubrics, "volume_vs_time_to_fix": volume}
    (HERE / "results/exploratory.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
