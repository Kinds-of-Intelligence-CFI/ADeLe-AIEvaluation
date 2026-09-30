"""Pre-registered analysis of b2-search (PREREGISTRATION.md). Writes results/b2_search.json.

PLp per state = median of three Opus-low repeats (claude-opus-5-5 answers only, at least two), for candidate
B2 (this study) and for the current text (rivercross-v2, run rc-search, same 54 states and prompt builder).
Predictors standardised, OLS with HC3 errors.
  E1 (exit criterion) B2: PLp ~ bits + ctg, bits coefficient > 0 with p < 0.05, and larger than ctg's
  E2  B2's ctg coefficient smaller than the current text's (0.328)
  E3  Spearman of B2's PLp with Opus 5.5's non-optimal share (rivercross-v2 amendment 3) at least 0.3

    python experiments/benchmarks/plp-b2/analysis/analyse.py
"""

import json
from pathlib import Path

import pandas as pd
import statsmodels.api as sm
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parents[1]
RC = HERE.parent / "rivercross-v2"
JUDGE = "claude-opus-5-5"


def plp(path: Path) -> tuple[pd.Series, float]:
    lab = pd.read_csv(path)
    lab = lab[lab["valid"] & (lab["writer_model"] == JUDGE)]
    g = lab.groupby("instance_id")["level"]
    return g.median()[g.count() >= 2], round(float(g.nunique().eq(1).mean()), 3)


def ols(y: pd.Series, X: pd.DataFrame) -> dict:
    Z = (X - X.mean()) / X.std()
    fit = sm.OLS(y, sm.add_constant(Z)).fit(cov_type="HC3")
    return {c: {"coef": round(float(fit.params[c]), 3), "p": float(f"{fit.pvalues[c]:.3g}")} for c in X.columns} | {
        "r2": round(float(fit.rsquared), 3), "n": int(len(y))}


def main() -> None:
    truth = pd.read_csv(RC / "frames/search_truth.csv").set_index("custom_id")
    b2, agree_b2 = plp(HERE / "labels/b2-search/labels_long.csv")
    cur, agree_cur = plp(RC / "labels/rc-search/labels_long.csv")
    sv = pd.read_csv(RC / "labels/rc-solve-opus/solve_long.csv")
    sv = sv[sv["writer_model"] == JUDGE]
    nonopt = 1 - sv.groupby("custom_id")["optimal"].mean()
    df = truth.join(b2.rename("B2")).join(cur.rename("current")).join(nonopt.rename("opus_non_optimal"))
    d = df.dropna(subset=["B2"])
    m_b2, m_cur = ols(d["B2"], d[["bits", "ctg"]]), ols(df.dropna(subset=["current"])["current"],
                                                        df.dropna(subset=["current"])[["bits", "ctg"]])
    e3 = round(float(spearmanr(d["B2"], d["opus_non_optimal"])[0]), 3)
    checks = {"E1_exit": bool(m_b2["bits"]["coef"] > 0 and m_b2["bits"]["p"] < 0.05
                              and m_b2["bits"]["coef"] > m_b2["ctg"]["coef"]),
              "E2_ctg_below_current": bool(m_b2["ctg"]["coef"] < m_cur["ctg"]["coef"]),
              "E3_vs_opus_non_optimal_ge_0.3": bool(e3 >= 0.3)}

    def cells(col: str) -> dict:
        t = d.groupby(["ctg_bin", "bits_band"])[col].mean().round(2).unstack()
        return {r: {c: float(v) for c, v in row.items()} for r, row in t.iterrows()}

    out = {"n_states": int(len(d)), "B2_model": m_b2, "current_model": m_cur,
           "E3_B2_vs_opus_non_optimal": e3,
           "current_vs_opus_non_optimal": round(float(spearmanr(d["current"], d["opus_non_optimal"])[0]), 3),
           "checks": checks,
           "descriptive": {
               "B2_levels": {int(k): int(v) for k, v in d["B2"].value_counts().sort_index().items()},
               "current_levels": {int(k): int(v) for k, v in d["current"].value_counts().sort_index().items()},
               "B2_by_cell": cells("B2"), "current_by_cell": cells("current"),
               "exact_B2_vs_current": round(float((d["B2"] == d["current"]).mean()), 3),
               "mean_shift_B2_minus_current": round(float((d["B2"] - d["current"]).mean()), 3),
               "repeat_agreement": {"B2": agree_b2, "current": agree_cur}}}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results/b2_search.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
