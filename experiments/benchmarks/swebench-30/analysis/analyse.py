"""Pre-registered analysis of swebench-30, run swev30-r4 (PREREGISTRATION.md: Pass/fail checks,
Predictions, Analysis).

Checks: (1) parse rate per judge >= 98%; (2) Sonnet-Opus agreement per dimension on the 30 new
tasks, within-1 >= 80% (exact agreement and quadratic-weighted kappa where both judges vary; a
dimension below 80% is flagged unreliable on this benchmark, not dropped); (3) test-retest on
the 14 anchors, each judge within 1 of the same judge's pilot label (pilot-3bench) on >= 80% of
its 42 anchor cells.
Predictions P1-P6 (descriptive, not gates), level distributions per judge for every dimension
with the v1 and v2 families side by side, and P5/P6 with and without the suspect tasks. As in
swebench-pl: Spearman rho with a Fisher-z 95% CI (Bonett-Wright standard error), two-sided p.

Writes results/analysis.json and results/levels.csv (judge x dimension x level counts).

    python experiments/benchmarks/swebench-30/analysis/analyse.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parents[1]
RUN = "swev30-r4"
JUDGES = ["sonnet", "opus"]
BUCKETS = {"<15 min fix": 0, "15 min - 1 hour": 1, "1-4 hours": 2, ">4 hours": 3}


def qwk(a: pd.Series, b: pd.Series, k: int = 6) -> float | None:
    """Quadratic-weighted Cohen's kappa on levels 0..k-1; None when either rater is constant."""
    if a.nunique() < 2 or b.nunique() < 2:
        return None
    o = np.zeros((k, k))
    for x, y in zip(a.astype(int), b.astype(int)):
        o[x, y] += 1
    w = np.subtract.outer(np.arange(k), np.arange(k)) ** 2
    e = np.outer(o.sum(1), o.sum(0)) / o.sum()
    return round(float(1 - (w * o).sum() / (w * e).sum()), 3)


def rho(x: pd.Series, y: pd.Series, direction: str) -> dict:
    r, p = spearmanr(x, y)
    n = len(x)
    se = np.sqrt((1 + r**2 / 2) / (n - 3))
    lo, hi = np.tanh(np.arctanh(r) + np.array([-1.96, 1.96]) * se)
    sign_ok = r < 0 if direction == "negative" else r > 0
    return {"n": n, "rho": round(float(r), 3), "p_two_sided": float(f"{p:.3g}"),
            "ci95": [round(float(lo), 3), round(float(hi), 3)], "predicted": direction,
            "direction_as_predicted": bool(sign_ok), "p_below_0.05": bool(p < 0.05)}


def share(s: pd.Series, cond) -> float:
    return round(float(cond(s).mean()), 3)


