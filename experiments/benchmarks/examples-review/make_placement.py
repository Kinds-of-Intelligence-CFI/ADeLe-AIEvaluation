"""Placement check for the changed example bullets of the examples review (run exrev-1).

For every bullet that a candidate file adds or rewords (against the active rubric), the judge sees the candidate rubric
with that one bullet removed (all other examples kept; JUDGING.md rule 2) and the bullet as the task. Target: the level
the bullet sits under. Three repeats per bullet, opaque ids, all rubrics shuffled together. Judge: Opus 5.5 at effort
low, v2 prompt, via judge-dispatcher-v2-low. A bullet whose median is within one level of its target is adopted; one
two or more levels off is not. Dropped bullets need no check. Prompts: ~/Developer/ADELE/judge-io/exrev-1/prompts/.

    python experiments/benchmarks/examples-review/make_placement.py
"""

import hashlib
import json
import random
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from adele.agentic import load_active_catalog
from adele.annotation.prompts import build_annotation_prompt_v2

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
IO = ROOT.parents[1] / "judge-io/exrev-1"
DIMS = ["PLp", "PLe", "PLs", "MSm", "MSc", "MMe", "MMp", "MMs"]
REPEATS, SEED = 3, 20261005
ID_CHARS = "abcdefghjkmnpqrstuvwxyz23456789"


def shown(text: str) -> str:
    """The rubric as the catalog shows it: no title line, no blank line after it, no final newline."""
    lines = text.splitlines()
    assert lines[0].startswith("# ") and lines[1] == ""
    return "\n".join(lines[2:]).rstrip("\n")


def bullets(text: str) -> list[tuple[int, str]]:
    out, level = [], None
    for line in text.splitlines():
        m = re.match(r"Level (\d)[:.]", line)
        if m:
            level = int(m.group(1))
        elif line.startswith("* "):
            out.append((level, line))
    return out


def main() -> None:
    cat = load_active_catalog()
    items = []
    for d in DIMS:
        cand = (HERE / d / f"{d}_candidate.txt").read_text(encoding="utf-8")
        assert shown(cand).replace("\n", "") != "", d
        old = {b for _, b in bullets(cat[d].content)}
        for lvl, b in bullets(cand):
            if b not in old:
                rubric = "\n".join(l for l in shown(cand).splitlines() if l != b)
                assert rubric.count("\n") == shown(cand).count("\n") - 1
                items.append({"dim": d, "level": lvl, "bullet": b[2:], "rubric": rubric, "name": cat[d].full_name})
    rng = random.Random(SEED)
    cells = [dict(it, repeat=k) for it in items for k in range(1, REPEATS + 1)]
    rng.shuffle(cells)
    ids, taken = [], set()
    while len(ids) < len(cells):
        i = "".join(rng.choice(ID_CHARS) for _ in range(5))
        if i not in taken:
            taken.add(i)
            ids.append(i)
    (IO / "prompts").mkdir(parents=True, exist_ok=True)
    (IO / "responses/opus-low").mkdir(parents=True, exist_ok=True)
    rows = []
    for c, i in zip(cells, ids):
        p = build_annotation_prompt_v2(c["name"], c["rubric"], c["bullet"])
        (IO / "prompts" / f"{i}@EX.txt").write_bytes(p.encode("utf-8"))
        rows.append({"file_id": i, "dim": c["dim"], "target": c["level"], "repeat": c["repeat"],
                     "bullet": c["bullet"], "prompt_sha256": hashlib.sha256(p.encode("utf-8")).hexdigest()})
    (HERE / "labels/exrev-1").mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(HERE / "labels/exrev-1/prompts_index.csv", index=False)
    (HERE / "labels/exrev-1/run.json").write_text(json.dumps({
        "run_id": "exrev-1", "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "repo_commit": subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True,
                                      text=True).stdout.strip(),
        "judge_io": "../../judge-io/exrev-1",
        "design": {"n_cells": len(rows), "judges": {"opus-low": "adele-judge-v2-low via judge-dispatcher-v2-low, model opus"}},
        "candidates_sha256": {d: hashlib.sha256((HERE / d / f"{d}_candidate.txt").read_bytes()).hexdigest()
                              for d in DIMS}}, indent=2) + "\n")
    print(pd.DataFrame(items).groupby("dim").size().to_string(), "\ncells:", len(rows))


if __name__ == "__main__":
    main()
