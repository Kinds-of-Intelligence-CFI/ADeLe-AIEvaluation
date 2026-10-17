"""Build the items, the 4-gram check, the prompts and the relay files of the ms-candidate study. See PREREGISTRATION.md.

Every item is judged under the current text and the candidate of its rubric (MSc_candidate.txt, MSm_candidate.txt),
same prompt (build_annotation_prompt_v2), judge (adele-judge-v2-low) and three repeats as ../ms-lab-regression/,
whose item builder this reuses.
  R  every item of the MS lab regression, rebuilt from today's catalog (sets P, F, S, L, B), on its own rubric
  M  msc-l4-note's eight minimal pairs, on MSc
  H  the 15 tau2 tasks of msc-l4-note, on MSc and MSm, with two inputs: the frozen script, and the full task (the
     agent-side worksheet's parts 1 to 3 with the policy and simulator rules written in)
Set P is placed on each arm's own examples. Items sharing a word 4-gram with any example bullet of either arm, or with
a candidate's new sentences, are void in both arms (real tau2 tasks are reported only).

Writes labels/mscand-1/{prompts_index.csv, relays.csv, run.json} and items.csv (tau2 texts blanked); prompts and relays
go to $ADELE_JUDGE_IO/mscand-1/ (never committed).

    uv run --extra annotate python experiments/benchmarks/ms-candidate/make_prompts.py
"""

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

ROOT, JUDGE_IO = mp.ROOT, mp.JUDGE_IO
L4 = HERE.parent / "msc-l4-note"
WORKSHEETS = Path("~/Developer/ADELE/worksheets/tau2-agent-side-2026-10-17").expanduser()
RUN = "mscand-1"
SEED = 20261017
ARMS = ("current", "candidate")
TAU2 = ("tau2-airline", "tau2-retail", "tau2-banking_knowledge")
MAX_LINES = 1900  # one Read call of the judge agent


def texts() -> dict[str, dict[str, str]]:
    """Rubric content per rubric and arm, as the catalog loads it (title line dropped, stripped)."""
    catalog = load_active_catalog()
    out = {}
    for dim in mp.RUBRICS:
        raw = Path(catalog[dim].file_path).read_text(encoding="utf-8")
        assert raw.split("\n", 1)[1].strip() == catalog[dim].content
        cand = (HERE / f"{dim}_candidate.txt").read_text(encoding="utf-8")
        out[dim] = {"current": catalog[dim].content, "candidate": cand.split("\n", 1)[1].strip()}
    return out


def new_sentences(cur: str, cand: str) -> list[str]:
    """Lines of the candidate that are not in the current text."""
    have = set(cur.splitlines())
    return [line for line in cand.splitlines() if line.strip() and line not in have]


def full_task(item_id: str) -> str:
    """The worksheet's parts 1 to 3, with the policy and the simulator rules written in."""
    md = (WORKSHEETS / f"{item_id}.md").read_text(encoding="utf-8")
    md = md.split("\n## Your labels")[0].rstrip()
    md = "# Task\n" + md.split("\n", 1)[1]  # drop the "# H-xx: ..." title
    md = md.replace("The script (this is our frozen task text):", "The script:")
    for domain in ("airline", "retail"):
        link = f"[policy_{domain}.md](policy_{domain}.md) (the agent's system prompt; read once per domain)"
        if link in md:
            policy = (WORKSHEETS / f"policy_{domain}.md").read_text(encoding="utf-8").strip()
            md = md.replace(link, "the agent's system prompt, in full below")
            md = md.replace("\n## 2. ", f"\n**The agent's policy:**\n\n```text\n{policy}\n```\n\n## 2. ", 1)
    rules = (WORKSHEETS / "simulator_rules.md").read_text(encoding="utf-8").strip()
    md = md.replace("[simulator_rules.md](simulator_rules.md)", "below")
    md = md.replace("\n## 3. ", f"\n```text\n{rules}\n```\n\n## 3. ", 1)
    assert "](" not in md, f"{item_id}: a link is left"
    return md


