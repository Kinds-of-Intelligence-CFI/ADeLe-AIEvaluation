"""Phase A analysis of spv-v2 (decision rules in PREREGISTRATION.md).

Reads labels/<run>/labels_long.csv (from collect.py; only answers written by claude-opus-5-5 count) and prints:
placement of the candidate's examples, ladder and carve items under both texts, the minimal pairs, the items that
need pass 2, and the verdict. Pass-2 labels (run spv2-2), if present, are pooled with pass 1 for the items they cover.

    python experiments/benchmarks/spv-v2/analysis/analyse.py
"""

from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parents[1]
ITEMS = pd.read_csv(HERE / "items.csv", dtype=str).fillna("")


def load(run: str) -> pd.DataFrame:
    p = HERE / "labels" / run / "labels_long.csv"
    if not p.exists():
        return pd.DataFrame()
    d = pd.read_csv(p)
    return d[(d.writer_model == "claude-opus-5-5") & d.valid]


def med(levels: pd.Series) -> int:
    s = sorted(int(x) for x in levels)
    return s[(len(s) - 1) // 2]  # lower middle if even


def medians(d: pd.DataFrame) -> pd.DataFrame:
    return d.groupby(["item_id", "set", "arm"]).agg(
        median=("level", med), labels=("level", lambda s: "".join(str(int(x)) for x in s)), n=("level", "size"),
    ).reset_index()


def main() -> None:
    d1, d2 = load("spv2-1"), load("spv2-2")
    if d1.empty:
        print("no labels yet")
        return
    m1 = medians(d1)

    # Placement
    pl = pd.read_csv(HERE / "placement_items.csv")
    p = m1[m1.set == "P"].merge(pl, on="item_id")
    p["off"] = p["median"] - p["level"]
    exact, far = (p.off == 0).sum(), (p.off.abs() >= 2).sum()
    print(f"\nPLACEMENT (cand, leave-one-out): {exact}/{len(p)} exact, {(p.off.abs() <= 1).sum()} within one, "
          f"{far} off by two or more")
    for r in p.sort_values(["level", "item_id"]).itertuples():
        flag = "" if r.off == 0 else ("  <-- off by %+d" % r.off)
        print(f"  L{r.level} {r.labels}  {r.bullet[:90]}{flag}")

    # Ladder, carves and pairs; pass 2 pooled where present
    lm = pd.concat([d1[d1.set != "P"], d2]) if not d2.empty else d1[d1.set != "P"]
    m = medians(lm)
    wide = m.pivot_table(index="item_id", columns="arm", values=["median", "labels"], aggfunc="first")
    wide.columns = [f"{a}_{b}" for a, b in wide.columns]
    t = ITEMS.set_index("item_id").join(wide)
    for arm in ("cur", "cand"):
        t[f"hit_{arm}"] = t[f"median_{arm}"].astype(int) == t[f"pred_{arm}"].astype(int)
    print("\nLADDER, CARVES AND PAIRS (median; labels)")
    print(f"  {'item':6} {'tests':32} {'cur':>9} {'pred':>4} {'cand':>9} {'pred':>4}")
    for i, r in t.iterrows():
        print(f"  {i:6} {r.tests[:32]:32} {r.labels_cur:>5} {int(r.median_cur):>3} {r.pred_cur:>4}"
              f" {r.labels_cand:>5} {int(r.median_cand):>3} {r.pred_cand:>4}{'' if r.hit_cand else '  <-- cand miss'}")
    L = t[t.set == "L"]
    off2 = t[(t.median_cand.astype(int) - t.pred_cand.astype(int)).abs() >= 2]
    carves = L[L.tests.str.contains("carve")]
    carve_ok = all(int(r.median_cand) <= (0 if "generation" in r.tests else 1) for _, r in carves.iterrows())
    fine = ["L-V2s", "L-V2f", "M1b", "M3b"]
    fine_ok = all(int(t.loc[i, "median_cand"]) == 2 for i in fine)

    pairs, lost = [], []
    for pid in sorted(t.pair[t.pair != ""].unique()):
        a, b = t.loc[f"{pid}a"], t.loc[f"{pid}b"]
        holds = {arm: int(b[f"median_{arm}"]) >= int(a[f"median_{arm}"]) + 1 for arm in ("cur", "cand")}
        pairs.append((pid, holds))
        if not holds["cand"]:
            lost.append(pid)
    print("\nPAIRS (b at least one level above a)")
    for pid, h in pairs:
        print(f"  {pid}: cur {'holds' if h['cur'] else 'fails'}, cand {'holds' if h['cand'] else 'fails'}")

    print(f"\nL items at prediction (cand): {L.hit_cand.sum()}/{len(L)}; (cur): {L.hit_cur.sum()}/{len(L)}")
    print(f"items off by two or more (cand): {list(off2.index) or 'none'}")
    print(f"carves bind (cand): {carve_ok}; fineness items at 2 (cand): {fine_ok}")
    need2 = sorted(set(off2.index) | {f"{p}{s}" for p in lost for s in 'ab'})
    if d2.empty and need2:
        print(f"\nPASS 2 NEEDED: {need2}")
    verdict = (exact >= 19 and far == 0 and L.hit_cand.sum() >= 13 and off2.empty and carve_ok and fine_ok
               and not lost)
    print(f"\nVERDICT (rules 1-4): {'PASS' if verdict else 'FAIL'}"
          + ("" if d2.empty and need2 == [] else "" if not d2.empty else " (provisional, pass 2 pending)"))


if __name__ == "__main__":
    main()
