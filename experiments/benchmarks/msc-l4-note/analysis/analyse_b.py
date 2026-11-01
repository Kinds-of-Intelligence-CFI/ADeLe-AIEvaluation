"""Pre-registered analysis of amendment 1 (candidate B, rule B) of the MSc Level 4 note test (PREREGISTRATION.md).

Labels: rule_b (and current/note on C and fresh2) from labels/msc-l4b-1 (+ msc-l4b-2 for pass 2); current-text labels
of every other item from labels/msc-l4-1. Lower median of counted labels, as in analyse.py. Rules:
  R   every MSc lab check that holds under the current text also holds under rule B (pass 2 confirms a failure)
  M1  rule B: B versions at 4 or more on at least 7 of 8 pairs
  M2  rule B: A below B on at least 6 of 8 pairs
  M3  rule B: C (behaviour unstated) at 4 or more on at least 7 of 8 pairs
  M4  rule B: A below C on at least 6 of 8 pairs
  H1  fresh2: rule B matches Pablo exactly at least as often as the current text
  H2  fresh2: no item two or more from Pablo under rule B that is within 1 under the current text
Candidate B passes if all seven hold.

    python experiments/benchmarks/msc-l4-note/analysis/analyse_b.py
"""

import importlib.util
import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("msc_l4_analyse", HERE / "analysis/analyse.py")
a4 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(a4)
lab = a4.lab


def main() -> None:
    items = pd.read_csv(HERE / "items_b.csv", dtype=str, keep_default_na=False)
    old = a4.medians("msc-l4-1")  # columns current, candidate (= note)
    new = a4.medians("msc-l4b-1")  # columns current, note, rule_b (current/note only on C and fresh2)
    p2 = HERE / "labels/msc-l4b-2/labels_long.csv"
    new2 = a4.medians("msc-l4b-2") if p2.exists() else None
    cur = old["current"].combine_first(new["current"])
    rb = new["rule_b"]
    r = items[items["set"].str.startswith("R-")].copy()
    r["set"] = r["set"].str.removeprefix("R-")
    out = {"R": {}, "M": {}, "H": {}}

    failed = []
    for name in a4.MSC_CHECKS:
        holds = {"current": a4.check_holds(r, cur, name), "rule_b": a4.check_holds(r, rb, name)}
        out["R"][name] = {"kind": lab.CHECKS[name][1], **{f"holds_{k}": v for k, v in holds.items()}}
        if holds["current"] and not holds["rule_b"]:
            failed.append(name)
    confirmed = []
    for name in failed:
        if new2 is None:
            confirmed.append(name + " (pass 2 not run)")
            continue
        merged = rb.copy()
        merged.update(new2["rule_b"])
        if not a4.check_holds(r, merged, name):
            confirmed.append(name)
    out["R"]["rule_b_only_failures"], out["R"]["confirmed"] = failed, confirmed
    judged = r[r["status"] == "judged"]["item_id"]
    both = pd.DataFrame({"current": cur, "rule_b": rb}).loc[lambda d: d.index.isin(judged)].dropna()
    out["R"]["items_changed"] = {i: {k: int(both.loc[i, k]) for k in both} for i in both.index
                                 if both.loc[i, "current"] != both.loc[i, "rule_b"]}
    out["R"]["battery_M01"] = {"current": cur.get("B-M01-on-MSc"), "note": old["candidate"].get("B-M01-on-MSc"),
                               "rule_b": rb.get("B-M01-on-MSc")}

    rows = []
    for p in range(1, 9):
        a, b, c = f"M-{p}A", f"M-{p}B", f"M-{p}C"
        rows.append({"pair": p, "A_current": old["current"][a], "A_note": old["candidate"][a], "A_rule_b": rb[a],
                     "B_current": old["current"][b], "B_note": old["candidate"][b], "B_rule_b": rb[b],
                     "C_current": new["current"][c], "C_note": new["note"][c], "C_rule_b": rb[c]})
    m = pd.DataFrame(rows).astype(int)
    out["M"]["pairs"] = m.to_dict("records")
    n1, n2 = int((m["B_rule_b"] >= 4).sum()), int((m["A_rule_b"] < m["B_rule_b"]).sum())
    n3, n4 = int((m["C_rule_b"] >= 4).sum()), int((m["A_rule_b"] < m["C_rule_b"]).sum())
    out["M"].update({"M1": f"{n1}/8", "M2": f"{n2}/8", "M3": f"{n3}/8", "M4": f"{n4}/8",
                     "C_at_4plus": {k: int((m[f"C_{k}"] >= 4).sum()) for k in ("current", "note", "rule_b")}})

    labels = pd.concat([pd.read_csv(HERE / "human_labels.csv"), pd.read_csv(HERE / "human_labels_b.csv")])
    labels = labels.dropna(subset=["pablo"]).set_index("item_id")["pablo"].astype(int)
    roles = pd.concat([pd.read_csv(HERE / "human_items.csv"), pd.read_csv(HERE / "human_items_b.csv")]) \
        .set_index("item_id")["role"]
    h = pd.DataFrame({"pablo": labels, "role": roles, "current": cur, "note": old["candidate"], "rule_b": rb}) \
        .loc[lambda d: d["pablo"].notna() & d["role"].notna()]
    out["H"]["items"] = [{"item": i, **{k: (None if pd.isna(v) else (v if k == "role" else int(v)))
                                        for k, v in x.items()}} for i, x in h.iterrows()]
    for role in ("fresh2", "fresh", "dev"):
        s = h[h["role"] == role]
        out["H"][role] = {k: {"n": int(s[k].notna().sum()), "exact": int((s[k] == s["pablo"]).sum()),
                              "within1": int(((s[k] - s["pablo"]).abs() <= 1).sum()),
                              "mean_shift_vs_pablo": round(float((s[k] - s["pablo"]).mean()), 2)}
                          for k in ("current", "note", "rule_b") if s[k].notna().any()}
    f2 = h[h["role"] == "fresh2"]
    worse = [i for i, x in f2.iterrows() if abs(x.rule_b - x.pablo) >= 2 and abs(x.current - x.pablo) <= 1]
    out["H"]["H2_items_worse"] = worse

    out["rules"] = {"R": not confirmed, "M1": n1 >= 7, "M2": n2 >= 6, "M3": n3 >= 7, "M4": n4 >= 6,
                    "H1": out["H"]["fresh2"]["rule_b"]["exact"] >= out["H"]["fresh2"]["current"]["exact"],
                    "H2": not worse}
    out["verdict"] = "pass" if all(out["rules"].values()) else "fail"
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results/results_b.json").write_text(json.dumps(out, indent=2, default=str) + "\n")
    print(json.dumps({k: out[k] for k in ("rules", "verdict")}, indent=1))
    print(m.to_string(index=False))
    print(json.dumps({k: v for k, v in out["R"].items()}, indent=1, default=str))
    print(json.dumps({k: v for k, v in out["H"].items() if k != "items"}, indent=1))
    print(pd.DataFrame(out["H"]["items"]).to_string(index=False))


if __name__ == "__main__":
    main()
