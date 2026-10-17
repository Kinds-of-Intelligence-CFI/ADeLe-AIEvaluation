"""Amendment 4 analysis: MSc v4 (mscand-v4) against the current text (mscand-1, arm current). Set H stays sealed.

  R  the MSc checks of ../ms-lab-regression/, per arm; a check that holds under the current text and fails under v4 is a
     loss, its items go to pass 2 (both texts). X06R is not ruled (amendment 1). Set P under v4 includes the new
     Level 1 example (P-MSc-L1-atlas, target 1, within 1).
  M  amendment 3's corrected rule: on refusal pairs 1, 2, 3, 4, 8, B at 3 or less on at least 4 of 5 and A, B within one
     level on at least 4 of 5; pairs 5, 6, 7 (B expected at 4+) reported.

    uv run python experiments/benchmarks/ms-candidate/analysis/analyse_v4.py [--version 5]
"""

import argparse

import importlib.util
import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("an", HERE / "analysis/analyse.py")
an = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(an)
reg = an.reg
REFUSAL, NEEDED = ["1", "2", "3", "4", "8"], ["5", "6", "7"]


def meds(path: Path, arm: str) -> dict[str, int]:
    lab = pd.read_csv(path)
    lab = lab[(lab["arm"] == arm) & (lab["rubric"] == "MSc") & lab["valid"].astype(bool)
              & lab["writer_model"].astype(str).str.startswith(reg.OPUS)]
    return {i: reg.lower_median([int(x) for x in g["level"]]) for i, g in lab.groupby("item_id")}


def rule_m(med: dict) -> dict:
    get = lambda p, v: med.get(f"M-{p}{v}")  # noqa: E731
    low_b = sum(get(p, "B") is not None and get(p, "B") <= 3 for p in REFUSAL)
    close = sum(None not in (get(p, "A"), get(p, "B")) and abs(get(p, "A") - get(p, "B")) <= 1 for p in REFUSAL)
    return {"refusal": {p: {"A": get(p, "A"), "B": get(p, "B")} for p in REFUSAL},
            "needed": {p: {"A": get(p, "A"), "B": get(p, "B")} for p in NEEDED},
            "B_at_3_or_less": low_b, "A_B_within_1": close, "holds": low_b >= 4 and close >= 4,
            "needed_B_at_4_plus": sum((get(p, "B") or 0) >= 4 for p in NEEDED)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", type=int, default=4)
    ver = ap.parse_args().version
    run, arm = f"mscand-v{ver}", f"candidate_v{ver}"
    items = an.r_items()
    items = items[items["rubric"] == "MSc"].copy()
    atlas = items[items["item_id"] == "P-MSc-L1-1"].assign(item_id="P-MSc-L1-atlas", text="")
    items_v4 = pd.concat([items, atlas], ignore_index=True)
    cur = meds(HERE / "labels/mscand-1/labels_long.csv", "current")
    v4 = meds(HERE / f"labels/{run}/labels_long.csv", arm)
    names = an.RUBRIC_CHECKS["MSc"]
    c_cur = reg.evaluate(items, reg.resolve(items, cur))
    c_v4 = reg.evaluate(items_v4, reg.resolve(items_v4, v4))
    lost = [n for n in names if c_cur[n]["holds"] and not c_v4[n]["holds"]]
    out = {
        "R": {"lost_pass1": lost,
              "fail_both": [n for n in names if not c_cur[n]["holds"] and not c_v4[n]["holds"]],
              "gained": [n for n in names if not c_cur[n]["holds"] and c_v4[n]["holds"]],
              "checks": {n: {"current": {k: c_cur[n][k] for k in ("holds", "failing", "unlabelled")},
                             "v4": {k: c_v4[n][k] for k in ("holds", "failing", "unlabelled")}} for n in names}},
        "M": {"current": rule_m(cur), "v4": rule_m(v4)},
        "changed": {i: {"current": cur.get(i), "v4": v4.get(i)} for i in sorted(set(cur) | set(v4))
                    if not i.startswith("H-") and cur.get(i) != v4.get(i)},
        "not_ruled": {i: {"current": cur.get(i), "v4": v4.get(i)} for i in an.NOT_RULED},
        "rerun_in_pass2": sorted({i for n in lost for i in c_v4[n]["failing"] + c_v4[n]["unlabelled"]}),
        "H": "sealed",
    }
    f2 = HERE / f"labels/{run}-2/labels_long.csv"
    if lost and f2.exists():  # pass 2: both texts on the items behind a loss
        v4_2 = {**v4, **meds(f2, arm)}
        c2 = reg.evaluate(items_v4, reg.resolve(items_v4, v4_2))
        out["R"]["confirmed"] = [n for n in lost if not c2[n]["holds"]]
        out["pass2"] = {i: {"current": meds(f2, "current").get(i), "v4": meds(f2, arm).get(i)}
                        for i in out["rerun_in_pass2"]}
    out["R"]["verdict"] = ("holds" if not lost else "pending pass 2" if "confirmed" not in out["R"]
                           else "fails" if out["R"]["confirmed"] else "holds")
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / f"results/results_v{ver}.json").write_text(json.dumps(out, indent=2, default=str) + "\n")
    print("R verdict:", out["R"]["verdict"], "| pass 2:", out.get("pass2"))
    print("R lost:", lost or "none", "| fail both:", out["R"]["fail_both"], "| gained:", out["R"]["gained"])
    for a in ("current", "v4"):
        m = out["M"][a]
        print(f"M ({a}): refusal B<=3 {m['B_at_3_or_less']}/5, A-B within 1 {m['A_B_within_1']}/5 -> {m['holds']}; "
              f"needed B at 4+ {m['needed_B_at_4_plus']}/3")
    print("changed:", out["changed"])
    print("not ruled:", out["not_ruled"], "| pass 2:", out["rerun_in_pass2"] or "none")


if __name__ == "__main__":
    main()
