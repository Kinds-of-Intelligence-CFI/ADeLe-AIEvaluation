"""Build PLp candidate S, the structural change (approved by Pablo on 2026-09-30), and pin its first test, run
s-search (PREREGISTRATION.md, amendment 1).

S is candidate B2 (make_b2.py) plus:
  - in the introduction, the placement rule: level = the higher of the kind of planning and the size of the search;
  - one sentence each at Levels 2, 3 and 4 placing a small, moderate or large search there;
  - one Level 4 example of a large pure search (not a river crossing);
  - at Level 5, that the size of the search alone does not place a task there (search size tops out at 4).
The script checks that S is exactly B2 plus these insertions, runs the word 4-gram check of all new text against
the 54 test frames, and builds the s-search prompts (same frames, builder and judge as b2-search).

    python experiments/benchmarks/plp-b2/make_s.py
"""

import importlib.util
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from adele.agentic import load_active_catalog
from adele.annotation.prompts import build_annotation_prompt_v2

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("make_b2", HERE / "make_b2.py")
b2mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b2mod)

RUN = "s-search"
INSERTS = [  # (anchor, text added right after it)
    ("no established procedure exists and a plan must be invented.",
     " Two things set the level: the kind of planning the task needs, and the size of the search it needs. The size "
     "of the search is how many choices could go wrong and how far ahead their consequences show. Place the task at "
     "the higher of the two."),
    ("Critically, the task remains at this level however many steps it involves, so long as the steps stay independent.",
     " Or the search is small: a few choices could go wrong, but each shows its consequence at once or one step later, "
     "so no looking ahead is needed."),
    ("Note, a static, fully observable, single-agent task can reach this level.",
     " Or the search is moderate: several choices could go wrong, and their consequences show only a few steps later, "
     "so options must be compared by looking ahead."),
    ("since a task-specific insight must be found before the subtasks can even be laid out.",
     " Or the search is large: many choices could go wrong and depend on one another, their consequences show only "
     "far ahead, and most plans that look workable fail."),
    ("The deliverable is the route plan, and the climb is not attempted here.",
     "\n* Timetable twelve exams into five slots under stated clashes and room limits, where most partial timetables "
     "that look fine fail only when the last few exams are placed."),
    ("where the decomposition must be discovered but the kind of work is itself established, the task belongs at the "
     "level below.",
     " The size of the search alone does not place a task here."),
]


def main() -> None:
    cur = load_active_catalog()["PLp"]
    b2 = (HERE / "PLp_B2.txt").read_text(encoding="utf-8").split("\n", 2)[2].rstrip("\n")
    s = b2
    for anchor, add in INSERTS:
        assert s.count(anchor) == 1, anchor
        s = s.replace(anchor, anchor + add)
    assert len(s) == len(b2) + sum(len(a) for _, a in INSERTS)
    (HERE / "PLp_S.txt").write_text(f"# {cur.full_name}\n\n{s}\n", encoding="utf-8")

    frames = pd.read_csv(b2mod.FRAME)
    new = set().union(*(b2mod.fourgrams(a) for _, a in INSERTS))
    shared = sorted({g for t in frames["prompt"] for g in b2mod.fourgrams(t) & new})
    print("4-grams shared between the new text and the 54 frames:", shared or "none")

    io, labels = b2mod.JUDGE_IO / RUN, HERE / "labels" / RUN
    for d in [io / "prompts", labels] + [io / "responses" / r for r in b2mod.REPEATS]:
        d.mkdir(parents=True, exist_ok=True)
    rows = []
    for st in frames.itertuples(index=False):
        prompt = build_annotation_prompt_v2(cur.full_name, s, st.prompt)
        (io / "prompts" / f"{st.custom_id}@PLp.txt").write_text(prompt, encoding="utf-8")
        rows.append({"benchmark": "rivercross", "instance_id": st.custom_id, "file_id": st.custom_id, "demand": "PLp",
                     "family": "v2", "prompt_sha256": b2mod.sha256(prompt.encode("utf-8"))})
    pd.DataFrame(rows).to_csv(labels / "prompts_index.csv", index=False)
    b2run = json.loads((HERE / "labels/b2-search/run.json").read_text())
    run = {**b2run, "run_id": RUN, "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "repo_commit": b2mod.git("rev-parse", "HEAD"),
           "repo_dirty_tracked_files": b2mod.git("status", "--porcelain", "--untracked-files=no").splitlines(),
           "rubric": {**b2run["rubric"], "candidate": "experiments/benchmarks/plp-b2/PLp_S.txt",
                      "candidate_sha256": b2mod.sha256(s.encode()),
                      "fourgrams_shared_with_frames": [" ".join(g) for g in shared]},
           "judge_io": os.path.relpath(io, b2mod.ROOT)}
    (labels / "run.json").write_text(json.dumps(run, indent=2) + "\n")
    print(f"{RUN}: {len(rows)} prompts x {len(b2mod.REPEATS)}")


if __name__ == "__main__":
    main()
