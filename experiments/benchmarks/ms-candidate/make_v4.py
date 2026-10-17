"""Amendments 4 and 5: an MSc candidate (v4 by default, --version 5 for v5) judged on every MSc item of mscand-1
(R-MSc, M, H on MSc), run mscand-v<version>.

Candidate arm only; the current arm is mscand-1's (same judge, prompt and repeats, judged 2026-10-17). Items, prompts
and the 4-gram rule as make_prompts.py, with v4's bullets and new lines in the check. Set P: v4's examples keep the
ids of the current examples they match (the refund example keeps P-MSc-L4-2); the new Level 1 refusal example is
P-MSc-L1-atlas.

    uv run --extra annotate python experiments/benchmarks/ms-candidate/make_v4.py [--version 5]
"""

import argparse

import importlib.util
import random
from pathlib import Path
from types import SimpleNamespace

import pandas as pd

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("cand_prompts", HERE / "make_prompts.py")
cp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cp)
mp = cp.mp
RUN = "mscand-v4"
VERSION = 4
ATLAS = "P-MSc-L1-atlas"


def v4_text() -> str:
    return (HERE / f"MSc_candidate_v{VERSION}.txt").read_text(encoding="utf-8").split("\n", 1)[1].strip()


def p_ids(cur: str, v4: str) -> dict[str, str]:
    """item id -> v4 bullet text: same id where the text is unchanged; the refund example by position; the new one."""
    cur_ids = {t: f"P-{stem}" for stem, _, t in mp.numbered(cur, "MSc")}
    out, unmatched = {}, []
    for level, text in mp.bullets(v4):
        if text in cur_ids:
            out[cur_ids[text]] = text
        else:
            unmatched.append((level, text))
    missing = sorted(set(cur_ids.values()) - set(out))
    assert len(missing) == 1 and missing[0] == "P-MSc-L4-2", missing
    assert len(unmatched) == 2 and {lvl for lvl, _ in unmatched} == {1, 4}, unmatched
    for level, text in unmatched:
        out["P-MSc-L4-2" if level == 4 else ATLAS] = text
    return out


def main() -> None:
    global RUN, VERSION
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", type=int, default=4)
    VERSION = ap.parse_args().version
    RUN = f"mscand-v{VERSION}"
    catalog = cp.load_active_catalog()
    cur, v4 = catalog["MSc"].content, v4_text()
    arms = cp.texts()
    arms["MSc"]["candidate"] = v4
    items = cp.build_items(arms)
    items = items[items["rubric"] == "MSc"]
    old = pd.read_csv(HERE / "items.csv", keep_default_na=False)
    old = old[old["rubric"] == "MSc"].set_index("item_id")["status"]
    changed = {i: (old.get(i), s) for i, s in zip(items["item_id"], items["status"]) if old.get(i) != s}
    assert not changed, f"void status differs from mscand-1: {changed}"
    ptext = p_ids(cur, v4)
    cat = {"MSc": SimpleNamespace(content=v4, full_name=catalog["MSc"].full_name)}
    cells = []
    judged = items[items["status"] == "judged"]
    rows = list(judged.itertuples(index=False))
    for r in rows:
        text = ptext[r.item_id] if r.set == "R-P" else r.text
        p = mp.prompt_for(cat, SimpleNamespace(rubric="MSc", set=r.set.removeprefix("R-"), text=text))
        cells.append({"item_id": r.item_id, "set": r.set, "arm": f"candidate_v{VERSION}", "rubric": "MSc",
                      "prompt_sha256": mp.sha256(p.encode("utf-8")), "prompt": p})
    p = mp.prompt_for(cat, SimpleNamespace(rubric="MSc", set="P", text=ptext[ATLAS]))
    cells.append({"item_id": ATLAS, "set": "R-P", "arm": f"candidate_v{VERSION}", "rubric": "MSc",
                  "prompt_sha256": mp.sha256(p.encode("utf-8")), "prompt": p})
    rng = random.Random(cp.SEED + VERSION)
    rng.shuffle(cells)
    taken = set()
    for f in cp.ROOT.glob("experiments/benchmarks/*/labels/*/prompts_index.csv"):
        idx = pd.read_csv(f)
        if "file_id" in idx:
            taken |= set(idx["file_id"].astype(str))
    for c, i in zip(cells, mp.opaque_ids(len(cells), rng, taken)):
        c["file_id"] = i
    cells = [{"file_id": c["file_id"], **{k: v for k, v in c.items() if k != "file_id"}} for c in cells]
    cp.RUN = RUN
    cp.write_run(cells, {"pass": 1, "candidate_file": f"ms-candidate/MSc_candidate_v{VERSION}.txt",
                         "rubric_sha256": mp.sha256(v4.encode("utf-8")), "amendment": VERSION,
                         "current_arm": "mscand-1"})
    print(pd.DataFrame(cells).groupby("set").size().to_string())


if __name__ == "__main__":
    main()