def build_items(arms: dict) -> pd.DataFrame:
    catalog = load_active_catalog()
    r = mp.build_items(catalog)
    r = r.assign(set="R-" + r["set"])
    rows = [r]
    pairs = pd.read_csv(L4 / "pairs.csv", dtype={"pair": str})
    rows.append(pd.DataFrame({"item_id": "M-" + pairs["pair"] + pairs["version"], "set": "M", "rubric": "MSc",
                              "source": "../msc-l4-note/pairs.csv", "text": pairs["text"], "check": "none",
                              "label_kind": "new", "rebuilt": False, "status": "judged"}))
    human = pd.read_csv(L4 / "human_items.csv", dtype={"instance_id": str})
    frozen = pd.concat(pd.read_csv(ROOT / f"data/instances/instances_{b}.csv", dtype={"instance_id": str})
                       for b in TAU2).set_index(["benchmark", "instance_id"])["prompt"]
    for h in human.itertuples(index=False):
        for dim in mp.RUBRICS:
            for inp, text in (("script", frozen[(h.benchmark, h.instance_id)]), ("full", full_task(h.item_id))):
                rows.append(pd.DataFrame([{"item_id": f"{h.item_id}-{inp}-on-{dim}", "set": f"H-{inp}",
                                           "rubric": dim, "source": f"{h.benchmark} {h.instance_id}", "text": text,
                                           "check": "none", "label_kind": "human", "rebuilt": False,
                                           "status": "judged"}]))
    items = pd.concat(rows, ignore_index=True)[list(mp.COLS)]
    assert items["item_id"].is_unique
    # 4-gram check against both arms: every bullet, and the candidate's new sentences.
    void, extra = [], []
    for r in items.itertuples(index=False):
        if r.set == "R-P":
            extra.append("")
            continue
        g = mp.fourgrams(r.text)
        texts_ = [t for a in ARMS for _, t in mp.bullets(arms[r.rubric][a])]
        texts_ += new_sentences(arms[r.rubric]["current"], arms[r.rubric]["candidate"])
        shared = sorted({" ".join(x) for t in texts_ for x in g & mp.fourgrams(t)})
        extra.append(" | ".join(shared))
        void.append(bool(shared) and not r.set.startswith("H-") and r.status != "void")
    items["fourgram_both_arms"] = extra
    items.loc[items["set"] != "R-P", "status"] = [
        "void" if v else s for v, s in zip(void, items.loc[items["set"] != "R-P", "status"])]
    return items


def p_text(arms: dict, item_id: str, arm: str) -> str:
    """Set P: the item is the bullet with the same id in this arm's text."""
    dim = item_id.split("-")[1]
    return {f"P-{stem}": t for stem, _, t in mp.numbered(arms[dim][arm], dim)}[item_id]


