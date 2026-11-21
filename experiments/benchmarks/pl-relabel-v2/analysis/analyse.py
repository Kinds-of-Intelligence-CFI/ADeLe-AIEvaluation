"""Pre-registered analysis of pl-relabel-v2 (PREREGISTRATION.md). Writes results/relabel.json.

It reruns each study's own pre-registered analysis on the v2-prompt labels, with the studies' own
functions, and puts the old-prompt results beside them:
  - swebench-pl: questions() on the 435 solvable tasks (as its low_effort.py does for Opus low);
  - tau2-tb4-pl: analyse() on tau2 and Terminal-Bench (as its analyse.py does).
It also reports, per benchmark and rubric, the agreement between old and new labels.

    python experiments/benchmarks/pl-relabel-v2/analysis/analyse.py
"""

import importlib.util
import json
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parents[1]
BENCH = HERE.parent
DIMS = ["PLp", "PLe", "PLs"]
MODEL = "claude-opus-5-5"


def load(name: str, path: Path):
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def read(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype={"instance_id": str})


def agreement(new: pd.DataFrame, old: pd.DataFrame) -> dict:
    # tau2 task ids repeat across domains ("0" in airline and in retail), so the benchmark is part of the key.
    m = new.merge(old, on=["benchmark", "instance_id", "demand"], suffixes=("_new", "_old"))
    out = {}
    for d in DIMS:
        x = m[m["demand"] == d]
        diff = x["level_new"] - x["level_old"]
        out[d] = {"n": len(x), "exact": round(float((diff == 0).mean()), 3),
                  "within1": round(float((diff.abs() <= 1).mean()), 3), "mean_shift": round(float(diff.mean()), 3)}
    return out


def main() -> None:
    out = {}

    # SWE-bench Verified, with swebench-pl's own functions and table.
    from datasets import load_dataset
    swe = load("swepl_analyse", BENCH / "swebench-pl/analysis/analyse.py")
    new = pd.concat([read(HERE / "labels/v2-swe/labels_long.csv"),
                     read(BENCH / "natural-prompt/labels/npb-gate-opuslow/labels_long.csv")])
    new = new[new["valid"] & new["writer_model"].astype(str).str.startswith(MODEL)]
    old = pd.concat(read(BENCH / f"swebench-pl/labels/{r}/labels_long.csv") for r in ("swepl-gate-low", "swepl-r1-low"))
    sample = pd.read_csv(BENCH / "swebench-pl/sample.csv").set_index("instance_id")
    solvable = sample.index[sample["solvable"]]
    wide = new.pivot(index="instance_id", columns="demand", values="level")[DIMS]
    wide = wide.loc[wide.index.intersection(solvable)]
    meta = load_dataset("princeton-nlp/SWE-bench_Verified", split="test",
                        revision=swe.HF_REVISION).to_pandas().set_index("instance_id")
    df = wide.join(sample).join(meta["difficulty"])
    df["time_to_fix"] = df["difficulty"].map(swe.BUCKETS)
    varied = [d for d in DIMS if df[d].nunique() >= 3]
    out["swe"] = {"n_tasks": len(wide), "questions_v2": swe.questions(df, varied),
                  "questions_old_low": json.loads((BENCH / "swebench-pl/results/low_effort.json").read_text())["questions_on_low_labels"],
                  "old_vs_new": agreement(new, old),
                  "levels_v2": {d: {int(k): int(v) for k, v in wide[d].value_counts().sort_index().items()} for d in DIMS}}

    # tau2 and Terminal-Bench, with tau2-tb4-pl's own analyse().
    t2 = load("t2_analyse", BENCH / "tau2-tb4-pl/analysis/analyse.py")
    lab = pd.concat(read(HERE / f"labels/{r}/labels_long.csv") for r in ("v2-tau2", "v2-tb4"))
    usable = lab[lab["valid"]]
    t2_sample = read(BENCH / "tau2-tb4-pl/sample.csv")
    res, _ = t2.analyse(usable[usable["writer_model"] == t2.JUDGE_MODEL], t2_sample)
    old_t2 = pd.concat(read(BENCH / f"tau2-tb4-pl/labels/{r}/labels_long.csv") for r in ("tau2pl-r1", "tb4pl-r1"))
    out["tau2_tb4"] = {"analysis_v2": res,
                       "analysis_old": json.loads((BENCH / "tau2-tb4-pl/results/analysis.json").read_text()),
                       "old_vs_new": {b: agreement(usable[usable["benchmark"].str.startswith(b)],
                                                   old_t2[old_t2["benchmark"].str.startswith(b)])
                                      for b in ("tau2", "terminal-bench")},
                       "answers_by_other_models": int((usable["writer_model"] != t2.JUDGE_MODEL).sum()),
                       "unparsed": int((~lab["valid"]).sum())}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results/relabel.json").write_text(json.dumps(out, indent=2, default=float) + "\n")
    print(json.dumps({"swe_questions_v2": out["swe"]["questions_v2"], "swe_old_vs_new": out["swe"]["old_vs_new"],
                      "tau2_tb4_old_vs_new": out["tau2_tb4"]["old_vs_new"]}, indent=1, default=float))


if __name__ == "__main__":
    main()
