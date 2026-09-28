"""Pre-registered analysis of the lab regression for PLp candidate C (PREREGISTRATION.md).

Reads items.csv and labels/labreg-r1/labels_long.csv (pass 1), plus labels/labreg-r2/labels_long.csv
(pass 2, the re-runs) when it exists. Writes results/regression.json and prints a summary.

Rules, in short:
  - A label counts only if the judge's registered model wrote it (writers.csv, via collect.py).
  - The label of an item under one text is the median of its three judges (with two labels, the lower).
  - An outcome is a lab check on one item or pair (for example "PLp-1 scores 3 or more").
  - A loss is an outcome that holds under the current text and fails under C. A gain is the reverse.
  - Every item behind a pass-1 loss, and every item that moves by two levels or more, is judged
    again under both texts (pass 2). A loss or a big move counts only if pass 2 repeats it.
  - C passes if no loss and no move of two levels or more is confirmed.

    python experiments/benchmarks/plp-candidate/lab-regression/analysis/analyse.py
"""

import json
import re
from pathlib import Path

import pandas as pd
from scipy.stats import binomtest

HERE = Path(__file__).resolve().parents[1]
MODELS = {"haiku-low": "claude-haiku-4-5", "sonnet-low": "claude-sonnet-5", "opus-low": "claude-opus-5-5"}
CARVE_PHRASES = ("knowledge rather than planning", "pitfalls that the method avoids", "knowing the established method")


