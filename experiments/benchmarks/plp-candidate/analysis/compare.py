"""Pre-registered comparison of plp-candidate (PREREGISTRATION.md): the three rules, the verdict and
the reported extras. Only labels written by the registered judge are used.
Writes results/compare.json.

    python experiments/benchmarks/plp-candidate/analysis/compare.py
"""

import importlib.util
import json
from pathlib import Path

import pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parents[1]
BENCH = HERE.parent
JUDGE_MODEL = "claude-opus-5-5"
PABLO_2 = ["html-js-filter", "layout-config-recreation", "risk-scorer-replay"]
_spec = importlib.util.spec_from_file_location("t2_analyse", BENCH / "tau2-tb4-pl/analysis/analyse.py")
t2 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(t2)


def plp(path: Path) -> pd.Series:
    """PLp levels written by the registered judge, keyed by (benchmark, instance_id)."""
    lab = pd.read_csv(path, dtype={"instance_id": str})
    lab = lab[(lab["demand"] == "PLp") & lab["valid"]]
    if "writer_model" in lab:
        lab = lab[lab["writer_model"] == JUDGE_MODEL]
    if "benchmark" not in lab:
        lab = lab.assign(benchmark="swe-bench-verified")
    return lab.set_index(["benchmark", "instance_id"])["level"].astype(int)


def counts(s: pd.Series) -> dict:
    return {int(k): int(v) for k, v in s.value_counts().sort_index().items()}


def rho(x: pd.Series, y: pd.Series) -> float:
    return round(float(spearmanr(x, y)[0]), 3)


def main() -> None:
    sample = pd.read_csv(HERE / "sample.csv", dtype={"instance_id": str})
    lab = {r: plp(HERE / f"labels/{r}/labels_long.csv") for r in ("cand-tb", "ctrl-tb", "cand-swe", "cand-tau2")}
    ref_tb = plp(BENCH / "tau2-tb4-pl/labels/tb4pl-r1/labels_long.csv")
    ref_tau2 = plp(BENCH / "tau2-tb4-pl/labels/tau2pl-r1/labels_long.csv")
    ref_swe = pd.concat(plp(BENCH / f"swebench-pl/labels/{r}/labels_long.csv") for r in ("swepl-gate-low", "swepl-r1-low"))
    tb4 = "terminal-bench-4.0.0"

    def at(series: pd.Series, ids: list[str]) -> list:
        return [int(series.get((tb4, i), -1)) for i in ids]

    # Rule 1: binding on the three tasks Pablo put at Level 2.
    cand3, ctrl3 = at(lab["cand-tb"], PABLO_2), at(lab["ctrl-tb"], PABLO_2)
    rule1 = sum(v == 2 for v in cand3) >= 2 and sum(v == 2 for v in ctrl3) <= 1

    # Rule 2: SWE-bench, candidate against reference on the same tasks.
    sw = sample[sample["run"] == "cand-swe"].set_index("instance_id")
    c, r = lab["cand-swe"].droplevel(0), ref_swe.droplevel(0)
    ids = [i for i in sw.index if i in c.index and i in r.index]
    swe = {"n": len(ids), "rho_candidate": rho(c[ids], sw.loc[ids, "solve_rate"]),
           "rho_reference": rho(r[ids], sw.loc[ids, "solve_rate"]),
           "mean_shift_candidate_minus_reference": round(float((c[ids] - r[ids]).mean()), 3),
           "levels_candidate": counts(c[ids]), "levels_reference": counts(r[ids])}
    rule2 = abs(swe["rho_candidate"] - swe["rho_reference"]) <= 0.10 and abs(swe["mean_shift_candidate_minus_reference"]) <= 0.25

    # Rule 3: tau2, the pre-registered within-domain test on the candidate labels.
    ta = sample[sample["run"] == "cand-tau2"].copy()
    ta["PLp"] = [lab["cand-tau2"].get((b, i)) for b, i in zip(ta["benchmark"], ta["instance_id"])]
    comb = t2.combined(ta, "PLp", "solve_rate", "negative")
    rule3 = isinstance(comb["combined"], dict) and comb["combined"]["supported"] and comb["combined"]["rho"] <= -0.225
    ta_ref = ta.assign(PLp=[ref_tau2.get((b, i)) for b, i in zip(ta["benchmark"], ta["instance_id"])])

    # Terminal-Bench extras: noise, agreement with Pablo, exploratory correlations.
    tbs = sample[sample["run"] == "cand-tb"].set_index("instance_id")
    pablo = pd.read_csv(BENCH / "tau2-tb4-pl/human-labels/pablo_plp.csv", dtype={"pablo_level": "Int64"}).dropna(subset=["pablo_level"])
    def vs(a: pd.Series, b: pd.Series) -> dict:
        k = a.index.intersection(b.index)
        d = a[k] - b[k]
        return {"n": len(k), "exact": round(float((d == 0).mean()), 3), "mean_shift": round(float(d.mean()), 3)}
    tb = {
        "pablo_2_tasks": dict(zip(PABLO_2, [{"candidate": x, "control": y} for x, y in zip(cand3, ctrl3)])),
        "levels": {"candidate": counts(lab["cand-tb"]), "control": counts(lab["ctrl-tb"]), "reference": counts(ref_tb.loc[[(tb4, i) for i in tbs.index if (tb4, i) in ref_tb.index]])},
        "control_vs_reference_test_retest": vs(lab["ctrl-tb"], ref_tb),
        "candidate_vs_control": vs(lab["cand-tb"], lab["ctrl-tb"]),
        "exact_with_pablo": {name: int(sum(int(s.get((tb4, i), -1)) == int(p) for i, p in zip(pablo["instance_id"], pablo["pablo_level"])))
                             for name, s in (("candidate", lab["cand-tb"]), ("control", lab["ctrl-tb"]), ("reference", ref_tb))},
        "exploratory": {name: {f"PLp_vs_{col}": rho(v, tbs.loc[v.index, col]) for col in ("solve_rate", "expert_hours")}
                        for name, s in (("candidate", lab["cand-tb"]), ("control", lab["ctrl-tb"]))
                        for v in [pd.Series(at(s, list(tbs.index)), index=tbs.index).pipe(lambda x: x[x >= 0])]},
    }
    verdict = "helps" if rule1 and rule2 and rule3 else ("harms" if not (rule2 and rule3) else "no effect")
    out = {"rule1_binding": {"passed": rule1, "candidate": cand3, "control": ctrl3},
           "rule2_swe": {"passed": rule2, **swe},
           "rule3_tau2": {"passed": rule3, "candidate": comb, "reference_combined": t2.combined(ta_ref, "PLp", "solve_rate", "negative")["combined"],
                          "levels_candidate": counts(ta["PLp"].dropna().astype(int)), "levels_reference": counts(ta_ref["PLp"].dropna().astype(int))},
           "terminal_bench": tb, "verdict": verdict}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results/compare.json").write_text(json.dumps(out, indent=2, default=str) + "\n")
    print(json.dumps(out, indent=2, default=str))


if __name__ == "__main__":
    main()