def write_run(cells: list[dict], note: dict) -> None:
    io_dir, labels = JUDGE_IO / RUN, HERE / "labels" / RUN
    answered = [p for j in mp.JUDGES for p in (io_dir / "responses" / j).glob("*.txt")]
    assert not answered, f"{RUN} already has {len(answered)} answers; refusing to overwrite a judged run"
    for d in [io_dir / "prompts", io_dir / "relays", labels] + [io_dir / "responses" / j for j in mp.JUDGES]:
        d.mkdir(parents=True, exist_ok=True)
    for old in list((io_dir / "prompts").glob("*.txt")) + list((io_dir / "relays").glob("*.txt")):
        old.unlink()
    for c in cells:
        (io_dir / "prompts" / f"{c['file_id']}@{c['rubric']}.txt").write_text(c.pop("prompt"), encoding="utf-8")
    pd.DataFrame(cells).to_csv(labels / "prompts_index.csv", index=False)
    relays = []
    for judge in mp.JUDGES:
        ids = [f"{c['file_id']}@{c['rubric']}" for c in cells]
        for k in range(0, len(ids), mp.RELAY_MAX):
            batch = ids[k:k + mp.RELAY_MAX]
            name = f"{judge}-{k // mp.RELAY_MAX + 1:02d}"
            (io_dir / "relays" / f"{name}.txt").write_text(
                "\n".join(["Model: opus", f"I/O folder: {io_dir}", f"Judge folder name: {judge}",
                           f"Cells ({len(batch)}):", *batch]), encoding="utf-8")
            relays.append({"relay": name, "judge": judge, "cells": len(batch)})
    pd.DataFrame(relays).to_csv(labels / "relays.csv", index=False)
    run = {
        "run_id": RUN, "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "repo_commit": mp.git("rev-parse", "HEAD").strip(),
        "repo_dirty_tracked_files": mp.git("status", "--porcelain", "--untracked-files=no").splitlines(),
        "design": {"n_cells": len(cells), "dims": list(mp.RUBRICS), "arms": list(ARMS), "judges": mp.JUDGES,
                   "n_calls": len(cells) * len(mp.JUDGES), "relays": len(relays), "relay_max_cells": mp.RELAY_MAX},
        **note,
        "prompt": {"builder": "adele.annotation.prompts.build_annotation_prompt_v2",
                   "builder_file_sha256": mp.sha256((ROOT / "src/adele/annotation/prompts.py").read_bytes())},
        "judge_agent": {"file": str(mp.AGENT.relative_to(ROOT)), "sha256": mp.sha256(mp.AGENT.read_bytes())},
        "dispatcher_agent": {"file": str(mp.DISPATCHER.relative_to(ROOT)),
                             "sha256": mp.sha256(mp.DISPATCHER.read_bytes())},
        "judge_instruction": mp.INSTRUCTION, "judge_io": os.path.relpath(io_dir, ROOT),
        "sampling": "harness defaults; snapshot cannot be pinned for subagents; effort is set in the agent file",
    }
    (labels / "run.json").write_text(json.dumps(run, indent=2) + "\n")
    print(f"{RUN}: {len(cells)} prompts x {len(mp.JUDGES)} repeats = {len(cells) * len(mp.JUDGES)} calls, "
          f"in {len(relays)} relays of at most {mp.RELAY_MAX} cells ({io_dir / 'relays'})")


def main() -> None:
    arms = texts()
    catalog = load_active_catalog()
    items = build_items(arms)
    blank = items["set"].str.startswith("H-")
    items.assign(text=items["text"].where(~blank, "")).to_csv(HERE / "items.csv", index=False)  # tau2 texts stay out
    cells = []
    for r in items[items["status"] == "judged"].itertuples(index=False):
        for arm in ARMS:
            text = p_text(arms, r.item_id, arm) if r.set == "R-P" else r.text
            cat = {r.rubric: SimpleNamespace(content=arms[r.rubric][arm], full_name=catalog[r.rubric].full_name)}
            p = mp.prompt_for(cat, SimpleNamespace(rubric=r.rubric, set=r.set.removeprefix("R-"), text=text))
            assert len(p.splitlines()) <= MAX_LINES, f"{r.item_id}: {len(p.splitlines())} lines; needs the chunked judge"
            cells.append({"item_id": r.item_id, "set": r.set, "arm": arm, "rubric": r.rubric,
                          "prompt_sha256": mp.sha256(p.encode("utf-8")), "prompt": p})
    rng = random.Random(SEED)
    rng.shuffle(cells)
    taken = set()
    for p in ROOT.glob("experiments/benchmarks/*/labels/*/prompts_index.csv"):
        if p.parent.name != RUN:
            idx = pd.read_csv(p)
            if "file_id" in idx:
                taken |= set(idx["file_id"].astype(str))
    for c, i in zip(cells, mp.opaque_ids(len(cells), rng, taken)):
        c["file_id"] = i
    cells = [{"file_id": c["file_id"], **{k: v for k, v in c.items() if k != "file_id"}} for c in cells]
    note = {"rubrics": {f"{d}/{a}": {"sha256": mp.sha256(arms[d][a].encode("utf-8"))} for d in arms for a in ARMS},
            "candidate_files": {d: f"ms-candidate/{d}_candidate.txt" for d in arms},
            "items": "ms-candidate/items.csv", "lab_record_commit": mp.LAB, "pass": 1,
            "worksheets": str(WORKSHEETS.relative_to(Path.home()))}
    write_run(cells, note)
    print(items.groupby(["set", "rubric", "status"]).size().to_string())
    for r in items[(items["status"] == "void") | (items["set"].str.startswith("H-") & (items["fourgram_both_arms"] != ""))].itertuples(index=False):
        print(f"  {r.status}: {r.item_id}: {r.fourgram_both_arms or r.fourgram_shared}")


if __name__ == "__main__":
    main()
