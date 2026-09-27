"""Pre-registered analysis of tau2-tb4-pl (PREREGISTRATION.md, section Analysis), committed
before any label.

Analysis sets: tau2, the 232 verifiably solvable tasks of airline, retail and banking_knowledge;
Terminal-Bench 4.0.0, its 34 verifiably solvable tasks. Reports the level distributions; Q1,
Spearman rho between each PL rubric and solve rate (PLe and PLs only where they take at least
three values), on tau2 within domain (per-domain rho combined by the inverse-variance-weighted
mean of Fisher z); Q2, PLp against Terminal-Bench's expert time estimate; the tau2 robustness
checks; and the planned exploratory correlations on Terminal-Bench's other 32 tasks and all 66.
Statistics as in swebench-pl (its `rho`): two-sided alpha = 0.05, Fisher-z 95% CI with the
Bonett-Wright standard error; a prediction is supported when p < 0.05 with the predicted sign.

Needs the committed labels and sample.csv. Writes results/analysis.json and results/pl_levels.csv.

    python experiments/benchmarks/tau2-tb4-pl/analysis/analyse.py
"""

import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm, spearmanr

HERE = Path(__file__).resolve().parents[1]
DIMS = ["PLp", "PLe", "PLs"]
RUNS = ["tau2pl-r1", "tb4pl-r1"]
TB4 = "terminal-bench-4.0.0"

_spec = importlib.util.spec_from_file_location("swepl_analyse", HERE.parent / "swebench-pl/analysis/analyse.py")
_swepl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_swepl)
rho = _swepl.rho


def combined(df: pd.DataFrame, dim: str, outcome: str, direction: str) -> dict:
    """Within-domain rho: Spearman per domain, then the inverse-variance-weighted mean of the
    Fisher z (Bonett-Wright variances). A domain where the rubric takes one value contributes
    nothing."""
    per, z, w = {}, [], []
    for bench, g in df.groupby("benchmark"):
        if g[dim].nunique() < 2:
            per[bench] = {"n": len(g), "note": "one level: not included"}
            continue
        per[bench] = rho(g[dim], g[outcome], direction)
        r = spearmanr(g[dim], g[outcome])[0]
        z.append(np.arctanh(r))
        w.append((len(g) - 3) / (1 + r**2 / 2))
    if not z:
        return {"combined": "not testable: one level in every domain", "per_domain": per}
    zbar, se = np.dot(w, z) / sum(w), 1 / np.sqrt(sum(w))
    p = 2 * norm.sf(abs(zbar) / se)
    lo, hi = np.tanh(zbar + np.array([-1.96, 1.96]) * se)
    sign_ok = zbar < 0 if direction == "negative" else zbar > 0
    return {"combined": {"domains": len(z), "n": int(sum(per[b]["n"] for b in per if "rho" in per[b])),
                         "rho": round(float(np.tanh(zbar)), 3), "p_two_sided": float(f"{p:.3g}"),
                         "ci95": [round(float(lo), 3), round(float(hi), 3)], "predicted": direction,
                         "supported": bool(sign_ok and p < 0.05)},
            "per_domain": per}


def tested(df: pd.DataFrame) -> list[str]:
    return ["PLp"] + [d for d in DIMS[1:] if df[d].nunique() >= 3]


def levels(df: pd.DataFrame) -> dict:
    return {d: {int(k): int(v) for k, v in df[d].value_counts().reindex(range(6), fill_value=0).items()}
            for d in DIMS}


def analyse(labels: pd.DataFrame, sample: pd.DataFrame) -> tuple[dict, pd.DataFrame]:
    wide = labels.pivot(index=["benchmark", "instance_id"], columns="demand", values="level")[DIMS]
    df = sample.set_index(["benchmark", "instance_id"]).join(wide, how="inner").reset_index()
    assert len(df) == len(sample) and df[DIMS].notna().all().all()
    tau2 = df[df["benchmark"].str.startswith("tau2-") & df["analysis_set"]]
    tb_all = df[df["benchmark"] == TB4]
    tb, tb_other = tb_all[tb_all["analysis_set"]], tb_all[~tb_all["analysis_set"]]
    assert len(tau2) == 232 and len(tb) == 34 and len(tb_other) == 32

    sets = {**{b: g for b, g in tau2.groupby("benchmark")}, "tau2 (3 domains)": tau2,
            f"{TB4} analysis set": tb, f"{TB4} other 32": tb_other}
    table = pd.DataFrame([{"set": s, "demand": d, "level": k, "tasks": v}
                          for s, g in sets.items() for d, c in levels(g).items() for k, v in c.items()])
    dims_tau2, dims_tb = tested(tau2), tested(tb)
    out = {
        "analysis_sets": {"tau2": {b: len(g) for b, g in tau2.groupby("benchmark")}, TB4: len(tb)},
        "levels": {s: levels(g) for s, g in sets.items()},
        "rubrics_tested_in_Q1": {"tau2": dims_tau2, TB4: dims_tb},
        "Q1_tau2_within_domain": {d: combined(tau2, d, "solve_rate", "negative") for d in dims_tau2},
        "Q1_terminal_bench": {d: rho(tb[d], tb["solve_rate"], "negative") for d in dims_tb},
        "Q2_terminal_bench_PLp_vs_expert_hours": rho(tb["PLp"], tb["expert_hours"], "positive"),
        "robustness_tau2_solve_rate_all_configurations": {
            d: combined(tau2, d, "solve_rate_all", "negative")["combined"] for d in dims_tau2},
        "robustness_tau2_pooled_over_domains": {d: rho(tau2[d], tau2["solve_rate"], "negative") for d in dims_tau2},
        "exploratory_terminal_bench": {
            name: {"PLp_vs_solve_rate": rho(g["PLp"], g["solve_rate"], "negative"),
                   "PLp_vs_expert_hours": rho(g["PLp"], g["expert_hours"], "positive")}
            for name, g in (("other_32", tb_other), ("all_66", tb_all))},
    }
    return out, table


def main() -> None:
    labels = pd.concat(pd.read_csv(HERE / f"labels/{r}/labels_long.csv", dtype={"instance_id": str}) for r in RUNS)
    assert labels["valid"].all() and (labels["judge"] == "opus-low").all()
    sample = pd.read_csv(HERE / "sample.csv", dtype={"instance_id": str})
    out, table = analyse(labels, sample)
    (HERE / "results").mkdir(exist_ok=True)
    table.to_csv(HERE / "results/pl_levels.csv", index=False)
    (HERE / "results/analysis.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
