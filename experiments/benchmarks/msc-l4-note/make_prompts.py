"""Build the items, the 4-gram check, the prompts and the relay files of the MSc Level 4 note test.

See PREREGISTRATION.md. Every item is judged on MSc twice, once with the current text (catalog MSc.txt) and once
with the candidate (MSc_candidate.txt: the current text plus two sentences in Level 4's Note). Same prompt
(build_annotation_prompt_v2), judge (adele-judge-v2-low, Opus at effort low), three repeats and relays as
../ms-lab-regression/, whose item builder this reuses.
Item sets:
  R  the MSc items of the MS lab regression (P, F, S, L, B), rebuilt from today's catalog
  M  eight minimal pairs (pairs.csv): A = one objection, answered once and let go; B = sustained pushback
  H  real tau2 tasks: ten fresh items that Pablo labels blind, plus five development items he labelled on
     2026-10-14 (human_items.csv; texts from data/instances, never committed)

    python experiments/benchmarks/msc-l4-note/make_prompts.py                         # pass 1, msc-l4-1
    python experiments/benchmarks/msc-l4-note/make_prompts.py --replicate ITEM [...]  # pass 2, msc-l4-2
"""

import argparse
import json
import os
import random
import sys
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "ms-lab-regression"))
import make_prompts as mp  # noqa: E402  (the MS lab regression's builder)

from adele.agentic import load_active_catalog  # noqa: E402

ROOT = mp.ROOT
JUDGE_IO = mp.JUDGE_IO
CANDIDATE = HERE / "MSc_candidate.txt"
NOTE = ("Importantly, the other party must keep pushing, so that move after move answers theirs. A single "
        "objection, answered once and then dropped, determines little of what is said, and belongs at the level the "
        "rest of the exchange calls for.")
ARMS = ("current", "candidate")
SEED = 20261014
# Fresh human items: released relabel-v2 MSc level -> how many, drawn from tau2 texts of at most 1,000 characters.
STRATA = {4: 4, 3: 3, 2: 3}
TAU2 = ("tau2-airline", "tau2-retail", "tau2-banking_knowledge")
# Development items: worksheets/ms-human-2026-10-12 M01, M02, M04, M06, M07, which Pablo labelled on 2026-10-14.
DEV = [("tau2-airline", "27"), ("tau2-banking_knowledge", "task_006"), ("tau2-airline", "0"),
       ("tau2-airline", "22"), ("tau2-airline", "4")]


def texts() -> dict[str, str]:
    """The rubric as the catalog loads it (title line and final newline dropped), current and candidate."""
    catalog = load_active_catalog()
    raw = CANDIDATE.read_text(encoding="utf-8")
    assert raw.count(NOTE) == 1 and raw.replace(" " + NOTE, "") == Path(catalog["MSc"].file_path).read_text(
        encoding="utf-8"), "MSc_candidate.txt must be MSc.txt plus the note"
    current = catalog["MSc"].content
    anchor = "or from one aligned side."
    assert current.count(anchor) == 1
    candidate = current.replace(anchor, f"{anchor} {NOTE}")
    assert candidate in raw and mp.bullets(candidate) == mp.bullets(current)
    return {"current": current, "candidate": candidate}


def tau2_prompts() -> pd.DataFrame:
    p = pd.concat(pd.read_csv(ROOT / f"data/instances/instances_{b}.csv", dtype={"instance_id": str}) for b in TAU2)
    return p.set_index(["benchmark", "instance_id"])["prompt"]


def select_human() -> pd.DataFrame:
    """Draw the fresh items once (seeded) and write human_items.csv with ids only."""
    released = pd.read_csv(ROOT / "experiments/benchmarks/mass-annotation/runs/relabel-v2/labels.csv",
                           dtype={"instance_id": str})
    released = released[(released["rubric_ref"] == "v2/MSc") & released["benchmark"].isin(TAU2) & released["valid"]]
    prompts = tau2_prompts()
    released["chars"] = [len(prompts[(b, i)]) for b, i in zip(released["benchmark"], released["instance_id"])]
    pool = released[(released["chars"] <= 1000) & ~released[["benchmark", "instance_id"]].apply(tuple, axis=1).isin(DEV)]
    picks = [pool[pool["level"] == lvl].sample(n, random_state=SEED) for lvl, n in STRATA.items()]
    fresh = pd.concat(picks).sample(frac=1, random_state=SEED)[["benchmark", "instance_id"]].assign(role="fresh")
    dev = pd.DataFrame(DEV, columns=["benchmark", "instance_id"]).assign(role="dev")
    out = pd.concat([fresh, dev], ignore_index=True)
    out.insert(0, "item_id", [f"H-{k:02d}" for k in range(1, len(out) + 1)])
    out.to_csv(HERE / "human_items.csv", index=False)
    return out


