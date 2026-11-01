"""Build the 4-gram check and the prompts of spv-v2 phase A (see PREREGISTRATION.md).

Two texts: `cur` is src/adele/rubrics/data_v2/Paolo_Pablo/SPv.txt; `cand` is SPv_candidate.txt. Both are shown as the
catalog shows a rubric (no title line). Item sets:
  P  every example bullet of `cand`, judged under `cand` with that one bullet removed (leave-one-out placement)
  L  ladder, aggregation and carve items (items.csv), both texts
  M  five minimal pairs (items.csv), both texts
Three repeats per item and text. Every item of L and M is checked for shared word 4-grams against every example
bullet of both texts; a shared 4-gram stops the build. One prompt file per call, opaque ids, all sets and texts
shuffled together into one run (judge folder opus-low).

    python experiments/benchmarks/spv-v2/make_prompts.py              # run spv2-1
    python experiments/benchmarks/spv-v2/make_prompts.py --pass2 ID [ID ...]   # run spv2-2
"""

import argparse
import hashlib
import json
import os
import random
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from adele.annotation.prompts import build_annotation_prompt_v2

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
JUDGE_IO = ROOT.parents[1] / "judge-io"
CUR = ROOT / "src/adele/rubrics/data_v2/Paolo_Pablo/SPv.txt"
CAND = HERE / "SPv_candidate.txt"
NAME = "Visual processing"
SEED = 20261005
REPEATS = 3
ID_CHARS = "abcdefghjkmnpqrstuvwxyz23456789"
AGENT = Path.home() / "Developer/ADELE/.claude/agents/adele-judge-v2-low.md"
INSTRUCTION = "Prompt file: {prompt_file}\nResponse file: {response_file}"


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, check=True).stdout


def shown(text: str) -> str:
    """The rubric as the catalog shows it: no title line, no blank line after it, no final newline."""
    lines = text.splitlines()
    assert lines[0].startswith("# ") and lines[1] == ""
    return "\n".join(lines[2:]).rstrip("\n")


def bullets(text: str) -> list[tuple[int, str]]:
    out, level = [], None
    for line in text.splitlines():
        m = re.match(r"Level (\d):", line)
        if m:
            level = int(m.group(1))
        elif line.startswith("* "):
            out.append((level, line))
    return out


def fourgrams(text: str) -> set[tuple[str, ...]]:
    w = re.findall(r"[a-z0-9]+", text.lower())
    return {tuple(w[i:i + 4]) for i in range(len(w) - 3)}


def shared(text: str, rubric: str) -> str:
    g = fourgrams(text)
    return "; ".join(f"Level {lvl}: " + " | ".join(" ".join(x) for x in sorted(g & fourgrams(b)))
                     for lvl, b in bullets(rubric) if g & fourgrams(b))


def write_run(run_id: str, cells: list[dict], rng: random.Random, note: dict) -> None:
    rng.shuffle(cells)
    taken: set[str] = set()
    io_dir, labels = JUDGE_IO / run_id, HERE / "labels" / run_id
    for d in (io_dir / "prompts", io_dir / "responses/opus-low", labels):
        d.mkdir(parents=True, exist_ok=True)
    rows = []
    for c in cells:
        while True:
            fid = "".join(rng.choice(ID_CHARS) for _ in range(5))
            if fid not in taken:
                taken.add(fid)
                break
        p = build_annotation_prompt_v2(NAME, c["rubric"], c["text"]).encode("utf-8")
        (io_dir / "prompts" / f"{fid}@SPv.txt").write_bytes(p)
        rows.append({"file_id": fid, "item_id": c["item_id"], "set": c["set"], "arm": c["arm"],
                     "target": c["target"], "repeat": c["repeat"], "prompt_sha256": sha256(p)})
    pd.DataFrame(rows).to_csv(labels / "prompts_index.csv", index=False)
    run = {"run_id": run_id, "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "repo_commit": git("rev-parse", "HEAD").strip(),
           "design": {"n_cells": len(rows), "dims": ["SPv"], "judges": {
               "opus-low": "Claude Code subagent 'adele-judge-v2-low' (Read, Write; omitClaudeMd; effort low), "
                           "model alias 'opus', relayed by 'judge-dispatcher-v2-low'"}},
           "texts": {"cur": {"file": os.path.relpath(CUR, ROOT), "sha256": sha256(CUR.read_bytes())},
                     "cand": {"file": os.path.relpath(CAND, ROOT), "sha256": sha256(CAND.read_bytes())}},
           **note,
           "prompt": {"builder": "adele.annotation.prompts.build_annotation_prompt_v2",
                      "builder_file_sha256": sha256((ROOT / "src/adele/annotation/prompts.py").read_bytes())},
           "judge_agent": {"file": "~/Developer/ADELE/.claude/agents/adele-judge-v2-low.md",
                           "sha256": sha256(AGENT.read_bytes())},
           "judge_instruction": INSTRUCTION, "judge_io": os.path.relpath(io_dir, ROOT)}
    (labels / "run.json").write_text(json.dumps(run, indent=2) + "\n")
    print(f"{run_id}: {len(rows)} prompts")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pass2", nargs="*")
    args = ap.parse_args()
    texts = {"cur": CUR.read_text(encoding="utf-8"), "cand": CAND.read_text(encoding="utf-8")}
    items = pd.read_csv(HERE / "items.csv", dtype=str).fillna("")

    clash = {r.item_id: s for r in items.itertuples() for arm, t in texts.items()
             if (s := shared(r.text, t))}
    if clash:
        raise SystemExit(f"4-gram clash, reword before sealing: {clash}")

    rng = random.Random(SEED)
    cells = []
    if args.pass2 is None:
        for i, (lvl, b) in enumerate(bullets(texts["cand"])):
            rubric = "\n".join(line for line in shown(texts["cand"]).splitlines() if line != b)
            assert rubric.count("\n") == shown(texts["cand"]).count("\n") - 1
            for k in range(1, REPEATS + 1):
                cells.append({"item_id": f"P-L{lvl}-{i:02d}", "set": "P", "arm": "cand", "target": str(lvl),
                              "repeat": k, "rubric": rubric, "text": b[2:]})
        pd.DataFrame([{"item_id": f"P-L{lvl}-{i:02d}", "level": lvl, "bullet": b[2:]}
                      for i, (lvl, b) in enumerate(bullets(texts["cand"]))]).to_csv(HERE / "placement_items.csv",
                                                                                   index=False)
        chosen, run_id = items, "spv2-1"
    else:
        chosen, run_id = items[items.item_id.isin(args.pass2)], "spv2-2"
        assert len(chosen) == len(args.pass2), "unknown item id"
    for r in chosen.itertuples():
        for arm, t in texts.items():
            for k in range(1, REPEATS + 1):
                cells.append({"item_id": r.item_id, "set": r.set, "arm": arm,
                              "target": r.pred_cur if arm == "cur" else r.pred_cand,
                              "repeat": k, "rubric": shown(t), "text": r.text})
    write_run(run_id, cells, rng, {"pass": 1 if args.pass2 is None else 2})


if __name__ == "__main__":
    main()
