"""Build PLp candidate S-q (approved by Pablo on 2026-10-01) and pin its rivercross and SWE-bench runs
(PREREGISTRATION.md, amendment 4). The lab regression is pinned by
../plp-candidate/lab-regression/make_prompts_s.py --candidate sq.

S-q is S with the size of the search defined by odds instead of counts: four sentences of S are replaced
(the definition in the introduction and the search clauses of Levels 2, 3 and 4). Everything else is S.
The script checks that, runs the word 4-gram check of the new text against the 54 rivercross frames and the
lab items, and writes
  - sq-search:   the 54 rivercross states, as s-search (Opus low, three repeats)
  - sq-swe-gate: the 44 SWE-bench Verified gate tasks, as s-swe-gate (Opus low, one call)

    python experiments/benchmarks/plp-b2/make_sq.py
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

REPLACE = [  # (sentence of S, its replacement in S-q)
    ("The size of the search is how many choices could go wrong and how far ahead their consequences show.",
     "The size of the search is how rarely a plan works when it is built by someone who knows the usual methods for "
     "this kind of task but does not look ahead."),
    ("Or the search is small: a few choices could go wrong, but each shows its consequence at once or one step later, "
     "so no looking ahead is needed.",
     "Or the search is small: such a plan works at least one time in four, and any slip shows at once."),
    ("Or the search is moderate: several choices could go wrong, and their consequences show only a few steps later, "
     "so options must be compared by looking ahead.",
     "Or the search is moderate: such a plan works between one time in four and one in a hundred, so options must be "
     "compared by looking ahead."),
    ("Or the search is large: many choices could go wrong and depend on one another, their consequences show only "
     "far ahead, and most plans that look workable fail.",
     "Or the search is large: such a plan works less than one time in a hundred, and most plans that look workable "
     "fail only far ahead."),
]


def write(run: str, rows: list[dict], prompts: dict[str, str], repeats: list[str], meta: dict) -> None:
    io, labels = b2mod.JUDGE_IO / run, HERE / "labels" / run
    for d in [io / "prompts", labels] + [io / "responses" / r for r in repeats]:
        d.mkdir(parents=True, exist_ok=True)
    for fid, p in prompts.items():
        (io / "prompts" / f"{fid}@PLp.txt").write_text(p, encoding="utf-8")
    pd.DataFrame(rows).to_csv(labels / "prompts_index.csv", index=False)
    meta = {**meta, "run_id": run, "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "repo_commit": b2mod.git("rev-parse", "HEAD"),
            "repo_dirty_tracked_files": b2mod.git("status", "--porcelain", "--untracked-files=no").splitlines(),
            "judge_io": os.path.relpath(io, b2mod.ROOT)}
    (labels / "run.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(f"{run}: {len(rows)} prompts x {len(repeats)}")


def main() -> None:
    cur = load_active_catalog()["PLp"]
    s = (HERE / "PLp_S.txt").read_text(encoding="utf-8").split("\n", 2)[2].rstrip("\n")
    sq = s
    for old, new in REPLACE:
        assert sq.count(old) == 1, old
        sq = sq.replace(old, new)
    (HERE / "PLp_Sq.txt").write_text(f"# {cur.full_name}\n\n{sq}\n", encoding="utf-8")
    sq_sha = b2mod.sha256(sq.encode())

    new = set().union(*(b2mod.fourgrams(n) for _, n in REPLACE))
    frames = pd.read_csv(b2mod.FRAME)
    lab = pd.read_csv(HERE.parent / "plp-candidate/lab-regression/items_s.csv")
    lab = lab[lab["set"] != "P"]
    shared = {"frames": sorted({" ".join(g) for t in frames["prompt"] for g in b2mod.fourgrams(t) & new}),
              "lab_items": sorted({" ".join(g) for t in lab["text"] for g in b2mod.fourgrams(t) & new})}
    print("4-grams shared with the new text:", shared)

    # Rivercross: the 54 states of s-search, three repeats.
    srun = json.loads((HERE / "labels/s-search/run.json").read_text())
    rows, prompts = [], {}
    for st in frames.itertuples(index=False):
        prompts[st.custom_id] = build_annotation_prompt_v2(cur.full_name, sq, st.prompt)
        rows.append({"benchmark": "rivercross", "instance_id": st.custom_id, "file_id": st.custom_id, "demand": "PLp",
                     "family": "v2", "prompt_sha256": b2mod.sha256(prompts[st.custom_id].encode("utf-8"))})
    write("sq-search", rows, prompts, b2mod.REPEATS,
          {**srun, "rubric": {**srun["rubric"], "candidate": "experiments/benchmarks/plp-b2/PLp_Sq.txt",
                              "candidate_sha256": sq_sha, "fourgrams_shared_with_frames": shared["frames"]}})

    # SWE-bench gate: the 44 tasks of s-swe-gate, one call each.
    grun = json.loads((HERE / "labels/s-swe-gate/run.json").read_text())
    gate = pd.read_csv(HERE / "labels/s-swe-gate/prompts_index.csv")
    inst = pd.read_parquet(b2mod.ROOT / "data/instances/instances_swe-bench-verified.parquet").set_index("instance_id")
    rows, prompts = [], {}
    for r in gate.itertuples(index=False):
        old = build_annotation_prompt_v2(cur.full_name, s, inst.loc[r.instance_id, "prompt"])
        assert b2mod.sha256(old.encode("utf-8")) == r.prompt_sha256, r.instance_id  # S prompt reproduces
        prompts[r.instance_id] = build_annotation_prompt_v2(cur.full_name, sq, inst.loc[r.instance_id, "prompt"])
        rows.append({**r._asdict(), "s_prompt_sha256": r.prompt_sha256,
                     "prompt_sha256": b2mod.sha256(prompts[r.instance_id].encode("utf-8"))})
    write("sq-swe-gate", rows, prompts, ["opus-low"],
          {**grun, "rubric": {**grun["rubric"], "candidate": "experiments/benchmarks/plp-b2/PLp_Sq.txt",
                              "candidate_sha256": sq_sha},
           "baseline": "plp-b2/labels/s-swe-gate (S) and natural-prompt/labels/npb-gate-opuslow (current text)"})


if __name__ == "__main__":
    main()