def build_items(current: str) -> pd.DataFrame:
    catalog = load_active_catalog()
    lab = mp.build_items(catalog)
    r = lab[lab["rubric"] == "MSc"].copy()
    r["set"] = "R-" + r["set"]
    rows = [r]
    note_grams = mp.fourgrams(NOTE)
    pairs = pd.read_csv(HERE / "pairs.csv", dtype={"pair": str})
    m = pd.DataFrame({"item_id": "M-" + pairs["pair"] + pairs["version"], "set": "M", "rubric": "MSc",
                      "source": "pairs.csv, written for this study", "text": pairs["text"],
                      "check": "none", "label_kind": "new", "rebuilt": False})
    human = pd.read_csv(HERE / "human_items.csv", dtype={"instance_id": str}) if (HERE / "human_items.csv").exists() \
        else select_human()
    prompts = tau2_prompts()
    h = pd.DataFrame({"item_id": human["item_id"], "set": "H-" + human["role"], "rubric": "MSc",
                      "source": human["benchmark"] + " " + human["instance_id"],
                      "text": [prompts[(b, i)] for b, i in zip(human["benchmark"], human["instance_id"])],
                      "check": "none", "label_kind": "human", "rebuilt": False})
    for new in (m, h):  # 4-gram independence against every MSc example bullet and the note
        hits = []
        for t in new["text"]:
            g = mp.fourgrams(t)
            hits.append(sum(len(g & mp.fourgrams(b)) for _, b in mp.bullets(current)) + len(g & note_grams))
        new["fourgram_hits"] = hits
        # Written items are void on any shared 4-gram (JUDGING.md rule 4); real tasks are only reported.
        new["status"] = ["void" if n and new is m else "judged" for n in hits]
        rows.append(new)
    items = pd.concat(rows, ignore_index=True)[list(mp.COLS)]
    assert items["item_id"].is_unique
    return items


def write_run(run_id: str, cells: list[dict], note: dict) -> None:
    io_dir, labels = JUDGE_IO / run_id, HERE / "labels" / run_id
    answered = [p for j in mp.JUDGES for p in (io_dir / "responses" / j).glob("*.txt")]
    assert not answered, f"{run_id} already has {len(answered)} answers; refusing to overwrite a judged run"
    for d in [io_dir / "prompts", io_dir / "relays", labels] + [io_dir / "responses" / j for j in mp.JUDGES]:
        d.mkdir(parents=True, exist_ok=True)
    for old in list((io_dir / "prompts").glob("*.txt")) + list((io_dir / "relays").glob("*.txt")):
        old.unlink()  # an unjudged earlier build of this run
    for c in cells:
        (io_dir / "prompts" / f"{c['file_id']}@MSc.txt").write_text(c.pop("prompt"), encoding="utf-8")
    pd.DataFrame(cells).to_csv(labels / "prompts_index.csv", index=False)
    relays = []
    for judge in mp.JUDGES:
        ids = [f"{c['file_id']}@MSc" for c in cells]
        for k in range(0, len(ids), mp.RELAY_MAX):
            batch = ids[k:k + mp.RELAY_MAX]
            name = f"{judge}-{k // mp.RELAY_MAX + 1:02d}"
            msg = "\n".join(["Model: opus", f"I/O folder: {io_dir}", f"Judge folder name: {judge}",
                             f"Cells ({len(batch)}):", *batch])
            (io_dir / "relays" / f"{name}.txt").write_text(msg, encoding="utf-8")
            relays.append({"relay": name, "judge": judge, "cells": len(batch)})
    pd.DataFrame(relays).to_csv(labels / "relays.csv", index=False)
    run = {
        "run_id": run_id,
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "repo_commit": mp.git("rev-parse", "HEAD").strip(),
        "repo_dirty_tracked_files": mp.git("status", "--porcelain", "--untracked-files=no").splitlines(),
        "design": {"n_cells": len(cells), "dims": ["MSc"], "arms": list(ARMS), "judges": mp.JUDGES,
                   "n_calls": len(cells) * len(mp.JUDGES), "relays": len(relays), "relay_max_cells": mp.RELAY_MAX},
        **note,
        "prompt": {"builder": "adele.annotation.prompts.build_annotation_prompt_v2",
                   "builder_file_sha256": mp.sha256((ROOT / "src/adele/annotation/prompts.py").read_bytes())},
        "judge_agent": {"file": str(mp.AGENT.relative_to(ROOT)), "sha256": mp.sha256(mp.AGENT.read_bytes())},
        "dispatcher_agent": {"file": str(mp.DISPATCHER.relative_to(ROOT)),
                             "sha256": mp.sha256(mp.DISPATCHER.read_bytes())},
        "judge_instruction": mp.INSTRUCTION,
        "judge_io": os.path.relpath(io_dir, ROOT),
        "sampling": "harness defaults; snapshot cannot be pinned for subagents; effort is set in the agent file",
    }
    (labels / "run.json").write_text(json.dumps(run, indent=2) + "\n")
    print(f"{run_id}: {len(cells)} prompts x {len(mp.JUDGES)} repeats = {len(cells) * len(mp.JUDGES)} calls, "
          f"in {len(relays)} relays of at most {mp.RELAY_MAX} cells ({io_dir / 'relays'})")


