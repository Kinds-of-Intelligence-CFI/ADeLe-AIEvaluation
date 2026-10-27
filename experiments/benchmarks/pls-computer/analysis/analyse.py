"""Pre-registered analysis of pls-computer. Writes results/analysis.json.

Labels: labels/plsc-1 (and labels/plsc-2 when it exists), valid answers written by claude-opus-5-5 only. An item's
label under a text is the median of its labels (with an even count, the lower middle one). R's reference is the
released label of each task. Checks (PREREGISTRATION.md):
  P  each new example's median under the current text against its own level (exact, within 1, or off by 2+)
  M  per pair and text: M1 to M3 hold if a <= 2 and b >= 3; M4 holds if a <= 2 and b <= a.
     A loss holds under cur and fails under cand; a gain is the reverse
  B  per item, cand - cur; a move of 2+ goes to pass 2
  R  per task, cand - released label, and cur (noise subset) - released label; a move of 2+ goes to pass 2.
     Drift: more tasks up than down under cand, sign test p < 0.05, and a larger share up than in the noise subset
Pass 2 (plsc-2) re-judges items behind a loss or a 2+ move under both texts, three repeats. A loss is confirmed if
the pair fails under cand and holds under cur in pass 2; a move is confirmed if pass 2 moves the item the same way.

    python experiments/benchmarks/pls-computer/analysis/analyse.py
"""

import json
import re
from pathlib import Path

import pandas as pd
from scipy.stats import binomtest

HERE = Path(__file__).resolve().parents[1]
MODEL = "claude-opus-5-5"
NEW = r"retries each failed call|evicts the least recently used|cannot be rehearsed|300 services|no copy of the"


def load(run: str) -> pd.DataFrame:
    p = HERE / f"labels/{run}/labels_long.csv"
    if not p.exists():
        return pd.DataFrame()
    lab = pd.read_csv(p)
    return lab[lab["valid"].astype(bool) & lab["writer_model"].astype(str).str.startswith(MODEL)]