def main() -> None:
    labels = pd.read_csv(HERE / f"labels/{RUN}/labels_long.csv")
    sample = pd.read_csv(HERE / "sample.csv").set_index("instance_id")
    expected = len(pd.read_csv(HERE / f"labels/{RUN}/prompts_index.csv"))
    family = labels.drop_duplicates("demand").set_index("demand")["family"]
    wide = labels.pivot_table(index=["instance_id", "demand"], columns="judge", values="level")
    new_ids = set(sample.index[sample["role"] == "new"])
    anchor_ids = set(sample.index[sample["role"] == "anchor"])
    new = wide[wide.index.get_level_values(0).isin(new_ids)]
    dims = sorted(new.index.get_level_values(1).unique(), key=lambda d: (family[d] != "v1", d))

    # Check 1: parse rate.
    parse = {j: round(float(labels.loc[labels["judge"] == j, "valid"].sum()) / expected, 3) for j in JUDGES}

    # Check 2: inter-judge agreement per dimension on the 30 new tasks.
    agreement = {}
    for d in dims:
        x = new.xs(d, level="demand")[JUDGES].dropna()
        diff = x["sonnet"] - x["opus"]
        within1 = round(float((diff.abs() <= 1).mean()), 3)
        agreement[d] = {"family": family[d], "n": len(x), "within1": within1,
                        "exact": round(float((diff == 0).mean()), 3),
                        "qwk": qwk(x["sonnet"], x["opus"]),
                        "mean_shift_sonnet_minus_opus": round(float(diff.mean()), 3),
                        "passes_80": within1 >= 0.80}

    # Check 3: test-retest against the same judge's pilot label on the 42 anchor cells.
    pilot = pd.read_csv(HERE.parent / "pilot-3bench/labels_long.csv")
    pilot["instance_id"] = pilot["custom_id"].str.removeprefix("swe-")
    pilot = pilot[pilot["instance_id"].isin(anchor_ids)].set_index(["instance_id", "dim", "judge"])["level"]
    retest = {}
    for j in JUDGES:
        now = wide[wide.index.get_level_values(0).isin(anchor_ids)][j].dropna()
        then = pd.Series({(i, d): pilot.get((i, d, j), np.nan) for i, d in now.index}).reindex(now.index)
        diff = (now - then).dropna()
        retest[j] = {"n": len(diff), "within1": round(float((diff.abs() <= 1).mean()), 3),
                     "exact": round(float((diff == 0).mean()), 3),
                     "mean_shift_now_minus_pilot": round(float(diff.mean()), 3),
                     "passes_80": bool((diff.abs() <= 1).mean() >= 0.80),
                     "by_dim_within1": {d: round(float((diff.xs(d, level=1).abs() <= 1).mean()), 3)
                                        for d in ["PLp", "PLe", "PLs"]}}

    # Level distributions, every dimension, per judge, on the 30 new tasks.
    levels = (labels[labels["instance_id"].isin(new_ids)]
              .groupby(["judge", "demand"])["level"].value_counts().unstack(fill_value=0)
              .reindex(columns=range(6), fill_value=0))
    levels.insert(0, "family", [family[d] for _, d in levels.index])

    # Predictions P1-P6, on the 30 new tasks.
    per = {j: new[j].unstack("demand") for j in JUDGES}
    preds = {
        "P1_PLe_eq_3_ge_90pct": {j: share(per[j]["PLe"], lambda s: s == 3) for j in JUDGES},
        "P2_PLs_le_1_ge_90pct": {j: share(per[j]["PLs"], lambda s: s <= 1) for j in JUDGES},
        "P3_PLp_distinct_values_ge_3": {j: int(per[j]["PLp"].nunique()) for j in JUDGES},
        "P4_MSm_eq_0_ge_90pct": {j: share(per[j]["MSm"], lambda s: s == 0) for j in JUDGES},
        "P4_MSc_eq_0_ge_90pct": {j: share(per[j]["MSc"], lambda s: s == 0) for j in JUDGES},
    }
    meta = sample.loc[sorted(new_ids)]
    mean_vo = ((per["sonnet"]["VO"] + per["opus"]["VO"]) / 2).loc[meta.index]
    mean_plp = ((per["sonnet"]["PLp"] + per["opus"]["PLp"]) / 2).loc[meta.index]
    ttf = meta["difficulty"].map(BUCKETS)
    keep = ~meta["suspect"]
    preds["P5_VO_vs_time_to_fix"] = {"all": rho(mean_vo, ttf, "positive"),
                                     "without_suspect": rho(mean_vo[keep], ttf[keep], "positive")}
    preds["P6_PLp_vs_solve_rate"] = {"all": rho(mean_plp, meta["solve_rate"], "negative"),
                                     "without_suspect": rho(mean_plp[keep], meta.loc[keep, "solve_rate"], "negative"),
                                     "per_judge_all": {j: rho(per[j]["PLp"].loc[meta.index], meta["solve_rate"], "negative")
                                                       for j in JUDGES}}
    verdicts = {
        "P1": all(v >= 0.90 for v in preds["P1_PLe_eq_3_ge_90pct"].values()),
        "P2": all(v >= 0.90 for v in preds["P2_PLs_le_1_ge_90pct"].values()),
        "P3": all(v >= 3 for v in preds["P3_PLp_distinct_values_ge_3"].values()),
        "P4": all(v >= 0.90 for k in ["P4_MSm_eq_0_ge_90pct", "P4_MSc_eq_0_ge_90pct"]
                  for v in preds[k].values()),
        "P5": preds["P5_VO_vs_time_to_fix"]["all"]["direction_as_predicted"],
        "P6": preds["P6_PLp_vs_solve_rate"]["all"]["direction_as_predicted"],
    }

    out = {
        "run": RUN, "n_new_tasks": len(new_ids), "n_anchors": len(anchor_ids),
        "checks": {"1_parse_rate_ge_0.98": {"rate": parse, "passes": all(v >= 0.98 for v in parse.values())},
                   "2_interjudge_within1_ge_0.80": {"dimensions_passing": sum(a["passes_80"] for a in agreement.values()),
                                                    "of": len(agreement),
                                                    "flagged_unreliable": [d for d, a in agreement.items() if not a["passes_80"]]},
                   "3_test_retest_within1_ge_0.80": {j: retest[j]["passes_80"] for j in JUDGES}},
        "agreement_by_dimension": agreement,
        "test_retest": retest,
        "predictions": preds,
        "prediction_verdicts": verdicts,
    }
    (HERE / "results").mkdir(exist_ok=True)
    levels.to_csv(HERE / "results/levels.csv")
    (HERE / "results/analysis.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