def lower_median(levels: list[int]) -> int | None:
    s = sorted(levels)
    return s[(len(s) - 1) // 2] if s else None


def medians(labels: pd.DataFrame) -> pd.DataFrame:
    """item x arm -> median of the counted labels, and the labels themselves."""
    ok = labels[labels["counted"]]
    g = ok.groupby(["item_id", "arm"])["level"].apply(lambda s: lower_median([int(x) for x in s]))
    return g.unstack("arm")


def outcomes(items: pd.DataFrame, m: dict[str, int | None]) -> dict[str, bool | None]:
    """Every pre-registered outcome, given one text's medians m[item_id]."""
    out = {}
    def get(i):
        return m.get(i)
    for r in items.itertuples(index=False):
        v = get(r.item_id)
        if r.status != "judged" or v is None:
            continue
        if r.set == "P":
            out[f"P {r.item_id} placed at Level {r.target}"] = v == r.target
        elif r.set == "F":
            out[f"F {r.item_id} clean (PLp 2 or less)"] = v <= 2
        elif r.set == "D":
            out[f"D {r.item_id} " + ("on the diagonal (3 or more)" if r.own_dim == "PLp" else "off the diagonal (2 or less)")] = \
                v >= 3 if r.own_dim == "PLp" else v <= 2
    a1, a2, a3, d1, d2 = (get(i) for i in ("M-A1", "M-A2", "M-A3", "M-D1", "M-D2"))
    if None not in (a1, a2):
        out["M A1->A2 rises by 2 or more"] = a2 - a1 >= 2
    if None not in (a1, a3):
        out["M A1->A3 does not rise"] = a3 <= a1
    if d1 is not None:
        out["M D1 stays at 1 or less"] = d1 <= 1
    if d2 is not None:
        out["M D2 reaches 3 or more"] = d2 >= 3
    b = items[(items["set"] == "B") & (items["status"] == "judged")]
    for other in ("PLe", "PLs", "MSc"):
        hi = [(get(r.item_id), getattr(r, f"reg_{other}")) for r in b[b["family"] == "pure_PLp"].itertuples(index=False)]
        hi = [v - x for v, x in hi if v is not None]
        out[f"B H1 PLp>>{other} (gap 3+ on all but at most one item)"] = sum(g < 3 for g in hi) <= 1
        lo = [(get(r.item_id), getattr(r, f"reg_{other}")) for r in b[b["family"] == f"pure_{other}"].itertuples(index=False)]
        lo = [x - v for v, x in lo if v is not None]
        out[f"B H1 {other}>>PLp (gap 3+ on all but at most one item)"] = sum(g < 3 for g in lo) <= 1
    for r in b.itertuples(index=False):
        v = get(r.item_id)
        if v is None:
            continue
        if r.family == "pure_PLp":
            out[f"B D {r.item_id} on the diagonal (3 or more)"] = v >= 3
        elif r.family.startswith("pure_"):
            out[f"B D {r.item_id} off the diagonal (2 or less)"] = v <= 2
        elif r.family.startswith("co_PLp"):
            out[f"B H2 {r.item_id} PLp 4 or more"] = v >= 4
        elif r.family == "low":
            out[f"B H3 {r.item_id} PLp 1 or less"] = v <= 1
        elif r.family == "mid":
            out[f"B H4 {r.item_id} within 1 of Level {r.target}"] = abs(v - r.target) <= 1
    return out


def feeders(name: str) -> list[str]:
    """The items an outcome depends on."""
    if name.startswith("M A1->A2"):
        return ["M-A1", "M-A2"]
    if name.startswith("M A1->A3"):
        return ["M-A1", "M-A3"]
    if name.startswith("M D1"):
        return ["M-D1"]
    if name.startswith("M D2"):
        return ["M-D2"]
    m = re.match(r"B H1 (\w+)>>(\w+)", name)
    if m:
        return f"pure_{m.group(1)}"  # a battery family, resolved by the caller against items.csv
    if name.startswith("B "):
        return [name.split()[2]]
    return [name.split()[1]]


def load(run: str, items: pd.DataFrame) -> pd.DataFrame | None:
    f = HERE / f"labels/{run}/labels_long.csv"
    if not f.exists():
        return None
    lab = pd.read_csv(f)
    lab["counted"] = lab["valid"] & lab.apply(lambda r: str(r["writer_model"]).startswith(MODELS[r["judge"]]), axis=1)
    return lab


def main() -> None:
    items = pd.read_csv(HERE / "items.csv")
    judged = items[items["status"] == "judged"]
    fams = judged.groupby("family")["item_id"].apply(list).to_dict()
    r1 = load("labreg-r1", items)
    assert r1 is not None, "no pass-1 labels"
    m1 = medians(r1)
    cur1, c1 = m1["cur"].dropna().astype(int).to_dict(), m1["C"].dropna().astype(int).to_dict()
    o_cur, o_c = outcomes(items, cur1), outcomes(items, c1)
    losses = [k for k in o_cur if o_cur[k] and o_c.get(k) is False]
    gains = [k for k in o_cur if o_cur[k] is False and o_c.get(k)]

    def items_of(name):
        f = feeders(name)
        return fams[f] if isinstance(f, str) else f

    moved = {i: c1[i] - cur1[i] for i in cur1 if i in c1 and c1[i] != cur1[i]}
    big = sorted(i for i, d in moved.items() if abs(d) >= 2)
    to_rerun = sorted({i for k in losses for i in items_of(k) if i in moved} | set(big))

    r2 = load("labreg-r2", items)
    confirmed_losses, confirmed_big, pending = [], [], False
    if to_rerun:
        if r2 is None:
            pending = True
        else:
            m2 = medians(r2)
            missing = [i for i in to_rerun if i not in m2.index]
            assert not missing, f"pass 2 lacks {missing}"
            cur2 = {**cur1, **m2["cur"].dropna().astype(int).to_dict()}
            c2 = {**c1, **m2["C"].dropna().astype(int).to_dict()}
            o_cur2, o_c2 = outcomes(items, cur2), outcomes(items, c2)
            confirmed_losses = [k for k in losses if o_cur2.get(k) and o_c2.get(k) is False]
            for i in big:
                d2 = c2[i] - cur2[i]
                if d2 != 0 and (d2 > 0) == (moved[i] > 0):
                    confirmed_big.append(i)

    # Secondary: paired sign test over single-judge labels, pass 1.
    ok = r1[r1["counted"]].pivot_table(index=["item_id", "judge"], columns="arm", values="level", aggfunc="first").dropna()
    d = ok["C"] - ok["cur"]
    down, up = int((d < 0).sum()), int((d > 0).sum())
    p = float(binomtest(down, down + up, 0.5).pvalue) if down + up else 1.0

    per_set = {}
    for s, g in judged.groupby("set"):
        ids = [i for i in g["item_id"] if i in cur1 and i in c1]
        diffs = [c1[i] - cur1[i] for i in ids]
        per_set[s] = {"items": len(ids), "exact": sum(x == 0 for x in diffs), "down": sum(x < 0 for x in diffs),
                      "up": sum(x > 0 for x in diffs), "mean_shift": round(sum(diffs) / len(diffs), 3) if ids else None}

    # Exploratory: the current text against the stored lab medians (battery-v1 verbatim; rebuilt items).
    st = judged.dropna(subset=["stored_median"])
    st = st[st["item_id"].isin(cur1)]
    vs_stored = {"items": len(st), "exact": int(sum(cur1[i] == int(s) for i, s in zip(st["item_id"], st["stored_median"]))),
                 "mean_shift": round(float(sum(cur1[i] - s for i, s in zip(st["item_id"], st["stored_median"])) / len(st)), 3) if len(st) else None}

    # Exploratory: how often C's judges quote the new sentence (needs the gitignored raw responses).
    raw = HERE.parents[3] / "data/annotations/labreg-r1/raw.jsonl"
    carve = None
    if raw.exists():
        rows = [json.loads(l) for l in raw.read_text().splitlines()]
        cite = [r for r in rows if r["arm"] == "C" and any(ph in r["response"].lower() for ph in CARVE_PHRASES)]
        carve = {"C_answers": sum(r["arm"] == "C" for r in rows), "quoting_the_new_sentence": len(cite),
                 "by_set": pd.Series([r["set"] for r in cite]).value_counts().to_dict(),
                 "on_moved_items": sorted({r["item_id"] for r in cite if r["item_id"] in moved})}

    verdict = "pending pass 2" if pending else ("fail" if confirmed_losses or confirmed_big else "pass")
    res = {
        "verdict": verdict,
        "outcomes": {"n": len(o_cur), "hold_under_current": sum(bool(v) for v in o_cur.values()),
                     "hold_under_C": sum(bool(v) for v in o_c.values())},
        "losses_pass1": losses, "gains_pass1": gains,
        "moved_items_pass1": {i: int(v) for i, v in sorted(moved.items())},
        "moves_of_two_or_more_pass1": big, "rerun_in_pass2": to_rerun,
        "confirmed_losses": confirmed_losses, "confirmed_moves_of_two_or_more": confirmed_big,
        "per_set": per_set,
        "sign_test_single_judge_labels": {"C_lower": down, "C_higher": up, "p_two_sided": round(p, 4)},
        "current_vs_stored_lab_medians": vs_stored,
        "carve_quotes": carve,
        "medians_pass1": {i: {"cur": cur1.get(i), "C": c1.get(i)} for i in sorted(set(cur1) | set(c1))},
        "outcomes_pass1": {k: {"cur": o_cur[k], "C": o_c.get(k)} for k in o_cur},
    }
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results/regression.json").write_text(json.dumps(res, indent=2) + "\n")
    print("verdict:", verdict)
    print(f"outcomes holding: current {res['outcomes']['hold_under_current']}/{len(o_cur)}, C {res['outcomes']['hold_under_C']}/{len(o_cur)}")
    print("losses (pass 1):", losses or "none")
    print("gains (pass 1):", gains or "none")
    print("moved items (pass 1):", res["moved_items_pass1"] or "none")
    print("re-run in pass 2:", to_rerun or "none", "| confirmed losses:", confirmed_losses or "none",
          "| confirmed moves of 2+:", confirmed_big or "none")
    print("per set:", per_set)
    print("sign test:", res["sign_test_single_judge_labels"], "| current vs stored:", vs_stored)
    if carve:
        print("carve quotes:", carve)


if __name__ == "__main__":
    main()
