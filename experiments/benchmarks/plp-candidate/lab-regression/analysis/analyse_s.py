"""Pre-registered analysis of the lab regression for PLp candidate S (PREREGISTRATION.md, "Candidate S").

Pass 1 (labreg-s1): S under the v2 prompt, Opus low, three repeats; an item's label is the median
(with two labels, the lower). Reference: the current text's Opus-low label in labreg-r1 (v1 prompt).
Pass 2 (labreg-s2): the items behind a pass-1 loss or a move of two levels, judged again under both
texts with the v2 prompt, three repeats each. A loss or a big move counts only if pass 2 repeats it,
with pass 2's current-text medians as the reference. The checks are those of analyse.py.
S's three new examples (P-S-*) have no reference; their placement is reported, not ruled on.

    python experiments/benchmarks/plp-candidate/lab-regression/analysis/analyse_s.py [--candidate sq]

With --candidate sq, candidate S-q is analysed the same way (labreg-sq1, labreg-sq2 -> regression_sq.json).
"""

import argparse
import json
from pathlib import Path

import pandas as pd
from scipy.stats import binomtest

from analyse import feeders, lower_median, outcomes

HERE = Path(__file__).resolve().parents[1]
OPUS = "claude-opus-5-5"
S_PHRASES = ("size of the search", "higher of the two", "search is small", "search is moderate", "search is large",
             "could go wrong")


def load(run: str) -> pd.DataFrame | None:
    f = HERE / f"labels/{run}/labels_long.csv"
    if not f.exists():
        return None
    lab = pd.read_csv(f)
    lab["counted"] = lab["valid"] & lab["writer_model"].astype(str).str.startswith(OPUS)
    return lab


