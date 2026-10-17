"""Amendment 2 screen: msc-l4-note's 16 minimal-pair items judged under MSc_candidate_v2.txt (run mscand-s1).

Same prompt, judge and repeats as mscand-1. Rule M is applied to the screen's labels. Only if it holds does the full
v2 run follow (R-MSc and H on MSc), after Pablo has seen the v2 wording. Items sharing a word 4-gram with any v2
bullet or new line are void.

    uv run --extra annotate python experiments/benchmarks/ms-candidate/make_screen.py
"""

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
RUN = "mscand-s1"


def main() -> None:
    catalog = cp.load_active_catalog()
    v2 = (HERE / "MSc_candidate_v2.txt").read_text(encoding="utf-8").split("\n", 1)[1].strip()
    cur = catalog["MSc"].content
    pairs = pd.read_csv(cp.L4 / "pairs.csv", dtype={"pair": str})
    cells = []
    for r in pairs.itertuples(index=False):
        item = f"M-{r.pair}{r.version}"
        texts = [t for _, t in mp.bullets(v2)] + cp.new_sentences(cur, v2)
        shared = {g for t in texts for g in mp.fourgrams(r.text) & mp.fourgrams(t)}
        assert not shared, f"{item} shares {shared} with v2"
        cat = {"MSc": SimpleNamespace(content=v2, full_name=catalog["MSc"].full_name)}
        p = mp.prompt_for(cat, SimpleNamespace(rubric="MSc", set="M", text=r.text))
        cells.append({"item_id": item, "set": "M", "arm": "candidate_v2", "rubric": "MSc",
                      "prompt_sha256": mp.sha256(p.encode("utf-8")), "prompt": p})
    rng = random.Random(cp.SEED + 3)
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
    cp.write_run(cells, {"pass": "screen", "candidate_file": "ms-candidate/MSc_candidate_v2.txt",
                         "rubric_sha256": mp.sha256(v2.encode("utf-8")), "amendment": 2})


if __name__ == "__main__":
    main()
