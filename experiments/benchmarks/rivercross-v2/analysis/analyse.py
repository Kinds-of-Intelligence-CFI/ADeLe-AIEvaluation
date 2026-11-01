"""Pre-registered analysis of rivercross-v2 (PREREGISTRATION.md). Writes results/rivercross.json.

Only answers written by claude-opus-5-5 count. Tests:
  T1  rc-state: Spearman of PLp with the solver's cost-to-go, with a Fisher-z 95% interval;
  T2  rc-state: share of the cost-to-go-1 states labelled PLp 0 or 1;
  T3  rc-state: share of PLe labels at the most common level;
  T4  rc-state: share of PLs labels at 2 or below, and Spearman of PLs with cost-to-go;
  T5  rc-play: share of PLe labels at the most common level.
Exploratory: PLs against the puzzle's structure (items, forbidden pairs, boat size), and the new labels
against the older rivercross labels (other rubric text and protocol) for the same states.

    python experiments/benchmarks/rivercross-v2/analysis/analyse.py
"""

import json
import math
from pathlib import Path

import pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[2]
RC = ROOT / "experiments/rivercross"
MODEL = "claude-opus-5-5"


def rho(x: pd.Series, y: pd.Series) -> dict:
    ok = x.notna() & y.notna()
    x, y = x[ok], y[ok]
    if x.nunique() < 2 or y.nunique() < 2:
        return {"n": int(len(x)), "rho": None}
    r, p = spearmanr(x, y)
    z, se = math.atanh(max(min(r, 0.999999), -0.999999)), 1 / math.sqrt(len(x) - 3)
    return {"n": int(len(x)), "rho": round(float(r), 3), "p_two_sided": float(f"{p:.3g}"),
            "ci95": [round(math.tanh(z - 1.96 * se), 3), round(math.tanh(z + 1.96 * se), 3)]}


def labels(run: str) -> pd.DataFrame:
    lab = pd.read_csv(HERE / f"labels/{run}/labels_long.csv")
    lab = lab[lab["valid"] & (lab["writer_model"] == MODEL)]
    return lab.pivot(index="instance_id", columns="demand", values="level")


def structure(instance: str) -> dict:
    """Items, forbidden pairs and boat size, read from the puzzle name (e.g. cycle-4-boat-2)."""
    parts = instance.split("-")
    if parts[0] == "missionaries":
        return {"topology": "missionaries-cannibals", "items": 2 * int(parts[2]), "forbidden_pairs": None, "boat": 2}
    n, top = int(parts[1]), parts[0]
    pairs = {"chain": n - 1, "star": n - 1, "cycle": n, "complete": n * (n - 1) // 2}[top]
    return {"topology": top, "items": n, "forbidden_pairs": pairs, "boat": int(parts[3])}


def share(s: pd.Series, cond) -> float:
    return round(float(cond(s).mean()), 3)


def main() -> None:
    state = labels("rc-state")
    ctg = pd.read_csv(RC / "frames/ground_truth/1b_state_visible_cost_to_go.csv").set_index("custom_id")["dist_to_goal"]
    df = state.join(ctg)
    df = df.join(pd.DataFrame([structure(i.split("#")[0]) for i in df.index], index=df.index))
    play = labels("rc-play")

    t1 = rho(df["PLp"], df["dist_to_goal"])
    one = df[df["dist_to_goal"] == 1]["PLp"].dropna()
    t2 = share(one, lambda s: s <= 1)
    t3 = share(df["PLe"].dropna(), lambda s: s == s.mode()[0])
    t4_low = share(df["PLs"].dropna(), lambda s: s <= 2)
    t4_rho = rho(df["PLs"], df["dist_to_goal"])
    t5 = share(play["PLe"].dropna(), lambda s: s == s.mode()[0])
    checks = {
        "T1_PLp_rho_ge_0.6_and_p_lt_0.05": t1["rho"] is not None and t1["rho"] >= 0.6 and t1["p_two_sided"] < 0.05,
        "T2_ctg1_PLp_le_1_share_ge_0.8": t2 >= 0.8,
        "T3_PLe_modal_share_ge_0.8": t3 >= 0.8,
        "T4a_PLs_le_2_share_ge_0.8": t4_low >= 0.8,
        "T4b_PLs_rho_below_PLp_rho": t1["rho"] is not None and (t4_rho["rho"] or 0) < t1["rho"],
        "T5_play_PLe_modal_share_ge_0.8": t5 >= 0.8,
    }

    old_p = pd.read_csv(RC / "method1b/labels_v11/opus_PLp.csv").set_index("custom_id")["level"]
    old_e = pd.read_csv(RC / "ple/labels/1b/opus_PLe.csv").set_index("custom_id")["level"]

    def against_old(new: pd.Series, old: pd.Series) -> dict:
        m = pd.concat([new.rename("new"), old.rename("old")], axis=1).dropna()
        return {"n": len(m), "exact": round(float((m["new"] == m["old"]).mean()), 3),
                "mean_shift": round(float((m["new"] - m["old"]).mean()), 3)}

    def levels(s: pd.Series) -> dict:
        return {int(k): int(v) for k, v in s.dropna().value_counts().sort_index().items()}

    out = {
        "counts": {"rc-state": {d: int(df[d].notna().sum()) for d in ("PLp", "PLe", "PLs")},
                   "rc-play": int(play["PLe"].notna().sum())},
        "levels": {"rc-state": {d: levels(df[d]) for d in ("PLp", "PLe", "PLs")}, "rc-play PLe": levels(play["PLe"])},
        "cost_to_go": {int(k): int(v) for k, v in ctg.value_counts().sort_index().items()},
        "T1_PLp_vs_cost_to_go": t1,
        "T2_cost_to_go_1": {"n": int(len(one)), "share_PLp_le_1": t2},
        "T3_PLe_modal_share": t3,
        "T4_PLs": {"share_le_2": t4_low, "vs_cost_to_go": t4_rho},
        "T5_play_PLe_modal_share": t5,
        "checks": checks,
        "exploratory": {
            "PLp_mean_by_cost_to_go": {int(k): round(float(v), 2) for k, v in df.groupby("dist_to_goal")["PLp"].mean().items()},
            "PLs_vs_items": rho(df["PLs"], df["items"]),
            "PLs_vs_forbidden_pairs": rho(df["PLs"], df["forbidden_pairs"]),
            "PLs_vs_boat": rho(df["PLs"], df["boat"]),
            "PLp_vs_items": rho(df["PLp"], df["items"]),
            "PLe_vs_cost_to_go": rho(df["PLe"], df["dist_to_goal"]),
            "PLs_mean_by_topology": {k: round(float(v), 2) for k, v in df.groupby("topology")["PLs"].mean().items()},
            "PLp_against_old_opus_labels": against_old(df["PLp"], old_p),
            "PLe_play_against_old_opus_labels": against_old(play["PLe"], old_e),
        },
    }
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results/rivercross.json").write_text(json.dumps(out, indent=2, default=float) + "\n")
    print(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
