"""Prompts of amendment 1 of the MSc Level 4 note test: the C check. See PREREGISTRATION.md, "Amendment 1".

The eight C items (pairs_c.csv: each pair's shared scenario, saying nothing about how the other party responds) are
judged under the current MSc text only, three repeats, as in msc-l4-1. Run msc-l4c-1, 24 calls.

    python experiments/benchmarks/msc-l4-note/make_prompts_c.py
"""

import importlib.util
import random
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("msc_l4_make_prompts_b", HERE / "make_prompts_b.py")
b = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(b)
m4, mp = b.m4, b.mp
SEED = 20261016


def main() -> None:
    arms = b.texts()
    catalog = m4.load_active_catalog()
    items = b.build_items(arms)
    c = items[(items["set"] == "C") & (items["status"] == "judged")]
    assert len(c) == 8
    cat = {"MSc": SimpleNamespace(content=arms["current"], full_name=catalog["MSc"].full_name)}
    cells = []
    for r in c.itertuples(index=False):
        p = mp.prompt_for(cat, SimpleNamespace(rubric="MSc", set="C", text=r.text))
        assert m4.NOTE not in p and b.NOTE_B not in p
        cells.append({"item_id": r.item_id, "set": "C", "arm": "current", "rubric": "MSc",
                      "prompt_sha256": mp.sha256(p.encode("utf-8")), "prompt": p})
    rng = random.Random(SEED)
    rng.shuffle(cells)
    for cell, i in zip(cells, mp.opaque_ids(len(cells), rng, m4.taken_ids("msc-l4c-1"))):
        cell["file_id"] = i
    cells = [{"file_id": x["file_id"], **{k: v for k, v in x.items() if k != "file_id"}} for x in cells]
    m4.ARMS = ("current",)
    m4.write_run("msc-l4c-1", cells, {"rubrics": {"current": {"sha256": mp.sha256(arms["current"].encode("utf-8"))}},
                                      "items": "msc-l4-note/pairs_c.csv", "amendment": 1, "pass": 1})


if __name__ == "__main__":
    main()
