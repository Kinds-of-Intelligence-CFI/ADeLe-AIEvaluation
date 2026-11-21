"""prompt-ablation (README.md): the level change of each one-step prompt change, against re-judging noise.

    python experiments/benchmarks/prompt-ablation/analyse.py
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "mass-annotation"))
from analyse_gates import valid  # noqa: E402

RUBRICS = ["v1/AS", "v1/CEc", "v1/CL", "v1/KNa", "v1/KNc", "v1/MCt", "v1/MCu", "v1/QLq"]
ARMS = {"A": "gate-v1-bridge-h", "A2": "abl-a2", "S1": "abl-s1", "S2": "abl-s2", "S3": "abl-s3",
        "B": "gate-v1-bridge-pub"}
STEPS = [("noise (A' - A)", "A2", "A"), ("tie rule (S1 - A)", "S1", "A"), ("length clause (S2 - S1)", "S2", "S1"),
         ("layout (S3 - S2)", "S3", "S2"), ("reasoning (B - S3)", "B", "S3"), ("all (B - A)", "B", "A")]


def levels() -> pd.DataFrame:
    """One column per arm: the level of each (instance, rubric) cell the arms share."""
    cols = []
    for arm, run in ARMS.items():
        df, _ = valid(run)
        df = df[df["rubric_ref"].isin(RUBRICS)].set_index(["instance_id", "rubric_ref"])["level"].rename(arm)
        cols.append(df)
    return pd.concat(cols, axis=1, join="inner")


def boot_ci(diff: pd.Series, n: int = 5000, seed: int = 20261102) -> tuple:
    """95% CI of the mean change, resampling items (all of an item's rubrics together)."""
    per_item = diff.groupby(level="instance_id").agg(["sum", "size"])
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(per_item), size=(n, len(per_item)))
    means = per_item["sum"].values[idx].sum(1) / per_item["size"].values[idx].sum(1)
    return np.percentile(means, [2.5, 97.5])


def main() -> None:
    lv = levels()
    print(f"{len(lv)} cells shared by all arms ({lv.index.get_level_values(0).nunique()} items x {len(RUBRICS)} rubrics)")
    noise = (lv["A2"] - lv["A"]).mean()
    rows = []
    for name, x, y in STEPS:
        d = lv[x] - lv[y]
        lo, hi = boot_ci(d)
        moves = abs(d.mean()) >= 0.10 and (lo > 0 or hi < 0) and abs(d.mean()) > abs(noise) + 0.05
        rows.append({"step": name, "mean": round(d.mean(), 3), "ci": f"[{lo:+.2f}, {hi:+.2f}]",
                     "changed": f"{(d != 0).mean():.0%}", "up": f"{(d > 0).mean():.0%}", "down": f"{(d < 0).mean():.0%}",
                     "moves": "yes" if moves and not name.startswith(("noise", "all")) else ""})
    print(pd.DataFrame(rows).to_string(index=False))
    s = sum(r["mean"] for r in rows[1:5])
    print(f"sum of the four steps {s:+.3f} vs B - A {rows[5]['mean']:+.3f} (gap = interaction)")
    per = pd.DataFrame({name: (lv[x] - lv[y]).groupby(level="rubric_ref").mean() for name, x, y in STEPS}).round(2)
    print(per.to_string())


if __name__ == "__main__":
    main()
