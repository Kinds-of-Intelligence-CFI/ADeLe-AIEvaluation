"""Pre-registered analysis of swebench-clean (PREREGISTRATION.md). Writes results/clean.json.

PL labels for the 443 clean tasks: the existing Opus-low v2-prompt labels (PLp = text O) plus run clean-swe. Only
answers written by claude-opus-5-5 count. swebench-pl's own `questions()` is applied:
  main         the 443 clean tasks
  robustness   the clean tasks with solve rate >= 0.05 (swebench-pl's cut)
Descriptive: level counts, and PLp on the tasks solved by 1 to 6 of 135 entries against the rest.

    uv run --extra annotate --with scipy python experiments/benchmarks/swebench-clean/analysis/analyse.py
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
SOURCES = {"PLp": ["plp-o-relabel/labels/o-swe", "plp-b2/labels/o-swe-gate"],
           "PLe": ["pl-relabel-v2/labels/v2-swe", "natural-prompt/labels/npb-gate-opuslow"],
           "PLs": ["pl-relabel-v2/labels/v2-swe", "natural-prompt/labels/npb-gate-opuslow"]}


def load(name: str, path: Path):
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def read(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype={"instance_id": str})
    return df[df["valid"] & df["writer_model"].astype(str).str.startswith(MODEL)]


def main() -> None:
    from datasets import load_dataset
    swe = load("swepl_analyse", BENCH / "swebench-pl/analysis/analyse.py")
    tasks = pd.read_csv(HERE / "tasks.csv").set_index("instance_id")
    keep = tasks[tasks["keep"]]
    new = read(HERE / "labels/clean-swe/labels_long.csv")
    parts = [new]
    for dim, runs in SOURCES.items():
        for r in runs:
            old = read(BENCH / r / "labels_long.csv")
            parts.append(old[old["demand"] == dim])
    lab = pd.concat(parts)
    lab = lab[lab["instance_id"].isin(keep.index)].drop_duplicates(["instance_id", "demand"])
    wide = lab.pivot(index="instance_id", columns="demand", values="level")[DIMS]
    meta = load_dataset("princeton-nlp/SWE-bench_Verified", split="test",
                        revision=swe.HF_REVISION).to_pandas().set_index("instance_id")
    df = keep.join(wide).join(meta["difficulty"])
    df["time_to_fix"] = df["difficulty"].map(swe.BUCKETS)
    unlabelled = {d: sorted(df.index[df[d].isna()]) for d in DIMS}
    df = df.dropna(subset=DIMS)
    varied = [d for d in DIMS if df[d].nunique() >= 3]
    cut = df[df["solve_rate"] >= 0.05]
    rare = df["solved_by"] <= 6
    out = {
        "n_clean": int(len(keep)), "n_analysed": int(len(df)), "unlabelled": unlabelled,
        "rubrics_tested": varied,
        "main": swe.questions(df, varied),
        "robustness_solve_rate_ge_0.05": {"n": int(len(cut)), **swe.questions(cut, varied)},
        "levels": {d: {int(k): int(v) for k, v in df[d].value_counts().sort_index().items()} for d in DIMS},
        "rarely_solved": {"n": int(rare.sum()),
                          "PLp_mean_rare": round(float(df.loc[rare, "PLp"].mean()), 3),
                          "PLp_mean_rest": round(float(df.loc[~rare, "PLp"].mean()), 3),
                          "PLp_levels_rare": {int(k): int(v) for k, v in
                                              df.loc[rare, "PLp"].value_counts().sort_index().items()}},
    }
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results/clean.json").write_text(json.dumps(out, indent=2, default=float) + "\n")
    print(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