def medians(lab: pd.DataFrame, arm: str) -> dict[str, int]:
    ok = lab[lab["counted"] & (lab["arm"] == arm)]
    return ok.groupby("item_id")["level"].apply(lambda s: lower_median([int(x) for x in s])).to_dict()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", choices=["s", "sq"], default="s")
    c = ap.parse_args().candidate
    items = pd.read_csv(HERE / "items_s.csv")
    judged = items[items["status"] == "judged"]
    fams = judged.groupby("family")["item_id"].apply(list).to_dict()
    r1 = load("labreg-r1")
    ref = r1[r1["counted"] & (r1["judge"] == "opus-low") & (r1["arm"] == "cur")].set_index("item_id")["level"]
    ref = ref.astype(int).to_dict()
    s1_lab = load(f"labreg-{c}1")
    assert s1_lab is not None, "no pass-1 labels"
    s1 = medians(s1_lab, "S")
    base = items[~items["item_id"].str.startswith("P-S-")]
    o_ref, o_s = outcomes(base, ref), outcomes(base, s1)
    losses = [k for k in o_ref if o_ref[k] and o_s.get(k) is False]
    gains = [k for k in o_ref if o_ref[k] is False and o_s.get(k)]

    def items_of(name):
        f = feeders(name)
        return fams[f] if isinstance(f, str) else f

    moved = {i: s1[i] - ref[i] for i in ref if i in s1 and s1[i] != ref[i]}
    big = sorted(i for i, d in moved.items() if abs(d) >= 2)
    to_rerun = sorted({i for k in losses for i in items_of(k) if i in moved} | set(big))

    s2_lab = load(f"labreg-{c}2")
    confirmed_losses, confirmed_big, pending, pass2 = [], [], False, None
    if to_rerun:
        if s2_lab is None:
            pending = True
        else:
            cur2, s2 = medians(s2_lab, "cur"), medians(s2_lab, "S")
            missing = [i for i in to_rerun if i not in cur2 or i not in s2]
            assert not missing, f"pass 2 lacks {missing}"
            ref2, sx = {**ref, **cur2}, {**s1, **s2}
            o_ref2, o_s2 = outcomes(base, ref2), outcomes(base, sx)
            confirmed_losses = [k for k in losses if o_ref2.get(k) and o_s2.get(k) is False]
            for i in big:
                d2 = sx[i] - ref2[i]
                if d2 != 0 and (d2 > 0) == (moved[i] > 0):
                    confirmed_big.append(i)
            pass2 = {i: {"cur_v2": cur2[i], "S_v2": s2[i]} for i in sorted(cur2)}

    diffs = [s1[i] - ref[i] for i in ref if i in s1]
    down, up = sum(d < 0 for d in diffs), sum(d > 0 for d in diffs)
    p = float(binomtest(down, down + up, 0.5).pvalue) if down + up else 1.0
    per_set = {}
    for st, g in judged[~judged["item_id"].str.startswith("P-S-")].groupby("set"):
        d = [s1[i] - ref[i] for i in g["item_id"] if i in s1 and i in ref]
        per_set[st] = {"items": len(d), "exact": sum(x == 0 for x in d), "down": sum(x < 0 for x in d),
                       "up": sum(x > 0 for x in d), "mean_shift": round(sum(d) / len(d), 3) if d else None}
    new_examples = {r.item_id: {"target": int(r.target), "S": s1.get(r.item_id)}
                    for r in items[items["item_id"].str.startswith("P-S-")].itertuples(index=False)}

    # Repeat agreement within S (all three repeats equal).
    ok = s1_lab[s1_lab["counted"]].groupby("item_id")["level"]
    repeat_agree = round(float((ok.nunique() == 1).mean()), 3)
    levels = pd.Series(list(s1.values())).value_counts().sort_index().to_dict()

    raw = HERE.parents[3] / f"data/annotations/labreg-{c}1/raw.jsonl"
    quotes = None
    if raw.exists():
        rows = [json.loads(l) for l in raw.read_text().splitlines()]
        cite = [r for r in rows if any(ph in r["response"].lower() for ph in S_PHRASES)]
        quotes = {"answers": len(rows), "quoting_S_search_text": len(cite),
                  "on_moved_items": sorted({r["item_id"] for r in cite if r["item_id"] in moved})}

    verdict = "pending pass 2" if pending else ("fail" if confirmed_losses or confirmed_big else "pass")
    res = {
        "verdict": verdict,
        "outcomes": {"n": len(o_ref), "hold_under_reference": sum(bool(v) for v in o_ref.values()),
                     "hold_under_S": sum(bool(v) for v in o_s.values())},
        "losses_pass1": losses, "gains_pass1": gains,
        "moved_items_pass1": {i: int(v) for i, v in sorted(moved.items())},
        "moves_of_two_or_more_pass1": big, "rerun_in_pass2": to_rerun,
        "pass2_medians": pass2,
        "confirmed_losses": confirmed_losses, "confirmed_moves_of_two_or_more": confirmed_big,
        "per_set": per_set,
        "sign_test_item_medians": {"S_lower": int(down), "S_higher": int(up), "p_two_sided": round(p, 4)},
        "new_examples_placement": new_examples,
        "S_level_counts": {int(k): int(v) for k, v in levels.items()},
        "S_repeat_agreement_all_three_equal": repeat_agree,
        "search_text_quotes": quotes,
        "medians_pass1": {i: {"reference": ref.get(i), "S": s1.get(i)} for i in sorted(set(ref) | set(s1))},
        "outcomes_pass1": {k: {"reference": o_ref[k], "S": o_s.get(k)} for k in o_ref},
    }
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / f"results/regression_{c}.json").write_text(json.dumps(res, indent=2) + "\n")
    print("verdict:", verdict)
    print(f"outcomes holding: reference {res['outcomes']['hold_under_reference']}/{len(o_ref)}, "
          f"S {res['outcomes']['hold_under_S']}/{len(o_ref)}")
    print("losses (pass 1):", losses or "none")
    print("gains (pass 1):", gains or "none")
    print("moved items (pass 1):", res["moved_items_pass1"] or "none")
    print("re-run in pass 2:", to_rerun or "none", "| confirmed losses:", confirmed_losses or "none",
          "| confirmed moves of 2+:", confirmed_big or "none")
    print("per set:", per_set)
    print("sign test:", res["sign_test_item_medians"], "| new examples:", new_examples)
    print("S levels:", res["S_level_counts"], "| repeat agreement:", repeat_agree, "| quotes:", quotes)


if __name__ == "__main__":
    main()
