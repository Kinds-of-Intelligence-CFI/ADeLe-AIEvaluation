"""Pre-registered analysis of the MSc Level 4 note test (PREREGISTRATION.md).

Labels: labels/msc-l4-1 (and msc-l4-2 for pass 2). An item's label per arm is the lower median of its counted
labels (parsed, written by claude-opus-5-5). Rules:
  R   every MSc check of the MS lab regression that holds under the current text also holds under the candidate;
      a candidate-only failure is confirmed if it persists with the pass-2 labels of its items
  M1  candidate: B at 4 or more on at least 7 of 8 pairs
  M2  candidate: A below B on at least 6 of 8 pairs
  H1  fresh human items: the candidate matches Pablo exactly at least as often as the current text
  H2  fresh human items: no item two or more from Pablo under the candidate that is within 1 under the current text
The candidate passes if R, M1, M2, H1 and H2 all hold.

    python experiments/benchmarks/msc-l4-note/analysis/analyse.py
"""

import json
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE.parent / "ms-lab-regression" / "analysis"))
import analyse as lab  # noqa: E402  (the MS lab regression's checks)

ARMS = ("current", "candidate")
MSC_CHECKS = ["P-MSc placement", "F-on-MSc no leak", "L r30 MSc minimal pairs", "L r36 MSc pair", "L r75 MSc ladder",
              "L r70 human labels", "B MSc high", "B MSc mid-band", "B MSc anchors"]


def medians(run: str) -> pd.DataFrame:
    d = pd.read_csv(HERE / f"labels/{run}/labels_long.csv")
    d = d[d["valid"] & d["writer_model"].astype(str).str.startswith(lab.OPUS)]
    return (d.groupby(["item_id", "arm"])["level"].apply(lambda s: lab.lower_median([int(x) for x in s]))
            .unstack("arm"))


def check_holds(items: pd.DataFrame, med: pd.Series, name: str) -> bool:
    """One lab check on one arm's medians (items with set stripped of 'R-', aliases resolved)."""
    sel = items[lab.CHECKS[name][0](items)]
    if name in lab.PAIRS:
        pairs, need = lab.PAIRS[name]
        ok = 0
        for lo, hi, change in pairs:
            if lo not in med.index or hi not in med.index or pd.isna(med[lo]) or pd.isna(med[hi]):
                continue
            ok += (med[hi] == med[lo]) if change == "same" else (med[hi] > med[lo])
        return bool(ok >= need)
    def m(i):
        v = med.get(i)
        return None if v is None or pd.isna(v) else int(v)
    return all(lab.item_ok(r.check, r.target, m(r.judged_as or r.item_id)) is not False
               for r in sel.itertuples(index=False))


def main() -> None:
    items = pd.read_csv(HERE / "items.csv", dtype=str, keep_default_na=False)
    m1 = medians("msc-l4-1")
    p2 = HERE / "labels/msc-l4-2/labels_long.csv"
    m2 = medians("msc-l4-2") if p2.exists() else None
    r = items[items["set"].str.startswith("R-")].copy()
    r["set"] = r["set"].str.removeprefix("R-")
    out = {"R": {}, "M": {}, "H": {}}

    # R: the lab checks, per arm
    failed_new = []
    for name in MSC_CHECKS:
        holds = {a: check_holds(r, m1[a], name) for a in ARMS}
        out["R"][name] = {"kind": lab.CHECKS[name][1], **{f"holds_{a}": holds[a] for a in ARMS}}
        if holds["current"] and not holds["candidate"]:
            failed_new.append(name)
    confirmed = []
    for name in failed_new:
        if m2 is None:
            confirmed.append(name + " (pass 2 not run)")
            continue
        merged = m1["candidate"].copy()
        merged.update(m2["candidate"])
        if not check_holds(r, merged, name):
            confirmed.append(name)
    out["R"]["candidate_only_failures"] = failed_new
    out["R"]["confirmed"] = confirmed
    judged_r = r[r["status"] == "judged"]["item_id"]
    both = m1.loc[m1.index.isin(judged_r)].dropna()
    out["R"]["items_changed"] = {i: {a: int(both.loc[i, a]) for a in ARMS}
                                 for i in both.index if both.loc[i, "current"] != both.loc[i, "candidate"]}
    rule_r = not confirmed

    # M: minimal pairs
    rows = []
    for p in sorted({i[2:-1] for i in items["item_id"] if i.startswith("M-")}, key=int):
        a, b = m1.loc[f"M-{p}A"], m1.loc[f"M-{p}B"]
        rows.append({"pair": p, **{f"A_{x}": int(a[x]) for x in ARMS}, **{f"B_{x}": int(b[x]) for x in ARMS}})
    mp_ = pd.DataFrame(rows)
    n = len(mp_)
    b4 = int((mp_["B_candidate"] >= 4).sum())
    a_lt_b = int((mp_["A_candidate"] < mp_["B_candidate"]).sum())
    out["M"] = {"pairs": rows, "M1_B_at_4plus_candidate": f"{b4}/{n}", "M2_A_below_B_candidate": f"{a_lt_b}/{n}",
                "current_A_equals_B": f"{int((mp_['A_current'] == mp_['B_current']).sum())}/{n}",
                "current_B_at_4plus": f"{int((mp_['B_current'] >= 4).sum())}/{n}"}
    rule_m1, rule_m2 = b4 >= 7, a_lt_b >= 6

    # H: human items
    human = pd.read_csv(HERE / "human_labels.csv", dtype={"pablo": "Int64"}).set_index("item_id")
    roles = pd.read_csv(HERE / "human_items.csv").set_index("item_id")["role"]
    h = human.join(m1, how="left").join(roles)
    h = h[h["pablo"].notna()]
    table = [{"item": i, "role": x.role, "pablo": int(x.pablo), "current": int(x.current),
              "candidate": int(x.candidate)} for i, x in h.iterrows()]
    out["H"]["items"] = table
    for role in ("fresh", "dev"):
        s = h[h["role"] == role]
        out["H"][role] = {a: {"n": len(s), "exact": int((s[a] == s["pablo"]).sum()),
                              "within1": int(((s[a] - s["pablo"]).abs() <= 1).sum()),
                              "mean_shift_vs_pablo": round(float((s[a] - s["pablo"]).mean()), 2) if len(s) else None}
                          for a in ARMS}
    fresh = h[h["role"] == "fresh"]
    worse = [i for i, x in fresh.iterrows() if abs(x.candidate - x.pablo) >= 2 and abs(x.current - x.pablo) <= 1]
    out["H"]["H2_items_worse"] = worse
    rule_h1 = out["H"]["fresh"]["candidate"]["exact"] >= out["H"]["fresh"]["current"]["exact"]
    rule_h2 = not worse

    out["rules"] = {"R": rule_r, "M1": rule_m1, "M2": rule_m2, "H1": rule_h1, "H2": rule_h2}
    out["verdict"] = "pass" if all(out["rules"].values()) else "fail"
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results/results.json").write_text(json.dumps(out, indent=2, default=str) + "\n")
    print(json.dumps({k: out[k] for k in ("rules", "verdict")}, indent=2))
    print(json.dumps(out["M"], indent=1, default=str))
    print(json.dumps({k: v for k, v in out["R"].items() if k != "items_changed"}, indent=1))
    print("R items changed:", out["R"]["items_changed"])
    print(json.dumps(out["H"], indent=1, default=str))


if __name__ == "__main__":
    main()
