"""Pre-registered analysis of the examples regression. Writes results/analysis.json.

Labels: labels/exreg-1 (and labels/exreg-2 when it exists), valid answers written by claude-opus-5-5. Per rubric:
  B  battery items: new minus old (single labels); a move of 2+ goes to pass 2
  R  real tasks: new minus the task's current Opus label (old text); a move of 2+ goes to pass 2
  N  the noise subset: old (rerun) minus the current label
A move is confirmed if pass 2 (three repeats per text) moves the item the same way. Drift (per rubric, B and R
pooled): more moves one way than the other, sign test p < 0.05, and a larger share moving that way than in N.
A rubric passes if it has no confirmed move of 2+ and no drift.

    python experiments/benchmarks/examples-regression/analysis/analyse.py
"""

import json
from pathlib import Path

import pandas as pd
from scipy.stats import binomtest

HERE = Path(__file__).resolve().parents[1]
DIMS = ["PLp", "PLe", "PLs", "MSm", "MSc"]
MODEL = "claude-opus-5-5"


def load(run: str) -> pd.DataFrame:
    p = HERE / f"labels/{run}/labels_long.csv"
    if not p.exists():
        return pd.DataFrame(columns=["item_id", "set", "dim", "arm", "level"])
    lab = pd.read_csv(p)
    return lab[lab["valid"].astype(bool) & lab["writer_model"].astype(str).str.startswith(MODEL)]


def med(s: pd.Series) -> int:
    v = sorted(s.astype(int))
    return v[(len(v) - 1) // 2]


def main() -> None:
    items = pd.read_csv(HERE / "items.csv", dtype={"instance_id": str}).set_index("item_id")
    l1, l2 = load("exreg-1"), load("exreg-2")
    m2 = {k: med(g["level"]) for k, g in l2.groupby(["item_id", "dim", "arm"])} if len(l2) else {}
    rows = []
    for (item, d), g in l1.groupby(["item_id", "dim"]):
        s = items.loc[item, "set"]
        new = g[g["arm"] == "new"]["level"]
        old = g[(g["arm"] == "old") & (g["set"] == "B")]["level"]
        ref = old.iloc[0] if s == "B" else items.loc[item, f"ref_{d}"]
        if len(new):
            rows.append({"item_id": item, "set": s, "dim": d, "ref": int(ref), "level": int(new.iloc[0])})
        noise = g[g["set"] == "N"]["level"]
        if len(noise):
            rows.append({"item_id": item, "set": "N", "dim": d, "ref": int(items.loc[item, f"ref_{d}"]),
                         "level": int(noise.iloc[0])})
    df = pd.DataFrame(rows)
    df["move"] = df["level"] - df["ref"]
    out = {"n_labels": {"exreg-1": int(len(l1)), "exreg-2": int(len(l2))}, "by_dim": {}, "pass2_needed": []}
    for d in DIMS:
        x = df[(df["dim"] == d) & df["set"].isin(["B", "R"])]
        n = df[(df["dim"] == d) & (df["set"] == "N")]
        up, down = int((x["move"] > 0).sum()), int((x["move"] < 0).sum())
        big = x[x["move"].abs() >= 2]
        moves = []
        for r in big.itertuples(index=False):
            o, w = m2.get((r.item_id, d, "old")), m2.get((r.item_id, d, "new"))
            conf = None if o is None or w is None else bool((w - o) * r.move > 0)
            if conf is None:
                out["pass2_needed"].append(f"{r.item_id}:{d}")
            moves.append({"item_id": r.item_id, "set": r.set, "ref": r.ref, "level": r.level,
                          "pass2_old": o, "pass2_new": w, "confirmed": conf})
        p = binomtest(up, up + down).pvalue if up + down else 1.0
        n_up, n_down = (n["move"] > 0).mean() if len(n) else 0, (n["move"] < 0).mean() if len(n) else 0
        share_up, share_down = up / len(x), down / len(x)
        drift = bool(p < 0.05 and ((up > down and share_up > n_up) or (down > up and share_down > n_down)))
        confirmed = [m for m in moves if m["confirmed"]]
        out["by_dim"][d] = {
            "B": {"n": int((x["set"] == "B").sum()), "same": int(((x["set"] == "B") & (x["move"] == 0)).sum())},
            "R": {"n": int((x["set"] == "R").sum()), "same": int(((x["set"] == "R") & (x["move"] == 0)).sum())},
            "up": up, "down": down, "sign_test_p": round(float(p), 4),
            "noise": {"n": int(len(n)), "same": int((n["move"] == 0).sum()), "up": int((n["move"] > 0).sum()),
                      "down": int((n["move"] < 0).sum())},
            "moves_2plus": moves, "drift": drift,
            "verdict": "pending pass 2" if any(m["confirmed"] is None for m in moves) else
                       "pass" if not (confirmed or drift) else "fail"}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results/analysis.json").write_text(json.dumps(out, indent=2, default=str) + "\n")
    print(json.dumps({d: {k: v for k, v in r.items() if k != "moves_2plus"} | {"n_moves_2plus": len(r["moves_2plus"])}
                      for d, r in out["by_dim"].items()}, indent=1))
    print("pass 2 needed:", out["pass2_needed"])


if __name__ == "__main__":
    main()
