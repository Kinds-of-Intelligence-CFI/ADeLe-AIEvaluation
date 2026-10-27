"""Pre-registered analysis of cooperbench-plms. Writes results/analysis.json.

Labels: mass run cooperbench-plms (PLp, PLe, PLs, MSm, MSc on 120 pairs x solo, coop; Opus 5.5 low, v2 prompt); only
valid answers written by claude-opus-5-5 count. Outcomes: tasks.csv (make_set.py): per pair, solo_rate and coop_rate
over GPT-5, Claude Sonnet 4.5 and GPT-5.5, and drop = solo_rate - coop_rate.
Tests (Spearman, swebench-pl's `rho`):
  primary     MSc of the coop prompt against drop, and MSm of the coop prompt against drop: predicted positive
  secondary   every rubric's coop - solo difference against drop (positive); every rubric's solo level against
              solo_rate and coop level against coop_rate (negative)
  sensitivity the primary tests without flagged pairs (a feature's spec or tests changed after the runs), and with the
              official site coop results for GPT-5 and Claude (data/raw/cooperbench/outcomes_site.csv, local only)
Descriptive: level distributions by condition; share of pairs whose coop prompt is above its solo prompt.

    python experiments/benchmarks/cooperbench-plms/analysis/analyse.py
"""

import importlib.util
import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parents[1]
BENCH = HERE.parent
ROOT = BENCH.parents[1]
DIMS = ["PLp", "PLe", "PLs", "MSm", "MSc"]
MODEL = "claude-opus-5-5"
RUN = BENCH / "mass-annotation/runs/cooperbench-plms/labels.csv"
SITE = ROOT / "data/raw/cooperbench/outcomes_site.csv"

_spec = importlib.util.spec_from_file_location("swepl_analyse", BENCH / "swebench-pl/analysis/analyse.py")
_swepl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_swepl)
rho = _swepl.rho


def test(df: pd.DataFrame, x: str, y: str, direction: str) -> dict:
    h = df.dropna(subset=[x, y])
    if h[x].nunique() < 2 or h[y].nunique() < 2:
        return {"n": int(len(h)), "note": "constant: not testable"}
    return rho(h[x], h[y], direction)


def main() -> None:
    lab = pd.read_csv(RUN, dtype={"instance_id": str})
    lab = lab[lab["valid"].astype(bool) & lab["writer_model"].astype(str).str.startswith(MODEL)]
    lab[["pair_id", "condition"]] = lab["instance_id"].str.rsplit("@", n=1, expand=True)
    lab["col"] = lab["rubric_ref"].str.removeprefix("v2/") + "_" + lab["condition"]
    wide = lab.pivot(index="pair_id", columns="col", values="level")
    tasks = pd.read_csv(HERE / "tasks.csv").set_index("pair_id")
    df = tasks[tasks["sampled"]].join(wide)
    for d in DIMS:
        df[f"{d}_diff"] = df.get(f"{d}_coop") - df.get(f"{d}_solo")

    out = {"n": {"pairs": int(len(df)), "unflagged": int((~df["any_flag"]).sum()),
                 "labelled": {c: int(df[c].notna().sum()) for c in sorted(wide.columns)}},
           "levels": {c: {int(k): int(v) for k, v in df[c].value_counts().sort_index().items()}
                      for c in sorted(wide.columns)},
           "coop_above_solo": {d: round(float((df[f"{d}_diff"] > 0).mean()), 3) for d in DIMS},
           "outcomes": df[["solo_rate", "coop_rate", "drop"]].describe().round(3).to_dict(),
           "primary": {d: test(df, f"{d}_coop", "drop", "positive") for d in ("MSc", "MSm")},
           "secondary": {}, "sensitivity": {}}
    for d in DIMS:
        out["secondary"][f"{d}_diff_vs_drop"] = test(df, f"{d}_diff", "drop", "positive")
        out["secondary"][f"{d}_solo_vs_solo_rate"] = test(df, f"{d}_solo", "solo_rate", "negative")
        out["secondary"][f"{d}_coop_vs_coop_rate"] = test(df, f"{d}_coop", "coop_rate", "negative")
    clean = df[~df["any_flag"]]
    out["sensitivity"]["unflagged"] = {d: test(clean, f"{d}_coop", "drop", "positive") for d in ("MSc", "MSm")}
    if SITE.exists():
        s = pd.read_csv(SITE)
        s = s[(s["condition"] == "coop") & s["config"].isin(["gpt5", "claude"])]
        s = s.assign(ok=s["success"].astype(str).str.lower().eq("true")).pivot(
            index="pair_id", columns="config", values="ok").astype(float)
        site = df.copy()
        site["coop_rate"] = (s["gpt5"].reindex(site.index) + s["claude"].reindex(site.index) + site["gpt55_coop"]) / 3
        site["drop"] = site["solo_rate"] - site["coop_rate"]
        out["sensitivity"]["site_coop"] = {d: test(site, f"{d}_coop", "drop", "positive") for d in ("MSc", "MSm")}
    else:
        out["sensitivity"]["site_coop"] = "not run: data/raw/cooperbench/outcomes_site.csv missing"
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results/analysis.json").write_text(json.dumps(out, indent=2, default=str) + "\n")
    print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
