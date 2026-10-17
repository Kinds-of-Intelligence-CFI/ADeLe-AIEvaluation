"""Pre-registered analysis of eqbench4-plms. Writes results/analysis.json.

Labels: mass run eqbench4-plms (PLp, PLe, PLs, MSm, MSc; Opus 5.5 low, v2 prompt); only valid answers written by
claude-opus-5-5 count. Outcomes: labels/eq4-outcome/outcomes.csv (collect_outcome.py), valid first-pass cells only.
Per scenario, over the 10 judged models:
  disclosure_rate   primary: share of models whose transcript has CORE = yes (the persona openly acknowledged its
                    hidden core issue)
  acknowledged_rate CORE = yes or partly
  items_rate        share of "deep down" items voiced, pooled over models
Tests (Spearman, swebench-pl's `rho`; each rubric predicted negative):
  primary     MSm and MSc against disclosure_rate within source type (generated, hand-authored), combined by Fisher z
              (tau2-tb4-pl's `combined`)
  secondary   PLp, PLe, PLs the same way; every rubric against acknowledged_rate and items_rate; all 120 pooled
Checks: judge repeatability (CORE exact agreement and Cohen's kappa on the 60 repeat cells); model-level
disclosure rate against EQ-Bench 4 Elo (Spearman, predicted positive, n = 10).

    python experiments/benchmarks/eqbench4-plms/analysis/analyse.py
"""

import importlib.util
import json
import sys
from pathlib import Path

import pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parents[1]
BENCH = HERE.parent
ROOT = BENCH.parents[1]
DIMS = ["PLp", "PLe", "PLs", "MSm", "MSc"]
MODEL = "claude-opus-5-5"
RUN = BENCH / "mass-annotation/runs/eqbench4-plms/labels.csv"
OUTCOMES = ["disclosure_rate", "acknowledged_rate", "items_rate"]


def load(name: str, path: Path):
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


rho = load("swepl_analyse", BENCH / "swebench-pl/analysis/analyse.py").rho
combined = load("t2_analyse", BENCH / "tau2-tb4-pl/analysis/analyse.py").combined


def kappa(a: pd.Series, b: pd.Series) -> float:
    cats = sorted(set(a) | set(b))
    po = (a.values == b.values).mean()
    pe = sum((a == c).mean() * (b == c).mean() for c in cats)
    return round(float((po - pe) / (1 - pe)), 3) if pe < 1 else 1.0


def main() -> None:
    lab = pd.read_csv(RUN, dtype={"instance_id": str})
    lab = lab[lab["valid"].astype(bool) & lab["writer_model"].astype(str).str.startswith(MODEL)]
    wide = lab.assign(d=lab["rubric_ref"].str.removeprefix("v2/")).pivot(
        index="instance_id", columns="d", values="level").reindex(columns=DIMS)
    meta = pd.read_csv(ROOT / "data/instances/meta_eqbench4.csv").set_index("instance_id")

    oc = pd.read_csv(HERE / "labels/eq4-outcome/outcomes.csv")
    first = oc[(oc["repeat"] == 1) & oc["valid"]]
    per = first.assign(yes=first["core"] == "yes", ack=first["core"].isin(["yes", "partly"])).groupby("scenario")
    scen = pd.DataFrame({"n_models": per.size(), "disclosure_rate": per["yes"].mean(),
                         "acknowledged_rate": per["ack"].mean(),
                         "items_rate": per["n_voiced"].sum() / per["n_items"].sum()})
    df = wide.join(scen).join(meta[["source_type"]]).rename(columns={"source_type": "benchmark"})

    out = {"n": {"scenarios": int(len(df)), "labelled": {d: int(df[d].notna().sum()) for d in DIMS},
                 "outcome_cells_valid": int(len(first)), "outcome_cells_total": int((oc["repeat"] == 1).sum())},
           "levels": {d: {int(k): int(v) for k, v in df[d].value_counts().sort_index().items()} for d in DIMS},
           "levels_by_source": {s: {d: {int(k): int(v) for k, v in g[d].value_counts().sort_index().items()}
                                    for d in DIMS} for s, g in df.groupby("benchmark")},
           "outcome_summary": df[OUTCOMES].describe().round(3).to_dict(),
           "within_source": {}, "pooled": {}}
    for y in OUTCOMES:
        for d in DIMS:
            out["within_source"][f"{d}_vs_{y}"] = combined(df, d, y, "negative")
            h = df.dropna(subset=[d, y])
            out["pooled"][f"{d}_vs_{y}"] = (rho(h[d], h[y], "negative") if h[d].nunique() > 1
                                            else {"n": int(len(h)), "note": "one level: not testable"})

    rep = oc[oc["valid"]]
    pairs = rep[rep["repeat"] == 2].assign(base=lambda t: t["cell"].str.removesuffix("~r2")).merge(
        rep[rep["repeat"] == 1][["cell", "core", "n_voiced"]], left_on="base", right_on="cell", suffixes=("_2", "_1"))
    out["repeatability"] = {"n": int(len(pairs)),
                            "core_exact": round(float((pairs["core_2"] == pairs["core_1"]).mean()), 3),
                            "core_kappa": kappa(pairs["core_1"], pairs["core_2"]),
                            "items_exact": round(float((pairs["n_voiced_2"] == pairs["n_voiced_1"]).mean()), 3)}
    lb = pd.read_csv(BENCH / "eqbench4-data/leaderboard.csv").set_index("slug")
    mod = first.assign(yes=first["core"] == "yes").groupby("model")["yes"].mean().to_frame("disclosure_rate")
    mod = mod.join(lb["elo"])
    r, p = spearmanr(mod["disclosure_rate"], mod["elo"])
    out["model_level"] = {"n": int(len(mod)), "rho_disclosure_vs_elo": round(float(r), 3),
                          "p_two_sided": float(f"{p:.3g}"),
                          "disclosure_rate": mod["disclosure_rate"].round(3).to_dict()}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results/analysis.json").write_text(json.dumps(out, indent=2, default=str) + "\n")
    print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