def med(s: pd.Series) -> int:
    v = sorted(s.astype(int))
    return v[(len(v) - 1) // 2]


def medians(lab: pd.DataFrame) -> dict:
    return {k: med(g["level"]) for k, g in lab.groupby(["item_id", "arm"])} if len(lab) else {}


def pair_holds(m: dict, pair: str, arm: str):
    a, b = m.get((f"{pair}a", arm)), m.get((f"{pair}b", arm))
    if a is None or b is None:
        return None
    return bool(a <= 2 and (b <= a if pair == "M4" else b >= 3))


def main() -> None:
    items = pd.read_csv(HERE / "items.csv").set_index("item_id")
    l1, l2 = load("plsc-1"), load("plsc-2")
    m1, m2 = medians(l1), medians(l2)
    out = {"n_labels": {"plsc-1": int(len(l1)), "plsc-2": int(len(l2))}}

    out["P"] = {}
    for i in items.index[items["set"] == "P"]:
        lv, t = m1.get((i, "cur")), int(items.loc[i, "target"])
        out["P"][i] = {"labels": sorted(l1[l1["item_id"] == i]["level"].astype(int)), "median": lv, "target": t,
                       "verdict": None if lv is None else "exact" if lv == t else "within 1" if abs(lv - t) == 1
                       else "off by 2+ (drop)"}

    out["M"], losses = {}, []
    for pair in ["M1", "M2", "M3", "M4"]:
        cur, cand = pair_holds(m1, pair, "cur"), pair_holds(m1, pair, "cand")
        rec = {"medians": {f"{pair}{s}": {a: m1.get((f"{pair}{s}", a)) for a in ("cur", "cand")} for s in "ab"},
               "holds_cur": cur, "holds_cand": cand, "pass1": "loss" if cur and cand is False
               else "gain" if cand and cur is False else "no change"}
        if rec["pass1"] == "loss":
            losses.append(pair)
            rec["pass2"] = {"holds_cur": pair_holds(m2, pair, "cur"), "holds_cand": pair_holds(m2, pair, "cand")}
            rec["confirmed"] = bool(rec["pass2"]["holds_cur"] and rec["pass2"]["holds_cand"] is False)
        out["M"][pair] = rec

    def moves(ids: list[str], ref: dict) -> list[dict]:
        rows = []
        for i in ids:
            c = m1.get((i, "cand"))
            if c is None or ref.get(i) is None:
                continue
            d = {"item_id": i, "ref": ref[i], "cand": c, "move": c - ref[i]}
            if abs(d["move"]) >= 2:
                p_cur, p_cand = m2.get((i, "cur")), m2.get((i, "cand"))
                d["pass2"] = {"cur": p_cur, "cand": p_cand}
                d["confirmed"] = None if p_cur is None or p_cand is None else \
                    bool((p_cand - p_cur) * d["move"] > 0)
            rows.append(d)
        return rows

    b_ids = list(items.index[items["set"] == "B"])
    b = moves(b_ids, {i: m1.get((i, "cur")) for i in b_ids})
    r_items = items[items["set"] == "R"]
    r = moves(list(r_items.index), r_items["target"].astype(int).to_dict())
    noise = [{"item_id": i, "ref": int(r_items.loc[i, "target"]), "cur": m1[(i, "cur")],
              "move": m1[(i, "cur")] - int(r_items.loc[i, "target"])}
             for i in r_items.index[r_items["role"] == "noise"] if (i, "cur") in m1]

    def summary(rows: list[dict]) -> dict:
        mv = [x["move"] for x in rows]
        up, down = sum(x > 0 for x in mv), sum(x < 0 for x in mv)
        return {"n": len(mv), "same": mv.count(0), "up": up, "down": down,
                "sign_test_p": round(binomtest(up, up + down).pvalue, 4) if up + down else None,
                "moves_2plus": [x for x in rows if abs(x["move"]) >= 2]}

    out["B"] = summary(b)
    out["R"] = {"all": summary(r), "noise_cur_vs_released": summary(noise),
                "by_benchmark": {k: summary([x for x in r if r_items.loc[x["item_id"], "pair"] == k])
                                 for k in r_items["pair"].unique()},
                "levels_cand": pd.Series([x["cand"] for x in r]).value_counts().sort_index().to_dict(),
                "levels_released": r_items["target"].astype(int).value_counts().sort_index().to_dict()}
    ra, rn = out["R"]["all"], out["R"]["noise_cur_vs_released"]
    share = lambda s: s["up"] / s["n"] if s["n"] else 0.0
    out["R"]["drift"] = bool(ra["up"] > ra["down"] and (ra["sign_test_p"] or 1) < 0.05 and share(ra) > share(rn))

    confirmed_moves = [x for s in (out["B"], out["R"]["all"]) for x in s["moves_2plus"] if x.get("confirmed")]
    pending = [x["item_id"] for s in (out["B"], out["R"]["all"]) for x in s["moves_2plus"] if x.get("confirmed") is None]
    pending += [p for p in losses if out["M"][p].get("pass2", {}).get("holds_cand") is None]
    confirmed_losses = [p for p in losses if out["M"][p].get("confirmed")]
    out["pass2_needed"] = pending
    out["verdict"] = "pending pass 2" if pending else \
        "pass" if not (confirmed_losses or confirmed_moves or out["R"]["drift"]) else "fail"
    out["examples_kept"] = [i for i, v in out["P"].items() if v["verdict"] in ("exact", "within 1")]

    raw = Path(HERE.parents[2] / "data/annotations/plsc-1/raw.jsonl")
    if raw.exists():
        ans = pd.DataFrame([json.loads(x) for x in raw.read_text().splitlines()])
        ans = ans[ans["arm"] == "cand"]
        hit = ans["response"].str.contains(NEW, flags=re.I, regex=True)
        out["quotes_new_examples"] = {s: round(float(hit[ans["set"] == s].mean()), 3) for s in ("M", "B", "R")}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results/analysis.json").write_text(json.dumps(out, indent=2, default=str) + "\n")
    print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
