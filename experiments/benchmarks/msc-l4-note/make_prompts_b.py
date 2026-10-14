"""Prompts of amendment 1 (candidate B, rule B) of the MSc Level 4 note test. See PREREGISTRATION.md, "Amendment 1".

Candidate B (MSc_candidate_b.txt) replaces nothing and adds one Importantly clause to Level 4's Note: read the other
party as the task describes them; a party the task shows dropping its objection once answered sets little of what is
said; where the task does not say how they will respond, take them to keep pursuing the outcome the task gives them.

Run msc-l4b-1 (same judge, prompt, repeats and relays as msc-l4-1), arms per item:
  rule_b   every item of msc-l4-1 (R, M, H-fresh, H-dev), the C items and the fresh2 items
  current  the C items and the fresh2 items (the other current labels come from msc-l4-1, judged the same day)
  note     the C items (candidate A of msc-l4-1, to show its misfire on unstated behaviour)
C items (pairs_c.csv): each pair's shared scenario, with nothing on how the other party responds.
fresh2 (human_items_b.csv): ten more tau2 tasks for Pablo to label blind, drawn as the first ten.

    python experiments/benchmarks/msc-l4-note/make_prompts_b.py                         # pass 1, msc-l4b-1
    python experiments/benchmarks/msc-l4-note/make_prompts_b.py --replicate ITEM [...]  # pass 2, msc-l4b-2
"""

import argparse
import importlib.util
import random
from pathlib import Path
from types import SimpleNamespace

import pandas as pd

HERE = Path(__file__).resolve().parent
# The msc-l4-1 builder, loaded under its own name: it imports the MS lab regression's builder as `make_prompts`.
_spec = importlib.util.spec_from_file_location("msc_l4_make_prompts", HERE / "make_prompts.py")
m4 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m4)
mp = m4.mp
CANDIDATE_B = HERE / "MSc_candidate_b.txt"
NOTE_B = ("Importantly, read the other party as the task describes them. Where the task shows them raising an objection "
          "once and letting it go when answered, little of what is said is set by them, and the task belongs at the level "
          "the rest of the exchange calls for. Where the task does not say how they will respond, take them to keep "
          "pursuing the outcome the task gives them.")
SEED = 20261015


def texts() -> dict[str, str]:
    arms = m4.texts()  # current and candidate A, as the catalog loads them
    raw = CANDIDATE_B.read_text(encoding="utf-8")
    catalog = m4.load_active_catalog()
    assert raw.count(NOTE_B) == 1 and raw.replace(" " + NOTE_B, "") == Path(catalog["MSc"].file_path).read_text(
        encoding="utf-8"), "MSc_candidate_b.txt must be MSc.txt plus rule B"
    anchor = "or from one aligned side."
    rule_b = arms["current"].replace(anchor, f"{anchor} {NOTE_B}")
    assert rule_b in raw and mp.bullets(rule_b) == mp.bullets(arms["current"])
    return {"current": arms["current"], "note": arms["candidate"], "rule_b": rule_b}


def select_fresh2() -> pd.DataFrame:
    """Ten more tau2 tasks, drawn as the first ten, excluding every item of human_items.csv."""
    released = pd.read_csv(m4.ROOT / "experiments/benchmarks/mass-annotation/runs/relabel-v2/labels.csv",
                           dtype={"instance_id": str})
    released = released[(released["rubric_ref"] == "v2/MSc") & released["benchmark"].isin(m4.TAU2)
                        & released["valid"]]
    prompts = m4.tau2_prompts()
    released["chars"] = [len(prompts[(b, i)]) for b, i in zip(released["benchmark"], released["instance_id"])]
    used = set(map(tuple, pd.read_csv(HERE / "human_items.csv", dtype=str)[["benchmark", "instance_id"]].values))
    keys = released[["benchmark", "instance_id"]].apply(tuple, axis=1)
    pool = released[(released["chars"] <= 1000) & ~keys.isin(used)]
    picks = [pool[pool["level"] == lvl].sample(n, random_state=SEED) for lvl, n in m4.STRATA.items()]
    out = pd.concat(picks).sample(frac=1, random_state=SEED)[["benchmark", "instance_id"]].assign(role="fresh2")
    out.insert(0, "item_id", [f"H-{k}" for k in range(16, 16 + len(out))])
    out.to_csv(HERE / "human_items_b.csv", index=False)
    return out


