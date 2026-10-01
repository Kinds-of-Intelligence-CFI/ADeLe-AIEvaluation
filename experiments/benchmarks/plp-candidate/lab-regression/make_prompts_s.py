"""Prompts of the lab regression for PLp candidate S (PREREGISTRATION.md, section "Candidate S").

S is ../../plp-b2/PLp_S.txt. It is judged alone, with the v2 prompt (build_annotation_prompt_v2),
by Opus at effort low, three repeats per item. The items are those of items.csv, plus S's three new
example bullets in set P (items_s.csv). Set P is scored with every Examples block stripped, as before.

    python experiments/benchmarks/plp-candidate/lab-regression/make_prompts_s.py                        # pass 1, labreg-s1
    python experiments/benchmarks/plp-candidate/lab-regression/make_prompts_s.py --replicate ITEM [...]  # pass 2, labreg-s2

With --candidate sq, the same is done for candidate S-q (../../plp-b2/PLp_Sq.txt): runs labreg-sq1 and
labreg-sq2. Its items are those of items_s.csv; the 4-gram check is redone against S-q's bullets.

Pass 2 judges the listed items under both texts, S and the current text, with the v2 prompt: the
current-text arm is the control that pass 1 lacks.
"""

import argparse
import json
import random
from types import SimpleNamespace
from pathlib import Path

import pandas as pd

from adele.agentic import load_active_catalog
from adele.annotation.prompts import build_annotation_prompt_v2

import make_prompts as mp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
S_FILE = ROOT / "experiments/benchmarks/plp-b2/PLp_S.txt"
AGENT = ROOT / "experiments/benchmarks/natural-prompt/adele-judge-v2-low.md"
JUDGES = {f"opus-low-r{k}": f"adele-judge-v2-low, model alias 'opus'; repeat {k}" for k in (1, 2, 3)}
SEED = 20260930


def s_text(path: Path = S_FILE) -> str:
    return path.read_text(encoding="utf-8").split("\n", 2)[2].rstrip("\n")


def build_items(cur: str, s: str) -> pd.DataFrame:
    """items.csv plus S's new example bullets (set P), with the 4-gram check redone against S's bullets."""
    items = pd.read_csv(HERE / "items.csv")
    old = set(t for _, t in mp.bullets(cur))
    new, counts = [], {}
    for level, text in mp.bullets(s):
        if text in old:
            continue
        counts[level] = counts.get(level, 0) + 1
        new.append({"item_id": f"P-S-L{level}-{counts[level]}", "set": "P", "own_dim": "PLp", "target": level,
                    "status": "judged", "source": "PLp_S.txt example bullet (new in S)", "text": text,
                    "fourgram_shared": "n/a: the item is a bullet of this file, and the rubric shown has no examples"})
    assert len(new) == 3, new
    cand = [(lvl, i, mp.fourgrams(t)) for i, (lvl, t) in enumerate(mp.bullets(s), 1)]
    for r in items.itertuples():
        if r.set == "P":
            continue
        hit = any(mp.fourgrams(r.text) & g for _, _, g in cand)
        assert hit == (r.status == "void"), f"{r.item_id}: 4-gram status differs under S"
    return pd.concat([items, pd.DataFrame(new)], ignore_index=True)


def prompt(full_name: str, content: str, item) -> str:
    rubric = mp.strip_examples(content) if item.set == "P" else content
    return build_annotation_prompt_v2(full_name, rubric, item.text)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", choices=["s", "sq"], default="s")
    ap.add_argument("--replicate", nargs="+", metavar="ITEM", help="write pass 2 (labreg-s2)")
    args = ap.parse_args()
    plp = load_active_catalog()["PLp"]
    path = S_FILE if args.candidate == "s" else S_FILE.with_name("PLp_Sq.txt")
    s = s_text(path)
    c = args.candidate
    mp.JUDGES, mp.AGENT = JUDGES, AGENT
    note = {"rubric": {"file": str(Path(plp.file_path).relative_to(ROOT)),
                       "sha256": mp.sha256(Path(plp.file_path).read_bytes()),
                       "candidate": f"plp-b2/{path.name}", "candidate_sha256": mp.sha256(path.read_bytes()),
                       "set_P": "every Examples block stripped from the rubric shown (r25 design)"},
            "items": "lab-regression/items_s.csv", "lab_record_commit": mp.LAB}
    taken = set(pd.concat(pd.read_csv(p) for p in HERE.glob("labels/*/prompts_index.csv"))["file_id"])

    if args.replicate:
        items = pd.read_csv(HERE / "items_s.csv").set_index("item_id")
        assert set(args.replicate) <= set(items.index), "unknown item"
        cells = [{"item_id": i, "set": items.loc[i, "set"], "arm": arm, "demand": "PLp",
                  "prompt": prompt(plp.full_name, content, SimpleNamespace(**items.loc[i]))}
                 for i in args.replicate for arm, content in (("cur", plp.content), ("S", s))]
        run, extra, arms, seed = f"labreg-{c}2", {"pass": 2, "replicates": f"labreg-{c}1"}, ("cur", "S"), SEED + 2
    else:
        items = build_items(plp.content, s)
        if c == "s":
            items.to_csv(HERE / "items_s.csv", index=False)
        else:  # S-q has S's bullets: same items
            assert items.equals(build_items(plp.content, s_text()))
        judged = items[items["status"] == "judged"]
        cells = [{"item_id": r.item_id, "set": r.set, "arm": "S", "demand": "PLp",
                  "prompt": prompt(plp.full_name, s, r)} for r in judged.itertuples(index=False)]
        run, extra, arms, seed = f"labreg-{c}1", {"pass": 1, "reference": "labreg-r1, arm cur, judge opus-low (v1 prompt)"}, ("S",), SEED + (0 if c == "s" else 100)
    for c in cells:
        c["prompt_sha256"] = mp.sha256(c["prompt"].encode("utf-8"))
    rng = random.Random(seed)
    rng.shuffle(cells)
    for c, i in zip(cells, mp.opaque_ids(len(cells), rng, taken)):
        c["file_id"] = i
    cells = [{"file_id": c["file_id"], **{k: v for k, v in c.items() if k != "file_id"}} for c in cells]
    mp.write_run(run, cells, {**note, **extra}, arms)
    # write_run records the v1 builder; this study uses v2.
    f = HERE / f"labels/{run}/run.json"
    meta = json.loads(f.read_text())
    meta["prompt"] = {"builder": "adele.annotation.prompts.build_annotation_prompt_v2",
                      "builder_file_sha256": mp.sha256((ROOT / "src/adele/annotation/prompts.py").read_bytes())}
    f.write_text(json.dumps(meta, indent=2) + "\n")


if __name__ == "__main__":
    main()
