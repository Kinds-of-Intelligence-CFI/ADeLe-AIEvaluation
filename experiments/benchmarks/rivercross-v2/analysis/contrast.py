"""Pre-registered analysis of rc-contrast (PREREGISTRATION.md, amendment 1). Writes results/contrast.json.

Each state's PLp label is the median of its three repeats (answers by claude-opus-5-5 only; a state needs at
least two). For each pair, the difference is PLp(high) - PLp(low):
  search pairs: same puzzle and cost-to-go, 'high' has 2 or more extra decision points;
  length pairs: same puzzle and decision points, 'high' has 2 or more extra crossings left.
  S1  search effect: mean difference at least 0.5, and a one-sided sign test on untied pairs with p < 0.05;
  L1  length effect: the same on the length pairs.

    python experiments/benchmarks/rivercross-v2/analysis/contrast.py
"""

import json
from math import comb
from pathlib import Path

import pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parents[1]
MODEL = "claude-opus-5-5"


def sign_test(d: pd.Series) -> dict:
    up, down = int((d > 0).sum()), int((d < 0).sum())
    n = up + down
    p = sum(comb(n, k) for k in range(up, n + 1)) / 2 ** n if n else 1.0
    return {"higher": up, "lower": down, "tied": int((d == 0).sum()), "p_one_sided": round(p, 4)}


def main() -> None:
    lab = pd.read_csv(HERE / "labels/rc-contrast/labels_long.csv")
    lab = lab[lab["valid"] & (lab["writer_model"] == MODEL)]
    per = lab.groupby("instance_id")["level"]
    plp = per.median()[per.count() >= 2]
    truth = pd.read_csv(HERE / "frames/contrast_truth.csv").set_index("custom_id")
    pairs = pd.read_csv(HERE / "frames/contrast_pairs.csv")
    pairs["d"] = pairs["high"].map(plp) - pairs["low"].map(plp)

    out = {"states_labelled": int(len(plp)), "states": int(len(truth)),
           "repeat_agreement": round(float(lab.groupby("instance_id")["level"].nunique().eq(1).mean()), 3)}
    for kind, key in (("search", "S1"), ("length", "L1")):
        d = pairs.loc[pairs["kind"] == kind, "d"].dropna()
        st = sign_test(d)
        out[kind] = {"pairs": int(len(d)), "mean_difference": round(float(d.mean()), 3), **st,
                     "differences": [float(x) for x in d]}
        out[f"{key}_holds"] = bool(d.mean() >= 0.5 and st["p_one_sided"] < 0.05)
    df = truth.join(plp.rename("PLp")).dropna(subset=["PLp"])
    out["exploratory"] = {
        "PLp_vs_ctg": round(float(spearmanr(df["PLp"], df["ctg"])[0]), 3),
        "PLp_vs_decision_points": round(float(spearmanr(df["PLp"], df["T"])[0]), 3),
        "ctg_vs_decision_points": round(float(spearmanr(df["ctg"], df["T"])[0]), 3),
        "mean_PLp_by_ctg": {int(k): round(float(v), 2) for k, v in df.groupby("ctg")["PLp"].mean().items()},
        "mean_PLp_by_decision_points": {int(k): round(float(v), 2) for k, v in df.groupby("T")["PLp"].mean().items()},
    }
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results/contrast.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
