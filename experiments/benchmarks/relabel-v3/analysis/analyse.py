"""Pre-registered analysis of relabel-v3: PLp and MSm relabelled after the two flagged examples were fixed.
Writes results/analysis.json.

New labels: mass runs relabel-v3, relabel-v3-long, relabel-v3-eqbench4, relabel-v3-cooperbench, relabel-v3-gamearena
(Opus 5.5 low, v2 prompt); only valid answers written by claude-opus-5-5 count. Old labels: old_labels.csv, the
relabel-v2 labels of PLp and MSm, frozen before any new label (column `opus`). Only cells within one level of the
changed example were re-judged (PLp at 3-5, MSm at 4-5; selected.csv); the others keep their old label. Per set and rubric: level counts, the
share unchanged, the mean shift, and for the agentic sets the Spearman of old and new labels with the set's primary
outcome (as ms-benchmarks; tau2 within domain). For the social sets: mean PLp and MSm per set, old and new.

    python experiments/benchmarks/relabel-v3/analysis/analyse.py
"""

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parents[1]
BENCH = HERE.parent
DIMS = ["PLp", "MSm"]
MODEL = "claude-opus-5-5"
RUNS = ["relabel-v3-plp", "relabel-v3-plp-long", "relabel-v3-plp-eqbench4", "relabel-v3-plp-cooperbench",
        "relabel-v3-plp-gamearena", "relabel-v3-msm-eqbench4", "relabel-v3-msm-gamearena"]
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
        p = BENCH / f"mass-annotation/runs/{r}/labels.csv"
        if not p.exists():
            continue
        lab = pd.read_csv(p, dtype={"instance_id": str})
        lab = lab[lab["valid"].astype(bool) & lab["writer_model"].astype(str).str.startswith(MODEL)]
        parts.append(lab.assign(rubric=lab["rubric_ref"].str.removeprefix("v2/"))[
            ["benchmark", "instance_id", "rubric", "level"]].rename(columns={"level": "new"}))
    return pd.concat(parts)


def main() -> None:
    old = pd.read_csv(HERE / "old_labels.csv", dtype={"instance_id": str})
    df = old.merge(new_labels(), on=["benchmark", "instance_id", "rubric"], how="outer")
    # Only cells within one level of the changed example were re-judged; the others keep their relabel-v2 label.
    df["rejudged"] = df["new"].notna()
    df["new"] = df["new"].fillna(df["opus"])
    df["set"] = np.where(df["benchmark"].isin(TAU2), "tau2", df["benchmark"])
    oc = outcomes()
    out = {"n": {}, "levels": {}, "unchanged": {}, "mean_shift": {}, "spearman": {}, "social_means": {}}
    for (s, d), g in df.groupby(["set", "rubric"]):
        k = f"{s}/{d}"
        both = g.dropna(subset=["opus", "new"])
        out["n"][k] = {"old": int(g["opus"].notna().sum()), "new": int(g["new"].notna().sum())}
        out["levels"][k] = {c: {str(int(v)): int(n) for v, n in g[c].value_counts().sort_index().items()}
                            for c in ("opus", "new")}
        out["unchanged"][k] = round(float((both["opus"] == both["new"]).mean()), 3) if len(both) else None
        out["mean_shift"][k] = round(float((both["new"] - both["opus"]).mean()), 3) if len(both) else None
        if s in SOCIAL:
            out["social_means"][k] = {c: round(float(g[c].mean()), 2) for c in ("opus", "new")}
            continue
        h = g.merge(oc, on=["benchmark", "instance_id"], how="left")
        res = {}
        for c in ("opus", "new"):
            x = h.dropna(subset=[c, "outcome"])
            if s == "tau2":
                res[c] = combined(x, c, "outcome", "negative")["combined"] if len(x) else None
            elif x[c].nunique() < 2:
                res[c] = {"n": int(len(x)), "note": "one level: not testable"}
            else:
                res[c] = rho(x[c], x["outcome"], "negative")
        out["spearman"][k] = res
    pooled = df.dropna(subset=["opus", "new"])
    out["pooled_unchanged"] = {d: round(float((g["opus"] == g["new"]).mean()), 3) for d, g in pooled.groupby("rubric")}
    rj = pooled[pooled["rejudged"]]
    out["rejudged"] = {d: {"n": int(len(g)), "unchanged": round(float((g["opus"] == g["new"]).mean()), 3),
                           "mean_shift": round(float((g["new"] - g["opus"]).mean()), 3),
                           "moves": {f"{int(a)}->{int(b)}": int(n) for (a, b), n in g.groupby(["opus", "new"]).size().items() if a != b}}
                       for d, g in rj.groupby("rubric")}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results/analysis.json").write_text(json.dumps(out, indent=2, default=str) + "\n")
    print(json.dumps({"pooled_unchanged": out["pooled_unchanged"], "rejudged": out["rejudged"]}, indent=1))


if __name__ == "__main__":
    main()
