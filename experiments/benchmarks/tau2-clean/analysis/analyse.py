"""Analysis of tau2-clean. Writes results/clean.json.

PL labels for the 242 clean tasks: the existing Opus-low v2-prompt labels (PLp = text O from plp-o-relabel run
o-tau2; PLe and PLs from pl-relabel-v2 run v2-tau2) plus the mass run tau2-clean-new-pl (the 10 new banking tasks).
Only answers written by claude-opus-5-5 count. tau2-tb4-pl's own `combined()` is applied (Spearman per domain, then
the inverse-variance-weighted mean of Fisher z), for PLp, PLe and PLs against:
  solve_rate       over the common configurations (banking: post-v1.0.1 runs only)
  solve_rate_all   over every configuration (banking: post-v1.0.1 runs only)
Banking comparison: on the clean banking tasks, each rubric against the post-change rates and against the mixed-grading
rates (every banking run, as tau2-tb4-pl used), and the within-domain test with banking's mixed rates.

    python experiments/benchmarks/tau2-clean/analysis/analyse.py
"""

import importlib.util
import json
import sys
from pathlib import Path

import pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parents[1]
BENCH = HERE.parent
DIMS = ["PLp", "PLe", "PLs"]
MODEL = "claude-opus-5-5"
BANKING = "tau2-banking_knowledge"
SOURCES = {"PLp": ["plp-o-relabel/labels/o-tau2"], "PLe": ["pl-relabel-v2/labels/v2-tau2"],
           "PLs": ["pl-relabel-v2/labels/v2-tau2"]}
NEW_RUN = BENCH / "mass-annotation/runs/tau2-clean-new-pl/labels.csv"


def load(name: str, path: Path):
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def ok(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["valid"].astype(bool) & df["writer_model"].astype(str).str.startswith(MODEL)]


def read_labels() -> pd.DataFrame:
    parts = []
    for dim, runs in SOURCES.items():
        for r in runs:
            old = ok(pd.read_csv(BENCH / r / "labels_long.csv", dtype={"instance_id": str}))
            parts.append(old.loc[old["demand"] == dim, ["benchmark", "instance_id", "demand", "level"]])
    if not NEW_RUN.exists():
        sys.exit(f"{NEW_RUN} not found: run and collect tau2-clean-new-pl first")
    new = ok(pd.read_csv(NEW_RUN, dtype={"instance_id": str}))
    new = new[new["rubric_ref"].isin([f"v2/{d}" for d in DIMS])]
    parts.append(new.assign(demand=new["rubric_ref"].str.removeprefix("v2/"))[
        ["benchmark", "instance_id", "demand", "level"]])
    lab = pd.concat(parts).drop_duplicates(["benchmark", "instance_id", "demand"])
    return lab.astype({"level": float})


def main() -> None:
    t2 = load("t2_analyse", BENCH / "tau2-tb4-pl/analysis/analyse.py")
    tasks = pd.read_csv(HERE / "tasks.csv", dtype={"instance_id": str})
    keep = tasks[tasks["keep"]].set_index(["benchmark", "instance_id"])
    wide = read_labels().pivot(index=["benchmark", "instance_id"], columns="demand", values="level")
    df = keep.join(wide.reindex(columns=DIMS), how="left").reset_index()
    assert len(df) == len(keep)
    unlabelled = {d: [f"{b}/{i}" for b, i in df.loc[df[d].isna(), ["benchmark", "instance_id"]].values] for d in DIMS}

    bank = df[df["benchmark"] == BANKING]
    mixed = df.copy()
    is_b = mixed["benchmark"] == BANKING
    mixed.loc[is_b, "solve_rate"] = mixed.loc[is_b, "solve_rate_mixed"]
    mixed.loc[is_b, "solve_rate_all"] = mixed.loc[is_b, "solve_rate_all_mixed"]
    bank_cmp = {}
    for d in DIMS:
        g = bank.dropna(subset=[d])
        if g[d].nunique() < 2:
            bank_cmp[d] = {"n": len(g), "note": "one level: not testable"}
            continue
        bank_cmp[d] = {f"vs_{c}": t2.rho(g[d], g[c], "negative")
                       for c in ("solve_rate", "solve_rate_mixed", "solve_rate_all", "solve_rate_all_mixed")}
    agree = spearmanr(bank["solve_rate"], bank["solve_rate_mixed"])[0]

    out = {
        "n_clean": {"all": int(len(df)), **df.groupby("benchmark").size().astype(int).to_dict()},
        "unlabelled": unlabelled,
        "levels": {**{b: t2.levels(g) for b, g in df.groupby("benchmark")}, "tau2 (3 domains)": t2.levels(df)},
        "rubrics_with_3plus_levels": t2.tested(df),
        "within_domain_vs_solve_rate": {d: t2.combined(df, d, "solve_rate", "negative") for d in DIMS},
        "within_domain_vs_solve_rate_all": {d: t2.combined(df, d, "solve_rate_all", "negative") for d in DIMS},
        "banking_grading": {
            "n": int(len(bank)),
            "post_vs_mixed_solve_rate": {"spearman": round(float(agree), 3),
                                         "mean_abs_diff": round(float((bank["solve_rate"]
                                                                       - bank["solve_rate_mixed"]).abs().mean()), 4),
                                         "mean_post": round(float(bank["solve_rate"].mean()), 4),
                                         "mean_mixed": round(float(bank["solve_rate_mixed"].mean()), 4)},
            "rubric_vs_rates": bank_cmp,
            "within_domain_with_banking_mixed": {
                d: t2.combined(mixed, d, "solve_rate", "negative")["combined"] for d in DIMS},
        },
    }
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results/clean.json").write_text(json.dumps(out, indent=2, default=float) + "\n")
    print(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
