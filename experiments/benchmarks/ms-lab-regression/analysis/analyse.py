"""Pre-registered analysis of the MSm/MSc lab regression (PREREGISTRATION.md).

Pass 1 (ms-labreg1): every judged item of items.csv, v2 prompt, Opus low, three repeats. An item's label is
the median of its counted labels (with two, the lower). A label counts only if it parsed and
claude-opus-5-5 wrote it. An alias item (r70's human labels) takes the label of the item it is judged as.
Each ruled check holds if every one of its items meets its item check (items.csv, column `check`).
Pass 2 (ms-labreg2): the items behind a failed check are judged again, three repeats. A failure is
confirmed if the check still fails with the pass-2 labels of those items. The verdict is pass if no
failure is confirmed. Set S has no rule; it is reported as a table.

    python experiments/benchmarks/ms-lab-regression/analysis/analyse.py [--labels DIR] [--out FILE]
"""

import argparse
import json
import re
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parents[1]
OPUS = "claude-opus-5-5"

# name: (which items, lab or new, what it reproduces)
CHECKS = {
    "P-MSm placement": (lambda i: (i["set"] == "P") & (i["rubric"] == "MSm"), "new",
                        "every MSm example within 1 of its level, examples stripped (no stored result for these examples)"),
    "P-MSc placement": (lambda i: (i["set"] == "P") & (i["rubric"] == "MSc"), "lab",
                        "every MSc example within 1 of its level, examples stripped (r34: all within 1, older text)"),
    "F-on-MSc no leak": (lambda i: (i["set"] == "F") & (i["rubric"] == "MSc"), "lab",
                         "no PL example at Levels 3-5 scores 3+ on MSc (r34)"),
    "F-on-MSm no leak": (lambda i: (i["set"] == "F") & (i["rubric"] == "MSm"), "new",
                         "no PL example at Levels 3-5 scores 3+ on MSm"),
    "L r30 MSc minimal pairs": (lambda i: i["item_id"].str.startswith("L-r30-"), "lab",
                                "r30 H7: at least 3 contrasts as MSc's text predicts (stakes S3-S4: no change; resistance "
                                "R1-R2: a rise; parties A1-A2: no change); S1-S2 is void, so all three must hold; r33 found 4 of 4"),
    "L r36 MSc pair": (lambda i: i["item_id"].str.startswith("L-r36-"), "lab",
                       "D1 and D2 within 1 of r36's MSc medians (4, 5); rebuilt items"),
    "L r60 stated-stance carve": (lambda i: i["item_id"].isin(["L-r60-B1", "L-r60-B2"]), "lab",
                                  "r60 rule 2: B1 <= 1 and B2 >= 3"),
    "L r60 anti-count guard": (lambda i: i["item_id"] == "L-r60-B3", "lab", "r60 rule 3: B3 <= 3"),
    "L r60/r69 Level 4/5 boundary": (lambda i: i["item_id"].isin(["L-r60-B4", "L-r69-M5"]), "lab",
                                     "single nesting stays at 4 (B4 = 4), a three-way interlock reaches 5 (M5 = 5)"),
    "L r75 MSc ladder": (lambda i: i["item_id"].str.startswith("L-r75-"), "lab",
                         "r75 rule 1: all nine medians equal to r61's"),
    "L r70 human labels": (lambda i: i["label_kind"] == "human", "lab",
                           "all seven within 1 of Pablo's label (r70: 6 of 7 exact, 7 of 7 within 1)"),
    "B MSc high": (lambda i: (i["set"] == "B") & (i["rubric"] == "MSc") & (i["check"] == ">=4"), "lab",
                   "pure and co-occurring MSc items at 4 or more (battery-v1 H1, H2)"),
    "B MSc mid-band": (lambda i: (i["set"] == "B") & (i["rubric"] == "MSc") & (i["check"] == "within1"), "lab",
                       "MSc mid-band items within 1 of their registered level (battery-v1 H4)"),
    "B MSc anchors": (lambda i: (i["set"] == "B") & (i["rubric"] == "MSc") & (i["check"] == "<=1"), "lab",
                      "anchors at 1 or less (battery-v1 H3)"),
    "B MSm low": (lambda i: (i["set"] == "B") & (i["rubric"] == "MSm") & (i["own_dim"] != "pure_MSc"), "new",
                  "anchors and pure PL items at 1 or less on MSm"),
    "B MSm on pure MSc items": (lambda i: (i["set"] == "B") & (i["rubric"] == "MSm") & (i["own_dim"] == "pure_MSc"),
                                "new", "M01 and M04 (stated stance with reasons) at 2 or less, M02 at 3 or less, "
                                       "M03 (reasons unstated) within 1 of 3 (battery_targets.csv)"),
}

