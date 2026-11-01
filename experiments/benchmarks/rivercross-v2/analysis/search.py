"""Pre-registered analysis of amendment 2 (PREREGISTRATION.md): search (bits) against execution length (ctg).
Writes results/search.json.

Per state: PLp = median of the three repeats (claude-opus-5-5 answers only, at least two); failure = share of
the solver's scored attempts that did not succeed (answers by the pilot-chosen model only, at least three).
Both predictors are standardised over the 54 states; OLS with HC3 standard errors.
  H1  PLp ~ bits + ctg: bits coefficient > 0 with two-sided p < 0.05
  H2  the same model: ctg coefficient > 0 with p < 0.05
  H3  bits coefficient larger than ctg coefficient
  C1  failure ~ bits + ctg: bits coefficient > 0 with p < 0.05
  C2  the same model: ctg coefficient > 0 with p < 0.05
  C3  Spearman of PLp with failure at least 0.3
Sensitivity: H1-H3 and C1-C2 with tree_bits in place of bits. Descriptive: VO levels and their Spearman with
ctg and bits; PLp and failure by cell of the 3 x 3 grid; repeat agreement.

    python experiments/benchmarks/rivercross-v2/analysis/search.py --solver-model claude-haiku-4-5-20251001
"""

import argparse
import json
from pathlib import Path

import pandas as pd
import statsmodels.api as sm
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parents[1]
JUDGE = "claude-opus-5-5"


def ols(y: pd.Series, X: pd.DataFrame) -> dict:
    Z = (X - X.mean()) / X.std()
    fit = sm.OLS(y, sm.add_constant(Z)).fit(cov_type="HC3")
    return {c: {"coef": round(float(fit.params[c]), 3), "p": float(f"{fit.pvalues[c]:.3g}")} for c in X.columns} | {
        "r2": round(float(fit.rsquared), 3), "n": int(len(y))}


def srho(a: pd.Series, b: pd.Series) -> float:
    return round(float(spearmanr(a, b, nan_policy="omit")[0]), 3)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--solver-model", required=True)
    solver = ap.parse_args().solver_model
    truth = pd.read_csv(HERE / "frames/search_truth.csv").set_index("custom_id")

    lab = pd.read_csv(HERE / "labels/rc-search/labels_long.csv")
    lab = lab[lab["valid"] & (lab["writer_model"] == JUDGE)]
    g = lab.groupby("instance_id")["level"]
    plp = g.median()[g.count() >= 2]
    vo_lab = pd.read_csv(HERE / "labels/rc-search-vo/labels_long.csv")
    vo = vo_lab[vo_lab["valid"] & (vo_lab["writer_model"] == JUDGE)].set_index("instance_id")["level"]
    sv = pd.read_csv(HERE / "labels/rc-solve/solve_long.csv")
    sv = sv[sv["writer_model"] == solver]
    f = sv.groupby("custom_id")["success"]
    failure = (1 - f.mean())[f.count() >= 3]

    df = truth.join(plp.rename("PLp")).join(vo.rename("VO")).join(failure.rename("failure"))
    a = df.dropna(subset=["PLp"])
    b = df.dropna(subset=["failure"])
    m1, m2 = ols(a["PLp"], a[["bits", "ctg"]]), ols(b["failure"], b[["bits", "ctg"]])
    c3 = srho(df["PLp"], df["failure"])
    checks = {"H1_bits_on_PLp": m1["bits"]["coef"] > 0 and m1["bits"]["p"] < 0.05,
              "H2_ctg_on_PLp": m1["ctg"]["coef"] > 0 and m1["ctg"]["p"] < 0.05,
              "H3_bits_gt_ctg_on_PLp": m1["bits"]["coef"] > m1["ctg"]["coef"],
              "C1_bits_on_failure": m2["bits"]["coef"] > 0 and m2["bits"]["p"] < 0.05,
              "C2_ctg_on_failure": m2["ctg"]["coef"] > 0 and m2["ctg"]["p"] < 0.05,
              "C3_PLp_vs_failure_ge_0.3": c3 >= 0.3}

    def cells(col: str) -> dict:
        t = df.groupby(["ctg_bin", "bits_band"])[col].mean().round(2).unstack()
        return {r: {c: (None if pd.isna(v) else float(v)) for c, v in row.items()} for r, row in t.iterrows()}

    out = {
        "solver_model": solver,
        "n": {"states": int(len(truth)), "PLp": int(df["PLp"].notna().sum()), "VO": int(df["VO"].notna().sum()),
              "failure": int(df["failure"].notna().sum()), "solver_attempts": int(len(sv))},
        "sample_spearman_ctg_bits": srho(truth["ctg"], truth["bits"]),
        "PLp_model": m1, "failure_model": m2, "C3_PLp_vs_failure": c3, "checks": checks,
        "sensitivity_tree_bits": {"PLp_model": ols(a["PLp"], a[["tree_bits", "ctg"]]),
                                  "failure_model": ols(b["failure"], b[["tree_bits", "ctg"]])},
        "descriptive": {
            "PLp_levels": {int(k): int(v) for k, v in df["PLp"].value_counts().sort_index().items()},
            "VO_levels": {int(k): int(v) for k, v in df["VO"].value_counts().sort_index().items()},
            "VO_vs_ctg": srho(df["VO"], df["ctg"]), "VO_vs_bits": srho(df["VO"], df["bits"]),
            "PLp_vs_ctg": srho(df["PLp"], df["ctg"]), "PLp_vs_bits": srho(df["PLp"], df["bits"]),
            "failure_vs_ctg": srho(df["failure"], df["ctg"]), "failure_vs_bits": srho(df["failure"], df["bits"]),
            "PLp_by_cell": cells("PLp"), "failure_by_cell": cells("failure"),
            "PLp_repeat_agreement": round(float(g.nunique().eq(1).mean()), 3),
            "solver_success": round(float(sv["success"].mean()), 3),
            "solver_optimal": round(float(sv["optimal"].mean()), 3),
        },
    }
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results/search.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
