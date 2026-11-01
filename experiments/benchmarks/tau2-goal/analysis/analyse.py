"""Pre-registered analysis of tau2-goal: the five rubrics on the 242 released tau2 tasks, judged on the full task with
its goal but without the grader's expected-action list. Writes results/analysis.json.

New labels: mass runs tau2-goal and tau2-goal-long (Opus 5.5 low, bare digit); only valid answers written by
claude-opus-5-5 count. Compared with the released labels (`../tau2-full/old_labels.csv`, column `released`) and the
tau2-full labels (`full`, as `../tau2-full/analysis/analyse.py` reads them). Per domain and rubric: level counts, exact
and within-one agreement, mean shift. Per rubric: Spearman with solve rate within domain (as ms-benchmarks). MSc
against Pablo's 15 labels. Sealed predictions are scored at the end.

    python experiments/benchmarks/tau2-goal/analysis/analyse.py
"""

import importlib.util
import json
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parents[1]
BENCH = HERE.parent
MODEL = "claude-opus-5-5"
RUNS = ["tau2-goal", "tau2-goal-long"]
KEY = ["benchmark", "instance_id", "rubric"]
COLS = ("released", "full", "new")


def load(name: str, path: Path):
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


combined = load("t2_analyse", BENCH / "tau2-tb4-pl/analysis/analyse.py").combined
outcomes = load("msb_analyse", BENCH / "ms-benchmarks/analysis/analyse.py").outcomes
tau2_full = load("tau2_full_analyse", BENCH / "tau2-full/analysis/analyse.py")


def new_labels() -> pd.DataFrame:
    parts = []
    for r in RUNS:
        lab = pd.read_csv(BENCH / f"mass-annotation/runs/{r}/labels.csv", dtype={"instance_id": str})
        lab = lab[lab["valid"].astype(bool) & lab["writer_model"].astype(str).str.startswith(MODEL)]
        parts.append(lab.assign(rubric=lab["rubric_ref"].str.removeprefix("v2/"))[KEY + ["level"]]
                     .rename(columns={"level": "new"}))
    return pd.concat(parts)


def human(df: pd.DataFrame) -> dict:
    items = pd.read_csv(BENCH / "msc-l4-note/human_items.csv", dtype={"instance_id": str})
    h = pd.read_csv(BENCH / "ms-candidate/human_labels.csv")
    h["pablo"] = h["msc_revised"].fillna(h["msc"])
    msc = df[df["rubric"] == "MSc"][["benchmark", "instance_id", *COLS]]
    m = items.merge(h[["item_id", "pablo"]], on="item_id").merge(msc, on=["benchmark", "instance_id"], how="left")
    out = {"items": m[["item_id", "benchmark", "instance_id", "pablo", *COLS]].to_dict("records")}
    for c in COLS:
        x = m.dropna(subset=[c])
        out[c] = {"exact": int((x[c] == x["pablo"]).sum()), "within_one": int(((x[c] - x["pablo"]).abs() <= 1).sum()),
                  "mean_diff": round(float((x[c] - x["pablo"]).mean()), 2), "n": int(len(x))}
    return out


def main() -> None:
    old = pd.read_csv(BENCH / "tau2-full/old_labels.csv", dtype={"instance_id": str})[KEY + ["released"]]
    full = tau2_full.new_labels().rename(columns={"new": "full"})
    df = old.merge(full, on=KEY, how="outer").merge(new_labels(), on=KEY, how="outer")
    oc = outcomes()
    out = {"n": {}, "levels": {}, "vs_released": {}, "vs_full": {}, "spearman": {}}
    groups = [(f"{b}/{d}", g) for (b, d), g in df.groupby(["benchmark", "rubric"])]
    groups += [(f"tau2/{d}", g) for d, g in df.groupby("rubric")]
    for k, g in groups:
        out["n"][k] = {c: int(g[c].notna().sum()) for c in COLS}
        out["levels"][k] = {c: tau2_full.counts(g[c]) for c in COLS}
        out["vs_released"][k] = tau2_full.agree(g, "released")
        out["vs_full"][k] = tau2_full.agree(g, "full")
    for d, g in df.groupby("rubric"):
        h = g.merge(oc, on=["benchmark", "instance_id"], how="left")
        out["spearman"][d] = {c: combined(h.dropna(subset=[c, "outcome"]), c, "outcome", "negative")["combined"]
                              for c in COLS}
    out["no_new_label"] = df.loc[df["new"].isna(), KEY].to_dict("records")
    out["human_tau2_msc"] = hm = human(df)
    both = df.dropna(subset=["full", "new"])
    out["pooled_exact_vs_full"] = round(float((both["full"] == both["new"]).mean()), 3)
    sp = out["spearman"]
    out["predictions"] = {
        "MSc exact vs Pablo >= 12 of 15 (0.65)": hm["new"]["exact"] >= 12,
        "PLp negative within-domain signal, p < 0.05 (0.8)": bool(sp["PLp"]["new"]["rho"] < 0
                                                                  and sp["PLp"]["new"]["p_two_sided"] < 0.05),
        "pooled exact vs tau2-full >= 80% (0.6)": out["pooled_exact_vs_full"] >= 0.8,
    }
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results/analysis.json").write_text(json.dumps(out, indent=2, default=str) + "\n")
    print(json.dumps({"predictions": out["predictions"], "pooled_exact_vs_full": out["pooled_exact_vs_full"],
                      "human": {c: hm[c] for c in COLS}}, indent=1))


if __name__ == "__main__":
    main()
