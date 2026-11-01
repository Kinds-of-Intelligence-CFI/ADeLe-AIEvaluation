"""Exploratory tables for the lab regression of PLp candidate C (not pre-registered).

Writes results/exploratory.json and prints:
  - placement (set P): the level each example got under each text;
  - leaks (set F): foreign examples at PLp 3 or more under each text;
  - the current text against the stored lab medians, item by item;
  - per judge: exact agreement between the texts, and mean level under each;
  - how C's judges refer to the new sentence (needs the gitignored raw answers).

    python experiments/benchmarks/plp-candidate/lab-regression/analysis/exploratory.py
"""

import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[3]


def main() -> None:
    items = pd.read_csv(HERE / "items.csv").set_index("item_id")
    res = json.loads((HERE / "results/regression.json").read_text())
    med = pd.DataFrame(res["medians_pass1"]).T
    lab = pd.read_csv(HERE / "labels/labreg-r1/labels_long.csv")
    wide = lab.pivot_table(index=["item_id", "judge"], columns="arm", values="level", aggfunc="first")

    placement = [{"item": i, "level": int(items.loc[i, "target"]), "cur": int(med.loc[i, "cur"]), "C": int(med.loc[i, "C"])}
                 for i in items.index if items.loc[i, "set"] == "P"]
    leaks = {arm: sorted(i for i in med.index if items.loc[i, "set"] == "F" and med.loc[i, arm] >= 3) for arm in ("cur", "C")}
    st = items.dropna(subset=["stored_median"])
    st = st[st.index.isin(med.index)]
    vs_stored = [{"item": i, "stored": int(s), "cur": int(med.loc[i, "cur"])}
                 for i, s in st["stored_median"].items() if int(med.loc[i, "cur"]) != int(s)]
    judges = {}
    for j, g in wide.groupby(level="judge"):
        judges[j] = {"exact_between_texts": round(float((g["C"] == g["cur"]).mean()), 3),
                     "mean_cur": round(float(g["cur"].mean()), 3), "mean_C": round(float(g["C"].mean()), 3)}
    carve = None
    raw = ROOT / "data/annotations/labreg-r1/raw.jsonl"
    if raw.exists():
        rows = [json.loads(l) for l in raw.read_text().splitlines()]
        exact = ("knowledge rather than planning", "pitfalls that the method avoids", "knowing the established method")
        carve = {
            "quotes": sorted(f"{r['item_id']} ({r['judge']})" for r in rows
                             if r["arm"] == "C" and any(p in r["response"].lower() for p in exact)),
            "word_knowledge_share": {arm: round(sum("knowledge" in r["response"].lower() for r in rows if r["arm"] == arm)
                                                / sum(r["arm"] == arm for r in rows), 3) for arm in ("cur", "C")},
        }
    out = {"placement": placement, "leaks": leaks, "cur_vs_stored_differences": vs_stored,
           "judges": judges, "carve": carve}
    (HERE / "results/exploratory.json").write_text(json.dumps(out, indent=2) + "\n")
    print(pd.DataFrame(placement).to_string(index=False))
    print("leaks:", leaks)
    print("current vs stored, differences:", vs_stored)
    print("judges:", judges)
    print("carve:", carve)


if __name__ == "__main__":
    main()
