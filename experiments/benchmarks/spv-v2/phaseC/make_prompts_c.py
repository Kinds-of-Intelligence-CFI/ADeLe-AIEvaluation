"""Build the prompts of spv-v2 phase C (see PREREGISTRATION_C.md): SPv on the 100 ZeroBench questions.

ZeroBench is gated and its terms forbid sharing answers. Nothing from it enters the repo: the parquet stays in the
gitignored data/downloads/zerobench/, images are written to the run folder in judge-io (outside the repo), and prompts
carry the question and the images but never the answer. The task text is the question, then one line naming each
image by absolute path with its native size. Arms: cur and cand, two repeats each, shuffled into run spv2-c.

    python experiments/benchmarks/spv-v2/phaseC/make_prompts_c.py
"""

import io
import json
import os
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from make_prompts import CAND, CUR, ID_CHARS, JUDGE_IO, NAME, ROOT, git, sha256, shown  # noqa: E402

from adele.annotation.prompts import build_annotation_prompt_v2  # noqa: E402

HERE = Path(__file__).resolve().parent
RUN = "spv2-c"
SEED = 20261007
REPEATS = 2
DATA = ROOT / "data/downloads/zerobench/data/zerobench-00000-of-00001.parquet"
AGENT = Path.home() / "Developer/ADELE/.claude/agents/adele-judge-v2-low-image.md"


def main() -> None:
    zb = pd.read_parquet(DATA)
    io_dir, labels = JUDGE_IO / RUN, HERE.parent / "labels" / RUN
    img_dir = io_dir / "images"
    for d in (io_dir / "prompts", io_dir / "responses/opus-low", img_dir, labels):
        d.mkdir(parents=True, exist_ok=True)
    texts = {"cur": shown(CUR.read_text(encoding="utf-8")), "cand": shown(CAND.read_text(encoding="utf-8"))}

    tasks, meta = {}, []
    for r in zb.itertuples(index=False):
        lines = []
        for j, x in enumerate(r.question_images_decoded):
            im = Image.open(io.BytesIO(x["bytes"]))
            path = img_dir / f"q{r.question_id}_{j}.png"
            im.save(path)
            lines.append(f"Image {j + 1}: {path} (native size {im.size[0]} x {im.size[1]} pixels; your view of it "
                         "may be downscaled)")
        tasks[r.question_id] = r.question_text.strip() + "\n\n" + "\n".join(lines)
        meta.append({"question_id": r.question_id, "n_images": len(lines), "question_chars": len(r.question_text)})
    pd.DataFrame(meta).to_csv(labels / "question_meta.csv", index=False)

    cells = [{"item_id": q, "arm": arm, "repeat": k} for q in tasks for arm in texts for k in range(1, REPEATS + 1)]
    rng = random.Random(SEED)
    rng.shuffle(cells)
    taken, rows = set(), []
    for c in cells:
        while (fid := "".join(rng.choice(ID_CHARS) for _ in range(5))) in taken:
            pass
        taken.add(fid)
        p = build_annotation_prompt_v2(NAME, texts[c["arm"]], tasks[c["item_id"]]).encode("utf-8")
        (io_dir / "prompts" / f"{fid}@SPv.txt").write_bytes(p)
        rows.append({"file_id": fid, "item_id": c["item_id"], "set": "Z", "arm": c["arm"], "target": "",
                     "repeat": c["repeat"], "prompt_sha256": sha256(p)})
    pd.DataFrame(rows).to_csv(labels / "prompts_index.csv", index=False)
    run = {"run_id": RUN, "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "repo_commit": git("rev-parse", "HEAD").strip(), "pass": 1,
           "design": {"n_cells": len(rows), "dims": ["SPv"], "judges": {
               "opus-low": "Claude Code subagent 'adele-judge-v2-low-image' (Read, Write; omitClaudeMd; effort low), "
                           "model alias 'opus', relayed by 'judge-dispatcher-v2-low-image'"}},
           "texts": {"cur": {"file": os.path.relpath(CUR, ROOT), "sha256": sha256(CUR.read_bytes())},
                     "cand": {"file": os.path.relpath(CAND, ROOT), "sha256": sha256(CAND.read_bytes())}},
           "data": {"dataset": "jonathan-roberts1/zerobench (gated; answers not shared)",
                    "file_sha256": sha256(DATA.read_bytes())},
           "prompt": {"builder": "adele.annotation.prompts.build_annotation_prompt_v2",
                      "builder_file_sha256": sha256((ROOT / "src/adele/annotation/prompts.py").read_bytes())},
           "judge_agent": {"file": "~/Developer/ADELE/.claude/agents/adele-judge-v2-low-image.md",
                           "sha256": sha256(AGENT.read_bytes())},
           "judge_instruction": "Prompt file: {prompt_file}\nResponse file: {response_file}",
           "judge_io": os.path.relpath(io_dir, ROOT)}
    (labels / "run.json").write_text(json.dumps(run, indent=2) + "\n")
    answers = set(zb.question_answer.astype(str).str.strip())
    leaked = [r["file_id"] for r in rows
              if any(a and len(a) > 3 and a in (io_dir / "prompts" / f"{r['file_id']}@SPv.txt").read_text()
                     for a in answers)]
    print(f"{RUN}: {len(rows)} prompts; prompts containing an answer string longer than 3 characters: {len(leaked)}")


if __name__ == "__main__":
    main()
