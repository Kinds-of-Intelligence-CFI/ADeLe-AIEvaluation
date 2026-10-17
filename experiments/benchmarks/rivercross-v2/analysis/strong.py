"""Pre-registered analysis of amendment 3 (PREREGISTRATION.md): the solver criterion with Sonnet 5.5 and Opus 5.5.
Writes results/strong.json.

Per solver and state, over the attempts written by the intended model (at least three):
  failure     = share of attempts that did not succeed (illegal move, no answer, or goal not reached);
  non_optimal = share of attempts that did not succeed with the solver's minimum number of crossings.
PLp is the amendment 2 label (median of three Opus-low repeats). Predictors standardised, OLS with HC3 errors.
Per solver:
  F1 failure ~ bits + ctg: bits > 0, p < 0.05      F2 same model: ctg > 0, p < 0.05
  O1 non_optimal ~ bits + ctg: bits > 0, p < 0.05  O2 same model: ctg > 0, p < 0.05
  P1 Spearman of PLp with non_optimal at least 0.3
A criterion whose overall share is below 0.05 is reported as uninformative (ceiling), not as a failed test.

    python experiments/benchmarks/rivercross-v2/analysis/strong.py
"""

import json
from pathlib import Path

import pandas as pd
import statsmodels.api as sm
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parents[1]
SOLVERS = {"rc-solve-sonnet": "claude-sonnet-5-5", "rc-solve-opus": "claude-opus-5-5"}
FLOOR = 0.05


def ols(y: pd.Series, X: pd.DataFrame) -> dict:
    Z = (X - X.mean()) / X.std()
    fit = sm.OLS(y, sm.add_constant(Z)).fit(cov_type="HC3")
    return {c: {"coef": round(float(fit.params[c]), 3), "p": float(f"{fit.pvalues[c]:.3g}")} for c in X.columns} | {
        "r2": round(float(fit.rsquared), 3), "n": int(len(y))}


def main() -> None:
    truth = pd.read_csv(HERE / "frames/search_truth.csv").set_index("custom_id")
    lab = pd.read_csv(HERE / "labels/rc-search/labels_long.csv")
    lab = lab[lab["valid"] & (lab["writer_model"] == "claude-opus-5-5")]
    g = lab.groupby("instance_id")["level"]
    plp = g.median()[g.count() >= 2]
    out = {}
    for run, model in SOLVERS.items():
        sv = pd.read_csv(HERE / f"labels/{run}/solve_long.csv")
        n_all = len(sv)
        sv = sv[sv["writer_model"] == model]
        per = sv.groupby("custom_id")
        keep = per.size()[per.size() >= 3].index
        st = pd.DataFrame({"failure": 1 - per["success"].mean(), "non_optimal": 1 - per["optimal"].mean()}).loc[keep]
        df = truth.join(st, how="inner").join(plp.rename("PLp"))
        kinds = sv.assign(kind=lambda x: x["success"].map({True: "success"}).fillna(
            x["answer_found"].map({False: "no answer"}))).copy()
        kinds.loc[kinds["kind"].isna() & ~kinds["legal"], "kind"] = "illegal move"
        kinds.loc[kinds["kind"].isna(), "kind"] = "legal, goal not reached"
        res = {"model": model, "attempts": n_all, "attempts_by_model": int(len(sv)), "states": int(len(df)),
               "failure_share": round(float(1 - sv["success"].mean()), 3),
               "non_optimal_share": round(float(1 - sv["optimal"].mean()), 3),
               "outcomes": kinds["kind"].value_counts().to_dict()}
        checks = {}
        for crit, key in (("failure", "F"), ("non_optimal", "O")):
            share = res[f"{crit}_share"]
            m = ols(df[crit], df[["bits", "ctg"]])
            res[f"{crit}_model"] = m
            res[f"{crit}_by_cell"] = {r: {c: round(float(v), 2) for c, v in row.items()} for r, row in
                                      df.groupby(["ctg_bin", "bits_band"])[crit].mean().unstack().iterrows()}
            if share < FLOOR:
                checks[f"{key}1_bits"] = checks[f"{key}2_ctg"] = "uninformative (ceiling)"
            else:
                checks[f"{key}1_bits"] = bool(m["bits"]["coef"] > 0 and m["bits"]["p"] < 0.05)
                checks[f"{key}2_ctg"] = bool(m["ctg"]["coef"] > 0 and m["ctg"]["p"] < 0.05)
        p1 = float(spearmanr(df["PLp"], df["non_optimal"])[0])
        res["P1_PLp_vs_non_optimal"] = round(p1, 3)
        checks["P1_ge_0.3"] = ("uninformative (ceiling)" if res["non_optimal_share"] < FLOOR else bool(p1 >= 0.3))
        res["PLp_vs_failure"] = round(float(spearmanr(df["PLp"], df["failure"])[0]), 3)
        res["checks"] = checks
        out[run] = res
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results/strong.json").write_text(json.dumps(out, indent=2, default=str) + "\n")
    print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