def build_items(arms: dict[str, str]) -> pd.DataFrame:
    base = m4.build_items(arms["current"])
    c = pd.read_csv(HERE / "pairs_c.csv", dtype={"pair": str})
    c = pd.DataFrame({"item_id": "M-" + c["pair"] + "C", "set": "C", "rubric": "MSc",
                      "source": "pairs_c.csv: the pair's shared scenario", "text": c["text"], "check": "none",
                      "label_kind": "new", "rebuilt": False})
    f2 = pd.read_csv(HERE / "human_items_b.csv", dtype={"instance_id": str}) if (HERE / "human_items_b.csv").exists() \
        else select_fresh2()
    prompts = m4.tau2_prompts()
    f2 = pd.DataFrame({"item_id": f2["item_id"], "set": "H-fresh2", "rubric": "MSc",
                       "source": f2["benchmark"] + " " + f2["instance_id"],
                       "text": [prompts[(b, i)] for b, i in zip(f2["benchmark"], f2["instance_id"])],
                       "check": "none", "label_kind": "human", "rebuilt": False})
    grams = mp.fourgrams(m4.NOTE) | mp.fourgrams(NOTE_B)
    for new in (c, f2):
        new["fourgram_hits"] = [sum(len(mp.fourgrams(t) & mp.fourgrams(b)) for _, b in mp.bullets(arms["current"]))
                                + len(mp.fourgrams(t) & grams) for t in new["text"]]
        new["status"] = ["void" if n and new is c else "judged" for n in new["fourgram_hits"]]
    # The written pairs are checked against rule B's clause too.
    m = base["set"] == "M"
    hit = [len(mp.fourgrams(t) & mp.fourgrams(NOTE_B)) for t in base.loc[m, "text"]]
    assert not any(hit), "a pair item shares a 4-gram with rule B"
    items = pd.concat([base, c, f2], ignore_index=True)[list(mp.COLS)]
    assert items["item_id"].is_unique
    return items


def arms_for(item_set: str) -> tuple[str, ...]:
    if item_set == "C":
        return ("current", "note", "rule_b")
    if item_set == "H-fresh2":
        return ("current", "rule_b")
    return ("rule_b",)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--replicate", nargs="+", metavar="ITEM", help="write pass 2 (msc-l4b-2): every arm of each item")
    args = ap.parse_args()
    arms = texts()
    catalog = m4.load_active_catalog()
    m4.ARMS = tuple(arms)  # recorded in run.json
    note = {"rubrics": {a: {"sha256": mp.sha256(t.encode("utf-8"))} for a, t in arms.items()},
            "candidate_files": {"note": "msc-l4-note/MSc_candidate.txt", "rule_b": "msc-l4-note/MSc_candidate_b.txt"},
            "baseline": "current-text labels of msc-l4-1 for every item not judged under current here",
            "items": "msc-l4-note/items_b.csv", "lab_record_commit": mp.LAB, "amendment": 1}

    if args.replicate:
        r1 = pd.read_csv(HERE / "labels/msc-l4b-1/prompts_index.csv")
        todo = r1[r1["item_id"].isin(args.replicate)]
        assert set(todo["item_id"]) == set(args.replicate), "unknown or unjudged item"
        rng = random.Random(SEED + 2)
        cells = []
        for r, new in zip(todo.sample(frac=1, random_state=SEED + 2).itertuples(index=False),
                          mp.opaque_ids(len(todo), rng, m4.taken_ids("msc-l4b-2"))):
            p = (m4.JUDGE_IO / "msc-l4b-1/prompts" / f"{r.file_id}@MSc.txt").read_text(encoding="utf-8")
            assert mp.sha256(p.encode("utf-8")) == r.prompt_sha256
            cells.append({"file_id": new, "item_id": r.item_id, "set": r.set, "arm": r.arm, "rubric": "MSc",
                          "prompt_sha256": r.prompt_sha256, "pass1_file_id": r.file_id, "prompt": p})
        m4.write_run("msc-l4b-2", cells, {**note, "pass": 2, "replicates": "msc-l4b-1"})
        return

    items = build_items(arms)
    items.assign(text=items["text"].where(~items["set"].str.startswith("H-"), "")).to_csv(
        HERE / "items_b.csv", index=False)  # tau2 texts stay out of the repo
    judged = items[items["status"] == "judged"]
    cells = []
    for r in judged.itertuples(index=False):
        for arm in arms_for(r.set):
            cat = {"MSc": SimpleNamespace(content=arms[arm], full_name=catalog["MSc"].full_name)}
            p = mp.prompt_for(cat, SimpleNamespace(rubric="MSc", set=r.set.removeprefix("R-"), text=r.text))
            assert (NOTE_B in p) == (arm == "rule_b") and (m4.NOTE in p) == (arm == "note")
            cells.append({"item_id": r.item_id, "set": r.set, "arm": arm, "rubric": "MSc",
                          "prompt_sha256": mp.sha256(p.encode("utf-8")), "prompt": p})
    rng = random.Random(SEED)
    rng.shuffle(cells)
    for c, i in zip(cells, mp.opaque_ids(len(cells), rng, m4.taken_ids("msc-l4b-1"))):
        c["file_id"] = i
    cells = [{"file_id": c["file_id"], **{k: v for k, v in c.items() if k != "file_id"}} for c in cells]
    m4.write_run("msc-l4b-1", cells, {**note, "pass": 1})
    print(pd.DataFrame(cells).groupby(["set", "arm"]).size().to_string())
    for r in items[items["status"] == "void"].itertuples(index=False):
        print(f"  void: {r.item_id} ({r.fourgram_hits} shared 4-grams)")


if __name__ == "__main__":
    main()
