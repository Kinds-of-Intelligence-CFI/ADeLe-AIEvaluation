"""rWG against the published GPT-4o levels, the agreement index of the paper's Table 7 (arXiv:2503.06378, §5.3).

Per item, rWG = 1 - s² / σ²_EU, where s² is the variance of the two ratings (judge, GPT-4o) and σ²_EU = (A² - 1) / 12
is the variance of a uniform null over A = 6 levels; negative values are set to 0, then averaged per rubric.
A one-level difference on an item gives 0.83, so the index is lenient.
For reference, the paper reports Delphi consensus vs GPT-4o 0.86 and humans among themselves 0.83 (18 rubrics, other
items). Our runs share the 60 bridge items and the 8 rubrics of abl-s3, all with builder v1-layout-noreason.

Run: .venv/bin/python experiments/benchmarks/v1-prompt-bridge/rwg.py   (writes rwg.json)
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
REPO = HERE.parents[2]
RUNS = HERE.parent / "mass-annotation" / "runs"
RUBRICS = ["AS", "CEc", "CL", "KNa", "KNc", "MCt", "MCu", "QLq"]
JUDGES = {"Opus 5.5 low": "abl-s3", "Sonnet 5.5 low": "rwg-sonnet-low", "Haiku 5.5 low": "rwg-haiku-low"}
SIGMA2_EU = (6 ** 2 - 1) / 12


def labels(run: str) -> pd.DataFrame:
    df = pd.read_csv(RUNS / run / "labels.csv", dtype={"instance_id": str})
    df = df[df["valid"]]
    df["rubric"] = df["rubric_ref"].str.removeprefix("v1/")
    return df.pivot_table(index="instance_id", columns="rubric", values="level", aggfunc="first")[RUBRICS]


def main() -> None:
    ref = pd.read_csv(REPO / "data" / "instances" / "v1_bridge_reference.csv", dtype={"instance_id": str})
    ref = ref.set_index("instance_id")[RUBRICS]
    out = {}
    for name, run in JUDGES.items():
        x = labels(run).reindex(ref.index)
        rwg = (1 - (x - ref) ** 2 / 2 / SIGMA2_EU).clip(lower=0)  # NaN where the judge gave no label
        out[name] = {"run": run, "labelled": int(x.notna().sum().sum()), "rwg": round(float(rwg.stack().mean()), 3),
                     "exact": round(float((x == ref).stack().mean()), 3),
                     "within_1": round(float(((x - ref).abs() <= 1).stack().mean()), 3),
                     "shift": round(float((x - ref).stack().mean()), 3),
                     "rwg_per_rubric": rwg.mean().round(2).to_dict()}
    (HERE / "rwg.json").write_text(json.dumps(out, indent=2) + "\n")
    print(pd.DataFrame(out).T.drop(columns="rwg_per_rubric").to_string())
    print(pd.DataFrame({k: v["rwg_per_rubric"] for k, v in out.items()}).to_string())


if __name__ == "__main__":
    main()