def taken_ids(exclude: str) -> set[str]:
    idx = [p for p in HERE.glob("labels/*/prompts_index.csv") if p.parent.name != exclude]
    return set(pd.concat(pd.read_csv(p) for p in idx)["file_id"]) if idx else set()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--replicate", nargs="+", metavar="ITEM", help="write pass 2 (msc-l4-2): both arms of each item")
    args = ap.parse_args()
    arms = texts()
    catalog = load_active_catalog()
    note = {"rubrics": {"current": {"file": str(Path(catalog["MSc"].file_path).relative_to(ROOT)),
                                    "sha256": mp.sha256(arms["current"].encode("utf-8"))},
                        "candidate": {"file": str(CANDIDATE.relative_to(ROOT)),
                                      "sha256": mp.sha256(arms["candidate"].encode("utf-8"))}},
            "set_R-P": "every Examples block stripped from the rubric shown (r25 design)",
            "items": "msc-l4-note/items.csv", "lab_record_commit": mp.LAB}

    if args.replicate:  # pass 2: the pass-1 prompts of the listed items, both arms, under new ids
        r1 = pd.read_csv(HERE / "labels/msc-l4-1/prompts_index.csv")
        todo = r1[r1["item_id"].isin(args.replicate)]
        assert set(todo["item_id"]) == set(args.replicate), "unknown or unjudged item"
        rng = random.Random(SEED + 2)
        cells = []
        for r, new in zip(todo.sample(frac=1, random_state=SEED + 2).itertuples(index=False),
                          mp.opaque_ids(len(todo), rng, taken_ids("msc-l4-2"))):
            p = (JUDGE_IO / "msc-l4-1/prompts" / f"{r.file_id}@MSc.txt").read_text(encoding="utf-8")
            assert mp.sha256(p.encode("utf-8")) == r.prompt_sha256
            cells.append({"file_id": new, "item_id": r.item_id, "set": r.set, "arm": r.arm, "rubric": "MSc",
                          "prompt_sha256": r.prompt_sha256, "pass1_file_id": r.file_id, "prompt": p})
        write_run("msc-l4-2", cells, {**note, "pass": 2, "replicates": "msc-l4-1"})
        return

    items = build_items(arms["current"])
    items.assign(text=items["text"].where(~items["set"].str.startswith("H-"), "")).to_csv(
        HERE / "items.csv", index=False)  # tau2 texts stay out of the repo
    judged = items[items["status"] == "judged"]
    cells = []
    for arm, content in arms.items():
        cat = {"MSc": SimpleNamespace(content=content, full_name=catalog["MSc"].full_name)}
        for r in judged.itertuples(index=False):
            p = mp.prompt_for(cat, SimpleNamespace(rubric="MSc", set=r.set.removeprefix("R-"), text=r.text))
            assert (NOTE in p) == (arm == "candidate")
            cells.append({"item_id": r.item_id, "set": r.set, "arm": arm, "rubric": "MSc",
                          "prompt_sha256": mp.sha256(p.encode("utf-8")), "prompt": p})
    rng = random.Random(SEED)
    rng.shuffle(cells)
    for c, i in zip(cells, mp.opaque_ids(len(cells), rng, taken_ids("msc-l4-1"))):
        c["file_id"] = i
    cells = [{"file_id": c["file_id"], **{k: v for k, v in c.items() if k != "file_id"}} for c in cells]
    write_run("msc-l4-1", cells, {**note, "pass": 1})
    print(items.groupby(["set", "status"]).size().to_string())
    for r in items[items["status"] == "void"].itertuples(index=False):
        print(f"  void: {r.item_id} ({r.fourgram_hits} shared 4-grams)")


if __name__ == "__main__":
    main()
