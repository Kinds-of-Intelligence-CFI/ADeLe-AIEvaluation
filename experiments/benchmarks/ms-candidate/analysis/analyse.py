"""Pre-registered analysis of ms-candidate (PREREGISTRATION.md, with amendment 1).

Labels: an item's label per arm is the lower median of its counted labels (parsed, written by claude-opus-5-5).
  R  the checks of ../ms-lab-regression/ (its analyse.py, imported), evaluated per arm. A check that holds under the
     current text and fails under the candidate is a loss; its items go to pass 2 (mscand-2, both arms). A loss is
     confirmed if the candidate still fails with the pass-2 labels. Checks failing under both texts are reported.
     Amendment 1: battery X06R is not ruled under "B MSc high" (reported only).
  M  candidate arm: A and B within one level on at least 7 of 8 pairs, and B at 3 or less on at least 7 of 8.
  H  sealed until human_labels.csv holds Pablo's labels: then H1 and H2 per rubric (full-task input), H3 (input).

    uv run python experiments/benchmarks/ms-candidate/analysis/analyse.py
"""

import importlib.util
import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[2]
_spec = importlib.util.spec_from_file_location("reg", HERE.parent / "ms-lab-regression/analysis/analyse.py")
reg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(reg)
ARMS = ("current", "candidate")
RUBRIC_CHECKS = {
    "MSc": ["P-MSc placement", "F-on-MSc no leak", "L r30 MSc minimal pairs", "L r36 MSc pair", "L r75 MSc ladder",
            "L r70 human labels", "B MSc high", "B MSc mid-band", "B MSc anchors"],
    "MSm": ["P-MSm placement", "F-on-MSm no leak", "L r60 stated-stance carve", "L r60 anti-count guard",
            "L r60/r69 Level 4/5 boundary", "B MSm low", "B MSm on pure MSc items"],
}
NOT_RULED = {"B-X06R-on-MSc": "amendment 1: the task states nothing it needs from the managers"}


def medians(lab: pd.DataFrame) -> dict[str, dict[str, int]]:
    ok = lab[lab["valid"].astype(bool) & lab["writer_model"].astype(str).str.startswith(reg.OPUS)]
    out = {a: {} for a in ARMS}
    for (item, arm), g in ok.groupby(["item_id", "arm"]):
        out[arm][item] = reg.lower_median([int(x) for x in g["level"]])
    return out


def r_items() -> pd.DataFrame:
    items = pd.read_csv(HERE / "items.csv", dtype={"judged_as": str}, keep_default_na=False)
    items = items[items["set"].str.startswith("R-") & items["status"].isin(["judged", "alias"])].copy()
    items["set"] = items["set"].str.removeprefix("R-")
    for i in NOT_RULED:
        items.loc[items["item_id"] == i, "check"] = "none"
    return items


def rule_m(med: dict[str, int]) -> dict:
    pairs = {p: (med.get(f"M-{p}A"), med.get(f"M-{p}B")) for p in map(str, range(1, 9))}
    close = sum(a is not None and b is not None and abs(a - b) <= 1 for a, b in pairs.values())
    low_b = sum(b is not None and b <= 3 for _, b in pairs.values())
    return {"pairs": {p: {"A": a, "B": b} for p, (a, b) in pairs.items()}, "A_B_within_1": close, "B_at_3_or_less": low_b,
            "holds": close >= 7 and low_b >= 7}


def main() -> None:
    items = r_items()
    lab1 = pd.read_csv(HERE / "labels/mscand-1/labels_long.csv")
    m1 = medians(lab1)
    checks = {a: reg.evaluate(items, reg.resolve(items, m1[a])) for a in ARMS}
    judged_as = dict(zip(items["item_id"], [j or i for i, j in zip(items["item_id"], items["judged_as"])]))
    out = {"R": {}, "M": {a: rule_m(m1[a]) for a in ARMS}}
    rerun = set()
    for dim, names in RUBRIC_CHECKS.items():
        lost = [n for n in names if checks["current"][n]["holds"] and not checks["candidate"][n]["holds"]]
        both = [n for n in names if not checks["current"][n]["holds"] and not checks["candidate"][n]["holds"]]
        gained = [n for n in names if not checks["current"][n]["holds"] and checks["candidate"][n]["holds"]]
        for n in lost:
            rerun |= {judged_as[i] for i in checks["candidate"][n]["failing"] + checks["candidate"][n]["unlabelled"]}
        out["R"][dim] = {"lost_pass1": lost, "fail_both": both, "gained": gained,
                         "checks": {n: {a: {k: checks[a][n][k] for k in ("holds", "failing", "unlabelled")} for a in ARMS}
                                    for n in names}}
    f2 = HERE / "labels/mscand-2/labels_long.csv"
    if rerun and f2.exists():
        m2 = medians(pd.read_csv(f2))
        merged = {a: {**m1[a], **m2[a]} for a in ARMS}
        checks2 = {a: reg.evaluate(items, reg.resolve(items, merged[a])) for a in ARMS}
        for dim in RUBRIC_CHECKS:
            out["R"][dim]["confirmed"] = [n for n in out["R"][dim]["lost_pass1"] if not checks2["candidate"][n]["holds"]]
        out["pass2_medians"] = {i: {a: (m1[a].get(i), m2[a].get(i)) for a in ARMS} for i in sorted(rerun)}
    for dim in RUBRIC_CHECKS:
        r = out["R"][dim]
        r["verdict"] = ("holds" if not r["lost_pass1"] else
                        "pending pass 2" if "confirmed" not in r else ("fails" if r["confirmed"] else "holds"))
    out["rerun_in_pass2"] = sorted(rerun)
    out["changed_between_arms"] = {i: {a: m1[a].get(i) for a in ARMS} for i in sorted(set(m1["current"]) | set(m1["candidate"]))
                                   if not i.startswith("H-") and m1["current"].get(i) != m1["candidate"].get(i)}
    out["not_ruled"] = {i: {"why": w, **{a: m1[a].get(i) for a in ARMS}} for i, w in NOT_RULED.items()}
    by = lab1[lab1["valid"].astype(bool)].groupby(["item_id", "arm"])["level"]
    out["repeat_agreement_all_three_equal"] = round(float((by.nunique() == 1).mean()), 3)
    out["labels"] = {"answers": len(lab1), "counted": int((lab1["valid"].astype(bool)
                                                            & lab1["writer_model"].astype(str).str.startswith(reg.OPUS)).sum())}
    human = HERE / "human_labels.csv"
    out["H"] = "sealed: Pablo's labels are not in yet" if not human.exists() else "see analysis/analyse_h.py"
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results/results_rm.json").write_text(json.dumps(out, indent=2, default=str) + "\n")
    for dim in RUBRIC_CHECKS:
        r = out["R"][dim]
        print(f"{dim} R: {r['verdict']} | lost {r['lost_pass1']} | both fail {r['fail_both']} | gained {r['gained']}")
    for a in ARMS:
        m = out["M"][a]
        print(f"M ({a}): within 1 on {m['A_B_within_1']}/8, B<=3 on {m['B_at_3_or_less']}/8 -> {m['holds']}")
    print("pass 2 items:", out["rerun_in_pass2"] or "none")
    print("changed between arms:", out["changed_between_arms"])
    print("not ruled:", out["not_ruled"], "| repeats agree:", out["repeat_agreement_all_three_equal"], "|", out["labels"])


if __name__ == "__main__":
    main()
