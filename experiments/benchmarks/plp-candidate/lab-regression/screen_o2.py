"""Screen of candidate O' (PREREGISTRATION.md, "Candidate O' screen"): O minus the sentence "Only choices that could
go wrong add to this demand." (../../plp-b2/PLp_O2.txt).

Run labreg-o2s: set P of items_o.csv (23 example bullets, rubric shown with every Examples block stripped), v2
prompt, Opus low. Every item is judged under O' by repeats r1-r3. The covering letter (P-L1-3) is also judged under
O' by r4-r6, and under O (its labreg-o1 prompt, reused) by r4-r6, so both texts have six labels for it.

    python experiments/benchmarks/plp-candidate/lab-regression/screen_o2.py pin
    python experiments/benchmarks/plp-candidate/lab-regression/screen_o2.py analyse

Rule. The screen passes if (a) the covering letter is at Level 2 in at most 2 of its 6 O' labels, (b) set P has at
least as many examples placed at their own level under O' as under O (labreg-o1 medians), and (c) no set-P median
moves by two levels or more between O and O'.
"""

import json
import random
import sys
from pathlib import Path

import pandas as pd

from adele.agentic import load_active_catalog

import make_prompts as mp
import make_prompts_s as ms

HERE = Path(__file__).resolve().parent
RUN = "labreg-o2s"
LETTER = "P-L1-3"
O2 = HERE.parents[1] / "plp-b2/PLp_O2.txt"


def pin() -> None:
    plp = load_active_catalog()["PLp"]
    o2 = ms.s_text(O2)
    o = ms.s_text(O2.with_name("PLp_O.txt"))
    assert o.replace("Only choices that could go wrong add to this demand. ", "") == o2
    items = pd.read_csv(HERE / "items_o.csv")
    p = items[items["set"] == "P"]
    cells = [{"item_id": r.item_id, "set": "P", "arm": "O2", "demand": "PLp", "prompt": ms.prompt(plp.full_name, o2, r)}
             for r in p.itertuples(index=False)]
    o1 = pd.read_csv(HERE / "labels/labreg-o1/prompts_index.csv").set_index("item_id").loc[LETTER]
    o_prompt = (mp.JUDGE_IO / "labreg-o1/prompts" / f"{o1['file_id']}@PLp.txt").read_text(encoding="utf-8")
    assert mp.sha256(o_prompt.encode("utf-8")) == o1["prompt_sha256"]
    cells.append({"item_id": LETTER, "set": "P", "arm": "O", "demand": "PLp", "prompt": o_prompt})
    for c in cells:
        c["prompt_sha256"] = mp.sha256(c["prompt"].encode("utf-8"))
    taken = set(pd.concat(pd.read_csv(f) for f in HERE.glob("labels/*/prompts_index.csv"))["file_id"])
    rng = random.Random(ms.SEED + 300)
    rng.shuffle(cells)
    for c, i in zip(cells, mp.opaque_ids(len(cells), rng, taken)):
        c["file_id"] = i
    cells = [{"file_id": c["file_id"], **{k: v for k, v in c.items() if k != "file_id"}} for c in cells]
    mp.JUDGES = {f"opus-low-r{k}": f"adele-judge-v2-low, model alias 'opus'; repeat {k}" for k in range(1, 7)}
    mp.AGENT = ms.AGENT
    note = {"rubric": {"candidate": "plp-b2/PLp_O2.txt", "candidate_sha256": mp.sha256(O2.read_bytes()),
                       "removed_from_O": "Only choices that could go wrong add to this demand.",
                       "set_P": "every Examples block stripped from the rubric shown (r25 design)"},
            "cells": "O2 items: repeats r1-r3 (P-L1-3 also r4-r6); the O cell (P-L1-3, labreg-o1 prompt): r4-r6 only"}
    mp.write_run(RUN, cells, note, ("O2", "O"))
    f = HERE / f"labels/{RUN}/run.json"
    meta = json.loads(f.read_text())
    meta["prompt"] = {"builder": "adele.annotation.prompts.build_annotation_prompt_v2",
                      "builder_file_sha256": mp.sha256((mp.ROOT / "src/adele/annotation/prompts.py").read_bytes())}
    f.write_text(json.dumps(meta, indent=2) + "\n")


def analyse() -> None:
    items = pd.read_csv(HERE / "items_o.csv").set_index("item_id")
    lab = pd.read_csv(HERE / f"labels/{RUN}/labels_long.csv")
    lab = lab[lab["valid"] & lab["writer_model"].astype(str).str.startswith("claude-opus-5-5")]
    o1 = pd.read_csv(HERE / "labels/labreg-o1/labels_long.csv")
    o1 = o1[o1["valid"] & o1["writer_model"].astype(str).str.startswith("claude-opus-5-5") & (o1["set"] == "P")]
    first3 = lab[(lab["arm"] == "O2") & lab["judge"].isin([f"opus-low-r{k}" for k in (1, 2, 3)])]
    med = lambda df: df.groupby("item_id")["level"].apply(lambda s: sorted(int(x) for x in s)[(len(s) - 1) // 2])
    m_o2, m_o = med(first3).to_dict(), med(o1).to_dict()
    placed = lambda m: sorted(i for i, v in m.items() if v == items.loc[i, "target"])
    letter_o2 = sorted(int(x) for x in lab[(lab["arm"] == "O2") & (lab["item_id"] == LETTER)]["level"])
    letter_o = sorted([int(x) for x in o1[o1["item_id"] == LETTER]["level"]]
                      + [int(x) for x in lab[(lab["arm"] == "O") & (lab["item_id"] == LETTER)]["level"]])
    moves = {i: m_o2[i] - m_o[i] for i in m_o2 if i in m_o and m_o2[i] != m_o[i]}
    checks = {"a_letter_at_2_in_at_most_2_of_6": bool(len(letter_o2) == 6 and sum(x >= 2 for x in letter_o2) <= 2),
              "b_placement_not_worse": bool(len(placed(m_o2)) >= len(placed(m_o))),
              "c_no_move_of_two": bool(all(abs(d) < 2 for d in moves.values()))}
    out = {"verdict": "pass" if all(checks.values()) else "fail", "checks": checks,
           "letter": {"O2": letter_o2, "O": letter_o},
           "placed_at_own_level": {"O2": len(placed(m_o2)), "O": len(placed(m_o)), "of": len(m_o2)},
           "moves_O_to_O2": moves,
           "missed_under_O2": {i: {"target": int(items.loc[i, "target"]), "O2": m_o2[i], "O": m_o.get(i)}
                               for i in m_o2 if m_o2[i] != items.loc[i, "target"]}}
    (HERE / "results/screen_o2.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    {"pin": pin, "analyse": analyse}[sys.argv[1]]()
