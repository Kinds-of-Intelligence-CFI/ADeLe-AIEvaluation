"""Pre-registered analysis of tau2-full: the five rubrics on the 242 released tau2 tasks, judged on the full task.
Writes results/analysis.json.

New labels (Opus 5.5 low, bare digit): airline and retail from mass run tau2-full; banking from tau2-full-banking and
tau2-full-banking-long (amendment 1). Only valid answers written by claude-opus-5-5 count. Old labels: old_labels.csv, frozen from label set `current` (column `released`) and, for MSm
and MSc, relabel-v4-ms (column `v4ms`: same rubric text and prompt, script input). Per benchmark and rubric: level
counts, exact and within-one agreement, mean shift. Per rubric: Spearman with solve rate within domain (as
ms-benchmarks). MSc against Pablo's 15 labels (ms-candidate/human_labels.csv, msc_revised where he revised one).
Sealed predictions are scored at the end.

    python experiments/benchmarks/tau2-full/analysis/analyse.py
"""

import importlib.util
import json
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parents[1]
BENCH = HERE.parent
MODEL = "claude-opus-5-5"
# Amendment 1: banking from the plain-text re-judge; tau2-full's banking labels and tau2-full-long are set aside.
RUNS = {"tau2-full": ["tau2-airline", "tau2-retail"],
        "tau2-full-banking": ["tau2-banking_knowledge"], "tau2-full-banking-long": ["tau2-banking_knowledge"]}
KEY = ["benchmark", "instance_id", "rubric"]


def load(name: str, path: Path):
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


combined = load("t2_analyse", BENCH / "tau2-tb4-pl/analysis/analyse.py").combined
outcomes = load("msb_analyse", BENCH / "ms-benchmarks/analysis/analyse.py").outcomes


def new_labels() -> pd.DataFrame:
    parts = []
    for r, benches in RUNS.items():
        lab = pd.read_csv(BENCH / f"mass-annotation/runs/{r}/labels.csv", dtype={"instance_id": str})
        lab = lab[lab["valid"].astype(bool) & lab["writer_model"].astype(str).str.startswith(MODEL)
                  & lab["benchmark"].isin(benches)]
        parts.append(lab.assign(rubric=lab["rubric_ref"].str.removeprefix("v2/"))[KEY + ["level"]]
                     .rename(columns={"level": "new"}))
    return pd.concat(parts)


def counts(s: pd.Series) -> dict:
    return {str(int(v)): int(n) for v, n in s.dropna().value_counts().sort_index().items()}


def agree(g: pd.DataFrame, ref: str) -> dict:
    x = g.dropna(subset=[ref, "new"])
    d = x["new"] - x[ref]
    return {"n": int(len(x)), "exact": round(float((d == 0).mean()), 3),
            "within_one": round(float((d.abs() <= 1).mean()), 3), "mean_shift": round(float(d.mean()), 3)}


def human(df: pd.DataFrame) -> dict:
    items = pd.read_csv(BENCH / "msc-l4-note/human_items.csv", dtype={"instance_id": str})
    h = pd.read_csv(BENCH / "ms-candidate/human_labels.csv")
    h["pablo"] = h["msc_revised"].fillna(h["msc"])
    msc = df[df["rubric"] == "MSc"][["benchmark", "instance_id", "released", "v4ms", "new"]]
    m = items.merge(h[["item_id", "msc", "pablo"]], on="item_id").merge(msc, on=["benchmark", "instance_id"], how="left")
    out = {"items": m[["item_id", "benchmark", "instance_id", "msc", "pablo", "released", "v4ms", "new"]].to_dict("records")}
    for c in ("released", "v4ms", "new"):
        x = m.dropna(subset=[c])
        out[c] = {"exact": int((x[c] == x["pablo"]).sum()), "within_one": int(((x[c] - x["pablo"]).abs() <= 1).sum()),
                  "mean_diff": round(float((x[c] - x["pablo"]).mean()), 2), "n": int(len(x))}
    return out


def main() -> None:
    old = pd.read_csv(HERE / "old_labels.csv", dtype={"instance_id": str})
    df = old.merge(new_labels(), on=KEY, how="outer")
    oc = outcomes()
    out = {"n": {}, "levels": {}, "vs_released": {}, "vs_v4ms": {}, "spearman": {}}
    for (b, d), g in df.groupby(["benchmark", "rubric"]):
        k = f"{b}/{d}"
        out["n"][k] = {c: int(g[c].notna().sum()) for c in ("released", "v4ms", "new")}
        out["levels"][k] = {c: counts(g[c]) for c in ("released", "v4ms", "new") if g[c].notna().any()}
        out["vs_released"][k] = agree(g, "released")
        if g["v4ms"].notna().any():
            out["vs_v4ms"][k] = agree(g, "v4ms")
    for d, g in df.groupby("rubric"):
        out["levels"][f"tau2/{d}"] = {c: counts(g[c]) for c in ("released", "v4ms", "new") if g[c].notna().any()}
        out["vs_released"][f"tau2/{d}"] = agree(g, "released")
        if g["v4ms"].notna().any():
            out["vs_v4ms"][f"tau2/{d}"] = agree(g, "v4ms")
        h = g.merge(oc, on=["benchmark", "instance_id"], how="left")
        out["spearman"][d] = {c: combined(h.dropna(subset=[c, "outcome"]), c, "outcome", "negative")["combined"]
                              for c in ("released", "v4ms", "new") if g[c].notna().any()}
    out["no_new_label"] = df.loc[df["new"].isna(), KEY].to_dict("records")
    out["human_tau2_msc"] = hm = human(df)
    msc = df[df["rubric"] == "MSc"]
    sp = out["spearman"]
    out["predictions"] = {
        "MSc exact vs Pablo >= 13 of 15 (0.75)": hm["new"]["exact"] >= 13,
        "more MSc at Level 1 than relabel-v4-ms (0.75)": bool((msc["new"] == 1).sum() > (msc["v4ms"] == 1).sum()),
        "PLp negative within-domain signal, p < 0.05 (0.6)": bool(sp["PLp"]["new"]["rho"] < 0
                                                                  and sp["PLp"]["new"]["p_two_sided"] < 0.05),
        "MSc negative within-domain signal, p < 0.05 (0.5)": bool(sp["MSc"]["new"]["rho"] < 0
                                                                  and sp["MSc"]["new"]["p_two_sided"] < 0.05),
    }
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results/analysis.json").write_text(json.dumps(out, indent=2, default=str) + "\n")
    print(json.dumps({"predictions": out["predictions"], "human": {c: hm[c] for c in ("released", "v4ms", "new")}},
                     indent=1))


if __name__ == "__main__":
    main()
