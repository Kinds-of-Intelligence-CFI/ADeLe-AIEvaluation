"""Set H of ms-candidate (PREREGISTRATION.md): the 15 tau2 tasks against Pablo's agent-side labels.

Run only once human_labels.csv holds his labels (columns item_id, enough_info, msc, msm, note). Until then set H is
sealed. Items he marks enough_info = no leave the rules and are reported.
  H1 (per rubric, full-task input): candidate exact matches >= current exact matches
  H2 (per rubric, full-task input): no item 2+ from Pablo under the candidate while within 1 under the current text
  H3 (current text): full-task exact matches >= script exact matches (finding for the input decision)
The MSc candidate is v4 (amendment 4, run mscand-v4); MSm's candidate is mscand-1's.
MSm rules apply only with at least 10 MSm labels.

    uv run python experiments/benchmarks/ms-candidate/analysis/analyse_h.py
"""

import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[2]
OPUS = "claude-opus-5-5"


def lower_median(xs) -> int | None:
    xs = sorted(int(x) for x in xs)
    return xs[(len(xs) - 1) // 2] if xs else None


def main() -> None:
    human = pd.read_csv(HERE / "human_labels.csv", dtype=str, keep_default_na=False).set_index("item_id")
    assert (human[["msc"]] != "").all().all(), "Pablo's MSc labels are not all in; set H stays sealed"
    lab = pd.read_csv(ROOT / "data/annotations/mscand-1/sealed_H.csv")
    # Amendment 4: the MSc candidate is v4 (mscand-v4); mscand-1's MSc candidate arm (v1) is superseded.
    v4 = pd.read_csv(ROOT / "data/annotations/mscand-v4/sealed_H.csv").assign(arm="candidate")
    lab = pd.concat([lab[~((lab["rubric"] == "MSc") & (lab["arm"] == "candidate"))], v4], ignore_index=True)
    lab = lab[lab["valid"].astype(bool) & lab["writer_model"].astype(str).str.startswith(OPUS)]
    parts = lab["item_id"].str.extract(r"^(H-\d+)-(script|full)-on-(MSc|MSm)$")
    lab = lab.assign(task=parts[0], input=parts[1])
    med = lab.groupby(["task", "input", "rubric", "arm"])["level"].apply(lower_median)
    kept = [t for t in human.index if human.loc[t, "enough_info"].strip().lower() not in ("no", "n")]
    out = {"excluded_not_enough_info": [t for t in human.index if t not in kept], "rubrics": {}}
    for dim, col in (("MSc", "msc"), ("MSm", "msm")):
        ref = {t: int(human.loc[t, col]) for t in kept if human.loc[t, col].strip() != ""}
        get = lambda t, inp, arm: med.get((t, inp, dim, arm))  # noqa: E731
        exact = {(inp, arm): sum(get(t, inp, arm) == v for t, v in ref.items())
                 for inp in ("script", "full") for arm in ("current", "candidate")}
        h2 = [t for t, v in ref.items() if get(t, "full", "candidate") is not None and get(t, "full", "current") is not None
              and abs(get(t, "full", "candidate") - v) >= 2 and abs(get(t, "full", "current") - v) <= 1]
        applies = dim == "MSc" or len(ref) >= 10
        out["rubrics"][dim] = {
            "n": len(ref), "rules_apply": applies,
            "exact": {f"{i}/{a}": n for (i, a), n in exact.items()},
            "H1": exact[("full", "candidate")] >= exact[("full", "current")] if applies else None,
            "H2": (not h2) if applies else None, "H2_items": h2,
            "H3": exact[("full", "current")] >= exact[("script", "current")] if applies else None,
            "per_item": {t: {"pablo": v, **{f"{i}/{a}": get(t, i, a) for i in ("script", "full")
                                             for a in ("current", "candidate")}} for t, v in ref.items()},
        }
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results/results_h.json").write_text(json.dumps(out, indent=2, default=str) + "\n")
    print(json.dumps({d: {k: v for k, v in r.items() if k != "per_item"} for d, r in out["rubrics"].items()}, indent=2,
                     default=str))


if __name__ == "__main__":
    main()