# Checks ruled on contrasts within pairs rather than on single items: (low item, high item, predicted change).
PAIRS = {"L r30 MSc minimal pairs": ([("L-r30-S1", "L-r30-S2", "same"), ("L-r30-S3", "L-r30-S4", "same"),
                                      ("L-r30-R1", "L-r30-R2", "rise"), ("L-r30-A1", "L-r30-A2", "same")], 3)}


def lower_median(xs: list[int]) -> int | None:
    xs = sorted(xs)
    return xs[(len(xs) - 1) // 2] if xs else None


def item_ok(check: str, target, m) -> bool | None:
    if check == "none" or m is None:
        return None
    if check == "exact":
        return m == int(target)
    if check == "within1":
        return abs(m - int(target)) <= 1
    op, n = re.fullmatch(r"(<=|>=)(\d)", check).groups()
    return m <= int(n) if op == "<=" else m >= int(n)


def load(labels: Path, run: str) -> pd.DataFrame | None:
    f = labels / run / "labels_long.csv"
    if not f.exists():
        return None
    lab = pd.read_csv(f)
    lab["counted"] = lab["valid"].astype(bool) & lab["writer_model"].astype(str).str.startswith(OPUS)
    return lab


def medians(lab: pd.DataFrame) -> dict[str, int]:
    ok = lab[lab["counted"]]
    return ok.groupby("item_id")["level"].apply(lambda s: lower_median([int(x) for x in s])).to_dict()


def resolve(items: pd.DataFrame, med: dict[str, int]) -> dict[str, int | None]:
    """Medians for every ruled item, aliases taking the label of the item they are judged as."""
    out = {}
    for r in items.itertuples(index=False):
        out[r.item_id] = med.get(r.judged_as if r.status == "alias" else r.item_id)
    return out


def evaluate(items: pd.DataFrame, med: dict) -> dict[str, dict]:
    res = {}
    for name, (sel, kind, desc) in CHECKS.items():
        g = items[sel(items)]
        if name in PAIRS:
            pairs, need = PAIRS[name]
            dropped = [f"{a}->{b}" for a, b, _ in pairs if not {a, b} <= set(items["item_id"])]  # void items
            pairs = [p for p in pairs if {p[0], p[1]} <= set(items["item_id"])]
            got = {f"{a}->{b}": (med.get(a), med.get(b), want) for a, b, want in pairs}
            ok = {k: None if None in (x, y) else (y == x if w == "same" else y > x) for k, (x, y, w) in got.items()}
            missing = sorted(i for a, b, _ in pairs for i in (a, b) if med.get(i) is None)
            holds = not missing and sum(bool(v) for v in ok.values()) >= need
            failing = [] if holds else sorted(i for a, b, _ in pairs if ok[f"{a}->{b}"] is False for i in (a, b))
            res[name] = {"kind": kind, "rule": desc, "items": len(g), "holds": holds, "failing": failing,
                         "unlabelled": missing, "void_contrasts": dropped, "contrasts": {k: {"low": x, "high": y, "predicted": w, "as_predicted": ok[k]}
                                                              for k, (x, y, w) in got.items()}}
            continue
        per = {r.item_id: item_ok(r.check, r.target, med.get(r.item_id)) for r in g.itertuples(index=False)}
        failing = sorted(i for i, v in per.items() if v is False)
        missing = sorted(i for i, v in per.items() if v is None)
        res[name] = {"kind": kind, "rule": desc, "items": len(per), "holds": not failing and not missing,
                     "failing": failing, "unlabelled": missing}
    return res


def rates(items: pd.DataFrame, med: dict) -> dict:
    out = {}
    lab = items[(items["check"] != "none") & (items["label_kind"] == "lab")]  # human labels are reported apart
    for (st, rub), g in lab.groupby(["set", "rubric"]):
        d = [(med.get(r.item_id), int(r.target)) for r in g.itertuples(index=False) if med.get(r.item_id) is not None]
        out[f"{st}-{rub}"] = {"items": len(g), "labelled": len(d), "exact": sum(m == t for m, t in d),
                              "within_1": sum(abs(m - t) <= 1 for m, t in d)}
        if st == "F":
            out[f"{st}-{rub}"]["leaks_3plus"] = sorted(r.item_id for r in g.itertuples(index=False)
                                                       if (med.get(r.item_id) or 0) >= 3)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--labels", type=Path, default=HERE / "labels")
    ap.add_argument("--out", type=Path, default=HERE / "results/regression.json")
    args = ap.parse_args()
    items = pd.read_csv(HERE / "items.csv", dtype={"judged_as": str}, keep_default_na=False)
    items = items[items["status"].isin(["judged", "alias"])].copy()
    lab1 = load(args.labels, "ms-labreg1")
    assert lab1 is not None, "no pass-1 labels"
    m1 = medians(lab1)
    med1 = resolve(items, m1)
    checks1 = evaluate(items, med1)
    failed1 = [k for k, v in checks1.items() if not v["holds"]]
    judged_as = dict(zip(items["item_id"], [j or i for i, j in zip(items["item_id"], items["judged_as"])]))
    rerun = sorted({judged_as[i] for k in failed1 for i in checks1[k]["failing"] + checks1[k]["unlabelled"]})

    lab2 = load(args.labels, "ms-labreg2")
    confirmed, pending, pass2 = [], False, None
    if rerun:
        if lab2 is None:
            pending = True
        else:
            m2 = medians(lab2)
            lacking = [i for i in rerun if i not in m2]
            assert not lacking, f"pass 2 lacks {lacking}"
            med2 = resolve(items, {**m1, **m2})
            checks2 = evaluate(items, med2)
            confirmed = [k for k in failed1 if not checks2[k]["holds"]]
            pass2 = {i: {"pass1": m1.get(i), "pass2": m2[i]} for i in rerun}

    verdict = "pending pass 2" if pending else ("fail" if confirmed else "pass")
    by_item = lab1[lab1["counted"]].groupby("item_id")["level"]
    agree = round(float((by_item.nunique() == 1).mean()), 3) if len(by_item) else None
    s = items[items["set"] == "S"]
    s_table = [{"item_id": r.item_id, "own": f"{r.own_dim} L{r.own_level}", "judged_on": r.rubric,
                "median": med1.get(r.item_id), "labels": sorted(int(x) for x in by_item.get_group(r.item_id))
                if r.item_id in by_item.groups else []} for r in s.itertuples(index=False)]
    human = items[items["label_kind"] == "human"]
    human_tab = {r.item_id: {"pablo": int(r.target), "judges_now": med1.get(r.item_id),
                             "judges_r61": int(r.stored) if str(r.stored) != "" else None}
                 for r in human.itertuples(index=False)}
    stored = items[(items["stored"].astype(str).str.fullmatch(r"\d")) & (items["label_kind"] == "lab")]
    stored_cmp = {r.item_id: {"stored": int(r.stored), "now": med1.get(r.item_id)} for r in stored.itertuples(index=False)}
    n_counted = int(lab1["counted"].sum())
    res = {
        "verdict": verdict,
        "checks_pass1": checks1,
        "failed_pass1": failed1,
        "rerun_in_pass2": rerun,
        "pass2_medians": pass2,
        "confirmed_failures": [{"check": k, "kind": CHECKS[k][1]} for k in confirmed],
        "rates_pass1": rates(items, med1),
        "human_labelled": {**human_tab,
                           "exact": sum(v["judges_now"] == v["pablo"] for v in human_tab.values()),
                           "within_1": sum(v["judges_now"] is not None and abs(v["judges_now"] - v["pablo"]) <= 1
                                           for v in human_tab.values())},
        "S_cross_loading": s_table,
        "stored_lab_medians_vs_now": {**stored_cmp,
                                      "exact": sum(v["now"] == v["stored"] for v in stored_cmp.values()),
                                      "n": len(stored_cmp)},
        "repeat_agreement_all_three_equal": agree,
        "labels": {"answers": int(len(lab1)), "counted": n_counted,
                   "set_aside_not_opus_or_unparsed": int(len(lab1)) - n_counted},
        "level_counts": {rub: {int(k): int(v) for k, v in
                               pd.Series([med1[i] for i in g["item_id"] if med1.get(i) is not None])
                               .value_counts().sort_index().items()}
                         for rub, g in items.groupby("rubric")},
        "medians_pass1": {i: med1[i] for i in sorted(med1)},
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(res, indent=2) + "\n")
    print("verdict:", verdict)
    for k, v in checks1.items():
        print(f"  [{v['kind']}] {k}: {'holds' if v['holds'] else 'FAILS ' + str(v['failing'] + v['unlabelled'])}")
    print("re-run in pass 2:", rerun or "none", "| confirmed failures:", confirmed or "none")
    print("rates:", res["rates_pass1"])
    print("human:", res["human_labelled"])
    print("S table:", [(t["item_id"], t["median"]) for t in s_table])
    print("stored vs now:", res["stored_lab_medians_vs_now"]["exact"], "of", len(stored_cmp), "exact",
          "| repeat agreement:", agree, "| labels:", res["labels"])


if __name__ == "__main__":
    main()
