"""Build the prompts of spv-v2 phase B (see PREREGISTRATION_B.md): real images, judged by an image-reading judge.

Stimuli come from make_stimuli.py (stimuli.csv, stimuli/*.png). They are copied into the run folder and hashed, and
prompts name them by absolute path. Arms:
  cur       current SPv.txt, no answer key
  cand      SPv_candidate.txt, no answer key
  cand_key  SPv_candidate.txt, with the code given as a reference answer (sweeps and views only)
Two repeats per stimulus and arm. Also set P: the replaced Level 3 example (paint over two meter digits), placed under
the candidate with that bullet removed, three repeats. One prompt per call, opaque ids, all shuffled into run spv2-b.

    python experiments/benchmarks/spv-v2/phaseB/make_prompts_b.py
"""

import hashlib
import json
import os
import random
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from make_prompts import CAND, CUR, ID_CHARS, JUDGE_IO, NAME, ROOT, bullets, git, sha256, shown  # noqa: E402

from adele.annotation.prompts import build_annotation_prompt_v2  # noqa: E402

HERE = Path(__file__).resolve().parent
RUN = "spv2-b"
SEED = 20261006
REPEATS = 2
AGENT = Path.home() / "Developer/ADELE/.claude/agents/adele-judge-v2-low-image.md"
METER = "* Read a six-digit meter on which a splash of paint covers the lower half of two digits."
TRAPS = {
    "trap-search": "In which quarter of the image at {0} (top left, top right, bottom left or bottom right) is the "
                   "one red circle?",
    "trap-counting": "How many dots are there in the image at {0}?",
    "trap-arc": "The image at {0} shows three example pairs of coloured grids, each input above its output, and a "
                "fourth input on its own. Give the output grid for the fourth input.",
    "trap-rotation": "In the image at {0}, is the right-hand shape the left-hand shape rotated within the page?",
}


def task(row: pd.Series, paths: list[str], key: bool) -> str:
    if row.family == "trap":
        return TRAPS[row.stim_id].format(paths[0])
    if row.family == "views":
        t = (f"The three images at {paths[0]}, {paths[1]} and {paths[2]} are overlapping crops of one printed "
             "label, given in an unknown order. Read the label's full six-character code.")
    else:
        t = f"Read the six-character code shown in the image at {paths[0]}."
    return t + (f"\n\n(Reference answer, for the annotator only: {row.code})" if key else "")


def main() -> None:
    stim = pd.read_csv(HERE / "stimuli.csv", dtype={"code": str}).fillna("")
    io_dir, labels = JUDGE_IO / RUN, HERE.parent / "labels" / RUN
    img_dir = io_dir / "images"
    for d in (io_dir / "prompts", io_dir / "responses/opus-low", img_dir, labels):
        d.mkdir(parents=True, exist_ok=True)
    hashes = {}
    for f in sorted((HERE / "stimuli").glob("*.png")):
        shutil.copyfile(f, img_dir / f.name)
        hashes[f.name] = sha256(f.read_bytes())

    texts = {"cur": shown(CUR.read_text(encoding="utf-8")), "cand": shown(CAND.read_text(encoding="utf-8"))}
    assert METER in CAND.read_text(encoding="utf-8")
    cells = []
    for row in stim.itertuples(index=False):
        row = pd.Series(row._asdict())
        paths = [str(img_dir / f) for f in row.files.split(";")]
        arms = ["cur", "cand"] + (["cand_key"] if row.family != "trap" else [])
        for arm in arms:
            for k in range(1, REPEATS + 1):
                cells.append({"item_id": row.stim_id, "set": "T" if row.family == "trap" else "S", "arm": arm,
                              "family": row.family, "step": row.step, "repeat": k,
                              "rubric": texts["cand" if arm.startswith("cand") else "cur"],
                              "text": task(row, paths, arm == "cand_key")})
    rubric = "\n".join(line for line in texts["cand"].splitlines() if line != METER)
    assert rubric.count("\n") == texts["cand"].count("\n") - 1
    assert (3, METER) in bullets(CAND.read_text(encoding="utf-8"))
    for k in range(1, 4):
        cells.append({"item_id": "P-meter", "set": "P", "arm": "cand", "family": "placement", "step": 3,
                      "repeat": k, "rubric": rubric, "text": METER[2:]})

    rng = random.Random(SEED)
    rng.shuffle(cells)
    taken, rows = set(), []
    for c in cells:
        while (fid := "".join(rng.choice(ID_CHARS) for _ in range(5))) in taken:
            pass
        taken.add(fid)
        p = build_annotation_prompt_v2(NAME, c["rubric"], c["text"]).encode("utf-8")
        (io_dir / "prompts" / f"{fid}@SPv.txt").write_bytes(p)
        rows.append({"file_id": fid, **{k: c[k] for k in ("item_id", "set", "arm", "family", "step", "repeat")},
                     "target": "", "prompt_sha256": sha256(p)})
    pd.DataFrame(rows).to_csv(labels / "prompts_index.csv", index=False)
    run = {"run_id": RUN, "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "repo_commit": git("rev-parse", "HEAD").strip(), "pass": 1,
           "design": {"n_cells": len(rows), "dims": ["SPv"], "judges": {
               "opus-low": "Claude Code subagent 'adele-judge-v2-low-image' (Read, Write; omitClaudeMd; effort low), "
                           "model alias 'opus', relayed by 'judge-dispatcher-v2-low-image'"}},
           "texts": {"cur": {"file": os.path.relpath(CUR, ROOT), "sha256": sha256(CUR.read_bytes())},
                     "cand": {"file": os.path.relpath(CAND, ROOT), "sha256": sha256(CAND.read_bytes())}},
           "images_sha256": hashes,
           "prompt": {"builder": "adele.annotation.prompts.build_annotation_prompt_v2",
                      "builder_file_sha256": sha256((ROOT / "src/adele/annotation/prompts.py").read_bytes())},
           "judge_agent": {"file": "~/Developer/ADELE/.claude/agents/adele-judge-v2-low-image.md",
                           "sha256": sha256(AGENT.read_bytes())},
           "judge_instruction": "Prompt file: {prompt_file}\nResponse file: {response_file}",
           "judge_io": os.path.relpath(io_dir, ROOT)}
    (labels / "run.json").write_text(json.dumps(run, indent=2) + "\n")
    print(f"{RUN}: {len(rows)} prompts, {len(hashes)} images")


if __name__ == "__main__":
    main()
