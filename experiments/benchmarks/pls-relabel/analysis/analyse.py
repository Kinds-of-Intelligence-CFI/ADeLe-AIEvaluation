"""Pre-registered analysis of pls-relabel: PLs after the 2026-10-04 example change, on the clean sets of the PL
studies. Writes results/analysis.json.

New labels: mass runs pls-relabel and pls-relabel-long (Opus 5.5 low, v2 prompt); only valid answers written by
claude-opus-5-5 count. Old labels: v2/PLs in each study's release/labels.csv (the text before the change). Per set:
level distributions (old, new), the old-to-new crosstab, the share unchanged, the mean shift, and Spearman with the
set's primary outcome for both (as ms-benchmarks: swebench-pl's `rho`, predicted negative; tau2 within domain,
combined by Fisher z). A rubric with one level in a set is reported as not testable there.

    python experiments/benchmarks/pls-relabel/analysis/analyse.py
"""

import importlib.util
import json
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parents[1]
BENCH = HERE.parent
MODEL = "claude-opus-5-5"
RUNS = [BENCH / f"mass-annotation/runs/{r}/labels.csv" for r in ("pls-relabel", "pls-relabel-long")]
SETS = {"swe-bench-verified": ("swebench-clean", "solve_rate"), "terminal-bench-4.0.0": ("tb4-clean", "solve_rate"),
        "terminal-bench-science-0.1": ("tbsci-pl", "solve_rate"), "deepswe-v1.1": ("deepswe-clean", "solve_rate"),
        "frontierswe-v2": ("frontierswe-pl", "solve_rate_0.9"), "programbench": ("programbench-pl", "solve_rate_0.9")}
TAU2 = ["tau2-airline", "tau2-retail", "tau2-banking_knowledge"]


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
    lab = pd.concat([pd.read_csv(r, dtype={"instance_id": str}) for r in RUNS if r.exists()])
    lab = lab[lab["valid"].astype(bool) & lab["writer_model"].astype(str).str.startswith(MODEL)]
    return lab[lab["rubric_ref"] == "v2/PLs"][["benchmark", "instance_id", "level"]].rename(columns={"level": "new"})


def old_labels(sub: pd.DataFrame) -> pd.DataFrame:
    parts = []
    for bench, (study, _) in SETS.items():
        lab = pd.read_csv(BENCH / study / "release/labels.csv", dtype={"instance_id": str})
        parts.append(lab[lab["rubric"] == "v2/PLs"][["instance_id", "level"]].assign(benchmark=bench))
    # tau2 ids repeat across domains, so its domain comes from labels_wide
    w = pd.read_csv(BENCH / "tau2-clean/release/labels_wide.csv", dtype={"instance_id": str})
    parts.append(w[["benchmark", "instance_id", "v2/PLs"]].rename(columns={"v2/PLs": "level"}))
    old = pd.concat(parts).rename(columns={"level": "old"})
    assert not old.duplicated(["benchmark", "instance_id"]).any()
    return sub.merge(old, how="left")


def test(g: pd.DataFrame, col: str, tau2: bool) -> dict:
    h = g.dropna(subset=[col, "outcome"])
    if tau2:
        return combined(h, col, "outcome", "negative")
    if h[col].nunique() < 2:
        return {"n": int(len(h)), "note": "one level: not testable"}
    return rho(h[col], h["outcome"], "negative")


def main() -> None:
    sub = pd.concat([pd.read_csv(HERE / f, dtype={"instance_id": str}) for f in ("subset.csv", "subset_long.csv")])
    df = old_labels(sub[["benchmark", "instance_id"]]).merge(new_labels(), how="left").merge(outcomes(), how="left")
    out = {"n": {}, "unlabelled": {}, "levels": {}, "crosstab": {}, "unchanged": {}, "mean_shift": {}, "spearman": {}}
    groups = {b: g for b, g in df.groupby("benchmark") if b not in TAU2} | {"tau2": df[df["benchmark"].isin(TAU2)]}
    for name, g in groups.items():
        both = g.dropna(subset=["old", "new"])
        out["n"][name] = int(len(g))
        out["unlabelled"][name] = {c: int(g[c].isna().sum()) for c in ("old", "new")}
        out["levels"][name] = {c: {str(int(k)): int(v) for k, v in g[c].value_counts().sort_index().items()}
                               for c in ("old", "new")}
        ct = pd.crosstab(both["old"].astype(int), both["new"].astype(int))
        out["crosstab"][name] = {str(i): {str(j): int(ct.loc[i, j]) for j in ct.columns} for i in ct.index}
        out["unchanged"][name] = round(float((both["old"] == both["new"]).mean()), 3)
        out["mean_shift"][name] = round(float((both["new"] - both["old"]).mean()), 3)
        out["spearman"][name] = {c: test(g, c, name == "tau2") for c in ("old", "new")}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results/analysis.json").write_text(json.dumps(out, indent=2, default=str) + "\n")
    print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
