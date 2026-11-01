"""Pre-registered analysis of plp-o-relabel (PREREGISTRATION.md). Writes results/relabel_o.json.

PLp labels come from this study (o-swe, o-tau2, o-tb4; the SWE gate from plp-b2's o-swe-gate). PLe and PLs are
unchanged rubrics, so their labels come from pl-relabel-v2. Each study's own pre-registered functions are rerun, as
in pl-relabel-v2/analysis/analyse.py, and pl-relabel-v2's results (current PLp text, same prompt and judge) are put
beside them. Only answers written by claude-opus-5-5 count.

    python experiments/benchmarks/plp-o-relabel/analysis/analyse.py
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
    df = pd.read_csv(path, dtype={"instance_id": str})
    return df[df["valid"] & df["writer_model"].astype(str).str.startswith(MODEL)]


def agreement(new: pd.DataFrame, old: pd.DataFrame) -> dict:
    m = new.merge(old, on=["benchmark", "instance_id"], suffixes=("_new", "_old"))
    diff = m["level_new"] - m["level_old"]
    return {"n": len(m), "exact": round(float((diff == 0).mean()), 3),
            "within1": round(float((diff.abs() <= 1).mean()), 3), "mean_shift": round(float(diff.mean()), 3)}


def levels(df: pd.DataFrame) -> dict:
    return {int(k): int(v) for k, v in df["level"].value_counts().sort_index().items()}


def main() -> None:
    out = {}
    prev = json.loads((BENCH / "pl-relabel-v2/results/relabel.json").read_text())

    # SWE-bench Verified, with swebench-pl's own functions.
    from datasets import load_dataset
    swe = load("swepl_analyse", BENCH / "swebench-pl/analysis/analyse.py")
    o_plp = pd.concat([read(HERE / "labels/o-swe/labels_long.csv"),
                       read(BENCH / "plp-b2/labels/o-swe-gate/labels_long.csv")])
    v2 = pd.concat([read(BENCH / "pl-relabel-v2/labels/v2-swe/labels_long.csv"),
                    read(BENCH / "natural-prompt/labels/npb-gate-opuslow/labels_long.csv")])
    lab = pd.concat([o_plp[o_plp["demand"] == "PLp"], v2[v2["demand"].isin(["PLe", "PLs"])]])
    sample = pd.read_csv(BENCH / "swebench-pl/sample.csv").set_index("instance_id")
    wide = lab.pivot(index="instance_id", columns="demand", values="level")[DIMS]
    wide = wide.loc[wide.index.intersection(sample.index[sample["solvable"]])]
    meta = load_dataset("princeton-nlp/SWE-bench_Verified", split="test",
                        revision=swe.HF_REVISION).to_pandas().set_index("instance_id")
    df = wide.join(sample).join(meta["difficulty"])
    df["time_to_fix"] = df["difficulty"].map(swe.BUCKETS)
    varied = [d for d in DIMS if df[d].nunique() >= 3]
    v2_plp = v2[v2["demand"] == "PLp"].assign(benchmark="swe-bench-verified")
    out["swe"] = {"n_tasks": len(wide), "questions_O": swe.questions(df, varied),
                  "questions_current": prev["swe"]["questions_v2"],
                  "O_vs_current_PLp": agreement(o_plp[o_plp["demand"] == "PLp"].assign(benchmark="swe-bench-verified"),
                                                v2_plp),
                  "PLp_levels_O": levels(o_plp[o_plp["instance_id"].isin(wide.index)]),
                  "PLp_levels_current": levels(v2_plp[v2_plp["instance_id"].isin(wide.index)])}

    # tau2 and Terminal-Bench, with tau2-tb4-pl's own analyse().
    t2 = load("t2_analyse", BENCH / "tau2-tb4-pl/analysis/analyse.py")
    o_t = pd.concat(read(HERE / f"labels/{r}/labels_long.csv") for r in ("o-tau2", "o-tb4"))
    v2_t = pd.concat(read(BENCH / f"pl-relabel-v2/labels/{r}/labels_long.csv") for r in ("v2-tau2", "v2-tb4"))
    lab_t = pd.concat([o_t, v2_t[v2_t["demand"].isin(["PLe", "PLs"])]])
    res, _ = t2.analyse(lab_t, pd.read_csv(BENCH / "tau2-tb4-pl/sample.csv", dtype={"instance_id": str}))
    v2_tp = v2_t[v2_t["demand"] == "PLp"]
    out["tau2_tb4"] = {"analysis_O": res, "analysis_current": prev["tau2_tb4"]["analysis_v2"],
                       "O_vs_current_PLp": {b: agreement(o_t[o_t["benchmark"].str.startswith(b)],
                                                         v2_tp[v2_tp["benchmark"].str.startswith(b)])
                                            for b in ("tau2", "terminal-bench")},
                       "PLp_levels_O": {b: levels(o_t[o_t["benchmark"].str.startswith(b)]) for b in ("tau2", "terminal-bench")},
                       "PLp_levels_current": {b: levels(v2_tp[v2_tp["benchmark"].str.startswith(b)])
                                              for b in ("tau2", "terminal-bench")}}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results/relabel_o.json").write_text(json.dumps(out, indent=2, default=float) + "\n")
    print(json.dumps({"swe": {k: out["swe"][k] for k in ("questions_O", "O_vs_current_PLp", "PLp_levels_O")},
                      "tau2_tb4_agreement": out["tau2_tb4"]["O_vs_current_PLp"]}, indent=1, default=float))


if __name__ == "__main__":
    main()
