"""Pre-registered analysis of relabel-v4-ms: MSm and MSc relabelled after adoption (b05ddf3). Writes results/analysis.json.

New labels: mass runs relabel-v4-ms, -long, -eqbench4, -cooperbench, -gamearena (Opus 5.5 low, bare digit); only valid
answers written by claude-opus-5-5 count. Old labels: old_labels.csv, the MSm and MSc labels of label set `current`
(dc0e04a), frozen from labelsets/current.toml. Per set and rubric: level counts, exact and within-one agreement, the
mean shift, and for the agentic sets the Spearman of old and new labels with the set's primary outcome (as
ms-benchmarks; tau2 within domain). For the social sets: mean MSm and MSc, old and new. On the tau2 sets: MSc against
Pablo's 15 agent-side labels (ms-candidate/human_labels.csv; msc_revised where he revised one).

    python experiments/benchmarks/relabel-v4-ms/analysis/analyse.py
"""

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parents[1]
BENCH = HERE.parent
MODEL = "claude-opus-5-5"
RUNS = ["relabel-v4-ms", "relabel-v4-ms-long", "relabel-v4-ms-eqbench4", "relabel-v4-ms-cooperbench",
        "relabel-v4-ms-gamearena"]
TAU2 = ["tau2-airline", "tau2-retail", "tau2-banking_knowledge"]
SOCIAL = ["eqbench4", "cooperbench", "gamearena"]


def load(name: str, path: Path):
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


rho = load("swepl_analyse", BENCH / "swebench-pl/analysis/analyse.py").rho
combined = load("t2_analyse", BENCH / "tau2-tb4-pl/analysis/analyse.py").combined
outcomes = load("msb_analyse", BENCH / "ms-benchmarks/analysis/analyse.py").outcomes


def new_labels() -> pd.DataFrame:
    parts = []
    for r in RUNS:
        lab = pd.read_csv(BENCH / f"mass-annotation/runs/{r}/labels.csv", dtype={"instance_id": str})
        lab = lab[lab["valid"].astype(bool) & lab["writer_model"].astype(str).str.startswith(MODEL)]
        parts.append(lab.assign(rubric=lab["rubric_ref"].str.removeprefix("v2/"))[
            ["benchmark", "instance_id", "rubric", "level"]].rename(columns={"level": "new"}))
    return pd.concat(parts)


def counts(s: pd.Series) -> dict:
    return {str(int(v)): int(n) for v, n in s.dropna().value_counts().sort_index().items()}


def human(df: pd.DataFrame) -> dict:
    items = pd.read_csv(BENCH / "msc-l4-note/human_items.csv", dtype={"instance_id": str})
    h = pd.read_csv(BENCH / "ms-candidate/human_labels.csv")
    h["pablo"] = h["msc_revised"].fillna(h["msc"])
    msc = df[df["rubric"] == "MSc"][["benchmark", "instance_id", "old", "new"]]
    m = items.merge(h[["item_id", "msc", "pablo"]], on="item_id").merge(msc, on=["benchmark", "instance_id"], how="left")
    out = {"n": int(len(m)), "missing": m.loc[m["new"].isna(), "item_id"].tolist(),
           "items": m[["item_id", "benchmark", "instance_id", "role", "msc", "pablo", "old", "new"]].to_dict("records")}
    for c in ("old", "new"):
        x = m.dropna(subset=[c])
        out[c] = {ref: {"exact": int((x[c] == x[ref]).sum()), "within_one": int(((x[c] - x[ref]).abs() <= 1).sum()),
                        "mean_diff": round(float((x[c] - x[ref]).mean()), 2), "n": int(len(x))}
                  for ref in ("pablo", "msc")}
    return out


def main() -> None:
    old = pd.read_csv(HERE / "old_labels.csv", dtype={"instance_id": str})[["benchmark", "instance_id", "rubric", "old"]]
    df = old.merge(new_labels(), on=["benchmark", "instance_id", "rubric"], how="outer")
    df["set"] = np.where(df["benchmark"].isin(TAU2), "tau2", df["benchmark"])
    oc = outcomes()
    out = {"n": {}, "levels": {}, "exact": {}, "within_one": {}, "mean_shift": {}, "spearman": {}, "social_means": {}}
    for (s, d), g in df.groupby(["set", "rubric"]):
        k = f"{s}/{d}"
        both = g.dropna(subset=["old", "new"])
        diff = both["new"] - both["old"]
        out["n"][k] = {"old": int(g["old"].notna().sum()), "new": int(g["new"].notna().sum()), "both": int(len(both))}
        out["levels"][k] = {c: counts(g[c]) for c in ("old", "new")}
        out["exact"][k] = round(float((diff == 0).mean()), 3)
        out["within_one"][k] = round(float((diff.abs() <= 1).mean()), 3)
        out["mean_shift"][k] = round(float(diff.mean()), 3)
        if s in SOCIAL:
            out["social_means"][k] = {c: round(float(g[c].mean()), 2) for c in ("old", "new")}
            continue
        h = g.merge(oc, on=["benchmark", "instance_id"], how="left")
        res = {}
        for c in ("old", "new"):
            x = h.dropna(subset=[c, "outcome"])
            if s == "tau2":
                res[c] = combined(x, c, "outcome", "negative")["combined"] if len(x) else None
            elif x[c].nunique() < 2:
                res[c] = {"n": int(len(x)), "note": "one level: not testable"}
            else:
                res[c] = rho(x[c], x["outcome"], "negative")
        out["spearman"][k] = res
    both = df.dropna(subset=["old", "new"])
    out["tau2_by_domain"] = {f"{b}/{d}": {"n": int(len(g)), "exact": round(float((g["old"] == g["new"]).mean()), 3),
                                          "within_one": round(float(((g["new"] - g["old"]).abs() <= 1).mean()), 3),
                                          "levels": {c: counts(g[c]) for c in ("old", "new")}}
                             for (b, d), g in both[both["set"] == "tau2"].groupby(["benchmark", "rubric"])}
    out["pooled"] = {d: {"n": int(len(g)), "exact": round(float((g["old"] == g["new"]).mean()), 3),
                         "within_one": round(float(((g["new"] - g["old"]).abs() <= 1).mean()), 3),
                         "mean_shift": round(float((g["new"] - g["old"]).mean()), 3),
                         "moves": {f"{int(a)}->{int(b)}": int(n) for (a, b), n in
                                   g.groupby(["old", "new"]).size().items() if a != b}}
                     for d, g in both.groupby("rubric")}
    out["no_new_label"] = df.loc[df["new"].isna(), ["benchmark", "instance_id", "rubric"]].to_dict("records")
    out["no_old_label"] = df.loc[df["old"].isna(), ["benchmark", "instance_id", "rubric"]].to_dict("records")
    out["human_tau2_msc"] = human(df[df["set"] == "tau2"])
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results/analysis.json").write_text(json.dumps(out, indent=2, default=str) + "\n")
    print(json.dumps({"pooled": out["pooled"], "human": {c: out["human_tau2_msc"][c] for c in ("old", "new")}}, indent=1))


if __name__ == "__main__":
    main()
